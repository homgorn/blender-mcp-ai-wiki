#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Human translations chunk B2: wf_02 -> es/de/zh."""
from pathlib import Path
W = Path(r"C:\BLENDER ai\WIKI") / "multilang"

ARCH = """```
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
```"""

PREPY = """```python
# preprocess.py
from PIL import Image
from rembg import remove

def preprocess_image(input_path, output_path, size=512):
    img = Image.open(input_path)
    img_no_bg = remove(img)
    img_square = make_square(img_no_bg, size)
    img_square.save(output_path, "PNG")
    return output_path

def make_square(img, size):
    w, h = img.size
    max_dim = max(w, h)
    new_img = Image.new('RGBA', (max_dim, max_dim), (0,0,0,0))
    new_img.paste(img, ((max_dim-w)//2, (max_dim-h)//2))
    return new_img.resize((size, size), Image.LANCZOS)
```"""

GENPY = """```python
# generate_mesh.py
from triposr import TripoSR
import numpy as np
import trimesh

def generate_3d(image_path, output_dir, steps=50):
    model = TripoSR.from_pretrained('VAST-AI/TripoSR')
    output = model.generate(image_path, num_inference_steps=steps)
    vertices = output['vertices']
    faces = output['faces']
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.export(f"{output_dir}/model.obj")
    mesh.export(f"{output_dir}/model.glb")
    if 'texture' in output:
        Image.fromarray(output['texture']).save(f"{output_dir}/texture.png")
    return mesh
```"""

