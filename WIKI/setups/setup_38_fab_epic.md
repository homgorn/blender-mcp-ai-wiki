---
id: setup_38_fab_epic
lang: ru
category: setups
type: setup
status: full
tags: [assets, pipeline, setup]
---
# SETUP 38: FAB.COM (EPIC) PIPELINE

**ID:** SETUP-38 | **Type:** Marketplace | **Difficulty:** ⭐⭐ | **Time:** 35-45 min

> Когда применять: когда нужно завести в Blender контент с Fab (бывшие Megascans) — surface-комплекты, 3D-скан-ассеты, модели — и наладить повторяемую выгрузку, а не разовый ручной импорт.

## 🎯 ЦЕЛЬ

Fab — маркетплейс Epic Games, в который переехали Megascans; отдельный Quixel Bridge больше не развивается. Настраиваем связку «учётная запись Fab → приложение-мост → Blender»: ставим аддон, забираем ассеты, приводим их к единому масштабу и раскладываем по коллекциям, чтобы дальше собирать сцену скриптом, а не руками. Отдельно разбираем поверхности UDIM — это главная причина, по которой «скачал и вставил» не работает: 8K-набор раскладывается по плиткам 1001…1008, и одной картинки недостаточно.

> [!NOTE]
> Способы установки аддона Fab для Blender, имя его пакета и набор маршрутов локального API менялись между сборками приложения Fab. Не выдумывай `module=` и `api/v1/...` — распечатай то, что реально лежит в скачанном `.zip` и в настройках приложения.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Аккаунт Fab | любая, бесплатная регистрация | вход в библиотеку, нужен для загрузок |
| Приложение Fab (desktop) | текущая | локальный мост и менеджер загрузок |
| Blender | 4.x LTS | цель пайплайна |
| Аддон Fab для Blender | версия под твой Blender | импорт прямо в сцену |
| glTF 2.0 / FBX / OBJ | — | форматы, которые Blender читает из коробки |
| Python 3.11 из поставки Blender | 3.11 | встроенный интерпретатор, отдельный ставить не надо |

## 🛠️ НАСТРОЙКА

### 1. Аккаунт и приложение

