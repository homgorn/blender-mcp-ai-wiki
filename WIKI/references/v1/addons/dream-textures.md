---
lang: en
tags: [addon, reference, stable-diffusion]
---
# DREAM TEXTURES ADDON - DEEP DIVE

## Overview
**Repo:** https://github.com/carson-katri/dream-textures
**Version:** Latest | **Blender:** 3.3+ | **License:** GPL-3.0
**Stars:** 8.2k | **Discord:** https://discord.gg/EmDJ8CaWZ7

Dream Textures brings **Stable Diffusion natively into Blender** - runs locally via diffusers/PyTorch, no external services needed. Best for texture generation, inpainting, outpainting, and texture projection.

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    DREAM TEXTURES ADDON                      │
├────────────────────────────────────────────────────────────┤
│  .python_dependencies/    # Bundled PyTorch, diffusers      │
│  builtin_presets/         # Prompt presets                  │
│  community_backends/      # Alternative backends            │
│  engine/                  # Core generation pipeline        │
│  generator_process/       # Subprocess for model inference  │
│  operators/               # Blender operators               │
│  ui/                      # N-panel + node editor           │
│  sd_configs/              # Model configurations            │
│  realtime_viewport.py     # Live preview                    │
│  render_pass.py           # Cycles render pass integration  │
│  prompt_engineering.py    # Prompt enhancement              │
│  image_utils.py           # Image processing                │
└────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Text-to-Texture
- Generate PBR texture sets (Base Color, Roughness, Normal, Metallic, Height)
- Seamless tiling option
- Preset styles: photorealistic, stylized, fantasy, sci-fi

### 2. Texture Projection (Depth-to-Image)
- Project textures onto 3D models using depth maps
- "Project Dream Texture" operator
- Works on entire scenes

### 3. Inpainting / Outpainting
- Fix texture seams
- Extend textures beyond boundaries
- Convert non-seamless → seamless

### 4. Render Pass Integration
- Use Cycles render as ControlNet input
- Re-style renders via img2img
- Animation re-styling frame-by-frame

### 5. AI Upscaling
- 4x upscale via ESRGAN/RealESRGAN
- Integrated in node system

### 6. History System
- Recall, export, import generations
- Prompt + parameters saved

---

## Installation

### Download Release (Recommended)
1. Go to: https://github.com/carson-katri/dream-textures/releases/latest
2. Download `dream_textures-<version>.zip`
3. Blender → Preferences → Add-ons → **Install from ZIP**
4. Enable **Dream Textures**

### First Run
- Addon downloads PyTorch + diffusers (~2-4 GB) to `.python_dependencies/`
- Requires **4GB+ VRAM** (CUDA or Apple Silicon)
- On macOS: may need quarantine removal:
  ```bash
  xattr -r -d com.apple.quarantine ~/Library/Application\ Support/Blender/3.3/scripts/addons/dream_textures/.python_dependencies
  ```

### Cloud Fallback (DreamStudio)
- If hardware unsupported: configure DreamStudio API key in preferences
- Processes in cloud instead of locally

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **VRAM** | 4 GB | 8-12 GB |
| **GPU** | CUDA 11.7+ / Apple Silicon | RTX 3080+ / M2 Max+ |
| **RAM** | 8 GB | 16-32 GB |
| **Disk** | 10 GB free | 20 GB+ |

---

## Usage Workflows

### Basic Texture Generation
```
1. Select object → N-panel → Dream Textures
2. Choose "Generate Texture" tab
3. Enter prompt: "weathered copper metal, patina, seamless"
4. Enable "Seamless" for tiling
5. Click Generate
6. Apply to material slots
```

### Texture Projection
```
1. Set up camera/view for projection
2. Select target object(s)
3. Choose "Project Dream Texture"
4. Enter prompt: "ancient stone temple walls, moss, cracks"
5. Adjust depth influence
6. Project → Creates UV-mapped textures
```

### Inpainting (Fix Seams)
```
1. Select texture in Image Editor
2. Mask problem area
3. Dream Textures → Inpaint
4. Prompt: "seamless continuation of stone texture"
5. Blend result
```

### Render Re-style
```
1. Set up Cycles scene
2. Render pass → Dream Textures node
3. Prompt: "cyberpunk neon aesthetic, volumetric lighting"
4. Re-render → AI transforms
```

---

## Node System (Advanced)

Dream Textures adds custom nodes to Shader Editor:
- **Dream Texture Node** - Generate textures in node graph
- **ControlNet Node** - Depth/Canny/Normal guidance
- **Upscale Node** - AI upscaling in pipeline

Enables complex procedural workflows.

---

## Model Backends

| Backend | Models | Notes |
|---------|--------|-------|
| **diffusers** (default) | SD 1.5, SDXL, SD 2.1, ControlNet | Local, free |
| **DreamStudio** | SDXL, SD 3 | Cloud, paid |
| **Community** | Flux, SD3, custom | Experimental |

---

## Configuration

### Preferences (Edit → Preferences → Add-ons → Dream Textures)
- **Device:** CUDA / MPS / CPU
- **Precision:** fp16 (default) / fp32 / bf16
- **Model Cache:** Custom path for model weights
- **DreamStudio API Key:** For cloud processing
- **Telemetry:** Opt-in/out

### Presets
Built-in presets in `builtin_presets/`:
- PBR Materials (metal, fabric, wood, stone)
- Environments (sky, ground, foliage)
- Styles (anime, photorealistic, pixel art)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **Out of VRAM** | Reduce resolution; use fp16; close other apps |
| **Model download fails** | Check internet; set HF_TOKEN for gated models |
| **macOS quarantine** | Run xattr command above |
| **Slow generation** | Use lower steps (20-30); smaller resolution |
| **Seams visible** | Enable "Seamless"; use inpainting to fix |

---

## Integration with GenesisCore / blender-mcp

Dream Textures runs **independently** - no MCP integration. Use via:
1. **Manual** - N-panel in Blender
2. **Python API** - Call operators from `execute_blender_code`:
   ```python
   bpy.ops.dream_texture.generate(
       prompt="brick wall, seamless",
       seamless=True,
       width=1024,
       height=1024
   )
   ```
3. **Combine workflows:**
   - GenesisCore for geometry/scene
   - Dream Textures for materials

---

## File Locations

| File | Path |
|------|------|
| Addon | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\dream_textures\` |
| Models | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\dream_textures\.python_dependencies\` |
| Presets | `builtin_presets/` in addon |
| Output | Blender temp / project folder |

---

## Related Wiki Pages
- [Texture Generation Workflow](../workflows/texture-generation.md)
- [GenesisCore + Dream Textures Combo](../workflows/scene-building.md)
- [Blender Material API](../api/materials.md)

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [BLENDER-MCP ADDON - DEEP DIVE](blender-mcp.md), [DREAM TEXTURES - FULL WIKI DOCUMENTATION](dream-textures-full.md), [GENESISCORE ADDON - DEEP DIVE](genesiscore.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [ANIMATION WORKFLOWS](../workflows/animation.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md)
- **Теги:** #addon, #reference, #stable-diffusion

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

