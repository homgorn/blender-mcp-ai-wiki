---
id: setup_57_face_mocap_arkit
lang: ru
category: setups
status: stub
tags: [mocap, setup, vr]
---
# SETUP 57: FACE MOCAP ARKIT

**ID:** SETUP-57 | **Type:** Face Cap | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Лицевой мокап. EN: Face mocap.

## 1. Шаги / Steps
1. iPhone LiveLink
2. 52 blendshapes
3. Shape key map
4. Audio sync

## 2. MCP промпт / Prompt
```
RU: "ARKit 52 blendshapes → shape keys, smoothing 5, audio lip-sync rough" / EN: "ARKit 52 → shape keys, smooth 5, rough lip-sync"
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

- **Прочие в категории «Сетапы»:** [SETUP 56: MOCAP ROKOKO / MOVE AI](setup_56_mocap_rokoko.md), [SETUP 58: VR SCENE INSPECTION](setup_58_vr_scene_inspection.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P44: MOCAP RETARGETING](../prompts/44_mocap_retarget.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **Теги:** #mocap, #setup, #vr

