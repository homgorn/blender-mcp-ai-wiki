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
  isTemplateMirror,
  isRealTranslation,
  computeOrigLang,
  publishedEntries,
  buildBodyLinkMap,
  slugify,
  REAL_TRANSLATIONS,
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
  // two entries own one URL and the copy overwrites the original.
  // The `translation: 'ai'` matters: without a quality marker the entry is a
  // template and is dropped for a second, independent reason.
  const orig = E({ id: 'a', lang: 'ru' });
  const sameLang = E({ id: 'a__ru', lang: 'ru', isTranslation: true, translation: 'ai' });
  const otherLang = E({ id: 'a__de', lang: 'de', isTranslation: true, translation: 'ai' });
  const m = computeOrigLang([orig, sameLang, otherLang]);

  assert.equal(isShadowMirror(orig, m), false);
  assert.equal(isShadowMirror(sameLang, m), true);
  assert.equal(isShadowMirror(otherLang, m), false);

  const pub = publishedEntries([orig, sameLang, otherLang]);
  assert.deepEqual(pub.map((e) => e.id), ['a', 'a__de']);
});

test('a template mirror is never published', () => {
  // The rule that removed 631 pages. A template mirror is the original text with
  // a language header: publishing it as noindex was honest to a crawler and
  // dishonest to a reader who had chosen that language.
  const orig = E({ id: 'a', lang: 'ru' });
  const tmplEs = E({ id: 'a__es', lang: 'es', isTranslation: true, translation: 'template' });
  const tmplZh = E({ id: 'a__zh', lang: 'zh', isTranslation: true, translation: 'template' });
  const legacy = E({ id: 'a__de', lang: 'de', isTranslation: true, translation: 'legacy' });
  const humanEs = E({ id: 'a__es', lang: 'es', isTranslation: true, translation: 'human' });
  const aiZh = E({ id: 'a__zh', lang: 'zh', isTranslation: true, translation: 'ai' });

  assert.equal(isTemplateMirror(tmplEs), true);
  assert.equal(isTemplateMirror(legacy), true);
  assert.equal(isTemplateMirror(humanEs), false);
  assert.equal(isTemplateMirror(aiZh), false);
  assert.equal(isTemplateMirror(orig), false);

  const pub = publishedEntries([orig, tmplEs, tmplZh, legacy, humanEs, aiZh]);
  assert.deepEqual(pub.map((e) => `${e.id}:${e.translation ?? 'original'}`),
    ['a:original', 'a__es:human', 'a__zh:ai']);
});

test('an unmarked translation is treated as a template, not as real', () => {
  // Failing open here would publish 790 pages of untranslated text.
  const x = E({ id: 'x__es', lang: 'es', isTranslation: true });
  assert.equal(isTemplateMirror(x), true);
  assert.equal(isRealTranslation(x, new Map()), false);
});

test('a real translation in a new language is published', () => {
  const orig = E({ id: 'a', lang: 'ru' });
  const es = E({ id: 'a__es', lang: 'es', isTranslation: true, translation: 'ai' });
  const m = computeOrigLang([orig, es]);
  assert.equal(isRealTranslation(es, m), true);
  assert.equal(isShadowMirror(es, m), false);
});

test('the duplicate test and the publication rule agree', () => {
  // These two drifted once: the publication rule learned about `ai` and the
  // isDuplicate test did not, so 19 Russian references were published and noindex
  // at the same time — in the sitemap, invisible to search. The invariant is that
  // nothing can be both published and a duplicate.
  for (const q of ['human', 'ai', 'legacy', 'template', undefined] as const) {
    const e = E({ id: 'x__es', lang: 'es', isTranslation: true, translation: q });
    const published = publishedEntries([e]).length === 1;
    const isDuplicate = !REAL_TRANSLATIONS.has((q ?? 'template') as never);
    assert.equal(published && isDuplicate, false, `translation=${q} is published AND duplicate`);
  }
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
    all.push(E({ id: `p01__${lang}`, origId: 'p01', lang, isTranslation: true, translation: 'ai' }));
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
  const from = E({ id: 'c1__de', origId: 'c1', lang: 'de', isTranslation: true, translation: 'ai',
    category: 'cases', filePath: 'multilang/de/cases/c1.md', body: '[S](../setups/s1.md)' });
  const ruTarget = E({ id: 's1', origId: 's1', lang: 'ru', category: 'setups', filePath: 'setups/s1.md' });
  const deTarget = E({ id: 's1__de', origId: 's1', lang: 'de', isTranslation: true, translation: 'ai',
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
  const from = E({ id: '05__en', origId: '05', lang: 'en', isTranslation: true, translation: 'ai',
    filePath: 'multilang/en/prompts/05.md', body: '[P](../prompts/09.md)' });
  const ownOriginal = E({ id: '05', origId: '05', lang: 'ru', filePath: 'prompts/05.md' });
  const target = E({ id: '09', origId: '09', lang: 'en', filePath: 'prompts/09.md' });
  const map = buildBodyLinkMap(from, ctx([from, ownOriginal, target]));
  assert.equal(map.get('../prompts/09.md'), '/en/prompts/09');
});

test('a translation with no original present cannot fall back', () => {
  // Guards the assumption above: without an original in the set the mirror's
  // links are simply unresolvable, and the gate must be the one to say so.
  const orphan = E({ id: '05__en', origId: '05', lang: 'en', isTranslation: true, translation: 'ai',
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

test('the rule reads both shapes of entry', () => {
  // The shared rule is called with database entries by the scripts and with the
  // built objects by the Astro data layer, and the two spell their fields
  // differently. A version that read only `is_translation` got `undefined` on
  // the built objects, decided every entry was an original, and published all
  // 794 mirrors — 935 pages instead of 285.
  const dbEntry = {
    meta: {
      id: 'a__es', orig_id: 'a', language: 'es', category: 'prompts',
      is_translation: true, translation: 'ai',
    },
  };
  const built = {
    id: 'a__es', origId: 'a', lang: 'es', category: 'prompts',
    isTranslation: true, translation: 'ai',
  };
  const dbOriginal = { meta: { id: 'a', language: 'ru', category: 'prompts', is_translation: false } };
  const builtOriginal = { id: 'a', origId: 'a', lang: 'ru', category: 'prompts', isTranslation: false };

  for (const [orig, tr, asTemplate] of [
    [dbOriginal, dbEntry, (t) => ({ meta: { ...t.meta, translation: 'template' } })],
    [builtOriginal, built, (t) => ({ ...t, translation: 'template' })],
  ]) {
    const m = computeOrigLang([orig, tr]);
    assert.equal(isShadowMirror(tr, m), false, 'es differs from the ru original');
    assert.equal(isRealTranslation(tr, m), true);
    assert.equal(isTemplateMirror(tr), false);
    assert.equal(publishedEntries([orig, tr]).length, 2, 'both should be published');

    const tmpl = asTemplate(tr);
    assert.equal(isTemplateMirror(tmpl), true, 'a template is not a translation');
    assert.equal(publishedEntries([orig, tmpl]).length, 1, 'the template must not be published');
  }
});

test('slugify drops characters that cannot appear in a URL path', () => {
  assert.equal(slugify('01_geometry_basics'), '01-geometry-basics');
  assert.equal(slugify('case_14_food_r visualisation'), 'case-14-food-r-visualisation');
  assert.equal(slugify('Промпты'), '');
  assert.equal(slugify('a.md'), 'a');
  assert.equal(slugify('--a--'), 'a');
});

/* ---------------------------------------------------------------- slugify */
