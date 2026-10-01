---
id: setup_47_zero123_instantmesh
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 47: ZERO123 / INSTANTMESH

> Ziel: 

**ID:** setup_47_zero123_instantmesh | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_47_zero123_instantmesh'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_47_zero123_instantmesh / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_47_zero123_instantmesh
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 47: ZERO123 / INSTANTMESH

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_47_zero123_instantmesh | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 47: ZERO123 / INSTANTMESH

**ID:** SETUP-47 | **Type:** Multi-view 3D | **Difficulty:** ⭐⭐⭐ | **Time:** 30 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мультивью реконструкция. EN: Multi-view reconstruction.

## 1. Шаги / Steps
1. Zero123++ views
2. InstantMesh LRM
3. NeRF→mesh
4. Texture refine

## 2. MCP промпт / Prompt
```
RU: "Zero123++: 6 views из 1 фото → InstantMesh → textured mesh" / EN: "Zero123++: 6 views from 1 photo → InstantMesh → textured mesh"
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
