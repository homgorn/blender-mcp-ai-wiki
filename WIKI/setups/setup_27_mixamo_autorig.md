---
id: setup_27_mixamo_autorig
lang: ru
category: setups
status: stub
tags: [rigging, setup]
---
# SETUP 27: MIXAMO AUTO-RIG

**ID:** SETUP-27 | **Type:** Auto Rig | **Difficulty:** ⭐ | **Time:** 10 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Mixamo риг за 10 минут. EN: Mixamo rig in 10 minutes.

## 1. Шаги / Steps
1. T-pose import
2. Auto-rig
3. Skin + fix
4. MCP batch

## 2. MCP промпт / Prompt
```
RU: "Загрузи T-pose FBX, Mixamo auto-rig, скачай 5 анимаций, ретаргет в Blender" / EN: "Upload T-pose FBX, Mixamo auto-rig, download 5 anims, retarget in Blender"
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

- **Прочие в категории «Сетапы»:** [SETUP 28: ACCURIG / ACTORCORE RIG](setup_28_accurig_cc.md), [SETUP 29: AUTO-RIG PRO](setup_29_autorignpro.md), [SETUP 30: RIGIFY ADVANCED + FACE](setup_30_rigify_advanced.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P17: RIGIFY HUMANOID SETUP](../prompts/17_rigify_setup.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #rigging, #setup

