---
id: setup_41_hdri_lighting_lab
lang: ru
category: setups
status: stub
tags: [lighting, setup]
---
# SETUP 41: HDRI LIGHTING LAB

**ID:** SETUP-41 | **Type:** Lighting | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Лаборатория HDRI света. EN: HDRI lighting lab.

## 1. Шаги / Steps
1. HDRI rotation
2. Exposure ladder
3. Light portals
4. Volumetric

## 2. MCP промпт / Prompt
```
RU: "HDRI ladder: rotation 0/90/180/270, strength 0.5/1/2, portals on, рендер-превью" / EN: "HDRI ladder: rot 0/90/180/270, strength 0.5/1/2, portals, preview renders"
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
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [P13: LIGHTING & HDRI](../prompts/13_lighting_hdri.md), [P14: CAMERA & COMPOSITION](../prompts/14_camera_composition.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #lighting, #setup

