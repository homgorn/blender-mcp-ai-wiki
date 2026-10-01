---
lang: ru
orig_lang: en
translation: ai
---
# ВОРКФЛОУ TEXT-TO-3D

## Обзор
Несколько подходов к генерации 3D-моделей из текстовых промптов.

---

## Метод 1: Hyper3D Rodin (через blender-mcp)
**Лучше всего для:** быстрых концепт-моделей, игровых ассетов
**Стоимость:** кредиты API (есть бесплатный тариф)
**Качество:** среднее-высокое, чистая топология

### Воркфлоу
```bash
# 1. Включить в Blender
N-panel → MCP for Blender → отметить "Use Hyper3D" → добавить API-ключ (Preferences)

# 2. Через ИИ (OpenCode/Claude):
"Generate a 3D model of a medieval fantasy sword using Hyper3D Rodin"
# → Создаёт задачу → опрашивает статус → импортирует результат

# 3. Постобработка:
"Decimate the sword to 2000 tris, add bevel, create metal material"
```

### Параметры
- `prompt`: текстовое описание
- `seed`: для воспроизводимости
- `generate_textures`: необязательная генерация PBR

---

## Метод 2: Hunyuan3D (через blender-mcp)
**Лучше всего для:** ассетов высокого качества, китайских/азиатских тем
**Стоимость:** требуются SecretId/SecretKey
**Качество:** высокое, годится для продакшена

### Воркфлоу
```bash
# 1. Получить учётные данные: https://3d.hunyuan.tencent.com/
# 2. Включить в Blender: отметить "Use Hunyuan3D" → добавить SecretId/SecretKey/API URL

# 3. Через ИИ:
"Create a 3D model of a Chinese dragon using Hunyuan3D"
# → Задача → опрос → импорт

# 4. Чистка:
"Separate loose parts, apply scale, create materials for each part"
```

---

## Метод 3: TripoSR (локально, бесплатно)
**Лучше всего для:** приватности, офлайна, экспериментов
**Стоимость:** бесплатно (работает локально)
**Качество:** ниже, годится для концептов
**Железо:** рекомендуется 8GB+ VRAM

### Установка
```bash
# Вариант A: pip
pip install triposr

# Вариант B: клонировать репозиторий
git clone https://github.com/VAST-AI-Research/TripoSR
cd TripoSR
pip install -r requirements.txt

# Скачать веса (автоматически при первом запуске)
```

### Использование из Python
```python
# Выполнять через execute_blender_code
import bpy
from triposr import TripoSR

model = TripoSR.from_pretrained("VAST-AI/TripoSR")
output = model.generate("a cute robot", num_inference_steps=50)
# output — словарь с мешем → импортировать в Blender
```

### Интеграция с Blender
```python
# Сохранить как .obj/.glb, затем импортировать
import bpy
bpy.ops.wm.obj_import(filepath="output.obj")
# или
bpy.ops.import_scene.gltf(filepath="output.glb")
```

---

## Метод 4: MeshGPT / Shap-E (локально)
**Лучше всего для:** исследований, собственного обучения
**Стоимость:** бесплатно
**Качество:** экспериментальное

### Shap-E (OpenAI)
```bash
git clone https://github.com/openai/shap-e
cd shap-e
pip install -e .
# Скачать веса
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

## Метод 5: LGM (Large Gaussian Model)
**Лучше всего для:** высокого качества и скорости (Gaussian splatting)
**Стоимость:** бесплатно (локально)

```bash
git clone https://github.com/ashawkey/LGM
cd LGM
pip install -r requirements.txt
```

---

## Сравнительная матрица

| Метод | Локально/облако | Стоимость | Качество | Скорость | Топология | UV |
|-------|-----------------|-----------|----------|----------|-----------|----|
| **Hyper3D** | Облако | $ | ⭐⭐⭐⭐ | Быстро | Хорошая | Есть |
| **Hunyuan3D** | Облако | $ | ⭐⭐⭐⭐⭐ | Средне | Отличная | Есть |
| **TripoSR** | Локально | Бесплатно | ⭐⭐⭐ | Быстро | Базовая | Базовые |
| **Shap-E** | Локально | Бесплатно | ⭐⭐ | Медленно | Базовая | Нет |
| **LGM** | Локально | Бесплатно | ⭐⭐⭐⭐ | Быстро | Н/П (сплаты) | Н/П |

---

## Рекомендуемый пайплайн (2026)

### Для продакшен-ассетов
```
1. Сгенерировать базу: Hyper3D или Hunyuan3D (облако)
2. Импорт → Blender
3. Чистка: Decimate, Separate, Scale, Origin
4. Ретопология: Quad Remesher / Instant Meshes
5. UV: Smart UV Project / вручную
6. Запекание: Normal, AO, Curvature из high-poly
7. Текстуры: Substance Painter / Dream Textures
6. Экспорт: GLTF (игра) / USD (пайплайн)
```

### Для быстрого прототипа
```
1. TripoSR (локально, бесплатно) → быстрый концепт
2. Если перспективно → Hyper3D ради качества
3. GenesisCore для сборки сцены
4. Dream Textures для материалов
```

### Для приватности / local-first
```
1. Ollama (llama3.2/codellama) через GenesisCore
2. TripoSR для генерации 3D
3. Dream Textures (локальный SD) для текстур
4. Всё офлайн, без API-ключей
```

---

## Шаблон скрипта автоматизации

```python
# Выполнять через execute_blender_code
import bpy
import requests
import time

def generate_hyper3d(prompt, api_key):
    # Отправить задачу
    resp = requests.post(
        "https://api.hyper3d.ai/v1/jobs",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"prompt": prompt, "generate_textures": True}
    )
    job_id = resp.json()["job_id"]
    
    # Опрашивать статус
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

# Использование
url = generate_hyper3d("futuristic motorcycle", "YOUR_KEY")
# Скачать и импортировать
import urllib.request
urllib.request.urlretrieve(url, "/tmp/model.glb")
bpy.ops.import_scene.gltf(filepath="/tmp/model.glb")
```

---

## Чек-лист после генерации

- [ ] **Scale:** применить масштаб (Ctrl+A → Scale), попасть в реальный размер
- [ ] **Origin:** выставить в центр геометрии (Right-click → Set Origin → Origin to Geometry)
- [ ] **Topology:** проверить трисы/квады, при необходимости decimate
- [ ] **Separation:** разделить Loose Parts (P → By Loose Parts) под материалы
- [ ] **Naming:** переименовать объекты осмысленно
- [ ] **Materials:** назначить/создать PBR-материалы
- [ ] **UVs:** развернуть (Smart UV Project), проверить наложения
- [ ] **LODs:** создать LOD-версии (50%, 25%, 10%)
- [ ] **Export:** GLTF для веба/игры, USD для пайплайна

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](../../../setups/setup_45_hunyuan3d_21.md), [WORKFLOWS - PRODUCTION PIPELINES](scene-building.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md)
- **Теги:** #ai-3d, #blender, #mcp, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность ⭐⭐⭐⭐.
