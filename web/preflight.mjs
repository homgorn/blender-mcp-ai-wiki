#!/usr/bin/env node
/**
 * Pre-deploy gate. Cheap checks that must pass BEFORE `wrangler pages deploy`,
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

const EXPECTED_HOST = 'blendee-skills.refertur.net';

console.log('== 1. Environment ==');
const site = (process.env.PUBLIC_SITE_URL || '').trim();
if (!site) {
  fail(`PUBLIC_SITE_URL is not set — canonical/hreflang/sitemap would be wrong. Use https://${EXPECTED_HOST}`);
} else if (/^https?:\/\/(localhost|127\.0\.0\.1)/.test(site)) {
  fail(`PUBLIC_SITE_URL is local: ${site}`);
} else if (!/^https:\/\//.test(site)) {
  fail(`PUBLIC_SITE_URL must be https: ${site}`);
} else if (new URL(site).host !== EXPECTED_HOST) {
  warn(`PUBLIC_SITE_URL is ${new URL(site).host}, expected ${EXPECTED_HOST}`);
} else {
  ok(`PUBLIC_SITE_URL = ${site}`);
}
function warn(m) { console.log(`  [WARN] ${m}`); }

console.log('== 2. Wrangler config (Cloudflare Pages) ==');
try {
  const raw = readFileSync(join(HERE, 'wrangler.jsonc'), 'utf8');
  if (!/pages_build_output_dir/.test(raw)) {
    fail('wrangler.jsonc has no pages_build_output_dir — this project deploys to Pages, not Workers');
  } else {
    // The key is quoted in JSONC, so allow a quote between key and colon.
    const m = /"pages_build_output_dir"\s*:\s*"([^"]+)"/.exec(raw);
    ok(`pages_build_output_dir = ${m ? m[1] : '(found, unparsed)'}`);
  }
  if (!/"name"\s*:\s*"blendee-skills"/.test(raw)) fail('worker/project name is not blendee-skills');
  else ok('project name = blendee-skills');
  if (!/compatibility_date/.test(raw)) fail('no compatibility_date');
} catch (e) {
  fail(`wrangler.jsonc unreadable: ${e.message}`);
}

console.log('== 3. Build output ==');
const DIST = join(HERE, 'dist');
if (!existsSync(DIST)) {
  fail('dist/ does not exist — run `npm run build:full`');
} else {
  for (const f of ['index.html', '_headers', 'llms.txt', 'robots.txt', 'sitemap-index.xml', '404.html', 'og-default.png']) {
    if (!existsSync(join(DIST, f))) fail(`dist/${f} missing`);
  }
  if (!fails.length) ok('required build artifacts present');

  const count = (dir) => readdirSync(dir, { withFileTypes: true })
    .reduce((n, d) => n + (d.isDirectory() ? count(join(dir, d.name)) : 1), 0);
  const files = count(DIST);
  // Pages: 20,000 files on Free. (Workers has the same limit; stated once.)
  if (files > 20000) fail(`${files} files exceeds the Pages Free limit of 20,000`);
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

  const h = readFileSync(join(DIST, '_headers'), 'utf8');
  if (!/\/\*/.test(h)) fail('_headers has no /* rule — security headers would not apply');
  else ok('_headers has a /* rule (Pages supports _headers on static assets)');
}

console.log('== 4. Search index ==');
if (existsSync(join(DIST, 'pagefind'))) ok('pagefind index present');
else fail('dist/pagefind missing — search will 404. Run `npm run index`.');

console.log('== 5. DNS reminder ==');
console.log(`  The deploy alone will not make the hostname resolve. Add at the DNS host`);
console.log(`  serving refertur.net (Timeweb, not the registrar):`);
console.log(`      CNAME  blendee-skills  blendee-skills.pages.dev`);

console.log();
if (fails.length) {
  console.log(`PREFLIGHT: FAIL (${fails.length} issues) — deploy aborted`);
  process.exit(1);
}
console.log('PREFLIGHT: OK — safe to deploy');
