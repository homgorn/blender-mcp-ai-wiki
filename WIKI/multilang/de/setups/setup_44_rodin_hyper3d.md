---
id: setup_44_rodin_hyper3d
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 44: RODIN / HYPER3D GEN

> Ziel: 

**ID:** setup_44_rodin_hyper3d | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_44_rodin_hyper3d'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_44_rodin_hyper3d / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_44_rodin_hyper3d
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 44: RODIN / HYPER3D GEN

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_44_rodin_hyper3d | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 44: RODIN / HYPER3D GEN

**ID:** SETUP-44 | **Type:** Image-to-3D | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Rodin генерация. EN: Rodin generation.

## 1. Шаги / Steps
1. Rodin Gen-1
2. Multi-view
3. PBR bake
4. Blender cleanup

## 2. MCP промпт / Prompt
```
RU: "Rodin: front+side фото → 3D, decimate 15k, Smart UV, bake normal" / EN: "Rodin: front+side photos → 3D, decimate 15k, Smart UV, bake normal"
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
