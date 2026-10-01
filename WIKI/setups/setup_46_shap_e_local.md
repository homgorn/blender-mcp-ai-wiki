---
id: setup_46_shap_e_local
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, setup]
---
# SETUP 46: SHAP-E / POINT-E LOCAL

**ID:** SETUP-46 | **Type:** Research Gen | **Difficulty:** ⭐⭐ | **Time:** 30-40 min

> Когда применять: когда нужен полностью локальный, бесплатный и предсказуемый по зависимостям генератор — и когда результат нужен как «форма-подсказка» для моделирования, а не как финальный ассет.

## 🎯 ЦЕЛЬ

Shap-E и Point-E — исследовательские модели OpenAI, которые генерируют 3D из текста или картинки. Они не для продакшена: геометрия грубая, часто «каплевидная», зато работают на CPU, ничего не стоят и не отправляют данные наружу. Статья даёт честный расклад: где Shap-E сильнее Point-E, как поставить его локально, как вытащить из неявного представления нормальный меш и что в Blender с ним делать, чтобы он перестал выглядеть генератом.

> [!NOTE]
> Shap-E и Point-E — модели 2022-2023 годов, и их репозитории не развиваются. Зато они до сих пор полезны как способ проверить идею «а что, если сгенерить форму», без ключей, без очередей и без кредитов. Не жди от них деталей и текстур уровня облачных сервисов.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Python | 3.10-3.11 | официальный репозиторий рассчитан на это |
| PyTorch | CUDA-сборка, если есть GPU | базовая модель на CPU работает, но медленно |
| Репозиторий | `openai/shap-e` | код и веса |
| `trimesh` | ставится с репозиторием | запись и просмотр меша |
| Blender | 4.x LTS | чистка результата |
| Около 2 ГБ диска | — | веса базовой и текстурной модели |

## 🛠️ НАСТРОЙКА

### 1. Ставим

```bash
git clone https://github.com/openai/shap-e.git
cd shap-e

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e .
```

### 2. Смотрим, что реально лежит в репозитории

```bash
ls shap_e/assets/
ls *.py | head -20
python -m pip show shap-e
```

> [!NOTE]
> Имена сэмпл-скриптов и файлов весов в репозитории менялись. Прежде чем писать команду, посмотри список: `python sample_text_to_3d.py --help` покажет реальные флаги, если скрипт их поддерживает. Никакого `sample_text_to_3d.py --text ... --outdir ...` не выдумывается — проверь выводом `--help`.

### 3. Текст → форма

```python
# Минимальный скрипт по API модели (имена классов стабильны в ветке main):
from pathlib import Path
from shap_e.rendering import TextTo3DModel

# Точное имя файла весов бери из ls shap_e/assets/ — оно менялось между коммитами
model = TextTo3DModel("shap_e.assets/<файл_из_assets>.pkl")
print("модель загружена")
```

```python
# Дальше — рендер сетки из неявного представления.
# У Shap-E это NeRF-подобная сетка плюс marching cubes, поэтому шаг обязателен.
import numpy as np
import torch

# seed фиксирует результат: без него каждый запуск даёт разный меш
torch.manual_seed(42)
np.random.seed(42)

model.renderers.mesh.render_coarse_to_fine(
    0,                                        # индекс промпта в списке
    "a red wooden chair",                     # текстовое описание
    0,                                        # индекс seed
    verbose=True,
)
print("рендер завершён")
```

> [!NOTE]
> Список промптов задаётся при создании `TextTo3DModel` либо в настройках рендерера, и его форма в разных коммитах отличается. Сначала напечатай доступные атрибуты `model.renderers` и прочитай пример из `README` репозитория — это надёжнее, чем угадывать сигнатуру.

### 4. Сохраняем в файл

```python
import trimesh
from pathlib import Path

OUT = Path(r"C:/assets/ai3d/shap_e"); OUT.mkdir(parents=True, exist_ok=True)
# scene у Shap-E — объект trimesh; у scene.geometry список мешей
scene = None    # <- результат шага 3
print(type(scene), [type(g).__name__ for g in getattr(scene, "geometry", [])])
# scene.export(OUT / "chair.glb")
```

### 5. Импорт в Blender и грубая чистка

```python
import bpy
from pathlib import Path

def import_ai3d(path: Path, coll="AI3D") -> bpy.types.Collection:
    c = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    for o in set(bpy.data.objects) - before:
        for old in list(o.users_collection):
            old.objects.unlink(o)
        c.objects.link(o)
    return c

# coll = import_ai3d(OUT / "chair.glb")
```

