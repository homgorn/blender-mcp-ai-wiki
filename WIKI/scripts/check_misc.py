#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check misc/ dupes: every misc stem must have a counterpart in proper category."""
import os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
ml = WIKI/"multilang"
proper = set()
for lang in ["en","ru","es","de","zh"]:
    for cat in ["prompts","cases","setups","workflows"]:
        d = ml/lang/cat
        if d.exists():
            proper.update(p.name for p in d.glob("*.md"))
for lang in ["en","ru","es","de","zh"]:
    d = ml/lang/"misc"
    if not d.exists():
        print(lang, "no misc dir"); continue
    files = list(d.glob("*.md"))
    orphans = [f.name for f in files if f.name not in proper]
    print(f"{lang}: misc={len(files)} orphans={len(orphans)}")
    for o in orphans[:20]:
        print("  ORPHAN", o)
