---
id: setup_14_godot_pipeline
lang: en
orig_lang: en
category: setups
type: setup
difficulty: 2
translation: template
---
# SETUP 14: BLENDER + GODOT PIPELINE

> Goal: ## 5. MCP
```
RU: "Экспортируй в GLB для Godot 4: apply transforms, запеки анимации, Draco off (Godot плохо читает), текстуры KTX2/Basis"
EN: "Export GLB for Godot 4: apply transforms, bake anims, Draco off, KTX2/Basis textures"
```

**ID:** setup_14_godot_pipeline | **Lang:** en | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 14: BLENDER + GODOT PIPELINE

**ID:** SETUP-14 | **Type:** Open-source Engine | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: glTF 2.0 как нативный мост Blender → Godot 4. EN: glTF 2.0 as native bridge Blender → Godot 4.

## 1. Экспорт / Export
```python
bpy.ops.export_scene.gltf(
 filepath="//exports/godot/prop.glb", export_format='GLB',
 use_selection=True, export_apply=True, export_yup=True,
 export_materials='EXPORT', export_image_format='AUTO',
 export_texcoords=True, export_normals=True, export_tangents=True,
 export_animations=True, export_frame_range=True, export_skins=True, export_morph=True
)
```

## 2. Материалы / Materials
| Blender Principled | Godot StandardMaterial3D |
|---|---|
| Base Color | Albedo |
| Metallic | Metallic |
| Roughness | Roughness |
| Normal | Normal Map (OpenGL ok) |
| Emission | Emission |
| Alpha | Transparency > Alpha |
RU: Godot понимает glTF PBR напрямую. EN: Godot reads glTF PBR directly.

## 3. Риг / Rig
- RU: Имена костей без пробелов, root at origin. EN: No spaces in bone names, root at origin.
- Godot: `AnimationPlayer` + `AnimationTree` from GLB animations.

## 4. LOD/Коллизии / LOD/Collision
- RU: Суффиксы `_LOD0/1`, коллизии `-col` / `UCX_`. Godot: MeshInstance LOD + `StaticBody3D+CollisionShape`.
- EN: Same.

## 5. MCP
```
RU: "Экспортируй в GLB для Godot 4: apply transforms, запеки анимации, Draco off (Godot плохо читает), текстуры KTX2/Basis"
EN: "Export GLB for Godot 4: apply transforms, bake anims, Draco off, KTX2/Basis textures"
```

## 🔗 Setup 08, WF-07, Case 02
