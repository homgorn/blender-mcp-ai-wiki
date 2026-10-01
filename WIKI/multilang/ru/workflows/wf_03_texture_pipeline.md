---
id: wf_03_texture_pipeline
lang: ru
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: template
---
# WF 03: TEXTURE PIPELINE

> Цель: ## 🌍 MULTILANG

**ID:** wf_03_texture_pipeline | **Lang:** ru | **Orig:** ru | **Category:** workflows | **Tags:** 

---

# WF 03: TEXTURE PIPELINE

**ID:** WF-03 | **Type:** PBR Texture Creation | **Difficulty:** ⭐⭐ | **Time:** 15-45 min per material

---

## 🎯 ЦЕЛЬ
Полный пайплайн создания production-ready PBR материалов: от генерации до экспорта

---

## 📋 ПАЙПЛАЙН СТАДИИ

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  SOURCE     │───▶│  GENERATE   │───▶│  REFINE     │───▶│  BAKE       │───▶│  EXPORT     │
│  (Reference/│    │  (AI/Proc/  │    │  (Seamless, │    │  (PBR Maps) │    │  (Multi-fmt)│
│  Photo)     │    │  Hand-paint)│    │  Tile, Color)│    │  (AO, Curv) │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🎨 ИСТОЧНИКИ ТЕКСТУР

| Источник | Качество | Скорость | Cost | Use Case |
|----------|----------|----------|------|----------|
| **Poly Haven** | ⭐⭐⭐⭐⭐ | Fast | Free | Production ready PBR |
| **Dream Textures (SD)** | ⭐⭐⭐⭐ | Med | Free (local) | Unique/custom |
| **Substance Designer** | ⭐⭐⭐⭐⭐ | Slow | $ | Procedural library |
| **Quixel/Megascans** | ⭐⭐⭐⭐⭐ | Fast | Free (UE) | Photorealistic |
| **Hand Paint (Blender)** | ⭐⭐⭐⭐ | Slow | Free | Artistic control |
| **Photo → AI (CSM/Meshy)** | ⭐⭐⭐⭐ | Fast | $ | Photo-to-PBR |

---

## 🔧 MCP КОМАНДЫ ПО СТАДИЯМ

### СТАДИЯ 1: POLY HAVEN (Готовые PBR)
```bash
# Поиск
"Найди на Poly Haven текстуру 'weathered concrete' категория 'ground' 2k"

# Скачивание + применение
"Скачай 'concrete_plaster_01' 2k с Poly Haven и присвой к объекту 'Wall'"

# Автопоиск по сцене
"Найди на Poly Haven текстуры для всех объектов в сцене: стены, пол, потолок"
```

### СТАДИЯ 2: DREAM TEXTURES (AI Генерация)
```bash
# Генерация с нуля
"Сгенерируй текстуру 'ancient stone wall, moss in cracks, seamless' 
Dream Textures: model=sd-2.1-base, size=1024, seamless=true"

# Texture Projection (на модель)
"Проектируй текстуру 'brick wall with moss' на выбранные грани стены
Model: stable-diffusion-2-depth, seamless=true"

# Inpainting (исправление швов)
"Замаскируй швы на текстуре стены и сделай Inpainting: 
'seamless continuation of stone texture'"

# Outpainting (расширение)
"Расширь текстуру пола на 2x с Outpainting: 
'continuation of wooden floor boards'"
```

### СТАДИЯ 3: PROCEDURAL (Node Groups)
```bash
# Создание нод-группы для металла
"Создай Node Group 'Procedural_Metal' с входами:
- BaseColor (Color)
- Roughness (Float 0-1)
- Anisotropy (Float 0-1)
- EdgeWear (Float 0-1)
Выход: PBR материалы"

# Использование
"Присвой Node Group 'Procedural_Metal' к объекту 'Sword' 
с параметрами: color=gold, roughness=0.1, anisotropy=0.8"
```

### СТАДИЯ 4: HAND PAINT (Texture Paint)
```bash
# Настройка слоев
"Настрой Texture Paint для 'Character_Body':
Layers: BaseColor, Roughness, Metallic, Normal, Height, Subsurface
Brushes: Draw, Soften, Smear, Clone, Fill, Mask
Resolution: 4k BaseColor, 2k остальные"

# Рисование
"Нарисуй на слое BaseColor: кожу с порами, веснушками
На слое Roughness: разную шероховатость (лицо/тело)
На слое Subsurface: слуховой проход, кончики пальцев"
```

