---
id: ocio_aces
lang: ru
orig_lang: en
category: color
type: reference
difficulty: 0
translation: template
---
# COLOR MANAGEMENT: OCIO / ACES

> Цель: ## 🌍 MULTILANG

**ID:** ocio_aces | **Lang:** ru | **Orig:** en | **Category:** color | **Tags:** 

---

# COLOR MANAGEMENT: OCIO / ACES

**Professional color management for Blender pipelines**

---

## 🎯 WHY COLOR MANAGEMENT?

| Problem | Solution |
|---------|----------|
| Inconsistent colors across apps | OCIO config shared across pipeline |
| Wrong gamma on export | ACES 1.3 + OCIO v2 |
| HDR/clipping issues | ACEScg working space, proper tone mapping |
| Team inconsistency | Centralized OCIO config |
| HDR delivery | ACES 1.3 + PQ / HLG |

---

## 🏗️ ACES 1.3 OVERVIEW

### ACES Color Spaces
```
ACES 1.3 Color Spaces:
├── ACEScg          ← Working space (linear, wide gamut, AP1 primaries)
├── ACES2065-1      ← Archival/interchange (linear, AP0 primaries)
├── ACEScct         ← Color grading (log-like, for grading)
├── ACESproxy       ← On-set monitoring (10-bit log)
├── sRGB            ← Display/web (sRGB primaries, ~2.2 gamma)
├── Rec.709         ← HD TV (Rec.709 primaries, ~2.4 gamma)
├── P3-D65          ← DCI-P3 cinema (DCI-P3 primaries, 2.6 gamma)
├── Rec.2020        ← UHD TV (Rec.2020 primaries, 2.4/ST2084)
└── PQ / HLG        ← HDR (ST2084 / HLG transfer functions)
```

### ACES Pipeline
```
Camera/Source → IDT (Input Device Transform) 
    → ACEScg (Working Space) 
        → Creative Grade (ACEScct) 
            → RRT (Reference Rendering Transform) 
                → ODT (Output Device Transform) 
                    → Display/Output
```

---

## ⚙️ BLENDER OCIO SETUP

### Blender 4.0+ OCIO v2 Support
```python
import bpy

# Check OCIO version
print(f"OCIO Version: {bpy.context.scene.ocio_config_version}")

# Set OCIO Config
scene = bpy.context.scene
scene.view_settings.view_transform = 'ACES 1.3 SDR-video'  # or custom

# Set Working Space (ACEScg)
scene.view_settings.look = 'ACES 1.3 SDR-video'
# Or for HDR:
scene.view_settings.look = 'ACES 1.3 ST2084-1000nits'
# or
scene.view_settings.look = 'ACES 1.3 HLG'

# Set View Transform
scene.view_settings.view_transform = 'ACES 1.3 SDR-video'
# Options:
# - 'ACES 1.3 SDR-video'
# - 'ACES 1.3 ST2084-1000nits' (HDR PQ)
# - 'ACES 1.3 ST2084-2000nits'
# - 'ACES 1.3 ST2084-4000nits'
# - 'ACES 1.3 HLG' (Hybrid Log-Gamma)
# - 'Raw' (no transform)
```

