/**
 * SEO / structured data layer.
 *
 * Two audiences are served by the same markup:
 *  - crawlers  -> canonical, hreflang cluster, robots directives, JSON-LD
 *  - LLM agents -> JSON-LD, plus the .md twin linked via rel="alternate"
 */
import { SITE_URL, SITE_NAME, TWITTER_HANDLE, LANG_META, type Lang } from './site';
import { entryUrl, hreflangCluster, isIndexable, stats } from './content';
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

  return {
    url,
    canonical: canonicalTarget,
    robots,
    image: abs(input.image ?? '/og-default.png'),
    lang: input.lang,
    alternates,
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

export function articleJsonLd(e: Entry) {
  const url = abs(entryUrl(e));
  const words = e.wordCount || 1;
  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        // Article, not TechArticle. Google rich results accept only
        // Article / NewsArticle / BlogPosting — TechArticle is valid schema.org
        // but earns no Google rich result. Semantics are preserved via
        // articleSection, proficiencyLevel and about.
        '@type': 'Article',
        '@id': `${url}#article`,
        mainEntityOfPage: { '@type': 'WebPage', '@id': url },
        headline: e.title.slice(0, 110),
        name: e.title,
        description: e.description.slice(0, 300),
        inLanguage: LANG_META[e.lang].locale,
        dateModified: e.updated || undefined,
        datePublished: e.updated || undefined,
        keywords: e.tags.slice(0, 20).join(', '),
        wordCount: words,
        timeRequired: `PT${Math.max(1, Math.round(words / 180))}M`,
        proficiencyLevel: PROFICIENCY[Math.min(3, Math.max(1, e.difficulty))] || 'Beginner',
        articleSection: e.category,
        articleType: e.type,
        isAccessibleForFree: true,
        encodingFormat: 'text/html',
        // Structured, machine-readable body summary helps LLM extraction.
        abstract: e.description.slice(0, 500),
        author: { '@id': `${SITE_URL}/#org` },
        publisher: { '@id': `${SITE_URL}/#org` },
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

/** Compact "answer" block that AI engines lift verbatim. */
export function faqFrom(e: Entry): { q: string; a: string }[] {
  const out: { q: string; a: string }[] = [];
  const goal = /^##\s+.*?(?:ЦЕЛЬ|GOAL)\s*$/im.exec(e.body);
  if (goal) {
    const rest = e.body.slice(goal.index).split('\n').slice(1).join('\n');
    const answer = rest
      .split(/\n##\s+/)
      .shift()!
      .replace(/```[\s\S]*?```/g, '')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 500);
    if (answer.length > 30) out.push({ q: e.title.replace(/^P\d+:\s*/i, ''), a: answer });
  }
  return out;
}

export function faqJsonLd(faq: { q: string; a: string }[]) {
  if (!faq.length) return null;
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faq.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  };
}

export const siteStats = stats;
