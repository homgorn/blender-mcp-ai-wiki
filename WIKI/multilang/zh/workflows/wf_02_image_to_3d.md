---
id: wf_02_image_to_3d
lang: zh
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# WF 02：图片转 3D

**ID:** WF-02 | **AI:** AI 生成管线 | **⭐⭐** | **每个资产 10-30 分钟**

---

## 🎯 目标
通过 AI 将 2D 图像（照片、草图、概念图）转为 3D 模型

---

## 📋 管线架构

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

## 🤖 AI 模型（2024/2025）

### 本地（免费，需要 GPU）
| 模型 | 质量 | 速度 | 显存 | 安装 |
|--------|----------|----------|------|-----------|
| **TripoSR** | ⭐⭐⭐⭐ | ~0.5s | 6GB | `pip install triposr` |
| **LRM（Large Reconstruction Model）** | ⭐⭐⭐⭐⭐ | ~2s | 8GB | `pip install lrm` |
| **Zero123++** | ⭐⭐⭐ | ~5s | 6GB | `pip install zero123pp` |
| **InstantMesh** | ⭐⭐⭐⭐ | ~10s | 8GB | `pip install instant-mesh` |

### 云端（API，质量更高）
| 服务 | 质量 | 费用 | API |
|--------|----------|-----------|-----|
| **Hunyuan3D 2.0** | ⭐⭐⭐⭐⭐ | 免费层 | Tencent Cloud |
| **Hyper3D Rodin** | ⭐⭐⭐⭐⭐ | $0.5/次 | hyper3d.ai |
| **Meshy.ai** | ⭐⭐⭐⭐ | $0.2/次 | meshy.ai |
| **CSM (Common Sense Machines)** | ⭐⭐⭐⭐ | $0.3/次 | csm.ai |
| **Tripo AI** | ⭐⭐⭐⭐ | $0.1/次 | tripo3d.ai |

---

## 🔧 MCP 命令

### 本地生成（TripoSR）
```bash
# 安装
pip install triposr torch torchvision

# 通过 Python 生成
python -c "
from triposr import TripoSR
model = TripoSR.from_pretrained('VAST-AI/TripoSR')
output = model.generate('input_image.png', num_inference_steps=50)
# output: 含 vertices、faces、textures 的 mesh 字典
"
```

### MCP：HYPER3D / HUNYUAN3D（经由 blender-mcp）
```bash
# 在 OpenCode / Cursor 中：
"用 Hyper3D Rodin 从图像 'concept_art.png' 生成 3D 模型
1. 加载图像
2. 启动生成
3. 等待完成
4. 导入结果到 Blender
4. 自动重拓扑到 10k tris
5. UV 展开 + PBR 纹理烘焙
6. 导出为 GLB"
```

### MCP：MESHY.AI
```bash
"用 Meshy.ai 从 'product_photo.jpg' 生成 3D：
1. 加载照片
2. 参数：quality=high, texture_resolution=2048
3. 下载结果为 GLB
4. 导入 Blender
5. 检查 UV 和材质"
```

---

## 📝 分步管线（本地 TripoSR）

### 1. 图像预处理
```python
# preprocess.py
from PIL import Image
from rembg import remove

def preprocess_image(input_path, output_path, size=512):
    img = Image.open(input_path)
    # 去除背景
    img_no_bg = remove(img)
    # 带填充的方形裁剪
    img_square = make_square(img_no_bg, size)
    # 保存
    img_square.save(output_path, "PNG")
    return output_path

def make_square(img, size):
    # 为正方形添加白色/透明背景
    w, h = img.size
    max_dim = max(w, h)
    new_img = Image.new('RGBA', (max_dim, max_dim), (0,0,0,0))
    new_img.paste(img, ((max_dim-w)//2, (max_dim-h)//2))
    return new_img.resize((size, size), Image.LANCZOS)
```

### 2. 网格生成（TripoSR）
```python
# generate_mesh.py
from triposr import TripoSR
import numpy as np
import trimesh

def generate_3d(image_path, output_dir, steps=50):
    model = TripoSR.from_pretrained('VAST-AI/TripoSR')
    # 生成
    output = model.generate(image_path, num_inference_steps=steps)
    # 转为 trimesh
    vertices = output['vertices']
    faces = output['faces']
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    # 导出
    mesh.export(f"{output_dir}/model.obj")
    mesh.export(f"{output_dir}/model.glb")
    # 纹理（如有）
    if 'texture' in output:
        Image.fromarray(output['texture']).save(f"{output_dir}/texture.png")
    return mesh
```

### 3. 在 BLENDER 中后处理（MCP）
```bash
# 在 OpenCode 中：
"把生成的 model.glb 导入 Blender：
1. File → Import → glTF 2.0
2. 自动重拓扑：Quad Remesher target=10000 tris
3. UV 展开：Smart Project angle=66 island_margin=0.01
4. PBR 纹理烘焙：BaseColor, Roughness, Normal, Metallic, AO
5. 材质：Principled BSDF + Texture Nodes
5. 导出：GLB + 独立 2k 纹理"
```

---

## 📊 质量与规格

| 方法 | Tris | 纹理分辨率 | UV 质量 | 用时 (RTX 3080) |
|-------|------|-------------|------------|-----------------|
| **TripoSR (raw)** | 10k-50k | 512x512 | Auto UV | 0.5s |
| **TripoSR + Retopo** | 5k-15k | 2k | Clean UV | 30s |
| **LRM** | 20k-100k | 1024x1024 | Good UV | 2s |
| **Hunyuan3D 2.0** | 10k-50k | 2k-4k | Excellent UV | 30s (API) |
| **Hyper3D Rodin** | 10k-30k | 4k | Production UV | 60s (API) |

---

## 💡 技巧

| 技巧 | 原因 |
|-----|-----|
| 用 `rembg` 去背景 | 干净剪影 = 更好几何 |
| 多视角（front/side/back） | LRM/Hunyuan 支持多视角 |
| 方形输入 512x512 | 多数模型的标准 |
| 后重拓扑是必须的 | 原始网格不适合游戏/动画 |
| UV 之后做 PBR 烘焙 | 法线/腔体来自几何 |

---

## 🔗 LINKS

- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR
- **LRM:** https://github.com/lrm-dev/LRM
- **InstantMesh:** https://github.com/TencentARC/InstantMesh
- **Hunyuan3D:** https://3d.hunyuan.tencent.com/
- **Hyper3D:** https://hyper3d.ai/
- **Meshy:** https://www.meshy.ai/
- **配置 03:** [Dream Textures](../setups/setup_03_dream_textures.md)
- **下一个:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
