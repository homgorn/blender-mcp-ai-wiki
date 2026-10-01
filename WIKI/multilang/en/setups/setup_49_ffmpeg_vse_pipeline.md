---
id: setup_49_ffmpeg_vse_pipeline
lang: en
orig_lang: en
category: setups
type: setup
difficulty: 2
translation: template
---
# SETUP 49: FFMPEG + VSE PIPELINE

> Goal: ## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

**ID:** setup_49_ffmpeg_vse_pipeline | **Lang:** en | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 49: FFMPEG + VSE PIPELINE

**ID:** SETUP-49 | **Type:** Video | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Монтаж+кодирование. EN: Edit+encode.

## 1. Шаги / Steps
1. VSE strips
2. Proxy 25%
3. FFmpeg encode
4. HDR metadata

## 2. MCP промпт / Prompt
```
RU: "VSE: 3 strips + crossfade + text, proxy 25%, FFmpeg H264 CRF18 + ProRes master" / EN: "VSE: 3 strips + cross + text, 25% proxy, FFmpeg H264 CRF18 + ProRes"
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
