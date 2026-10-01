---
lang: ru
tags: [assets, lighting, modeling, pipeline, prompt]
---
# P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)

**ID:** P36 | **Кластер:** MCP Integration | **Сложность:** ⭐ | **Теги:** #licensing #poly-pizza #sketchfab #polyhaven #cc0 #cc-by

---

## 🎯 ЦЕЛЬ
Правильно фильтровать лицензии: CC0 без атрибуции, CC-BY с кредитом

---

## 📝 ПРОМПТ (РУС)

```
Ищи только [CC0/CC-BY] ассеты "[запрос]".
Для CC-BY: запиши автора в custom property и README сцены.
```

---

## 📝 ПРОМПТ (ENG)

```
Search only [CC0/CC-BY] assets "[query]".
For CC-BY: store author in custom property and scene README.
```

---

## 🔧 MCP

```json
{"type": "search_polypizza_models", "params": {"query": "chair", "licence": "CC0", "limit": 20}}
{"type": "search_sketchfab_models", "params": {"query": "table", "count": 20, "downloadable": true}}
```

```python
import bpy

def stamp_attribution(obj_name, author, source, licence):
    obj = bpy.data.objects.get(obj_name)
    obj["attribution_author"] = author
    obj["attribution_source"] = source
    obj["attribution_licence"] = licence
    return {"stamped": obj_name}
```

---

## 📊 ЛИЦЕНЗИИ
| Лицензия | Коммерция | Атрибуция |
|----------|-----------|-----------|
| CC0 | Да | Нет |
| CC-BY | Да | Да |
| CC-BY-SA | Да | Да, share-alike |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P27: POLY HAVEN ASSET PIPELINE](27_polyhaven_pipeline.md), [P13: LIGHTING & HDRI](13_lighting_hdri.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [P03: MODIFIERS STACK](03_modifiers_stack.md)
- **Теги:** #assets, #cc, #cc-by, #licensing, #lighting, #modeling, #pipeline, #poly, #poly-pizza, #polyhaven

