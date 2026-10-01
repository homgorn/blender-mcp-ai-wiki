---
id: setup_28_accurig_cc
lang: ru
category: setups
status: stub
tags: [rigging, setup]
---
# SETUP 28: ACCURIG / ACTORCORE RIG

**ID:** SETUP-28 | **Type:** Auto Rig | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Reallusion риггинг. EN: Reallusion rigging.

## 1. Шаги / Steps
1. AccuRig skeleton
2. ActorCore motions
3. Blender retarget
4. Face+body

## 2. MCP промпт / Prompt
```
RU: "AccuRig скелет, 3 ActorCore анимации, ретаргет на Rigify" / EN: "AccuRig skeleton, 3 ActorCore anims, retarget to Rigify"
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

- **Прочие в категории «Сетапы»:** [SETUP 27: MIXAMO AUTO-RIG](setup_27_mixamo_autorig.md), [SETUP 29: AUTO-RIG PRO](setup_29_autorignpro.md), [SETUP 30: RIGIFY ADVANCED + FACE](setup_30_rigify_advanced.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P17: RIGIFY HUMANOID SETUP](../prompts/17_rigify_setup.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #rigging, #setup

