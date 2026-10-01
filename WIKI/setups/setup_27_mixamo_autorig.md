---
id: setup_27_mixamo_autorig
lang: ru
category: setups
status: stub
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

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX
