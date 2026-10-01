---
id: setup_22_rizomuv_bridge
lang: ru
category: setups
status: stub
tags: [setup, topology]
---
# SETUP 22: RIZOMUV BRIDGE

**ID:** SETUP-22 | **Type:** UV Pro | **Difficulty:** ⭐⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Идеальная развертка через RizomUV. EN: Perfect unwrap via RizomUV.

## 1. Шаги / Steps
1. FBX roundtrip
2. Auto seams
3. Pack islands
4. UDIM tiles

## 2. MCP промпт / Prompt
```
RU: "Экспорт в RizomUV, auto seams by angle 70°, pack margin 4px, верни UV" / EN: "Export to RizomUV, auto seams 70°, pack 4px, return UVs"
```

## 3. Проверка / Check
- [ ] Аддон/сервис отвечает
- [ ] Тестовая сцена собирается
- [ ] Экспорт читается целевым софтом

## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 26: TOPOGUN / QUAD DRAW RETOPO](setup_26_topogun_quad.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #topology

