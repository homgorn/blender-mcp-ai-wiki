---
id: setup_16_automatic1111_api
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 16: BLENDER + AUTOMATIC1111 API

> Ziel: 

**ID:** setup_16_automatic1111_api | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_16_automatic1111_api'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_16_automatic1111_api / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_16_automatic1111_api
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 16: BLENDER + AUTOMATIC1111 API

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_16_automatic1111_api | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 16: BLENDER + AUTOMATIC1111 API

**ID:** SETUP-16 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: A1111 API как дешевый SD-бэкенд. EN: A1111 API as cheap SD backend.

## 1. Шаги / Steps
1. A1111 --api
2. img2img/inpaint
3. Blender image editor bridge
4. Batch queue

## 2. MCP промпт / Prompt
```
RU: "Через A1111 API: img2img strength 0.5, 30 steps, seamless tile" / EN: "Via A1111 API: img2img strength 0.5, 30 steps, seamless tiling"
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
