/**
 * Invariant tests over the built site.
 *
 * The unit tests in site-logic.test.ts prove the rules are implemented
 * correctly; these prove the built output actually obeys them. They run against
 * dist/, so they need a build first (npm test does that for you).
 *
 * The build gates check most of this too. That is deliberate, not redundant: the
 * gate stops a bad deploy, this is a test suite that can be run, read and
 * pointed at a single URL.
 */
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, relative, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const DIST = join(ROOT, 'dist');
const DB = join(ROOT, '..', 'WIKI', 'db', 'wiki_database.json');

const slugify = (s) =>
  s.toLowerCase().replace(/\.md$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
const origOf = (m) => m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');

let db, htmls, published, shadows, categories, langs;

before(() => {
  assert.ok(existsSync(DIST), 'dist/ is missing — run `npm run build:full` first');
  db = JSON.parse(readFileSync(DB, 'utf8'));

  const origLang = new Map();
  for (const e of db.entries) {
    const m = e.meta;
    if (!m.is_translation) origLang.set(origOf(m), m.language);
  }
  const isShadow = (m) => m.is_translation && origLang.get(origOf(m)) === m.language;
  published = db.entries
    .filter((e) => !isShadow(e.meta))
    .map((e) => ({
      url: `/${e.meta.language}/${e.meta.category || 'references'}/${slugify(origOf(e.meta))}`,
      id: e.meta.id,
      lang: e.meta.language,
      category: e.meta.category || 'references',
      indexable: !e.meta.is_translation || e.meta.translation === 'human',
    }));
  shadows = db.entries.filter((e) => isShadow(e.meta)).length;

  categories = new Set(published.map((p) => p.category));
  langs = ['ru', 'en', 'es', 'de', 'zh'];

  htmls = [];
  const walk = (d) => {
    for (const n of readdirSync(d)) {
      const p = join(d, n);
      if (statSync(p).isDirectory()) walk(p);
      else if (n.endsWith('.html')) htmls.push(p);
    }
  };
  walk(DIST);
});

/* ------------------------------------------------------------- published set */

test('every published entry has exactly one HTML page', () => {
  const missing = published.filter((p) => !existsSync(join(DIST, `${p.url}.html`)));
  assert.deepEqual(missing.map((p) => p.url), [], 'published entries with no page');
});

test('no two published entries claim the same URL', () => {
  const seen = new Map();
  const dupes = [];
  for (const p of published) {
    if (seen.has(p.url)) dupes.push(`${p.url}: ${seen.get(p.url)} and ${p.id}`);
    seen.set(p.url, p.id);
  }
  assert.deepEqual(dupes, []);
});

test('shadow mirrors are not published', () => {
  // A shadow shares its original's URL, so its page is the original's. What it
  // must not do is appear as a *separate* file.
  const byUrl = new Map(published.map((p) => [p.url, p]));
  assert.equal(shadows, 163, `shadow count changed: ${shadows} (was 163 — check the rule, not the test)`);
  assert.equal(byUrl.size, published.length);
});

/* ---------------------------------------------------------- markdown twins */

test('every published page has a .md twin with the same id', () => {
  // The whole point of a twin is that it is the same document. 167 pages once
  // advertised a twin holding a shadow's content.
  const bad = [];
  for (const p of published) {
    const t = join(DIST, `${p.url}.md`);
    if (!existsSync(t)) { bad.push(`${p.url}: no twin`); continue; }
    // (.+) not (\S+): five ids contain a space.
    const id = /^id:\s*(.+)$/m.exec(readFileSync(t, 'utf8'))?.[1]?.trim();
    if (id !== p.id) bad.push(`${p.url}: twin id=${id} page id=${p.id}`);
  }
  assert.deepEqual(bad.slice(0, 10), []);
  assert.equal(bad.length, 0, `${bad.length} twin(s) wrong`);
});

test('no twin exists for a URL with no page', () => {
  const orphans = published
    .filter((p) => !existsSync(join(DIST, `${p.url}.html`)))
    .filter((p) => existsSync(join(DIST, `${p.url}.md`)));
  assert.deepEqual(orphans.map((o) => o.url), []);
});

/* ------------------------------------------------------------------ links */

test('every internal href resolves, relative ones included', () => {
  // The original gate regex required a leading slash, so it inspected 22 668 of
  // 51 164 hrefs and reported "no broken internal links" while 2 227 were
  // broken. Relative hrefs are resolved here the way a browser does.
  const resolve = (base, rel) => {
    const out = base.split('/');
    for (const s of rel.split('/')) {
      if (!s || s === '.') continue;
      if (s === '..') out.pop();
      else out.push(s);
    }
    return out.join('/');
  };
  const broken = [];
  let checked = 0;
  for (const f of htmls) {
    const pageUrl = ('/' + relative(DIST, f).replace(/\\/g, '/'))
      .replace(/index\.html$/, '').replace(/\.html$/, '');
    for (const m of readFileSync(f, 'utf8').matchAll(/href="([^"]+)"/g)) {
      const href = m[1];
      if (/^(https?:|mailto:|tel:|data:|\/\/|#)/i.test(href)) continue;
      const p = href.split('#')[0].split('?')[0];
      if (!p) continue;
      checked++;
      const abs = p.startsWith('/') ? p : resolve(pageUrl, p);
      const t = abs.replace(/\/$/, '');
      const ok = [
        join(DIST, abs.endsWith('/') ? abs + 'index.html' : abs + '.html'),
        join(DIST, abs),
        join(DIST, t + '.html'),
        join(DIST, t, 'index.html'),
      ].some((x) => existsSync(x));
      if (!ok && broken.length < 10) broken.push(`${relative(DIST, f)} -> ${href}`);
    }
  }
  assert.deepEqual(broken, []);
  assert.ok(checked > 1000, `only ${checked} hrefs inspected — the check may be degenerate`);
});

test('no link points at a .md path other than the page own twin', () => {
  // Bodies are written with markdown links, so the renderer must have rewritten
  // them to site URLs. The one `.md` href a page may legitimately carry is a
  // link to its own markdown version — that is the llms.txt v2 contract, offered
  // to the reader as well as declared in <head>. Anything else ending in .md is
  // an unrewritten body link, which is the defect (2 227 of them once).
  const survivors = [];
  for (const f of htmls) {
    const t = readFileSync(f, 'utf8');
    const pageUrl = ('/' + relative(DIST, f).replace(/\\/g, '/'))
      .replace(/index\.html$/, '').replace(/\.html$/, '');
    const own = new Set([`${pageUrl}.md`, `https://blender-skills.refertur.net${pageUrl}.md`]);
    for (const a of t.matchAll(/<a [^>]*href="([^"]+\.md)"/g)) {
      if (!own.has(a[1])) survivors.push(`${relative(DIST, f)} -> ${a[1]}`);
    }
  }
  assert.deepEqual(survivors.slice(0, 10), []);
  assert.equal(survivors.length, 0, `${survivors.length} link(s) still point at a foreign .md path`);
});

test('every article page offers its own markdown twin as a link', () => {
  // Scoped to article pages. Category pages and the 404 have no twin, so
  // requiring one of them to link to a .md would be a wrong requirement — the
  // first version of this test failed on exactly those 82.
  const missing = [];
  for (const p of published) {
    const t = readFileSync(join(DIST, `${p.url}.html`), 'utf8');
    if (!t.includes(`href="https://blender-skills.refertur.net${p.url}.md"`)) missing.push(p.url);
    if (!/<link rel="alternate" type="text\/markdown"/.test(t)) missing.push(`${p.url} (no head alternate)`);
  }
  assert.deepEqual(missing.slice(0, 10), []);
  assert.equal(missing.length, 0, `${missing.length} article page(s) do not advertise their twin`);
});

test('every page declares the same canonical origin', () => {
  // The invariant is about what the page *declares* — canonical, og:url, the
  // JSON-LD @id — not about every URL that appears in the text. The corpus
  // legitimately documents local endpoints (Ollama on :11434, ComfyUI on
  // :8188, MCP servers on :8080); an earlier version of this test flagged those
  // 41 mentions and would have pushed someone to "fix" correct documentation.
  const seen = new Map();
  const local = [];
  for (const f of htmls) {
    const t = readFileSync(f, 'utf8');
    const canon = /<link rel="canonical" href="([^"]+)"/.exec(t)?.[1];
    if (canon) {
      const host = new URL(canon).host;
      if (/^(localhost|127\.0\.0\.1)$/.test(host)) local.push(`${relative(DIST, f)}: ${canon}`);
      if (!seen.has(host)) seen.set(host, 0);
      seen.set(host, seen.get(host) + 1);
    }
  }
  assert.deepEqual(local, [], 'a page canonicalises to localhost');
  assert.equal(seen.size, 1, `pages declare ${seen.size} different origins: ${[...seen.keys()].join(', ')}`);
});

