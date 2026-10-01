---
id: setup_52_git_lfs_blend
lang: es
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 52: GIT LFS + BLEND VERSIONING

> Objetivo: 

**ID:** setup_52_git_lfs_blend | **Lang:** es | **Orig:** ru | **Category:** setups | **Tags:** **

## Cómo usar
Esta es la versión en español de 'setup_52_git_lfs_blend'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
setup_52_git_lfs_blend / setups / **
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: setup_52_git_lfs_blend
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 52: GIT LFS + BLEND VERSIONING

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_52_git_lfs_blend | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 52: GIT LFS + BLEND VERSIONING

**ID:** SETUP-52 | **Type:** Versioning | **Difficulty:** ⭐⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Версионирование .blend. EN: .blend versioning.

## 1. Шаги / Steps
1. LFS track
2. Lock files
3. Blend diff
4. CI validate

## 2. MCP промпт / Prompt
```
RU: "Git LFS track *.blend/*.exr/*.fbx, lock мейн-сцены, CI рендер-превью" / EN: "Git LFS track blend/exr/fbx, lock mains, CI preview render"
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
