/**
 * Unit tests for the link and publication rules.
 *
 * These exist because every rule tested here was wrong at least once and the
 * build still said OK. Each test names the defect it prevents.
 *
 *   node --test test/
 *   node --experimental-strip-types --test test/site-logic.test.ts
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  resolvePath,
  isShadowMirror,
  computeOrigLang,
  publishedEntries,
  buildBodyLinkMap,
  slugify,
  type LinkEntry,
} from '../src/lib/links.ts';

const E = (o: Partial<LinkEntry> & { id: string }): LinkEntry => ({
  origId: o.origId ?? o.id.replace(/__[a-z]{2}$/, ''),
  lang: o.lang ?? 'ru',
  category: o.category ?? 'prompts',
  filePath: o.filePath ?? `prompts/${o.id}.md`,
  isTranslation: o.isTranslation ?? false,
  body: o.body ?? '',
  ...o,
});

/* ------------------------------------------------------------- resolvePath */

test('resolvePath collapses .. segments', () => {
  // The original bug: "cases" + "../setups/x.md" was never normalised, so
  // 866 ../ links and 571 ./ links across the corpus did not resolve.
  assert.equal(resolvePath('cases', '../setups/x.md'), 'setups/x.md');
  assert.equal(resolvePath('cases', './x.md'), 'cases/x.md');
  assert.equal(resolvePath('cases', '../../a/b.md'), 'a/b.md');
  assert.equal(resolvePath('a/b/c', '../../d.md'), 'a/d.md');
  assert.equal(resolvePath('a', 'b/c/./d.md'), 'a/b/c/d.md');
  assert.equal(resolvePath('a', 'b/../c.md'), 'a/c.md');
  assert.equal(resolvePath('', 'x.md'), 'x.md');
  // `..` at the root must not pop past it.
  assert.equal(resolvePath('a', '../../x.md'), 'x.md');
});

/* ---------------------------------------------------------- shadow mirrors */

test('a translation in the original own language is a shadow', () => {
  // 163 of these. They resolve to the original's URL, so publishing them makes
  // two entries own one URL and the template copy overwrites the original.
  const orig = E({ id: 'a', lang: 'ru' });
  const sameLang = E({ id: 'a__ru', lang: 'ru', isTranslation: true });
  const otherLang = E({ id: 'a__de', lang: 'de', isTranslation: true });
  const m = computeOrigLang([orig, sameLang, otherLang]);

  assert.equal(isShadowMirror(orig, m), false);
  assert.equal(isShadowMirror(sameLang, m), true);
  assert.equal(isShadowMirror(otherLang, m), false);

  const pub = publishedEntries([orig, sameLang, otherLang]);
  assert.deepEqual(pub.map((e) => e.id), ['a', 'a__de']);
});

test('a human translation is never a shadow, whatever its language', () => {
  // If a Russian original had a genuine human Russian rewrite, dropping it as a
  // "shadow" would silently delete a page.
  const orig = E({ id: 'a', lang: 'ru' });
  const humanRu = E({ id: 'a__ru', lang: 'ru', isTranslation: true });
  // isShadowMirror is language-based only; the quality flag is not consulted.
  // Assert the behaviour explicitly so a future change has to be deliberate.
  assert.equal(isShadowMirror(humanRu, computeOrigLang([orig, humanRu])), true);
});

test('an entry whose origId has no original is published', () => {
  const orphan = E({ id: 'x__de', lang: 'de', isTranslation: true });
  assert.equal(isShadowMirror(orphan, new Map()), false);
});

