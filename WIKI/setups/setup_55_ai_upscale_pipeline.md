---
id: setup_55_ai_upscale_pipeline
lang: ru
category: setups
status: stub
tags: [pipeline, setup, upscale]
---
# SETUP 55: AI UPSCALE PIPELINE

**ID:** SETUP-55 | **Type:** Upscale | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Апскейл рендеров. EN: Upscale renders.

## 1. Шаги / Steps
1. ESRGAN/Topaz
2. Sequence upscale
3. Denoise+sharpen
4. EXR safe

## 2. MCP промпт / Prompt
```
RU: "Topaz/ESRGAN 2x PNG sequence → denoise → sharpen 0.2, EXR untouched" / EN: "Topaz/ESRGAN 2x PNG seq → denoise → sharpen 0.2, keep EXR"
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
- **По темам:** [SETUP 59: WEB VIEWER EXPORT](setup_59_web_viewer_export.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md)
- **Теги:** #pipeline, #setup, #upscale

