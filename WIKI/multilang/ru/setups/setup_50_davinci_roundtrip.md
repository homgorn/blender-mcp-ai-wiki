---
id: setup_50_davinci_roundtrip
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 50: DAVINCI RESOLVE ROUNDTRIP

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_50_davinci_roundtrip | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 50: DAVINCI RESOLVE ROUNDTRIP

**ID:** SETUP-50 | **Type:** Color/Edit | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Монтаж/грейдинг туда-обратно. EN: Edit/grade roundtrip.

## 1. Шаги / Steps
1. EDL/XML
2. ACES pipeline
3. CDL/LUT
4. Back to Blender

## 2. MCP промпт / Prompt
```
RU: "Экспорт EDL+EXR в Resolve, грейд ACES, верни LUT .cube в Blender" / EN: "Export EDL+EXR to Resolve, ACES grade, return .cube LUT to Blender"
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
