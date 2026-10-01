/**
 * Link and publication rules, extracted so they can be tested.
 *
 * These four rules decide which pages exist, which URLs they own, and where an
 * in-body link actually points. All four were wrong at least once, and none of
 * them had a test:
 *
 *   - path joining ignored `..`, so 1 433 of 1 437 internal links went unresolved
 *   - the resolved link table was computed and then never rendered, so 2 227
 *     in-body links shipped as raw relative paths on 446 of 916 pages
 *   - `.md` twins were written for shadow mirrors too, so 167 pages advertised a
 *     twin holding a different document than the page
 *   - a translation's body links were resolved against the mirror's folder
 *     instead of the original's
 *
 * Nothing here touches Astro, `import.meta.env` or the filesystem, so it runs
 * under `node --test` directly. See test/site-logic.test.ts.
 */

/** Minimal shape needed here, so tests need not import the full Entry type. */
export interface LinkEntry {
  id: string;
  origId: string;
  lang: string;
  category: string;
  filePath: string;
  isTranslation: boolean;
  /** Raw markdown body, used to find in-body links. */
  body: string;
}

/**
 * Join a relative path onto a directory the way a browser does.
 *
 * The bug this replaces: concatenating folder + link and then stripping a
 * leading `./` from the result, which can never match because the result always
 * starts with the folder.
 */
export function resolvePath(fromDir: string, rel: string): string {
  const out: string[] = [];
  for (const seg of fromDir.split('/')) if (seg) out.push(seg);
  for (const seg of rel.split('/')) {
    if (!seg || seg === '.') continue;
    if (seg === '..') out.pop();
    else out.push(seg);
  }
  return out.join('/');
}

/** origId -> language of the non-translation entry. */
export function computeOrigLang<T extends { origId: string; lang: string; isTranslation: boolean }>(
  entries: readonly T[],
): Map<string, string> {
  const m = new Map<string, string>();
  for (const e of entries) if (!e.isTranslation) m.set(e.origId, e.lang);
  return m;
}

/**
 * A translation whose language equals its original's resolves to the same URL
 * and is therefore not published. 163 of them, and the rule has to be identical
 * in the page builder, the agent-file generator and the SEO gate.
 */
export function isShadowMirror(
  e: { origId: string; lang: string; isTranslation: boolean },
  origLangByOrig: ReadonlyMap<string, string>,
): boolean {
  if (!e.isTranslation) return false;
  return origLangByOrig.get(e.origId) === e.lang;
}

export function publishedEntries<T extends { origId: string; lang: string; isTranslation: boolean }>(
  entries: readonly T[],
): T[] {
  const orig = computeOrigLang(entries);
  return entries.filter((e) => !isShadowMirror(e, orig));
}

export interface BodyLinkContext<T> {
  /** posix file path (lowercased) -> published entry. Shadows absent. */
  byFile: Map<string, T>;
  /** origId -> lang -> published entry. */
  byOrig: Map<string, Map<string, T>>;
  /** Categories that have at least one published page. */
  categories: ReadonlySet<string>;
  entryUrl: (e: T) => string;
  categoryUrl: (lang: string, category: string) => string;
  /** The original's directory, for a translation whose body was copied. */
  originalDir?: (e: T) => string | undefined;
}

/** Markdown links in a body, ignoring images: `![alt](x)` is not a link. */
function* bodyHrefs(body: string): Generator<string> {
  const rx = /(?<!!)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
  for (const m of body.matchAll(rx)) yield m[1];
}

function dirOf(posixFilePath: string): string {
  return posixFilePath.split('/').slice(0, -1).join('/');
}

/**
 * For one entry: the hrefs as written in its body, mapped to site URLs.
 *
 * Keyed by the literal string from the markdown, because `marked` copies that
 * string into the `href` attribute unchanged, so the renderer can substitute
 * without re-parsing. Keys are per entry: `../setups/x.md` means different files
 * in different folders.
 *
 * A href that cannot be resolved is left out, deliberately. The renderer then
 * keeps the original text, and the gate reports it — a silent rewrite to a wrong
 * URL would be worse than a visible failure.
 */
export function buildBodyLinkMap<T extends LinkEntry>(e: T, ctx: BodyLinkContext<T>): Map<string, string> {
  const map = new Map<string, string>();
  const ownDir = dirOf(e.filePath.replace(/\\/g, '/'));
  const origDir = ctx.originalDir?.(e);

  for (const raw of bodyHrefs(e.body)) {
    if (/^(?:https?:|mailto:|tel:|data:|#)/i.test(raw)) continue;
    const path = raw.split('#')[0].split('?')[0];
    if (!path) continue;
    const key = raw.toLowerCase();
    if (map.has(key)) continue;

    let target = ctx.byFile.get(resolvePath(ownDir, path).toLowerCase());
    if (!target && origDir !== undefined && origDir !== ownDir) {
      // A translation's body is a copy of the original's, so its relative links
      // were written against the original's folder. Without this fallback,
      // English mirrors resolved into multilang/en/... , which does not exist
      // for categories whose originals are already English.
      target = ctx.byFile.get(resolvePath(origDir, path).toLowerCase());
    }

    if (target) {
      map.set(key, ctx.entryUrl(ctx.byOrig.get(target.origId)?.get(e.lang) ?? target));
      continue;
    }

    // A path with no file whose last segment is a category means "the section":
    // `../prompts/` inside a setups article asks for the category page.
    const segs = resolvePath(ownDir, path).split('/').filter(Boolean);
    const last = (segs[segs.length - 1] ?? '').replace(/\.md$/, '');
    if (last && ctx.categories.has(last)) {
      map.set(key, ctx.categoryUrl(e.lang, last));
    }
  }
  return map;
}

/** Slug used in URLs. Ids may contain spaces, so they must not survive here. */
export function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/\.md$/, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
