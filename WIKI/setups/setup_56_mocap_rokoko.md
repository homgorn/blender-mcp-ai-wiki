---
id: setup_56_mocap_rokoko
lang: ru
category: setups
status: full
---
# SETUP 56: MOCAP ROKOKO / MOVE AI

**ID:** SETUP-56 | **Type:** Mocap | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мокап в Blender. EN: Mocap to Blender.

## 1. Шаги / Steps
1. Rokoko Studio
2. Move.ai video
3. FBX retarget
4. Clean curves

## 2. MCP промпт / Prompt
```
RU: "Rokoko FBX → Rigify retarget, foot lock, clean spikes, loop" / EN: "Rokoko FBX → Rigify retarget, foot lock, despike, loop"
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

---

## FULL GUIDE

### Пайплайн
1. Rokoko Studio → export FBX (60fps).
2. Blender: import → retarget на Rigify (см. P44).
3. Foot lock на контактных кадрах, despike, bake.
4. Loop: первый = последний+1.

### Проверка
- [ ] Стопы не скользят
- [ ] Нет спайков в Graph Editor

