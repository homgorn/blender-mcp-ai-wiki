---
id: 11_procedural_textures
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P11: PROCEDURAL TEXTURES

> Цель: ## 🌍 MULTILANG

**ID:** 11_procedural_textures | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, math, math-nodes, musgrave, noise, procedural, textures, voronoi

---

# P11: PROCEDURAL TEXTURES

**ID:** P11 | **Cluster:** Materials PBR | **Difficulty:** ⭐⭐ | **Tags:** #procedural #noise #voronoi #musgrave #math-nodes #textures

---

## 🎯 GOAL
Create fully procedural PBR textures using only math and noise nodes - no image files needed

---

## 📝 PROMPT (RUS)

```
Создай процедуруальную текстуру "[MATERIAL_TYPE]" используя только математические ноды:
База: NOISE / VORONOI / MUSGRAVE / WAVE / MAGIC / BRICK / CHECKER / GRADIENT
Модификаторы: MAPPING, COLOR_RAMP, MATH, VECTOR_MATH, MIX_RGB
Выходы: Base Color, Roughness, Normal, Height, Metallic
```

---

## 📝 PROMPT (ENG)

```
Create procedural texture "[MATERIAL_TYPE]" using only math nodes:
Base: NOISE / VORONOI / MUSGRAVE / WAVE / MAGIC / BRICK / CHECKER / GRADIENT
Modifiers: MAPPING, COLOR_RAMP, MATH, VECTOR_MATH, MIX_RGB
Outputs: Base Color, Roughness, Normal, Height, Metallic
```

---

## 🔧 MCP: `execute_blender_code`

