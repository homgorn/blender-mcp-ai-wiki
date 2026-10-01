#!/usr/bin/env node
/**
 * SEO / AI-readiness gate for the built site.
 *
 * Parses dist/ and fails loudly. "SEO optimized" is a claim; this is the proof.
 * Everything here maps to a documented requirement:
 *   - title / description / canonical / robots           -> crawlability
 *   - hreflang cluster, reciprocal + x-default           -> Google multi-language
 *   - JSON-LD Article + BreadcrumbList                   -> rich results
 *   - .md twin + rel=alternate                           -> llms.txt v2
 *   - llms.txt / llms-full.txt / robots.txt / rss.xml    -> agent entry points
 *   - no broken internal links                           -> crawl budget
 *
 * Run:  node scripts/verify-seo.mjs        (exit 1 on any FAIL)
 */
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const DIST = join(HERE, '..', 'dist');
const DB = join(HERE, '..', '..', 'WIKI', 'db', 'wiki_database.json');

const fails = [];
const warns = [];
const fail = (m) => fails.push(m);
const warn = (m) => warns.push(m);
const ok = (m) => console.log(`  [OK] ${m}`);

const slugify = (s) => s.toLowerCase().replace(/\.md$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
const read = (p) => readFileSync(join(DIST, p), 'utf8');

/* --------------------------------------------------------- ground truth */
const db = JSON.parse(readFileSync(DB, 'utf8'));
const entries = db.entries.map((e) => {
  const m = e.meta;
  const origId = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
  return {
    id: m.id,
    origId,
    lang: m.language,
    category: m.category || 'references',
    title: m.title,
    translation: m.translation,
    isTranslation: Boolean(m.is_translation),
    url: `/${m.language}/${m.category || 'references'}/${slugify(origId)}`,
  };
});
const indexable = entries.filter((e) => !e.isTranslation || e.translation === 'human');
/**
 * Mirrors published but marked noindex (excluded from the sitemap).
 * Mirrors whose language equals the original's language are NOT published at
 * all (they would collide on the same URL) — see dropShadowMirrors in
 * src/lib/content.ts. Checking those for noindex would demand the impossible.
 */
const originalLang = new Map();
for (const e of entries) {
  if (!e.isTranslation) originalLang.set(e.origId, e.lang);
}
const isShadow = (e) => e.isTranslation && originalLang.get(e.origId) === e.lang;
const duplicates = entries.filter(
  (e) => e.isTranslation && e.translation && e.translation !== 'human' && !isShadow(e),
);
const shadows = entries.filter(isShadow);
const shadowUrls = new Set(shadows.map((e) => e.url));

/* ----------------------------------------------------- file existence */
console.log('== 1. Build output present ==');
for (const f of ['index.html', 'llms.txt', 'llms-full.txt', 'robots.txt', 'rss.xml', 'sitemap-index.xml', '404.html', '_headers', 'og-default.png']) {
  if (existsSync(join(DIST, f))) ok(`dist/${f}`);
  else fail(`dist/${f} missing`);
}

// A localhost origin means canonical, hreflang, OG and the sitemap all point at
// a machine that does not exist. Never ship that.
{
  const home = read('index.html');
  const m = /<link rel="canonical" href="([^"]+)"/.exec(home)?.[1] ?? '';
  if (/^https?:\/\/(localhost|127\.0\.0\.1)/.test(m)) {
    fail(`built with a local origin (${m}) — set PUBLIC_SITE_URL before deploying`);
  } else {
    ok(`canonical origin: ${m}`);
  }
}

