---
id: setup_20_zbrush_goz
lang: en
orig_lang: en
category: setups
type: setup
difficulty: 2
translation: template
---
# SETUP 20: ZBRUSH GOZ BRIDGE

> Goal: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_20_zbrush_goz | **Lang:** en | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 20: ZBRUSH GOZ BRIDGE

**ID:** SETUP-20 | **Type:** Sculpt | **Difficulty:** ⭐⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мост ZBrush ↔ Blender через GoZ. EN: ZBrush ↔ Blender via GoZ.

## 1. Шаги / Steps
1. GoZ button
2. Polypaint → vertex color
3. Displacement export
4. Retopo flow

## 2. MCP промпт / Prompt
```
RU: "GoZ экспорт high-poly, полипейнт в vertex color, displacement 32-bit EXR" / EN: "GoZ export high-poly, polypaint to vertex color, 32-bit EXR displacement"
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
