---
id: 32_light_linking
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P32: LIGHT LINKING & SHADOWS

> Ziel: ---

**ID:** 32_light_linking | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** collections, cycles, eevee, light, light-linking, shadows

## Verwendung
Dies ist die deutsche Version von '32_light_linking'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
32_light_linking / prompts / collections, cycles, eevee, light, light-linking, shadows
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P32: LIGHT LINKING & SHADOWS

**ID:** P32 | **Кластер:** Lighting | **Сложность:** ⭐⭐ | **Теги:** #light-linking #shadows #collections #cycles #eevee

---

## 🎯 ЦЕЛЬ
Управлять какие объекты освещает каждый свет; настроить тени без артефактов

---

## 📝 ПРОМПТ (РУС)

```
Настрой light linking: свет "[LIGHT]" влияет только на коллекцию "[COLL]".
Тени: soft size [R], bias авто, contact shadows для EEVEE.
```

---

## 📝 ПРОМПТ (ENG)

```
Setup light linking: light "[LIGHT]" affects only collection "[COLL]".
Shadows: soft size [R], auto bias, contact shadows for EEVEE.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def tune_shadows(light_name, soft_size=0.5, clip_start=0.1, clip_end=100.0):
    light = bpy.data.objects.get(light_name)
    if not light:
        raise ValueError("Light not found")
    ld = light.data
    if hasattr(ld, 'shadow_soft_size'):
        ld.shadow_soft_size = soft_size
    ld.shadow_buffer_clip_start = clip_start
    ld.shadow_buffer_clip_end = clip_end
    return {"shadows": "tuned", "light": light_name}
```

---

## ⚠️ ОШИБКИ
| Ошибка | Решение |
|--------|---------|
| Свет влияет на всё | Проверь коллекцию получателей, исключи фон (Light Linking, Blender 4.x) |
| Полосы/акне на тенях | Увеличь bias, уменьши clip_end |

---

## 🔗 СВЯЗИ
- **Промпты:** [P13 Lighting](./13_lighting_hdri.md), [P31 Passes](./31_render_passes_aov.md)
- **Следующий:** [P33: Camera Path](./33_camera_path.md)