Регистрируешься на [fab.com](https://www.fab.com), скачиваешь desktop-приложение и входишь в него. Лицензия у ассетов разная, и она указана на странице самого ассета — читать надо там, а не по памяти: часть каталога доступна бесплатно, часть требует подписки или валюты в аккаунте.

### 2. Узнаём настоящее имя пакета аддона

Аддон приезжает `.zip`-ом. Имя модуля для `addon_enable` — это имя папки внутри архива, а не имя файла:

```python
import zipfile
from pathlib import Path

ADDON_ZIP = Path(r"C:/addons/fab_blender.zip")   # путь к скачанному архиву

with zipfile.ZipFile(ADDON_ZIP) as z:
    roots = sorted({n.split("/")[0] for n in z.namelist() if "/" in n})
print(roots)   # первый элемент — то, что нужно в module=
```

### 3. Ставим и включаем аддон

```python
import bpy

MODULE = roots[0]   # подставь значение из шага 2
bpy.ops.preferences.addon_install(filepath=str(ADDON_ZIP), overwrite=True)
bpy.ops.preferences.addon_enable(module=MODULE)

# Проверка: аддон появился в списке и его модуль импортируется
import addon_utils
print(MODULE, addon_utils.check(MODULE))
print([m.__name__ for m in addon_utils.modules() if MODULE in m.__name__])
```

### 4. Пакетный импорт GLB в коллекцию

```python
import bpy
from pathlib import Path

ROOT = Path(r"C:/assets/fab/batch01")

def import_glb_folder(root: Path, coll_name: str = "FAB") -> bpy.types.Collection:
    coll = bpy.data.collections.get(coll_name) or bpy.data.collections.new(coll_name)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    for path in sorted(root.glob("*.glb")):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        for obj in set(bpy.data.objects) - before:
            for c in list(obj.users_collection):
                c.objects.unlink(obj)
            coll.objects.link(obj)
    return coll

print(import_glb_folder(ROOT).name)
```

### 5. Единый масштаб и имена

Фабы отдают ассеты в разных единицах, поэтому «планка рядом с креслом» после импорта не работает. Приводим высоту по мировой Z к метру и фиксируем трансформ:

```python
import bpy

def normalize(obj, target_height=1.0):
    if obj.type != "MESH" or obj.dimensions.z <= 0:
        return
    s = target_height / obj.dimensions.z
    obj.scale = (s, s, s)
    obj.name = f"FAB_{obj.name}"
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

for obj in bpy.data.collections["FAB"].objects:
    normalize(obj, target_height=1.0)
print([o.name for o in bpy.data.collections["FAB"].objects])
```

### 6. Surface-набор: UDIM

8K surface — это не одна 8192×8192, а сетка плиток. Грузим первую (`1001`), Blender распознаёт паттерн по имени:

```python
import bpy
from pathlib import Path

TEX_DIR = Path(r"C:/assets/fab/surfaces/oak")
img = bpy.data.images.load(str(TEX_DIR / "oak_color.1001.exr"), check_existing=True)
print("source:", img.source, "size:", tuple(img.size), "tiles:", img.source == "TILED")

# Значения enum менялись между 3.x и 4.x — печатаем, а не гадаем
try:
    print([i.identifier for i in bpy.types.Image.bl_rna.properties["source"].enum_items])
except Exception as e:
    print("enum introspection failed:", e)
```

> [!NOTE]
> `Image.source == "TILED"` — проверка, а не гарантия: в части версий Blender значение называется иначе. Если `False`, открой картинку через UI и переключи режим UDIM вручную; в любом случае проверяй, что в Image Editor видны плитки, а не одна.

### 7. Локальный сервис приложения Fab

Приложение поднимает HTTP-сервис на `127.0.0.1` — это и есть «мостик» между клиентом Fab и Blender:

```python
import socket, urllib.request, urllib.error

for port in (2000, 2001, 8080):                       # типовой диапазон сборок
    s = socket.socket(); s.settimeout(0.4)
    print(port, "open" if s.connect_ex(("127.0.0.1", port)) == 0 else "closed")
    s.close()

for path in ("/", "/health"):                          # проверяем, что сервис отвечает
    url = f"http://127.0.0.1:2000{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            print(url, r.status, r.read(120))
    except urllib.error.HTTPError as e:
        print(url, "HTTP", e.code)
    except Exception as e:
        print(url, "ERR", type(e).__name__, e)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Пакетная обработка без GUI: сцена-шаблон + скрипт
blender --background template.blend --python import_fab_batch.py
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `target_height` | `1.0` (метр) | для пропов ставь реальный размер, иначе ляжет масштаб |
| `ADDON_ZIP` | путь к архиву аддона | одна установка на одну версию Blender |
| `MODULE` | папка внутри архива | менять только при обновлении аддона |
| `bpy.ops.import_scene.gltf` | оператор импорта GLB | для FBX — `bpy.ops.import_scene.fbx` |
| `bpy.ops.wm.obj_import` | оператор импорта OBJ | в 3.3+ это новый C++-импортёр |
| `img.source` | должно быть `TILED` | если нет — грузи через UI вручную |
| порт локального сервиса | см. настройки приложения Fab | меняется между сборками приложения |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Плоская текстура, видны только квадратные плитки | грузится одна плитка, паттерн не распознан | грузи `..._1001.exr` из папки UDIM, проверь `img.source` |
| Объект «микроскопический» или в километрах | ассет пришёл в другой единице | прогони `normalize()` из шага 5 |
| Импорт не создаёт объектов | glTF-файл битый или это `.blend`-архив | открой файл, проверь `gltf` в заголовке файла |
| `addon_enable` ругается на `module` | имя модуля ≠ имя zip-файла | распечатай `roots` из шага 2 |
| Аддон есть, но кнопки в UI нет | аддон включён в preferences другого пользователя | `Edit → Preferences → Add-ons`, включить вручную |
| `localhost` не отвечает | приложение Fab не запущено / другой порт | запусти приложение, порт бери из его настроек |
| Текстуры в материале чёрные | материал не связан с Image Texture | проверь ноду `Image Texture → Base Color` и Color Management |
| Модель вставлена в начало координат | не выставлен origin | `bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")` |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 37: BLENDERKIT ASSETS](setup_37_blenderkit_assets.md), [SETUP 39: QUIXEL BRIDGE STANDALONE](setup_39_quixel_bridge.md), [SETUP 40: AMBIENTCG + POLYHAVEN BATCH](setup_40_ambientcg_polyhaven.md)
- **По темам:** [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](../prompts/36_asset_licensing.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md)
- **Теги:** #assets, #pipeline, #setup
