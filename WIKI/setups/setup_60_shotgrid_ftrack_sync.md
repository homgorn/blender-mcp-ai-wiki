---
id: setup_60_shotgrid_ftrack_sync
lang: ru
category: setups
status: stub
tags: [production, setup]
---
# SETUP 60: SHOTGRID / FTRACK SYNC

**ID:** SETUP-60 | **Type:** Production | **Difficulty:** ⭐⭐⭐ | **Time:** 35 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Продакшн-трекинг. EN: Production tracking.

## 1. Шаги / Steps
1. Shot entities
2. Version publish
3. Review notes
4. Status sync

## 2. MCP промпт / Prompt
```
RU: "ShotGrid: shot/tasks/versions, publish EXR+MP4, review notes → Blender markers" / EN: "ShotGrid: shots/tasks/versions, publish EXR+MP4, notes → Blender markers"
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

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **Теги:** #production, #setup