/* --------------------------------------------------------- article pages */
console.log('== 2. Article pages: head tags, JSON-LD, hreflang, md twin ==');
let checked = 0;
for (const e of indexable) {
  const file = join(DIST, `${e.url}.html`);
  if (!existsSync(file)) { fail(`article html missing: ${e.url}`); continue; }
  const html = readFileSync(file, 'utf8');
  const problems = [];

  const title = /<title>([^<]*)<\/title>/.exec(html)?.[1] ?? '';
  if (!title) problems.push('no <title>');
  else if (title.length > 70) problems.push(`title ${title.length} chars (>70)`);

  const desc = /<meta name="description" content="([^"]*)"/.exec(html)?.[1] ?? '';
  // Script-aware floor: 50 Latin characters is a sentence, 50 CJK characters is
  // a paragraph. Judging both by 50 falsely fails every Chinese page.
  const descMin = /[぀-ヿ㐀-䶿一-鿿]/.test(e.title) ? 30 : 50;
  if (!desc) problems.push('no meta description');
  else if (desc.length < descMin) problems.push(`description only ${desc.length} chars (<${descMin})`);
  else if (desc.length > 320) problems.push(`description ${desc.length} chars (>320)`);

  if (!/<link rel="canonical" href="[^"]+"/.test(html)) problems.push('no canonical');
  if (!/<meta property="og:title"/.test(html)) problems.push('no og:title');
  if (!/<meta property="og:description"/.test(html)) problems.push('no og:description');
  if (!/<meta property="og:image"/.test(html)) problems.push('no og:image');
  if (!/<meta name="twitter:card"/.test(html)) problems.push('no twitter:card');
  if (!/<html lang="/.test(html)) problems.push('no lang on <html>');
  if (!/<meta name="robots" content="index/.test(html)) problems.push('indexable page is not "index"');

  // JSON-LD: collect the union of types across every ld+json block on the page.
  // A page emits Article+BreadcrumbList in one block and FAQPage in another, so
  // checking each block separately produces false failures.
  const ldTypes = new Set();
  let ldCount = 0;
  for (const m of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    ldCount++;
    try {
      const node = JSON.parse(m[1]);
      for (const n of node['@graph'] ?? [node]) {
        const t = n['@type'];
        if (Array.isArray(t)) t.forEach((x) => ldTypes.add(x));
        else if (t) ldTypes.add(t);
      }
    } catch {
      problems.push('JSON-LD is not valid JSON');
    }
  }
  if (ldCount === 0) problems.push('no JSON-LD at all');
  if (!ldTypes.has('Article')) problems.push('JSON-LD without Article');
  if (!ldTypes.has('BreadcrumbList')) problems.push('JSON-LD without BreadcrumbList');

  // hreflang: own lang + x-default
  if (!/hreflang="x-default"/.test(html)) problems.push('no hreflang x-default');
  const own = { ru: 'ru-RU', en: 'en-US', es: 'es-ES', de: 'de-DE', zh: 'zh-CN' }[e.lang];
  if (!html.includes(`hreflang="${own}"`)) problems.push(`no self hreflang ${own}`);

  // llms.txt v2 markdown twin
  if (!/<link rel="alternate" type="text\/markdown"/.test(html)) problems.push('no markdown twin link');
  if (!existsSync(join(DIST, `${e.url}.md`))) problems.push('markdown twin file missing');

  if ((html.match(/<h1[\s>]/g) || []).length !== 1) problems.push('not exactly one <h1>');

  if (problems.length) fail(`${e.url}: ${problems.join('; ')}`);
  checked++;
}
if (!fails.length) ok(`${checked} indexable articles pass all head/JSON-LD/hreflang checks`);

/* --------------------------------------- duplicates must be de-duplicated */
console.log('== 3. Template mirrors: noindex + canonical to original ==');
let dupOk = 0;
for (const e of duplicates) {
  if (shadowUrls.has(e.url)) continue;   // owned by the original, not by the mirror
  const file = join(DIST, `${e.url}.html`);
  if (!existsSync(file)) { fail(`mirror page missing: ${e.url}`); continue; }
  const html = readFileSync(file, 'utf8');
  const problems = [];
  if (!/<meta name="robots" content="noindex/.test(html)) problems.push('missing noindex');
  const canon = /<link rel="canonical" href="([^"]+)"/.exec(html)?.[1] ?? '';
  if (!canon || canon.endsWith(e.url)) problems.push(`canonical not pointing at original (${canon})`);
  if (problems.length) fail(`${e.url}: ${problems.join('; ')}`);
  else dupOk++;
}
ok(`${dupOk} template mirrors carry noindex + canonical-to-origin`);
ok(`${shadows.length} shadow mirrors correctly not published (URL owned by the original)`);

