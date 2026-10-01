---
id: 27_polyhaven_pipeline
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P27: POLY HAVEN ASSET PIPELINE

> Goal: ---

**ID:** 27_polyhaven_pipeline | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** assets, hdri, mcp, models, polyhaven, textures

## How to use
This page is the en version of '27_polyhaven_pipeline'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.

## MCP Prompt (copy-paste)
```
27_polyhaven_pipeline / prompts / assets, hdri, mcp, models, polyhaven, textures
```

> Note: code/paths stay in English for Blender/Python compatibility.

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
- **Промпты:** [P13 Lighting](./13_lighting_hdri.md)
- **Следующий:** [P28: Custom MCP Tools](./28_custom_mcp_tools.md)
