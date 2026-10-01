---
id: setup_45_hunyuan3d_21
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 45: HUNYUAN3D 2.1 LOCAL

> Ziel: 

**ID:** setup_45_hunyuan3d_21 | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_45_hunyuan3d_21'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_45_hunyuan3d_21 / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_45_hunyuan3d_21
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 45: HUNYUAN3D 2.1 LOCAL

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_45_hunyuan3d_21 | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 45: HUNYUAN3D 2.1 LOCAL

**ID:** SETUP-45 | **Type:** Local 3D Gen | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Локальный Hunyuan3D. EN: Local Hunyuan3D.

## 1. Шаги / Steps
1. Hunyuan Docker
2. SD+3D pipeline
3. PBR export
4. VRAM 12GB+

## 2. MCP промпт / Prompt
```
RU: "Hunyuan3D Docker: text 'cozy cabin' → mesh + PBR 2k, импорт GLB" / EN: "Hunyuan3D Docker: 'cozy cabin' → mesh + 2k PBR, import GLB"
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
