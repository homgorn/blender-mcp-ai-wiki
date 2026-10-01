---
id: setup_24_metashape_scan
lang: ru
category: setups
status: stub
tags: [photogrammetry, setup]
---
# SETUP 24: AGISOFT METASHAPE

**ID:** SETUP-24 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Metashape → Blender пайплайн. EN: Metashape → Blender pipeline.

## 1. Шаги / Steps
1. Align photos
2. Dense cloud
3. Mesh+texture
4. Scale bars

## 2. MCP промпт / Prompt
```
RU: "Импорт Metashape OBJ 8k текстурой, ретопо, UDIM, запеки AO/curvature" / EN: "Import Metashape OBJ 8k texture, retopo, UDIM, bake AO/curvature"
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

- **Прочие в категории «Сетапы»:** [SETUP 23: REALITYCAPTURE SCAN TO BLENDER](setup_23_realitycapture_scan.md), [SETUP 25: POLYCAM / LUMA / KIRI SCAN](setup_25_polycam_luma.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **Теги:** #photogrammetry, #setup

