---
id: setup_54_cloud_render_aws
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 54: CLOUD RENDER AWS/GCP

> Цель: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_54_cloud_render_aws | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 54: CLOUD RENDER AWS/GCP

**ID:** SETUP-54 | **Type:** Cloud | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Облачный рендер. EN: Cloud render.

## 1. Шаги / Steps
1. Spot instances
2. Docker Blender
3. S3 sync
4. Cost cap

## 2. MCP промпт / Prompt
```
RU: "AWS Spot g5.xlarge Docker Blender, S3 sync, budget cap $20" / EN: "AWS Spot g5 Docker Blender, S3 sync, $20 cap"
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
