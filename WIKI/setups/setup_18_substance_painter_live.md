---
id: setup_18_substance_painter_live
lang: ru
category: setups
status: stub
tags: [setup, substance]
---
# SETUP 18: SUBSTANCE PAINTER LIVE-LINK

**ID:** SETUP-18 | **Type:** Texturing Pro | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Substance → Blender живой линк. EN: Substance → Blender live link.

## 1. Шаги / Steps
1. FBX/GLTF roundtrip
2. UDIM workflow
3. Smart materials
4. Live link plugin

## 2. MCP промпт / Prompt
```
RU: "Экспорт FBX с UDIM в Substance, запеки ID/curvature/AO, верни PBR 4k в Blender" / EN: "Export FBX with UDIM to Substance, bake ID/curvature/AO, return 4k PBR to Blender"
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

- **Прочие в категории «Сетапы»:** [SETUP 19: SUBSTANCE DESIGNER SBSAR](setup_19_substance_designer_sbsar.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #substance

