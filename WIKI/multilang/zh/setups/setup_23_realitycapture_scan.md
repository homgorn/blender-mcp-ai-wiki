---
id: setup_23_realitycapture_scan
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 23: REALITYCAPTURE SCAN TO Blender

> 目标: 

**ID:** setup_23_realitycapture_scan | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_23_realitycapture_scan' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_23_realitycapture_scan / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_23_realitycapture_scan
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 23: REALITYCAPTURE SCAN TO BLENDER

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_23_realitycapture_scan | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 23: REALITYCAPTURE SCAN TO BLENDER

**ID:** SETUP-23 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 40-60 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Фотограмметрия → game-ready. EN: Photogrammetry → game-ready.

## 1. Шаги / Steps
1. RC CLI
2. Laser+photo align
3. Decimate/retopo
4. PBR bake 8k

## 2. MCP промпт / Prompt
```
RU: "Импорт RC mesh 5M tris → Quad Remesher 20k → Smart UV → bake 8k→2k" / EN: "Import RC 5M mesh → Quad Remesher 20k → Smart UV → bake 8k→2k"
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