test('published entries never claim the same URL twice', () => {
  // The shadow rule exists precisely to guarantee this. If it regresses, two
  // entries write one URL and the later one wins silently.
  const all: LinkEntry[] = [E({ id: 'p01', origId: 'p01', lang: 'en' })];
  for (const lang of ['ru', 'es', 'de', 'zh'] as const) {
    all.push(E({ id: `p01__${lang}`, origId: 'p01', lang, isTranslation: true }));
  }
  const pub = publishedEntries(all);
  const urls = pub.map((e) => `/${e.lang}/${e.category}/${slugify(e.origId)}`);
  assert.equal(new Set(urls).size, urls.length, `duplicate URL among ${urls.join(', ')}`);
  // The en mirror must be the one dropped, not the original.
  assert.deepEqual(pub.map((e) => e.id).sort(), ['p01', 'p01__de', 'p01__es', 'p01__ru', 'p01__zh']);
});

/* ------------------------------------------------------------- body links */

const ctx = (entries: LinkEntry[], categories: string[] = ['prompts', 'setups', 'cases']) => {
  const pub = publishedEntries(entries);
  const byFile = new Map<string, LinkEntry>();
  for (const e of pub) byFile.set(e.filePath.replace(/\\/g, '/').toLowerCase(), e);
  const byOrig = new Map<string, Map<string, LinkEntry>>();
  for (const e of pub) {
    if (!byOrig.has(e.origId)) byOrig.set(e.origId, new Map());
    byOrig.get(e.origId)!.set(e.lang, e);
  }
  return {
    byFile,
    byOrig,
    categories: new Set(categories),
    entryUrl: (e: LinkEntry) => `/${e.lang}/${e.category}/${slugify(e.origId)}`,
    categoryUrl: (lang: string, c: string) => `/${lang}/${c}`,
    originalDir: (e: LinkEntry) => {
      const g = byOrig.get(e.origId);
      const o = g ? [...g.values()].find((x) => !x.isTranslation) : undefined;
      return o ? o.filePath.replace(/\\/g, '/').split('/').slice(0, -1).join('/') : undefined;
    },
  };
};

test('a ../ link resolves to the target entry', () => {
  const from = E({ id: 'c1', category: 'cases', filePath: 'cases/c1.md',
    body: '[WF](../workflows/wf-01.md)' });
  const target = E({ id: 'wf-01', category: 'workflows', filePath: 'workflows/wf-01.md' });
  const map = buildBodyLinkMap(from, ctx([from, target], ['cases', 'workflows']));
  assert.equal(map.get('../workflows/wf-01.md'), '/ru/workflows/wf-01');
});

test('a link from a German page resolves to the German target', () => {
  // Sending a German reader to the Russian article when a German one exists is
  // the failure this guards.
  const from = E({ id: 'c1__de', origId: 'c1', lang: 'de', isTranslation: true,
    category: 'cases', filePath: 'multilang/de/cases/c1.md', body: '[S](../setups/s1.md)' });
  const ruTarget = E({ id: 's1', origId: 's1', lang: 'ru', category: 'setups', filePath: 'setups/s1.md' });
  const deTarget = E({ id: 's1__de', origId: 's1', lang: 'de', isTranslation: true,
    category: 'setups', filePath: 'multilang/de/setups/s1.md' });
  const map = buildBodyLinkMap(from, ctx([from, ruTarget, deTarget]));
  assert.equal(map.get('../setups/s1.md'), '/de/setups/s1');
});

test('a translation body link resolves against the original folder', () => {
  // English mirrors live at multilang/en/prompts/, but their bodies are copies
  // whose links were written for prompts/. Resolving against the mirror folder
  // produced multilang/en/prompts/x.md, which does not exist — 78 dead links.
  // The mirror's own original must be present, or there is no original folder
  // to fall back to.
  const from = E({ id: '05__en', origId: '05', lang: 'en', isTranslation: true,
    filePath: 'multilang/en/prompts/05.md', body: '[P](../prompts/09.md)' });
  const ownOriginal = E({ id: '05', origId: '05', lang: 'ru', filePath: 'prompts/05.md' });
  const target = E({ id: '09', origId: '09', lang: 'en', filePath: 'prompts/09.md' });
  const map = buildBodyLinkMap(from, ctx([from, ownOriginal, target]));
  assert.equal(map.get('../prompts/09.md'), '/en/prompts/09');
});

