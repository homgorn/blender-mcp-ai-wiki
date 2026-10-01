---
id: case_05_procedural_city
lang: ru
orig_lang: en
category: cases
type: case
difficulty: 3
translation: template
---
# КЕЙС 05: PROCEDURAL CITY

> Цель: ## 🌍 MULTILANG

**ID:** case_05_procedural_city | **Lang:** ru | **Orig:** en | **Category:** cases | **Tags:** 

---

# CASE 05: PROCEDURAL CITY

**ID:** CASE-05 | **Type:** Procedural Generation | **Difficulty:** ⭐⭐⭐ | **Time:** 2-4 hours

---

## 🎯 GOAL
Generate infinite city with Geometry Nodes: buildings, roads, props, traffic, LOD system

---

## 📋 PIPELINE (6 STAGES)

```
STAGE 1: City Grid & Zoning           → P29, P30
STAGE 2: Building Generator           → P29, P03
STAGE 3: Road Network & Traffic       → P30, P07
STAGE 4: Props & Vegetation Scatter   → P07, P37 (Poly Pizza)
STAGE 5: LOD & Optimization           → P06, P45
STAGE 6: Render & Compositing         → P13, P14, P15
```

---

## 🔧 MCP COMMANDS

### STAGE 1: CITY GRID (Geometry Nodes)
```bash
# Base Grid 10x10 blocks, 100x100м каждый
"GN: Grid 10x10, spacing 100м
Атрибут 'District': Random (0=Downtown, 1=Residential, 2=Industrial, 3=Park)
Атрибут 'Density': по District (Downtown=1.0, Res=0.6, Ind=0.8, Park=0.1)"
```

### STAGE 2: BUILDING GENERATOR (GN)
```bash
# Building Logic по District
"Downtown (0): Высота 50-200м, Glass/Concrete, Flat Roof + HVAC
Residential (1): Высота 10-50м, Brick/Plaster, Pitched Roof + Balconies
Industrial (2): Высота 5-20м, Metal/Concrete, Flat Roof + Vents
Park (3): Нет зданий, только скеттер деревьев/лавочек

# Building GN Tree:
1. Grid → Random Scale/Offset → Extrude (Height by District)
2. Window Array: фасад → Grid → Boolean/Inset → Glass Material
3. Roof Details: HVAC units, Antennas, Green Roof (Downtown)
4. LOD: Distance → Decimate (0.5 / 0.25 / 0.1)
5. Instancing: Collection → Random Pick → Realize Instances"
```

### STAGE 3: ROAD NETWORK & TRAFFIC
```bash
# Roads (Curve-based)
"GN: Curve Grid 11x11 (между блоками)
Road Width: Main=12м, Local=8м, Alley=4м
Sidewalks: 2м each side, Curb height 0.15м
Markings: Center line, Crosswalks, Lane dividers

# Traffic (GN Animation)
"Car Collection: 10 low-poly variants (Poly Pizza)
Path Follow: Roads → Resample → Points → Instance Cars
Speed: Random 30-60 км/ч, Loop на 500 фреймах
Traffic Lights: Procedural на перекрёстках (Red/Yellow/Green cycle)"
```

### STAGE 4: PROPS & VEGETATION
```bash
# Street Props (Poly Pizza + GN)
"Streetlights: каждые 20м по тротуарам, вариант 3 типа
Benches: в парках/у жилых, случайная ротация
Trash cans, Hydrants, Signs: Scatter по тротуарам (Density=0.05)
Trees: 5 видов (Poly Pizza), Scatter в парках/улицах
Grass/Flowers: Geometry Nodes на парках (Weight Paint для путей)"

# GN Scatter Setup
"Distribute Points on Faces → Poisson Disk → Density Attribute
Instance on Points → Random Pick from Collection → Random Rotation/Scale
Realize Instances → Merge by Distance"
```

### STAGE 5: LOD SYSTEM
```bash
# Distance-based LOD (GN)
"Attribute 'Distance' = length(Camera_Location - Position)
LOD0 (0-50м): Full Geo, 4k textures
LOD1 (50-200м): Decimate 0.5, 2k textures
LOD2 (200-500м): Decimate 0.25, 1k textures
LOD3 (500м+): Decimate 0.1, Billboard/Impostor

# Impostors для遠距離
"Render Billboard: 8 углов → Sprite Sheet → Shader: Billboard + Alpha"
```

### STAGE 6: RENDER
```bash
# Camera: Drone fly-through
"Path: Spiral Up 500м за 500 фреймов
DOF: Focus на центр города, f/4.0

# Lighting
"HDRI 'city_day' 4k strength=1.0
Sun: 5000W, angle 45°, shadows ON
Volumetric: Light fog density=0.01"

# Render
"Cycles 128 samples, Denoising, 4K
Viewport: 1/4 res для превью
Output: EXR + MP4 (60fps)"
```

---

## 📊 CITY SPECS

| Параметр | Значение |
|----------|----------|
| **Grid Size** | 10x10 блоков (1км²) |
| **Buildings** | 800-1200 инстансов |
| **Road Length** | ~50 км |
| **Props** | 50k-100k инстансов |
| **Trees** | 10k-20k |
| **Triangles (LOD0)** | 50-100M |
| **Draw Calls (GN)** | 1 (Instanced) |
| **VRAM** | 8-12GB (4K) |

---

## 🔗 LINKS

- **Prompts:** P03, P06, P07, P13, P14, P15, P29, P30, P37
- **Workflows:** [WF 05: Procedural Assets](../workflows/wf_05_procedural_assets.md), [WF 08: Batch](../workflows/wf_08_batch_processing.md)
- **Prompts Used:** P03, P06, P07, P13, P14, P15, P29, P30, P37

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| Collection Instancing в GN | Один Draw Call на тип здания |
| Distance Culling в GN | Не рендерить за камерой |
| Billboard Impostors > 500м | Огромная экономия VRAM |
| Seed = Frame для анимации | Детерминированный трафик |
| Weight Paint для путей | Реалистичная трава без путей |

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/cases/case_05_procedural_city.md` |
| Russian | `multilang/ru/cases/case_05_procedural_city.md` |