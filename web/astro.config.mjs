// @ts-check
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

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
const SITE = process.env.PUBLIC_SITE_URL || process.env.SITE_URL || 'http://localhost:4321';
if (/^https?:\/\/(localhost|127\.0\.0\.1)/.test(SITE)) {
  console.warn(`[site] building with a local origin (${SITE}). Set PUBLIC_SITE_URL before deploying.`);
}

/**
 * Mirrors that collide with their own original, and near-duplicate mirrors.
 *
 * MUST stay in lockstep with the same rule in src/lib/content.ts, otherwise the
 * sitemap and the published page set disagree — the sitemap then drops pages
 * that are indexable, or lists pages that are noindex. verify-seo.mjs asserts
 * that sitemap coverage equals the published set, so drift fails the build.
 *
 *   shadow    : translation whose language == the original's language
 *               (Russian originals are already Russian, so multilang/ru/* is a
 *                duplicate of the original at the identical URL)
 *   duplicate : published, but a template/legacy copy -> noindex, not in sitemap
 */
function classify() {
  const slugify = (s) =>
    s.toLowerCase().replace(/\.md$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  let db;
  try {
    db = JSON.parse(readFileSync(DB_PATH, 'utf8'));
  } catch {
    console.warn('[seo] wiki_database.json not found — sitemap filter falls back to "index everything"');
    return { noindex: new Set(), shadow: new Set() };
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
    } else if (m.translation && m.translation !== 'human') {
      noindex.add(path);
    }
  }
  return { noindex, shadow };
}

const { noindex: NOINDEX, shadow: SHADOW } = classify();

export default defineConfig({
  site: SITE,
  // Static output: every entry is prerendered to real HTML. No adapter is needed
  // for static output, and Cloudflare Workers serves ./dist as static assets.
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
