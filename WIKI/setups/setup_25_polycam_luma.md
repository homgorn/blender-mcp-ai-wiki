---
id: setup_25_polycam_luma
lang: ru
category: setups
status: stub
tags: [photogrammetry, setup]
---
# SETUP 25: POLYCAM / LUMA / KIRI SCAN

**ID:** SETUP-25 | **Type:** Mobile Scan | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мобильные сканы → Blender. EN: Mobile scans → Blender.

## 1. Шаги / Steps
1. NeRF/Gaussian splat
2. GLB export
3. Cleanup
4. Scale fix

## 2. MCP промпт / Prompt
```
RU: "Импорт Polycam GLB, почини масштаб x0.01, удали мусор, ретопо" / EN: "Import Polycam GLB, fix scale x0.01, cleanup, retopo"
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

- **Прочие в категории «Сетапы»:** [SETUP 23: REALITYCAPTURE SCAN TO BLENDER](setup_23_realitycapture_scan.md), [SETUP 24: AGISOFT METASHAPE](setup_24_metashape_scan.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **Теги:** #photogrammetry, #setup

