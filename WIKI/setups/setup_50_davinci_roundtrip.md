---
id: setup_50_davinci_roundtrip
lang: ru
category: setups
status: stub
tags: [setup, video]
---
# SETUP 50: DAVINCI RESOLVE ROUNDTRIP

**ID:** SETUP-50 | **Type:** Color/Edit | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Монтаж/грейдинг туда-обратно. EN: Edit/grade roundtrip.

## 1. Шаги / Steps
1. EDL/XML
2. ACES pipeline
3. CDL/LUT
4. Back to Blender

## 2. MCP промпт / Prompt
```
RU: "Экспорт EDL+EXR в Resolve, грейд ACES, верни LUT .cube в Blender" / EN: "Export EDL+EXR to Resolve, ACES grade, return .cube LUT to Blender"
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

- **Прочие в категории «Сетапы»:** [SETUP 49: FFMPEG + VSE PIPELINE](setup_49_ffmpeg_vse_pipeline.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #video

