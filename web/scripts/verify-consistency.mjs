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

const slugify = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
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
const indexable = new Set(rows.filter((r) => !r.isTr || r.tr === 'human').map((r) => r.url));
const dupes = new Set(rows.filter((r) => !isShadow(r) && r.isTr && r.tr && r.tr !== 'human').map((r) => r.url));

console.log('== Classification ==');
console.log(`  indexable=${indexable.size} duplicates=${dupes.size} shadows(unpublished)=${shadows.length}`);

console.log('== 1. robots meta on disk agrees with classification ==');
let bad = 0;
for (const url of [...indexable, ...dupes]) {
  const f = join(DIST, `${url}.html`);
  if (!existsSync(f)) continue;
  const m = /<meta name="robots" content="([^"]*)"/.exec(read(`${url}.html`))?.[1] ?? '';
  const want = indexable.has(url);
  if (want && m.includes('noindex')) { bad++; if (bad <= 3) fail(`indexable but noindex: ${url}`); }
  if (!want && !m.includes('noindex')) { bad++; if (bad <= 3) fail(`duplicate not noindex: ${url}`); }
}
if (!bad) ok('robots meta matches the classification on every page');

console.log('== 2. sitemap ==');
{
  const idx = read('sitemap-index.xml');
  const child = /<loc>([^<]+)<\/loc>/.exec(idx)?.[1] ?? '';
  const rel = child.replace(/^https?:\/\/[^/]+/, '');
  const sm = read(rel.replace(/^\//, ''));
  const urls = new Set([...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname));
  const leak = [...urls].filter((u) => dupes.has(u));
  const missing = [...indexable].filter((u) => !urls.has(u));
  if (leak.length) fail(`sitemap lists ${leak.length} noindex mirrors: ${leak.slice(0, 2)}`);
  else ok('sitemap contains no noindex mirror');
  if (missing.length) fail(`sitemap omits ${missing.length} indexable pages: ${missing.slice(0, 2)}`);
  else ok('sitemap covers every indexable page');
}

console.log('== 3. llms-full.txt ==');
{
  const srcs = [...read('llms-full.txt').matchAll(/<!-- source: (\S+)/g)].map((m) => new URL(m[1]).pathname);
  const leak = srcs.filter((u) => dupes.has(u));
  if (leak.length) fail(`llms-full.txt contains ${leak.length} noindex mirrors: ${leak.slice(0, 2)}`);
  else ok('llms-full.txt contains only indexable documents');
  const missing = [...indexable].filter((u) => !srcs.includes(u));
  if (missing.length) fail(`llms-full.txt omits ${missing.length} indexable pages`);
  else ok(`llms-full.txt covers all ${indexable.size} indexable documents`);
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
