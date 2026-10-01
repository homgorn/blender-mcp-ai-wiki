---
id: setup_24_metashape_scan
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 24: AGISOFT METASHAPE

> 目标: 

**ID:** setup_24_metashape_scan | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_24_metashape_scan' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_24_metashape_scan / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_24_metashape_scan
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 24: AGISOFT METASHAPE

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_24_metashape_scan | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 24: AGISOFT METASHAPE

**ID:** SETUP-24 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Metashape → Blender пайплайн. EN: Metashape → Blender pipeline.

## 1. Шаги / Steps
1. Align photos
2. Dense cloud
3. Mesh+texture
4. Scale bars

## 2. MCP промпт / Prompt
```
RU: "Импорт Metashape OBJ 8k текстурой, ретопо, UDIM, запеки AO/curvature" / EN: "Import Metashape OBJ 8k texture, retopo, UDIM, bake AO/curvature"
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
