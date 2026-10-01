---
id: setup_39_quixel_bridge
lang: ru
category: setups
status: stub
tags: [assets, setup]
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

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 37: BLENDERKIT ASSETS](setup_37_blenderkit_assets.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 40: AMBIENTCG + POLYHAVEN BATCH](setup_40_ambientcg_polyhaven.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](../prompts/36_asset_licensing.md)
- **Теги:** #assets, #setup

