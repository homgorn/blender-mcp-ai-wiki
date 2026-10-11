#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repair the 19 articles whose ЦЕЛЬ section was generated from code-block content.

An earlier version of complete_sections.py extracted the "first prose sentence"
without removing fenced code first. On these articles it lifted a shell or Python
snippet out of a ``` block and pasted it into the article, which duplicated the
block and left an unbalanced fence. The SEO gate reported it as "not exactly one
<h1>"; the article text was intact, the markdown structure was not.

The generator is fixed. This repairs what it already wrote:
  * the injected block is removed,
  * a clean, factual ЦЕЛЬ section is put back.

Detection is by content, not by file list: a ЦЕЛЬ section whose body contains a
fence marker is, by construction, corrupt.

Idempotent.

Run:  python scripts/repair_goal_sections.py [--dry]
"""
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
DRY = "--dry" in sys.argv
import complete_sections as cs  # noqa: E402  (needs sys.path above)

# A corrupt section: the heading exists and its body carries code, or the
# heading is duplicated. Two signatures, because the generator had two failure
# modes — it lifted fenced code verbatim, and it lifted loose code lines that
# sat outside any fence.
GOAL = re.compile(r"^##\s*[^\n]*ЦЕЛЬ[^\n]*\n(.*?)(?=\n---\n\n## |\n## |\Z)",
                  re.MULTILINE | re.DOTALL)

CODE_LINE = re.compile(r"^\s*(#|//|\$|>>>|\w+\([^)]*\)\s*=|[^)]*[{};]\s*$)", re.M)


def is_corrupt(body: str) -> bool:
    if "```" in body or "~~~" in body:
        return True
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith(("-", "*", ">", "|")) and CODE_LINE.match(s):
            return True
    return False


repaired = 0
for cat in cs.CATS:
    d = WIKI / cat
    if not d.exists():
        continue
    for path in sorted(d.rglob("*.md")):
        rel = path.relative_to(WIKI).as_posix()
        if rel not in cs.BY_FILE:
            continue
        text = path.read_text(encoding="utf-8")
        matches = list(GOAL.finditer(text))
        if not matches:
            continue
        if not any(is_corrupt(m.group(1)) for m in matches) and len(matches) == 1:
            continue

        # Drop every ЦЕЛЬ section, then append one clean section built by the
        # fixed generator.
        cleaned = GOAL.sub("", text)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).rstrip()
        fresh = cs.goal_section(rel, cleaned)
        out = cleaned + "\n\n---\n\n" + fresh + "\n"
        if out.strip() == text.strip():
            continue
        repaired += 1
        if DRY:
            print(f"[dry]  {rel}")
        else:
            path.write_text(out, encoding="utf-8")
            print(f"[ok]   {rel}")

# Prove the result: no ЦЕЛЬ section may contain code, and no article may have
# an unbalanced fence.
bad = 0
for cat in cs.CATS:
    d = WIKI / cat
    if not d.exists():
        continue
    for path in sorted(d.rglob("*.md")):
        t = path.read_text(encoding="utf-8")
        for m in GOAL.finditer(t):
            if is_corrupt(m.group(1)):
                bad += 1
                print(f"  STILL CORRUPT: {path.relative_to(WIKI).as_posix()}")
        if t.count("```") % 2 or t.count("~~~") % 2:
            bad += 1
            print(f"  UNBALANCED FENCE: {path.relative_to(WIKI).as_posix()}")

verb = "would repair" if DRY else "repaired"
print(f"OK {verb} {repaired} file(s); {bad} problem(s) remaining")
sys.exit(1 if bad else 0)
