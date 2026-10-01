---
id: setup_34_metahuman_blender
lang: ru
category: setups
status: stub
tags: [blender, character, setup]
---
# SETUP 34: METAHUMAN → BLENDER

**ID:** SETUP-34 | **Type:** MetaHuman | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: MetaHuman для Blender рендера. EN: MetaHuman for Blender render.

## 1. Шаги / Steps
1. Quixel Bridge
2. DNA/livelink
3. Groom convert
4. LOD/render

## 2. MCP промпт / Prompt
```
RU: "Quixel Bridge MetaHuman LOD0, groom→curves, materials to Principled" / EN: "Quixel Bridge MetaHuman LOD0, groom→curves, to Principled"
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

- **Прочие в категории «Сетапы»:** [SETUP 32: DAZ → BLENDER (DIFFEOMORPHIC)](setup_32_daz_diffeomorphic.md), [SETUP 36: VROID STUDIO → BLENDER](setup_36_vroid_studio.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #blender, #character, #setup