/* --------------------------------------------------------- thin pages, sitemap */

test('a category page with no articles is noindex', () => {
  const empty = [];
  for (const lang of langs) {
    for (const cat of categories) {
      const f = join(DIST, lang, cat, 'index.html');
      const f2 = join(DIST, `${lang}/${cat}.html`);
      const file = existsSync(f) ? f : existsSync(f2) ? f2 : null;
      if (!file) continue;
      const n = published.filter((p) => p.lang === lang && p.category === cat && p.indexable).length;
      if (n > 0) continue;
      empty.push(file);
      const robots = /<meta name="robots" content="([^"]+)"/.exec(readFileSync(file, 'utf8'))?.[1] ?? '';
      assert.match(robots, /noindex/, `${lang}/${cat} is empty but indexable`);
    }
  }
  assert.ok(empty.length > 0, 'no empty category pages found — the check is not exercising anything');
});

test('the sitemap contains no noindex URL', () => {
  const sm = readdirSync(DIST)
    .filter((f) => /^sitemap-\d+\.xml$/.test(f))
    .map((f) => readFileSync(join(DIST, f), 'utf8'))
    .join('');
  const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname);
  const offenders = [];
  for (const p of locs) {
    const f = join(DIST, `${p.replace(/^\//, '').replace(/\/$/, '')}.html`);
    if (!existsSync(f)) continue;
    const robots = /<meta name="robots" content="([^"]+)"/.exec(readFileSync(f, 'utf8'))?.[1] ?? '';
    if (/noindex/.test(robots)) offenders.push(p);
  }
  assert.deepEqual(offenders.slice(0, 10), []);
});

