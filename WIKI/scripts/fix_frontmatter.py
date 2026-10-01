#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove the derived `tags:` line from frontmatter (idempotent).

Why this exists
---------------
`bulk_multilang.py` copied body-extracted tags into the frontmatter of 363
mirrors, unquoted and unfiltered: `tags: **, 8b7355`. A bare `*` is a YAML
alias indicator, so PyYAML raised "while scanning an alias" and
`extract_frontmatter` swallowed the error -> the entire frontmatter of those
363 files was silently discarded (no `translation:`, no `id:`, no `lang:`).

`meta["tags"]` is derived from the body by extract_metadata() anyway, so a
hand-written tags line in frontmatter is redundant *and* dangerous. It is
removed at the source instead of quoted.

Run:  python scripts/fix_frontmatter.py
"""
import re
import sys
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WIKI = Path(r"C:\BLENDER ai\WIKI")
FM = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
# derived fields that must never be hand-written into frontmatter
DERIVED = ("tags",)


def main():
    fixed = checked = 0
    leftovers = []
    for f in sorted((WIKI / "multilang").rglob("*.md")):
        t = f.read_text(encoding="utf-8")
        m = FM.match(t)
        if not m:
            continue
        checked += 1
        block, body = m.group(1), t[m.end():]
        lines = [ln for ln in block.split("\n")
                 if not any(re.match(rf"^{k}\s*:", ln, re.IGNORECASE) for k in DERIVED)]
        new_block = "\n".join(lines)
        if new_block != block:
            f.write_text(f"---\n{new_block}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
            fixed += 1
        if any(re.match(rf"^{k}\s*:", ln, re.IGNORECASE) for k in DERIVED
               for ln in new_block.split("\n")):
            leftovers.append(str(f.relative_to(WIKI)))
    print(f"OK frontmatter: checked={checked} cleaned={fixed} leftovers={len(leftovers)}")
    if leftovers:
        print("  still present:", leftovers[:5])
    return 1 if leftovers else 0


if __name__ == "__main__":
    sys.exit(main())
