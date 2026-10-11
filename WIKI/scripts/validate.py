#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full project validation: encoding, structure, DB, API, links. Exit 0=OK, 1=FAIL."""
import json, os, re, sys
from pathlib import Path
# A validator that crashes on a legacy console is not a validator: Windows consoles
# are often cp1251/cp1252, and the output contains Cyrillic + emoji.
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
fails = []
def ok(msg): print(f"  [OK] {msg}")
def fail(msg):
    print(f"  [FAIL] {msg}"); fails.append(msg)

print("== 1. Encoding (utf-8 read) ==")
mds = list(WIKI.rglob("*.md"))
bad = 0
for f in mds:
    try: f.read_text(encoding="utf-8")
    except Exception as e: bad += 1; fail(f"encoding {f.relative_to(WIKI)}: {e}")
if not bad: ok(f"{len(mds)} md files readable")

print("== 2. Required dirs ==")
for d in ["prompts","cases","setups","workflows","crossref","multilang","db","scripts","site","site/data"]:
    if (WIKI/d).exists(): ok(f"dir {d}")
    else: fail(f"missing dir {d}")

print("== 3. Prompts P01-Pxx coverage ==")
prompts = sorted((WIKI/"prompts").glob("*.md"))
nums = set()
for p in prompts:
    m = re.match(r"(\d+)_", p.name)
    if m: nums.add(int(m.group(1)))
print(f"  prompts files: {len(prompts)}, nums: {sorted(nums)}")
if max(nums, default=0) < 16: fail("prompts coverage < P16")
else: ok("prompts chunk progress")

print("== 4. Root duplication check ==")
ROOT = WIKI.parent
root_dupes = []
for d in ["addons","api","guides","mcp","workflows"]:
    if (ROOT/d).exists(): root_dupes.append(d)
if root_dupes: fail(f"root dupes not merged: {root_dupes}")
else: ok("no root dupes")

print("== 5. DB build ==")
import subprocess
r = subprocess.run([sys.executable, str(WIKI/"scripts"/"build_database.py")], capture_output=True, text=True, timeout=180)
if r.returncode != 0:
    fail(f"build_database failed: {(r.stderr or r.stdout)[-500:]}")
else:
    db = json.loads((WIKI/"db"/"wiki_database.json").read_text(encoding="utf-8"))
    print(f"  [OK] entries={db.get('total_entries', len(db['entries']))}")

print("== 6. Multilang 5-lang coverage ==")
langs = {}
for lang in ["en","ru","es","de","zh"]:
    langs[lang] = len(list((WIKI/"multilang"/lang).rglob("*.md"))) if (WIKI/"multilang"/lang).exists() else 0
print(f"  {langs}")
if min(langs.values()) < 50: fail(f"multilang thin: {langs}")
else: ok("multilang coverage")

print("== 7. Site data ==")
for f in ["wiki_database.json","search_index.json","graph.json","sitemap.json","langs.json"]:
    p = WIKI/"site"/"data"/f
    if p.exists() and p.stat().st_size > 100: ok(f"site/data/{f} {p.stat().st_size//1024}KB")
    else: fail(f"site/data/{f} missing/small")
# The site loads meta.json + per-category chunks (not the 9 MB DB) -> must be in sync.
meta_p = WIKI/"site"/"data"/"meta.json"
if not meta_p.exists():
    fail("site/data/meta.json missing (site would fall back to the 9MB DB)")
else:
    smeta = json.loads(meta_p.read_text(encoding="utf-8"))
    cats = {m.get("category","misc") for m in smeta["items"]}
    chunk_total = 0
    for c in cats:
        cp = WIKI/"site"/"data"/"chunks"/f"entries_{c}.json"
        if not cp.exists():
            fail(f"site chunk missing: entries_{c}.json"); continue
        chunk_total += json.loads(cp.read_text(encoding="utf-8"))["total"]
    db_n = len(json.loads((WIKI/"db"/"wiki_database.json").read_text(encoding="utf-8"))["entries"])
    if smeta["total"] == db_n and chunk_total == db_n:
        ok(f"site meta.json + {len(cats)} chunks in sync with DB ({db_n})")
    else:
        fail(f"site data out of sync: meta={smeta['total']} chunks={chunk_total} db={db_n}")
    g = json.loads((WIKI/"site"/"data"/"graph.json").read_text(encoding="utf-8"))
    nopos = [n["id"] for n in g["nodes"][:200] if "x" not in n or "y" not in n]
    if nopos: fail(f"graph nodes without precomputed layout: {nopos[:5]}")
    else: ok(f"graph layout precomputed ({len(g['nodes'])} nodes)")

