#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export wiki DB to CSV + Obsidian vault + Notion JSON. Usage: python export_all.py [--chunk N/M]"""
import argparse, csv, json, os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
DB = WIKI/"db"/"wiki_database.json"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--chunks", type=int, default=1)
    a = ap.parse_args()
    db = json.loads(DB.read_text(encoding="utf-8"))
    entries = sorted(db["entries"], key=lambda e: e["meta"]["id"])
    n = len(entries); size = (n + a.chunks - 1)//a.chunks
    part = entries[a.chunk*size:(a.chunk+1)*size]
    out_csv = WIKI/"db"/f"wiki_export_{a.chunk}.csv"
    out_obs = WIKI/"export_obsidian"
    out_not = WIKI/"export_notion"
    out_obs.mkdir(exist_ok=True); out_not.mkdir(exist_ok=True)
    # CSV chunk
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id","title","category","type","difficulty","language","tags","tools","file","description"])
        for e in part:
            m = e["meta"]
            w.writerow([m["id"],m.get("title",""),m.get("category",""),m.get("type",""),m.get("difficulty",0),m.get("language",""),"|".join(m.get("tags",[])),"|".join(m.get("mcp_tools",[])),e["file_path"],m.get("description","")[:500]])
    # Obsidian notes chunk (wikilinks)
    for e in part:
        m = e["meta"]
        p = out_obs/f"{m['id']}.md"
        links = "\n".join([f"- [[{l['url'].split('/')[-1].replace('.md','')}]]" for l in m.get("links",[])[:10]])
        p.write_text(f"---\nid: {m['id']}\ncategory: {m.get('category','')}\ntags: [{', '.join(m.get('tags',[])[:10])}]\nlang: {m.get('language','en')}\n---\n\n# {m.get('title',m['id'])}\n\n{m.get('description','')}\n\n## Links\n{links}\n\n_File: `{e['file_path']}`_\n", encoding="utf-8")
    # Notion import JSON chunk
    nj = []
    for e in part:
        m = e["meta"]
        nj.append({"object":"page","properties":{"title":[{"text":{"content":m.get('title',m['id'])}}],"Category":{"select":{"name":m.get('category','misc')}},"Lang":{"select":{"name":m.get('language','en')}},"Difficulty":{"number":m.get('difficulty',0)},"Tags":{"multi_select":[{"name":t} for t in m.get('tags',[])[:10]]},"File":{"rich_text":[{"text":{"content":e['file_path']}}]}},"children":[{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"text":{"content":m.get('description','')[:1000]}}]}}]})
    (out_not/f"notion_import_{a.chunk}.json").write_text(json.dumps({"pages":nj}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK chunk={a.chunk}/{a.chunks} n={len(part)} csv={out_csv.name}")

if __name__=="__main__":
    main()
