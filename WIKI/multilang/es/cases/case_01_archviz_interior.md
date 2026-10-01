---
id: case_01_archviz_interior
lang: es
orig_lang: ru
category: cases
type: case
difficulty: 3
translation: template
---
# КЕЙС 01: ARCHVIZ INTERIOR

> Objetivo: 

**ID:** case_01_archviz_interior | **Lang:** es | **Orig:** ru | **Category:** cases | **Tags:** **, 1a1a1a, 8b6914, 8b7355, e8e0d0, f5f0e8

## Cómo usar
Esta es la versión en español de 'case_01_archviz_interior'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
case_01_archviz_interior / cases / **, 1a1a1a, 8b6914, 8b7355, e8e0d0, f5f0e8
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: case_01_archviz_interior
lang: ru
orig_lang: en
category: cases
type: case
difficulty: 3
---

# КЕЙС 01: ARCHVIZ INTERIOR

> Цель: ## 🌍 MULTILANG

**ID:** case_01_archviz_interior | **Lang:** ru | **Orig:** en | **Category:** cases | **Tags:** 1a1a1a, 8b6914, 8b7355, e8e0d0, f5f0e8

---

# CASE 01: ARCHVIZ INTERIOR

**ID:** CASE-01 | **Type:** Architectural Visualization | **Difficulty:** ⭐⭐⭐ | **Time:** 2-4 hours

---

## 🎯 GOAL
Create photorealistic interior render: modeling, materials, lighting, camera, compositing

---

## 📋 PIPELINE OVERVIEW (8 STAGES)

```
STAGE 1: Room Shell          → P01, P02, P03
STAGE 2: Windows/Doors       → P02 (Boolean)
STAGE 3: Furniture/Props     → P01, P07, P37 (Poly Pizza)
STAGE 4: Materials           → P09, P11, P12
STAGE 5: Lighting            → P13 (HDRI + Studio)
STAGE 6: Camera              → P14
STAGE 7: Render Settings     → P15
STAGE 8: Compositing         → P15
```

---

## 🔧 MCP COMMANDS BY STAGE

### STAGE 1: ROOM SHELL (10x8x3m)
```bash
# Floor
"Создай плоскость 'Floor' 10x8м в (0,0,0) материал 'Mat_Floor_Parquet'"

# Walls (4 шт.)
"Создай куб 'Wall_North' 10x0.2x3м в (0, -4, 1.5)"
"Создай куб 'Wall_South' 10x0.2x3м в (0, 4, 1.5)"
"Создай куб 'Wall_East' 0.2x8x3м в (5, 0, 1.5)"
"Создай куб 'Wall_West' 0.2x8x3м в (-5, 0, 1.5)"

# Ceiling
"Создай плоскость 'Ceiling' 10x8м в (0,0,3) материал 'Mat_Ceiling_White'"
```

### STAGE 2: WINDOWS & DOORS (Boolean)
```bash
# Large window (North wall, centered)
"Создай куб 'Window_Cut' 3x0.3x2м в (0, -4.1, 1.5)
Вычти Window_Cut из Wall_North (DIFFERENCE)"

# Door (South wall)
"Создай куб 'Door_Cut' 1x0.3x2.2м в (-1, 4.1, 1.1)
Вычти Door_Cut из Wall_South (DIFFERENCE)

# Window frame (отдельный объект)
"Создай куб 'Window_Frame' 3.1x0.05x2.1м в (0, -4.1, 1.5) материал 'Mat_Wood_White'"
```

### STAGE 3: FURNITURE (Poly Pizza + Primitives)
```bash
# Sofa (Poly Pizza)
"Найди на Poly Pizza 'sofa' лицензия CC0, скачай, normalize_size=true, target_size=2.0
Позиция: (0, -2, 0)"

# Coffee Table
"Создай куб 'Table_Top' 1.2x0.6x0.05м в (0, -1, 0.45) материал 'Mat_Wood_Oak'
Создай 4 ножки: цилиндр 0.05x0.4м в углах стола"

# Armchairs (2 шт.)
"Найди на Poly Pizza 'armchair' CC0, скачай 2 шт., target_size=0.9
Позиции: (-1.5, -2.5, 0) и (1.5, -2.5, 0)"

# Floor Lamp
"Создай цилиндр 'Lamp_Base' 0.3x0.05м в (2, -3, 0) материал 'Mat_Metal_Black'
Создай цилиндр 'Lamp_Stand' 0.02x1.5м в (2, -3, 0.025) материал 'Mat_Metal_Black'
Создай сферу 'Lamp_Shade' 0.4м в (2, -3, 1.55) материал 'Mat_Fabric_Linen'
Добавь точечный свет в центр шейда, энергия 200W, цвет warm"
```

