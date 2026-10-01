---
id: setup_48_gaussian_splatting
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 48: GAUSSIAN SPLATTING → Blender

> 目标: 

**ID:** setup_48_gaussian_splatting | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_48_gaussian_splatting' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_48_gaussian_splatting / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_48_gaussian_splatting
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 48: GAUSSIAN SPLATTING → BLENDER

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_48_gaussian_splatting | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 48: GAUSSIAN SPLATTING → BLENDER

**ID:** SETUP-48 | **Type:** 3DGS | **Difficulty:** ⭐⭐⭐ | **Time:** 30 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Гауссианы в Blender. EN: Gaussians to Blender.

## 1. Шаги / Steps
1. 3DGS ply
2. Splat→mesh
3. Postshot/Luma
4. Blender import

## 2. MCP промпт / Prompt
```
RU: "Импорт .ply splat, конверт в mesh (SuGaR), запеки текстуру" / EN: "Import .ply splats, convert to mesh (SuGaR), bake texture"
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
