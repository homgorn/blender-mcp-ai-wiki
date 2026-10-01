---
id: wf_07_game_asset_pipeline
lang: en
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: template
---
# WF 07: GAME ASSET PIPELINE

> Goal: ## 🌍 MULTILANG

**ID:** wf_07_game_asset_pipeline | **Lang:** en | **Orig:** ru | **Category:** workflows | **Tags:** 

---

# WF 07: GAME ASSET PIPELINE

**ID:** WF-07 | **Type:** Game Asset Production | **Difficulty:** ⭐⭐ | **Time:** 1-3 hours per asset

---

## 🎯 ЦЕЛЬ
Production-ready пайплайн для игровых ассетов: от концепта до интеграции в движок

---

## 📋 ПАЙПЛАЙН СТАДИИ

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CONCEPT    │───▶│  BLOCKOUT   │───▶│  HIGH POLY  │───▶│  RETOPO     │───▶│  UV &       │───▶│  BAKING &   │
│  /REFERENCE │    │  (Primitives)│    │  (Sculpt)   │    │  (Low Poly) │    │  BAKING     │    │  TEXTURING  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                                                     │
                                                                                                     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  ENGINE     │◀───│  VALIDATION │◀───│  EXPORT     │◀───│  LOD        │◀───│  MATERIAL   │◀───│  TEXTURE    │
│  INTEGRATION│    │  (Auto QA)  │    │  (Multi-fmt)│    │  Generation │    │  SETUP      │    │  FINALIZE   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 📋 СТАДИЯ 1: CONCEPT & REFERENCE

### Reference Board
```bash
"Создай Reference Board в PureRef / Milanote:
- Orthographic views (Front/Side/Top) - обязательно для пропорций
- Material close-ups (Metal wear, Fabric weave, Wood grain)
- Lighting references (Studio, Outdoor, Mood)
- Scale references (Human silhouette, Door height 2.1m)
- Polycount targets: Hero 15k, Prop 5k, Foliage 500"
```

### Scale Reference Setup
```bash
"Создай Scale Reference в сцене:
1. Human proxy: Cylinder 1.8m height, 0.5m width
2. Door frame: 2.1m x 0.9m
3. Standard chair: 0.45m seat height
3. Grid floor: 1m x 1m squares
Всё в Collection 'Reference' → Hide in Render"
```

---

## 🔧 СТАДИЯ 2: BLOCKOUT (Primitives + Boolean)

```bash
# Основные формы
"Создай блокаут из примитивов:
- Body: Cube → Subdivide → Shape
- Head: Sphere → Shape
- Limbs: Cylinders → Taper
- Props: Primitives → Boolean для вырезов

# Пропорции через Drivers
"Driver на Scale: Body_Height = 1.8m (Driver Variable)
Limb_Length = Body_Height * 0.45
Head_Size = Body_Height * 0.125"

# Boolean для деталей
"Boolean Difference: Вырезы для глаз, рта, карманов
Boolean Union: Объединение частей оружия/аксессуаров"
```

---

## 🔧 СТАДИЯ 3: HIGH POLY (Sculpting)

```bash
# Dyntopo Sculpting
"Dyntopo: Constant Detail 8-12, Symmetry X
Brushes: Clay Strips, Draw Sharp, Smooth, Grab, Inflate, Crease
Детали: Мышцы, Жесты, Ткани, Швы, Пуговицы, Застежки"

# Multires для анимируемых частей
"Multires Modifier: 4-5 уровней подделения
Sculpt Level: 3-4 для деталей лица/рук
Base Level: 0 для риггинга"
```

---

## 🔧 СТАДИЯ 3: RETOPOLOGY (Game-Ready)

```bash
# Auto Retopo (Quad Remesher)
"Quad Remesher: Target Quads 5000 (Hero) / 2000 (Prop)
Adaptivity: 0.3 (больше полигонов в деталях)
Symmetry: X

# Manual Retopo (Критичные зоны)
"Ручная ретопология:
- Лицо: Edge flow по мимическим мышцам (Лоопы вокруг глаз/рта)
- Руки: Edge flow по суставам, Edge loops вокруг запястий
- Деформационные зоны: Колени, Локти, Плечи, Таз
- Edge Flow: Следует за анатомией, Квады только"
```