### UNIVERSAL PROCEDURAL BUILDER
```python
import bpy

def create_procedural_material(name, texture_type, params):
    """
    texture_type: 'METAL', 'WOOD', 'STONE', 'FABRIC', 'CONCRETE', 'PLASTIC', 'RUST', 'SNOW'
    params: dict с параметрами
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Principled BSDF
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Texture Coordinate + Mapping
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # === GENERATORS ===
    
    def add_noise(scale=50, detail=4, roughness=0.5, distortion=0):
        n = nodes.new('ShaderNodeTexNoise')
        n.noise_dimensions = '3D'
        n.noise_type = 'FBM'
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = roughness
        n.inputs['Distortion'].default_value = distortion
        n.location = (-200, 200)
        return n
    
    def add_voronoi(scale=50, feature='SMOOTH_F1', metric='MANHATTAN'):
        v = nodes.new('ShaderNodeTexVoronoi')
        v.voronoi_dimensions = '3D'
        v.feature = feature
        v.metric = metric
        v.inputs['Scale'].default_value = scale
        v.location = (-200, 0)
        return v
    
    def add_musgrave(scale=50, detail=4, dimension=2, lacunarity=2, octaves=4):
        m = nodes.new('ShaderNodeTexMusgrave')
        m.musgrave_dimensions = '3D'
        m.musgrave_type = 'MULTIFRACTAL'
        m.inputs['Scale'].default_value = scale
        m.inputs['Detail'].default_value = detail
        m.inputs['Dimension'].default_value = dimension
        m.inputs['Lacunarity'].default_value = lacunarity
        m.inputs['Octaves'].default_value = octaves
        m.location = (-200, -200)
        return m
    
    def add_ramp(colors, positions, interpolation='LINEAR'):
        """colors: [(pos, (r,g,b,a)), ...]"""
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = interpolation
        ramp.location = (0, 0)
        for i, (pos, col) in enumerate(zip(positions, colors)):
            if i < 2:
                ramp.color_ramp.elements[i].position = pos
                ramp.color_ramp.elements[i].color = col
            else:
                elem = ramp.color_ramp.elements.new(pos)
                elem.color = col
        return ramp
    
    def add_math(op, val=0.5):
        m = nodes.new('ShaderNodeMath')
        m.operation = op
        if op not in ['SINE', 'COSINE', 'TANGENT']:
            m.inputs[1].default_value = val
        m.location = (0, -200)
        return m
    
    # === MATERIAL RECIPES ===
    
    if texture_type == 'METAL':
        # Шум для микропотертостей
        noise = add_noise(scale=200, detail=8, roughness=0.7)
        ramp = add_ramp([
            (0.3, (0.02, 0.02, 0.02, 1)),
            (0.7, (0.05, 0.05, 0.05, 1)),
        ])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        links.new(noise.outputs['Fac'], principled.inputs['Roughness'])
        
        principled.inputs['Base Color'].default_value = params.get('color', (0.8, 0.7, 0.6, 1))
        principled.inputs['Metallic'].default_value = 1.0
        principled.inputs['Roughness'].default_value = 0.1
        
    elif texture_type == 'WOOD':
        # Мусклгрейв для волокон
        musg = add_musgrave(scale=params.get('scale', 20), detail=8)
        musg.musgrave_type = 'RIDGED_MULTIFRACTAL'
        
        ramp = add_ramp([
            (0.0, (0.15, 0.08, 0.03, 1)),
            (0.3, (0.25, 0.15, 0.07, 1)),
            (0.6, (0.35, 0.2, 0.1, 1)),
            (1.0, (0.45, 0.3, 0.15, 1)),
        ], positions=[0.0, 0.3, 0.6, 1.0])
        
        links.new(mapping.outputs['Vector'], musg.inputs['Vector'])
        links.new(musg.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], principled.inputs['Base Color'])
        
        # Roughness по волокнам
        ramp2 = add_ramp([(0.0, (0.6,)), (1.0, (0.3,))])
        links.new(musg.outputs['Fac'], ramp2.inputs['Fac'])
        links.new(ramp2.outputs['Color'], principled.inputs['Roughness'])
        
        principled.inputs['Metallic'].default_value = 0.0
        
    elif texture_type == 'STONE':
        voronoi = add_voronoi(scale=params.get('scale', 30), feature='SMOOTH_F1')
        noise = add_noise(scale=100, detail=4)
        
        # Комбинировать
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.location = (0, 200)
        links.new(voronoi.outputs['Distance'], mix.inputs[1])
        links.new(noise.outputs['Fac'], mix.inputs[2])
        mix.inputs[0].default_value = 0.5
        
        ramp = add_ramp([
            (0.0, (0.3, 0.3, 0.3, 1)),
            (0.5, (0.4, 0.35, 0.3, 1)),
            (1.0, (0.5, 0.45, 0.4, 1)),
        ])
        links.new(mix.outputs['Color'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], principled.inputs['Base Color'])
        
        # Roughness
        ramp2 = add_ramp([(0.0, (0.9,)), (1.0, (0.5,))])
        links.new(noise.outputs['Fac'], ramp2.inputs['Fac'])
        links.new(ramp2.outputs['Color'], principled.inputs['Roughness'])
        
        principled.inputs['Metallic'].default_value = 0.0
        
    elif texture_type == 'CONCRETE':
        # Смесь шума и ворона
        noise1 = add_noise(scale=80, detail=6, roughness=0.6)
        noise2 = add_noise(scale=200, detail=3, roughness=0.3)
        voronoi = add_voronoi(scale=15, feature='F1')
        
        # Композиция
        mix1 = nodes.new('ShaderNodeMixRGB')
        mix1.blend_type = 'OVERLAY'
        mix1.location = (0, 200)
        links.new(noise1.outputs['Fac'], mix1.inputs[1])
        links.new(noise2.outputs['Fac'], mix1.inputs[2])
        
        mix2 = nodes.new('ShaderNodeMixRGB')
        mix2.blend_type = 'MULTIPLY'
        mix2.location = (200, 0)
        links.new(mix1.outputs['Color'], mix2.inputs[1])
        links.new(voronoi.outputs['Distance'], mix2.inputs[2])
        
        ramp = add_ramp([
            (0.0, (0.4, 0.4, 0.4, 1)),
            (0.5, (0.5, 0.5, 0.5, 1)),
            (1.0, (0.6, 0.6, 0.6, 1)),
        ])
        links.new(mix2.outputs['Color'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], principled.inputs['Base Color'])
        
        principled.inputs['Roughness'].default_value = 0.8
        principled.inputs['Metallic'].default_value = 0.0
        
    elif texture_type == 'FABRIC':
        # Ткань: волны + шум
        wave = nodes.new('ShaderNodeTexWave')
        wave.wave_type = 'SINE'
        wave.inputs['Scale'].default_value = 50
        wave.inputs['Distortion'].default_value = 2.0
        wave.location = (-200, 200)
        
        noise = add_noise(scale=200, detail=4)
        
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'ADD'
        mix.location = (0, 200)
        links.new(wave.outputs['Color'], mix.inputs[1])
        links.new(noise.outputs['Color'], mix.inputs[2])
        
        ramp = add_ramp([
            (0.0, params.get('color_dark', (0.1, 0.1, 0.3, 1))),
            (1.0, params.get('color_light', (0.3, 0.3, 0.5, 1))),
        ])
        links.new(mix.outputs['Color'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], principled.inputs['Base Color'])
        
        # Sheen для ткани
        principled.inputs['Sheen Weight'].default_value = 0.3
        principled.inputs['Sheen Roughness'].default_value = 0.5
        
    elif texture_type == 'RUST':
        # База металл + ржавчина сверху
        noise = add_noise(scale=50, detail=6)
        voronoi = add_voronoi(scale=30, feature='SMOOTH_F1')
        
        # Маска ржавчины
        mix_mask = nodes.new('ShaderNodeMixRGB')
        mix_mask.blend_type = 'MULTIPLY'
        links.new(noise.outputs['Fac'], mix_mask.inputs[1])
        links.new(voronoi.outputs['Distance'], mix_mask.inputs[2])
        
        ramp_rust = add_ramp([
            (0.3, (0, 0, 0, 0)),
            (0.5, (0.5, 0.15, 0.05, 0.5)),
            (0.8, (0.6, 0.2, 0.05, 1)),
        ])
        links.new(mix_mask.outputs['Color'], ramp_rust.inputs['Fac'])
        
        # Mix с базовым металлом
        base_color = params.get('base_color', (0.6, 0.55, 0.5, 1))
        rust_color = params.get('rust_color', (0.6, 0.2, 0.05, 1))
        
        mix_final = nodes.new('ShaderNodeMixRGB')
        mix_final.blend_type = 'MIX'
        links.new(ramp_rust.outputs['Color'], mix_final.inputs['Fac'])
        mix_final.inputs[1].default_value = base_color + (1,)
        mix_final.inputs[2].default_value = rust_color + (1,)
        links.new(mix_final.outputs['Color'], principled.inputs['Base Color'])
        
        principled.inputs['Metallic'].default_value = 0.8
        principled.inputs['Roughness'].default_value = 0.6
    
    # Normal Map из Height (Bump)
    bump = nodes.new('ShaderNodeBump')
    bump.location = (200, -200)
    links.new(principled.inputs['Base Color'].links[0].from_node.outputs['Color'] if principled.inputs['Base Color'].links else noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    
    return mat

# === USAGE ===
create_procedural_material("Proc_Metal_Gold", "METAL", {'color': (1.0, 0.84, 0.0, 1)})
create_procedural_material("Proc_Wood_Oak", "WOOD", {'scale': 15})
create_procedural_material("Proc_Stone_Granite", "STONE", {'scale': 25})
create_procedural_material("Proc_Concrete_Raw", "CONCRETE", {})
create_procedural_material("Proc_Fabric_Denim", "FABRIC", {'color_dark': (0.05, 0.05, 0.3, 1), 'color_light': (0.2, 0.2, 0.4, 1)})
create_procedural_material("Proc_Rusted_Iron", "RUST", {'base_color': (0.5, 0.45, 0.4, 1), 'rust_color': (0.6, 0.2, 0.05, 1)})
```

