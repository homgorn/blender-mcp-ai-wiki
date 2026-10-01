---
id: setup_47_zero123_instantmesh
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, setup]
---
# SETUP 47: ZERO123 / INSTANTMESH

**ID:** SETUP-47 | **Type:** Multi-view 3D | **Difficulty:** ⭐⭐⭐ | **Time:** 1.5-2 h

> Когда применять: когда есть одна фотография объекта и нужен текстурированный меш — а облачный API нельзя или не хочется. Цепочка: диффузионная модель дорисовывает ракурсы, InstantMesh собирает из них геометрию.

## 🎯 ЦЕЛЬ

Zero123 / Zero123++ превращают одно фото в набор новых ракурсов. InstantMesh берёт эти ракурсы (или одно фото и делает ракурсы сам) и восстанавливает текстурированный меш за минуты на GPU. Настраиваем локальный запуск обеих частей и разбираем главную проблему: качество результата определяется не моделью, а согласованностью промежуточных ракурсов. Если они «разъезжаются» — меш будет сломан, и никакая чистка в Blender это не спасёт.

> [!NOTE]
> У Zero123 есть несколько репозиториев и весов (оригинальная работа «Zero-1-to-3» и улучшенные варианты). Имена скриптов, флаги и сами веса отличаются от репозитория к репозиторию. Прежде чем запускать, открой README того репозитория, который ставишь, и снимай имена оттуда.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Ориентир | Зачем |
|---|---|---|
| GPU | 16 ГБ VRAM | InstantMesh в дефолтных настройках; на 12 ГБ — со снижением разрешения |
| CUDA | под твою карту | иначе всё уходит в CPU и часы вместо минут |
| Диск | 15-25 ГБ | веса обеих моделей |
| Python | 3.8-3.10 (репозитории старые) | свежий Python часто ломает зависимости |
| Blender | 4.x LTS | импорт и чистка |
| `trimesh` | для проверки геометрии | диагностика до импорта |

> [!NOTE]
> Требования по VRAM зависят от настроек. Ориентир «16 ГБ» — то, на чём InstantMesh стабильно отрабатывает дефолтные параметры; на 12 ГБ приходится резать разрешение входа и число итераций. Точные значения смотри в README репозитория.

## 🛠️ НАСТРОЙКА

### 1. Готовим референс

```python
from pathlib import Path
from PIL import Image

SRC = Path(r"C:/assets/refs/chair.jpg")
OUT_DIR = Path(r"C:/assets/ai3d/zero123"); OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(SRC).convert("RGB")
# Модели ждут квадрат: центрируем кропом, а не ресайзом — иначе пропорции поплывут
side = min(img.size)
left, top = ((img.width - side) // 2, (img.height - side) // 2)
img = img.crop((left, top, left + side, top + side))
img = img.resize((512, 512), Image.LANCZOS)
img.save(OUT_DIR / "ref.png")
print("референс:", img.size, "исходник:", Image.open(SRC).size)
```

> [!NOTE]
> 512×512 — типичный вход для Zero123-подобных моделей. Некоторые варианты принимают 256. Точный допустимый размер выводит модель при загрузке — посмотри лог, а не угадывай.

### 2. Ставим Zero123 / Zero123++

```bash
git clone <репозиторий zero123> && cd zero123
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt

# Дальше смотри README репозитория: имя скрипта генерации ракурсов и его флаги
ls *.py
```

```bash
# Проверяем GPU до того, как потратим час на установку
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
```

### 3. Генерируем ракурсы

```bash
# Типовая форма вызова: скрипт с промптом, числом ракурсов и папкой вывода.
# Имя скрипта и точные флаги бери из README того репозитория, который клонировал.
python <скрипт_генерации_ракурсов>.py \
  --image ../ref.png \
  --num-views 6 \
  --output_dir ../views
```

```python
# Проверяем результат ДО того, как отдавать его InstantMesh
from pathlib import Path
import os
from PIL import Image

VIEWS = Path(r"C:/assets/ai3d/zero123/views")
files = sorted(VIEWS.glob("*.png"))
print("ракурсов:", len(files))

# Кадры должны быть одинакового размера и без чёрных/пустых — иначе InstantMesh их выкинет
for f in files:
    im = Image.open(f)
    print(f.name, im.size, im.mode,
          "OK" if im.size[0] == im.size[1] and im.size[0] >= 256 else "ПРОБЛЕМА")
```

### 4. Ставим InstantMesh

