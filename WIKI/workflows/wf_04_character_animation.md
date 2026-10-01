---
id: wf_04_character_animation
lang: ru
category: workflows
status: full
---
# WF 04: CHARACTER ANIMATION

**ID:** WF-04 | **Type:** Character Pipeline | **Difficulty:** ⭐⭐⭐ | **Time:** 2-6 hours

---

## 🎯 ЦЕЛЬ
Полный пайплайн анимации персонажа: от риггинга до экспорта в игровые движки

---

## 📋 ПАЙПЛАЙН СТАДИИ

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   BASE      │───▶│  RETOPO     │───▶│  UV &       │───▶│  RIGGING    │───▶│  SKINNING   │───▶│  ANIMATION  │
│   MESH      │    │  (Game-ready)│    │  TEXTURE    │    │  (Rigify/   │    │  (Weights)  │    │  (Cycles/   │
│  (Sculpt)   │    │             │    │             │    │  Custom)    │    │             │    │  NLA)       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  EXPORT     │◀───│  BATCH      │◀───│  RENDER/    │◀───│  POLISH     │◀───│  ANIMATION  │
│  (FBX/GLTF/ │    │  EXPORT     │    │  PREVIEW    │    │  (Cleanup)  │    │  LIBRARY    │
│  USDZ/Alembic)    (CI/CD)      │    │             │    │             │    │  (NLA)      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🔧 MCP КОМАНДЫ ПО СТАДИЯМ

### СТАДИЯ 1: BASE MESH (Скульптинг)
```bash
# Базовые пропорции (8 голов)
"Создай базовый меш персонажа: голова, торс, бедра, конечности
Dyntopo: constant_detail=8, symmetry X
Пропорции: рост=1.8м, голова=1/8, плечи=2 головы, талия=1.5 головы"

# Детализация
"Dyntopo sculpting: анатомия мышц, руки/ноги, лицо
Детали: пальцы, ногти, зубы, глаза, волосы (базовые)"
```

### СТАДИЯ 2: РЕТОПОЛОГИЯ (Game-ready ~15k tris)
```bash
# Quad Remesher
"Quad Remesher: target_quads=5000, adaptivity=0.3, smoothness=1.0
Проверить: только квады, нет полюсов >5, edge flow по анатомии"

# Ручная ретопо (для лица/рук)
"Ручная ретопология критических зон: лицо (edge flow по мимике),
руки (edge flow по суставам), область таза/плеч"
```

### СТАДИЯ 3: UV & ТЕКСТУРИРОВАНИЕ
```bash
# UDIM Layout (4 тайла для 4k текстур)
"UDIM Layout:
1001: Head/Neck (4k)
1002: Torso/Arms (2k)
1003: Legs (2k)
1004: Hands/Feet/Details (2k)

# Texture Paint слои
"BaseColor, Roughness, Normal, Subsurface, Specular, Displacement, Alpha"
```

### СТАДИЯ 4: RIGGING (Rigify + Custom)
```bash
# Meta-Rig
"Add Armature → Human (Meta-Rig)
Масштабировать под меш: Match to Mesh
Generate Rig → Rigify

# Дополнительные кости
"Face Rig: 50+ костей (jaw, eyes, brows, lips, cheeks, tongue)
Fingers: полная иерархия (3 фаланги на палец)
Twist bones: forearm (2), upper arm (2), thigh (2), calf (2)
Corrective shapes: knees, elbows, shoulders, hips"
```

### СТАДИЯ 5: SKINNING
```bash
# Автоматические веса + чистка
"Parent Mesh → Rig (Automatic Weights)
Weight Paint cleanup:
- Head: жесткая привязка к skull/spine
- Shoulders: градиент clavicle/upperarm/deltoid
- Elbows: градиент upperarm/forearm + twist
- Hips: плавный переход spine/leg + gluteus
- Fingers: по фалангам (tip→base)
Test: extreme poses, проверка деформаций коленей/локтей"
```