### Polycount Targets
| Asset Type | Tris (LOD0) | Tris (LOD1) | Tris (LOD2) | UV Tiles |
|------------|-------------|-------------|-------------|----------|
| **Hero Character** | 15k-25k | 8k-12k | 3k-5k | 2-4 (UDIM) |
| **NPC/Enemy** | 8k-15k | 4k-8k | 2k-4k | 1-2 |
| **Hero Prop** | 5k-10k | 2k-5k | 1k-2k | 1 |
| **Environment Prop** | 2k-5k | 1k-3k | 500-1k | 1 |
| **Foliage/Billboard** | 200-500 | 100-200 | 50-100 | 1 |

---

## 🔧 СТАДИЯ 4: UV & BAKING

### UV Unwrapping Strategy
```bash
# Character UV (UDIM)
"UDIM Layout:
1001: Head/Neck (4k)
1002: Torso/Arms (2k)
1003: Legs (2k)
1004: Hands/Feet/Details (2k)

# Props/Environment
"Smart UV Project: Angle Limit 66°, Island Margin 0.005
Lightmap Pack: Padding 4px (для Lightmap UV)
Cube Projection: Для архитектуры/коробок"
```

### Baking Setup (High → Low Poly)
```bash
# Bake Settings (Cycles)
"Bake Settings:
Engine: Cycles, Samples: 16 (AO 256)
Ray Distance: 0.01 (Cage)
Margin: 16px
Use Selected to Active: True

# Maps to Bake:
1. Normal (Tangent Space, +X +Y +Z) → EXR 32-bit
2. AO (256 samples, Distance 0.5m) → PNG 16-bit
3. Curvature (Convex/Concave) → EXR 16-bit
4. Position (World Space) → EXR 32-bit
5. Thickness (Subsurface) → PNG 16-bit
5. Material ID → PNG 8-bit
6. Base Color (из High Poly материалов) → PNG 16-bit sRGB"
```

---

## 🔧 СТАДИЯ 5: TEXTURING (Substance / Blender)

### Substance Painter Workflow
```bash
# Export для SP
"Export FBX: Apply Scale, Bake Space Transform, Selected Only
Import в SP: Template 'PBR Metallic Roughness'
Project Settings: 4k, Padding 16, Dilation 4"

# Smart Materials
"Smart Material Library:
- Metal_Gold, Metal_Steel, Metal_Rusted
- Fabric_Cotton, Fabric_Leather, Fabric_Denim
- Wood_Oak, Wood_Pine, Wood_Painted
- Stone_Marble, Stone_Concrete, Stone_Brick
- Plastic_Glossy, Plastic_Matte, Rubber"

# Layer Stack
"Base: BaseColor + Normal + Roughness + Metallic
Detail: Height/Normal Detail (Micro-detail)
Wear: Edge Wear (Curvature Mask), Dirt (AO Mask)
Damage: Scratches (Normal Map), Chips (Height Map)
Story: Stickers, Decals, Graffiti (Alpha Blend)"
```

### Blender Texture Paint (Alternative)
```bash
"Blender Texture Paint Setup:
Layers: BaseColor, Roughness, Metallic, Normal, Height, Subsurface
Resolution: 4k Head, 2k Body
Brushes: Draw, Soften, Smear, Clone, Fill, Mask
Stencil: Для текстуры кожи, ткани, металла
Export: Все карты → //textures/{asset}_v001/"
```

---

## 🔧 СТАДИЯ 6: MATERIAL SETUP (Engine Ready)

### Unity URP/HDRP
```bash
# Shader Graph / Standard Shader
"Material Setup:
- Shader: URP/Lit или HDRP/Lit
- Base Map: BaseColor (sRGB)
- Normal Map: Normal (BC5/BC7 compression)
- Mask Map: R=Metallic, G=AO, B=Detail, A=Smoothness (1-Roughness)
- Detail Maps: Detail Normal + Detail Albedo
- Emission Map: Для свечения
- UV2: Lightmap UV (Generate Lightmap UVs)"
```

### Unreal Engine
```bash
# Material Instance
"Master Material: MF_PBR_Master
Parameters:
- BaseColor (Texture)
- Normal (Texture, BC5)
- ORM: R=AO, G=Roughness, B=Metallic
- Emissive Color + Emissive Map
- Subsurface Profile (для кожи)
- Clearcoat (для лака/керамики)
- Parallax/POM (для рельефа)

# Texture Compression
"Default: BC7 (BaseColor/Normal), BC4 (ORM)
Normal: BC5n (Normal Map)
HDR: BC6H (Emission/HDRI)"
```

---

## 🔧 СТАДИЯ 7: LOD GENERATION

