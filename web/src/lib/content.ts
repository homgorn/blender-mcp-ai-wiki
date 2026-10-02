/**
 * Data layer.
 *
 * Single source of truth is the markdown corpus in WIKI/. The Python pipeline
 * (WIKI/scripts/build_database.py) turns it into WIKI/db/wiki_database.json,
 * which is the machine-readable form this site consumes. We deliberately do NOT
 * re-implement parsing in TypeScript, and we do NOT copy the markdown into this
 * project — one source, one parser, documented in SDD/SCHEMA.md.
 */
import db from '../../../WIKI/db/wiki_database.json';
import { LANGS, LANG_META, DEFAULT_LANG, type Lang } from './site';
import {
  buildBodyLinkMap, publishedEntries, slugify,
  REAL_TRANSLATIONS, type TranslationQuality,
} from './links';

export type { TranslationQuality } from './links';

export interface Entry {
  /** DB id: `01_geometry_basics` or `01_geometry_basics__es` */
  id: string;
  /** Original article id, shared across all languages. */
  origId: string;
  lang: Lang;
  category: string;
  type: string;
  title: string;
  description: string;
  difficulty: number;
  tags: string[];
  mcpTools: string[];
  status?: 'full' | 'stub';
  translation?: TranslationQuality;
  isTranslation: boolean;
  wordCount: number;
  codeBlocks: number;
  updated: string;
  filePath: string;
  /** Markdown body with frontmatter stripped. */
  body: string;
  /** Internal links resolved to site URLs. */
  links: { text: string; href: string; external: boolean }[];
  /** True when this page is a near-duplicate template mirror of the original. */
  isDuplicate: boolean;
}

interface RawMeta {
  id: string;
  orig_id?: string;
  title: string;
  category: string;
  type: string;
  difficulty: number;
  tags: string[];
  language: string;
  description: string;
  mcp_tools: string[];
  status?: string;
  translation?: string;
  is_translation?: boolean;
  word_count: number;
  code_blocks: number;
  updated: string;
  links: { text: string; url: string }[];
}

interface RawEntry {
  meta: RawMeta;
  full_content: string;
  file_path: string;
}

const RAW = (db as { entries: RawEntry[] }).entries;

/**
 * `01_geometry_basics` -> `01-geometry-basics`. Stable, derived, no drift.
 *
 * Re-exported from links.ts so the URL rule has exactly one implementation; the
 * agent-file generator and the SEO gate used to carry their own copies.
 */
export { slugify } from './links';

const FM = /^---\n[\s\S]*?\n---\n?/;
function stripFrontmatter(md: string): string {
  return md.replace(FM, '').trimStart();
}

/**
 * The layout already renders the article title as the page <h1>. The markdown
 * source repeats it as its own first heading, which would produce two <h1>s and
 * a duplicated outline. Drop the leading H1 only.
 */
