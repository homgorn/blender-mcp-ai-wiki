---
lang: en
tags: [pipeline, prompt]
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

- **Прочие в категории «Промпты»:** [P46: UDIM WORKFLOW](46_udim_workflow.md), [P12: TEXTURE PAINTING](12_texture_painting.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P27: POLY HAVEN ASSET PIPELINE](27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](36_asset_licensing.md)
- **По темам:** [P39: EXPORT PRESETS (GLB/FBX/USD)](39_export_presets.md), [P47: ALEMBIC CACHE PIPELINE](47_alembic_cache.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md)
- **Теги:** #ao, #baking, #cage, #curvature, #normal, #pipeline, #prompt

