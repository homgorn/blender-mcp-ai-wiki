#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
b = Path(r"C:\BLENDER ai\WIKI\multilang")
base = {p.relative_to(b/"en").as_posix(): p for p in (b/"en").rglob("*.md")}
for lang in ["ru","es","de","zh"]:
    cur = {p.relative_to(b/lang).as_posix() for p in (b/lang).rglob("*.md")}
    missing = sorted(set(base) - cur)
    extra = sorted(cur - set(base))
    print(lang, "total", len(cur), "missing", len(missing))
    for m in missing[:20]:
        print("  MISSING", m)
    for m in extra[:10]:
        print("  EXTRA", m)