/* --------------------------------------------------- markdown twin fidelity */
console.log('== 3b. Markdown twins match their page ==');
{
  // llms.txt v2 promises: "the .md at the same URL is this article in
  // markdown". Nothing checked that. 167 of 834 pages advertised a twin whose
  // frontmatter named a different entry than the page it was advertised on —
  // a shadow mirror had overwritten the original's twin at the shared URL, so
  // the HTML said `index, follow` while the .md said `translation: template`
  // and carried an injected banner. The twin is the whole point for agents, so
  // a twin that is a different document is a correctness failure, not a
  // cosmetic one.
  const idByUrl = new Map();
  const origLang = new Map();
  for (const e of db.entries) {
    const m = e.meta ?? {};
    const oid = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
    if (!m.is_translation) origLang.set(oid, m.language);
  }
  for (const e of db.entries) {
    const m = e.meta ?? {};
    const oid = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
    // Mirror the published rule: a translation in the original's own language
    // is not published.
    if (m.is_translation && origLang.get(oid) === m.language) continue;
    const url = `/${m.language}/${m.category || 'references'}/${slugify(oid)}`;
    idByUrl.set(url, m.id);
  }

  let checked = 0;
  const mismatched = [];
  const missing = [];
  for (const [url, wantId] of idByUrl) {
    const twin = join(DIST, `${url}.md`);
    const page = join(DIST, `${url}.html`);
    if (!existsSync(page)) continue;          // shadow: neither should exist
    if (!existsSync(twin)) { missing.push(url); continue; }
    const t = readFileSync(twin, 'utf8');
    // `(.+)` not `(\S+)`: five ids legitimately contain a space
    // (`case_14_food_r visualisation`), and \S+ truncated them, so the gate
    // reported five false mismatches the first time it ran.
    const gotId = /^id:\s*(.+)$/m.exec(t)?.[1]?.trim();
    checked++;
    if (gotId !== wantId) mismatched.push(`${url}: twin id=${gotId} page id=${wantId}`);
  }
  if (missing.length) fail(`${missing.length} published page(s) have no .md twin: ${missing.slice(0, 3)}`);
  else ok(`every one of ${checked} published pages has a .md twin`);

  if (mismatched.length) {
    for (const m of mismatched.slice(0, 5)) fail(`twin is a different document — ${m}`);
    fail(`${mismatched.length} .md twin(s) do not match the page they are served with`);
  } else {
    ok(`all ${checked} .md twins carry the same id as their page`);
  }
}

