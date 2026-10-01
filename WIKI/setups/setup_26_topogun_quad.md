---
id: setup_26_topogun_quad
lang: ru
category: setups
status: stub
tags: [setup, topology]
---
# SETUP 26: TOPOGUN / QUAD DRAW RETOPO

**ID:** SETUP-26 | **Type:** Retopo | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Ручная ретопология для анимации. EN: Manual retopo for animation.

## 1. Шаги / Steps
1. Manual retopo
2. Edge flow
3. Shrinkwrap
4. Bake maps

## 2. MCP промпт / Prompt
```
RU: "Ретопо лица: loops вокруг глаз/рта, полюса 3/5, shrinkwrap 0.001" / EN: "Retopo face: loops around eyes/mouth, 3/5 poles, shrinkwrap 0.001"
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

- **Прочие в категории «Сетапы»:** [SETUP 22: RIZOMUV BRIDGE](setup_22_rizomuv_bridge.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #topology

