#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove links headings that have no body.

The bulk-authored files carried a prose reference heading like

    ## 🔗 Setup 01, Setup 08, INDEX

An earlier repair pass replaced the *content* of such sections with real links,
but only when the section still had prose to recognise. Once the body was gone
the heading became an empty `##` and the pass had nothing to match, so the empty
heading survived next to the real `## 🔗 СВЯЗИ`. 166 files ended up with a
stray heading that renders as an empty section.

The rule is simple and safe: a links-ish heading whose body is empty before the
next heading, or before the end of the file, is removed. A heading with any
content is never touched, so a file with exactly one links section keeps it.

Idempotent.

Run:  python scripts/fix_empty_link_headings.py [--dry]
"""
import re
import sys
import os
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
DRY = "--dry" in sys.argv

# A `##` links-ish heading and its body, up to the next heading or EOF.
HEAD = re.compile(
    r"^##[ \t]*[^\n]*(?:\U0001F517|СВЯЗИ|Связи|LINKS)[^\n]*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL)


def fix(text: str) -> tuple[str, int]:
    removed = 0
    while True:
        for m in HEAD.finditer(text):
            if m.group(1).strip() == "":
                # Drop the heading and the blank lines it left behind.
                text = text[: m.start()] + text[m.end():]
                text = re.sub(r"\n{3,}", "\n\n", text)
                removed += 1
                break
        else:
            return text, removed


changed = 0
total = 0
for path in sorted(WIKI.rglob("*.md")):
    t = path.read_text(encoding="utf-8")
    if "##" not in t:
        continue
    new, removed = fix(t)
    if not removed:
        continue
    changed += 1
    total += removed
    if DRY:
        print(f"[dry]  {path.relative_to(WIKI).as_posix()}: -{removed}")
    else:
        path.write_text(new, encoding="utf-8")
        print(f"[ok]   {path.relative_to(WIKI).as_posix()}: -{removed}")

left = []
for path in sorted(WIKI.rglob("*.md")):
    for m in HEAD.finditer(path.read_text(encoding="utf-8")):
        if m.group(1).strip() == "":
            left.append(path.relative_to(WIKI).as_posix())
            break

verb = "would remove" if DRY else "removed"
print(f"OK {verb} {total} empty heading(s) in {changed} file(s); {len(left)} remaining")
for p in left[:10]:
    print("  LEFTOVER", p)
sys.exit(1 if left else 0)
