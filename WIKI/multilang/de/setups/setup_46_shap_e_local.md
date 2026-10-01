---
id: setup_46_shap_e_local
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 46: SHAP-E / POINT-E LOCAL

> Ziel: 

**ID:** setup_46_shap_e_local | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_46_shap_e_local'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_46_shap_e_local / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_46_shap_e_local
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 46: SHAP-E / POINT-E LOCAL

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_46_shap_e_local | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 46: SHAP-E / POINT-E LOCAL

**ID:** SETUP-46 | **Type:** Research Gen | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Исследовательская генерация. EN: Research generation.

## 1. Шаги / Steps
1. OpenAI Shap-E
2. Text-to-3D latent
3. Marching cubes
4. Cleanup

## 2. MCP промпт / Prompt
```
RU: "Shap-E: 'red chair' → latent → mesh, remesh, scale 1м" / EN: "Shap-E: 'red chair' → latent → mesh, remesh, scale 1m"
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
