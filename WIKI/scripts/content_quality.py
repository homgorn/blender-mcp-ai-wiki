#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content quality checks that no gate can make on structure alone.

`validate.py` proves a file is well formed. This proves it is worth reading.
Both matter, because the alternative to a thin article is no article, and the
failure mode of bulk authoring is a corpus that is structurally perfect and
useless.

Checks
------
dead-check     `bool(bpy.ops.x)` is always True, so it teaches a reader a
               pattern that cannot fail — and hides the fact that the operator
               may not exist at all
placeholder    TODO / XXX / `<вставьте>` / `...` standing in for content
empty-block    a fenced code block with no code in it
thin-full      `status: full` below the word floor the contract sets
duplicate      the same 60-word paragraph appearing in more than one article,
               which is how a corpus becomes 70 articles of the same paragraph
waffle         a proportion of sentences that assert nothing, e.g. "это важно",
               "нужно учитывать" — reads as content, carries none

Exits non-zero on any finding so it can be a gate. `--warn` reports without
failing, which is what you want while a batch is still in progress.

Run:  python scripts/content_quality.py [--warn] [--json]
"""
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WIKI = Path(r"C:\BLENDER ai\WIKI")
WARN = "--warn" in sys.argv
AS_JSON = "--json" in sys.argv
CATS = ["prompts", "setups", "workflows", "cases", "references"]
FENCE = "`" * 3

WORD_FLOOR = 450          # WIKI/templates/DEPTH.md
CODE_FLOOR = 8            # a code-heavy article can qualify on code instead
WAFDLE_FLOOR = 0.12       # 12% of sentences may be pure filler, at most
WAFDLE = [
    r"это\s+важно", r"нужно\s+учитывать", r"очень\s+важно",
    r"стоит\s+отметить", r"имеет\s+огромное\s+значение",
    r"в\s+современном\s+мире", r"это\s+необходимо",
]
# XXX only as a standalone uppercase token. Lowercase `xxx` is a legitimate
# placeholder inside an identifier (`tex_sky.xxx`), and flagging that teaches the
# checker to be ignored.
PLACEHOLDER = re.compile(
    r"(TODO|FIXME|\bXXX\b|\bTBD\b|вставьте|подставьте|"
    r"your[-_ ]?key[-_ ]?here|your[-_ ]?token|<встав)")

# Sentences that assert nothing. Whole-word-ish, Cyrillic aware.
WORD_RX = re.compile(r"[A-Za-zА-Яа-яЁё]{3,}")
SENT_RX = re.compile(r"[.!?]\s")

findings = defaultdict(list)


def note(kind, path, detail):
    findings[kind].append({"file": path, "detail": detail})


def prose_of(text):
    """Body with fenced code and frontmatter removed."""
    t = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    t = re.sub(r"```[\s\S]*?```", " ", t)
    t = re.sub(r"~~~[\s\S]*?~~~", " ", t)
    t = re.sub(r"`[^`]*`", " ", t)
    t = re.sub(r"https?://\S+", " ", t)
    return t


def scan_file(path, rel):
    text = path.read_text(encoding="utf-8")

    # dead check: a bpy.ops attribute assigned to a name and then bool()-ed.
    # `bool(bpy.ops.x)` is always True, and so is `op = bpy.ops.x; bool(op)` —
    # the operator may not even exist, and the check cannot tell.
    #
    # Comment lines are excluded. An article that explains *why* not to write
    # `bool(bpy.ops.x)` has to mention it, and flagging that would penalise the
    # one file that got the lesson right.
    code_lines = "\n".join(
        l for l in text.splitlines()
        if not l.lstrip().startswith("#")
    )
    for m in re.finditer(r"(\w+)\s*=\s*(bpy\.ops\.[A-Za-z0-9_.]+)", code_lines):
        name, op = m.group(1), m.group(2)
        if re.search(rf"bool\(\s*{re.escape(name)}\s*\)", code_lines):
            note("dead-check", rel, f"bool({name}) where {name} = {op} is always True")
    for m in re.finditer(r"bool\(\s*(bpy\.ops\.[A-Za-z0-9_.]+)\s*\)", code_lines):
        note("dead-check", rel, f"bool({m.group(1)}) is always True")

    for m in re.finditer(r"^\s*(#|//)?\s*(TODO|FIXME|XXX)\b", text, re.MULTILINE):
        note("placeholder", rel, m.group(0).strip()[:60])
    for m in PLACEHOLDER.finditer(text):
        if m.group(0).lower().startswith("your-key") or m.group(0).lower().startswith("your-token"):
            continue          # a legitimate example of a credential placeholder
        note("placeholder", rel, m.group(0)[:60])

    # empty code block
    for m in re.finditer(r"^([ \t]*" + re.escape(FENCE) + r"[\w+]*)[ \t]*\n([ \t]*)\n("
                         + re.escape(FENCE) + r")[ \t]*$", text, re.MULTILINE):
        note("empty-block", rel, "fenced block with no code")

    body = prose_of(text)
    words = len(WORD_RX.findall(body))
    blocks = len(re.findall(r"^" + re.escape(FENCE), text, re.MULTILINE)) // 2
    fm = re.search(r"^status:\s*(\S+)", text, re.MULTILINE)
    # Qualify on words OR on code. A setup article that is mostly commands can be
    # genuinely useful at 300 prose words and 12 code blocks; a flat word floor
    # would have failed setup_09 and the other command-heavy articles, and a
    # checker that fails correct work gets switched off.
    if fm and fm.group(1) == "full" and words < WORD_FLOOR and blocks < CODE_FLOOR:
        note("thin-full", rel,
             f"status: full but {words} words and {blocks} code blocks "
             f"(need {WORD_FLOOR} words or {CODE_FLOOR} blocks)")

    if words >= 120:
        sents = [s.strip() for s in SENT_RX.split(body) if s.strip()]
        if sents:
            w = sum(1 for s in sents if any(re.search(p, s, re.IGNORECASE) for p in WAFDLE))
            if w / len(sents) > WAFDLE_FLOOR:
                note("waffle", rel, f"{w}/{len(sents)} sentences are pure filler")

    # Paragraph duplication, excluding the cross-reference section.
    # Связи are supposed to overlap: two articles in the same category link to
    # the same neighbours. Flagging that would be a false positive on the one
    # part of the file that is legitimately uniform.
    scan = re.split(r"^##\s+.*(?:СВЯЗИ|LINKS).*$", body, maxsplit=1, flags=re.MULTILINE)[0]
    paras = [p.strip() for p in re.split(r"\n\s*\n", scan) if len(p.strip()) > 200]
    for p in paras:
        w = WORD_RX.findall(p.lower())
        if len(w) < 60:
            continue
        key = " ".join(w[:60])
        note("_keys", rel, key)


para_index = defaultdict(set)
for cat in CATS:
    d = WIKI / cat
    if not d.exists():
        continue
    for path in sorted(d.rglob("*.md")):
        rel = path.relative_to(WIKI).as_posix()
        scan_file(path, rel)
        n_before = sum(len(findings[k]) for k in findings)
        for item in list(findings.get("_keys", [])):
            if item["file"] == rel:
                para_index[item["detail"]].add(rel)

keys = findings.pop("_keys", [])
dupes = {k: sorted(v) for k, v in para_index.items() if len(v) > 1}
for k, files in sorted(dupes.items(), key=lambda kv: -len(kv[1])):
    findings["duplicate"].append({
        "file": files[0],
        "detail": f"identical 60-word opening in {len(files)} articles: {', '.join(files[:3])}",
    })

order = ["dead-check", "placeholder", "empty-block", "thin-full", "waffle", "duplicate"]
total = 0
if AS_JSON:
    print(json.dumps({k: findings[k] for k in order if k in findings}, ensure_ascii=False, indent=2))
else:
    print("== content quality ==")
    for kind in order:
        items = findings.get(kind, [])
        total += len(items)
        if not items:
            print(f"  [OK ] {kind}")
            continue
        print(f"  [{len(items):>3}] {kind}")
        for it in items[:8]:
            print(f"          {it['file']}: {it['detail']}")
        if len(items) > 8:
            print(f"          ... and {len(items) - 8} more")

print()
if total:
    verb = "findings" if WARN else "FINDINGS"
    print(f"{verb}: {total}")
    sys.exit(0 if WARN else 1)
print("OK: no content quality findings")
