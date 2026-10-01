---
lang: en
tags: [reference, texturing]
---
# TEXTURE GENERATION WORKFLOWS

## Overview
Multiple approaches for creating PBR textures and materials.

---

## Method 1: Dream Textures (Local Stable Diffusion)
**Best for:** Custom textures, seamless tiling, inpainting, projection
**Cost:** Free (local GPU)
**Quality:** High, fully controllable

### Basic Texture Generation
```
1. Select object → N-panel → Dream Textures
2. Tab: "Generate Texture"
3. Prompt: "weathered brick wall, moss in cracks, seamless"
4. Check: "Seamless" (for tiling)
5. Model: stabilityai/stable-diffusion-2-1-base
6. Size: 512x512 (or 1024x1024 if VRAM)
7. Click: Generate
8. Click: "Apply to Material" or drag to shader nodes
```

### Texture Projection (Depth-to-Image)
```
1. Model your geometry (wall, floor, character)
2. Select faces to texture (Edit Mode → Select faces)
3. Local View (/) to isolate
4. Dream Textures → "Project Dream Texture"
5. Model: stabilityai/stable-diffusion-2-depth (REQUIRED)
6. Prompt: "ancient stone temple, moss, cracks, torch lighting"
7. Data Source: "Depth" or "Depth and Color"
8. Click: Project Dream Texture
9. Auto-creates material + UVs
```

### Inpainting (Fix Seams / Edit)
```
1. Open generated texture in Image Editor
2. Mask problem area (brush tool)
3. Dream Textures → Inpaint
4. Prompt: "seamless continuation of stone texture"
5. Generates only in masked area
```

### Outpainting (Extend Texture)
```
1. Image Editor → Select texture
2. Dream Textures → Outpaint
3. Choose origin (center, edge, corner)
3. Prompt: "extend brick wall pattern"
4. Increases canvas size
```

### Render Pass Re-style
```
1. Set up Cycles scene with basic lighting
2. Add "Dream Texture" node in Compositor
3. Connect Render Layers → Dream Texture → Composite
4. Prompt: "cyberpunk neon, volumetric fog, photorealistic"
5. Re-render → AI transforms each frame
```

### AI Upscaling
```
1. Low-res texture (512x512)
2. Dream Textures → Upscale
3. Model: stabilityai/stable-diffusion-x4-upscaler
4. Output: 2048x2048
```

---

## Method 2: Poly Haven Textures (Free, Curated)
**Best for:** Production-ready PBR, consistent quality
**Cost:** Free (CC0)
**Quality:** Professional, 1k-8k

### Workflow (via blender-mcp / GenesisCore)
```bash
# Via AI:
"Search Poly Haven textures for 'metal' category 'rusted' at 2k resolution
Download 'RustedIron' and apply to object 'Pipe'"

# Steps:
1. search_polyhaven_assets(asset_type="textures", categories="metal")
2. download_polyhaven_asset(asset_id="RustedIron", asset_type="textures", resolution="2k")
3. set_texture(object_name="Pipe", texture_id="RustedIron")
```

### Maps Included
- Base Color (Diffuse)
- Roughness
- Normal (OpenGL)
- Metallic
- AO (Ambient Occlusion)
- Height/Displacement

### Resolution Options
| Resolution | Use Case |
|------------|----------|
| 1k | Preview, mobile, background |
| 2k | Standard production |
| 4k | Hero assets, close-ups |
| 8k | Extreme detail, film |

---

## Method 3: Procedural / Node-Based (Blender Native)
**Best for:** Infinite variation, parametric, no GPU needed
**Cost:** Free
**Quality:** Mathematical precision

### Voronoi Noise Pattern
```python
# Execute via execute_blender_code
import bpy

mat = bpy.data.materials.new("ProceduralMetal")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Nodes
output = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
voronoi = nodes.new('ShaderNodeTexVoronoi')
color_ramp = nodes.new('ShaderNodeValToRGB')
mapping = nodes.new('ShaderNodeMapping')
tex_coord = nodes.new('ShaderNodeTexCoord')

# Layout
tex_coord.location = (-600, 0)
mapping.location = (-400, 0)
voronoi.location = (-200, 0)
color_ramp.location = (0, 0)
principled.location = (200, 0)
output.location = (400, 0)

# Configure
voronoi.feature = 'SMOOTH_F1'
voronoi.metric = 'MANHATTAN'
color_ramp.color_ramp.elements[0].position = 0.3
color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1)
color_ramp.color_ramp.elements[1].position = 0.7
color_ramp.color_ramp.elements[1].color = (0.8, 0.7, 0.6, 1)

# Links
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
links.new(voronoi.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(voronoi.outputs['Distance'], principled.inputs['Roughness'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Animate mapping scale
mapping.inputs['Scale'].default_value = (5, 5, 5)
```

### Brick Generator (Geometry Nodes → Texture)
```python
# Creates procedural brick pattern with mortar
# Use Geometry Nodes to generate mesh → bake to texture
```

