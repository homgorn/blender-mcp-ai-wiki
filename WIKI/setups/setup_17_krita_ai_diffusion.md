---
id: setup_17_krita_ai_diffusion
lang: ru
category: setups
status: stub
tags: [2d-ai, blender, setup]
---
# SETUP 17: BLENDER + KRITA AI DIFFUSION

**ID:** SETUP-17 | **Type:** 2D/3D Paint | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Рисуешь в Krita — обновляется в Blender. EN: Paint in Krita — updates in Blender.

## 1. Шаги / Steps
1. Krita AI Diffusion plugin
2. Inpaint/outpaint
3. Live paint to Blender texture
4. Layer sync

## 2. MCP промпт / Prompt
```
RU: "Настрой Krita AI Diffusion live-sync с Blender текстурой 2k" / EN: "Setup Krita AI Diffusion live-sync with Blender 2k texture"
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
- **Теги:** #blender, #setup

