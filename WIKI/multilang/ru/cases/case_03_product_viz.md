---
id: case_03_product_viz
lang: ru
orig_lang: en
category: cases
type: case
difficulty: 2
translation: template
---
# КЕЙС 03: PRODUCT VISUALIZATION

> Цель: ## 🌍 MULTILANG

**ID:** case_03_product_viz | **Lang:** ru | **Orig:** en | **Category:** cases | **Tags:** 0d0d0d, 1a1a1a, b8b8c0

---

# CASE 03: PRODUCT VISUALIZATION

**ID:** CASE-03 | **Type:** Product Visualization | **Difficulty:** ⭐⭐ | **Time:** 1-2 hours

---

## 🎯 GOAL
Create studio-quality product render: watch, perfume bottle, or tech gadget with macro details

---

## 📋 PIPELINE (6 STAGES)

```
STAGE 1: Modeling (CAD-like precision)    → P01, P02, P03, P04
STAGE 2: UV Unwrapping                    → P05
STAGE 3: Materials (Hero quality)         → P09, P11, P12
STAGE 4: Lighting (Studio)                → P13
STAGE 5: Camera (Macro/Detail)            → P14
STAGE 6: Compositing (Clean)              → P15
```

---

## 🔧 MCP COMMANDS

### STAGE 1: MODELING (Watch Example)
```bash
# Case body
"Создай цилиндр 'Case_Body' радиус 0.022м глубина 0.012м вершин 64
Позиция (0,0,0) материал 'Mat_Metal_Steel'"

# Bezel
"Создай цилиндр 'Bezel' радиус 0.024м глубина 0.003м вершин 64
Позиция (0,0,0.006) материал 'Mat_Metal_Ceramic'"

# Crystal
"Создай цилиндр 'Crystal' радиус 0.021м глубина 0.004м вершин 64
Позиция (0,0,0.008) материал 'Mat_Glass_Sapphire'"

# Crown
"Создай цилиндр 'Crown' радиус 0.004м глубина 0.008м вершин 32
Позиция (0.024, 0, 0.004) материал 'Mat_Metal_Steel'
Boolean DIFFERENCE для паза"

# Buttons (2 шт.)
"Создай цилиндр 'Button_1' радиус 0.003м глубина 0.004м
Позиция (0.024, 0, 0.002) материал 'Mat_Metal_Steel'
Button_2 зеркально по X"

# Strap (Geometry Nodes)
"Создай плоскость 'Strap_Base' 0.2x0.02м
GN: Curve to Mesh, профиль 0.004м, материал 'Mat_Leather_Black'
Array по кривой длиной 0.25м"
```

### STAGE 2: UV UNWRAPPING
```bash
# Case body
"Smart Project angle_limit=66 island_margin=0.01"

# Crystal - Cube Projection
"Cube Project clip_to_bounds=True"

# Strap - Follow Active Quads
"Select edge loop → Mark Seam → Unwrap → Follow Active Quads"
```

### STAGE 3: MATERIALS (Hero Quality)
```bash
# Steel (Case, Crown, Buttons)
"Mat_Metal_Steel:
BaseColor: #B8B8C0, Roughness: 0.15, Metallic: 1.0
Clearcoat: 0.3, ClearcoatRough: 0.05
Anisotropic: 0.3, Tangent: UV
Normal: brushed metal procedural"

# Ceramic Bezel
"Mat_Metal_Ceramic:
BaseColor: #1A1A1A, Roughness: 0.05, Metallic: 0.0
Transmission: 0, Clearcoat: 1.0, ClearcoatRough: 0.01
Normal: subtle ceramic texture"

# Sapphire Crystal
"Mat_Glass_Sapphire:
Transmission: 1.0, IOR: 1.77, Roughness: 0
Clearcoat: 0.5 (AR coating), ClearcoatRough: 0.001
Absorption: slight blue tint at edges"

# Leather Strap
"Mat_Leather_Black:
BaseColor: #0D0D0D, Roughness: 0.85, Metallic: 0
Sheen: 0.15, SheenTint: 0.3
Normal: leather grain procedural
Height: embossed pattern"
```

### STAGE 4: LIGHTING (Product Studio)
```bash
# HDRI
"Poly Haven 'studio_small_01' 2k, strength=0.3"

# Key Light (Main)
"AREA 1000W, 0.3x0.3м, позиция (0.1, -0.2, 0.15), поворот к часам
Shape: Rectangle, Spread: 45°"

# Fill Light
"AREA 300W, 0.5x0.5м, позиция (-0.15, 0.1, 0.1), мягкий"

# Rim Light
"AREA 200W, 0.2x0.2м, позиция (0, 0.15, 0.15), контрастный край"

# Accent (Sparkle on Crystal)
"POINT 50W, позиция (0.02, -0.02, 0.02), размер 0"
```

### STAGE 5: CAMERA (Macro)
```bash
# Hero Shot
"Cam_Hero: позиция (0, -0.3, 0.05) focal=100mm sensor=36mm
DOF: focus на циферблат, f-stop=2.8, blades=9
Composition: Center + Rule of Thirds"

# Detail Shots
"Cam_Dial: (0, -0.15, 0.03) focal=150mm f/2.0 → крупно циферблат
Cam_Crown: (0.025, 0, 0.005) focal=100mm f/4.0 → коронка
Cam_Strap: (-0.1, -0.2, 0) focal=85mm f/2.8 → текстура ремня"
```

### STAGE 6: COMPOSITING
```bash
"Passes: Combined, Depth, Normal, Cryptomatte, Mist
Color: Lift/Gamma/Gain (Teal & Orange), Glare (0.15 threshold),
Vignette (0.1), Sharpen (Unsharp Mask 0.5),
Chromatic Aberration (0.002)
Output: 4K EXR 32-bit + 4K PNG 16-bit"
```

---

## 📊 PRODUCT SPECS

| Параметр | Значение |
|----------|----------|
| **Model Scale** | Real-world (метры) |
| **Texture Res** | 4k BaseColor, 2k Roughness/Normal |
| **Triangles** | 50k-150k (hero) |
| **Materials** | 5-8 unique |
| **Samples** | 512-1024 |
| **Resolution** | 4K (3840x2160) |
| **Render Time** | 10-30 min (RTX 4090) |

---

## 🔗 LINKS

- **Prompts:** P01-P05, P09, P11-P15
- **Workflows:** [WF 01](../workflows/wf_01_text_to_scene.md), [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **Prompts Used:** P01, P02, P03, P04, P05, P09, P11, P12, P13, P14, P15

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| Real-world scale (метры) | Правильный DOF, физика света |
| Anisotropic Tangent = UV | Правильные блики на металле |
| Cryptomatte по материалам | Маски для каждого материала |
| Render Region (Ctrl+B) | Быстрый рендер деталей |
| 4K + 512 samples = Print Ready | Качество для маркетинга |

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/cases/case_03_product_viz.md` |
| Russian | `multilang/ru/cases/case_03_product_viz.md` |