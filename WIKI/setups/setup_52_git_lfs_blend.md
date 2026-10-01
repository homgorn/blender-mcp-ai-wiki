---
id: setup_52_git_lfs_blend
lang: ru
category: setups
status: stub
tags: [setup, version-control]
---
# SETUP 52: GIT LFS + BLEND VERSIONING

**ID:** SETUP-52 | **Type:** Versioning | **Difficulty:** ⭐⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Версионирование .blend. EN: .blend versioning.

## 1. Шаги / Steps
1. LFS track
2. Lock files
3. Blend diff
4. CI validate

## 2. MCP промпт / Prompt
```
RU: "Git LFS track *.blend/*.exr/*.fbx, lock мейн-сцены, CI рендер-превью" / EN: "Git LFS track blend/exr/fbx, lock mains, CI preview render"
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

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **Теги:** #setup, #version-control

