/**
 * SEO / structured data layer.
 *
 * Two audiences are served by the same markup:
 *  - crawlers  -> canonical, hreflang cluster, robots directives, JSON-LD
 *  - LLM agents -> JSON-LD, plus the .md twin linked via rel="alternate"
 */
import { SITE_URL, SITE_NAME, TWITTER_HANDLE, LANG_META, type Lang } from './site';
import { entryUrl, hreflangCluster, isIndexable, seoDescription, slugify, stats } from './content';
import type { Entry } from './content';

const ORG = {
  '@type': 'Organization',
  name: SITE_NAME,
  url: SITE_URL,
  logo: {
    '@type': 'ImageObject',
    url: `${SITE_URL}/og-default.png`,
    width: 1200,
    height: 630,
  },
};

export const abs = (path: string): string => (path.startsWith('http') ? path : `${SITE_URL}${path}`);

/** Difficulty 1..3 -> schema.org proficiencyLevel. */
const PROFICIENCY = ['', 'Beginner', 'Intermediate', 'Expert'] as const;

/* -------------------------------------------------- title / description */

/**
 * SERP truncation budgets.
 *
 * Google renders a result title in roughly 600 px (~60 Latin characters, less in
 * Cyrillic) and cuts it with its own ellipsis; the description is cut at about
 * 155-160 characters on desktop and about 120 on mobile. Measured on the built
 * site: 9 of 222 titles exceeded 60 characters and 95 of 222 descriptions
 * exceeded 160 — in every one of those cases the tail was invisible in the SERP
 * anyway, so what was actually lost was the part we chose.
 *
 * Truncating here instead buys two things: the visible part is a complete
 * thought (we break on a word boundary, Google breaks mid-word), and the
 * character budget is enforced in one place rather than per page template.
 */
export const MAX_TITLE = 60;
export const MAX_DESCRIPTION = 155;

/** Scripts written without spaces: there is no word boundary to break on. */
const CJK = /[\u2e80-\u9fff\uac00-\ud7af\uf900-\ufaff\uff00-\uffef]/;

/**
 * Cut to at most `max` characters without ever splitting a word.
 * Returns the text unchanged when it already fits — no truncation, no padding.
 */
export function cutAtWord(text: string, max: number): string {
  const t = text.trim();
  if (t.length <= max) return t;
  if (CJK.test(t)) return t.slice(0, max).trimEnd();
  const head = t.slice(0, max);
  // Position of the last space: everything from there on is a partial word.
  const sp = head.search(/\s\S*$/);
  return (sp > 0 ? head.slice(0, sp) : head).trimEnd();
}

/** Trailing punctuation a cut sentence should not keep. */
const DANGLING = /[\s,;:.!…—–-]+$/;

/**
 * `<title>` / `og:title` / `twitter:title` for a page, brand suffix included.
 *
 * The suffix is reserved first and the headline absorbs the cut, so the brand
 * never disappears — a title that reads `Blender AI Wiki` and nothing else is a
 * wasted listing. Unlike the description, a truncated title keeps the ellipsis:
 * the brand suffix that follows it would otherwise read as a broken word.
 */
export function clampTitle(title: string, brand?: string, sep = ' · '): string {
  // The root page passes the brand itself as its headline. Appending the brand to
  // it produced "Blender AI Wiki — Blender AI Wiki", which is the kind of title
  // that wastes the one line Google gives the most important page on the site.
  const hasBrand = Boolean(
    brand && (title === brand || title.startsWith(`${brand} `) || title.startsWith(`${brand} —`)),
  );
  const suffix = brand && !hasBrand ? `${sep}${brand}` : '';
  if (title.length + suffix.length <= MAX_TITLE) return `${title}${suffix}`;
  const room = MAX_TITLE - suffix.length - 1; // 1 char for the ellipsis
  const head = cutAtWord(title, room).replace(DANGLING, '');
  return `${head}…${suffix}`;
}

/**
 * `<meta name="description">` / `og:description` / `twitter:description`.
 *
 * No ellipsis here, deliberately: Google already appends its own, and two of
 * them read as sloppy. A description cut at a word boundary with nothing added
 * is indistinguishable from one that was written that short.
 */
export function clampDescription(text: string): string {
  return cutAtWord(text, MAX_DESCRIPTION).replace(DANGLING, '');
}

