#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repair unclosed fenced code blocks.

Two articles opened a ``` block and never closed it before a heading, so the
heading and the block that followed it were swallowed into a <pre> by the
renderer. Both were in the corpus before this work started (git shows no change
to them), and neither the SEO gates nor the unit tests could see it: an unclosed
fence does not change the number of <h1> elements, it just destroys the
rendering of everything after it.

The rule used here is the one the files themselves follow: a fence carrying a
language tag opens a block, one without closes it. When a tagged fence appears
while already inside a block, the previous block was never closed, and the fix is
a closing fence immediately before the heading that got swallowed.

Both sources are mirrored into five languages, so the repair runs over every copy.
`validate.py` now checks fence balance, so a new one fails the build.

Idempotent: a file with balanced fences is left untouched.

Run:  python scripts/fix_unclosed_fences.py [--dry]
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
FENCE = "`" * 3
FENCE_RX = re.compile(r"^\s*(```+|~~~+)(.*)$")


def repair(text: str) -> tuple[str, int]:
    """Insert the missing closing fence(s). Returns the new text and the count."""
    out: list[str] = []
    inside = False
    fixed = 0
    for line in text.splitlines():
        m = FENCE_RX.match(line)
        if m:
            marker, rest = m.group(1), m.group(2).strip()
            if inside and rest:
                # A tagged fence while inside: the block above was never closed.
                # The line before this fence is the swallowed heading.
                if out and out[-1].startswith("#"):
                    out.append(marker)
                    fixed += 1
                    inside = False
                out.append(line)
                inside = True
                continue
            out.append(line)
            inside = not inside
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), fixed


def unbalanced(text: str) -> bool:
    n = len(re.findall(r"^\s*(?:```|~~~)", text, re.M))
    return n % 2 == 1


changed = []
for f in sorted(WIKI.rglob("*.md")):
    t = f.read_text(encoding="utf-8")
    if not unbalanced(t):
        continue
    new, fixed = repair(t)
    if fixed and not unbalanced(new):
        rel = f.relative_to(WIKI).as_posix()
        changed.append(rel)
        if DRY:
            print(f"[dry]  {rel}: +{fixed} closing fence(s)")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"[ok]   {rel}: +{fixed} closing fence(s)")

left = [f.relative_to(WIKI).as_posix() for f in sorted(WIKI.rglob("*.md"))
        if unbalanced(f.read_text(encoding="utf-8"))]
verb = "would repair" if DRY else "repaired"
print(f"OK {verb} {len(changed)} file(s); {len(left)} still unbalanced")
for p in left:
    print("  LEFTOVER", p)
sys.exit(1 if left else 0)