### Custom OCIO Config
```yaml
# config.ocio (ACES 1.3 + Custom)
ocio_profile_version: 2

color_spaces:
  - name: ACEScg
    description: "ACES CG - Working Space"
    bit_depth: 32f
    is_data: false
    allocation: uniform
    to_reference: !<GroupTransform>
      children:
        - !<MatrixTransform> {matrix: [0.662454, 0.134004, 0.156187, 0, 0.272228, 0.674081, 0.053691, 0, -0.005574, -0.004058, 1.009632, 0, 0, 0, 0, 1]}
  
  - name: ACES2065-1
    description: "ACES 2065-1 - Archival"
    bit_depth: 32f
    is_data: false
    to_reference: !<GroupTransform>
      children:
        - !<MatrixTransform> {matrix: [0.59719, 0.35458, 0.04823, 0, 0.07600, 0.90834, 0.01566, 0, 0.02840, 0.13383, 0.83777, 0, 0, 0, 0, 1]}

  - name: sRGB
    description: "sRGB - Display"
    bit_depth: 8ui
    is_data: false
    to_reference: !<GroupTransform>
      children:
        - !<ColorSpaceTransform> {src: sRGB, dst: ACEScg}

  - name: Rec709
    description: "Rec.709 - HD Video"
    to_reference: !<ColorSpaceTransform> {src: Rec.709, dst: ACEScg}

  - name: P3D65
    description: "P3 D65 - Digital Cinema"
    to_reference: !<ColorSpaceTransform> {src: P3-D65, dst: ACEScg}

  - name: Rec2020
    description: "Rec.2020 - UHD"
    to_reference: !<ColorSpaceTransform> {src: Rec.2020, dst: ACEScg}

viewing_rules:
  - !<ViewingRule> {name: "sRGB", colorspace: "sRGB", encodings: ["sRGB"]}
  - !<ViewingRule> {name: "Rec.709", colorspace: "Rec709", encodings: ["Rec.709"]}

views:
  - !<View> {name: "ACES 1.3 SDR-video", colorspace: "sRGB", looks: ["ACES_sRGB"]}
  - !<View> {name: "ACES 1.3 ST2084-1000nits", colorspace: "Rec2020", looks: ["ACES_ST2084_1000"]}
  - !<View> {name: "ACES 1.3 HLG", colorspace: "Rec2020", looks: ["ACES_HLG"]}

looks:
  - !<Look> {name: "ACES_sRGB", process_space: "ACEScg", transform: !<GroupTransform> {children: [{!<ColorSpaceTransform> {src: ACEScg, dst: sRGB}}]}}
  - !<Look> {name: "ACES_ST2084_1000", process_space: "ACEScg", transform: !<GroupTransform> {children: [{!<ColorSpaceTransform> {src: ACEScg, dst: Rec2020_ST2084}}]}}
  - !<Look> {name: "ACES_HLG", process_space: "ACEScg", transform: !<GroupTransform> {children: [{!<ColorSpaceTransform> {src: ACEScg, dst: Rec2020_HLG}}]}}
```

### Load Custom Config in Blender
```python
import bpy

# Load custom OCIO config
bpy.context.scene.ocio_config = '/path/to/config.ocio'

# Or set via environment variable (before Blender start)
# export OCIO=/path/to/config.ocio

# Verify
print(f"Config: {bpy.context.scene.ocio_config}")
print(f"Views: {[v.name for v in bpy.context.scene.view_settings.views]}")
```

---

## 🎨 WORKING IN ACEScg

### Texture Color Spaces
```python
# Set correct color space for each texture type
def set_texture_colorspace(image, map_type):
    """Set correct color space for texture type"""
    
    color_spaces = {
        'base_color': 'sRGB',      # Albedo/Diffuse
        'diffuse': 'sRGB',
        'albedo': 'sRGB',
        'color': 'sRGB',
        'roughness': 'Non-Color',   # Data
        'metallic': 'Non-Color',    # Data
        'normal': 'Non-Color',      # Data (OpenGL)
        'height': 'Non-Color',      # Data
        'displacement': 'Non-Color', # Data
        'ao': 'Non-Color',          # Data
        'curvature': 'Non-Color',   # Data
        'opacity': 'Non-Color',     # Data
        'emission': 'sRGB',         # Color
        'transmission': 'Non-Color', # Data
        'subsurface': 'sRGB',       # Color
        'normal_gl': 'Non-Color',   # OpenGL normal
        'normal_dx': 'Non-Color',   # DirectX normal
    }
    
    cs = color_spaces.get(map_type.lower(), 'Non-Color')
    image.colorspace_settings.name = cs
    print(f"Set {image.name} to {cs}")

# Auto-detect from filename
def auto_set_colorspace(image):
    name = image.name.lower()
    if any(x in name for x in ['basecolor', 'albedo', 'diffuse', 'color', 'emission']):
        image.colorspace_settings.name = 'sRGB'
    elif any(x in name for x in ['rough', 'metal', 'normal', 'height', 'disp', 'ao', 'curv', 'opacity', 'mask']):
        image.colorspace_settings.name = 'Non-Color'
    elif 'emission' in name:
        image.colorspace_settings.name = 'sRGB'
```

