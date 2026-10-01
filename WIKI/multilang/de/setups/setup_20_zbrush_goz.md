---
id: setup_20_zbrush_goz
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 20: ZBRUSH GOZ BRIDGE

> Ziel: 

**ID:** setup_20_zbrush_goz | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_20_zbrush_goz'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_20_zbrush_goz / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_20_zbrush_goz
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 20: ZBRUSH GOZ BRIDGE

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_20_zbrush_goz | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

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
