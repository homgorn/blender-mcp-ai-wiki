---
lang: en
---
# EEVEE NEXT (BLENDER 4.2+)

**Next-generation real-time renderer in Blender 4.2+**

---

## 🎯 WHAT'S NEW IN EEVEE NEXT

| Feature | EEVEE Legacy | EEVEE Next |
|---------|--------------|------------|
| **Architecture** | OpenGL 3.3 | Vulkan / Metal / DX12 |
| **Shadow Maps** | Variance Shadow Maps | Contact Hardening Shadows (CHS) |
| **SSRR** | Screen Space Reflections | Ray-traced Reflections (hybrid) |
| **GI** | Irradiance Volumes + Light Probes | Radiance Cache + DDGI |
| **Volumetrics** | 3D Texture | Voxel-based, temporal |
| **Shaders** | GLSL | SPIR-V / Slang |
| **GPU Support** | OpenGL 3.3+ | Vulkan 1.2+ / Metal 2+ / DX12 |

---

## ⚙️ SETUP & REQUIREMENTS

### Hardware Requirements
```yaml
Minimum:
  GPU: Vulkan 1.2+ / Metal 2+ / DX12 Feature Level 12_1
  VRAM: 4 GB (8 GB recommended)
  Driver: Latest stable

Recommended:
  GPU: RTX 3070 / RX 6700 XT / M2 Pro
  VRAM: 12 GB+
  Driver: Latest Game Ready / Pro
```

### Enable EEVEE Next
```python
import bpy

# Switch to EEVEE Next
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Verify
print(f"Engine: {scene.render.engine}")
print(f"Device: {bpy.context.preferences.system.compute_device_type}")
```

---

## 🌟 KEY FEATURES

### 1. Contact Hardening Shadows (CHS)
```python
# Shadow Settings
scene.eevee.shadow_method = 'VSM'  # or 'EVSM' for exponential
scene.eevee.shadow_cube_size = '2048'  # 512, 1024, 2048, 4096
scene.eevee.shadow_cascade_size = '2048'

# Contact Hardening (automatic in Next)
# Penumbra size based on light size × distance
# No more manual bias tweaking!

# Per-light settings
light = bpy.data.lights["Sun"]
light.shadow_soft_size = 2.0  # Light size for penumbra
light.shadow_buffer_clip_start = 0.1
light.shadow_buffer_clip_end = 100.0
```

### 2. Screen-Space Ray-Traced Reflections (SSRR)
```python
# Enable Ray-traced Reflections
scene.eevee.use_ssr = True
scene.eevee.use_ssr_refraction = True
scene.eevee.ssr_quality = 0.5  # 0.25 - 1.0
scene.eevee.ssr_thickness = 0.01
scene.eevee.ssr_border_fade = 0.1

# Hybrid: SSR + Ray-tracing fallback
# Falls back to ray-tracing when SSR fails
# Requires RTX / RX 6000+ for hardware RT
```

### 3. Dynamic Diffuse Global Illumination (DDGI)
```python
# DDGI Probe Grid
scene.eevee.gi_diffuse_bounces = 3
scene.eevee.gi_cubemap_resolution = '512'  # 256, 512, 1024
scene.eevee.gi_probe_count = 64  # Per probe grid
scene.eevee.gi_probe_distance = 10.0  # Spacing

# Probe Grid Object
grid = bpy.data.objects.new("DDGI_Probe_Grid", None)
grid.empty_display_type = 'CUBE'
grid.empty_display_size = 10.0
bpy.context.collection.objects.link(grid)

# Add DDGI Probe Grid modifier
mod = grid.modifiers.new("DDGI_Probe_Grid", 'NODES')
# Configure in Geometry Nodes
```

### 4. Radiance Cache (Real-time GI)
```python
# Radiance Cache (screen-space GI fallback)
scene.eevee.gi_cache_resolution = '512'
scene.eevee.gi_cache_frames = 10  # Temporal accumulation
scene.eevee.gi_cache_quality = 'HIGH'

# Works with DDGI for hybrid GI
# Radiance Cache = Screen-space (fast, noisy)
# DDGI = World-space (stable, memory)
```

### 5. Volumetric Rendering (Voxel-based)
```python
# Volumetric Settings
scene.eevee.volumetric_tile_size = '64'  # 32, 64, 128
scene.eevee.volumetric_samples = 32
scene.eevee.volumetric_shadow_samples = 8

# Volumetric Lighting
light = bpy.data.lights["Spot"]
light.use_volumetric = True
light.volumetric_shadow_samples = 4

# Volumetric Material
mat = bpy.data.materials.new("Volume_Fog")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()
volume = nodes.new('ShaderNodeVolumePrincipled')
volume.inputs['Density'].default_value = 0.1
volume.inputs['Anisotropy'].default_value = 0.5
output = nodes.new('ShaderNodeOutputMaterial')
output.target = 'VOLUME'
links.new(volume.outputs['Volume'], output.inputs['Volume'])
```

### 6. Subsurface Scattering (Real-time)
```python
# SSS in EEVEE Next
mat = bpy.data.materials.new("Skin")
mat.use_nodes = True
nodes = mat.node_tree.nodes
principled = nodes['Principled BSDF']

# Enable SSS
principled.inputs['Subsurface Weight'].default_value = 0.5
principled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)
principled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)
principled.inputs['Subsurface IOR'].default_value = 1.4

# EEVEE Next: Real-time SSS (no bake needed!)
# Screen-space + Ray-traced fallback
```

---

## 🎨 MATERIAL NODES (EEVEE Next)

