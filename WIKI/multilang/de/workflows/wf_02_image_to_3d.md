---
id: wf_02_image_to_3d
lang: de
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# WF 02: BILD-ZU-3D

**ID:** WF-02 | **KI-Pipeline:** KI-Pipeline | **⭐⭐** | **10-30 Min pro Asset**

---

## 🎯 ZIEL
Ein 2D-Bild (Foto, Sketch, Concept Art) per KI in ein 3D-Modell verwandeln

---

## 📋 PIPELINE-ARCHITEKTUR

```
INPUT IMAGE
     │
     ▼
┌─────────────────────────────────────┐
│      PREPROCESSING                  │
│  • Background removal (RMBG)        │
│  • Normalize aspect ratio           │
│  • Multiple views generation        │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│      AI 3D GENERATION               │
│  • TripoSR / LRM / Zero123++        │
│  • Hunyuan3D / Hyper3D (cloud)      │
│  • Mesh + Textures + UV             │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│      POST-PROCESSING                │
│  • Retopology (Quad Remesher)       │
│  • UV Unwrap                        │
│  • PBR Texture Baking               │
│  • LOD Generation                   │
└─────────────────────────────────────┘
     │
     ▼
OUTPUT: .glb / .fbx / .obj + PBR textures
```

---

## 🤖 KI-MODELLE (2024/2025)

### LOKAL (kostenlos, GPU erforderlich)
| Modell | Qualität | Speed | VRAM | Installation |
|--------|----------|----------|------|-----------|
| **TripoSR** | ⭐⭐⭐⭐ | ~0.5s | 6GB | `pip install triposr` |
| **LRM (Large Reconstruction Model)** | ⭐⭐⭐⭐⭐ | ~2s | 8GB | `pip install lrm` |
| **Zero123++** | ⭐⭐⭐ | ~5s | 6GB | `pip install zero123pp` |
| **InstantMesh** | ⭐⭐⭐⭐ | ~10s | 8GB | `pip install instant-mesh` |

### CLOUD (API, höhere Qualität)
| Service | Qualität | Kosten | API |
|--------|----------|-----------|-----|
| **Hunyuan3D 2.0** | ⭐⭐⭐⭐⭐ | Free tier | Tencent Cloud |
| **Hyper3D Rodin** | ⭐⭐⭐⭐⭐ | $0.5/gen | hyper3d.ai |
| **Meshy.ai** | ⭐⭐⭐⭐ | $0.2/gen | meshy.ai |
| **CSM (Common Sense Machines)** | ⭐⭐⭐⭐ | $0.3/gen | csm.ai |
| **Tripo AI** | ⭐⭐⭐⭐ | $0.1/gen | tripo3d.ai |

---

## 🔧 MCP-BEFEHLE

### LOKALE GENERIERUNG (TripoSR)
```bash
# Installation
pip install triposr torch torchvision

# Generierung via Python
python -c "
from triposr import TripoSR
model = TripoSR.from_pretrained('VAST-AI/TripoSR')
output = model.generate('input_image.png', num_inference_steps=50)
# output: mesh-dict mit vertices, faces, textures
"
```

### MCP: HYPER3D / HUNYUAN3D (via blender-mcp)
```bash
# In OpenCode / Cursor:
"Generiere ein 3D-Modell aus dem Bild 'concept_art.png' mit Hyper3D Rodin
1. Bild laden
2. Generierung starten
3. Auf Abschluss warten
4. Ergebnis nach Blender importieren
4. Auto-Retopologie auf 10k Tris
5. UV Unwrap + PBR Texture Baking
6. Als GLB exportieren"
```

### MCP: MESHY.AI
```bash
"Nutze Meshy.ai für 3D aus 'product_photo.jpg':
1. Foto laden
2. Parameter: quality=high, texture_resolution=2048
3. Ergebnis als GLB laden
4. Nach Blender importieren
5. UV und Materialien prüfen"
```

