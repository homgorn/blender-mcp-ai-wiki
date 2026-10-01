---
id: setup_13_unity_roundtrip
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 13: Blender + UNITY ROUNDTRIP

> 目标: 

**ID:** setup_13_unity_roundtrip | **Lang:** zh | **Orig:** ru | **Category:** setups | **Tags:** **

## 使用方法
这是 'setup_13_unity_roundtrip' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
setup_13_unity_roundtrip / setups / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: setup_13_unity_roundtrip
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 13: BLENDER + UNITY ROUNDTRIP

> Цель: ## 6. Чек-лист / Checklist
- [ ] Scale applied, rotation 0
- [ ] Forward Y, Up Z
- [ ] Normals outward, no non-manifold
- [ ] UV0 + UV2 (lightmap)
- [ ] Textures: BaseColor sRGB, others Non-Color

**ID:** setup_13_unity_roundtrip | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

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

## 🔗 Связи / Links
Setup 08 Asset Pipeline, Setup 01 blender-mcp, WF-07 Game Asset Pipeline, Case 02