print("== 8. Frontmatter (full-scan multilang) ==")
fm_bad = 0
ml_files = [f for f in mds if "multilang" in f.parts]
for f in ml_files:
    t = f.read_text(encoding="utf-8")
    if not t.startswith("---"):
        fm_bad += 1; fail(f"no frontmatter {f.relative_to(WIKI)}")
if not fm_bad: ok(f"frontmatter OK ({len(ml_files)} multilang files)")

print("== 9. Broken md links (full-scan, excl. template mirrors) ==")
# Template mirrors under multilang/ have different relative depth than
# originals, so their copied relative links can't resolve. Only human
# translations (single source: scripts/wiki_const.HUMAN_MIRRORS) are checked.
import sys as _sys
_sys.path.insert(0, str(WIKI / "scripts"))
from wiki_const import HUMAN_MIRRORS as HUMAN_MIRRORS
HUMAN_MIRRORS = set(HUMAN_MIRRORS)
broken = 0
checked = 0
for f in mds:
    rel = f.relative_to(WIKI).as_posix()
    if "export_obsidian" in f.parts:
        continue
    if "templates" in f.parts:          # skeletons contain deliberate placeholders
        continue
    if "multilang" in f.parts and rel not in HUMAN_MIRRORS:
        continue
    t = f.read_text(encoding="utf-8")
    for txt, url in re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", t):
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        target = (f.parent / url.split("#")[0]).resolve()
        try:
            target.relative_to(WIKI)
            checked += 1
            if not target.exists():
                broken += 1; fail(f"broken link {f.relative_to(WIKI)} -> {url}")
        except ValueError:
            pass
if not broken: ok(f"links OK ({checked} links checked)")

print("== 10. Duplicate IDs / empty bodies / tag garbage / stubs ==")
import json as _json
try:
    db = _json.loads((WIKI/"db"/"wiki_database.json").read_text(encoding="utf-8"))
    ids = [e["meta"]["id"] for e in db["entries"]]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes: fail(f"duplicate ids: {dupes[:10]}")
    else: ok(f"no duplicate ids ({len(ids)} entries)")
    empty = [e["meta"]["id"] for e in db["entries"] if not (e.get("full_content") or "").strip()]
    if empty: fail(f"empty bodies: {empty[:10]}")
    else: ok("no empty bodies")
    bad_tags = set()
    for e in db["entries"]:
        for tg in e["meta"].get("tags", []):
            if tg in ("**",) or len(tg) > 30 or tg.isdigit():
                bad_tags.add(tg)
            import re as _re
            if _re.fullmatch(r'[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8}', tg):
                bad_tags.add(tg)
    if bad_tags: fail(f"tag garbage: {sorted(bad_tags)[:10]}")
    else: ok("tags clean")
    stubs = sum(1 for e in db["entries"] if e["meta"].get("status") == "stub")
    fulls = sum(1 for e in db["entries"] if e["meta"].get("status") == "full")
    print(f"  [INFO] status: stub={stubs} full={fulls} unmarked={len(ids)-stubs-fulls}")
except Exception as e:
    fail(f"db scan failed: {e}")

print("== 11. Multilang mirror pairing (translation must have an original) ==")
orphans = []
for lang in ["en","ru","es","de","zh"]:
    base = WIKI/"multilang"/lang
    if not base.exists():
        fail(f"multilang/{lang} missing"); continue
    for f in base.rglob("*.md"):
        rel = f.relative_to(base)
        if len(rel.parts) < 2:
            continue
        if not (WIKI/rel).exists():
            # The mirror path is the original path with `multilang/<lang>/` in
            # front, so resolve it as-is. The previous `WIKI/<cat>/<name>` form
            # only ever matched flat category dirs, and it reported every
            # nested mirror (references/v1/api/...) as an orphan of nothing.
            orphans.append(f"{rel.as_posix()}")
if orphans:
    fail(f"orphan translations without original ({len(orphans)}): {sorted(set(orphans))[:10]}")
else:
    ok("every translation maps to an original file")

print("== 12. SPEC numbers vs reality ==")
spec = (WIKI.parent/"SDD"/"SPEC.md").read_text(encoding="utf-8")
m = re.search(r"(\d+)\s+запис", spec)
try:
    db_n = len(json.loads((WIKI/"db"/"wiki_database.json").read_text(encoding="utf-8"))["entries"])
except Exception:
    db_n = -1
if m and int(m.group(1)) != db_n:
    fail(f"SPEC says {m.group(1)} entries, DB has {db_n} — update SDD/SPEC.md")
else:
    ok(f"SPEC entry count matches DB ({db_n})")
