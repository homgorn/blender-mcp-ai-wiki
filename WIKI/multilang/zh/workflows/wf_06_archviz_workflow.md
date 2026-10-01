---
id: wf_06_archviz_workflow
lang: zh
orig_lang: ru
category: workflows
type: workflow
difficulty: 3
translation: template
---
# WF 06: ARCHVIZ ВОРКФЛОУ

> 目标: 

**ID:** wf_06_archviz_workflow | **Lang:** zh | **Orig:** ru | **Category:** workflows | **Tags:** **, 4a7c2a, 8b3a2a, 8b7355, b0b0b0, cccccc, e0e0e0, e8d5b7

## 使用方法
这是 'wf_06_archviz_workflow' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
wf_06_archviz_workflow / workflows / **, 4a7c2a, 8b3a2a, 8b7355, b0b0b0, cccccc, e0e0e0, e8d5b7
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: wf_06_archviz_workflow
lang: ru
orig_lang: ru
category: workflows
type: workflow
difficulty: 3
---

# WF 06: ARCHVIZ ВОРКФЛОУ

> Цель: ## 🌍 MULTILANG

**ID:** wf_06_archviz_workflow | **Lang:** ru | **Orig:** ru | **Category:** workflows | **Tags:** 4a7c2a, 8b3a2a, 8b7355, b0b0b0, cccccc, e0e0e0, e8d5b7

---

# WF 06: ARCHVIZ WORKFLOW

**ID:** WF-06 | **Type:** Architectural Visualization | **Difficulty:** ⭐⭐⭐ | **Time:** 3-8 hours

---

## 🎯 ЦЕЛЬ
Профессиональный ArchViz пайплайн: от CAD планов до фотореалистичного рендера

---

## 📋 ПАЙПЛАЙН СТАДИИ

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CAD/IMPORT│───▶│  MODELING   │───▶│  MATERIALS  │───▶│  LIGHTING   │───▶│  CAMERA     │
│  (DWG/IFC/  │    │  (Walls,    │    │  (PBR,      │    │  (HDRI +    │    │  (Composition│
│  SketchUp)  │    │  Windows,   │    │  Displacement)│  │  Studio)    │    │  DOF)       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                                                                    │
       ▼                                                                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  FURNITURE  │───▶│  LANDSCAPE  │───▶│  RENDER     │───▶│  COMPOSITING│───▶│  DELIVERY   │
│  (Poly Pizza/│    │  (GN Scatter)│   │  (Cycles,    │    │  (Color,    │    │  (4K/8K,    │
│  Sketchfab)  │    │  Grass/Trees)│   │  256-512 spp)│   │  Glare, LUT)│    │  Video, VR)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🔧 MCP КОМАНДЫ ПО СТАДИЯМ

### СТАДИЯ 1: ИМПОРТ CAD / ПЛАНЫ
```bash
# Импорт DWG/DXF
"Импорт DWG планов:
File → Import → AutoCAD DXF/DWG
Scale: 1 Unit = 1 Meter
Layers: Walls, Doors, Windows, Dimensions, Text
Clean: Remove duplicate vertices, Merge by Distance"

# Или через SketchUp
"Import SKP: File → Import → SketchUp
Cleanup: Remove internal faces, Triangulate → Quads (Alt+J)"

# Из IFC (BIM)
"Import IFC: File → Import → IFC
IfcOpenShell: элементы → Collections по IfcClass
Walls/Slabs/Windows/Doors → Отдельные коллекции"
```

### СТАДИЯ 2: МОДЕЛИРОВАНИЕ АРХИТЕКТУРЫ
```bash
# Стены (из линий плана)
"Выбери линии стен → Convert to Mesh → Extrude 3m → Solidify 0.2m
Boolean: Windows/Doors cutouts (Difference)
Window Frames: Separate object, Bevel 0.02m, Material 'Aluminum'"

# Полы/Потолки
"Floor: Plane → Scale to room → Solidify 0.15m
Ceiling: Copy Floor → Move Z=3m → Modifier Array для плиток"

# Лестницы
"Curve → Bezier → Extrude → Bevel Depth 0.3m
Array: Count по высоте, Relative Offset Z=0.18m
Railing: Separate curve → Bevel Profile"
```

### СТАДИЯ 3: ОКНА И ДВЕРИ (Parametric)
```bash
# Окна (Geometry Nodes / Asset Browser)
"Window Asset: Frame 0.08m, Glass 0.004m, Sill 0.05m
Params: Width, Height, Divisions (2x2, 3x1, etc.), Handle Type
Insert: Boolean Difference в стену + Frame Object"

# Двери
"Door Asset: Frame, Panel, Handle, Hinges
Params: Width (0.9/1.0/1.2), Height (2.1/2.4), Swing Direction
Hardware: Handle, Lock, Hinges (Separate objects для анимации)"
```