/* ------------------------------------------------------------- sitemap */
console.log('== 4. sitemap ==');
{
  const idx = read('sitemap-index.xml');
  const child = /<loc>([^<]+sitemap[^<]*)<\/loc>/.exec(idx)?.[1];
  if (!child) fail('sitemap-index.xml has no child sitemap');
  else {
    const rel = child.replace(/^https?:\/\/[^/]+/, '');
    const smPath = join(DIST, rel);
    if (!existsSync(smPath)) fail(`sitemap ${rel} missing`);
    else {
      const sm = readFileSync(smPath, 'utf8');
      const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
      ok(`sitemap: ${locs.length} urls`);
      const md = locs.filter((l) => l.endsWith('.md'));
      if (md.length) fail(`sitemap contains ${md.length} .md urls`);
      else ok('sitemap excludes .md twins');
      const search = locs.filter((l) => /\/search(\?|$)/.test(l));
      if (search.length) fail(`sitemap contains ${search.length} /search urls`);
      else ok('sitemap excludes search pages');
      const dupLocs = locs.filter((l) => duplicates.some((d) => new URL(l).pathname === d.url));
      if (dupLocs.length) fail(`sitemap contains ${dupLocs.length} noindex mirror urls`);
      else ok('sitemap excludes noindex mirrors');

      // Coverage: the sitemap must equal the set of indexable pages that exist on
      // disk. This is the check that catches rule drift between the page builder
      // and the sitemap filter.
      const onDisk = indexable.filter((e) => existsSync(join(DIST, `${e.url}.html`)));
      const inSitemap = new Set(locs.map((l) => new URL(l).pathname));
      const missing = onDisk.filter((e) => !inSitemap.has(e.url));
      if (missing.length) {
        fail(`sitemap omits ${missing.length} indexable pages: ${missing.slice(0, 3).map((e) => e.url)}`);
      } else {
        ok(`sitemap covers all ${onDisk.length} indexable articles`);
      }
      if (!/xhtml:link/.test(sm)) warn('sitemap has no xhtml:link hreflang group');
      else ok('sitemap has xhtml:link hreflang groups');
    }
  }
}

/* ------------------------------------------- empty category pages (thin) */
console.log('== 4d. Empty category pages ==');
{
  // 48 category pages had no articles in their language and were published
  // index,follow inside the sitemap. Handing Google 48 empty pages is exactly
  // the kind of thin content the SEO work exists to prevent.
  //
  // The emptiness rule is implemented twice on purpose: `categoryHasContent` in
  // src/lib/content.ts drives the page's robots meta, and `emptyCategoryPaths`
  // in astro.config.mjs drives the sitemap. The config runs before TS loads, so
  // it cannot import the helper. This block is what makes the duplication safe:
  // it recomputes the set from the database and checks the built pages against
  // it, in both directions.
  const filled = new Set();
  const cats = new Set();
  for (const e of db.entries) {
    const m = e.meta ?? {};
    if (m.category) cats.add(m.category);
    const indexable = !m.is_translation || m.translation === 'human';
    if (indexable && m.language && m.category) filled.add(`${m.language}/${m.category}`);
  }
  const expectedEmpty = new Set();
  for (const cat of cats) {
    for (const l of ['ru', 'en', 'es', 'de', 'zh']) {
      if (!filled.has(`${l}/${cat}`)) expectedEmpty.add(`/${l}/${cat}`);
    }
  }

  // (1) None of them may be in the sitemap.
  const smFiles = readdirSync(DIST).filter((f) => /^sitemap-\d+\.xml$/.test(f));
  const smLocs = smFiles.flatMap((f) =>
    [...readFileSync(join(DIST, f), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname));
  const leaked = smLocs.filter((p) => expectedEmpty.has(p));
  if (leaked.length) fail(`sitemap contains ${leaked.length} empty category page(s): ${leaked.slice(0, 3)}`);
  else ok(`sitemap excludes all ${expectedEmpty.size} empty category pages`);

  // (2) Every published one must actually be empty, and must be noindex.
  let scanned = 0;
  const notEmpty = [];
  const indexableButEmpty = [];
  for (const p of expectedEmpty) {
    const f = join(DIST, `${p}.html`);
    if (!existsSync(f)) continue;
    scanned++;
    const html = readFileSync(f, 'utf8');
    const [, l, cat] = /^\/([a-z]{2})\/([^/]+)$/.exec(p);
    // An article link is a path two segments deeper: /{lang}/{category}/{slug}.
    const links = [...html.matchAll(new RegExp(`href="/${l}/${cat}/[^"#]+"`, 'g'))];
    if (links.length) notEmpty.push(p);
    const robots = /<meta name="robots" content="([^"]+)"/.exec(html)?.[1] ?? '';
    if (!/noindex/.test(robots)) indexableButEmpty.push(p);
  }
  if (notEmpty.length) {
    fail(`${notEmpty.length} page(s) counted as empty but list articles: ${notEmpty.slice(0, 3)}`);
  } else {
    ok(`all ${scanned} published empty category pages list no articles`);
  }
  if (indexableButEmpty.length) {
    fail(`${indexableButEmpty.length} empty category page(s) are not noindex: ${indexableButEmpty.slice(0, 3)}`);
  } else {
    ok('every empty category page is noindex');
  }
}

