---
id: 13_lighting_hdri
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P13: ILUMINACIÓN & HDRI

> Objetivo: 

**ID:** 13_lighting_hdri | **Lang:** es | **Orig:** ru | **Category:** prompts | **Tags:** **, hdri, ibl, lighting, polyhaven, studio, volumetric

## Cómo usar
Esta es la versión en español de '13_lighting_hdri'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
13_lighting_hdri / prompts / **, hdri, ibl, lighting, polyhaven, studio, volumetric
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: 13_lighting_hdri
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 2
---

# P13: LIGHTING & HDRI

> Цель: ## 🌍 MULTILANG

**ID:** 13_lighting_hdri | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, hdri, ibl, lighting, polyhaven, studio, volumetric

---

# P13: LIGHTING & HDRI

**ID:** P13 | **Cluster:** Lighting | **Difficulty:** ⭐⭐ | **Tags:** #lighting #hdri #polyhaven #ibl #studio #volumetric

---

## 🎯 GOAL
Setup professional lighting using HDRI, studio lights, and volumetric effects

---

## 📝 PROMPT (RUS)

```
Настрой освещение для сцены "[SCENE_NAME]":
Тип: HDRI / STUDIO / VOLUMETRIC / MIXED
HDRI: [Poly Haven ID] / [путь к файлу] разрешение [1k/2k/4k]
Studio: 3-point / 4-point / Ring / Area lights
Volumetric: Fog / God Rays / Dust
```

---

## 📝 PROMPT (ENG)

```
Setup lighting for scene "[SCENE_NAME]":
Type: HDRI / STUDIO / VOLUMETRIC / MIXED
HDRI: [Poly Haven ID] / [file path] resolution [1k/2k/4k]
Studio: 3-point / 4-point / Ring / Area lights
Volumetric: Fog / God Rays / Dust
```

---

## 🔧 MCP: `execute_blender_code`

### HDRI WORLD (Poly Haven)
```python
import bpy

# Через MCP: download_polyhaven_asset
# Или напрямую:
def setup_hdri_world(hdri_path, strength=1.0, rotation=0.0):
    world = bpy.data.worlds.new("World_HDRI")
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    # Background
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = strength
    
    # Environment Texture
    env = nodes.new('ShaderNodeTexEnvironment')
    env.location = (-400, 0)
    env.image = bpy.data.images.load(hdri_path)
    env.projection = 'EQUIRECTANGULAR'
    
    # Mapping для вращения
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Rotation'].default_value[2] = rotation
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env.inputs['Vector'])
    links.new(env.outputs['Color'], bg.inputs['Color'])
    
    # Output
    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (200, 0)
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    
    bpy.context.scene.world = world
    return world

# Poly Haven HDRI через MCP
# download_polyhaven_asset("abandoned_bakery", "hdris", "2k")
# setup_hdri_world("//polyhaven/abandoned_bakery_2k.hdr", strength=1.2, rotation=0.785)
```

### 3-POINT STUDIO LIGHTING
```python
def setup_3point_lighting(target_obj, key_energy=1000, fill_energy=300, rim_energy=500):
    """Классическое 3-точечное освещение"""
    target_loc = target_obj.location if target_obj else (0, 0, 0)
    
    # KEY LIGHT (основной, 45° сторона, 45° вверх)
    key = bpy.data.lights.new("Key_Light", 'AREA')
    key_obj = bpy.data.objects.new("Key_Light", key)
    bpy.context.collection.objects.link(key_obj)
    key.energy = key_energy
    key.size = 2.0
    key.size_y = 2.0
    key_obj.location = (target_loc[0] + 4, target_loc[1] - 4, target_loc[2] + 3)
    key_obj.rotation_euler = (0.785, 0, -0.785)  # 45°
    key.shape = 'RECTANGLE'
    
    # FILL LIGHT (заполнение, противоположная сторона, ниже)
    fill = bpy.data.lights.new("Fill_Light", 'AREA')
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill.energy = fill_energy
    fill.size = 3.0
    fill.size_y = 3.0
    fill_obj.location = (target_loc[0] - 3, target_loc[1] + 3, target_loc[2] + 1.5)
    fill_obj.rotation_euler = (0.5, 0, 0.785)
    fill.shape = 'RECTANGLE'
    
    # RIM/BACK LIGHT (контровой, сзади)
    rim = bpy.data.lights.new("Rim_Light", 'AREA')
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    bpy.context.collection.objects.link(rim_obj)
    rim.energy = rim_energy
    rim.size = 1.5
    rim.size_y = 1.5
    rim_obj.location = (target_loc[0] - 2, target_loc[1] - 2, target_loc[2] + 4)
    rim_obj.rotation_euler = (-0.5, 0, 3.14)
    rim.shape = 'RECTANGLE'
    
    return [key_obj, fill_obj, rim_obj]

# Использование
target = bpy.data.objects.get("Main_Subject")
lights = setup_3point_lighting(target)
```

### 4-POINT + BACKGROUND LIGHT
```python
def setup_4point_lighting(target_obj):
    lights = setup_3point_lighting(target_obj)
    
    # BACKGROUND LIGHT (освещение фона)
    bg = bpy.data.lights.new("BG_Light", 'AREA')
    bg_obj = bpy.data.objects.new("BG_Light", bg)
    bpy.context.collection.objects.link(bg_obj)
    bg.energy = 200
    bg.size = 10
    bg.size_y = 10
    bg_obj.location = (0, -8, 3)
    bg_obj.rotation_euler = (0, 0, 0)
    bg.shape = 'RECTANGLE'
    
    lights.append(bg_obj)
    return lights
```

