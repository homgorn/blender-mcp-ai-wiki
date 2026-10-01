---
id: setup_60_shotgrid_ftrack_sync
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 60: SHOTGRID / FTRACK SYNC

> 目标: 

**ID:** setup_60_shotgrid_ftrack_sync | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_60_shotgrid_ftrack_sync' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_60_shotgrid_ftrack_sync / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_60_shotgrid_ftrack_sync
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 60: SHOTGRID / FTRACK SYNC

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_60_shotgrid_ftrack_sync | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 60: SHOTGRID / FTRACK SYNC

**ID:** SETUP-60 | **Type:** Production | **Difficulty:** ⭐⭐⭐ | **Time:** 35 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Продакшн-трекинг. EN: Production tracking.

## 1. Шаги / Steps
1. Shot entities
2. Version publish
3. Review notes
4. Status sync

## 2. MCP промпт / Prompt
```
RU: "ShotGrid: shot/tasks/versions, publish EXR+MP4, review notes → Blender markers" / EN: "ShotGrid: shots/tasks/versions, publish EXR+MP4, notes → Blender markers"
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
