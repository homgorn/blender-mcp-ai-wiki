---
id: wf_02_image_to_3d
lang: en
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: template
---
# WF 02: IMAGE-TO-3D

> Goal: ## 🌍 MULTILANG

**ID:** wf_02_image_to_3d | **Lang:** en | **Orig:** ru | **Category:** workflows | **Tags:** 

---

# WF 02: IMAGE-TO-3D

**ID:** WF-02 | **Type:** AI Generation Pipeline | **Difficulty:** ⭐⭐ | **Time:** 10-30 min per asset

---

## 🎯 ЦЕЛЬ
Превратить 2D изображение (фото, скетч, концепт-арт) в 3D модель через AI

---

## 📋 ПАЙПЛАЙН АРХИТЕКТУРА

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

## 🤖 AI МОДЕЛИ (2024/2025)

### ЛОКАЛЬНЫЕ (бесплатно, требуют GPU)
| Модель | Качество | Скорость | VRAM | Установка |
|--------|----------|----------|------|-----------|
| **TripoSR** | ⭐⭐⭐⭐ | ~0.5s | 6GB | `pip install triposr` |
| **LRM (Large Reconstruction Model)** | ⭐⭐⭐⭐⭐ | ~2s | 8GB | `pip install lrm` |
| **Zero123++** | ⭐⭐⭐ | ~5s | 6GB | `pip install zero123pp` |
| **InstantMesh** | ⭐⭐⭐⭐ | ~10s | 8GB | `pip install instant-mesh` |

### ОБЛАЧНЫЕ (API, выше качество)
| Сервис | Качество | Стоимость | API |
|--------|----------|-----------|-----|
| **Hunyuan3D 2.0** | ⭐⭐⭐⭐⭐ | Free tier | Tencent Cloud |
| **Hyper3D Rodin** | ⭐⭐⭐⭐⭐ | $0.5/gen | hyper3d.ai |
| **Meshy.ai** | ⭐⭐⭐⭐ | $0.2/gen | meshy.ai |
| **CSM (Common Sense Machines)** | ⭐⭐⭐⭐ | $0.3/gen | csm.ai |
| **Tripo AI** | ⭐⭐⭐⭐ | $0.1/gen | tripo3d.ai |

---

## 🔧 MCP КОМАНДЫ

### ЛОКАЛЬНАЯ ГЕНЕРАЦИЯ (TripoSR)
```bash
# Установка
pip install triposr torch torchvision

# Генерация через Python
python -c "
from triposr import TripoSR
model = TripoSR.from_pretrained('VAST-AI/TripoSR')
output = model.generate('input_image.png', num_inference_steps=50)
# output: mesh dict с vertices, faces, textures
"
```

### MCP: HYPER3D / HUNYUAN3D (через blender-mcp)
```bash
# В OpenCode / Cursor:
"Сгенерируй 3D модель из изображения 'concept_art.png' используя Hyper3D Rodin
1. Загрузи изображение
2. Запуск генерации
3. Ожидание завершения
4. Импорт результата в Blender
4. Авто-ретопология до 10k tris
5. UV Unwrap + PBR Texture Baking
6. Экспорт в GLB"
```

### MCP: MESHY.AI
```bash
"Используй Meshy.ai для генерации 3D из 'product_photo.jpg':
1. Загрузи фото
2. Параметры: quality=high, texture_resolution=2048
3. Скачай результат как GLB
4. Импорт в Blender
5. Проверка UV и материалов"
```

---

## 📝 ПОШАГОВЫЙ ПАЙПЛАЙН (LOCAL TripoSR)

### 1. ПОДГОТОВКА ИЗОБРАЖЕНИЯ
```python
# preprocess.py
from PIL import Image
from rembg import remove

def preprocess_image(input_path, output_path, size=512):
    img = Image.open(input_path)
    
    # Удаление фона
    img_no_bg = remove(img)
    
    # Квадратный кроп с паддингом
    img_square = make_square(img_no_bg, size)
    
    # Сохранить
    img_square.save(output_path, "PNG")
    return output_path

def make_square(img, size):
    # Добавить белый/прозрачный фон для квадрата
    w, h = img.size
    max_dim = max(w, h)
    new_img = Image.new('RGBA', (max_dim, max_dim), (0,0,0,0))
    new_img.paste(img, ((max_dim-w)//2, (max_dim-h)//2))
    return new_img.resize((size, size), Image.LANCZOS)
```

### 2. ГЕНЕРАЦИЯ МЕША (TripoSR)
```python
# generate_mesh.py
from triposr import TripoSR
import numpy as np
import trimesh

def generate_3d(image_path, output_dir, steps=50):
    model = TripoSR.from_pretrained('VAST-AI/TripoSR')
    
    # Генерация
    output = model.generate(image_path, num_inference_steps=steps)
    
    # Конвертация в trimesh
    vertices = output['vertices']
    faces = output['faces']
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # Экспорт
    mesh.export(f"{output_dir}/model.obj")
    mesh.export(f"{output_dir}/model.glb")
    
    # Текстуры (если есть)
    if 'texture' in output:
        Image.fromarray(output['texture']).save(f"{output_dir}/texture.png")
    
    return mesh
```

### 3. ПОСТ-ПРОЦЕССИНГ В BLENDER (MCP)
```bash
# В OpenCode:
"Импортируй сгенерированный model.glb в Blender:
1. File → Import → glTF 2.0
2. Авто-ретопология: Quad Remesher target=10000 tris
3. UV Unwrap: Smart Project angle=66 island_margin=0.01
4. PBR Texture Baking: BaseColor, Roughness, Normal, Metallic, AO
5. Материал: Principled BSDF + Texture Nodes
5. Экспорт: GLB + отдельные текстуры 2k"
```

---

## 📊 КАЧЕСТВО И СПЕЦИФИКАЦИИ

| Метод | Tris | Texture Res | UV Quality | Time (RTX 3080) |
|-------|------|-------------|------------|-----------------|
| **TripoSR (raw)** | 10k-50k | 512x512 | Auto UV | 0.5s |
| **TripoSR + Retopo** | 5k-15k | 2k | Clean UV | 30s |
| **LRM** | 20k-100k | 1024x1024 | Good UV | 2s |
| **Hunyuan3D 2.0** | 10k-50k | 2k-4k | Excellent UV | 30s (API) |
| **Hyper3D Rodin** | 10k-30k | 4k | Production UV | 60s (API) |

---

## 💡 ПРО ТИПЫ

| Tip | Why |
|-----|-----|
| Используй `rembg` для удаления фона | Чистый силуэт = лучшая геометрия |
| Множественные ракурсы (front/side/back) | LRM/Hunyuan поддерживают multi-view |
| Квадратный ввод 512x512 | Стандарт для большинства моделей |
| Пост-ретопология обязательна | Raw mesh не подходит для игр/анимации |
| PBR Baking после UV | Нормалы/кавитация из геометрии |

---

## 🔗 LINKS

- **TripoSR:** https://github.com/VAST-AI-Research/TripoSR
- **LRM:** https://github.com/lrm-dev/LRM
- **InstantMesh:** https://github.com/TencentARC/InstantMesh
- **Hunyuan3D:** https://3d.hunyuan.tencent.com/
- **Hyper3D:** https://hyper3d.ai/
- **Meshy:** https://www.meshy.ai/
- **Setup 03:** [Dream Textures](../setups/setup_03_dream_textures.md)
- **Next:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/workflows/wf_02_image_to_3d.md` |
| Russian | `multilang/ru/workflows/wf_02_image_to_3d.md` |