### New Nodes
```python
# New Shader Nodes in EEVEE Next
# -----------------------------------
# Ray Portal: Portal for interior rendering
# Irradiance Volume: Light probe data
# Radiance Probe: DDGI probe data
# Light Probe: Generic light probe
# Volume Info: Volume properties
# Ray Length: Ray distance

# Usage in Shader Editor:
# 1. Add → Ray Portal
# 2. Connect to World Output → Volume
# 3. Position at windows/doors
```

### Screen-Space Effects
```python
# Ambient Occlusion
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 0.5
scene.eevee.gtao_factor = 1.0
scene.eevee.gtao_bounce_factor = 1.0

# Bloom
scene.eevee.use_bloom = True
scene.eevee.bloom_threshold = 0.8
scene.eevee.bloom_intensity = 0.05
scene.eevee.bloom_radius = 6.5
scene.eevee.bloom_threshold = 0.8

# Motion Blur
scene.eevee.use_motion_blur = True
scene.eevee.motion_blur_shutter = 0.5
scene.eevee.motion_blur_samples = 16
scene.eevee.motion_blur_shutter_curve = [(0,0), (0.5,1), (1,0)]
```

---

## 🎬 RENDER SETTINGS

### Quality Presets
```python
# Preset: Draft (Real-time)
def preset_draft():
    s = bpy.context.scene.eevee
    s.shadow_cube_size = '512'
    s.shadow_cascade_size = '512'
    s.gi_cubemap_resolution = '256'
    s.gi_cache_resolution = '256'
    s.volumetric_tile_size = '32'
    s.volumetric_samples = 8
    s.gtao_distance = 0.2
    s.bloom_intensity = 0.05

# Preset: Production
def preset_production():
    s = bpy.context.scene.eevee
    s.shadow_cube_size = '2048'
    s.shadow_cascade_size = '2048'
    s.gi_cubemap_resolution = '1024'
    s.gi_cache_resolution = '512'
    s.volumetric_tile_size = '64'
    s.volumetric_samples = 64
    s.gtao_distance = 1.0
    s.bloom_intensity = 0.1

# Preset: Cinematic
def preset_cinematic():
    s = bpy.context.scene.eevee
    s.shadow_cube_size = '4096'
    s.shadow_cascade_size = '4096'
    s.gi_cubemap_resolution = '2048'
    s.gi_cache_resolution = '1024'
    s.volumetric_tile_size = '128'
    s.volumetric_samples = 128
    s.gtao_distance = 2.0
    s.bloom_intensity = 0.15
    s.use_ssr = True
    s.use_ssr_refraction = True
```

---

## 🎮 GAME ENGINE EXPORT (EEVEE → Engine)

### Unreal Engine Compatibility
```python
def export_eevee_material_for_unreal(mat_name):
    """Export EEVEE material as compatible UE material"""
    mat = bpy.data.materials[mat_name]
    
    # EEVEE Next → UE5 Material mapping:
    mapping = {
        'Base Color': 'BaseColor',
        'Metallic': 'Metallic',
        'Roughness': 'Roughness',
        'Normal': 'Normal',
        'Emission': 'EmissiveColor',
        'Alpha': 'Opacity',
        'Subsurface': 'Subsurface',
        'Clearcoat': 'ClearCoat',
        'Clearcoat Roughness': 'ClearcoatRoughness',
        'Anisotropic': 'Anisotropy',
        'Sheen': 'Sheen',
        'Transmission': 'Transmission',
    }
    
    # Export textures
    for slot in mat.node_tree.nodes:
        if slot.type == 'TEX_IMAGE' and slot.image:
            # Export as PNG/EXR
            pass
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### Viewport Optimization
```python
# Viewport Settings (not render)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        space = area.spaces.active
        space.shading.type = 'RENDERED'
        space.shading.use_scene_lights = True
        space.shading.use_scene_world = True
        
        # Performance
        space.shading.show_shadows = True
        space.shading.show_cavity = True
        space.shading.cavity_type = 'SCREEN'
        space.shading.cavity_valley_factor = 0.5
        space.shading.cavity_ridge_factor = 0.5
```

### Instancing for Massive Scenes
```python
# Collection Instancing (EEVEE Next handles efficiently)
def setup_instancing(collection_name, count=1000):
    coll = bpy.data.collections.new(f"Instances_{collection_name}")
    
    # Source object
    src = bpy.data.objects.get(collection_name)
    if not src:
        return
    
    # Instancer
    instancer = bpy.data.objects.new(f"Instancer_{collection_name}", None)
    instancer.instance_type = 'COLLECTION'
    instancer.instance_collection = bpy.data.collections[collection_name]
    bpy.context.collection.objects.link(instancer)
    
    # Geometry Nodes for distribution
    gn = bpy.data.node_groups.new("Distribute", 'GeometryNodeTree')
    # ... distribute points on faces, instance collection
```

---

## 🐛 TROUBLESHOOTING

| Issue | Cause | Fix |
|-------|-------|-----|
| Black shadows | Shadow bias too high | Reduce `shadow_buffer_bias` |
| Flickering shadows | Cascade transition | Increase cascade count, adjust distances |
| SSR artifacts | Screen-space limits | Enable ray-tracing fallback, increase thickness |
| GI flickering | DDGI probe update | Increase probe count, reduce update frequency |
| Volumetric noise | Low samples | Increase `volumetric_samples`, use denoiser |
| VRAM OOM | High res shadows/textures | Reduce shadow map size, use texture streaming |

---

## 🔗 LINKS

- **EEVEE Next Announcement:** https://developer.blender.org/T112345
- **Vulkan Backend:** https://developer.blender.org/T112346
- **Vulkan Validation Layers:** https://vulkan.lunarg.com/doc/view/latest/windows/layer_configuration.html
- **Blender GPU Requirements:** https://www.blender.org/download/requirements/

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/realtime/eevee_next.md` |
| Russian | `multilang/ru/realtime/eevee_next.md` |