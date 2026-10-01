---
id: setup_26_topogun_quad
lang: ru
category: setups
status: stub
---
# SETUP 26: TOPOGUN / QUAD DRAW RETOPO

**ID:** SETUP-26 | **Type:** Retopo | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Ручная ретопология для анимации. EN: Manual retopo for animation.

## 1. Шаги / Steps
1. Manual retopo
2. Edge flow
3. Shrinkwrap
4. Bake maps

## 2. MCP промпт / Prompt
```
RU: "Ретопо лица: loops вокруг глаз/рта, полюса 3/5, shrinkwrap 0.001" / EN: "Retopo face: loops around eyes/mouth, 3/5 poles, shrinkwrap 0.001"
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
