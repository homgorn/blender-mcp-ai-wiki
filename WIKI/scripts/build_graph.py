#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Obsidian-style graph.json from wiki_database.json"""
import json
import math
import hashlib
from pathlib import Path
WIKI = Path(r"C:\BLENDER ai\WIKI")
DB = WIKI/"db"/"wiki_database.json"
OUT = WIKI/"db"/"graph.json"
db = json.loads(DB.read_text(encoding="utf-8"))
nodes=[]; links=[]; seen=set()
for e in db["entries"]:
    m=e["meta"]; nid=m["id"]
    if nid not in seen:
        seen.add(nid)
        nodes.append({"id":nid,"title":m.get("title",""),"category":m.get("category",""),"lang":m.get("language","en"),"tags":m.get("tags",[])[:8],"file":e["file_path"]})
    for l in m.get("links",[])[:8]:
        t=l.get("url","").split("/")[-1].replace(".md","")
        if t and t!=nid:
            links.append({"source":nid,"target":t,"label":l.get("text","")[:40]})
# Deterministic precomputed layout (golden-angle spiral, category sectors).
# graph.html uses x/y directly — no force layout in browser.
cats = sorted({n["category"] or "misc" for n in nodes})
cati = {c: i for i, c in enumerate(cats)}
bycat = {}
for n in sorted(nodes, key=lambda x: x["id"]):
    bycat.setdefault(n["category"] or "misc", []).append(n)
for c, items in bycat.items():
    off = 2 * math.pi * cati[c] / max(1, len(cats))
    for i, n in enumerate(items):
        a = off + i * 2.39996
        r = 120 + 26 * math.sqrt(i) + (int(hashlib.md5(n["id"].encode()).hexdigest()[:4], 16) % 40)
        n["x"] = round(math.cos(a) * r, 1)
        n["y"] = round(math.sin(a) * r, 1)
OUT.write_text(json.dumps({"nodes":nodes,"links":links}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK nodes={len(nodes)} links={len(links)} -> {OUT.name}")
