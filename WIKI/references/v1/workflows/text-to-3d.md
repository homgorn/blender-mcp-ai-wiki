---
lang: en
tags: [ai-3d, blender, mcp, reference]
---
# TEXT-TO-3D WORKFLOWS

## Overview
Multiple approaches for generating 3D models from text prompts.

---

## Method 1: Hyper3D Rodin (via blender-mcp)
**Best for:** Quick concept models, game-ready assets
**Cost:** API credits (free tier available)
**Quality:** Medium-high, clean topology

### Workflow
```bash
# 1. Enable in Blender
N-panel → MCP for Blender → Check "Use Hyper3D" → Add API key (Preferences)

# 2. Via AI (OpenCode/Claude):
"Generate a 3D model of a medieval fantasy sword using Hyper3D Rodin"
# → Creates job → Polls status → Imports result

# 3. Post-process:
"Decimate the sword to 2000 tris, add bevel, create metal material"
```

### Parameters
- `prompt`: Text description
- `seed`: For reproducibility
- `generate_textures`: Optional PBR generation

---

## Method 2: Hunyuan3D (via blender-mcp)
**Best for:** High-quality assets, Chinese/Asian themes
**Cost:** SecretId/SecretKey required
**Quality:** High, good for production

### Workflow
```bash
# 1. Get credentials: https://3d.hunyuan.tencent.com/
# 2. Enable in Blender: Check "Use Hunyuan3D" → Add SecretId/SecretKey/API URL

# 3. Via AI:
"Create a 3D model of a Chinese dragon using Hunyuan3D"
# → Job → Poll → Import

# 4. Cleanup:
"Separate loose parts, apply scale, create materials for each part"
```

---

## Method 3: TripoSR (Local, Free)
**Best for:** Privacy, offline, experimentation
**Cost:** Free (runs locally)
**Quality:** Lower, good for concepts
**Hardware:** 8GB+ VRAM recommended

### Installation
```bash
# Option A: pip
pip install triposr

# Option B: Clone repo
git clone https://github.com/VAST-AI-Research/TripoSR
cd TripoSR
pip install -r requirements.txt

# Download weights (auto on first run)
```

### Usage via Python
```python
# Execute via execute_blender_code
import bpy
from triposr import TripoSR

model = TripoSR.from_pretrained("VAST-AI/TripoSR")
output = model.generate("a cute robot", num_inference_steps=50)
# output is mesh dict → import to Blender
```

### Blender Integration
```python
# Save as .obj/.glb then import
import bpy
bpy.ops.wm.obj_import(filepath="output.obj")
# or
bpy.ops.import_scene.gltf(filepath="output.glb")
```

---

## Method 4: MeshGPT / Shap-E (Local)
**Best for:** Research, custom training
**Cost:** Free
**Quality:** Experimental

### Shap-E (OpenAI)
```bash
git clone https://github.com/openai/shap-e
cd shap-e
pip install -e .
# Download weights
```

```python
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import decode_latent_mesh

xm = load_model('transmitter', device='cuda')
model = load_model('text300M', device='cuda')
diffusion = diffusion_from_config(load_config('diffusion'))

latents = sample_latents(
    batch_size=1,
    model=model,
    diffusion=diffusion,
    prompt="a red sports car",
    guidance_scale=15.0,
    device='cuda'
)

for i, latent in enumerate(latents):
    mesh = decode_latent_mesh(xm, latent).tri_mesh()
    with open(f'car_{i}.obj', 'w') as f:
        mesh.write_obj(f)
```

---

## Method 5: LGM (Large Gaussian Model)
**Best for:** High-quality, fast (Gaussian splatting)
**Cost:** Free (local)

```bash
git clone https://github.com/ashawkey/LGM
cd LGM
pip install -r requirements.txt
```

---

## Comparison Matrix

| Method | Local/Cloud | Cost | Quality | Speed | Topology | UVs |
|--------|-------------|------|---------|-------|----------|-----|
| **Hyper3D** | Cloud | $ | ⭐⭐⭐⭐ | Fast | Good | Yes |
| **Hunyuan3D** | Cloud | $ | ⭐⭐⭐⭐⭐ | Medium | Excellent | Yes |
| **TripoSR** | Local | Free | ⭐⭐⭐ | Fast | Basic | Basic |
| **Shap-E** | Local | Free | ⭐⭐ | Slow | Basic | No |
| **LGM** | Local | Free | ⭐⭐⭐⭐ | Fast | N/A (splats) | N/A |

---

## Recommended Pipeline (2026)

### For Production Assets
```
1. Generate base: Hyper3D or Hunyuan3D (cloud)
2. Import → Blender
3. Cleanup: Decimate, Separate, Scale, Origin
4. Retopology: Quad Remesher / Instant Meshes
5. UV: Smart UV Project / Manual
6. Bake: Normal, AO, Curvature from high-poly
7. Texture: Substance Painter / Dream Textures
6. Export: GLTF (game) / USD (pipeline)
```

### For Rapid Prototyping
```
1. TripoSR (local, free) → quick concept
2. If promising → Hyper3D for quality
3. GenesisCore for scene assembly
4. Dream Textures for materials
```

### For Privacy/Local-First
```
1. Ollama (llama3.2/codellama) via GenesisCore
2. TripoSR for 3D gen
3. Dream Textures (local SD) for textures
4. All offline, no API keys
```

---

## Automation Script Template

```python
# Execute via execute_blender_code
import bpy
import requests
import time

def generate_hyper3d(prompt, api_key):
    # Submit job
    resp = requests.post(
        "https://api.hyper3d.ai/v1/jobs",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"prompt": prompt, "generate_textures": True}
    )
    job_id = resp.json()["job_id"]
    
    # Poll
    while True:
        time.sleep(10)
        status = requests.get(
            f"https://api.hyper3d.ai/v1/jobs/{job_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        ).json()
        if status["status"] == "completed":
            return status["result_url"]
        elif status["status"] == "failed":
            raise Exception(status["error"])

# Usage
url = generate_hyper3d("futuristic motorcycle", "YOUR_KEY")
# Download and import
import urllib.request
urllib.request.urlretrieve(url, "/tmp/model.glb")
bpy.ops.import_scene.gltf(filepath="/tmp/model.glb")
```

---

## Post-Generation Checklist

- [ ] **Scale:** Apply scale (Ctrl+A → Scale), target real-world size
- [ ] **Origin:** Set to geometry center (Right-click → Set Origin → Origin to Geometry)
- [ ] **Topology:** Check tris/quads, decimate if needed
- [ ] **Separation:** Separate loose parts (P → By Loose Parts) for materials
- [ ] **Naming:** Rename objects logically
- [ ] **Materials:** Assign/create PBR materials
- [ ] **UVs:** Unwrap (Smart UV Project), check for overlaps
- [ ] **LODs:** Create LOD versions (50%, 25%, 10%)
- [ ] **Export:** GLTF for web/game, USD for pipeline

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](../../../setups/setup_45_hunyuan3d_21.md), [WORKFLOWS - PRODUCTION PIPELINES](scene-building.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md)
- **Теги:** #ai-3d, #blender, #mcp, #reference

---

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность ⭐⭐⭐⭐.

