---
lang: ru
tags: [assets, pipeline, prompt]
---
# P27: POLY HAVEN ASSET PIPELINE

**ID:** P27 | **Кластер:** MCP Integration | **Сложность:** ⭐ | **Теги:** #polyhaven #assets #hdri #textures #models #mcp

---

## 🎯 ЦЕЛЬ
Поиск → скачивание → применение Poly Haven ассетов через MCP

---

## 📝 ПРОМПТ (РУС)

```
Найди на Poly Haven [тип: models/hdris/textures] "[запрос]",
скачай [ID] [resolution] и [примени/поставь world]
```

---

## 📝 ПРОМПТ (ENG)

```
Find on Poly Haven [type] "[query]", download [ID] [resolution] and [apply/set world]
```

---

## 🔧 MCP TOOLS

```json
// Поиск
{"type": "search_polyhaven_assets", "params": {"asset_type": "hdris", "categories": "studio"}}
// Скачивание HDRI
{"type": "download_polyhaven_asset", "params": {"asset_id": "studio_small_01", "asset_type": "hdris", "resolution": "2k"}}
// Скачивание текстуры + применение
{"type": "download_polyhaven_asset", "params": {"asset_id": "brick_wall_01", "asset_type": "textures", "resolution": "2k"}}
{"type": "set_texture", "params": {"object_name": "Wall", "texture_id": "brick_wall_01"}}
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](36_asset_licensing.md), [P13: LIGHTING & HDRI](13_lighting_hdri.md), [P11: PROCEDURAL TEXTURES](11_procedural_textures.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](26_mcp_basics.md)
- **По темам:** [P28: CUSTOM MCP TOOLS DEVELOPMENT](28_custom_mcp_tools.md), [P35: MCP ERROR RECOVERY](35_mcp_error_recovery.md), [P38: HIGH→LOW BAKE PIPELINE](38_bake_pipeline.md)
- **Теги:** #assets, #hdri, #mcp, #models, #pipeline, #polyhaven, #prompt, #textures

