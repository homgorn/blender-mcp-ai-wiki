---
id: setup_15_comfyui_sdxl
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 15: Blender + COMFYUI SDXL

> 目标: 

**ID:** setup_15_comfyui_sdxl | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_15_comfyui_sdxl' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_15_comfyui_sdxl / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_15_comfyui_sdxl
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 15: BLENDER + COMFYUI SDXL

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_15_comfyui_sdxl | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 15: BLENDER + COMFYUI SDXL

**ID:** SETUP-15 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 25-40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: ComfyUI как бэкенд генерации PBR. EN: ComfyUI as PBR backend.

## 1. Шаги / Steps
1. ComfyUI локально
2. SDXL base+refiner
3. ControlNet depth/canny
4. Blender texture nodes

## 2. MCP промпт / Prompt
```
RU: "Сгенерируй через ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth из viewport" / EN: "Generate via ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth from viewport"
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
