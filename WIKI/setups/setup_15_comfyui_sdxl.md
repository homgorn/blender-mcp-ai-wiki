---
id: setup_15_comfyui_sdxl
lang: ru
category: setups
status: stub
tags: [blender, setup, stable-diffusion]
---
# SETUP 15: BLENDER + COMFYUI SDXL

**ID:** SETUP-15 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 25-40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: ComfyUI как бэкенд генерации PBR. EN: ComfyUI as PBR backend.

## 1. Шаги / Steps
1. ComfyUI локально
2. SDXL base+refiner
3. ControlNet depth/canny
4. Blender texture nodes

## 2. MCP промпт / Prompt
```
RU: "Сгенерируй через ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth из viewport" / EN: "Generate via ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth from viewport"
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

- **Прочие в категории «Сетапы»:** [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #blender, #setup, #stable-diffusion

