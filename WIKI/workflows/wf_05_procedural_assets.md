---
id: wf_05_procedural_assets
lang: ru
category: workflows
status: full
tags: [geometry-nodes, modeling, pipeline, vegetation, workflow]
---
# WF 05: PROCEDURAL ASSETS

**ID:** WF-05 | **Type:** Procedural Generation (Geometry Nodes) | **Difficulty:** ⭐⭐⭐ | **Time:** 30-90 min per asset

---

## 🎯 ЦЕЛЬ
Создание бесконечных вариаций ассетов через Geometry Nodes: здания, растительность, реквизит, ландшафт

---

## 📋 ПАЙПЛАЙН СТАДИИ

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  PARAMETERS │───▶│  GENERATE   │───▶│  VARIATE    │───▶│  LOD        │───▶│  EXPORT     │
│  (Seed,     │    │  (GN Tree)  │    │  (Seed,     │    │  (Distance  │    │  (Collection│
│  Style,     │    │  Geometry   │    │  Attr,      │    │  Culling,   │    │  Instancing)│
│  Constraints)│    │  Nodes)     │    │  Noise)     │    │  Decimate)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🌲 АССЕТ ТИПЫ И GN ТРЕЕ

### 1. PROCEDURAL BUILDING (Building Generator)
```python
# GN Tree: Building_Generator
# Inputs:
# - Seed (Integer)
# - Width, Depth, Height (Float)
# - Floors (Integer)
# - Style: "modern" | "classical" | "industrial" | "sci-fi"
# - Window_Density (0-1)
# - Roof_Type: "flat" | "pitched" | "dome" | "green"

# Logic:
# 1. Base Box → Extrude by Floors
# 2. Facade Grid → Window Boolean/Array
# 3. Roof Generator by Type
# 4. Details: Balconies, HVAC, Antennas, Signage
# 5. Material Assignment by Vertex Group
# 6. LOD: Distance → Decimate (0.5 / 0.25 / 0.1)
# 7. Collection Instancing → Realize Instances
```

### 2. ROAD NETWORK
```python
# GN Tree: Road_Network
# Inputs:
# - Curve Grid (Base)
# - Road_Width: Main=12m, Local=8m, Alley=4m
# - Sidewalk_Width: 2m
# - Curb_Height: 0.15m
# - Markings: Center, Crosswalk, Lanes
# - Streetlights: Spacing=20m, Variants=3

# Traffic Animation:
# Car Collection (10 variants) → Path Follow → Speed 30-60 km/h
# Traffic Lights: Procedural Red/Yellow/Green cycle
```

### 3. VEGETATION SCATTER
```python
# GN Tree: Vegetation_Scatter
# Inputs:
# - Target Mesh (Terrain)
# - Collections: Trees_Large, Trees_Small, Bushes, Grass, Flowers
# - Density_Attribute (Weight Paint / Noise)
# - Scale_Range: (0.8, 1.2)
# - Rotation_Random: True
# - Align_To_Normal: True
# - Distance_Culling: Camera_Distance > 500m → Hide

# Biome System:
# - Forest: Trees_Large (Density 0.01) + Bushes (0.05) + Grass (0.5)
# - Park: Trees_Small (0.02) + Benches (0.01) + Flowers (0.3)
# - Urban: Streetlights (0.02) + Planters (0.01)
```

### 4. PROP VARIATIONS (Fence, Crates, Barrels)
```python
# GN Tree: Prop_Variations
# Inputs:
# - Source Collection (Base Props)
# - Count (Integer)
# - Scale_Range: (0.8, 1.3)
# - Rotation_Random: True
# - Position_Jitter: 0.1m
# - Material_Variation: Random UV Offset / Color Ramp

# LOD System:
# Distance < 10m: Full Geo + 4k Textures
# 10-50m: Decimate 0.5 + 2k Textures
# 50-200m: Decimate 0.25 + 1k Textures
# >200m: Billboard Impostor (8 angles)
```

---

## 🔧 GN НОДЫ РЕФЕРЕНС

### Core Nodes
| Node | Purpose | Key Settings |
|------|---------|--------------|
| **Distribute Points on Faces** | Рассеяние по поверхности | Poisson Disk, Density Attribute |
| **Distribute Points in Volume** | Объемное рассеяние | Density, Seed |
| **Instance on Points** | Инстансинг коллекций | Pick Instance, Scale, Rotation |
| **Collection Info** | Доступ к коллекции | Separate Children, Reset Children |
| **Realize Instances** | Конвертация в геометрию | Делает инстансы редактируемыми |

### Geometry Processing
| Node | Purpose |
|------|---------|
| **Mesh Boolean** | Union/Difference/Intersect |
| **Mesh to Points** | Конвертация в поинты |
| **Points to Curves** | Линии из точек |
| **Curve to Mesh** | Толщина линий |
| **Resample Curve** | Уравнивание точек |
| **Trim Curve** | Обрезка по фактору |

### Attributes
| Node | Purpose |
|------|---------|
| **Store Named Attribute** | Сохранить кастомные данные |
| **Named Attribute** | Чтение атрибутов |
| **Random Value** | Случайные числа/вектора |
| **Attribute Statistic** | Min/Max/Mean/Angle |
| **Attribute Transfer** | Передача между геометриями |

