---
id: 27_polyhaven_pipeline
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P27: POLY HAVEN ASSET 管线

> 目标: ---

**ID:** 27_polyhaven_pipeline | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** assets, hdri, mcp, models, polyhaven, textures

## 使用方法
这是 '27_polyhaven_pipeline' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
27_polyhaven_pipeline / prompts / assets, hdri, mcp, models, polyhaven, textures
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

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