### Node Setup for ACES
```python
# Node setup for ACEScg workflow
def setup_aces_nodes(material_name):
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Principled BSDF (works in ACEScg)
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    # Color Space conversion nodes (if needed)
    # Base Color: sRGB → ACEScg (handled by OCIO)
    # Normal: Non-Color (no conversion)
    # Roughness/Metallic: Non-Color
    
    # Texture nodes
    tex_base = nodes.new('ShaderNodeTexImage')
    tex_base.location = (-400, 300)
    tex_base.image.colorspace_settings.name = 'sRGB'
    
    tex_normal = nodes.new('ShaderNodeTexImage')
    tex_normal.location = (-400, 100)
    tex_normal.image.colorspace_settings.name = 'Non-Color'
    
    tex_rough = nodes.new('ShaderNodeTexImage')
    tex_rough.location = (-400, -100)
    tex_rough.image.colorspace_settings.name = 'Non-Color'
    
    # Normal Map
    normal_map = nodes.new('ShaderNodeNormalMap')
    normal_map.location = (-200, 100)
    
    # Links
    links.new(tex_base.outputs['Color'], principled.inputs['Base Color'])
    links.new(tex_normal.outputs['Color'], normal_map.inputs['Color'])
    links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
    links.new(tex_rough.outputs['Color'], principled.inputs['Roughness'])
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat
```

---

## 🖥️ VIEW TRANSFORMS & LOOKS

### View Transforms
```python
# Available in Blender 4.2+ with ACES 1.3
view_transforms = {
    'ACES 1.3 SDR-video': 'Standard SDR (Rec.709/sRGB)',
    'ACES 1.3 ST2084-1000nits': 'HDR PQ 1000 nits',
    'ACES 1.3 ST2084-2000nits': 'HDR PQ 2000 nits',
    'ACES 1.3 ST2084-4000nits': 'HDR PQ 4000 nits',
    'ACES 1.3 HLG': 'Hybrid Log-Gamma (broadcast HDR)',
    'Raw': 'No transform (linear)',
    'Standard': 'Legacy sRGB EOTF',
    'Film': 'Filmic log',
    'False Color': 'Exposure check',
}

# Set view transform
bpy.context.scene.view_settings.view_transform = 'ACES 1.3 SDR-video'

# Set look (creative grade)
looks = {
    'None': 'No look',
    'ACES 1.3 SDR-video': 'Standard',
    'ACES 1.3 ST2084-1000nits': 'HDR 1000nits',
    'Film': 'Filmic look',
    'High Contrast': 'High contrast',
    'Low Contrast': 'Low contrast',
}
bpy.context.scene.view_settings.look = 'None'  # or 'Film', etc.
```

### Exposure & Color Grading
```python
# Exposure
scene = bpy.context.scene
scene.view_settings.exposure = 0.0  # Stops
scene.view_settings.gamma = 1.0

# Filmic look (if using Filmic)
scene.view_settings.look = 'Filmic Log Encoding Base Curve'

# Custom LUT
scene.sequencer_colorspace_settings = 'Custom'
# Load .cube LUT via Color Management → Look → Custom
```

---

## 📊 RENDER OUTPUT SETTINGS

### EXR Output (Linear ACEScg)
```python
scene = bpy.context.scene
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '32'  # 32-bit float
scene.render.image_settings.exr_codec = 'ZIP'  # Lossless compression
scene.render.image_settings.use_preview = True

# Color space for EXR (stored as linear ACEScg)
# No conversion needed - EXR stores linear
```