/* ------------------------------------------------------------- llms.txt */
console.log('== 4c. Syntax highlighting ==');
{
  // Measured on the artifact, not asserted by the build script: Astro
  // re-evaluates components per page, so a "log once" guard is not available.
  let shiki = 0;
  let plain = 0;
  const sample = indexable.slice(0, 60);
  for (const e of sample) {
    const f = join(DIST, `${e.url}.html`);
    if (!existsSync(f)) continue;
    const html = readFileSync(f, 'utf8');
    shiki += (html.match(/class="shiki/g) || []).length;
    plain += (html.match(/<pre><code/g) || []).length;
  }
  if (shiki === 0 && plain === 0) {
    warn('no code blocks found in the sampled pages — nothing to verify');
  } else if (plain > 0) {
    fail(`${plain} unhighlighted code block(s) remain in the sample (${shiki} highlighted)`);
  } else {
    ok(`all ${shiki} code blocks in the sample are highlighted`);
  }
}

console.log('== 4b. Open Graph image ==');
{
  const og = join(DIST, 'og-default.png');
  if (!existsSync(og)) {
    fail('dist/og-default.png missing — every og:image and twitter:image points at it');
  } else {
    const buf = readFileSync(og);
    const isPng = buf.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
    if (!isPng) fail('og-default.png is not a PNG');
    // IHDR width/height are big-endian at bytes 16..24
    const w = buf.readUInt32BE(16);
    const h = buf.readUInt32BE(20);
    if (w < 1200 || h < 630) fail(`OG image is ${w}x${h}; recommended 1200x630`);
    else ok(`og-default.png ${w}x${h}, ${Math.round(buf.length / 1024)} KB`);
  }
}

console.log('== 5. llms.txt / robots.txt / rss.xml ==');
{
  const llms = read('llms.txt');
  const lines = llms.split('\n');
  if (!/^#\s+\S/.test(lines[0])) fail('llms.txt: first line must be an H1');
  else ok('llms.txt: H1 present');
  if (!lines.some((l) => l.startsWith('> '))) fail('llms.txt: missing blockquote summary');
  else ok('llms.txt: blockquote summary present');
  const links = [...llms.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)].map((m) => m[2]);
  if (links.length < 5) fail(`llms.txt: only ${links.length} links`);
  else ok(`llms.txt: ${links.length} links`);
  const bad = links.filter((h) => {
    const p = h.replace(/^https?:\/\/[^/]+/, '');
    if (p === '/') return !existsSync(join(DIST, 'index.html'));
    return !existsSync(join(DIST, p.replace(/\/$/, '') + '.html')) && !existsSync(join(DIST, p));
  });
  if (bad.length) fail(`llms.txt: ${bad.length} dead links: ${bad.slice(0, 3)}`);
  else ok('llms.txt: all internal links resolve');

  const full = read('llms-full.txt');
  const docs = (full.match(/<!-- source:/g) || []).length;
  if (docs < indexable.length) fail(`llms-full.txt: ${docs} docs < ${indexable.length} indexable`);
  else ok(`llms-full.txt: ${docs} documents`);

  const robots = read('robots.txt');
  for (const [name, re] of [
    ['User-agent: *', /User-agent:\s*\*/],
    ['Sitemap', /^Sitemap:\s*https?:\/\//m],
    ['OAI-SearchBot', /User-agent:\s*OAI-SearchBot/],
    ['ClaudeBot', /User-agent:\s*ClaudeBot/],
    ['GPTBot', /User-agent:\s*GPTBot/],
    ['PerplexityBot', /User-agent:\s*PerplexityBot/],
  ]) {
    if (!re.test(robots)) fail(`robots.txt: missing ${name}`);
  }
  ok('robots.txt: general + AI crawler rules + sitemap');

  const rss = read('rss.xml');
  const items = (rss.match(/<item>/g) || []).length;
  if (items < 10) fail(`rss.xml: only ${items} items`);
  else ok(`rss.xml: ${items} items`);
}

/* --------------------------------------------------- broken internal links */
console.log('== 6. Internal links across all HTML ==');
{
  const htmls = [];
  const walk = (dir) => {
    for (const n of readdirSync(dir)) {
      const p = join(dir, n);
      if (statSync(p).isDirectory()) walk(p);
      else if (n.endsWith('.html')) htmls.push(p);
    }
  };
  walk(DIST);

  /**
   * Resolve a path the way a browser does, collapsing `.` and `..`.
   *
   * The previous regex was /href="(\/[^"#]*)(#[^"]*)?"/ — it required a leading
   * slash, so it only ever inspected absolute hrefs: 22 668 of 51 164 on this
   * site. Every relative href was invisible to it, which is why the gate
   * printed "no broken internal links" while 2 227 of them, on 446 pages, went
   * to URLs that do not exist. A check that cannot fail is worse than no check,
   * because it is read as a passing result.
   */
  const resolve = (base, rel) => {
    const out = base.startsWith('/') ? base.split('/') : [];
    for (const seg of rel.split('/')) {
      if (!seg || seg === '.') continue;
      if (seg === '..') out.pop();
      else out.push(seg);
    }
    return out.join('/');
  };

  const broken = new Map();
  let inspected = 0;
  for (const f of htmls) {
    const html = readFileSync(f, 'utf8');
    // This page's own URL, e.g. /ru/cases/case-01-x
    let pageUrl = '/' + relative(DIST, f).replace(/\\/g, '/');
    pageUrl = pageUrl.replace(/index\.html$/, '').replace(/\.html$/, '');
    for (const m of html.matchAll(/href="([^"]+)"/g)) {
      const href = m[1];
      if (/^(https?:|mailto:|tel:|data:|\/\/|#)/i.test(href)) continue;
      inspected++;
      const path = href.split('#')[0].split('?')[0];
      if (!path) continue;
      const abs = path.startsWith('/') ? path : resolve(pageUrl, path);
      const trimmed = abs.replace(/\/$/, '');
      const cand = [
        join(DIST, abs.endsWith('/') ? abs + 'index.html' : abs + '.html'),
        join(DIST, abs),
        join(DIST, trimmed + '.html'),
        join(DIST, trimmed, 'index.html'),
        join(DIST, abs),                       // assets and .md twins live as-is
      ];
      if (!cand.some((p) => existsSync(p))) {
        if (!broken.has(href)) broken.set(href, relative(DIST, f));
      }
    }
  }
  if (broken.size) {
    for (const [href, from] of [...broken].slice(0, 10)) fail(`broken link ${href} (in ${from})`);
    fail(`total broken internal links: ${broken.size}`);
  } else {
    ok(`no broken internal links (${inspected} hrefs checked across ${htmls.length} HTML files)`);
  }
}

/* --------------------------------------------------------------- report */
console.log();
if (warns.length) { console.log('WARN:'); for (const w of warns) console.log('  - ' + w); console.log(); }
if (fails.length) {
  console.log(`RESULT: FAIL (${fails.length} issues)`);
  for (const f of fails.slice(0, 30)) console.log('  - ' + f);
  process.exit(1);
}
console.log(`RESULT: OK  (${indexable.length} indexable pages, ${duplicates.length} de-duplicated mirrors)`);