### STAGE 4: MATERIALS (PBR)
```bash
# Parquet Floor
"Создай материал 'Mat_Floor_Parquet':
BaseColor: #8B7355, Roughness: 0.6, Metallic: 0
Normal: procedural wood grain, Height: subtle"

# Walls - Plaster
"Создай материал 'Mat_Wall_Plaster':
BaseColor: #F5F0E8, Roughness: 0.85, Metallic: 0
Normal: subtle stucco texture"

# Window Glass
"Создай материал 'Mat_Glass_Clear':
Transmission: 1.0, IOR: 1.45, Roughness: 0
BaseColor: white, Alpha: 0.9"

# Wood (Furniture)
"Создай материал 'Mat_Wood_Oak':
BaseColor: #8B6914, Roughness: 0.4, Metallic: 0
Normal: wood grain, Clearcoat: 0.2"

# Metal (Lamp, Hardware)
"Создай материал 'Mat_Metal_Black':
BaseColor: #1A1A1A, Roughness: 0.2, Metallic: 1.0
Clearcoat: 0.1"

# Fabric (Sofa, Lamp Shade)
"Создай материал 'Mat_Fabric_Linen':
BaseColor: #E8E0D0, Roughness: 0.9, Metallic: 0
Sheen: 0.3, SheenTint: 0.5, Normal: fabric weave"
```

### STAGE 5: LIGHTING (HDRI + Studio)
```bash
# HDRI Environment
"Найди на Poly Haven HDRI 'studio' категория 'indoor' 2k
Скачай и поставь как World, strength=0.4"

# Studio Lights (3-point)
"Создай AREA свет 'Key_Light' 1000W в (3, -3, 4) размер 2x2м поворот к центру
Создай AREA свет 'Fill_Light' 300W в (-3, 2, 2) размер 3x3м
Создай AREA свет 'Rim_Light' 500W в (-2, -2, 4) размер 1.5x1.5м"

# Accent lights
"Добавь точечный свет в торшере 200W warm
Добавь полоску LED под диваном 50W warm"
```

### STAGE 6: CAMERA
```bash
# Main Camera
"Создай камеру 'Cam_Main' в (7, -6, 1.6) цель (0,0,1) focal=35mm sensor=36mm
DOF: focus на диван, f-stop=2.8
Composition: Rule of Thirds"

# Additional cameras
"Cam_Wide: (-10, -8, 1.5) focal=24mm
Cam_Detail: (-1, -1, 1) focal=85mm f/1.8"
```

### STAGE 7: RENDER SETTINGS
```bash
"Cycles: 256 samples, denoising ON (OPTIX), adaptive sampling
Resolution: 3840x2160 (4K) или 1920x1080
Color Management: Filmic, Look: Medium High Contrast
Output: EXR MultiLayer 32-bit + PNG 16-bit"
```

### STAGE 8: COMPOSITING
```bash
"Enable passes: Combined, Depth, Normal, AO, Mist, Cryptomatte
Compositor: Color Balance (lift/gamma/gain), Glare (fog glow 0.2), 
Vignette (0.15), Color Matrix (teal-orange), Film Grain (0.02)
Output: EXR 32-bit MultiLayer + PNG 16-bit"
```

---

## 📊 QUALITY CHECKLIST

| Категория | Target | Critical |
|-----------|--------|----------|
| **Triangles** | < 500k | < 1M |
| **Materials** | 10-20 unique | < 30 |
| **Texture Resolution** | 2k-4k | 1k min |
| **HDRI Resolution** | 2k-4k | 1k |
| **Samples** | 256-512 | 128 |
| **Render Time (RTX 3080)** | 5-15 min | 30 min |
| **VRAM Usage** | < 8GB | < 10GB |

---

## 🔗 LINKS

- **Prompts Used:** P01-P03, P07, P09, P11-P15
- **Setups:** [Setup 01: blender-mcp](../setups/setup_01_blender_mcp_basic.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md), [WF 06: ArchViz](../workflows/wf_06_archviz_workflow.md)
- **Prompts:** P01, P02, P03, P07, P09, P11, P12, P13, P14, P15

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| Используй Collection для организации | Легко скрывать/показывать этажи/комнаты |
| Light Linking в Cycles | Контроль отражений в окнах |
| Render Region (Ctrl+B) | Быстрый предпросмотр участков |
| Save versions каждые 30 мин | `File > Save As > v001, v002...` |
| Denoising + 256 samples = Production | Баланс скорость/качество |

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/cases/case_01_archviz_interior.md` |
| Russian | `multilang/ru/cases/case_01_archviz_interior.md` |