/* ------------------------------------------------------------------ origin */

test('the machine-readable layer agrees with the canonical origin', () => {
  // Sitemap, robots.txt and llms.txt must all name the same host the pages
  // canonicalise to, or a crawler is told one story and the pages tell another.
  const hosts = new Set();
  const canonHost = new Map();
  for (const f of htmls) {
    const c = /<link rel="canonical" href="([^"]+)"/.exec(readFileSync(f, 'utf8'))?.[1];
    if (c) canonHost.set(new URL(c).host, (canonHost.get(new URL(c).host) || 0) + 1);
  }
  assert.equal(canonHost.size, 1, `pages canonicalise to ${canonHost.size} hosts`);
  hosts.add([...canonHost.keys()][0]);

  for (const f of readdirSync(DIST).filter((x) => /^sitemap-\d+\.xml$/.test(x))) {
    for (const m of readFileSync(join(DIST, f), 'utf8').matchAll(/<loc>https?:\/\/([^/<]+)/g)) hosts.add(m[1]);
  }
  const robotsSm = /^Sitemap:\s*https?:\/\/([^/]+)/m.exec(readFileSync(join(DIST, 'robots.txt'), 'utf8'))?.[1];
  if (robotsSm) hosts.add(robotsSm);
  for (const m of readFileSync(join(DIST, 'llms.txt'), 'utf8').matchAll(/\]\(https?:\/\/([^/]+)/g)) hosts.add(m[1]);

  assert.equal(hosts.size, 1, `pages, sitemap, robots and llms.txt name ${hosts.size} hosts: ${[...hosts].join(', ')}`);
});
