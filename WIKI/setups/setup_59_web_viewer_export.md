---
id: setup_59_web_viewer_export
lang: ru
category: setups
status: stub
tags: [pipeline, setup, web]
---
# SETUP 59: WEB VIEWER EXPORT

**ID:** SETUP-59 | **Type:** Web 3D | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Вьювер для сайта. EN: Web viewer.

## 1. Шаги / Steps
1. GLB+Draco
2. Three.js viewer
3. KTX2 Basis
4. GitHub Pages

## 2. MCP промпт / Prompt
```
RU: "GLB Draco + KTX2, three.js viewer template, deploy GitHub Pages" / EN: "Draco GLB + KTX2, three.js template, deploy Pages"
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

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 49: FFMPEG + VSE PIPELINE](setup_49_ffmpeg_vse_pipeline.md)
- **По темам:** [P39: EXPORT PRESETS (GLB/FBX/USD)](../prompts/39_export_presets.md), [SETUP 55: AI UPSCALE PIPELINE](setup_55_ai_upscale_pipeline.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md)
- **Теги:** #pipeline, #setup, #web