---

## 📊 GENERATOR REFERENCE

| Генератор | Лучше для | Ключевые параметры |
|-----------|-----------|-------------------|
| **Noise** | Органика, микродитали | Scale, Detail, Roughness, Distortion |
| **Voronoi** | Ячейки, трещины, камни | Feature (F1/F2/Smooth), Metric, Scale |
| **Musgrave** | Фракталы, рифы, кора | Type (fBm, Ridged, Hybrid), Dimension |
| **Wave** | Волны, ткань, дюны | Type (Sine/Saw/Tri), Distortion |
| **Magic** | Абстрактные паттерны | Depth, Turbulence |
| **Brick** | Кирпичи, плитка | Brick Width, Row Height, Mortar |
| **Checker** | Плитка, шахматы | Scale |

---

## 💡 COMBINATION PATTERNS

| Паттерн | Ноды | Результат |
|---------|------|-----------|
| **Noise + ColorRamp** | Noise → Ramp | Контролируемые переходы |
| **Voronoi + Noise** | Voronoi Distance × Noise | Естественные трещины |
| **Musgrave × Noise** | Musgrave × Noise | Фрактальная детализация |
| **Wave + Noise** | Wave + Noise | Ткань с шумом |
| **Voronoi × Voronoi** | Разные Scale | Многослойные ячейки |

---

## 🔗 LINKS

- **Prompts:** [P09 Principled BSDF](./09_principled_bsdf.md), [P10 Node Groups](./10_node_groups.md)
- **Workflows:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **Cases:** [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **Next:** [P12: Texture Painting](./12_texture_painting.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/materials/11_procedural_textures.md` |
| Russian | `multilang/ru/materials/11_procedural_textures.md` |