---
id: setup_49_ffmpeg_vse_pipeline
lang: ru
category: setups
status: stub
tags: [pipeline, setup, video]
---
# SETUP 49: FFMPEG + VSE PIPELINE

**ID:** SETUP-49 | **Type:** Video | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Монтаж+кодирование. EN: Edit+encode.

## 1. Шаги / Steps
1. VSE strips
2. Proxy 25%
3. FFmpeg encode
4. HDR metadata

## 2. MCP промпт / Prompt
```
RU: "VSE: 3 strips + crossfade + text, proxy 25%, FFmpeg H264 CRF18 + ProRes master" / EN: "VSE: 3 strips + cross + text, 25% proxy, FFmpeg H264 CRF18 + ProRes"
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

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 50: DAVINCI RESOLVE ROUNDTRIP](setup_50_davinci_roundtrip.md)
- **По темам:** [SETUP 55: AI UPSCALE PIPELINE](setup_55_ai_upscale_pipeline.md), [SETUP 59: WEB VIEWER EXPORT](setup_59_web_viewer_export.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md)
- **Теги:** #pipeline, #setup, #video