export interface SeoInput {
  title: string;
  description: string;
  /** Site-root-relative path, extensionless. */
  path: string;
  lang: Lang;
  /** When true the page is not a search result target (template mirrors). */
  noindex?: boolean;
  /** Absolute or relative OG image. */
  image?: string;
  type?: 'website' | 'article';
  publishedTime?: string;
  modifiedTime?: string;
  keywords?: string[];
  /** For entry pages: build the hreflang cluster. */
  entry?: Entry;
}

/**
 * Per-article OG card, `/og/<slugified entry id>.png`.
 *
 * The filename is derived from the entry id only — no title, no timestamp, no
 * counter — so re-running the generator reproduces the same name and a card is
 * never generated twice under two names. The id includes the `__<lang>` suffix
 * of a translation, which keeps the five language versions of one article on
 * five separate files instead of overwriting each other.
 */
export const ogImageFor = (e: Entry): string => `/og/${slugify(e.id)}.png`;

export function buildSeo(input: SeoInput) {
  const url = abs(input.path);
  const canonicalTarget = input.entry && input.entry.isDuplicate
    ? abs(hreflangCluster(input.entry).find((h) => h.quality === 'original')?.href ?? input.path)
    : url;

  const robots = input.noindex
    ? 'noindex, follow, max-image-preview:large, max-snippet:-1'
    : 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1';

  const alternates: { hreflang: string; href: string }[] = input.entry
    ? hreflangCluster(input.entry).map((h) => ({ hreflang: LANG_META[h.lang].locale, href: abs(h.href) }))
    : [];

  // An entry page gets its own card; everything else shares the site default.
  const imagePath = input.image ?? (input.entry ? ogImageFor(input.entry) : '/og-default.png');

  return {
    url,
    canonical: canonicalTarget,
    robots,
    // The home page was the only place with a long dash; keep that one quirk.
    title: clampTitle(input.title, SITE_NAME, input.path === '/' ? ' — ' : ' · '),
    description: clampDescription(input.description),
    image: abs(imagePath),
    /** og:image:alt — a crawler cannot see the card, a screen reader cannot either. */
    imageAlt: `${input.title} — ${SITE_NAME}`,
    lang: input.lang,
    alternates,
    // og:type: an article is `article`, everything else is `website`. Left to the
    // caller because a listing of articles is still a `website`.
    ogType: input.type ?? 'website',
    publishedTime: input.entry?.updated || input.publishedTime || undefined,
    modifiedTime: input.entry?.updated || input.modifiedTime || undefined,
    // NOTE: no <meta name="keywords"> — Google states it has no effect on
    // indexing or ranking. Keywords still ship inside JSON-LD, which is read.
    keywords: input.keywords ?? [],
  };
}

/* ------------------------------------------------------------- JSON-LD */

export function websiteJsonLd(lang: Lang) {
  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': `${SITE_URL}/#website`,
        url: `${SITE_URL}/`,
        name: SITE_NAME,
        inLanguage: LANG_META[lang].locale,
        description:
          'База знаний по Blender, MCP и AI-агентам: промпты, сетапы, воркфлоу и кейсы с готовым кодом.',
        publisher: { '@id': `${SITE_URL}/#org` },
        potentialAction: {
          '@type': 'SearchAction',
          target: {
            '@type': 'EntryPoint',
            urlTemplate: `${SITE_URL}/${lang}/search?q={search_term_string}`,
          },
          'query-input': 'required name=search_term_string',
        },
      },
      { ...ORG, '@id': `${SITE_URL}/#org` },
    ],
  };
}

/**
 * Software entities the article is actually about.
 *
 * Only names that exist in the data: `mcp_tools` in the database, taken
 * verbatim (minus the backticks the frontmatter wraps them in) and
 * de-duplicated. Nothing is inferred from the title — a card that claims an
 * article is about a tool it never mentions is worse than no `about` at all.
 */
