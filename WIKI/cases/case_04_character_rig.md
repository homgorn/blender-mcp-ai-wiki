---
id: case_04_character_rig
lang: ru
category: cases
status: full
tags: [animation, case, rigging]
---
# CASE 04: CHARACTER RIG & ANIMATION

**ID:** CASE-04 | **Type:** Character Pipeline | **Difficulty:** ⭐⭐⭐ | **Time:** 3-6 hours

---

## 🎯 GOAL
Complete character pipeline: base mesh → rigging → skinning → animation → render

---

## 📋 PIPELINE (7 STAGES)

```
STAGE 1: Base Mesh (Modeling)          → P01, P04, P05, P08
STAGE 2: Retopology (Game-ready)       → P06
STAGE 3: UV & Texturing                → P05, P12
STAGE 4: Rigging (Rigify/Custom)       → P23
STAGE 5: Skinning & Weights            → P23
STAGE 6: Animation                     → P22, P24, P25, P26
STAGE 7: Render & Export               → P13, P14, P15, P49
```

---

## 🔧 MCP COMMANDS

### STAGE 1: BASE MESH (Sculpting)
```bash
# Base human proportions
"Создай сферу 'Head' радиус 0.12м сегменты 32
Создай цилиндр 'Torso' радиус 0.15м высота 0.5м
Создай цилиндр 'Hip' радиус 0.12м высота 0.2м
Создай 4 конечности: цилиндры с Subsurf + Dyntopo

# Объединить в один объект
"Объедини все части в 'Character_Base'
Dyntopo: constant_detail=8, symmetry X
Скульптинг: пропорции 8 голов, силуэт, анатомия"
```

### STAGE 2: RETOPOLOGY (Game-ready ~15k tris)
```bash
"Quad Remesher: target_quads=5000, adaptivity=0.3
Проверить: только квады, нет полюсов >5, edge flow по анатомии
UV: Smart Project для тела, ручная для лица/рук"
```

### STAGE 3: UV & TEXTURING
```bash
# UDIM layout (4 tiles)
"UDIM 1001: Head/Neck
UDIM 1002: Torso/Arms
UDIM 1003: Legs
UDIM 1004: Hands/Feet/Details

# Texture Paint слои
"BaseColor, Roughness, Normal, Subsurface, Specular, Displacement
4k на голову, 2k на тело"
```

### STAGE 4: RIGGING (Rigify)
```bash
# Meta-rig
"Add Armature → Human (Meta-Rig)
Масштабировать под меш: Match to Mesh
Generate Rig → Rigify

# Дополнительные кости
"Face Rig: 50+ костей (jaw, eyes, brows, lips, cheeks)
Fingers: полная иерархия (3 фаланги на палец)
Twist bones: forearm, upper arm, thigh, calf
Corrective shapes: knees, elbows, shoulders"
```

### STAGE 5: SKINNING
```bash
"Parent Mesh → Rig (Automatic Weights)
Weight Paint cleanup:
- Head: жесткая привязка к skull
- Shoulders: градиент clavicle/upperarm
- Hips: плавный переход spine/leg
- Fingers: по фалангам
Test: extreme poses, проверка деформаций"
```

### STAGE 6: ANIMATION
```bash
# Walk Cycle (24 фрейма = 1 сек @ 24fps)
"Frame 1: Contact (right heel, left toe)
Frame 7: Down (right foot flat, left passing)
Frame 13: Contact (left heel, right toe)
Frame 19: Down (left foot flat, right passing)
Frame 25 = Frame 1 (loop)

# Graph Editor: Bezier, Auto Clamp
# NLA: Walk Action → Push Down → Blend с Run/Idle"
```

### STAGE 7: RENDER & EXPORT
```bash
# Lighting
"HDRI 'studio' 2k + 3-point studio
Volumetric: легкая дымка density=0.02"

# Camera
"Cam_Main: focal=50mm, DOF на глаза f/2.0
Cam_CloseUp: focal=85mm f/1.4 на лицо"

# Render
"Cycles 256 samples, Denoising, 4K
Output: EXR + MP4 (H.264 High)"
```

---

## 📊 CHARACTER SPECS

| Spec | Game-Ready | Film-Ready |
|------|------------|------------|
| **Triangles** | 15k-25k | 50k-150k |
| **Bones** | 100-150 | 300-500 |
| **Blend Shapes** | 20-30 | 50-100 |
| **UV Tiles** | 1-2 (1024) | 4-8 (UDIM 4k) |
| **Texture Res** | 2k | 4k-8k |
| **Rig Type** | Rigify + Custom | Custom + Facial |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 06: ANIMATION LOOP](case_06_animation_loop.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md)
- **По темам:** [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 09: ANIME HEAD BUST](case_09_anime_head_bust.md)
- **Теги:** #animation, #case, #rigging

