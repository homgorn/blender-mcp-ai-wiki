---
id: setup_56_mocap_rokoko
lang: ru
category: setups
status: stub
tags: [mocap, setup]
---
# SETUP 56: MOCAP ROKOKO / MOVE AI

**ID:** SETUP-56 | **Type:** Mocap | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мокап в Blender. EN: Mocap to Blender.

## 1. Шаги / Steps
1. Rokoko Studio
2. Move.ai video
3. FBX retarget
4. Clean curves

## 2. MCP промпт / Prompt
```
RU: "Rokoko FBX → Rigify retarget, foot lock, clean spikes, loop" / EN: "Rokoko FBX → Rigify retarget, foot lock, despike, loop"
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

- **Прочие в категории «Сетапы»:** [SETUP 57: FACE MOCAP ARKIT](setup_57_face_mocap_arkit.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P44: MOCAP RETARGETING](../prompts/44_mocap_retarget.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **Теги:** #mocap, #setup

