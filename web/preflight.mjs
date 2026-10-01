#!/usr/bin/env node
/**
 * Pre-deploy gate. Cheap checks that must pass BEFORE `wrangler deploy`,
 * because a failed deploy after a full build wastes minutes.
 *
 *   node preflight.mjs
 */
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const fails = [];
const fail = (m) => { fails.push(m); console.log(`  [FAIL] ${m}`); };
const ok = (m) => console.log(`  [OK] ${m}`);

console.log('== 1. Environment ==');
const site = (process.env.PUBLIC_SITE_URL || '').trim();
if (!site) {
  fail('PUBLIC_SITE_URL is not set — canonical/hreflang/sitemap would ship localhost');
} else if (/^https?:\/\/(localhost|127\.0\.0\.1)/.test(site)) {
  fail(`PUBLIC_SITE_URL is local: ${site}`);
} else if (!/^https:\/\//.test(site)) {
  fail(`PUBLIC_SITE_URL must be https: ${site}`);
} else {
  ok(`PUBLIC_SITE_URL = ${site}`);
}

console.log('== 2. Wrangler config ==');
try {
  const raw = readFileSync(join(HERE, 'wrangler.jsonc'), 'utf8');
  if (!/"assets"/.test(raw)) fail('wrangler.jsonc has no assets block');
  else ok('assets block present');
  if (!/compatibility_date/.test(raw)) fail('no compatibility_date');
  else ok('compatibility_date set');
  if (!/html_handling/.test(raw)) fail('html_handling not set — trailing-slash duplicates possible');
  else ok('html_handling set');
} catch (e) {
  fail(`wrangler.jsonc unreadable: ${e.message}`);
}

console.log('== 3. Build output ==');
const DIST = join(HERE, 'dist');
if (!existsSync(DIST)) {
  fail('dist/ does not exist — run `npm run build:full`');
} else {
  const need = ['index.html', '_headers', 'llms.txt', 'robots.txt', 'sitemap-index.xml', '404.html'];
  for (const f of need) {
    if (!existsSync(join(DIST, f))) fail(`dist/${f} missing`);
  }
  if (!fails.length) ok('required build artifacts present');

  const count = (dir) => readdirSync(dir, { withFileTypes: true })
    .reduce((n, d) => n + (d.isDirectory() ? count(join(dir, d.name)) : 1), 0);
  const files = count(DIST);
  if (files > 20000) fail(`${files} files exceeds the Workers Free limit of 20,000`);
  else ok(`${files} files (limit 20,000)`);

  let biggest = { size: 0, name: '' };
  const scan = (dir) => {
    for (const d of readdirSync(dir, { withFileTypes: true })) {
      const p = join(dir, d.name);
      if (d.isDirectory()) scan(p);
      else {
        const s = statSync(p).size;
        if (s > biggest.size) biggest = { size: s, name: d.name };
      }
    }
  };
  scan(DIST);
  if (biggest.size > 25 * 1024 * 1024) fail(`largest file ${biggest.name} exceeds 25 MB`);
  else ok(`largest file ${Math.round(biggest.size / 1024)} KB (limit 25 MB)`);

  // _headers must be valid enough to be applied
  const h = readFileSync(join(DIST, '_headers'), 'utf8');
  if (!/\/\*/.test(h)) fail('_headers has no /* rule — security headers would not apply');
  else ok('_headers has a /* rule');
}

console.log('== 4. Search index ==');
if (existsSync(join(DIST, 'pagefind'))) {
  ok('pagefind index present');
} else {
  fail('dist/pagefind missing — search will 404. Run `npm run index`.');
}

console.log();
if (fails.length) {
  console.log(`PREFLIGHT: FAIL (${fails.length} issues) — deploy aborted`);
  process.exit(1);
}
console.log('PREFLIGHT: OK — safe to deploy');
