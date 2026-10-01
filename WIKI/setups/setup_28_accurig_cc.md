---
id: setup_28_accurig_cc
lang: ru
category: setups
status: stub
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

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX
