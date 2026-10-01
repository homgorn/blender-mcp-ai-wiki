---
id: setup_38_fab_epic
lang: ru
category: setups
status: stub
tags: [assets, pipeline, setup]
---
# SETUP 38: FAB.COM (EPIC) PIPELINE

**ID:** SETUP-38 | **Type:** Marketplace | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Fab/Quixel в Blender. EN: Fab/Quixel to Blender.

## 1. Шаги / Steps
1. Fab library
2. Quixel Megascans
3. Sketchfab migrate
4. Unreal+Blender

## 2. MCP промпт / Prompt
```
RU: "Fab: 3 Megascans surfaces 8k + 2 3D plants, bridge to Blender, UDIM" / EN: "Fab: 3 Megascans 8k surfaces + 2 plants, bridge to Blender, UDIM"
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

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 37: BLENDERKIT ASSETS](setup_37_blenderkit_assets.md), [SETUP 39: QUIXEL BRIDGE STANDALONE](setup_39_quixel_bridge.md), [SETUP 40: AMBIENTCG + POLYHAVEN BATCH](setup_40_ambientcg_polyhaven.md)
- **По темам:** [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](../prompts/36_asset_licensing.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md)
- **Теги:** #assets, #pipeline, #setup