### СТАДИЯ 4: МАТЕРИАЛЫ (ArchViz PBR Library)
```bash
# Базовая библиотека
"Создай Material Library Collection:
Mat_Concrete_Polished: BaseColor #E0E0E0, Rough 0.1, Metal 0, Clearcoat 0.3
Mat_Concrete_Rough: BaseColor #B0B0B0, Rough 0.8, Metal 0
Mat_Brick_Red: BaseColor #8B3A2A, Rough 0.9, Normal Brick, Height 0.01
Mat_Wood_Floor: BaseColor #8B7355, Rough 0.6, Anisotropic 0.5
Mat_Glass_Clear: Transmission 1, IOR 1.52, Rough 0
Mat_Grass: BaseColor #4A7C2A, Rough 0.9, Displacement Grass
Mat_Metal_Aluminum: BaseColor #CCCCCC, Rough 0.2, Metal 1, Aniso 0.3
Mat_Stone_Travertine: BaseColor #E8D5B7, Rough 0.7, Normal Stone"

# Displacement Setup
"Все материалы с Height: Material Settings → Displacement = Displacement Only
Cycles: Experimental → Adaptive Subdivision → Dicings Rate 1-2"
```

### СТАДИЯ 5: ОСВЕЩЕНИЕ (HDRI + Studio)
```bash
# Дневной интерьер
"HDRI: Poly Haven 'studio_small_01' 2k, Strength 0.4
Sun: 5000K, 5000W, Angle 45°, Size 0.5m (Soft Shadows)
Portals: World → Portal на всех окнах (Cycles)

# Вечерний интерьер
HDRI: 'evening_road_01' 2k, Strength 0.8
Interior Lights: 2700K, 800-1500 lm per fixture
Table Lamps: Emission 3000K, 500 lm
Cove Lighting: LED Strip 3000K, Hidden in cove"

# Дневной экстерьер
"HDRI: 'kloppenheim_02' 4k, Strength 1.0
Sun: 5500K, 10000W, Angle 30° (Morning) / 60° (Noon)
Volumetric: World Volume Scatter Density 0.01, Anisotropy 0.5"
```

### СТАДИЯ 6: МЕБЕЛЬ И ДЕКОР (Asset Browser)
```bash
# Poly Pizza (Low-poly, Free)
"Search Poly Pizza: 'sofa', 'chair', 'table', 'lamp', 'plant', 'rug'
License: CC0 preferred, Download → Normalize 1.0m → Apply Materials"

# Sketchfab (High-poly, Realistic)
"Search Sketchfab: 'modern sofa 3d model', 'dining table', 'floor lamp'
Downloadable: Yes, License: CC-BY/CC0
Import: GLTF → Scale → Materials Fix → Collection 'Furniture'"

# Custom Props (Custom Modeling)
"Custom: Kitchen cabinets (GN parametric), Wardrobes, Bookshelves
Plants: GN Scatter → Collection 'Plants_Indoor' (10 variants)"
```

### СТАДИЯ 7: ЛАНДШАФТ И ОКРУЖЕНИЕ
```bash
# Террейн
"Plane → Subdivide 200x200 → Displace (Noise Texture, Strength 5m)
Texture Paint: Grass, Dirt, Path, Grass/Flower Scatter (GN)"

# Растительность (GN Scatter)
"Collection 'Trees_Large': 5 variants, Density 0.005, Scale 0.8-1.3
Collection 'Bushes': 8 variants, Density 0.02
Collection 'Grass': 3 variants, Density 0.5, Weight Paint для путей
Collection 'Flowers': 5 variants, Density 0.1, Random Color"

# Вода
"Plane → Shader: Glass + Noise Displacement + Foam (Geometry Nodes)
River: Curve → Mesh → Flow Map → Animated UV Offset"
```

### СТАДИЯ 8: КАМЕРЫ И КОМПОЗИЦИЯ
```bash
# Камеры
"Cam_Main: Wide 24mm, Eye Level 1.6m, Rule of Thirds
Cam_Detail: 85mm, f/1.8, DOF on Detail
Cam_Wide: 16mm, Low Angle, Dramatic Perspective
Cam_Aerial: Drone View, 200m Height, Ortho/Perp

# DOF Setup
"Focus Object: Target Empty (Animated)
F-Stop: 2.8 (Interior), 8 (Exterior), 1.8 (Portrait)
Blades: 8-9, Ratio 1.0"

# Composition Guides
"Camera → Viewport Display → Composition Guides: Thirds / Golden Ratio"
```