function stripLeadingH1(md: string): string {
  return md.replace(/^\s*#\s+[^\n]*\n+/, '');
}

/**
 * A meta description must say what the page is about. The DB's `description`
 * field is "first paragraph after H1", which for this corpus is the metadata
 * line (`**ID:** P01 | **Кластер:** ...`) — useless as a description. Prefer the
 * goal section's prose; fall back to the DB description, then the title.
 */
export function seoDescription(e: Entry): string {
  const clean = (s: string) => s.replace(/```[\s\S]*?```/g, ' ').replace(/[*_`>#|-]/g, ' ').replace(/\s+/g, ' ').trim();
  // Minimum length is a function of the script: 50 Latin characters is a real
  // sentence, 50 Chinese characters is a paragraph. Judge by script, not count.
  const isCjk = /[぀-ヿ㐀-䶿一-鿿]/.test(e.body);
  const min = isCjk ? 30 : 50;

  const goal = /^#{1,3}\s+.*?(?:ЦЕЛЬ|GOAL)\s*$/im.exec(e.body);
  if (goal) {
    const text = clean(e.body.slice(goal.index + goal[0].length).split(/\n#{1,3}\s+/).shift()!);
    if (text.length >= min) return text.slice(0, 300);
  }
  const d = clean(e.description);
  if (d.length >= min) return d.slice(0, 300);

  // Last resort: first substantial body paragraph, so the description still says
  // something about the page instead of repeating the title.
  const para = e.body
    .split(/\n\s*\n/)
    .map(clean)
    .find((p) => p.length >= min && !/^[-*|>#]/.test(p));
  if (para) return para.slice(0, 300);
  return `${e.title}. ${e.category} — Blender AI Wiki.`;
}

const byFile = new Map<string, Entry>();

function build(raw: RawEntry): Entry {
  const m = raw.meta;
  const lang = (m.language as Lang) in LANG_META ? (m.language as Lang) : DEFAULT_LANG;
  const origId = m.orig_id ?? m.id.replace(/__[a-z]{2}$/, '');
  const translation = m.translation as TranslationQuality | undefined;
  return {
    id: m.id,
    origId,
    lang,
    category: m.category || 'references',
    type: m.type || 'reference',
    title: m.title || origId,
    description: m.description || '',
    difficulty: m.difficulty || 0,
    tags: Array.isArray(m.tags) ? m.tags : [],
    mcpTools: Array.isArray(m.mcp_tools) ? m.mcp_tools : [],
    status: (m.status as 'full' | 'stub') | undefined,
    translation,
    isTranslation: Boolean(m.is_translation),
    wordCount: m.word_count || 0,
    codeBlocks: m.code_blocks || 0,
    updated: m.updated || '',
    filePath: raw.file_path,
    body: stripLeadingH1(stripFrontmatter(raw.full_content || '')),
    links: [],
    // A duplicate is a published page that must not compete with its original.
    // Since template mirrors stopped being published, the only ones that can
    // reach this are ones that slipped through a stale rule — so the test is the
    // real-translation set, not a hardcoded 'human'. The previous version said
    // `!== 'human'` and quietly noindexed all 19 new `ai` references while the
    // sitemap still listed them.
    isDuplicate: Boolean(m.is_translation) && !REAL_TRANSLATIONS.has(
      (translation ?? 'template') as TranslationQuality,
    ),
  };
}

const all: Entry[] = RAW.map((raw) => {
  const e = build(raw);
  byFile.set(raw.file_path.replace(/\\/g, '/').toLowerCase(), e);
  return e;
});

/**
 * The published set.
 *
 * Two kinds of translation get no page of their own:
 *
 *   shadow  — its language equals the original's, so it resolves to the same URL
 *             (163 of them: `multilang/ru/...` against a Russian original)
 *   template — it is not a translation at all, just the original with a language
 *             header (790 of them)
 *
 * Template mirrors used to be published as noindex + canonical-to-origin. That
 * is the honest signal for a crawler and a dishonest one for a reader: someone
 * who picked Spanish got Russian or English with a banner, and the language
 * indexes counted articles they did not have. The files stay in the repository
 * as the translation backlog.
 *
 * This must stay identical to the same rule in astro.config.mjs,
 * generate-agent-files.mjs and verify-seo.mjs. A gate cannot check what it
 * cannot see, and drift here is what produced 631 pages that agreed with
 * nothing.
 */
function publishedSet(list: Entry[]): Entry[] {
  const kept = publishedEntries(list);
  if (kept.length !== list.length) {
    console.log(
      `[content] ${list.length} -> ${kept.length} published ` +
      `(${list.length - kept.length} mirrors unpublished: shadow or template)`,
    );
  }
  return kept;
}

export const entries: Entry[] = publishedSet(all);
export const originals: Entry[] = entries.filter((e) => !e.isTranslation);

// Built from the *published* set. Building it before shadow filtering let a
// dropped mirror overwrite the original in its language slot, which made the
// hreflang cluster resolve to a discarded copy and left duplicate pages
// self-canonical instead of canonical-to-origin.
const byOrigId = new Map<string, Map<Lang, Entry>>();
for (const e of entries) {
  let group = byOrigId.get(e.origId);
  if (!group) {
    group = new Map();
    byOrigId.set(e.origId, group);
  }
  group.set(e.lang, e);
}

// Resolve internal links now that every file is known.
for (const e of all) {
  const raw = RAW.find((r) => r.meta.id === e.id);
  e.links = (raw?.meta.links ?? []).map((l) => {
    if (/^https?:\/\//i.test(l.url)) return { text: l.text, href: l.url, external: true };
    // md links are relative to the source file's folder
    const dir = e.filePath.replace(/\\/g, '/').split('/').slice(0, -1).join('/');
    const abs = (dir ? dir + '/' : '') + l.url.split('#')[0];
    const target = byFile.get(abs.replace(/^\.\//, '').toLowerCase());
    return { text: l.text, href: target ? entryUrl(target) : l.url, external: false };
  });
}

/* ------------------------------------------------------------------ URLs */

/** file_path (posix) -> published entry. Shadows are deliberately absent. */
const byFilePublished = new Map<string, Entry>();
for (const e of entries) {
  byFilePublished.set(e.filePath.replace(/\\/g, '/').toLowerCase(), e);
}

/** Every category that has at least one published page, for section links. */
const categories = new Set(entries.map((e) => e.category));

/**
 * For one entry: the hrefs as written in its body, mapped to site URLs.
 *
 * The rules live in links.ts so they can be tested directly; this is only the
 * wiring to the real data. Previously `entry.links` was computed here and never
 * rendered, so 2 227 in-body links shipped as raw relative paths on 446 of 916
 * pages — the site publishes `setup-01-...` while the body says `setup_01_...`.
 */
const bodyLinkMaps = new Map<string, Map<string, string>>();
for (const e of entries) {
  const group = byOrigId.get(e.origId);
  const origin = group ? [...group.values()].find((o) => !o.isTranslation) : undefined;
  bodyLinkMaps.set(
    e.id,
    buildBodyLinkMap(e, {
      byFile: byFilePublished,
      byOrig: byOrigId,
      categories,
      entryUrl,
      categoryUrl,
      originalDir: (x) =>
        byOrigId.get(x.origId)
          ? [...byOrigId.get(x.origId)!.values()].find((o) => !o.isTranslation)?.filePath
              .replace(/\\/g, '/')
              .split('/')
              .slice(0, -1)
              .join('/')
          : undefined,
    }),
  );
}

/** Raw body href -> site URL, for one entry. Empty when nothing resolved. */
export function bodyLinks(e: Entry): Map<string, string> {
  return bodyLinkMaps.get(e.id) ?? new Map();
}

export function entryUrl(e: Entry): string {
  return `/${e.lang}/${e.category}/${slugify(e.origId)}`;
}
export function entryMdUrl(e: Entry): string {
  return `${entryUrl(e)}.md`;
}
export function langUrl(lang: Lang): string {
  return `/${lang}`;
}
export function categoryUrl(lang: Lang, category: string): string {
  return `/${lang}/${category}`;
}

/** Languages in which this article has genuinely unique content. */
export function hreflangCluster(e: Entry): { lang: Lang; href: string; quality: string }[] {
  const group = byOrigId.get(e.origId);
  if (!group) return [{ lang: e.lang, href: entryUrl(e), quality: e.translation ?? 'original' }];
  return LANGS.filter((l) => group!.has(l)).map((l) => {
    const t = group!.get(l)!;
    return { lang: l, href: entryUrl(t), quality: t.translation ?? 'original' };
  });
}

export function translationsOf(e: Entry): Entry[] {
  const group = byOrigId.get(e.origId);
  return group ? LANGS.map((l) => group.get(l)).filter((x): x is Entry => Boolean(x)) : [e];
}

export function byId(id: string): Entry | undefined {
  return entries.find((e) => e.id === id);
}

/* ------------------------------------------------------------- selectors */

export function byLang(lang: Lang): Entry[] {
  return entries.filter((e) => e.lang === lang);
}
export function byCategory(lang: Lang, category: string): Entry[] {
  return entries.filter((e) => e.lang === lang && e.category === category);
}
export function categoryCounts(lang: Lang): Record<string, number> {
  const out: Record<string, number> = {};
  for (const e of byLang(lang)) out[e.category] = (out[e.category] ?? 0) + 1;
  return out;
}

/**
 * Indexable = anything published, because nothing published is a duplicate.
 *
 * The old rule was `!isDuplicate`, where a duplicate was any non-human mirror.
 * Those are no longer published at all, so every published page is a real
 * article in its own right and the distinction has nothing left to decide.
 * It stayed as a function because the pages and the gates both ask the question,
 * and a named predicate is easier to keep honest than a bare negation.
 */
export function isIndexable(e: Entry): boolean {
  return !e.isDuplicate;
}

/**
 * Does this language have any indexable article in this category?
 *
 * Category pages are generated for the full cartesian product of
 * category × language, so a language with no content in a category still gets a
 * page. 48 of those were empty, and they were published `index, follow` and
 * listed in the sitemap — handing Google 48 pages with nothing on them. The
 * page itself is worth keeping (it explains the situation and points at the
 * languages that do have content, and footer links resolve), but it must not
 * ask to be indexed.
 *
 * The predicate lives here, once, because the rule has to hold in four places
 * — the page, the sitemap filter, llms.txt and the consistency gate. When those
 * disagreed, the sitemap and the pages did too.
 */
export function categoryHasContent(lang: Lang, category: string): boolean {
  return entries.some((e) => e.lang === lang && e.category === category && isIndexable(e));
}

/**
 * Related articles: shared tags, same language, originals only.
 *
 * `originals` is site-wide, and the old scoring only added +1 for a
 * same-language candidate, so a tag match in another language could outrank a
 * weaker same-language match. Result: 19 of 41 English pages had an entire
 * "Связанные материалы" block in Russian, with nothing on the cards to say so —
 * a German or English reader is not served by a Russian list.
 *
 * So: same-language candidates first, in their own ranked list. Only if a
 * language has nothing to show do we fall back to other languages, because an
 * empty block is worse than a foreign one.
 */
export function related(e: Entry, limit = 6): Entry[] {
  const group = byOrigId.get(e.origId);
  const tagSet = new Set(e.tags);
  const score = (o: Entry) => {
    if (o.origId === e.origId) return -1000; // the same article
    let s = 0;
    for (const t of o.tags) if (tagSet.has(t)) s += 2;
    if (o.category === e.category) s += 3;
    return s;
  };
  const rank = (list: Entry[]) =>
    list
      .map((o) => ({ o, s: score(o) }))
      .filter((x) => x.s > 0)
      .sort((a, b) => b.s - a.s || a.o.title.localeCompare(b.o.title))
      .slice(0, limit)
      .map((x) => x.o);

  const candidates = originals.filter((o) => o.origId !== e.origId);
  const sameLang = rank(candidates.filter((o) => o.lang === e.lang));
  if (sameLang.length) return sameLang;
  // `group` is consulted only to keep the intent readable: the origId check
  // above already excludes the same article in every language.
  void group;
  return rank(candidates);
}

export function popular(lang: Lang, limit = 12): Entry[] {
  return byLang(lang)
    .filter(isIndexable)
    .sort((a, b) => b.wordCount - a.wordCount)
    .slice(0, limit);
}

export function allTags(lang: Lang): { tag: string; count: number }[] {
  const m = new Map<string, number>();
  for (const e of byLang(lang)) for (const t of e.tags) m.set(t, (m.get(t) ?? 0) + 1);
  return [...m.entries()].map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count);
}

export function searchEntries(lang: Lang, q: string, limit = 20): Entry[] {
  const query = q.toLowerCase().trim();
  if (!query) return [];
  const words = query.split(/\s+/).filter((w) => w.length > 1);
  return byLang(lang)
    .map((e) => {
      const hay = `${e.title} ${e.description} ${e.tags.join(' ')} ${e.origId}`.toLowerCase();
      let s = 0;
      for (const w of words) {
        if (e.title.toLowerCase().includes(w)) s += 10;
        if (hay.includes(w)) s += 3;
      }
      return { e, s };
    })
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s)
    .slice(0, limit)
    .map((x) => x.e);
}

/** Published article count per language, computed from the published set. */
export const publishedByLang: Record<string, number> = {};
for (const l of LANGS) publishedByLang[l] = 0;
for (const e of entries) {
  if (isIndexable(e)) publishedByLang[e.lang] = (publishedByLang[e.lang] ?? 0) + 1;
}

/**
 * Languages that carry substantially the whole corpus.
 *
 * `stats.languages` used to be LANGS.length — five declared languages — and the
 * homepage printed it. That number was the "5 languages" claim, and it was
 * false: only two languages hold the corpus and the other three hold seven
 * articles each. A count of declared languages is not a count of content, and
 * printing it tells every visitor and every crawler something untrue.
 *
 * A language counts as full when it holds at least a third of the largest
 * language's articles. ru 160 and en 41 qualify; es/de/zh at 7 do not.
 */
const maxLang = Math.max(1, ...Object.values(publishedByLang));
export const fullLanguages: string[] = LANGS.filter((l) => publishedByLang[l] >= maxLang / 3);
export const partialLanguages: string[] = LANGS.filter((l) => publishedByLang[l] > 0
  && publishedByLang[l] < maxLang / 3);

/** Site-wide stats for the footer / structured data. */
export const stats = {
  total: entries.length,
  originals: originals.length,
  languages: LANGS.length,
  fullLanguages: fullLanguages.length,
  partialLanguages: partialLanguages.length,
  publishedByLang,
  categories: new Set(originals.map((e) => e.category)).size,
  humanTranslations: entries.filter((e) => e.translation === 'human').length,
  codeBlocks: entries.reduce((s, e) => s + e.codeBlocks, 0),
};