```bash
# Auto LOD (Blender/Simplygon/Quad Remesher)
"LOD0: Full Detail (Target Tris)
LOD1: Decimate 0.5 (50% tris), UV сохраняются
LOD2: Decimate 0.25 (25% tris)
LOD3: Decimate 0.1 (10% tris) или Billboard

# Billboard Impostor (Для дальних LOD)
"8 angles (45° steps) → Sprite Sheet 2048x2048
Shader: Billboard + Alpha + View Angle → Sprite Index
Material: Unlit/Transparent Cutout"
```

---

## 🔧 СТАДИЯ 8: EXPORT & VALIDATION

### Export Settings per Engine
```bash
# Unity (FBX)
"FBX Export:
- Apply Unit Scale, Bake Space Transform
- Object Types: ARMATURE, MESH
- Bake Animation: All Actions, NLA Strips
- Forward: Y, Up: X
- Embed Media: False (Textures отдельно)"

# Unreal (FBX)
"FBX Export:
- Export Animations: True
- Smoothing Groups: True
- Tangents: True
- Bake Animation: All, NLA Strips, Resample 1.0"

# Godot / Web (GLTF/GLB)
"GLTF Export:
- Format: GLB (Binary)
- Export Animations: All
- Tangents: True
- Draco Compression: Level 6-8
- Texture Compression: Basis Universal"

# Web/Three.js (Optimized GLB)
"GLTF Export:
- Format: GLB
- Draco Compression: Level 8
- Texture Compression: Basis Universal (KTX2)
- Remove Unused: Nodes, Materials, Textures
- Meshopt Compression: ON"
```

### Validation Checklist (Auto QA)
```bash
# Авто-проверка (Python Script)
"Validation Rules:
✅ Tris within target ±10%
✅ No non-manifold edges
✅ No overlapping UVs (Margin > 2px)
✅ All UVs in 0-1 range (or UDIM tiles)
✅ No zero-area faces
✅ Normals outward
✅ Vertex Groups named correctly (for rigging)
✅ Material names match naming convention
✅ Texture names follow convention: {asset}_{map}_{res}.{ext}
✅ LODs: Smooth transition, Screen size thresholds
✅ Pivot at base (0,0,0) or logical center
✅ Scale = 1.0 (Applied)
✅ No unused materials/textures
✅ Naming Convention: {asset}_{type}_{variant}_LOD{num}"
```

---

## 📦 ENGINE INTEGRATION

### Unity Pipeline
```bash
# Asset Postprocessor (Auto)
"Assets/Editor/AssetPostprocessor.cs:
- OnPreprocessModel: Auto-scale, Generate Colliders
- OnPostprocessModel: Setup Materials, LOD Groups
- OnPreprocessTexture: sRGB/Linear, Compression, Mipmaps
- Naming Convention Enforcement"

# Prefab Structure
"Prefab_Root/
├── Mesh (LOD Group)
│   ├── LOD0 (MeshRenderer)
│   ├── LOD1 (MeshRenderer)
│   └── LOD2 (MeshRenderer)
├── Rig (Animator + Avatar)
├── Colliders (Capsule/Box/Mesh)
├── Audio (AudioSource)
└── Scripts (MonoBehaviour)"
```

### Unreal Pipeline
```bash
# DataAsset + Blueprint
"Asset Structure:
/Game/Assets/
├── Meshes/
│   ├── SM_Asset_LOD0.uasset
│   ├── SM_Asset_LOD1.uasset
│   └── SM_Asset_LOD2.uasset
├── Materials/
│   ├── M_Asset_Base.uasset
│   └── MI_Asset_Variant.uasset
├── Textures/
│   ├── T_Asset_BaseColor.uasset
│   ├── T_Asset_Normal.uasset
│   └── T_Asset_ORM.uasset
├── Blueprints/
│   └── BP_Asset.uasset
└── Animations/
    └── A_Asset_Action.uasset"
```

---

## 🔗 LINKS

- **Poly Haven:** https://polyhaven.com/
- **Poly Pizza:** https://poly.pizza/
- **Sketchfab:** https://sketchfab.com/
- **Substance 3D:** https://www.adobe.com/products/substance3d.html
- **Setup 08:** [Asset Pipeline](../setups/setup_08_asset_pipeline.md)
- **Case 02:** [Game Props](../cases/case_02_game_props.md)
- **Next:** [WF 08: Batch Processing](../workflows/wf_08_batch_processing.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/workflows/wf_07_game_asset_pipeline.md` |
| Russian | `multilang/ru/workflows/wf_07_game_asset_pipeline.md` |