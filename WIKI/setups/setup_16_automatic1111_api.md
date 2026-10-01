---
id: setup_16_automatic1111_api
lang: ru
category: setups
status: stub
tags: [api, blender, setup, stable-diffusion]
---
# SETUP 16: BLENDER + AUTOMATIC1111 API

**ID:** SETUP-16 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: A1111 API как дешевый SD-бэкенд. EN: A1111 API as cheap SD backend.

## 1. Шаги / Steps
1. A1111 --api
2. img2img/inpaint
3. Blender image editor bridge
4. Batch queue

## 2. MCP промпт / Prompt
```
RU: "Через A1111 API: img2img strength 0.5, 30 steps, seamless tile" / EN: "Via A1111 API: img2img strength 0.5, 30 steps, seamless tiling"
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

- **Прочие в категории «Сетапы»:** [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 15: BLENDER + COMFYUI SDXL](setup_15_comfyui_sdxl.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #api, #blender, #setup, #stable-diffusion

