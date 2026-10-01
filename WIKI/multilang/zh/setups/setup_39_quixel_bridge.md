---
id: setup_39_quixel_bridge
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 39: QUIXEL BRIDGE STANDALONE

> 目标: 

**ID:** setup_39_quixel_bridge | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_39_quixel_bridge' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_39_quixel_bridge / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_39_quixel_bridge
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 39: QUIXEL BRIDGE STANDALONE

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_39_quixel_bridge | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 39: QUIXEL BRIDGE STANDALONE

**ID:** SETUP-39 | **Type:** Megascans | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Quixel Bridge экспорт. EN: Quixel Bridge export.

## 1. Шаги / Steps
1. Bridge export
2. LOD + maps
3. Calibrated PBR
4. Blender plugin

## 2. MCP промпт / Prompt
```
RU: "Bridge export: love2d, 4k, LOD0-2, metallic/roughness/normal/AO/displacement" / EN: "Bridge export: 4k, LOD0-2, metal/rough/normal/AO/displace"
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