### СТАДИЯ 6: ANIMATION LIBRARY (NLA)
```bash
# Базовые циклы
"Walk Cycle (24 frames @ 24fps):
Frame 1:  Contact R (Right heel, Left toe)
Frame 7:  Down (Right foot flat, Left passing)
Frame 13: Contact L (Left heel, Right toe)
Frame 19: Down (Left foot flat, Right passing)
Frame 25: = Frame 1 (Loop)

# Run Cycle (16 frames @ 24fps)
# Idle/Breathing (120 frames)
# Jump (30 frames): Anticipation → Jump → Landing → Recovery
# Attack/Action (30-60 frames)"

### NLA Workflow
```bash
# NLA Editor Setup
"Action Editor → Create Actions: Walk, Run, Idle, Jump, Attack
NLA Editor → Push Down каждый Action → Track
Blend Mode: Replace (базовый) / Add (аддитивные слои)
Extrapolation: Cyclic (для циклов) / Hold (для поз)
Layering: Base (Walk) + Additive (Arm swing) + Override (Head turn)"
```

---

## 📊 РИГ СПЕЦИФИКАЦИИ

| Компонент | Game-Ready | Film-Ready |
|-----------|------------|------------|
| **Bones** | 100-150 | 300-500 |
| **Face Bones** | 30-50 | 80-150 |
| **Twist Bones** | Forearm (2), Thigh (2) | Full chain |
| **Corrective Shapes** | 15-25 | 50-100 |
| **IK/FK** | Arms/Legs + Snap | Full body + Spine |
| **Face Rig** | Basic (jaw, eyes, brows) | FACS (50+ shapes) |
| **Cloth/Softbody** | Simulated separately | Integrated |

---

## 🔧 MCP КОМАНДЫ ДЛЯ АНИМАЦИИ

### Walk Cycle Creation
```bash
"Создай Walk Cycle для ригнутого персонажа:
1. Frame 1: Contact R (Right heel down, Left toe up)
2. Frame 7: Down (Right foot flat, Left knee bent passing)
3. Frame 13: Contact L (Left heel down, Right toe up)
4. Frame 19: Down (Left foot flat, Right knee bent passing)
5. Frame 25: = Frame 1 (Loop)
Graph Editor: All curves Bezier, Cyclic Extrapolation
NLA: Push Down → Repeat infinitely"
```

### Action Blending (NLA)
```bash
"Setup NLA для смешивания анимаций:
Track 0: Walk Cycle (Cyclic, Replace)
Track 1: Arm Swing Additive (Add, Influence 0.5)
Track 2: Head Turn Override (Replace, Influence 1.0)
Track 3: Facial Expressions (Add, per shot)
Blending: Crossfade 5 frames между действиями"
```

### Procedural Animation (Drivers)
```bash
# Breathing
"Driver на Chest bone: Scale Z = 1.0 + 0.02 * sin(frame * 0.1)"

# Foot Roll
"Driver на Foot Roll: Custom Property 'Foot_Roll' 
→ Driver: value * 45° (Degree to Radians)"

# Eye Blink (Random)
"Driver на Eyelid Bones: 
if random() < 0.001: blink = 1.0 else: blink = 0
Interpolation: Ease In/Out, Duration: 4 frames"
```

---

## 📊 ANIMATION EXPORT SPECS

| Target | Format | Settings | Notes |
|--------|--------|----------|-------|
| **Unity** | FBX | Apply Unit Scale, Bake Space Transform, Export Animations, NLA Strips | Loop poses = Frame 1 = Frame N+1 |
| **Unreal** | FBX | Export Animations, Smoothing Groups, Tangents | Root Motion отдельно |
| **Godot** | GLTF/GLB | Export Animations, Separate Animations | NLA Tracks → Separate Animations |
| **Web (Three.js)** | GLB | Export Animations, Morph Targets | Compression: Draco |
| **Cinematic** | Alembic | Full Geo Cache, 24fps | Для VFX пайплайна |
| **Game Engine** | FBX/GLB | Bake Deformers, Remove Drivers | Оптимизация |

---

## 🔧 BATCH EXPORT (CI/CD)

### scripts/export_animations.py
```python
import bpy
import os
import sys
import argparse