```bash
git clone https://github.com/tencent/InstantMesh.git && cd InstantMesh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Собираем меш

```bash
# Флаги читай в README: версии репозитория отличаются набором ключей
bash run.sh inputs/case_rendering  outputs/case   # вариант с готовым набором ракурсов
# или
python run.py inputs/case.png outputs/case        # вариант с одиночным изображением
```

```python
# Второй вариант существует и часто даёт лучший результат, чем ручные ракурсы:
# модель сама дорисовывает вид. Сравни оба выхода.
```

### 6. Проверяем геометрию до импорта

```python
import trimesh
from pathlib import Path

MESH = Path(r"C:/assets/ai3d/zero123/outputs/case/mesh.obj")
scene = trimesh.load(str(MESH), force="scene")
geoms = list(scene.geometry.values())
print("мешей:", len(geoms))
for name, g in scene.geometry.items():
    print(name, "verts:", len(g.vertices), "faces:", len(g.faces),
          "watertight:", g.is_watertight)
```

### 7. Импорт в Blender и чистка

```python
import bpy
from pathlib import Path
from mathutils import Vector

def import_mesh(path: Path, coll="AI3D") -> bpy.types.Collection:
    c = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=str(path))     # Blender 3.3+: C++-импортёр OBJ
    for o in set(bpy.data.objects) - before:
        for old in list(o.users_collection):
            old.objects.unlink(o)
        c.objects.link(o)
    return c

# coll = import_mesh(MESH)
# obj = next(iter(bpy.data.collections["AI3D"].objects))
# print(len(coll.objects), "объектов |", len(obj.data.polygons), "полигонов")

bpy.ops.object.select_all(action="DESELECT")
obj = bpy.context.view_layer.objects.active or next(iter(bpy.data.collections["AI3D"].objects))
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Выборочное удаление мусорных граней, если меш «оброс» шумом
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.select_non_manifold()
bpy.ops.mesh.delete(type="VERT")
bpy.ops.object.mode_set(mode="OBJECT")

# Масштаб и посадка на пол: без этого объект уезжает на 30 метров вверх
bpy.context.view_layer.update()
if obj.dimensions.z > 0:
    s = 0.5 / obj.dimensions.z
    obj.scale = (s, s, s)
bpy.context.view_layer.update()
obj.location.z -= min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)

smooth_ops = [o for o in dir(bpy.ops.object) if "smooth" in o]
print("итог:", tuple(round(v, 3) for v in obj.dimensions), "| smoothing ops:", smooth_ops)
```

> [!NOTE]
> Удаление non-manifold-граней лечит типичную болезнь этой цепочки — «пузыри» и дырки от несогласованных ракурсов. Но если ракурсы разъехались принципиально, геометрия будет «смята» впустую: тогда правь вход, а не меш.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Пакетно: 20 референсов через один запуск
python <скрипт_ракурсов>.py --image ref.png --num-views 6 --output_dir views/i%03d
```

| Параметр | Значение | Когда менять |
|---|---|---|
| входной размер | `512×512` | 256 для быстрой проверки идеи |
| `--num-views` | `6` | 4 хватит для простых форм, 8+ для сложных |
| InstantMesh вход | папка ракурсов ИЛИ одно фото | сравни оба, результат разный |
| `remesh_voxel_size` | не применяем | меши уже достаточно чистые |
| `dec.ratio` | `0.4–0.6` | только если полигонов слишком много |
| seed | фиксировать | без seed повторный запуск даст другой меш |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `ImportError` на torchao / разных версиях torch | репозитории старые, конфликт версий | отдельный venv на каждый репозиторий, не смешивать |
| Всё считается на CPU и очень долго | нет CUDA-сборки torch | поставь torch с CUDA под свою карту, проверь `torch.cuda.is_available()` |
| Меш «смят» в гармошку | ракурсы геометрически несогласованы | подай в InstantMesh одно фото, чтобы он дорисовал виды сам |
| InstantMesh падает на входе | кадры разного размера или есть пустые | проверь лог шага 3, перегенерируй |
| Текстура размытая на рёбрах | мало ракурсов | увеличь `--num-views` до 8 |
| UV перекрываются | реконструкция не гарантирует атлас | `bpy.ops.uv.smart_project()` |
| `wm.obj_import` не найден | версия старше 3.3 | используй `bpy.ops.import_scene.obj` |
| Меш в километрах | нет нормализации | прогони шаг 8 |
| Веса скачались не полностью | оборвалась загрузка | сверь размер с ожидаемым из README |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 43: MESHY API V4](setup_43_meshy_api_v4.md), [SETUP 44: RODIN / HYPER3D GEN](setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md)
- **По темам:** [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **Теги:** #ai-3d, #setup
