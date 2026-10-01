---
lang: en
tags: [reference, stable-diffusion]
---
# DREAM TEXTURES - FULL WIKI DOCUMENTATION

## Overview
**Repo:** https://github.com/carson-katri/dream-textures
**Wiki:** https://github.com/carson-katri/dream-textures/wiki
**Version:** Latest | **Blender:** 3.3+ | **License:** GPL-3.0

---

## Setup Guide (from Wiki)

### Installation
1. Download from [latest release](https://github.com/carson-katri/dream-textures/releases/latest)
2. Windows: Extract 7-Zip archive → get `.zip` → Install in Blender Preferences → Add-ons
3. Enable **Dream Textures** in add-ons
4. **DO NOT** manually install dependencies - use prebuilt version only

### Download Models
In add-on preferences, search and download:
- `stabilityai/stable-diffusion-2-1-base` - Primary 512x512 model
- `stabilityai/stable-diffusion-2-inpainting` - For inpainting/outpainting
- `stabilityai/stable-diffusion-2-depth` - For texture projection, depth-to-image
- `stabilityai/stable-diffusion-x4-upscaler` - For 4x AI upscaling
- `stabilityai/stable-diffusion-2-1` - Fine-tuned for 768x768

### Private Models
- Generate Hugging Face token at https://huggingface.co/settings/tokens
- Paste in "Token" field in preferences

### Import Checkpoints (.ckpt)
- Click "Import Checkpoint File" in preferences
- Select file → specify Model Config:
  - `v1` - Original CompVis models (SD 1.x)
  - `v2 (512, epsilon)` - 512x512 models with prediction_type="epsilon"
  - `v2 (768, v_prediction)` - 768x768 models with prediction_type="v_prediction"

### DreamStudio (Cloud)
- Enter API key from https://beta.dreamstudio.ai/membership?tab=apiKeys
- Processes in cloud if local hardware insufficient

---

## Image Generation (from Wiki)

### Access
- Open Image Editor or Shader Editor
- Press `N` for sidebar → **Dream** panel

### Options

| Option | Description |
|--------|-------------|
| **Pipeline** | Stable Diffusion (local) or DreamStudio (cloud) |
| **Model** | Choose installed model (some features require specific models) |
| **Prompt** | Text prompt. Presets available (e.g., "Texture" adds "texture" suffix) |
| **Seamless** | Circular convolution for perfect tiling. Can specify axes |
| **Negative** | What to avoid (e.g., "building" to remove buildings) |
| **Size** | Target dimensions (multiples of 64). Best at 512x512 |
| **Source Image** | File or Open Image for img2img |

#### Source Image Modes
1. **Color** - Mix image with noise
2. **Color + Generated Depth** - MiDaS depth + color (requires depth model)
3. **Color + Depth Map** - Custom depth map image
3. **Depth** - Treat image as depth map only

#### Advanced Parameters
| Parameter | Description |
|-----------|-------------|
| **Random Seed** | Auto-generate or manual seed |
| **Steps** | Sampler steps (more = better convergence) |
| **CFG Scale** | Prompt adherence strength |
| **Scheduler** | Different convergence speeds |
| **Step Preview** | "Fast" (latent preview) or "Accurate" (VAE decode each step) |
| **Speed Optimizations** | Half Precision recommended |
| **Memory Optimizations** | Attention Slicing (Auto) recommended |

---

## Texture Projection (from Wiki)

### Workflow
1. Select objects in 3D Viewport
2. Enter Edit Mode → select faces to target
3. Local View (`/`) to limit depth map to selection
4. **Tip:** Subdivide large faces if projection warps

### Settings
- Choose **depth model** (e.g., `stable-diffusion-2-depth`)
- Enter prompt
- **Data source:** "Depth" (default) or "Depth and Color" (uses viewport shading)
- Adjust image size to match viewport aspect ratio

### Execution
- Click **Project Dream Texture**
- New material created with seed name
- UVs updated for projection angle
- Live preview in Viewport Shading mode

---

## Inpaint and Outpaint (from Wiki)

### Inpainting
- Mask area in Image Editor
- Requires `stable-diffusion-2-inpainting` model
- Prompt: "seamless continuation of [texture]"
- **Making Textures Seamless:** Inpaint edges to blend

### Outpainting
- Extend image beyond boundaries
- Choose origin (center, corners, edges)
- Generates new content matching style

---

## Render Engine / Node System (from Wiki)

### Nodes Added
- **Dream Texture Node** - Generate textures in shader graph
- **ControlNet Node** - Depth/Canny/Normal guidance
- **Upscale Node** - AI upscaling in pipeline

### Render Pass Integration
- Use Cycles render as ControlNet input
- Re-style via img2img
- Animation: frame-by-frame re-styling

#### Controls
| Parameter | Effect |
|-----------|--------|
| **Depth** | Use depth pass for structure |
| **Noise Strength** | Deviation from render (0-1) |
| **Seed** | Reproducibility |

---

## AI Upscaling (from Wiki)
- 4x upscale via ESRGAN/RealESRGAN
- **Tile Size** option for large images

---

## History (from Wiki)
- Recall, export, import generations
- **Export:** Save prompt + params + seed
- **Import:** Restore previous generation settings

---

## Development Setup (from Wiki)
```bash
git clone https://github.com/carson-katri/dream-textures
cd dream-textures
# Install to Blender
# Install dependencies: pip install -r requirements.txt
```

---

## Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **VRAM** | 4 GB | 8-12 GB |
| **GPU** | CUDA 11.7+ / Apple Silicon | RTX 3080+ / M2 Max+ |
| **RAM** | 8 GB | 16-32 GB |
| **Disk** | 10 GB | 20 GB+ |

---

## Troubleshooting
| Issue | Fix |
|-------|-----|
| OOM / CUDA OOM | Reduce resolution; fp16; close apps |
| Model download fails | Check internet; HF_TOKEN for gated models |
| macOS quarantine | `xattr -r -d com.apple.quarantine <addon_path>/.python_dependencies` |
| Slow generation | Lower steps (20-30); smaller resolution |
| Seams visible | Enable Seamless; inpaint edges |

---

## Integration with MCP
Dream Textures is **standalone** - no MCP integration.
Use via:
1. Manual N-panel
2. Python API via `execute_blender_code`:
```python
bpy.ops.dream_texture.generate(
    prompt="brick wall, seamless",
    seamless=True,
    width=1024,
    height=1024
)
```
3. Combined workflow: GenesisCore for geometry → Dream Textures for materials

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [DREAM TEXTURES ADDON - DEEP DIVE](dream-textures.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [ANIMATION WORKFLOWS](../workflows/animation.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md)
- **По темам:** [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](../api/scripting-patterns.md), [BLENDER-MCP - FULL DOCUMENTATION](blender-mcp-full.md)
- **Теги:** #reference, #stable-diffusion