### СТАДИЯ 5: BAKING (PBR Maps)
```bash
# Bake все карты с High Poly на Low Poly
"Выбери High Poly (Source) и Low Poly (Target)
Bake: BaseColor, Roughness, Normal, Metallic, AO, Curvature, Height
Resolution: 4k, Cage: 0.01, Margin: 16
Output: EXR 32-bit для Normal/Height, PNG 16-bit для остальных"

# AO Bake
"Bake Ambient Occlusion: 256 samples, Distance: 0.5m
Output: AO_4k.exr"

# Curvature Bake
"Bake Curvature: Convex/Concave
Output: Curvature_4k.exr (для Edge Wear масок)"
```

### СТАДИЯ 6: EXPORT (Multi-format)
```bash
# PBR Texture Sets
"Экспортируй все карты текстуры 'Brick_Wall' в папку //textures/Brick_Wall/:
Formats: PNG 16-bit (BaseColor, Roughness, Metallic, AO)
EXR 32-bit (Normal, Height, Curvature)
Naming: brick_basecolor_2k.png, brick_normal_2k.exr, etc."

# Substance Painter Export
"Экспорт проекта для Substance Painter:
Export → SBSAR (Substance Material) + текстуры"
```

---

## 📊 PBR MAP SPECIFICATIONS

| Map | Format | Color Space | Bit Depth | Compression | Use Case |
|-----|--------|-------------|-----------|-------------|----------|
| **Base Color** | PNG | sRGB | 16-bit | Lossless | Albedo |
| **Roughness** | PNG | Non-Color | 16-bit | Lossless | Microsurface |
| **Metallic** | PNG | Non-Color | 8-bit | Lossless | Metalness |
| **Normal** | EXR | Non-Color | 32-bit | ZIP | Surface detail |
| **Height/Displacement** | EXR | Non-Color | 32-bit | ZIP | Tessellation |
| **AO** | PNG | Non-Color | 16-bit | Lossless | Contact shadows |
| **Curvature** | EXR | Non-Color | 16-bit | ZIP | Edge wear masks |
| **Emission** | PNG | sRGB | 16-bit | Lossless | Self-illumination |
| **Opacity/Alpha** | PNG | Non-Color | 8-bit | Lossless | Transparency |

---

## 📐 RESOLUTION GUIDELINES

| Asset Type | Hero | Secondary | Background | Mobile/Web |
|------------|------|-----------|------------|------------|
| **Character** | 4k | 2k | 1k | 1k |
| **Prop (Hero)** | 4k | 2k | 1k | 1k |
| **Environment** | 4k | 2k | 2k | 1k |
| **Vehicle** | 4k | 2k | 1k | 1k |
| **UI/Icon** | 1k | 512 | 256 | 256 |

---

## 🔧 NAMING CONVENTION

```
{asset}_{map}_{resolution}.{ext}

Examples:
hero_basecolor_4k.png
hero_roughness_4k.png
hero_normal_4k.exr
hero_height_4k.exr
hero_ao_4k.png
hero_curvature_4k.exr
hero_metallic_4k.png
hero_emission_4k.png
hero_opacity_4k.png

Variants:
hero_basecolor_4k_v01.png
hero_basecolor_4k_dirty.png
hero_basecolor_4k_clean.png
```

---

## 🔧 SUBSTANCE DESIGNER INTEGRATION

```bash
# Export from Blender → Substance
"Export mesh as FBX with UVs for Substance Designer:
File → Export → FBX, Apply Transform, Selected Only"

# Import SBSAR into Blender
"Import Substance Material (.sbsar) into Blender:
Preferences → Add-ons → Import-Export: Import SBSAR
Shader Editor → Add → Group → Select .sbsar"
```

---

## 📦 VERSION CONTROL (Git LFS)

### .gitattributes
```gitattributes
*.png filter=lfs diff=lfs merge=lfs -text
*.exr filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.hdr filter=lfs diff=lfs merge=lfs -text
*.exr filter=lfs diff=lfs merge=lfs -text
*.glb filter=lfs diff=lfs merge=lfs -text
*.gltf filter=lfs diff=lfs merge=lfs -text
*.fbx filter=lfs diff=lfs merge=lfs -text
*.usd filter=lfs diff=lfs merge=lfs -text
*.usdz filter=lfs diff=lfs merge=lfs -text
*.sbsar filter=lfs diff=lfs merge=lfs -text
```

---

## 🔗 LINKS

- **Poly Haven:** https://polyhaven.com/
- **Dream Textures:** https://github.com/carson-katri/dream-textures
- **Substance Designer:** https://www.adobe.com/products/substance3d-designer.html
- **Setup 03:** [Dream Textures](../setups/setup_03_dream_textures.md)
- **Setup 08:** [Asset Pipeline](../setups/setup_08_asset_pipeline.md)
- **Next:** [WF 04: Character Animation](../workflows/wf_04_character_animation.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/workflows/wf_03_texture_pipeline.md` |
| Russian | `multilang/ru/workflows/wf_03_texture_pipeline.md` |