argv = sys.argv[sys.argv.index("--") + 1:]
parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", default="exports/animations/")
parser.add_argument("--formats", nargs="+", default=["FBX", "GLTF"])
parser.add_argument("--fps", type=int, default=30)
args = parser.parse_args(argv)

os.makedirs(args.output_dir, exist_ok=True)

# Найти все Action'ы
actions = [a for a in bpy.data.actions if a.users > 0]

for action in actions:
    # Применить action к ригу
    rig = bpy.data.objects.get("Rig")
    if not rig:
        continue
    
    rig.animation_data.action = action
    
    # Экспорт
    name = action.name.replace(" ", "_")
    
    for fmt in args.formats:
        if fmt == "FBX":
            filepath = os.path.join(args.output_dir, f"{name}.fbx")
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                apply_unit_scale=True,
                bake_space_transform=True,
                object_types={'ARMATURE', 'MESH'},
                use_armature_deform_only=True,
                add_leaf_bones=False,
                primary_bone_axis='Y_FORWARD',
                secondary_bone_axis='X_UP',
                bake_anim=True,
                bake_anim_use_all_bones=True,
                bake_anim_use_nla_strips=True,
                bake_anim_use_all_actions=False,
                bake_anim_force_startend_keying=True,
                bake_anim_step=1.0,
                bake_anim_simplify_factor=1.0,
            )
        elif fmt == "GLTF":
            filepath = os.path.join(args.output_dir, f"{name}.glb")
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                export_format='GLB',
                use_selection=True,
                export_animations=True,
                export_frame_range=True,
                export_frame_step=1,
                export_force_sampling=True,
                export_skins=True,
                export_morph=True,
            )
    
    print(f"Exported: {name} → {fmt}")

print(f"Done! Exported {len(actions)} animations to {args.output_dir}")
```

---

## 📊 ANIMATION QUALITY CHECKLIST

| Check | Target | Tool |
|-------|--------|------|
| **Frame Range** | Start=1, End=N, Loop=1=N+1 | Dope Sheet |
| **Loop Seamless** | Frame 1 = Frame N+1 (pos/rot/scale) | Graph Editor |
| **No Gimbal Lock** | Euler Filter, Quaternion interpolation | Graph Editor |
| **IK/FK Snaps** | Smooth transitions, no pops | 3D View |
| **Foot Sliding** | Zero velocity on contact frames | Graph Editor (Velocity) |
| **Interpenetration** | No self-collision | Physics/Cloth sim |
| **Frame Rate** | Constant (24/30/60 fps) | Scene Settings |
| **Root Motion** | Clean translation/rotation | NLA/Action Editor |

---

## 🔗 LINKS

- **Rigify Docs:** https://docs.blender.org/manual/en/latest/animation/rigging/rigify.html
- **NLA Guide:** https://docs.blender.org/manual/en/latest/animation/nla.html
- **Game Export:** https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html
- **Setup 30:** [Rigify Advanced](../setups/setup_30_rigify_advanced.md)
- **Case 04:** [Character Rig](../cases/case_04_character_rig.md)
- **Next:** [WF 05: Procedural Assets](../workflows/wf_05_procedural_assets.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/workflows/wf_04_character_animation.md` |
| Russian | `multilang/ru/workflows/wf_04_character_animation.md` |

---

## FULL ADDENDUM: engine gates

### Unity gate
- [ ] FBX + bake transform, NLA baked, scale applied
### Unreal gate
- [ ] FBX + smoothing + tangents, LOD suffixes
### Godot gate
- [ ] GLB без Draco, animations separate

