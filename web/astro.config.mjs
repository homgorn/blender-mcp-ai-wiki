// @ts-check
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
// The publication rule is imported, not restated. It used to be written out by
// hand here, in generate-agent-files.mjs and in both gates, and the copies
// drifted — the config learned about the `ai` tier and one gate did not, which
// noindexed 19 pages that the sitemap still listed.
import { publishedEntries, emptyCategoryPairs, REAL_TRANSLATIONS } from './src/lib/publish.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const DB_PATH = resolve(HERE, '../WIKI/db/wiki_database.json');

/**
 * Canonical origin — the single source of truth for the whole site.
 * Astro exposes this to modules as `import.meta.env.SITE` (see src/lib/site-url.ts),
 * so pages and the sitemap can never disagree about the origin.
 *
 * REQUIRED in production: a wrong canonical actively hurts SEO, and a localhost
 * origin would ship a sitemap full of localhost URLs.
 */
const SITE = process.env.PUBLIC_SITE_URL || process.env.SITE_URL || 'https://blender-mcp-wiki.refertur.net';
if (/^https?:\/\/(localhost|127\.0\.0\.1)/.test(SITE)) {
  console.warn(`[site] building with a local origin (${SITE}). Set PUBLIC_SITE_URL before deploying.`);
}

/**
 * Translations that get no page of their own.
 *
 * MUST stay in lockstep with publishedEntries() in src/lib/links.ts and with the
 * rule in generate-agent-files.mjs, otherwise the sitemap and the published page
 * set disagree — the sitemap then drops pages that are indexable, or lists pages
 * that do not exist. verify-seo.mjs asserts that sitemap coverage equals the
 * published set, so drift fails the build.
 *
 *   shadow   : translation whose language == the original's, so it resolves to
 *              the same URL (Russian originals are already Russian, and
 *              multilang/ru/* is a duplicate at the identical URL)
 *   template : not a translation at all, just the original with a language header
 *              (790 of them; previously published as noindex, which was honest to
 *               a crawler and dishonest to a reader who had chosen a language)
 *
 * Both stay in the repository as the translation backlog.
 */
const REAL_TRANSLATIONS_LOCAL = REAL_TRANSLATIONS;
void REAL_TRANSLATIONS_LOCAL;

function classify() {
  const slugify = (s) =>
    s.toLowerCase().replace(/\.md$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  let db;
  try {
    db = JSON.parse(readFileSync(DB_PATH, 'utf8'));
  } catch {
    console.warn('[seo] wiki_database.json not found — sitemap filter falls back to "index everything"');
    return { noindex: new Set(), shadow: new Set(), template: new Set(), emptyCategories: new Set() };
  }
  const all = db.entries ?? [];
  const originalLang = new Map();
  for (const e of all) {
    const m = e.meta ?? {};
    if (!m.is_translation) {
      originalLang.set(m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, ''), m.language);
    }
  }
  const noindex = new Set();
  const shadow = new Set();
  const template = new Set();
  for (const e of all) {
    const m = e.meta ?? {};
    if (!m.is_translation) continue;
    const origId = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
    const path = `/${m.language}/${m.category}/${slugify(origId)}`;
    // A shadow mirror shares its URL with the original. Recording it as noindex
    // too would strip the *original* from the sitemap, because the filter works
    // on paths, not on the entity that owns them.
    if (originalLang.get(origId) === m.language) {
      shadow.add(path);
    } else if (!REAL_TRANSLATIONS.has(m.translation ?? 'template')) {
      // A template mirror is not a translation. It gets no page at all now, so
      // the sitemap never sees it; the set exists so the filter and the gate can
      // state the intent rather than relying on their absence.
      template.add(path);
    }
  }
  // From the shared rule, not a second copy of it.
  const empty = new Set();
  for (const pair of emptyCategoryPairs(all)) {
    const [l, c] = pair.split('/');
    empty.add(`/${l}/${c}`);
  }
  return { noindex, shadow, template, emptyCategories: empty };
}

const { noindex: NOINDEX, shadow: SHADOW, emptyCategories: EMPTY_CATS } = classify();

export default defineConfig({
  site: SITE,
  // Static output: every entry is prerendered to real HTML. No adapter is needed
  // for static output, and Cloudflare Pages serves ./dist directly. (The
  // "Pages support removed from @astrojs/cloudflare" note applies to on-demand
  // rendering only — see SDD/adr/0005.)
  output: 'static',
  // /foo -> /foo.html (not /foo/index.html). This is what makes the llms.txt v2
  // "same URL, .md extension" twin possible: /ru/prompts/01-geometry-basics.md
  build: { format: 'file' },
  trailingSlash: 'never',
  compressHTML: true,
  devToolbar: { enabled: false },
  integrations: [
    sitemap({
      // Only canonical, indexable content belongs in the sitemap.
      filter: (page) => {
        const path = page.replace(SITE, '');
        // A shadow mirror is never published separately, but its path IS the
        // original's path — so it must stay in the sitemap. Only true
        // near-duplicate mirrors (a different language) are dropped.
        if (NOINDEX.has(path)) return false;
        if (path.endsWith('.md')) return false;      // markdown twins
        if (/\/search$/.test(path)) return false;     // no search results in a sitemap
        // Category pages that list zero articles in their language are thin
        // content. They stay published (the notice and the language switcher
        // are useful, and footer links must resolve) but they are noindex, so
        // they must not be here.
        if (EMPTY_CATS.has(path)) return false;
        return true;
      },
      serialize(item) {
        if (item.url === `${SITE}/`) item.priority = 1.0;
        else if (/^\/(ru|en|es|de|zh)\/?$/.test(new URL(item.url).pathname)) item.priority = 0.9;
        else item.priority = 0.7;
        return item;
      },
      // Emits <xhtml:link rel="alternate" hreflang="…"> groups in the sitemap.
      // In-page <link rel="alternate"> tags are emitted separately by BaseLayout —
      // Google needs both, and the two are not the same mechanism.
      i18n: {
        defaultLocale: 'ru',
        locales: {
          ru: 'ru-RU',
          en: 'en-US',
          es: 'es-ES',
          de: 'de-DE',
          zh: 'zh-CN',
        },
      },
    }),
  ],
  vite: {
    // WIKI/ lives outside web/ and is read (never copied) at build time.
    server: { fs: { allow: ['..', '../WIKI'] } },
  },
});