WF02 = {
"es": {
"title": "WF 02: IMAGEN-A-3D",
"goal": "Convertir una imagen 2D (foto, boceto, concept art) en un modelo 3D mediante IA",
"arch_t": "ARQUITECTURA DEL PIPELINE",
"models_t": "MODELOS IA (2024/2025)",
"local": "LOCALES (gratis, requieren GPU)",
"cloud": "EN LA NUBE (API, mayor calidad)",
"h": ["Modelo", "Calidad", "Velocidad", "VRAM", "Instalación"],
"rows1": [["**TripoSR**", "⭐⭐⭐⭐", "~0.5s", "6GB", "`pip install triposr`"], ["**LRM (Large Reconstruction Model)**", "⭐⭐⭐⭐⭐", "~2s", "8GB", "`pip install lrm`"], ["**Zero123++**", "⭐⭐⭐", "~5s", "6GB", "`pip install zero123pp`"], ["**InstantMesh**", "⭐⭐⭐⭐", "~10s", "8GB", "`pip install instant-mesh`"]],
"h2": ["Servicio", "Calidad", "Coste", "API"],
"rows2": [["**Hunyuan3D 2.0**", "⭐⭐⭐⭐⭐", "Free tier", "Tencent Cloud"], ["**Hyper3D Rodin**", "⭐⭐⭐⭐⭐", "$0.5/gen", "hyper3d.ai"], ["**Meshy.ai**", "⭐⭐⭐⭐", "$0.2/gen", "meshy.ai"], ["**CSM (Common Sense Machines)**", "⭐⭐⭐⭐", "$0.3/gen", "csm.ai"], ["**Tripo AI**", "⭐⭐⭐⭐", "$0.1/gen", "tripo3d.ai"]],
"mcp_t": "COMANDOS MCP",
"gen_local": "GENERACIÓN LOCAL (TripoSR)",
"gen_install": "# Instalación\npip install triposr torch torchvision",
"gen_py": "# Generación con Python\npython -c \"\nfrom triposr import TripoSR\nmodel = TripoSR.from_pretrained('VAST-AI/TripoSR')\noutput = model.generate('input_image.png', num_inference_steps=50)\n# output: dict mesh con vertices, faces, textures\n\"",
"hyper": "MCP: HYPER3D / HUNYUAN3D (vía blender-mcp)",
"hyper_bash": '# En OpenCode / Cursor:\n"Genera un modelo 3D desde la imagen \'concept_art.png\' usando Hyper3D Rodin\n1. Carga la imagen\n2. Inicia la generación\n3. Espera a que termine\n4. Importa el resultado a Blender\n4. Auto-retopología a 10k tris\n5. UV Unwrap + PBR Texture Baking\n6. Exporta a GLB"',
"meshy": "MCP: MESHY.AI",
"meshy_bash": '"Usa Meshy.ai para generar 3D desde \'product_photo.jpg\':\n1. Carga la foto\n2. Parámetros: quality=high, texture_resolution=2048\n3. Descarga el resultado como GLB\n4. Importa a Blender\n5. Verifica UV y materiales"',
"pipe_t": "PIPELINE PASO A PASO (LOCAL TripoSR)",
"prep_t": "1. PREPARACIÓN DE LA IMAGEN",
"prep_c": "# Eliminación del fondo",
"prep_c2": "# Recorte cuadrado con padding",
"prep_c3": "# Guardar",
"prep_c4": "# Añadir fondo blanco/transparente para el cuadrado",
"gen_t": "2. GENERACIÓN DE LA MALLA (TripoSR)",
"gen_c": "# Generación",
"gen_c2": "# Conversión a trimesh",
"gen_c3": "# Exportación",
"gen_c4": "# Texturas (si hay)",
"post_t": "3. POST-PROCESADO EN BLENDER (MCP)",
"post_bash": '# En OpenCode:\n"Importa el model.glb generado a Blender:\n1. File → Import → glTF 2.0\n2. Auto-retopología: Quad Remesher target=10000 tris\n3. UV Unwrap: Smart Project angle=66 island_margin=0.01\n4. PBR Texture Baking: BaseColor, Roughness, Normal, Metallic, AO\n5. Material: Principled BSDF + Texture Nodes\n5. Exportación: GLB + texturas 2k separadas"',
"spec_t": "CALIDAD Y ESPECIFICACIONES",
"spec_h": ["Método", "Tris", "Texture Res", "UV Quality", "Time (RTX 3080)"],
"spec_r": [["**TripoSR (raw)**", "10k-50k", "512x512", "Auto UV", "0.5s"], ["**TripoSR + Retopo**", "5k-15k", "2k", "Clean UV", "30s"], ["**LRM**", "20k-100k", "1024x1024", "Good UV", "2s"], ["**Hunyuan3D 2.0**", "10k-50k", "2k-4k", "Excellent UV", "30s (API)"], ["**Hyper3D Rodin**", "10k-30k", "4k", "Production UV", "60s (API)"]],
"tips_t": "CONSEJOS",
"tips_h": ["Consejo", "Por qué"],
"tips_r": [["Usa `rembg` para quitar el fondo", "Silueta limpia = mejor geometría"], ["Múltiples vistas (front/side/back)", "LRM/Hunyuan soportan multi-view"], ["Entrada cuadrada 512x512", "Estándar de la mayoría de modelos"], ["Post-retopología obligatoria", "La malla raw no sirve para juegos/animación"], ["PBR Baking tras el UV", "Normales/cavidad desde la geometría"]],
"links": "- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR\n- **LRM:** https://github.com/lrm-dev/LRM\n- **InstantMesh:** https://github.com/TencentARC/InstantMesh\n- **Hunyuan3D:** https://3d.hunyuan.tencent.com/\n- **Hyper3D:** https://hyper3d.ai/\n- **Meshy:** https://www.meshy.ai/\n- **Setup 03:** [Dream Textures](../setups/setup_03_dream_textures.md)\n- **Siguiente:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)",
},
"de": {
"title": "WF 02: BILD-ZU-3D",
"goal": "Ein 2D-Bild (Foto, Sketch, Concept Art) per KI in ein 3D-Modell verwandeln",
"arch_t": "PIPELINE-ARCHITEKTUR",
"models_t": "KI-MODELLE (2024/2025)",
"local": "LOKAL (kostenlos, GPU erforderlich)",
"cloud": "CLOUD (API, höhere Qualität)",
"h": ["Modell", "Qualität", "Speed", "VRAM", "Installation"],
"rows1": [["**TripoSR**", "⭐⭐⭐⭐", "~0.5s", "6GB", "`pip install triposr`"], ["**LRM (Large Reconstruction Model)**", "⭐⭐⭐⭐⭐", "~2s", "8GB", "`pip install lrm`"], ["**Zero123++**", "⭐⭐⭐", "~5s", "6GB", "`pip install zero123pp`"], ["**InstantMesh**", "⭐⭐⭐⭐", "~10s", "8GB", "`pip install instant-mesh`"]],
"h2": ["Service", "Qualität", "Kosten", "API"],
"rows2": [["**Hunyuan3D 2.0**", "⭐⭐⭐⭐⭐", "Free tier", "Tencent Cloud"], ["**Hyper3D Rodin**", "⭐⭐⭐⭐⭐", "$0.5/gen", "hyper3d.ai"], ["**Meshy.ai**", "⭐⭐⭐⭐", "$0.2/gen", "meshy.ai"], ["**CSM (Common Sense Machines)**", "⭐⭐⭐⭐", "$0.3/gen", "csm.ai"], ["**Tripo AI**", "⭐⭐⭐⭐", "$0.1/gen", "tripo3d.ai"]],
"mcp_t": "MCP-BEFEHLE",
"gen_local": "LOKALE GENERIERUNG (TripoSR)",
"gen_install": "# Installation\npip install triposr torch torchvision",
"gen_py": "# Generierung via Python\npython -c \"\nfrom triposr import TripoSR\nmodel = TripoSR.from_pretrained('VAST-AI/TripoSR')\noutput = model.generate('input_image.png', num_inference_steps=50)\n# output: mesh-dict mit vertices, faces, textures\n\"",
"hyper": "MCP: HYPER3D / HUNYUAN3D (via blender-mcp)",
"hyper_bash": '# In OpenCode / Cursor:\n"Generiere ein 3D-Modell aus dem Bild \'concept_art.png\' mit Hyper3D Rodin\n1. Bild laden\n2. Generierung starten\n3. Auf Abschluss warten\n4. Ergebnis nach Blender importieren\n4. Auto-Retopologie auf 10k Tris\n5. UV Unwrap + PBR Texture Baking\n6. Als GLB exportieren"',
"meshy": "MCP: MESHY.AI",
"meshy_bash": '"Nutze Meshy.ai für 3D aus \'product_photo.jpg\':\n1. Foto laden\n2. Parameter: quality=high, texture_resolution=2048\n3. Ergebnis als GLB laden\n4. Nach Blender importieren\n5. UV und Materialien prüfen"',
"pipe_t": "SCHRITT-FÜR-SCHRITT-PIPELINE (LOKAL TripoSR)",
"prep_t": "1. BILDVORBEREITUNG",
"prep_c": "# Hintergrund entfernen",
"prep_c2": "# Quadratischer Crop mit Padding",
"prep_c3": "# Speichern",
"prep_c4": "# Weißer/transparenter Hintergrund für Quadrat",
"gen_t": "2. MESH-GENERIERUNG (TripoSR)",
"gen_c": "# Generierung",
"gen_c2": "# Konvertierung zu trimesh",
"gen_c3": "# Export",
"gen_c4": "# Texturen (falls vorhanden)",
"post_t": "3. POST-PROCESSING IN BLENDER (MCP)",
"post_bash": '# In OpenCode:\n"Importiere das generierte model.glb nach Blender:\n1. File → Import → glTF 2.0\n2. Auto-Retopologie: Quad Remesher target=10000 Tris\n3. UV Unwrap: Smart Project angle=66 island_margin=0.01\n4. PBR Texture Baking: BaseColor, Roughness, Normal, Metallic, AO\n5. Material: Principled BSDF + Texture Nodes\n5. Export: GLB + separate 2k-Texturen"',
"spec_t": "QUALITÄT UND SPEZIFIKATIONEN",
"spec_h": ["Methode", "Tris", "Texture Res", "UV Quality", "Time (RTX 3080)"],
"spec_r": [["**TripoSR (raw)**", "10k-50k", "512x512", "Auto UV", "0.5s"], ["**TripoSR + Retopo**", "5k-15k", "2k", "Clean UV", "30s"], ["**LRM**", "20k-100k", "1024x1024", "Good UV", "2s"], ["**Hunyuan3D 2.0**", "10k-50k", "2k-4k", "Excellent UV", "30s (API)"], ["**Hyper3D Rodin**", "10k-30k", "4k", "Production UV", "60s (API)"]],
"tips_t": "TIPPS",
"tips_h": ["Tipp", "Warum"],
"tips_r": [["`rembg` für Hintergrund nutzen", "Saubere Silhouette = bessere Geometrie"], ["Mehrere Ansichten (front/side/back)", "LRM/Hunyuan unterstützen Multi-View"], ["Quadratischer Input 512x512", "Standard der meisten Modelle"], ["Post-Retopologie ist Pflicht", "Raw-Mesh taugt nicht für Games/Animation"], ["PBR Baking nach UV", "Normals/Cavity aus Geometrie"]],
"links": "- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR\n- **LRM:** https://github.com/lrm-dev/LRM\n- **InstantMesh:** https://github.com/TencentARC/InstantMesh\n- **Hunyuan3D:** https://3d.hunyuan.tencent.com/\n- **Hyper3D:** https://hyper3d.ai/\n- **Meshy:** https://www.meshy.ai/\n- **Setup 03:** [Dream Textures](../setups/setup_03_dream_textures.md)\n- **Nächster:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)",
},
"zh": {
"title": "WF 02：图片转 3D",
"goal": "通过 AI 将 2D 图像（照片、草图、概念图）转为 3D 模型",
"arch_t": "管线架构",
"models_t": "AI 模型（2024/2025）",
"local": "本地（免费，需要 GPU）",
"cloud": "云端（API，质量更高）",
"h": ["模型", "质量", "速度", "显存", "安装"],
"rows1": [["**TripoSR**", "⭐⭐⭐⭐", "~0.5s", "6GB", "`pip install triposr`"], ["**LRM（Large Reconstruction Model）**", "⭐⭐⭐⭐⭐", "~2s", "8GB", "`pip install lrm`"], ["**Zero123++**", "⭐⭐⭐", "~5s", "6GB", "`pip install zero123pp`"], ["**InstantMesh**", "⭐⭐⭐⭐", "~10s", "8GB", "`pip install instant-mesh`"]],
"h2": ["服务", "质量", "费用", "API"],
"rows2": [["**Hunyuan3D 2.0**", "⭐⭐⭐⭐⭐", "免费层", "Tencent Cloud"], ["**Hyper3D Rodin**", "⭐⭐⭐⭐⭐", "$0.5/次", "hyper3d.ai"], ["**Meshy.ai**", "⭐⭐⭐⭐", "$0.2/次", "meshy.ai"], ["**CSM (Common Sense Machines)**", "⭐⭐⭐⭐", "$0.3/次", "csm.ai"], ["**Tripo AI**", "⭐⭐⭐⭐", "$0.1/次", "tripo3d.ai"]],
"mcp_t": "MCP 命令",
"gen_local": "本地生成（TripoSR）",
"gen_install": "# 安装\npip install triposr torch torchvision",
"gen_py": "# 通过 Python 生成\npython -c \"\nfrom triposr import TripoSR\nmodel = TripoSR.from_pretrained('VAST-AI/TripoSR')\noutput = model.generate('input_image.png', num_inference_steps=50)\n# output: 含 vertices、faces、textures 的 mesh 字典\n\"",
"hyper": "MCP：HYPER3D / HUNYUAN3D（经由 blender-mcp）",
"hyper_bash": '# 在 OpenCode / Cursor 中：\n"用 Hyper3D Rodin 从图像 \'concept_art.png\' 生成 3D 模型\n1. 加载图像\n2. 启动生成\n3. 等待完成\n4. 导入结果到 Blender\n4. 自动重拓扑到 10k tris\n5. UV 展开 + PBR 纹理烘焙\n6. 导出为 GLB"',
"meshy": "MCP：MESHY.AI",
"meshy_bash": '"用 Meshy.ai 从 \'product_photo.jpg\' 生成 3D：\n1. 加载照片\n2. 参数：quality=high, texture_resolution=2048\n3. 下载结果为 GLB\n4. 导入 Blender\n5. 检查 UV 和材质"',
"pipe_t": "分步管线（本地 TripoSR）",
"prep_t": "1. 图像预处理",
"prep_c": "# 去除背景",
"prep_c2": "# 带填充的方形裁剪",
"prep_c3": "# 保存",
"prep_c4": "# 为正方形添加白色/透明背景",
"gen_t": "2. 网格生成（TripoSR）",
"gen_c": "# 生成",
"gen_c2": "# 转为 trimesh",
"gen_c3": "# 导出",
"gen_c4": "# 纹理（如有）",
"post_t": "3. 在 BLENDER 中后处理（MCP）",
"post_bash": '# 在 OpenCode 中：\n"把生成的 model.glb 导入 Blender：\n1. File → Import → glTF 2.0\n2. 自动重拓扑：Quad Remesher target=10000 tris\n3. UV 展开：Smart Project angle=66 island_margin=0.01\n4. PBR 纹理烘焙：BaseColor, Roughness, Normal, Metallic, AO\n5. 材质：Principled BSDF + Texture Nodes\n5. 导出：GLB + 独立 2k 纹理"',
"spec_t": "质量与规格",
"spec_h": ["方法", "Tris", "纹理分辨率", "UV 质量", "用时 (RTX 3080)"],
"spec_r": [["**TripoSR (raw)**", "10k-50k", "512x512", "Auto UV", "0.5s"], ["**TripoSR + Retopo**", "5k-15k", "2k", "Clean UV", "30s"], ["**LRM**", "20k-100k", "1024x1024", "Good UV", "2s"], ["**Hunyuan3D 2.0**", "10k-50k", "2k-4k", "Excellent UV", "30s (API)"], ["**Hyper3D Rodin**", "10k-30k", "4k", "Production UV", "60s (API)"]],
"tips_t": "技巧",
"tips_h": ["技巧", "原因"],
"tips_r": [["用 `rembg` 去背景", "干净剪影 = 更好几何"], ["多视角（front/side/back）", "LRM/Hunyuan 支持多视角"], ["方形输入 512x512", "多数模型的标准"], ["后重拓扑是必须的", "原始网格不适合游戏/动画"], ["UV 之后做 PBR 烘焙", "法线/腔体来自几何"]],
"links": "- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR\n- **LRM:** https://github.com/lrm-dev/LRM\n- **InstantMesh:** https://github.com/TencentARC/InstantMesh\n- **Hunyuan3D:** https://3d.hunyuan.tencent.com/\n- **Hyper3D:** https://hyper3d.ai/\n- **Meshy:** https://www.meshy.ai/\n- **配置 03:** [Dream Textures](../setups/setup_03_dream_textures.md)\n- **下一个:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)",
},
}

