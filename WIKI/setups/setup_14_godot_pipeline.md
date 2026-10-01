---
id: setup_14_godot_pipeline
lang: ru
category: setups
status: full
tags: [blender, godot, pipeline, setup]
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

---

## FULL GUIDE

### glTF как нативный мост
- Export: apply transforms, Y-up, tangents, animations, skins, morphs.
- Draco OFF (Godot плохо читает), текстуры KTX2/Basis.

### Риг
- Имена костей без пробелов, root в origin. AnimationPlayer + AnimationTree из GLB.

### Проверка
- [ ] GLB открывается в Godot без ошибок
- [ ] Анимации в списке, LOD-суффиксы на месте

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P39: EXPORT PRESETS (GLB/FBX/USD)](../prompts/39_export_presets.md), [P46: UDIM WORKFLOW](../prompts/46_udim_workflow.md)
- **Теги:** #blender, #godot, #pipeline, #setup

