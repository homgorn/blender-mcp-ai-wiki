---
id: setup_53_flamenco_farm
lang: ru
category: setups
status: stub
tags: [render-farm, setup]
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

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P29: BATCH PROCESSING & CLI](../prompts/29_batch_cli.md), [P47: ALEMBIC CACHE PIPELINE](../prompts/47_alembic_cache.md), [P49: RENDER FARM SUBMIT](../prompts/49_farm_submit.md)
- **Теги:** #render-farm, #setup

