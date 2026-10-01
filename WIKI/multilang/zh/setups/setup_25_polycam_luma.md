---
id: setup_25_polycam_luma
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 1
translation: template
---
# СЕТАП 25: POLYCAM / LUMA / KIRI SCAN

> 目标: 

**ID:** setup_25_polycam_luma | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_25_polycam_luma' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_25_polycam_luma / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_25_polycam_luma
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 1
---

# СЕТАП 25: POLYCAM / LUMA / KIRI SCAN

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_25_polycam_luma | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 25: POLYCAM / LUMA / KIRI SCAN

**ID:** SETUP-25 | **Type:** Mobile Scan | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мобильные сканы → Blender. EN: Mobile scans → Blender.

## 1. Шаги / Steps
1. NeRF/Gaussian splat
2. GLB export
3. Cleanup
4. Scale fix

## 2. MCP промпт / Prompt
```
RU: "Импорт Polycam GLB, почини масштаб x0.01, удали мусор, ретопо" / EN: "Import Polycam GLB, fix scale x0.01, cleanup, retopo"
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