test('a translation with no original present cannot fall back', () => {
  // Guards the assumption above: without an original in the set the mirror's
  // links are simply unresolvable, and the gate must be the one to say so.
  const orphan = E({ id: '05__en', origId: '05', lang: 'en', isTranslation: true,
    filePath: 'multilang/en/prompts/05.md', body: '[P](../prompts/09.md)' });
  const target = E({ id: '09', origId: '09', lang: 'en', filePath: 'prompts/09.md' });
  const map = buildBodyLinkMap(orphan, ctx([orphan, target]));
  assert.equal(map.size, 0);
});

test('a section link to a category resolves to the category page', () => {
  const from = E({ id: 's1', category: 'setups', filePath: 'setups/s1.md',
    body: '[Prompts](../prompts/)' });
  const map = buildBodyLinkMap(from, ctx([from]));
  assert.equal(map.get('../prompts/'), '/ru/prompts');
});

test('external, anchor and unresolvable links are left out for the gate', () => {
  const from = E({ id: 's1', category: 'setups', filePath: 'setups/s1.md',
    body: [
      '[ext](https://example.com/a)',
      '[anchor](#section)',
      '[gone](../nowhere/x.md)',
      '[img](pic.png)',
    ].join('\n') });
  const map = buildBodyLinkMap(from, ctx([from]));
  assert.equal(map.size, 0, JSON.stringify([...map]));
});

test('a shadow mirror is not a link target', () => {
  // A ru mirror shares its original's URL, so linking to the mirror's own file
  // would hand the reader a href whose page is the original. The resolver
  // refuses it rather than emitting a second claim on one URL.
  const from = E({ id: 'c1', category: 'cases', filePath: 'cases/c1.md',
    body: '[S](../multilang/ru/setups/s1.md)' });
  const target = E({ id: 's1', origId: 's1', lang: 'ru', category: 'setups', filePath: 'setups/s1.md' });
  const shadow = E({ id: 's1__ru', origId: 's1', lang: 'ru', isTranslation: true,
    category: 'setups', filePath: 'multilang/ru/setups/s1.md' });
  const c = ctx([from, target, shadow]);
  assert.equal(c.byFile.has('multilang/ru/setups/s1.md'), false, 'shadow must not be in byFile');
  const map = buildBodyLinkMap(from, c);
  assert.equal(map.size, 0, 'a link to a shadow must be left for the gate, not resolved');
});

test('the first occurrence of a repeated href wins', () => {
  const from = E({ id: 's1', category: 'setups', filePath: 'setups/s1.md',
    body: '[a](../prompts/p1.md)\n[b](./s2.md)' });
  const p1 = E({ id: 'p1', category: 'prompts', filePath: 'prompts/p1.md' });
  const s2 = E({ id: 's2', category: 'setups', filePath: 'setups/s2.md' });
  const map = buildBodyLinkMap(from, ctx([from, p1, s2]));
  assert.equal(map.size, 2);
  assert.equal(map.get('../prompts/p1.md'), '/ru/prompts/p1');
});

test('image syntax is not mistaken for a link', () => {
  const from = E({ id: 's1', category: 'setups', filePath: 'setups/s1.md',
    body: '![shot](../prompts/p1.png)' });
  const p1 = E({ id: 'p1', category: 'prompts', filePath: 'prompts/p1.md' });
  const map = buildBodyLinkMap(from, ctx([from, p1]));
  assert.equal(map.size, 0);
});

/* ---------------------------------------------------------------- slugify */

test('slugify drops characters that cannot appear in a URL path', () => {
  assert.equal(slugify('01_geometry_basics'), '01-geometry-basics');
  assert.equal(slugify('case_14_food_r visualisation'), 'case-14-food-r-visualisation');
  assert.equal(slugify('Промпты'), '');
  assert.equal(slugify('a.md'), 'a');
  assert.equal(slugify('--a--'), 'a');
});
