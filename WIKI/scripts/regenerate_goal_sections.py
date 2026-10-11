#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate the ЦЕЛЬ sections that a generator wrote, with the fixed generator.

Every ЦЕЛЬ section whose body contains `категории «...»` was written by
complete_sections.py — the bulk-authored setups, workflows and cases have
hand-written ones and are left alone, which is why the test is on the text rather
than on the file.

Why regenerate rather than pattern-match the damage: the broken versions were
five different shapes, and every detector I wrote for them caught a different
subset. A generated section has a known form, so replacing it wholesale removes
the whole class instead of chasing instances:

  - eight empty `- [ ]` checkbox lines
  - a Windows path, which is a fact but not a goal
  - an un-fenced Python snippet
  - a bare "2."
  - an English sentence, because the file's language is English and the
    "first prose sentence" heuristic does not know the corpus is bilingual

Idempotent: after this, re-running changes nothing.

Run:  python scripts/regenerate_goal_sections.py [--dry]
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
import complete_sections as cs  # noqa: E402

# Only generator-written sections. The phrase is the generated opening.
GOAL = re.compile(r"^##\s*[^\n]*(?:ЦЕЛЬ|GOAL)[^\n]*\n(.*?)(?=\n---\n\n## |\n## |\Z)",
                  re.MULTILINE | re.DOTALL)
GENERATED = "категории «"

regenerated = 0
skipped_handwritten = 0
for cat in cs.CATS:
    d = WIKI / cat
    if not d.exists():
        continue
    for path in sorted(d.rglob("*.md")):
        rel = path.relative_to(WIKI).as_posix()
        if rel not in cs.BY_FILE:
            continue
        text = path.read_text(encoding="utf-8")
        m = GOAL.search(text)
        if not m:
            continue
        if GENERATED not in m.group(1):
            skipped_handwritten += 1
            continue
        # The generator reads the source prose, so it must be given the document
        # with the stale section removed — otherwise it can pick its own words back
        # up, which is how the code fragments got in there in the first place.
        stripped = GOAL.sub("", text)
        # The separator before the section survives the removal, and appending a
        # fresh one would accumulate a `---` per run. That is the whole reason the
        # first version of this script was not idempotent.
        stripped = re.sub(r"(?:\n[ \t]*-{3,}[ \t]*)+[ \t]*$", "", stripped.rstrip())
        stripped = re.sub(r"\n{3,}", "\n\n", stripped).rstrip()
        fresh = cs.goal_section(rel, stripped)
        out = stripped + "\n\n---\n\n" + fresh + "\n"
        if out.strip() == text.strip():
            continue
        regenerated += 1
        if DRY:
            print(f"[dry]  {rel}")
        else:
            path.write_text(out, encoding="utf-8")
            print(f"[ok]   {rel}")

# The mirrors are copies of the originals: they must carry the same section, or
# the Russian page would differ from the English one for no stated reason.
mirrors_fixed = 0
for path in sorted((WIKI / "multilang").rglob("*.md")):
    rel_ml = path.relative_to(WIKI / "multilang").as_posix()
    parts = rel_ml.split("/")
    if len(parts) < 2:
        continue
    orig_rel = "/".join(parts[1:])
    if orig_rel not in cs.BY_FILE:
        continue
    text = path.read_text(encoding="utf-8")
    m = GOAL.search(text)
    if not m or GENERATED not in m.group(1):
        continue
    orig_text = (WIKI / orig_rel).read_text(encoding="utf-8")
    orig_m = GOAL.search(orig_text)
    if not orig_m:
        continue
    if m.group(0).strip() == orig_m.group(0).strip():
        continue
    out = text[:m.start()] + orig_m.group(0).rstrip() + "\n" + text[m.end():]
    mirrors_fixed += 1
    if DRY:
        print(f"[dry]  mirror {rel_ml}")
    else:
        path.write_text(out, encoding="utf-8")
        print(f"[ok]   mirror {rel_ml}")

verb = "would regenerate" if DRY else "regenerated"
print(f"OK {verb} {regenerated} generated section(s), "
      f"synced {mirrors_fixed} mirror(s), {skipped_handwritten} hand-written left alone")