### 6. Voxel remesh — главный шаг для Shap-E

Marching cubes даёт треугольный меш с рваным рельефом. Пересборка вокселами убирает шум сильнее, чем любой Decimate:

```python
import bpy

obj = next(iter(bpy.data.collections["AI3D"].objects))
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Voxel Remesh работает в режиме Object и требует замкнутой поверхности
obj.data.remesh_voxel_size = 0.01      # в метрах объекта; меньше — детальнее и тяжелее
bpy.ops.object.voxel_remesh()
print("после remesh:", len(obj.data.polygons), "полигонов")

sm = obj.modifiers.new("Smooth", "SMOOTH")
sm.factor = 0.5
sm.iterations = 3
```

> [!NOTE]
> `remesh_voxel_size` — единственный параметр, который реально настраивают; подбирай его под масштаб объекта. Если меш «рассыпался», сначала проверь, что он замкнут: `remesh` требует watertight-поверхность, а marching cubes на плоских промптах даёт дырки.

### 7. Приводим к приличному виду

```python
import bpy
from mathutils import Vector

smooth_ops = [o for o in dir(bpy.ops.object) if "smooth" in o or "auto" in o]
print("smoothing ops:", smooth_ops)     # shade_smooth_by_angle в 4.1+, shade_auto_smooth в 4.0

dec = obj.modifiers.new("Decimate", "DECIMATE")
dec.ratio = 0.4
bpy.ops.object.shade_smooth()

bpy.context.view_layer.update()
if obj.dimensions.z > 0:
    s = 0.45 / obj.dimensions.z           # посадить на реальный размер предмета
    obj.scale = (s, s, s)
bpy.context.view_layer.update()
ground = min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
obj.location.z -= ground
print("итог:", tuple(round(v, 3) for v in obj.dimensions))
```

### 8. Point-E — только если совсем надо

```bash
git clone https://github.com/openai/point-e.git
cd point-e
python -m venv .venv && .venv\Scripts\activate      # Linux: source .venv/bin/activate
pip install -e .
```

Point-E — предшественник Shap-E: ниже разрешение, меньше контроля над результатом, вывод — облако точек. Практический смысл один: если Shap-E не ставится по зависимостям, Point-E иногда ставится, и на нём можно хотя бы проверить идею формы.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Список сэмпл-скриптов и их флагов — единственный честный источник имён
ls *.py
python sample_text_to_3d.py --help
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `torch.manual_seed` | `42` | без него результат невоспроизводим |
| `render_coarse_to_fine` | грубое → точное | грубое — быстрый превью-меш |
| `remesh_voxel_size` | `0.01` м | масштабируй пропорционально размеру объекта |
| `Smooth factor` / `iterations` | `0.5` / `3` | артефакты — увеличивай, форма плывёт — уменьшай |
| `dec.ratio` | `0.4` | после remesh, не раньше |
| базовая vs текстурная модель | базовая — быстрее | текстурная весит заметно больше |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `ModuleNotFoundError: shap_e` | пакет не установлен / не тот Python | `pip install -e .` в активированном venv |
| Веса не нашлись по имени | файл переименовали | `ls shap_e/assets/` и подставь реальное имя |
| Каждый запуск даёт разный меш | не зафиксирован seed | `torch.manual_seed` + `np.random.seed` |
| Меш в дырках, remesh падает | поверхность не замкнута | проверь замкнутость, увеличь `remesh_voxel_size` |
| `KeyError` на аргументах рендера | сигнатура коммита другая | `python sample_text_to_3d.py --help`, потом пример из README |
| Remesh «съел» объект | воксель крупнее геометрии | уменьши `remesh_voxel_size` вдвое |
| Очень долго на CPU | базовая модель без GPU | поставь CUDA-сборку PyTorch, если есть карта |
| В Blender импортируется пусто | экспорт прошёл в OBJ, а импортируем как GLB | проверь расширение и формат в `bpy.ops.import_scene` |
| `bpy.ops.object.shade_smooth` отсутствует | не объектный режим | `bpy.ops.object.mode_set(mode="OBJECT")` перед вызовом |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 43: MESHY API V4](setup_43_meshy_api_v4.md), [SETUP 44: RODIN / HYPER3D GEN](setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 47: ZERO123 / INSTANTMESH](setup_47_zero123_instantmesh.md)
- **По темам:** [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **Теги:** #ai-3d, #setup