### PNG/JPEG Output (sRGB)
```python
# For web/delivery
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '16'
scene.render.image_settings.compression = 15
# OCIO handles sRGB conversion on save
```

### Video Output (H.264/HEVC)
```python
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.audio_codec = 'AAC'
scene.render.ffmpeg.audio_bitrate = 192

# For HDR delivery
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'HEVC'
scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
# Requires HDR metadata injection post-render
```

---

## 🎬 ACES WORKFLOW IN COMPOSITOR

### Compositor Setup
```python
def setup_aces_compositor():
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    # Render Layers (linear ACEScg)
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (-400, 0)
    
    # Color Balance (Lift/Gamma/Gain) - in ACEScg
    cdl = nodes.new('CompositorNodeColorBalance')
    cdllocation = (0, 200)
    cdl.correction_method = 'LIFT_GAMMA_GAIN'
    cdl.lift = (1.01, 1.0, 0.98)   # Shadows warm
    cdl.gamma = (1.0, 1.0, 1.0)    # Midtones neutral
    cdl.gain = (0.98, 1.0, 1.02)   # Highlights cool
    
    # Hue/Sat
    hsv = nodes.new('CompositorNodeHueSat')
    hsv.location = (200, 200)
    hsv.color_saturation = 1.1
    
    # Gamma
    gamma = nodes.new('CompositorNodeGamma')
    gamma.location = (400, 200)
    gamma.inputs['Gamma'].default_value = 1.05
    
    # Output (OCIO handles ACEScg → Display)
    comp = nodes.new('CompositorNodeComposite')
    comp.location = (800, 0)
    
    viewer = nodes.new('CompositorNodeViewer')
    viewer.location = (800, -200)
    viewer.use_alpha = False
    
    # Links
    links.new(rl.outputs['Image'], cdl.inputs['Image'])
    links.new(cdl.outputs['Image'], hsv.inputs['Image'])
    links.new(hsv.outputs['Image'], gamma.inputs['Image'])
    links.new(gamma.outputs['Image'], comp.inputs['Image'])
    links.new(gamma.outputs['Image'], viewer.inputs['Image'])
    
    # File Output (EXR MultiLayer)
    file_out = nodes.new('CompositorNodeOutputFile')
    file_out.location = (800, -400)
    file_out.format.file_format = 'OPEN_EXR_MULTILAYER'
    file_out.format.color_mode = 'RGBA'
    file_out.format.color_depth = '32'
    file_out.base_path = "//renders/exr/"
    
    passes = ['Image', 'Depth', 'Normal', 'Mist', 'AO', 'Emission', 'Shadow', 'Cryptomatte00']
    for i, pass_name in enumerate(passes):
        if pass_name in rl.outputs:
            file_out.layer_slots.new(pass_name)
            links.new(rl.outputs[pass_name], file_out.inputs[i])

# Run
setup_aces_compositor()
```

---

## 🎬 HDR WORKFLOW

### HDR Setup (ST2084 / PQ)
```python
# HDR Setup for 1000 nits
scene = bpy.context.scene
scene.view_settings.view_transform = 'ACES 1.3 ST2084-1000nits'
scene.view_settings.look = 'None'

# Render settings for HDR
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '32'
scene.render.image_settings.exr_codec = 'ZIP'

# HDR Metadata (inject post-render via ffmpeg)
# ffmpeg -i input.exr -c:v libx265 -x265-params "hdr_opt=1:repeat_headers=1:colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:master-display=G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(10000000,1):max-cll=1000,400:max-fall=200" -pix_fmt yuv420p10le output.mp4
```

### HLG (Hybrid Log-Gamma)
```python
# HLG for Broadcast HDR
scene.view_settings.view_transform = 'ACES 1.3 HLG'
scene.view_settings.look = 'None'

# HLG is scene-referred, no ODT needed
# Compatible with SDR displays (backward compatible)
```

