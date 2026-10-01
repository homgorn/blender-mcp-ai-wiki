---
id: setup_58_vr_scene_inspection
lang: ru
category: setups
status: stub
tags: [setup, vr]
---
# SETUP 58: VR SCENE INSPECTION

**ID:** SETUP-58 | **Type:** VR/XR | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Проверка сцены в VR. EN: VR scene check.

## 1. Шаги / Steps
1. Blender XR
2. Quest Link
3. Scale check
4. Annotate

## 2. MCP промпт / Prompt
```
RU: "Blender XR session, Quest Link, scale 1:1, аннотации маркерами" / EN: "Blender XR, Quest Link, 1:1 scale, marker annotations"
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
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #vr