### СТАДИЯ 8: РЕНДЕР НАСТРОЙКИ
```bash
# Production Quality
"Cycles: 512 samples, Adaptive Threshold 0.01, Min Samples 64
Denoising: OPTIX (GPU) / OpenImageDenoise (CPU)
Adaptive Sampling: ON, Min 32, Threshold 0.01

# Light Paths
Max Bounces: 12, Diffuse 4, Glossy 4, Transmission 12, Volume 4
Caustics: Refractive ON, Reflective ON

# Color Management
Filmic, Look: Medium High Contrast
Exposure: 0.0, Gamma: 1.0

# Output
Resolution: 3840x2160 (4K) / 7680x4320 (8K)
Format: EXR MultiLayer 32-bit + PNG 16-bit
Color Mode: RGBA, Film Transparent: ON (для композинга)"
```

### СТАДИЯ 9: КОМПОЗИТИНГ
```bash
# Basic Compositor Tree
"Render Layers → Color Balance (Lift/Gamma/Gain) → Hue/Sat (1.1) 
→ Gamma (1.05) → Exposure (0.1) → Glare (Fog Glow, 0.2 mix) 
→ Lens Distortion (0.01) → Vignette (0.15) 
→ Color Matrix (Teal & Orange) → Vignette (0.1) 
→ Film Grain (Overlay 0.02) → Composite + Viewer"

# Cryptomatte для селекций
"Enable Cryptomatte: Object + Material
Compositor: Cryptomatte Node → Matte Output → Color Correct отдельные элементы"

# Passes для гибкости
"Enable: Combined, Depth, Normal, Mist, AO, Emission, Shadow, Cryptomatte
File Output: EXR MultiLayer 32-bit (All Passes) + PNG 16-bit (Beauty)"
```

### СТАДИЯ 10: ДЕЛИВЕРИ
```bash
# Форматы
"Still: 4K EXR 32-bit + PNG 16-bit + JPEG 95% (Web)
Animation: 4K 30fps MP4 (H.264 High) + ProRes 422 HQ (Archive)
VR/360: 8K Stereoscopic, Equirectangular, Stereo Side-by-Side

# Naming
project_scene_cam_v001_4k.exr
project_scene_cam_v001_4k.png
project_anim_v001_4k.mp4
project_anim_v001_4k_prores.mov"

# Color Space Delivery
"sRGB (Web), Rec.709 (Video), DCI-P3 (Cinema), Rec.2020 (HDR)
ICC Profile embedded в EXR/PNG"
```

---

## 📊 ARCHVIZ QUALITY PRESETS

| Preset | Samples | Resolution | Time (RTX 4090) | Use Case |
|--------|---------|------------|-----------------|----------|
| **Draft** | 64 | 1920x1080 | 30 сек | Blocking, Layout |
| **Preview** | 128 | 1920x1080 | 1 мин | Client Review |
| **Standard** | 256 | 3840x2160 | 5 мин | Standard Delivery |
| **High** | 512 | 3840x2160 | 12 мин | Competition |
| **Ultra** | 1024 | 7680x4320 | 45 мин | Billboard/Print |

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| **Portals на окнах** | Ускоряет рендер интерьера в 3-5x |
| **Adaptive Sampling** | Фокусирует сэмплы на шумных участках |
| **Light Linking** | Контроль отражений в зеркалах/стекле |
| **Cryptomatte** | Мгновенные маски в композинг без перерисовки |
| **EXR MultiLayer** | Все проходы в одном файле, 32-bit precision |
| **Adaptive Subdivision** | True displacement без тяжелого меша |
| **Portals + HDRI** | Реалистичное GI за секунды |

---

## 🔗 LINKS

- **Poly Haven:** https://polyhaven.com/
- **Poly Pizza:** https://poly.pizza/
- **Sketchfab:** https://sketchfab.com/
- **Blender ArchViz:** https://www.blender.org/community/archviz/
- **Case 01:** [ArchViz Interior](../cases/case_01_archviz_interior.md)
- **Setup 01:** [blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Next:** [WF 07: Game Asset Pipeline](../workflows/wf_07_game_asset_pipeline.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/workflows/wf_06_archviz_workflow.md` |
| Russian | `multilang/ru/workflows/wf_06_archviz_workflow.md` |