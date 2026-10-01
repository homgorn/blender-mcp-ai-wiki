---
id: 13_lighting_hdri
lang: en
category: prompts
type: prompt
difficulty: 2
translation: legacy
---

# P13: LIGHTING & HDRI

**ID:** P13 | **Cluster:** Lighting | **Difficulty:** ⭐⭐ | **Tags:** #lighting #hdri #polyhaven #ibl #studio #volumetric

---

## 🎯 GOAL
Setup professional lighting using HDRI, studio lights, and volumetric effects

---

## 📝 PROMPT

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

def setup_hdri_world(hdri_path, strength=1.0, rotation=0.0):
    world = bpy.data.worlds.new("World_HDRI")
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = strength
    
    env = nodes.new('ShaderNodeTexEnvironment')
    env.location = (-400, 0)
    env.image = bpy.data.images.load(hdri_path)
    env.projection = 'EQUIRECTANGULAR'
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Rotation'].default_value[2] = rotation
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env.inputs['Vector'])
    links.new(env.outputs['Color'], bg.inputs['Color'])
    
    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (200, 0)
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    
    bpy.context.scene.world = world
    return world
```

### 3-POINT STUDIO LIGHTING
```python
def setup_3point_lighting(target_obj, key_energy=1000, fill_energy=300, rim_energy=500):
    target_loc = target_obj.location if target_obj else (0, 0, 0)
    
    # KEY LIGHT
    key = bpy.data.lights.new("Key_Light", 'AREA')
    key_obj = bpy.data.objects.new("Key_Light", key)
    bpy.context.collection.objects.link(key_obj)
    key.energy = key_energy
    key.size = 2.0
    key.size_y = 2.0
    key_obj.location = (target_loc[0] + 4, target_loc[1] - 4, target_loc[2] + 3)
    key_obj.rotation_euler = (0.785, 0, -0.785)
    key.shape = 'RECTANGLE'
    
    # FILL LIGHT
    fill = bpy.data.lights.new("Fill_Light", 'AREA')
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill.energy = fill_energy
    fill.size = 3.0
    fill.size_y = 3.0
    fill_obj.location = (target_loc[0] - 3, target_loc[1] + 3, target_loc[2] + 1.5)
    fill_obj.rotation_euler = (0.5, 0, 0.785)
    fill.shape = 'RECTANGLE'
    
    # RIM LIGHT
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
```

### VOLUMETRIC LIGHTING
```python
def setup_volumetric_world(density=0.05, anisotropy=0.0, color=(1,1,1)):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Volume")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    volume = nodes.new('ShaderNodeVolumeScatter')
    volume.location = (0, 0)
    volume.inputs['Density'].default_value = density
    volume.inputs['Anisotropy'].default_value = anisotropy
    volume.inputs['Color'].default_value = color + (1,)
    
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (-200, 0)
    bg.inputs['Strength'].default_value = 0.1
    
    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (200, 0)
    
    links.new(volume.outputs['Volume'], out.inputs['Volume'])
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    
    bpy.context.scene.cycles.volume_step_rate = 0.1
    bpy.context.scene.cycles.volume_max_steps = 128
    return world
```

### HDRI + STUDIO MIX
```python
def setup_mixed_lighting(hdri_path, target_obj, hdri_strength=0.5, studio_strength=1.0):
    setup_hdri_world(hdri_path, strength=hdri_strength)
    setup_3point_lighting(target_obj, key_energy=1000*studio_strength, fill_energy=300*studio_strength, rim_energy=500*studio_strength)
    
    bpy.context.scene.cycles.caustics_reflective = True
    bpy.context.scene.cycles.caustics_refractive = True
    bpy.context.scene.cycles.max_bounces = 12
```

---

## 📊 LIGHTING PRESETS

| Preset | HDRI | Key | Fill | Rim | Volumetric | Use Case |
|--------|------|-----|------|-----|------------|----------|
| Studio Product | studio_2k (0.3) | 1000 | 300 | 500 | No | Product, jewelry |
| ArchViz Interior | interior_2k (1.0) | 800 | 400 | 200 | Light Fog | Architecture |
| Outdoor Day | outdoor_4k (1.0) | Sun 5000 | Sky 1000 | - | Yes | Arch, landscape |
| Dark Fantasy | dungeon_2k (0.8) | 300 | 100 | 500 | Heavy Fog | Games, cinematic |
| Car Studio | garage_2k (0.5) | 2000 | 800 | 1000 | No | Auto, glossy |
| Character Portrait | studio_2k (0.4) | 800 | 400 | 600 | No | Characters |

---

## 🔗 LINKS

- **Prompts:** [P09 Principled BSDF](./09_principled_bsdf.md), [P14 Camera](./14_camera_composition.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **MCP Tools:** `download_polyhaven_asset`, `set_material`
- **Next:** [P14: Camera & Composition](./14_camera_composition.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/13_lighting_hdri.md` |
| Russian | `multilang/ru/prompts/13_lighting_hdri.md` |