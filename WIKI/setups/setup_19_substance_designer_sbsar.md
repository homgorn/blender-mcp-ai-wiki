---
id: setup_19_substance_designer_sbsar
lang: ru
category: setups
status: stub
tags: [setup, shading, substance]
---
# SETUP 19: SUBSTANCE DESIGNER SBSAR

**ID:** SETUP-19 | **Type:** Procedural | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Параметрические .sbsar в Blender. EN: Parametric .sbsar in Blender.

## 1. Шаги / Steps
1. SBSAR import
2. Exposed params
3. Tiling control
4. Blender shader graph

## 2. MCP промпт / Prompt
```
RU: "Импортируй .sbsar кирпич, exposed: mortar width, color variation, roughness" / EN: "Import .sbsar brick, exposed: mortar width, color variation, roughness"
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

- **Прочие в категории «Сетапы»:** [SETUP 18: SUBSTANCE PAINTER LIVE-LINK](setup_18_substance_painter_live.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [P09: PRINCIPLED BSDF SETUP](../prompts/09_principled_bsdf.md), [P10: NODE GROUP CREATION](../prompts/10_node_groups.md), [P11: PROCEDURAL TEXTURES](../prompts/11_procedural_textures.md)
- **Теги:** #setup, #shading, #substance

