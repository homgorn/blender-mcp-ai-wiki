---
id: setup_22_rizomuv_bridge
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 22: RIZOMUV BRIDGE

> 目标: 

**ID:** setup_22_rizomuv_bridge | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_22_rizomuv_bridge' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_22_rizomuv_bridge / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_22_rizomuv_bridge
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 22: RIZOMUV BRIDGE

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_22_rizomuv_bridge | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 22: RIZOMUV BRIDGE

**ID:** SETUP-22 | **Type:** UV Pro | **Difficulty:** ⭐⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Идеальная развертка через RizomUV. EN: Perfect unwrap via RizomUV.

## 1. Шаги / Steps
1. FBX roundtrip
2. Auto seams
3. Pack islands
4. UDIM tiles

## 2. MCP промпт / Prompt
```
RU: "Экспорт в RizomUV, auto seams by angle 70°, pack margin 4px, верни UV" / EN: "Export to RizomUV, auto seams 70°, pack 4px, return UVs"
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
