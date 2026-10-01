---
id: setup_18_substance_painter_live
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 18: SUBSTANCE PAINTER LIVE-LINK

> 目标: 

**ID:** setup_18_substance_painter_live | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_18_substance_painter_live' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_18_substance_painter_live / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_18_substance_painter_live
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 18: SUBSTANCE PAINTER LIVE-LINK

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_18_substance_painter_live | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 18: SUBSTANCE PAINTER LIVE-LINK

**ID:** SETUP-18 | **Type:** Texturing Pro | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Substance → Blender живой линк. EN: Substance → Blender live link.

## 1. Шаги / Steps
1. FBX/GLTF roundtrip
2. UDIM workflow
3. Smart materials
4. Live link plugin

## 2. MCP промпт / Prompt
```
RU: "Экспорт FBX с UDIM в Substance, запеки ID/curvature/AO, верни PBR 4k в Blender" / EN: "Export FBX with UDIM to Substance, bake ID/curvature/AO, return 4k PBR to Blender"
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