---

## 🎨 LOOK DEVELOPMENT (LUTs)

### Using LUTs in ACES
```python
# Apply LUT in Compositor
def apply_lut(lut_path, strength=1.0):
    scene = bpy.context.scene
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    # LUT Node
    lut_node = nodes.new('CompositorNodeLUT')
    lut_node.location = (200, 0)
    lut_node.lut = bpy.data.images.load(lut_path)
    lut_node.strength = strength
    
    # Insert into node tree
    # ... connect between color grade and output

# Common LUT Formats
# .cube (most common)
# .3dl (3D LUT)
# .csp (CineSpace)
# .icc (ICC Profile)
```

### Film Emulation LUTs
```python
# Popular Film LUTs for ACES
film_luts = {
    'Kodak 2383': 'Kodak_2383_D55.cube',
    'Fujifilm 3513': 'Fujifilm_3513_D55.cube',
    'Kodak Vision3 50D': 'Kodak_Vision3_50D.cube',
    'Kodak Vision3 250D': 'Kodak_Vision3_250D.cube',
    'Kodak Vision3 500T': 'Kodak_Vision3_500T.cube',
    'ARRI LogC to ACES': 'ARRI_LogC_to_ACES.cube',
    'Sony S-Log3 to ACES': 'Sony_SLog3_to_ACES.cube',
    'RED Log3G10 to ACES': 'RED_Log3G10_to_ACES.cube',
}

# Apply in Compositor
def apply_film_lut(lut_name, strength=0.5):
    lut_path = f"/project/luts/{film_luts[lut_name]}"
    apply_lut(lut_path, strength)
```

---

## 📦 DELIVERY SPECS

### Delivery Checklist
```yaml
Delivery Specs:
  Web/sRGB:
    colorspace: sRGB
    gamma: 2.2
    format: PNG/JPEG
    bit_depth: 8-bit
    
  Broadcast/Rec.709:
    colorspace: Rec.709
    gamma: 2.4
    format: ProRes 422 HQ / DNxHR HQX
    bit_depth: 10-bit
    
  Digital Cinema (DCI-P3):
    colorspace: P3-D65
    gamma: 2.6
    format: ProRes 4444 / DPX
    bit_depth: 12-bit
    white_point: D65
    
  HDR (ST2084/PQ):
    colorspace: Rec.2020
    transfer: ST2084 (PQ)
    peak_brightness: 1000/2000/4000 nits
    format: ProRes 4444 / HEVC
    bit_depth: 10/12-bit
    metadata: HDR10 / Dolby Vision
    
  HDR (HLG):
    colorspace: Rec.2020
    transfer: HLG
    format: ProRes 4444 / HEVC
    bit_depth: 10-bit
    compatible: SDR displays
    
  Archival (ACES 2065-1):
    colorspace: ACES2065-1
    format: EXR / DPX
    bit_depth: 16/32-bit float
    compression: lossless
```

---

## 🔗 LINKS

- **ACES Central:** https://acescentral.com/
- **OCIO Configs (архив):** https://github.com/AcademySoftwareFoundation/OpenColorIO-Configs
- **ACES 1.3 Spec:** https://acescentral.com/wp-content/uploads/2022/06/ACES-1.3-Developer-Guide.pdf
- **Blender OCIO:** https://docs.blender.org/manual/en/latest/render/color_management.html
- **ACES GitHub:** https://github.com/ampas/aces-dev

> [!NOTE]
> - Репозиторий OpenColorIO-Configs архивирован; актуальные конфиги OCIO: https://github.com/AcademySoftwareFoundation/OpenColorIO/tree/main/configs
> - Blender Color Management документация: https://docs.blender.org/manual/en/latest/render/color_management/

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/color/ocio_aces.md` |
| Russian | `multilang/ru/color/ocio_aces.md` |