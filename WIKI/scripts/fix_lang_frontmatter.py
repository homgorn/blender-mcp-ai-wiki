#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write an explicit `lang:` into the frontmatter of original articles that lack one.

Why
---
Language was being guessed at build time, and the guess was wrong often enough to
matter: `build_database.py` overrode the declared value, Russian articles got
published under /en/, and their Russian mirrors then looked like duplicates of
English originals. The corpus is genuinely mixed (P16-P50 are Russian prose, the
case files are English prose, many prompts are bilingual), so no single heuristic
separates it reliably — measured Cyrillic/Latin ratios for Russian files span
0.33-0.58 and for English files 0.00-0.41. They overlap.

The fix is not a better heuristic. Language is authoring metadata: it belongs in
the file, written by a human, and the build should just read it. This script makes
the one-time decision, records it where it is visible and overridable, and prints
the table for review.

Idempotent: files that already declare `lang:` are left untouched.

Run:  python scripts/fix_lang_frontmatter.py            # apply
      python scripts/fix_lang_frontmatter.py --dry      # just show the decision
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
DRY = "--dry" in sys.argv
CATS = ["prompts", "setups", "workflows", "cases", "references",
        "mcp", "mcp_advanced", "integrations", "simulation", "realtime", "usd",
        "pipeline", "version_control", "color", "performance", "testing",
        "security", "ml_ai", "accessibility", "collaboration", "visuals"]

CYR = re.compile(r"[Ѐ-ӿ]")
LAT = re.compile(r"[A-Za-z]")
CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿]")
FM = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)

# 0.30 measured on this corpus: Russian files score 0.33-0.58, English 0.00-0.41.
# Below this a file is more English than Russian in its prose.
THRESHOLD = 0.30


def prose_only(text: str) -> str:
    t = re.sub(r"```[\s\S]*?```", " ", text)
    t = re.sub(r"`[^`]*`", " ", t)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"^\s*\|.*\|\s*$", " ", t, flags=re.M)
    return t


def guess(text: str) -> tuple[str, float]:
    s = prose_only(text)[:8000]
    # A stray CJK glyph in a code sample is not a Chinese document: require the
    # CJK run to be a real share of the prose before calling it zh.
    cjk = len(CJK.findall(s))
    letters = len(CYR.findall(s)) + len(LAT.findall(s))
    if cjk >= 20 and letters and cjk / (cjk + letters) >= 0.05:
        return "zh", 1.0
    cyr, lat = len(CYR.findall(s)), len(LAT.findall(s))
    if cyr + lat == 0:
        return "en", 0.0
    r = cyr / (cyr + lat)
    return ("ru" if r >= THRESHOLD else "en"), r


decisions = []
written = 0
for cat in CATS:
    d = WIKI / cat
    if not d.exists():
        continue
    for f in sorted(d.glob("*.md")):
        t = f.read_text(encoding="utf-8")
        m = FM.match(t)
        if m and re.search(r"^lang\s*:", m.group(1), re.MULTILINE):
            continue  # already explicit
        lang, ratio = guess(t)
        decisions.append((cat, f.name, lang, ratio))
        if DRY:
            continue
        if m:
            new_fm = m.group(1).rstrip() + f"\nlang: {lang}"
            out = f"---\n{new_fm}\n---\n" + t[m.end():]
        else:
            out = f"---\nlang: {lang}\n---\n" + t
        f.write_text(out, encoding="utf-8")
        written += 1

decisions.sort(key=lambda r: r[3])
print(f"{'file':<52}{'lang':<6}{'ratio':>7}")
for cat, name, lang, ratio in decisions:
    print(f"{cat}/{name:<44}{lang:<6}{ratio:>7.2f}")

by = {}
for _, _, lang, _ in decisions:
    by[lang] = by.get(lang, 0) + 1
print()
print(f"decided: {len(decisions)} files -> {by}")
if DRY:
    print("DRY RUN: nothing written")
else:
    print(f"written: {written}")
    print("\nReview this table. To correct one file, edit its `lang:` in the")
    print("frontmatter; the build reads that value and never overrides it.")
