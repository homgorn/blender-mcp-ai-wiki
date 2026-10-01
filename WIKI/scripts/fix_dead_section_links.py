"""One-off repair, kept for the record: two dead section links in the corpus.

`../lighting/` and `../materials/` name directories that do not exist and never
did. In both files the surrounding label already says "Prompts" / "Промпты", and
the files they grouped (P09-P15, P16-P21) do live in `prompts/`, so the intent was
the prompts category. Repointed to `../prompts/`.

Before: 3 broken internal links on the built site.
After:  0.

The site gate now resolves relative hrefs, so this class of error fails the
build instead of shipping.
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WIKI = Path(r"C:\BLENDER ai\WIKI")
FIX = {"(../lighting/)": "(../prompts/)", "(../materials/)": "(../prompts/)"}

changed = 0
touched: list[str] = []
for f in sorted(WIKI.rglob("*.md")):
    t = f.read_text(encoding="utf-8")
    new = t
    for bad, good in FIX.items():
        new = new.replace(bad, good)
    if new != t:
        f.write_text(new, encoding="utf-8")
        changed += 1
        touched.append(f.relative_to(WIKI).as_posix())

print(f"repaired {changed} file(s):")
for p in touched:
    print("  ", p)

# Prove nothing of the old form survives
left = []
for f in sorted(WIKI.rglob("*.md")):
    if re.search(r"\.\./(lighting|materials)/", f.read_text(encoding="utf-8")):
        left.append(f.relative_to(WIKI).as_posix())
print("remaining ../lighting/ or ../materials/ :", len(left))
for p in left:
    print("  LEFTOVER", p)