---

## 📝 SCHRITT-FÜR-SCHRITT-PIPELINE (LOKAL TripoSR)

### 1. BILDVORBEREITUNG
```python
# preprocess.py
from PIL import Image
from rembg import remove

def preprocess_image(input_path, output_path, size=512):
    img = Image.open(input_path)
    # Hintergrund entfernen
    img_no_bg = remove(img)
    # Quadratischer Crop mit Padding
    img_square = make_square(img_no_bg, size)
    # Speichern
    img_square.save(output_path, "PNG")
    return output_path

def make_square(img, size):
    # Weißer/transparenter Hintergrund für Quadrat
    w, h = img.size
    max_dim = max(w, h)
    new_img = Image.new('RGBA', (max_dim, max_dim), (0,0,0,0))
    new_img.paste(img, ((max_dim-w)//2, (max_dim-h)//2))
    return new_img.resize((size, size), Image.LANCZOS)
```

### 2. MESH-GENERIERUNG (TripoSR)
```python
# generate_mesh.py
from triposr import TripoSR
import numpy as np
import trimesh

def generate_3d(image_path, output_dir, steps=50):
    model = TripoSR.from_pretrained('VAST-AI/TripoSR')
    # Generierung
    output = model.generate(image_path, num_inference_steps=steps)
    # Konvertierung zu trimesh
    vertices = output['vertices']
    faces = output['faces']
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    # Export
    mesh.export(f"{output_dir}/model.obj")
    mesh.export(f"{output_dir}/model.glb")
    # Texturen (falls vorhanden)
    if 'texture' in output:
        Image.fromarray(output['texture']).save(f"{output_dir}/texture.png")
    return mesh
```

### 3. POST-PROCESSING IN BLENDER (MCP)
```bash
# In OpenCode:
"Importiere das generierte model.glb nach Blender:
1. File → Import → glTF 2.0
2. Auto-Retopologie: Quad Remesher target=10000 Tris
3. UV Unwrap: Smart Project angle=66 island_margin=0.01
4. PBR Texture Baking: BaseColor, Roughness, Normal, Metallic, AO
5. Material: Principled BSDF + Texture Nodes
5. Export: GLB + separate 2k-Texturen"
```

---

## 📊 QUALITÄT UND SPEZIFIKATIONEN

| Methode | Tris | Texture Res | UV Quality | Time (RTX 3080) |
|-------|------|-------------|------------|-----------------|
| **TripoSR (raw)** | 10k-50k | 512x512 | Auto UV | 0.5s |
| **TripoSR + Retopo** | 5k-15k | 2k | Clean UV | 30s |
| **LRM** | 20k-100k | 1024x1024 | Good UV | 2s |
| **Hunyuan3D 2.0** | 10k-50k | 2k-4k | Excellent UV | 30s (API) |
| **Hyper3D Rodin** | 10k-30k | 4k | Production UV | 60s (API) |

---

## 💡 TIPPS

| Tipp | Warum |
|-----|-----|
| `rembg` für Hintergrund nutzen | Saubere Silhouette = bessere Geometrie |
| Mehrere Ansichten (front/side/back) | LRM/Hunyuan unterstützen Multi-View |
| Quadratischer Input 512x512 | Standard der meisten Modelle |
| Post-Retopologie ist Pflicht | Raw-Mesh taugt nicht für Games/Animation |
| PBR Baking nach UV | Normals/Cavity aus Geometrie |

---

## 🔗 LINKS

- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR
- **LRM:** https://github.com/lrm-dev/LRM
- **InstantMesh:** https://github.com/TencentARC/InstantMesh
- **Hunyuan3D:** https://3d.hunyuan.tencent.com/
- **Hyper3D:** https://hyper3d.ai/
- **Meshy:** https://www.meshy.ai/
- **Setup 03:** [Dream Textures](../setups/setup_03_dream_textures.md)
- **Nächster:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
