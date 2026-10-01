---
lang: ru
tags: [pipeline, prompt, usd, web]
---
# P39: EXPORT PRESETS (GLB/FBX/USD)

**ID:** P39 | **Кластер:** Pipeline | **Сложность:** ⭐⭐ | **Теги:** #export #gltf #fbx #usd #unity #unreal #godot

---

## 🎯 ЦЕЛЬ
Экспорт-пресеты под движки: GLB (Godot/Web), FBX (Unity/Unreal), USD (pipeline)

---

## 📝 ПРОМПТ (РУС)

```
Экспортируй "[OBJECTS]" в [GLB/FBX/USD] пресет [Godot/Unity/Unreal/Pipeline]
в //exports/. Проверь масштаб и forward/up.
```

---

## 📝 ПРОМПТ (ENG)

```
Export "[OBJECTS]" to [GLB/FBX/USD] preset [Godot/Unity/Unreal/Pipeline]
to //exports/. Verify scale and forward/up.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def export_preset(objects, fmt='GLB', target='Godot', outdir="//exports/"):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        bpy.data.objects.get(o).select_set(True)
    if fmt == 'GLB':
        bpy.ops.export_scene.gltf(
            filepath=f"{outdir}{objects[0]}.glb", export_format='GLB',
            use_selection=True, export_apply=True, export_yup=True,
            export_materials='EXPORT', export_animations=True)
    elif fmt == 'FBX':
        bpy.ops.export_scene.fbx(
            filepath=f"{outdir}{objects[0]}.fbx", use_selection=True,
            apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
            bake_space_transform=(target == 'Unity'),
            object_types={'ARMATURE', 'MESH'},
            primary_bone_axis='Y_FORWARD', secondary_bone_axis='X_UP',
            bake_anim=True, bake_anim_use_nla_strips=True)
    elif fmt == 'USD':
        bpy.ops.wm.usd_export(
            filepath=f"{outdir}{objects[0]}.usda",
            selected_objects_only=True, export_materials=True,
            material_x=True, export_animation=True)
    return {"exported": fmt, "target": target}
```

---

## 📊 ПРЕСЕТЫ
| Target | Format | Scale |
|--------|--------|-------|
| Godot/Web | GLB | Meters, applied |
| Unity | FBX | Meters, applied, bake transform |
| Unreal | FBX | cm via unit scale |
| Pipeline | USD + MaterialX | Meters |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P22: PARTICLE SYSTEMS](22_particles.md), [P27: POLY HAVEN ASSET PIPELINE](27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](36_asset_licensing.md), [P38: HIGH→LOW BAKE PIPELINE](38_bake_pipeline.md), [P44: MOCAP RETARGETING](44_mocap_retarget.md)
- **По темам:** [CASE 07: STYLIZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md), [INTEGRATIONS: COMFYUI, UNREAL, USD, TOUCHDESIGNER](../integrations/comfyui_unreal_usd.md), [P46: UDIM WORKFLOW](46_udim_workflow.md)
- **Теги:** #export, #fbx, #gltf, #godot, #pipeline, #prompt, #unity, #unreal, #usd, #web

