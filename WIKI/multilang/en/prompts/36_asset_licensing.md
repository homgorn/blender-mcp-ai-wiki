---
id: 36_asset_licensing
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)

> Goal: ---

**ID:** 36_asset_licensing | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** cc, cc-by, licensing, poly, poly-pizza, polyhaven, sketchfab

## How to use
This page is the en version of '36_asset_licensing'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.

## MCP Prompt (copy-paste)
```
36_asset_licensing / prompts / cc, cc-by, licensing, poly, poly-pizza, polyhaven, sketchfab
```

> Note: code/paths stay in English for Blender/Python compatibility.

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
- **Промпты:** [P27 Poly Haven](./27_polyhaven_pipeline.md)
- **Следующий:** [P37: Seamless Textures](./37_seamless_textures.md)
