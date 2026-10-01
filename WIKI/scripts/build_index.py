#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate WIKI/INDEX.md + CHANGELOG entry from real directory scan + DB stats."""
import json
from pathlib import Path
from datetime import date
WIKI = Path(r"C:\BLENDER ai\WIKI")
DB = WIKI/"db"/"wiki_database.json"

def list_md(d):
    p = WIKI/d
    if not p.exists(): return []
    return sorted([f.name for f in p.glob("*.md")])

prompts = list_md("prompts"); cases = list_md("cases"); setups = list_md("setups")
wfs = list_md("workflows"); adv = {}
for d in ["mcp_advanced","integrations","simulation","realtime","usd","pipeline","color","performance","security","blender_api","references/v1/addons","references/v1/api","references/v1/guides","references/v1/mcp","references/v1/workflows","crossref","mcp","api","guides","visuals"]:
    adv[d] = list_md(d)
try:
    db = json.loads(DB.read_text(encoding="utf-8"))
    stats = db.get("statistics", {})
except Exception:
    stats = {}

def links(files, folder):
    return " ".join(f"[{f.replace('.md','')}]({folder}/{f})" for f in files[:12]) + (" ..." if len(files) > 12 else "")

L = []
L.append("# BLENDER + MCP WIKI — MASTER INDEX\n")
L.append(f"**Версия:** 2.0 | **Дата:** {date.today().isoformat()} | **Статус:** Активное развитие")
L.append(f"**Записей в базе:** {stats.get('total_entries','?')} | **Слов:** {stats.get('total_words','?')} | **Код-блоков:** {stats.get('total_code_blocks','?')}")
L.append("**Языки:** en / ru / es / de / zh (`multilang/`) | **API:** `scripts/wiki_api.py :8099` | **Сайт:** `site/`")
L.append("\n---\n")
L.append("## Структура (фактическая, сгенерирована скриптом `scripts/build_index.py`)\n")
L.append(f"### Prompts ({len(prompts)}) — `prompts/`")
L.append(links(prompts, "prompts") + "\n")
L.append(f"### Cases ({len(cases)}) — `cases/`")
L.append(links(cases, "cases") + "\n")
L.append(f"### Setups ({len(setups)}) — `setups/`")
L.append(links(setups, "setups") + "\n")
L.append(f"### Workflows ({len(wfs)}) — `workflows/`")
L.append(links(wfs, "workflows") + "\n")
L.append("### Advanced / References")
for d, files in adv.items():
    if files:
        L.append(f"- **{d}** ({len(files)}): {links(files, d)}")
L.append("\n---\n")
L.append("## Кластеры промптов\n")
L.append("| Кластер | Файлы |")
L.append("|---|---|")
L.append("| Geometry (01-08) | 01_geometry_basics → 08_sculpting_basics |")
L.append("| Materials/Lighting/Camera/Comp (09-15) | 09_principled_bsdf → 15_compositing |")
L.append("| Animation (16-20) | 16_keyframe_animation → 20_shape_keys |")
L.append("| Physics/GN/MCP/Advanced (21-30) | 21_physics_simulation → 30_optimization |")
L.append("\n---\n")
L.append("## Сайт и API\n")
L.append("- Сайт: открыть `site/index.html` (Static JSON) или `http://127.0.0.1:8099/site/` (API режим)")
L.append("- API: `python scripts/wiki_api.py --port 8099` → `/api/search`, `/api/entry`, `/api/list`, `/api/graph`, `/api/version`, `POST /api/export` (контракт: `SDD/API.md`)")
L.append("- Полный цикл одной командой: `python scripts/run_all.py`")
L.append("- Пересборка: `python scripts/build_database.py` → `python scripts/build_graph.py` → `python scripts/build_site.py`")
L.append("- Валидация: `python scripts/validate.py`")
(WIKI/"INDEX.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"OK INDEX.md: prompts={len(prompts)} cases={len(cases)} setups={len(setups)} wf={len(wfs)}")
