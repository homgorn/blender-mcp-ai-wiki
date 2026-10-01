---
lang: ru
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
- **Сетяпы:** [Setup 08](../setups/setup_08_asset_pipeline.md), [Setup 13 Unity](../setups/setup_13_unity_roundtrip.md)
- **Следующий:** [P40: Version Control](./40_version_control.md)
