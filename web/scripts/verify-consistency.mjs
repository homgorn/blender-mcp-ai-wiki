#!/usr/bin/env node
/**
 * Cross-artifact consistency gate.
 *
 * verify-seo.mjs checks each artifact on its own terms. This checks that the
 * artifacts agree with EACH OTHER, which is where the expensive bugs live:
 * a page that is noindex while the sitemap lists it, a noindex mirror leaking
 * into llms-full.txt, an RSS feed pointing at duplicates.
 *
 * One rule, applied everywhere (it must match astro.config.mjs and content.ts):
 *   shadow    — a mirror whose language equals its original's language is never
 *               published; the original owns that URL.
 *   duplicate — published, but noindex + canonical-to-origin.
 *   indexable — everything else.
 *
 * Run:  node scripts/verify-consistency.mjs
 */
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const DIST = join(HERE, '..', 'dist');
const DB = join(HERE, '..', '..', 'WIKI', 'db', 'wiki_database.json');
const read = (p) => readFileSync(join(DIST, p), 'utf8');

const fails = [];
const ok = (m) => console.log(`  [OK] ${m}`);
const fail = (m) => { fails.push(m); console.log(`  [FAIL] ${m}`); };

// The publication rule is imported. This gate was the last file still carrying
// its own copy, and it disagreed: it still called a published page a "duplicate"
// unless the translation was `human`, so it demanded `noindex` from the 19 new
// Russian references and then complained that the sitemap listed them.
import { publishedEntries, REAL_TRANSLATIONS, computeOrigLang } from '../src/lib/publish.mjs';

const slugify = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
const db = JSON.parse(readFileSync(DB, 'utf8'));
const rows = db.entries.map((e) => {
  const m = e.meta;
  const orig = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
  return {
    url: `/${m.language}/${m.category || 'references'}/${slugify(orig)}`,
    stem: slugify(orig),
    isTr: Boolean(m.is_translation),
    tr: m.translation,
  };
});

const origLangByStem = new Map();
for (const r of rows) if (!r.isTr) origLangByStem.set(r.stem, r.url.split('/')[1]);
const isShadow = (r) => r.isTr && origLangByStem.get(r.stem) === r.url.split('/')[1];

const shadows = rows.filter(isShadow);
// Published, by the shared rule rather than a fourth spelling of it.
const pubRows = publishedEntries(db.entries);
const indexable = new Set(pubRows.map((e) => {
  const m = e.meta;
  const orig = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
  return `/${m.language}/${m.category || 'references'}/${slugify(orig)}`;
}));
// Nothing is published and a duplicate any more: a duplicate was a published page
// that must not compete with its original, and the only ones left are files that
// got past a stale rule, which check 1 exists to catch.
const untranslated = new Set(
  rows.filter((r) => !indexable.has(r.url) && !isShadow(r)).map((r) => r.url),
);
const dupes = new Set();
void [REAL_TRANSLATIONS, computeOrigLang];

console.log('== Classification ==');
console.log(`  published=${indexable.size} untranslated mirrors=${rows.length - pubRows.length} (${shadows.length} shadow)`);

console.log('== 1. robots meta on disk agrees with classification ==');
let bad = 0;
for (const url of indexable) {
  const f = join(DIST, `${url}.html`);
  if (!existsSync(f)) continue;
  const m = /<meta name="robots" content="([^"]*)"/.exec(read(`${url}.html`))?.[1] ?? '';
  // Every published article must be indexable. The mirror case no longer
  // applies: an untranslated mirror has no page to carry a robots tag at all,
  // which check 2 verifies separately.
  if (m.includes('noindex')) { bad++; if (bad <= 3) fail(`published but noindex: ${url}`); }
}
for (const url of untranslated) {
  if (existsSync(join(DIST, `${url}.html`))) {
    bad++;
    if (bad <= 3) fail(`untranslated mirror is published: ${url}`);
  }
}
if (!bad) ok('robots meta matches the classification on every page');

console.log('== 2. sitemap ==');
{
  const idx = read('sitemap-index.xml');
  const child = /<loc>([^<]+)<\/loc>/.exec(idx)?.[1] ?? '';
  const rel = child.replace(/^https?:\/\/[^/]+/, '');
  const sm = read(rel.replace(/^\//, ''));
  const urls = new Set([...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname));
  const leak = [...urls].filter((u) => untranslated.has(u) && !indexable.has(u));
  const missing = [...indexable].filter((u) => !urls.has(u));
  if (leak.length) fail(`sitemap lists ${leak.length} untranslated mirrors: ${leak.slice(0, 2)}`);
  else ok('sitemap contains no untranslated mirror');
  if (missing.length) fail(`sitemap omits ${missing.length} published pages: ${missing.slice(0, 2)}`);
  else ok('sitemap covers every published page');
}

console.log('== 3. llms-full.txt ==');
{
  const srcs = [...read('llms-full.txt').matchAll(/<!-- source: (\S+)/g)].map((m) => new URL(m[1]).pathname);
  const leak = srcs.filter((u) => untranslated.has(u) && !indexable.has(u));
  if (leak.length) fail(`llms-full.txt contains ${leak.length} untranslated mirrors: ${leak.slice(0, 2)}`);
  else ok('llms-full.txt contains only published documents');
  const missing = [...indexable].filter((u) => !srcs.includes(u));
  if (missing.length) fail(`llms-full.txt omits ${missing.length} published pages`);
  else ok(`llms-full.txt covers all ${indexable.size} published documents`);
}

console.log('== 4. rss.xml ==');
{
  // Only <item> links are content entries; the channel-level <link> is the
  // site root and would otherwise look like a stray non-original page.
  const links = [...read('rss.xml').matchAll(/<item>[\s\S]*?<link>([^<]+)<\/link>/g)].map((m) => new URL(m[1]).pathname);
  // "Original" means is_translation === false, not "language === ru": the
  // references/usd/color articles are originals written in English. Checking
  // by language would demand an English RSS entry be removed.
  const origUrls = new Set(rows.filter((r) => !r.isTr).map((r) => r.url));
  const badLinks = links.filter((u) => !origUrls.has(u));
  if (badLinks.length) fail(`rss.xml lists ${badLinks.length} non-original pages: ${badLinks.slice(0, 2)}`);
  else ok(`rss.xml lists ${links.length} originals only (English originals included)`);
}

console.log('== 5. markdown twins exist for every published article ==');
{
  const missing = [...indexable].filter((u) => !existsSync(join(DIST, `${u}.md`)));
  if (missing.length) fail(`${missing.length} indexable pages have no .md twin: ${missing.slice(0, 2)}`);
  else ok('every indexable page has a .md twin');
}

console.log();
if (fails.length) {
  console.log(`RESULT: FAIL (${fails.length} issues)`);
  process.exit(1);
}
console.log('RESULT: OK');
