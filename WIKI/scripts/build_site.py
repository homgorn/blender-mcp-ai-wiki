#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build static site data: copy db JSON to site/data + sitemap + langs manifest."""
import json, os, shutil
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
SITE = WIKI/"site"; DATA = SITE/"data"
DATA.mkdir(parents=True, exist_ok=True)
for f in ["wiki_database.json","search_index.json","wiki_export.json","graph.json"]:
    s = WIKI/"db"/f
    if s.exists():
        shutil.copy2(s, DATA/f)
        print(f"copied {f} ({s.stat().st_size//1024} KB)")
# sitemap: list entry urls (hash routes)
db = json.loads((DATA/"wiki_database.json").read_text(encoding="utf-8"))
urls=[{"id":e["meta"]["id"],"lang":e["meta"].get("language","en"),"cat":e["meta"].get("category",""),"title":e["meta"].get("title","")[:120]} for e in db["entries"]]
(DATA/"sitemap.json").write_text(json.dumps({"total":len(urls),"items":urls}, ensure_ascii=False), encoding="utf-8")
# langs manifest
langs={}
for e in db["entries"]:
    l=e["meta"].get("language","en"); c=e["meta"].get("category","misc")
    langs.setdefault(l,{}).setdefault(c,0)
    langs[l][c]+=1
(DATA/"langs.json").write_text(json.dumps(langs, ensure_ascii=False, indent=1), encoding="utf-8")
# lightweight meta index (for fast first paint without full DB)
meta=[{"id":e["meta"]["id"],"title":e["meta"].get("title",""),"category":e["meta"].get("category","misc"),"type":e["meta"].get("type",""),"difficulty":e["meta"].get("difficulty",0),"tags":e["meta"].get("tags",[]),"language":e["meta"].get("language","en"),"file":e["file_path"],"desc":e["meta"].get("description","")[:300]} for e in db["entries"]]
(DATA/"meta.json").write_text(json.dumps({"total":len(meta),"items":meta}, ensure_ascii=False), encoding="utf-8")
# per-category chunks with full entries (lazy-loaded by openEntry)
chunksdir = DATA/"chunks"
chunksdir.mkdir(parents=True, exist_ok=True)
bycat = {}
for e in db["entries"]:
    bycat.setdefault(e["meta"].get("category","misc"), []).append(e)
for cat, items in bycat.items():
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in cat) or "misc"
    (chunksdir/f"entries_{safe}.json").write_text(json.dumps({"category":cat,"total":len(items),"items":items}, ensure_ascii=False), encoding="utf-8")
print(f"OK entries={len(urls)} langs={list(langs.keys())} chunks={len(bycat)}")