function aboutEntities(e: Entry) {
  const seen = new Set<string>();
  const out: { '@type': 'SoftwareApplication'; name: string; applicationCategory: string }[] = [];
  for (const raw of e.mcpTools) {
    const name = String(raw).replace(/[`"'*]/g, '').trim();
    // A tool is an identifier, not a sentence: anything with spaces is prose
    // that leaked into the field, and it must not become a schema name.
    if (!name || name.length > 64 || /\s/.test(name) || seen.has(name)) continue;
    seen.add(name);
    out.push({ '@type': 'SoftwareApplication', name, applicationCategory: 'DeveloperApplication' });
    if (out.length >= 10) break;
  }
  return out;
}

export function articleJsonLd(e: Entry) {
  const url = abs(entryUrl(e));
  const words = e.wordCount || 1;
  // The database's `description` field is "the paragraph after the H1", which for
  // this corpus is the metadata line and is empty on most entries. The page's own
  // meta description comes from seoDescription(), which falls back to the goal
  // paragraph — use that here too, so the markup describes the article instead of
  // shipping `"description": ""` on the pages that do have something to say.
  const summary = seoDescription(e);
  const about = aboutEntities(e);
  // The database exposes one date per entry. Both fields carry it rather than
  // publishing `datePublished: undefined`, which some validators read as a
  // schema error and others ignore silently.
  const stamp = e.updated || undefined;
  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        // TechArticle, not Article. schema.org models TechArticle as a subtype
        // of Article (TechArticle ⊂ Article ⊂ CreativeWork), and Google's
        // article rich-result documentation accepts any of them — Article,
        // NewsArticle, Report, Review, ScholarlyArticle, TechArticle — as long
        // as the required fields are present. So the narrower type keeps the
        // eligibility the plain Article had and states what the corpus actually
        // is: documentation with runnable code. The earlier comment here claimed
        // TechArticle "earns no Google rich result", which is simply wrong.
        '@type': 'TechArticle',
        '@id': `${url}#article`,
        mainEntityOfPage: { '@type': 'WebPage', '@id': url },
        // Google measures headline in pixels; ~110 characters is the documented
        // budget. Cut on a word boundary so a long title never ends mid-word.
        headline: cutAtWord(e.title, 110),
        name: e.title,
        description: cutAtWord(summary, 300),
        inLanguage: LANG_META[e.lang].locale,
        datePublished: stamp,
        dateModified: stamp,
        keywords: e.tags.slice(0, 20).join(', '),
        wordCount: words,
        timeRequired: `PT${Math.max(1, Math.round(words / 180))}M`,
        proficiencyLevel: PROFICIENCY[Math.min(3, Math.max(1, e.difficulty))] || 'Beginner',
        articleSection: e.category,
        articleType: e.type,
        isAccessibleForFree: true,
        encodingFormat: 'text/html',
        abstract: cutAtWord(summary, 500),
        // The article's own OG card: the same file og:image points at, so the
        // markup and the social preview can never drift apart.
        image: {
          '@type': 'ImageObject',
          url: abs(ogImageFor(e)),
          width: 1200,
          height: 630,
        },
        author: { '@id': `${SITE_URL}/#org` },
        publisher: { '@id': `${SITE_URL}/#org` },
        // Only when the database actually names tools: an empty `about` array is
        // a claim of "nothing in particular", which is noise in the graph.
        ...(about.length ? { about } : {}),
      },
      {
        '@type': 'BreadcrumbList',
        '@id': `${url}#breadcrumb`,
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: SITE_NAME, item: `${SITE_URL}/` },
          { '@type': 'ListItem', position: 2, name: e.category, item: `${SITE_URL}/${e.lang}/${e.category}` },
          { '@type': 'ListItem', position: 3, name: e.title, item: url },
        ],
      },
    ],
  };
}

export function collectionJsonLd(name: string, description: string, path: string, lang: Lang, items: Entry[]) {
  const url = abs(path);
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': `${url}#collection`,
    url,
    name,
    description,
    inLanguage: LANG_META[lang].locale,
    isPartOf: { '@id': `${SITE_URL}/#website` },
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: items.length,
      itemListElement: items.slice(0, 50).map((e, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        url: abs(entryUrl(e)),
        name: e.title,
      })),
    },
  };
}

/**
 * No FAQPage here, on purpose.
 *
 * 192 of the 222 published pages carried one, built from the article's own
 * title: `faqFrom` took the "ЦЕЛЬ/GOAL" paragraph as the answer and the title
 * as the question. Sampled, 8 of 8 questions did not end in a question mark —
 * "INSTANCING & ARRAYS", "SCULPTING BASICS", "NODE GROUP CREATION" — so the
 * markup described a Q&A page that does not exist on the site.
 *
 * Two reasons not to bring it back. Google narrowed FAQ rich results in August
 * 2023 to authoritative government and health sites, so a knowledge wiki gets
 * no rich snippet either way; and structured data that is not backed by visible
 * Q&A content on the page is exactly the pattern that earns a manual action
 * under the spam policies. The extracted goal paragraph still ships as the
 * article's `abstract`, which is the honest version of the same idea.
 */
export const siteStats = stats;
