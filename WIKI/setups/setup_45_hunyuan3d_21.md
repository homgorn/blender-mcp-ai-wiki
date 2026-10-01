---
id: setup_45_hunyuan3d_21
lang: ru
category: setups
status: stub
tags: [ai-3d, blender, llm, mcp, pipeline, setup]
---
# SETUP 45: HUNYUAN3D 2.1 LOCAL

**ID:** SETUP-45 | **Type:** Local 3D Gen | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Локальный Hunyuan3D. EN: Local Hunyuan3D.

## 1. Шаги / Steps
1. Hunyuan Docker
2. SD+3D pipeline
3. PBR export
4. VRAM 12GB+

## 2. MCP промпт / Prompt
```
RU: "Hunyuan3D Docker: text 'cozy cabin' → mesh + PBR 2k, импорт GLB" / EN: "Hunyuan3D Docker: 'cozy cabin' → mesh + 2k PBR, import GLB"
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

- **Прочие в категории «Сетапы»:** [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md)
- **Теги:** #ai-3d, #blender, #llm, #mcp, #pipeline, #setup

