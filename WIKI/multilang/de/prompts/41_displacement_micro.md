---
id: 41_displacement_micro
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P41: DISPLACEMENT & MICRO-DETAIL

> Ziel: ---

**ID:** 41_displacement_micro | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** adaptive, adaptive-subdivision, cycles, displacement, micro, micro-detail, true, true-displacement

## Verwendung
Dies ist die deutsche Version von '41_displacement_micro'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
41_displacement_micro / prompts / adaptive, adaptive-subdivision, cycles, displacement, micro, micro-detail, true, true-displacement
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P41: DISPLACEMENT & MICRO-DETAIL

**ID:** P41 | **Кластер:** Materials/Render | **Сложность:** ⭐⭐⭐ | **Теги:** #displacement #adaptive-subdivision #micro-detail #true-displacement #cycles

---

## 🎯 ЦЕЛЬ
Настоящий дисплейсмент: Adaptive Subdivision + 32-bit height + правильные настройки Cycles

---

## 📝 ПРОМПТ (РУС)

```
Настрой true displacement для "[OBJECT]":
Height map [путь], scale [S], midlevel [M].
Adaptive Subdivision: dicing rate [R]. Проверь силуэт на крупном плане.
```

---

## 📝 ПРОМПТ (ENG)

```
Setup true displacement for "[OBJECT]":
Height map [path], scale [S], midlevel [M].
Adaptive Subdivision: dicing rate [R]. Verify silhouette in close-up.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def true_displacement(obj_name, height_img_path, scale=0.1, midlevel=0.5, dicing=1.0):
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != 'MESH':
        raise ValueError("Mesh object required")
    mat = obj.active_material
    if not mat:
        raise ValueError("Object has no material")
    mat.cycles.displacement_method = 'BOTH'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(height_img_path)
    tex.image.colorspace_settings.name = 'Non-Color'
    tex.location = (-400, -300)
    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (-100, -300)
    disp.inputs['Scale'].default_value = scale
    disp.inputs['Midlevel'].default_value = midlevel
    out = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    links.new(tex.outputs['Color'], disp.inputs['Height'])
    links.new(disp.outputs['Displacement'], out.inputs['Displacement'])
    sub = obj.modifiers.new("AdaptiveSubdiv", 'SUBSURF')
    sub.subdivision_type = 'CATMULL_CLARK'
    sub.use_adaptive_subdiv = True
    s = bpy.context.scene
    s.cycles.feature_set = 'EXPERIMENTAL'
    s.cycles.preview_dicing_rate = dicing
    s.cycles.dicing_rate = max(0.5, dicing / 2)
    return {"displacement": True, "scale": scale}

# true_displacement("Ground", "//textures/ground_height_4k.exr", scale=0.15)
```

---

## 📊 ПАРАМЕТРЫ
| Параметр | Значение | Зачем |
|----------|----------|-------|
| Height map | 32-bit EXR | Без бандинга на плавных склонах |
| Scale | 0.05–0.3 | Реальная высота рельефа в метрах |
| Midlevel | 0.5 | Точка «ноль» (ниже — впадины, выше — выступы) |
| Dicing rate | 1.0 preview / 0.5 render | Детализация сабдива |
| Feature set | EXPERIMENTAL | Обязателен для adaptive |

---

## ⚠️ ОШИБКИ
| Ошибка | Решение |
|--------|---------|
| Плоский силуэт | Displacement method = Both/True, а не Bump Only |
| Взрыв геометрии | Scale слишком большой; проверь единицы midlevel |
| Шум/артефакты | Height в Non-Color, 32-bit, dicing меньше |

---

## 🔗 СВЯЗИ
- **Промпты:** [P11 Procedural](./11_procedural_textures.md), [P38 Bake](./38_bake_pipeline.md)
- **Следующий:** [P42: Portals & Caustics](./42_portals_caustics.md)
