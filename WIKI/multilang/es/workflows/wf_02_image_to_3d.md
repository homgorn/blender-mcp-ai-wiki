---
id: wf_02_image_to_3d
lang: es
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# WF 02: IMAGEN-A-3D

**ID:** WF-02 | **Flujo:** Flujo IA | **⭐⭐** | **10-30 min por asset**

---

## 🎯 OBJETIVO
Convertir una imagen 2D (foto, boceto, concept art) en un modelo 3D mediante IA

---

## 📋 ARQUITECTURA DEL PIPELINE

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

## 🤖 MODELOS IA (2024/2025)

### LOCALES (gratis, requieren GPU)
| Modelo | Calidad | Velocidad | VRAM | Instalación |
|--------|----------|----------|------|-----------|
| **TripoSR** | ⭐⭐⭐⭐ | ~0.5s | 6GB | `pip install triposr` |
| **LRM (Large Reconstruction Model)** | ⭐⭐⭐⭐⭐ | ~2s | 8GB | `pip install lrm` |
| **Zero123++** | ⭐⭐⭐ | ~5s | 6GB | `pip install zero123pp` |
| **InstantMesh** | ⭐⭐⭐⭐ | ~10s | 8GB | `pip install instant-mesh` |

### EN LA NUBE (API, mayor calidad)
| Servicio | Calidad | Coste | API |
|--------|----------|-----------|-----|
| **Hunyuan3D 2.0** | ⭐⭐⭐⭐⭐ | Free tier | Tencent Cloud |
| **Hyper3D Rodin** | ⭐⭐⭐⭐⭐ | $0.5/gen | hyper3d.ai |
| **Meshy.ai** | ⭐⭐⭐⭐ | $0.2/gen | meshy.ai |
| **CSM (Common Sense Machines)** | ⭐⭐⭐⭐ | $0.3/gen | csm.ai |
| **Tripo AI** | ⭐⭐⭐⭐ | $0.1/gen | tripo3d.ai |

---

## 🔧 COMANDOS MCP

### GENERACIÓN LOCAL (TripoSR)
```bash
# Instalación
pip install triposr torch torchvision

# Generación con Python
python -c "
from triposr import TripoSR
model = TripoSR.from_pretrained('VAST-AI/TripoSR')
output = model.generate('input_image.png', num_inference_steps=50)
# output: dict mesh con vertices, faces, textures
"
```

### MCP: HYPER3D / HUNYUAN3D (vía blender-mcp)
```bash
# En OpenCode / Cursor:
"Genera un modelo 3D desde la imagen 'concept_art.png' usando Hyper3D Rodin
1. Carga la imagen
2. Inicia la generación
3. Espera a que termine
4. Importa el resultado a Blender
4. Auto-retopología a 10k tris
5. UV Unwrap + PBR Texture Baking
6. Exporta a GLB"
```

### MCP: MESHY.AI
```bash
"Usa Meshy.ai para generar 3D desde 'product_photo.jpg':
1. Carga la foto
2. Parámetros: quality=high, texture_resolution=2048
3. Descarga el resultado como GLB
4. Importa a Blender
5. Verifica UV y materiales"
```

---

## 📝 PIPELINE PASO A PASO (LOCAL TripoSR)

### 1. PREPARACIÓN DE LA IMAGEN
```python
# preprocess.py
from PIL import Image
from rembg import remove

def preprocess_image(input_path, output_path, size=512):
    img = Image.open(input_path)
    # Eliminación del fondo
    img_no_bg = remove(img)
    # Recorte cuadrado con padding
    img_square = make_square(img_no_bg, size)
    # Guardar
    img_square.save(output_path, "PNG")
    return output_path

def make_square(img, size):
    # Añadir fondo blanco/transparente para el cuadrado
    w, h = img.size
    max_dim = max(w, h)
    new_img = Image.new('RGBA', (max_dim, max_dim), (0,0,0,0))
    new_img.paste(img, ((max_dim-w)//2, (max_dim-h)//2))
    return new_img.resize((size, size), Image.LANCZOS)
```

### 2. GENERACIÓN DE LA MALLA (TripoSR)
```python
# generate_mesh.py
from triposr import TripoSR
import numpy as np
import trimesh

def generate_3d(image_path, output_dir, steps=50):
    model = TripoSR.from_pretrained('VAST-AI/TripoSR')
    # Generación
    output = model.generate(image_path, num_inference_steps=steps)
    # Conversión a trimesh
    vertices = output['vertices']
    faces = output['faces']
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    # Exportación
    mesh.export(f"{output_dir}/model.obj")
    mesh.export(f"{output_dir}/model.glb")
    # Texturas (si hay)
    if 'texture' in output:
        Image.fromarray(output['texture']).save(f"{output_dir}/texture.png")
    return mesh
```

### 3. POST-PROCESADO EN BLENDER (MCP)
```bash
# En OpenCode:
"Importa el model.glb generado a Blender:
1. File → Import → glTF 2.0
2. Auto-retopología: Quad Remesher target=10000 tris
3. UV Unwrap: Smart Project angle=66 island_margin=0.01
4. PBR Texture Baking: BaseColor, Roughness, Normal, Metallic, AO
5. Material: Principled BSDF + Texture Nodes
5. Exportación: GLB + texturas 2k separadas"
```

---

## 📊 CALIDAD Y ESPECIFICACIONES

| Método | Tris | Texture Res | UV Quality | Time (RTX 3080) |
|-------|------|-------------|------------|-----------------|
| **TripoSR (raw)** | 10k-50k | 512x512 | Auto UV | 0.5s |
| **TripoSR + Retopo** | 5k-15k | 2k | Clean UV | 30s |
| **LRM** | 20k-100k | 1024x1024 | Good UV | 2s |
| **Hunyuan3D 2.0** | 10k-50k | 2k-4k | Excellent UV | 30s (API) |
| **Hyper3D Rodin** | 10k-30k | 4k | Production UV | 60s (API) |

---

## 💡 CONSEJOS

| Consejo | Por qué |
|-----|-----|
| Usa `rembg` para quitar el fondo | Silueta limpia = mejor geometría |
| Múltiples vistas (front/side/back) | LRM/Hunyuan soportan multi-view |
| Entrada cuadrada 512x512 | Estándar de la mayoría de modelos |
| Post-retopología obligatoria | La malla raw no sirve para juegos/animación |
| PBR Baking tras el UV | Normales/cavidad desde la geometría |

---

## 🔗 LINKS

- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR
- **LRM:** https://github.com/lrm-dev/LRM
- **InstantMesh:** https://github.com/TencentARC/InstantMesh
- **Hunyuan3D:** https://3d.hunyuan.tencent.com/
- **Hyper3D:** https://hyper3d.ai/
- **Meshy:** https://www.meshy.ai/
- **Setup 03:** [Dream Textures](../setups/setup_03_dream_textures.md)
- **Siguiente:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