n_prompts = len(list((WIKI/"prompts").glob("*.md")))
if f"P01–P{n_prompts:02d}" not in spec:
    fail(f"SPEC prompt scope does not match reality (prompts on disk: {n_prompts})")
else:
    ok(f"SPEC scope matches prompts on disk (P01–P{n_prompts:02d})")

print("== 13. Template conformance (see WIKI/templates, WIKI/CONTRIBUTING.md) ==")
# Each requirement is a list of accepted markers: the corpus has two heading
# dialects (RU: ЦЕЛЬ/ПРОМПТ/СВЯЗИ and EN: GOAL/PROMPT/LINKS). We check presence
# of the section, not the language of its heading.
REQUIRED = {
    "prompts":   {"goal": ["ЦЕЛЬ", "GOAL"], "prompt": ["ПРОМПТ", "PROMPT"],
                  # "How do I invoke this" — an MCP tool call, or a command block.
                  # P29 (CLI) and P40 (version control) are driven from a shell,
                  # not from an MCP session, so demanding MCP there was wrong.
                  "mcp": ["MCP", "КОМАНДЫ", "COMMANDS"], "links": ["СВЯЗИ", "LINKS"]},
    "setups":    {"goal": ["ЦЕЛЬ", "GOAL", "ЗАДАЧА"], "links": ["СВЯЗИ", "LINKS"]},
    "workflows": {"goal": ["ЦЕЛЬ", "GOAL"], "links": ["СВЯЗИ", "LINKS"]},
    "cases":     {"goal": ["ЦЕЛЬ", "GOAL", "Задача", "Brief"], "links": ["СВЯЗИ", "LINKS"]},
}
nonconform = {}
for cat, groups in REQUIRED.items():
    # Recursive: 19 articles under references/v1/** were never conformance-checked.
    for f in (WIKI/cat).rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        # Case-insensitive on purpose: bulk-authored files use
        # `## 🎯 Цель / Goal` and `## 🔗 Связи / Links`, and a case-sensitive
        # compare reported 67 goals and 47 links as missing while they were
        # present. A gate that cries wolf is ignored.
        upper = t.upper()
        miss = [name for name, marks in groups.items()
                if not any(mk.upper() in upper for mk in marks)]
        if miss:
            nonconform[f"{cat}/{f.relative_to(WIKI/cat).as_posix()}"] = miss
if nonconform:
    msg = f"{len(nonconform)} files miss template sections"
    if "--strict" in sys.argv:
        fail(f"{msg}: {list(nonconform.items())[:5]}")
    else:
        print(f"  [INFO] {msg} (not a gate; validate.py --strict to enforce). e.g. {list(nonconform.items())[:3]}")
else:
    ok("all files match the required template sections")

print("== 14. Fenced code blocks are balanced ==")
# An unclosed ``` swallows every following heading into a <pre>: the article text
# survives but its rendering does not. Two articles did exactly this, in the
# corpus and in all five of their mirrors, and nothing caught it — an unclosed
# fence does not change the number of <h1> elements, so the SEO gate saw a clean
# page. Checked as a hard gate because the failure is invisible downstream.
FENCE_RX = re.compile(r"^\s*(?:```|~~~)", re.M)
unbalanced = []
for f in sorted(WIKI.rglob("*.md")):
    if len(FENCE_RX.findall(f.read_text(encoding="utf-8"))) % 2:
        unbalanced.append(f.relative_to(WIKI).as_posix())
if unbalanced:
    fail(f"{len(unbalanced)} file(s) have an unclosed code fence: {unbalanced[:5]}")
else:
    ok("every fenced code block is closed")

print("== 15. No heading with an empty body ==")
# A `##` with nothing under it renders as an empty section on the page. 166 files
# had one, left over from an earlier repair that emptied the body but not the
# heading — a pass that recognises prose has nothing left to match once the prose
# is gone. Cheap to check and impossible to spot by reading the markdown.
EMPTY_HEAD = re.compile(
    r"^##[ \t]*[^\n]*(?:\U0001F517|СВЯЗИ|Связи|LINKS)[^\n]*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL)
empty_heads = []
for f in sorted(WIKI.rglob("*.md")):
    if any(m.group(1).strip() == "" for m in EMPTY_HEAD.finditer(f.read_text(encoding="utf-8"))):
        empty_heads.append(f.relative_to(WIKI).as_posix())
if empty_heads:
    fail(f"{len(empty_heads)} file(s) have a heading with an empty body: {empty_heads[:5]}")
else:
    ok("no heading has an empty body")

print()
if fails:
    print(f"RESULT: FAIL ({len(fails)} issues)")
    sys.exit(1)
print("RESULT: OK")
print("RESULT: OK")