### RING LIGHT (Для продукта/портрета)
```python
def setup_ring_light(target_obj, radius=3, count=8, energy=200):
    lights = []
    for i in range(count):
        angle = (i / count) * 6.283
        l = bpy.data.lights.new(f"Ring_{i}", 'AREA')
        lo = bpy.data.objects.new(f"Ring_{i}", l)
        bpy.context.collection.objects.link(lo)
        l.energy = energy
        l.size = 0.5
        l.shape = 'RECTANGLE'
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        lo.location = (x, y, 2)
        lo.rotation_euler = (math.pi/2, 0, angle + math.pi/2)
        lights.append(lo)
    return lights
```

### VOLUMETRIC LIGHTING (God Rays / Fog)
```python
def setup_volumetric_world(density=0.05, anisotropy=0.0, color=(1,1,1)):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Volume")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    # Очистить
    nodes.clear()
    
    # Volume Scatter
    volume = nodes.new('ShaderNodeVolumeScatter')
    volume.location = (0, 0)
    volume.inputs['Density'].default_value = density
    volume.inputs['Anisotropy'].default_value = anisotropy
    volume.inputs['Color'].default_value = color + (1,)
    
    # Background (опционально)
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (-200, 0)
    bg.inputs['Strength'].default_value = 0.1
    
    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (200, 0)
    
    links.new(volume.outputs['Volume'], out.inputs['Volume'])
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    
    # В Cycles: Render Properties > Volumetrics > Step Rate
    bpy.context.scene.cycles.volume_step_rate = 0.1
    bpy.context.scene.cycles.volume_max_steps = 128
    
    return world

# God Rays (через Spot Light + Volume)
def setup_god_rays(target_loc, energy=5000, cone_angle=0.5):
    spot = bpy.data.lights.new("God_Rays", 'SPOT')
    spot_obj = bpy.data.objects.new("God_Rays", spot)
    bpy.context.collection.objects.link(spot_obj)
    spot.energy = energy
    spot.spot_size = cone_angle
    spot.spot_blend = 0.5
    spot.show_cone = True
    spot_obj.location = (target_loc[0], target_loc[1] - 5, target_loc[2] + 10)
    spot_obj.rotation_euler = (-1.0, 0, 0)
    
    # Включить Volume в Render Properties
    bpy.context.scene.cycles.volume_step_rate = 0.1
    return spot_obj
```

### HDRI + STUDIO MIX
```python
def setup_mixed_lighting(hdri_path, target_obj, hdri_strength=0.5, studio_strength=1.0):
    """HDRI для окружения + Studio lights для формы"""
    # HDRI на низкой силе для отражений
    setup_hdri_world(hdri_path, strength=hdri_strength)
    
    # Studio lights для ключевых бликов
    setup_3point_lighting(target_obj, key_energy=1000*studio_strength, fill_energy=300*studio_strength, rim_energy=500*studio_strength)
    
    # Настройки Cycles для качества
    bpy.context.scene.cycles.caustics_reflective = True
    bpy.context.scene.cycles.caustics_refractive = True
    bpy.context.scene.cycles.max_bounces = 12
    bpy.context.scene.cycles.diffuse_bounces = 4
    bpy.context.scene.cycles.glossy_bounces = 4
    bpy.context.scene.cycles.transmission_bounces = 12
```

---

## 📊 LIGHTING PRESETS

| Пресет | HDRI | Key | Fill | Rim | Volumetric | Use Case |
|--------|------|-----|------|-----|------------|----------|
| **Studio Product** | studio_2k (0.3) | 1000 | 300 | 500 | No | Продукт, ювелирка |
| **ArchViz Interior** | interior_2k (1.0) | 800 | 400 | 200 | Light Fog | Архитектура |
| **Outdoor Day** | outdoor_4k (1.0) | Sun 5000 | Sky 1000 | - | Yes | Архитектура, ландшафт |
| **Dark Fantasy** | dungeon_2k (0.8) | 300 | 100 | 500 | Heavy Fog | Игры, кино |
| **Car Studio** | garage_2k (0.5) | 2000 | 800 | 1000 | No | Авто, глянец |
| **Character Portrait** | studio_2k (0.4) | 800 | 400 | 600 | No | Персонажи |

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| HDRI Strength 0.3-0.5 для студии | Не пересвечивает, даёт только отражения |
| Area Light > Spot для мягких теней | Физически корректнее |
| Light Linking (Cycles) | Контроль какие объекты освещает свет |
| Multiple Importance Sample в HDRI | Меньше шум в отражениях |
| Volumetric Step Rate 0.1 | Качество God Rays без лагов |

---

## 🔗 LINKS

- **Prompts:** [P16-P21 Lighting](../lighting/), [P09 Principled BSDF](./09_principled_bsdf.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md), [WF 06: ArchViz](../workflows/wf_06_archviz_workflow.md)
- **MCP Tools:** `download_polyhaven_asset`, `set_material`
- **Next:** [P14: Camera & Composition](./14_camera_composition.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/13_lighting_hdri.md` |
| Russian | `multilang/ru/prompts/13_lighting_hdri.md` |