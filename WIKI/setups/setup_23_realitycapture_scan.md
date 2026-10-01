---
id: setup_23_realitycapture_scan
lang: ru
category: setups
status: stub
tags: [blender, photogrammetry, setup]
---
# SETUP 23: REALITYCAPTURE SCAN TO BLENDER

**ID:** SETUP-23 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 40-60 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Фотограмметрия → game-ready. EN: Photogrammetry → game-ready.

## 1. Шаги / Steps
1. RC CLI
2. Laser+photo align
3. Decimate/retopo
4. PBR bake 8k

## 2. MCP промпт / Prompt
```
RU: "Импорт RC mesh 5M tris → Quad Remesher 20k → Smart UV → bake 8k→2k" / EN: "Import RC 5M mesh → Quad Remesher 20k → Smart UV → bake 8k→2k"
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

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #photogrammetry, #setup

