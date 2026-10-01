---
id: setup_34_metahuman_blender
lang: ru
category: setups
status: stub
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

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX
