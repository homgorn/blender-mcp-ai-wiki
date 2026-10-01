---
id: setup_35_readyplayerme
lang: ru
category: setups
status: stub
tags: [automation, blender, llm, mcp, rigging, setup, stable-diffusion]
---
# SETUP 35: READY PLAYER ME AVATARS

**ID:** SETUP-35 | **Type:** Avatar | **Difficulty:** ⭐ | **Time:** 10 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: RPM аватары пачкой. EN: RPM avatars in batch.

## 1. Шаги / Steps
1. GLB API
2. Mixamo rig
3. Face photo
4. Web3/VR

## 2. MCP промпт / Prompt
```
RU: "RPM API: 10 аватаров GLB full-body, Mixamo rig, импорт в Blender коллекцию" / EN: "RPM API: 10 GLB full-body avatars, Mixamo rig, import to Blender collection"
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

- **Прочие в категории «Сетапы»:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 15: BLENDER + COMFYUI SDXL](setup_15_comfyui_sdxl.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md)
- **Теги:** #automation, #blender, #llm, #mcp, #rigging, #setup, #stable-diffusion

