/**
 * The publication rule, in one place, with no dependencies.
 *
 * This file exists because the rule was stated in six places — the page builder,
 * the Astro config, the agent-file generator and the gates — and they drifted.
 * The last drift noindexed 19 freshly translated pages while the sitemap still
 * listed them, and a gate caught it only because a test happened to compare
 * robots tags against the sitemap.
 *
 * A rule that must be repeated should instead be imported. Plain `.mjs` so the
 * Astro config and the node scripts can load it without a TypeScript step;
 * `links.ts` re-exports it for the typed side, so there is still one
 * implementation.
 *
 * It accepts two shapes, because there are two kinds of caller: raw database
 * entries (`is_translation`, `language`, `category`, `orig_id`) and the objects
 * the Astro data layer builds from them (`isTranslation`, `lang`, `origId`).
 * Reading only one set of field names is what made an earlier version of this
 * file silently publish all 794 mirrors: the guard read `is_translation` on
 * objects that spell it `isTranslation`, got `undefined`, and decided every
 * entry was an original.
 *
 * What gets a page:
 *   original              -> published
 *   human / ai translation in a language the original does not already cover
 *                         -> published
 *   translation whose language equals the original's ("shadow")
 *                         -> not published: it resolves to the same URL
 *   template / legacy / unmarked
 *                         -> not published: it is not a translation
 *
 * Everything that is not published stays in the repository as the translation
 * backlog. The reason a template mirror is not published at all, rather than
 * published as noindex, is in SDD/SPEC.md: noindex was honest to a crawler and
 * dishonest to a reader who had chosen that language.
 */

/** Qualities that constitute a real translation. */
export const REAL_TRANSLATIONS = new Set(['human', 'ai']);

/**
 * Accept either a database entry or a built Entry.
 *
 * Typed loosely on purpose: the two shapes disagree on field names, and the
 * callers are three different consumers (Astro's data layer, the Astro config,
 * and the gates). Without a template parameter here, `publishedEntries` returns
 * `any[]` and every consumer loses its element type — which is what made
 * `npm run check` report implicit-any in thirteen places in the tests rather
 * than pointing at this line.
 *
 * @template T
 * @param {T} e
 * @returns {{isTranslation: boolean, translation: string|undefined,
 *            lang: string|undefined, category: string|undefined, origId: string}}
 */
function norm(e) {
  const m = (e && e.meta) || e || {};
  return {
    isTranslation: Boolean(m.is_translation ?? m.isTranslation),
    translation: m.translation,
    lang: m.language ?? m.lang,
    category: m.category,
    origId: m.orig_id ?? m.origId
      ?? String(m.id ?? '').replace(/__[a-z]{2}$/, ''),
  };
}

/**
 * A template mirror is the original text with a language header, not a translation.
 *
 * @template T
 * @param {T} e
 * @returns {boolean}
 */
export function isTemplateMirror(e) {
  const m = norm(e);
  if (!m.isTranslation) return false;
  return !REAL_TRANSLATIONS.has(m.translation || 'template');
}

/**
 * origId -> language of the non-translation entry.
 *
 * @template T
 * @param {readonly T[]} list
 * @returns {Map<string, string>}
 */
export function computeOrigLang(list) {
  const m = new Map();
  for (const e of list) {
    const n = norm(e);
    if (!n.isTranslation) m.set(n.origId, n.lang);
  }
  return m;
}

/**
 * A translation in the same language as its original: same URL, not published.
 *
 * @template T
 * @param {T} e
 * @param {Map<string, string>} origLangByOrig
 * @returns {boolean}
 */
export function isShadowMirror(e, origLangByOrig) {
  const m = norm(e);
  if (!m.isTranslation) return false;
  return origLangByOrig.get(m.origId) === m.lang;
}

/**
 * A real translation in a language the original does not already cover.
 *
 * @template T
 * @param {T} e
 * @param {Map<string, string>} origLangByOrig
 * @returns {boolean}
 */
export function isRealTranslation(e, origLangByOrig) {
  const m = norm(e);
  if (!m.isTranslation) return false;
  if (!REAL_TRANSLATIONS.has(m.translation || 'template')) return false;
  return origLangByOrig.get(m.origId) !== m.lang;
}

/**
 * The published set.
 *
 * @template T
 * @param {readonly T[]} list
 * @returns {T[]}
 */
export function publishedEntries(list) {
  const orig = computeOrigLang(list);
  return list.filter((e) => {
    const m = norm(e);
    if (!m.isTranslation) return true;
    if (!REAL_TRANSLATIONS.has(m.translation || 'template')) return false;
    return orig.get(m.origId) !== m.lang;
  });
}

/**
 * /{lang}/{category} pairs that have no published article.
 *
 * @template T
 * @param {readonly T[]} list
 * @returns {Set<string>}
 */
export function emptyCategoryPairs(list) {
  const orig = computeOrigLang(list);
  const filled = new Set();
  const cats = new Set();
  for (const e of list) {
    const m = norm(e);
    if (!m.category) continue;
    cats.add(m.category);
    if (!m.isTranslation) {
      if (m.lang) filled.add(`${m.lang}/${m.category}`);
    } else if (REAL_TRANSLATIONS.has(m.translation || 'template')
               && orig.get(m.origId) !== m.lang) {
      if (m.lang) filled.add(`${m.lang}/${m.category}`);
    }
  }
  const out = new Set();
  for (const c of cats) {
    for (const l of ['ru', 'en', 'es', 'de', 'zh']) {
      if (!filled.has(`${l}/${c}`)) out.add(`${l}/${c}`);
    }
  }
  return out;
}

/** `01_geometry_basics` -> `01-geometry-basics`. Ids may contain spaces. */
export function slugify(s) {
  return String(s)
    .toLowerCase()
    .replace(/\.md$/, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
