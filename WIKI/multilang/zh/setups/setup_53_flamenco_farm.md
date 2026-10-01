---
id: setup_53_flamenco_farm
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 53: FLAMENCO FARM CLUSTER

> 目标: 

**ID:** setup_53_flamenco_farm | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_53_flamenco_farm' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_53_flamenco_farm / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_53_flamenco_farm
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 53: FLAMENCO FARM CLUSTER

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_53_flamenco_farm | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 53: FLAMENCO FARM CLUSTER

**ID:** SETUP-53 | **Type:** Render Farm | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Ферма Flamenco. EN: Flamenco farm.

## 1. Шаги / Steps
1. Manager+workers
2. Shared storage
3. Job split
4. Monitor

## 2. MCP промпт / Prompt
```
RU: "Manager+3 workers, NFS storage, split 1-250 по 25 кадров, мониторинг" / EN: "Manager+3 workers, NFS, split 1-250 by 25, monitor"
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