### Math/Logic
| Node | Purpose |
|------|---------|
| **Math** | Базовая математика |
| **Vector Math** | Векторные операции |
| **Compare** | Сравнения (Greater/Less/Equal) |
| **Boolean Math** | AND/OR/NOT |
| **Switch** | Переключение по условию |
| **Index Switch** | Множественный выбор |

---

## 🎨 СТИЛИЗАЦИЯ (Style System)

### Building Styles (GN Input)
```python
STYLES = {
    "modern": {
        "materials": ["glass", "concrete", "metal_panel"],
        "window_ratio": 0.7,
        "roof_type": "flat",
        "details": ["hvac", "glass_railing", "sunshade"]
    },
    "classical": {
        "materials": ["brick", "stone", "wood_trim"],
        "window_ratio": 0.4,
        "roof_type": "pitched",
        "details": ["cornice", "balcony", "pilaster"]
    },
    "industrial": {
        "materials": ["corrugated_metal", "concrete", "rusted_metal"],
        "window_ratio": 0.2,
        "roof_type": "flat",
        "details": ["vents", "pipes", "loading_dock"]
    },
    "sci_fi": {
        "materials": ["metal_panel", "glass", "glowing_trim"],
        "window_ratio": 0.5,
        "roof_type": "dome",
        "details": ["antenna", "hologram", "force_field"]
    }
}
```

---

## 🎮 LOD SYSTEM (GN Implementation)

```python
# Distance-based LOD в GN
# Attribute "Distance" = length(Camera_Location - Position)

# LOD Switch Node:
# Distance < 50m:    LOD0 (Full Geo, 4k textures)
# 50-200m:          LOD1 (Decimate 0.5, 2k textures)
# 200-500m:         LOD2 (Decimate 0.25, 1k textures)
# 500m+:            LOD3 (Billboard Impostor)

# Impostor Generation (Pre-bake):
# 1. Render 8 views (45° steps) → Sprite Sheet
# 2. Shader: Billboard + Alpha + View Angle → Sprite Index
```

---

## 📦 EXPORT PIPELINE

### Collection Instancing (Performance)
```python
# Правило: 1 Draw Call на тип ассета
# GN Tree Output → Collection Instancing
# Blender автоматически батчит инстансы

# Export для Game Engines:
# 1. GN → Realize Instances → Apply Modifiers
# 2. Separate by Material → Export Collections
# 3. FBX/GLTF per Collection
# 4. LODs как отдельные меши с суффиксами _LOD0, _LOD1
```

---

## 🔧 MCP КОМАНДЫ ДЛЯ PROCEDURAL

### Building Generation
```bash
"Создай процедурный квартал 10x10 блоков:
- Grid 10x10, spacing 100м
- District Attribute: Random (0=Downtown, 1=Residential, 2=Industrial, 3=Park)
- Building Generator: Height by District, Style by District
- Road Network: Curves between blocks, Sidewalks 2m
- Props Scatter: Streetlights (20m), Trees (Parks), Benches
- LOD: Distance Culling + Decimate
- Output: Collection Instancing для рендера / FBX per Building для экспорта"
```

### Vegetation Scatter
```bash
"Рассей биом 'Forest' на Terrain:
- Collection: Trees_Large (Density 0.01, Scale 0.8-1.2)
- Collection: Bushes (Density 0.05, Scale 0.5-1.0)
- Collection: Grass (Density 0.5, Scale 0.1-0.3)
- Weight Paint Density Attribute для путей/полян
- LOD: Distance > 200m → Billboard Impostors
- Wind Animation: Vertex Offset by Noise(Position + Time)"
```

### Road Network
```bash
"Создай дорожную сеть из Curve Grid:
- Main Roads: 12m, 2 lanes + 2m sidewalks
- Local Roads: 8m, 1 lane + 1.5m sidewalks
- Markings: Center line, Crosswalks, Stop lines
- Traffic Lights: Procedural на перекрестках (Cycle 60s)
- Streetlights: Every 20m, 3 variants
- Cars: Path Follow curves, 10 variants, Speed 30-60 km/h"
```

---

## 📊 PERFORMANCE TIPS

| Technique | Impact | When to Use |
|-----------|--------|-------------|
| **Collection Instancing** | -90% Draw Calls | Всегда для повторяющихся объектов |
| **Distance Culling** | -50% Tris | Большие сцены |
| **Decimate Modifier (GN)** | -75% Tris | LOD1/LOD2 |
| **Billboard Impostors** | -99% Tris | >500m Distance |
| **Texture Atlasing** | -Draw Calls | Много маленьких текстур |
| **Instance Scale/Align in GN** | -CPU | Вместо Object Constraints |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md), [WF 12: CROWD SIM GN](wf_12_crowd_sim_gn.md)
- **По темам:** [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [P22: PARTICLE SYSTEMS](../prompts/22_particles.md), [P07: INSTANCING & ARRAYS](../prompts/07_instancing_arrays.md), [P23: GEOMETRY NODES BASICS](../prompts/23_geometry_nodes_basics.md)
- **Теги:** #geometry-nodes, #modeling, #pipeline, #vegetation, #workflow