WF02_META = {
 "es": ("Flujo IA", "⭐⭐", "10-30 min por asset", "OBJETIVO"),
 "de": ("KI-Pipeline", "⭐⭐", "10-30 Min pro Asset", "ZIEL"),
 "zh": ("AI 生成管线", "⭐⭐", "每个资产 10-30 分钟", "目标"),
}

for lang, d in WF02.items():
    typ, diff, t, goalw = WF02_META[lang]
    r1 = "\n".join("| " + " | ".join(r) + " |" for r in d["rows1"])
    r2 = "\n".join("| " + " | ".join(r) + " |" for r in d["rows2"])
    sr = "\n".join("| " + " | ".join(r) + " |" for r in d["spec_r"])
    tr = "\n".join("| " + " | ".join(r) + " |" for r in d["tips_r"])
    text = f"""---
id: wf_02_image_to_3d
lang: {lang}
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# {d['title']}

**ID:** WF-02 | **{typ.split()[0]}:** {typ} | **{diff}** | **{t}**

---

## 🎯 {goalw}
{d['goal']}

---

## 📋 {d['arch_t']}

{ARCH}

---

## 🤖 {d['models_t']}

### {d['local']}
| {' | '.join(d['h'])} |
|--------|----------|----------|------|-----------|
{r1}

### {d['cloud']}
| {' | '.join(d['h2'])} |
|--------|----------|-----------|-----|
{r2}

---

## 🔧 {d['mcp_t']}

### {d['gen_local']}
```bash
{d['gen_install']}

{d['gen_py']}
```

### {d['hyper']}
```bash
{d['hyper_bash']}
```

### {d['meshy']}
```bash
{d['meshy_bash']}
```

---

## 📝 {d['pipe_t']}

### {d['prep_t']}
```python
# preprocess.py
from PIL import Image
from rembg import remove

def preprocess_image(input_path, output_path, size=512):
    img = Image.open(input_path)
    {d['prep_c']}
    img_no_bg = remove(img)
    {d['prep_c2']}
    img_square = make_square(img_no_bg, size)
    {d['prep_c3']}
    img_square.save(output_path, "PNG")
    return output_path

def make_square(img, size):
    {d['prep_c4']}
    w, h = img.size
    max_dim = max(w, h)
    new_img = Image.new('RGBA', (max_dim, max_dim), (0,0,0,0))
    new_img.paste(img, ((max_dim-w)//2, (max_dim-h)//2))
    return new_img.resize((size, size), Image.LANCZOS)
```

### {d['gen_t']}
```python
# generate_mesh.py
from triposr import TripoSR
import numpy as np
import trimesh

def generate_3d(image_path, output_dir, steps=50):
    model = TripoSR.from_pretrained('VAST-AI/TripoSR')
    {d['gen_c']}
    output = model.generate(image_path, num_inference_steps=steps)
    {d['gen_c2']}
    vertices = output['vertices']
    faces = output['faces']
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    {d['gen_c3']}
    mesh.export(f"{{output_dir}}/model.obj")
    mesh.export(f"{{output_dir}}/model.glb")
    {d['gen_c4']}
    if 'texture' in output:
        Image.fromarray(output['texture']).save(f"{{output_dir}}/texture.png")
    return mesh
```

### {d['post_t']}
```bash
{d['post_bash']}
```

---

## 📊 {d['spec_t']}

| {' | '.join(d['spec_h'])} |
|-------|------|-------------|------------|-----------------|
{sr}

---

## 💡 {d['tips_t']}

| {' | '.join(d['tips_h'])} |
|-----|-----|
{tr}

---

## 🔗 LINKS

{d['links']}
"""
    (W / lang / "workflows" / "wf_02_image_to_3d.md").write_text(text, encoding="utf-8")
print("OK chunk B2: wf_02 x3")