---

## Method 4: Dream Textures + Poly Haven Hybrid
**Best for:** Hero assets with custom details on curated base

### Workflow
```
1. Base: Download Poly Haven "ConcreteFloor01" (2k PBR set)
2. Customize: Dream Textures Inpaint
   - Mask areas for "cracks with glowing moss"
   - "painted graffiti symbols"
   - "water puddles with reflections"
3. Bake: Combine into single texture set
4. Apply: Single material with all maps
```

---

## Method 5: Substance / External Tools
**Best for:** AAA production, team pipelines
**Cost:** Subscription
**Integration:** Export from Blender → Substance → Import

### Pipeline
```
1. Blender: Model + UV unwrap
2. Export: GLTF/FBX with UVs
3. Substance Painter: Smart materials + custom
4. Export: PBR maps (4k)
5. Blender: Import maps → Principled BSDF setup
```

---

## PBR Material Setup (Standard)

### Principled BSDF Connections
```
Image Texture (Base Color) ──────────────────→ Base Color
Image Texture (Roughness) ──────────────────→ Roughness (Color Space: Non-Color)
Image Texture (Normal) → Normal Map ────────→ Normal
Image Texture (Metallic) ───────────────────→ Metallic (Non-Color)
Image Texture (Height) → Displacement ──────→ Displacement (Material Settings)
Image Texture (AO) ─────────────────────────→ Mix with Base Color (Multiply)
```

### Node Setup Script
```python
# Execute via execute_blender_code
import bpy

def setup_pbr_material(obj, name, maps_dict):
    """maps_dict: {'base_color': img, 'roughness': img, 'normal': img, ...}"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Base Color
    if 'base_color' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['base_color']
        tex.image.colorspace_settings.name = 'sRGB'
        links.new(tex.outputs['Color'], principled.inputs['Base Color'])
    
    # Roughness
    if 'roughness' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['roughness']
        tex.image.colorspace_settings.name = 'Non-Color'
        links.new(tex.outputs['Color'], principled.inputs['Roughness'])
    
    # Normal
    if 'normal' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['normal']
        tex.image.colorspace_settings.name = 'Non-Color'
        normal_map = nodes.new('ShaderNodeNormalMap')
        links.new(tex.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
    
    # Metallic
    if 'metallic' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['metallic']
        tex.image.colorspace_settings.name = 'Non-Color'
        links.new(tex.outputs['Color'], principled.inputs['Metallic'])
    
    # Height/Displacement
    if 'height' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['height']
        tex.image.colorspace_settings.name = 'Non-Color'
        disp = nodes.new('ShaderNodeDisplacement')
        links.new(tex.outputs['Color'], disp.inputs['Height'])
        links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
        # Enable in Material Settings
        mat.displacement_method = 'BOTH'
    
    # Assign
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat
```

---

## Texture Resolution Guidelines

| Asset Type | Distance | Resolution |
|------------|----------|------------|
| Hero prop (hero) | Close-up | 4k-8k |
| Character | Medium | 2k-4k |
| Environment | Medium | 2k |
| Background | Far | 1k-2k |
| Mobile/Web | Any | 1k-2k |
| VR/AR | Close | 2k-4k |

---

## Optimization Tips

### VRAM Management (Dream Textures)
```bash
# Preferences → Dream Textures:
- Precision: fp16 (default)
- Speed: Half Precision
- Memory: Attention Slicing (Auto)
- Tile Size: 512 (for upscaling)
```

### Batch Texture Generation
```python
# Generate multiple variations
for i, prompt in enumerate(prompts):
    bpy.ops.dream_texture.generate(
        prompt=prompt,
        seed=i * 1000,
        width=512,
        height=512,
        seamless=True
    )
    # Save each
    img = bpy.data.images[-1]
    img.filepath_raw = f"//textures/tex_{i:03d}.png"
    img.save()
```

### Naming Convention
```
{asset}_{map}_{resolution}.{ext}
Examples:
- wall_basecolor_2k.png
- wall_roughness_2k.png
- wall_normal_2k.exr
- wall_height_2k.png
- wall_metallic_2k.png
- wall_ao_2k.png
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Seams visible | Enable "Seamless" in Dream Textures; use Inpaint on edges |
| Blurry texture | Increase resolution; check UV scale; use higher quality model |
| Wrong colors | Check Color Space (sRGB vs Non-Color) on each map |
| Normal map inverted | Flip Y in Normal Map node; check OpenGL vs DirectX |
| Displacement not working | Material Settings → Displacement: "BOTH" or "Displacement Only" |
| OOM | Reduce resolution; enable Attention Slicing; close other apps |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [ANIMATION WORKFLOWS](animation.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](../api/scripting-patterns.md)
- **По темам:** [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [CASE 03: PRODUCT VISUALIZATION](../../../cases/case_03_product_viz.md)
- **Теги:** #reference, #texturing

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

