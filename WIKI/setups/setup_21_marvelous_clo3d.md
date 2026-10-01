---
id: setup_21_marvelous_clo3d
lang: ru
category: setups
status: stub
tags: [clothing, setup]
---
# SETUP 21: MARVELOUS / CLO3D CLOTH

**ID:** SETUP-21 | **Type:** Cloth | **Difficulty:** ⭐⭐⭐ | **Time:** 30-45 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Одежда из Marvelous в Blender. EN: Garments from Marvelous to Blender.

## 1. Шаги / Steps
1. Alembic cache
2. Garment import
3. Thickness/solidify
4. Collision setup

## 2. MCP промпт / Prompt
```
RU: "Импорт Alembic одежды, solidify 0.002м, collision с телом, запеки normal" / EN: "Import Alembic garment, solidify 0.002m, body collision, bake normal"
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
- **По темам:** [P03: MODIFIERS STACK](../prompts/03_modifiers_stack.md), [P21: PHYSICS SIMULATION](../prompts/21_physics_simulation.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #clothing, #setup

