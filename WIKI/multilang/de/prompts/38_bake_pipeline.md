---
id: 38_bake_pipeline
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P38: HIGH→LOW BAKE PIPELINE

> Ziel: ---

**ID:** 38_bake_pipeline | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** ao, baking, cage, curvature, normal

## Verwendung
Dies ist die deutsche Version von '38_bake_pipeline'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
38_bake_pipeline / prompts / ao, baking, cage, curvature, normal
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P38: HIGH→LOW BAKE PIPELINE

**ID:** P38 | **Кластер:** Materials | **Сложность:** ⭐⭐⭐ | **Теги:** #baking #normal #ao #curvature #cage

---

## 🎯 ЦЕЛЬ
Запечь карты с high-poly на low-poly: normal/AO/curvature + Cage

---

## 📝 ПРОМПТ (РУС)

```
Запеки с "[HIGH]" на "[LOW]": [normal, AO, curvature],
Cage [dist], margin [px], resolution [res]. Выведи в //bakes/.
```

---

## 📝 ПРОМПТ (ENG)

```
Bake from "[HIGH]" to "[LOW]": [normal, AO, curvature],
Cage [dist], margin [px], resolution [res]. Output to //bakes/.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def bake_maps(high_name, low_name, out_dir="//bakes/", res=2048, margin=16, cage=0.02):
    high = bpy.data.objects.get(high_name)
    low = bpy.data.objects.get(low_name)
    if not high or not low:
        raise ValueError("Objects not found")
    bpy.ops.object.select_all(action='DESELECT')
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.render.bake.use_selected_to_active = True
    s.render.bake.cage_extrusion = cage
    s.render.bake.margin = margin
    for bake_type, suffix in [('NORMAL', 'normal'), ('AO', 'ao')]:
        img = bpy.data.images.new(f"{low_name}_{suffix}", res, res)
        mat = low.active_material
        tn = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tn.image = img
        tn.select = True
        mat.node_tree.nodes.active = tn
        bpy.ops.object.bake(type=bake_type, use_selected_to_active=True)
        img.filepath_raw = f"{out_dir}{low_name}_{suffix}.png"
        img.file_format = 'PNG'
        img.save()
        mat.node_tree.nodes.remove(tn)
    return {"baked": [high_name, low_name]}
```

---

## 🔗 СВЯЗИ
- **Промпты:** [P05 UV](./05_uv_unwrapping.md), [P06 Retopo](./06_retopology_workflow.md)
- **Следующий:** [P39: Export Presets](./39_export_presets.md)
