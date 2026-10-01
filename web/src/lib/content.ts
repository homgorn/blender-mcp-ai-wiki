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

export type TranslationQuality = 'human' | 'template' | 'legacy';

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

/** `01_geometry_basics` -> `01-geometry-basics`. Stable, derived, no drift. */
export function slugify(origId: string): string {
  return origId
    .toLowerCase()
    .replace(/\.md$/, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

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
    // A template/legacy mirror is a near-duplicate of the original: it must not
    // compete with it in search results, so it is noindex + canonical-to-origin.
    isDuplicate: Boolean(m.is_translation) && translation !== 'human',
  };
}

const all: Entry[] = RAW.map((raw) => {
  const e = build(raw);
  byFile.set(raw.file_path.replace(/\\/g, '/').toLowerCase(), e);
  return e;
});

/**
 * Drop mirrors that collide with their own original.
 *
 * Russian originals are already Russian, so `multilang/ru/<cat>/x.md` produces
 * the exact same URL as `<cat>/x.md` — 163 collisions, i.e. 163 pages that would
 * be published twice with the second one winning and, being a template copy,
 * marked noindex. The original is the canonical Russian version, so the ru mirror
 * is redundant and is not published.
 */
function dropShadowMirrors(list: Entry[]): Entry[] {
  const originalLangByOrig = new Map<string, Lang>();
  for (const e of list) {
    if (!e.isTranslation) originalLangByOrig.set(e.origId, e.lang);
  }
  const dropped = list.filter((e) => {
    if (!e.isTranslation) return true;
    return originalLangByOrig.get(e.origId) !== e.lang;
  });
  if (dropped.length !== list.length) {
    console.log(`[content] dropped ${list.length - dropped.length} shadow mirrors (mirror language == original language)`);
  }
  return dropped;
}

export const entries: Entry[] = dropShadowMirrors(all);
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

/** Indexable = original + human translations. Duplicates are noindex. */
export function isIndexable(e: Entry): boolean {
  return !e.isDuplicate;
}

/** Related articles: shared tags, same language preferred, originals only. */
export function related(e: Entry, limit = 6): Entry[] {
  const group = byOrigId.get(e.origId);
  const tagSet = new Set(e.tags);
  const score = (o: Entry) => {
    if (group?.has(o.lang)) return -1000; // same article, other language
    let s = 0;
    for (const t of o.tags) if (tagSet.has(t)) s += 2;
    if (o.category === e.category) s += 3;
    if (o.lang === e.lang) s += 1;
    return s;
  };
  return originals
    .filter((o) => o.origId !== e.origId)
    .map((o) => ({ o, s: score(o) }))
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s || a.o.title.localeCompare(b.o.title))
    .slice(0, limit)
    .map((x) => x.o);
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

/** Site-wide stats for the footer / structured data. */
export const stats = {
  total: entries.length,
  originals: originals.length,
  languages: LANGS.length,
  categories: new Set(originals.map((e) => e.category)).size,
  humanTranslations: entries.filter((e) => e.translation === 'human').length,
  codeBlocks: entries.reduce((s, e) => s + e.codeBlocks, 0),
};
