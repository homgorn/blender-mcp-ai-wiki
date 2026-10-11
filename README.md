<div align="center">

# Blender MCP Wiki

**A reference corpus for driving Blender from scripts and MCP servers — prompts, setups, workflows and worked cases, published as a static site and as machine-readable JSON.**

[Live site](https://blender-mcp-wiki.refertur.net) · [MIT License](LICENSE) · [Changelog](CHANGELOG.md)

[English](README.md) · [Русский](README.ru.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [中文](README.zh.md) · [日本語](README.ja.md)

</div>

---

## What this is

182 articles on automating Blender: how to call the Python API without guessing,
how to wire third-party tools into a pipeline, and what actually goes wrong when
you do. Every code example is checked against a real Blender install before it is
published — see [Verification](#verification) for what that means.

The same corpus is published four ways, because four kinds of reader need it
differently:

| Surface | For | Where |
|---|---|---|
| Static site | humans | [`blender-mcp-wiki.refertur.net`](https://blender-mcp-wiki.refertur.net) |
| `.md` twin per article | anyone scripting against it | same URL + `.md` |
| `llms.txt` / `llms-full.txt` | assistants and indexes | `/llms.txt` |
| `wiki_database.json` | your own tooling | `WIKI/db/`, rebuilt from source |

## Languages — the honest number

The corpus is **complete in Russian and English**. Spanish, German and Chinese
carry seven articles each.

That sentence is deliberate. An earlier version of this project published 790
"translations" that were the original text with a language header, and advertised
five languages. It was false, and the site now computes the number from the
published set instead of counting what it declared. Untranslated mirrors are kept
in the repository as a translation backlog; they have no page, because serving a
reader the original text under a language they chose is worse than serving them
nothing.

## Repository layout

```
WIKI/                 the corpus — Markdown is the source of truth
  prompts/            50  task-shaped API recipes
  setups/             60  third-party integrations, one tool each
  workflows/          28  multi-stage pipelines
  cases/              16  worked problems with numbers and post-mortems
  references/         19  API and tool reference
  scripts/            the pipeline: build, validate, export, render
  db/                 generated JSON, gitignored, rebuilt by the pipeline
web/                  the Astro 7 site → Cloudflare Pages
  src/lib/publish.mjs the publication rule, in one importable place
  scripts/            SEO and consistency gates
SDD/                  spec, architecture, API contract, ADRs
```

## Quick start

```powershell
# Everything: repair, build the database, build the site, run every gate
$env:PUBLIC_SITE_URL="https://blender-mcp-wiki.refertur.net"
python WIKI/scripts/run_all.py
```

```powershell
cd web
npm ci
npm run all     # build, test, verify, preflight
npm run dev     # local site
```

`npm run all` is the gate the CI runs. It fails on a broken internal link, a page
that is published but marked `noindex`, a canonical that disagrees with the
origin, an inline event handler the site's own CSP would refuse, and an article
whose `status: full` does not hold up.

## Verification

Claims in this repository are measured, not asserted. The parts worth knowing:

- **Every `bpy.*` path in the corpus is resolved against a real Blender.**
  `WIKI/scripts/api_compat.py` parses the code blocks, collects the API paths and
  checks them by introspection — without executing any corpus code. It found that
  `Mesh.use_auto_smooth` is gone, that `bpy.ops.export_mesh.stl` became
  `bpy.ops.wm.stl_export`, and that `bpy.ops.object.fluid_add` does not exist at
  all in 5.x. Twelve articles taught `action.fcurves`, which slotted Actions
  removed. Which Blender release this corpus targets is an open decision, tracked
  in [`SDD/adr/0006`](SDD/adr/0006-blender-api-target-version.md).
- **The publication rule lives in one file.** `web/src/lib/publish.mjs` decides
  what gets a page. Six hand-copied versions of that rule once drifted and shipped
  19 pages that were indexed and `noindex` at the same time.
- **Every published page is screenshotted.** All 304 of them, at 390 / 768 /
  1440 px, checked for one `<h1>`, no horizontal overflow, a labelled `<nav>`,
  console errors and failed requests. The script is `web/../shots.mjs` in the
  working tree; a run reports zero problems.
- **Untranslated mirrors cannot ship.** There is no `noindex` fallback: a mirror
  without a real translation gets no page, and a gate fails if one appears.
- **Content gates, not just structure.** `WIKI/scripts/content_quality.py` catches
  a `bool(bpy.ops…)` check that can never fail, placeholder text, empty code
  blocks, an article marked `full` that is thinner than the contract, and the
  same paragraph copy-pasted across articles.

## The corpus, by the numbers

| | |
|---|---|
| database entries | 1016 |
| original articles | 182 (141 Russian, 41 English) |
| published pages | 304 (222 articles, all indexable) |
| code blocks | 5448 |
| articles below the depth floor | 0 |

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). In short: Markdown in `WIKI/` is the
source of truth, the pipeline regenerates everything else, and
`python WIKI/scripts/run_all.py` must end in `PIPELINE GREEN`.

Contracts for writing live in `WIKI/templates/`: `DEPTH.md` for article depth
(including the rule that invented API names are worse than an honest gap) and
`TRANSLATION_RU.md` for translations.

## Known limits

Stated plainly, because a reference that overstates itself is worse than a short
one:

- **The Blender version is undecided.** The corpus was written against 4.x; 5.2.1
  LTS is installed; 29 files call APIs that version no longer has.
- **Only 7 articles each in Spanish, German and Chinese.**
- **No illustrations.** 196 articles, zero images.
- **`rel="nofollow"` was on every outbound source link** and has been removed —
  citing Blender's own documentation should pass that authority along.

## License

MIT — see [`LICENSE`](LICENSE). Articles describe third-party tools owned by their
authors; names and trademarks belong to them.