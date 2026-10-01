---
id: setup_13_unity_roundtrip
lang: ru
category: setups
status: full
tags: [blender, setup, unity]
---
# SETUP 13: BLENDER + UNITY ROUNDTRIP

**ID:** SETUP-13 | **Type:** Game Engine | **Difficulty:** ⭐⭐ | **Time:** 20-30 min
**RU/EN:** Двуязычный файл / Bilingual

---

## 🎯 ЦЕЛЬ / GOAL
**RU:** Бесшовный обмен Blender ↔ Unity: FBX, префабы, материалы URP/HDRP, анимации, LOD.
**EN:** Seamless Blender ↔ Unity exchange: FBX, prefabs, URP/HDRP materials, animations, LOD.

## 1. Масштаб / Scale
**RU:** Blender метры, Unity метры. Всегда Apply Scale перед экспортом.
**EN:** Blender meters, Unity meters. Always Apply Scale before export.
```python
import bpy
for o in bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
```

## 2. FBX Export (Unity preset)
```python
bpy.ops.export_scene.fbx(
  filepath="//exports/unity/prop.fbx",
  use_selection=True,
  apply_unit_scale=True,
  apply_scale_options='FBX_SCALE_ALL',
  bake_space_transform=False,  # Unity: Y-up, -Z forward handled by Unity
  object_types={'ARMATURE','MESH'},
  use_armature_deform_only=True,
  add_leaf_bones=False,
  primary_bone_axis='Y_FORWARD', secondary_bone_axis='X_UP',
  bake_anim=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=False
)
```

## 3. URP/HDRP материалы / Materials
| Blender | Unity URP Lit | Unity HDRP Lit |
|---|---|---|
| Base Color | Base Map (sRGB) | Base Color Map |
| Metallic | Metallic Map (R) | Mask Map R |
| Roughness | Smoothness (1-R) via Mask A | Mask Map G (or Smoothness remap) |
| Normal (OpenGL) | Normal Map (flip Y) | Normal Map (flip Y) |
| AO | Occlusion Map (G) | Mask Map G / AO |
| Emission | Emission Map + Color | Emissive Map |

**RU:** Для Unity инвертируй Y нормалей если артефакты. **EN:** Flip Y of normals if artifacts.
```python
# Проверка / Check
# Unity: Texture Type = Normal Map, Flip Y = true если из Blender OpenGL
```

## 4. LOD + Colliders
```python
# LOD: Blender Decimate → Unity LOD Group автоматически по суффиксам _LOD0/1/2
# Коллайдеры / Colliders: объекты с префиксом UCX_ / UBX_ / USP_
```

## 5. MCP команды / MCP prompts
```
RU: "Экспортируй выбранные объекты в FBX для Unity URP: apply scale, запеки NLA, LOD суффиксы, текстуры 2k в //exports/unity/"
EN: "Export selected to FBX for Unity URP: apply scale, bake NLA, LOD suffixes, 2k textures to //exports/unity/"
```

## 6. Чек-лист / Checklist
- [ ] Scale applied, rotation 0
- [ ] Forward Y, Up Z
- [ ] Normals outward, no non-manifold
- [ ] UV0 + UV2 (lightmap)
- [ ] Textures: BaseColor sRGB, others Non-Color

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #setup, #unity

