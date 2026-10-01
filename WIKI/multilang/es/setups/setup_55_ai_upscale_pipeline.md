---
id: setup_55_ai_upscale_pipeline
lang: es
orig_lang: ru
category: setups
type: setup
difficulty: 1
translation: template
---
# СЕТАП 55: AI UPSCALE PIPELINE

> Objetivo: 

**ID:** setup_55_ai_upscale_pipeline | **Lang:** es | **Orig:** ru | **Category:** setups | **Tags:** **

## Cómo usar
Esta es la versión en español de 'setup_55_ai_upscale_pipeline'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
setup_55_ai_upscale_pipeline / setups / **
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: setup_55_ai_upscale_pipeline
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 1
---

# СЕТАП 55: AI UPSCALE PIPELINE

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_55_ai_upscale_pipeline | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 55: AI UPSCALE PIPELINE

**ID:** SETUP-55 | **Type:** Upscale | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Апскейл рендеров. EN: Upscale renders.

## 1. Шаги / Steps
1. ESRGAN/Topaz
2. Sequence upscale
3. Denoise+sharpen
4. EXR safe

## 2. MCP промпт / Prompt
```
RU: "Topaz/ESRGAN 2x PNG sequence → denoise → sharpen 0.2, EXR untouched" / EN: "Topaz/ESRGAN 2x PNG seq → denoise → sharpen 0.2, keep EXR"
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
