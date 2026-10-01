---
id: setup_39_quixel_bridge
lang: ru
category: setups
type: setup
status: full
tags: [assets, setup]
---
# SETUP 39: QUIXEL BRIDGE STANDALONE

**ID:** SETUP-39 | **Type:** Megascans | **Difficulty:** ⭐⭐ | **Time:** 30 min

> Когда применять: когда нужен не сам Bridge (он уже неактуален), а воспроизводимый экспорт surface/скан-набора в набор карт, который предсказуемо ложится в Principled BSDF.

## 🎯 ЦЕЛЬ

Quixel Bridge больше не качается отдельно: его роль перешла к приложению Fab, а Megascans-каталог живёт там же. Поэтому этот сетап — не про установку Bridge, а про то, что Bridge делал: подобрать набор карт (BaseColor, Normal, Roughness, Displacement, AO, Specular), разрешение, тайлинг по UDIM и LOD для сканов, а потом собрать это в Blender так, чтобы материал не «мылил» и чтобы displacement реально давал силуэт. Разбираем именно контракт экспорта — он не изменился от смены приложения.

> [!NOTE]
> Bridge не обновляется. Если в задаче написано «поставь Bridge» — скорее всего, имеется в виду приложение Fab (см. [SETUP 38](setup_38_fab_epic.md)). Старые инструкции из сети ведут в никуда.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x LTS | сборка материала и рендер |
| Приложение Fab | текущая | источник Megascans-ассетов |
| EXR или PNG 16-bit | — | карты поверхности без потери в тёмных местах |
| Каталог на ASCII-пути | `C:/assets/megascans` | часть обвязки не переваривает кириллицу |
| Cycles | — | только он честно считает displacement |

## 🛠️ НАСТРОЙКА

### 1. Что именно выгружать

Три разных типа ассетов требуют разных наборов карт, и путаница между ними — половина проблем:

| Тип ассета | Обязательные карты | Что можно не брать |
|---|---|---|
| Surface (плитка, ткань, металл) | BaseColor, Normal, Roughness, Displacement | AO (считается из карт), Specular (legacy) |
| 3D-скан | BaseColor, Normal, Roughness, Displacement + LOD | AO |
| Билилборд/растительность | BaseColor + Alpha | всё остальное |

### 2. Скачиваем и раскладываем

```python
from pathlib import Path

ASSET = Path(r"C:/assets/megascans/wood_planks")
# Ожидаемая структура: wood_planks_1001_color.exr, ..._1001_normal.exr, ...
for p in sorted(ASSET.glob("*_1001_*")):
    print(p.name, p.stat().st_size // 1024, "KB")

# Плитки нумеруются 1001..100N по одной оси UDIM — считаем, сколько реально пришло
tiles = {p.name.split("_")[1] for p in ASSET.glob("*_color*")}
print("tiles:", sorted(tiles), "| всего:", len(tiles))
```

### 3. Загружаем карты как UDIM

```python
import bpy
from pathlib import Path

ASSET = Path(r"C:/assets/megascans/wood_planks")

def load_udim(pattern: str) -> bpy.types.Image:
    img = bpy.data.images.load(str(ASSET / pattern), check_existing=True)
    print(pattern, "->", img.source, tuple(img.size))
    return img

color = load_udim("wood_planks_1001_color.exr")
rough = load_udim("wood_planks_1001_roughness.exr")
nrm   = load_udim("wood_planks_1001_normal.exr")
disp  = load_udim("wood_planks_1001_displacement.exr")
```

> [!NOTE]
> `img.source` должен стать `"TILED"`. Если печатает иное — плитки не склеились, и дальше ты получишь только первый квадрат. Проверяй это на шаге сразу, а не после рендера.

### 4. Собираем материал в Principled BSDF

```python
import bpy

mat = bpy.data.materials.get("MS_WoodPlanks") or bpy.data.materials.new("MS_WoodPlanks")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out  = nt.nodes.new("ShaderNodeOutputMaterial");  out.location  = (600, 0)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled");   bsdf.location = (260, 0)

tex = {}
for name, img in (("Base Color", color), ("Roughness", rough), ("Normal", nrm)):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = img
    n.interpolation = "Smart"          # сглаживает мыло на далёких углах
    n.location = (-120, 200)
    n.label = name
    tex[name] = n

nt.links.new(tex["Base Color"].outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(tex["Roughness"].outputs["Color"], bsdf.inputs["Roughness"])

# Normal map -> Normal Map node -> Normal
nm = nt.nodes.new("ShaderNodeNormalMap")
nm.location = (20, -220)
nm.inputs["Strength"].default_value = 1.0
nt.links.new(tex["Normal"].outputs["Color"], nm.inputs["Color"])
nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

# Displacement: отдельная нода, у Principled BSDF такого входа нет
d = nt.nodes.new("ShaderNodeTexImage"); d.image = disp; d.location = (-120, -450)
dtex = nt.nodes.new("ShaderNodeDisplacement"); dtex.location = (260, -450)
dtex.inputs["Midlevel"].default_value = 0.5
dtex.inputs["Scale"].default_value = 0.1
nt.links.new(d.outputs["Color"], dtex.inputs["Height"])
nt.links.new(dtex.outputs["Displacement"], out.inputs["Displacement"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# Чтобы силуэт появился в геометрии, а не только в шейдинге
print("blend_method enum:", [i.identifier for i in bpy.types.Material.bl_rna.properties["blend_method"].enum_items]
      if "blend_method" in bpy.types.Material.bl_rna.properties else "n/a (Blender 4.2+)")
```

### 4a. Проверяем комплектность карт

```python
import re
from pathlib import Path

ASSET = Path(r"C:/assets/megascans/wood_planks")
KIND = ("color", "normal", "roughness", "displacement", "ao", "specular")

present = {k: len(list(ASSET.glob(f"*_{k}_1001_*"))) for k in KIND}
for k, v in present.items():
    print(f"{k:15s} {'ok' if v else 'НЕТ'}")
missing = [k for k, v in present.items() if not v]
print("не хватает:", missing or "ничего")
# Если не хватает roughness — материал будет выглядеть пластиковым,
# если normal — поверхность потеряет микрорельеф.
```

### 5. Включаем реальный displacement

```python
import bpy

scene = bpy.context.scene
scene.render.engine = "CYCLES"
mat = bpy.data.materials["MS_WoodPlanks"]

# Метод смещения в настройках материала: читаем доступные значения, а не угадываем
for key in ("surface_render_method",):
    if key in bpy.types.Material.bl_rna.properties:
        print(key, [i.identifier for i in bpy.types.Material.bl_rna.properties[key].enum_items])

# В UI это Render Properties -> Displacement: Displacement Only / Both
# Сама настройка хранится на материале в UI; из скрипта надёжнее проверить рендер:
scene.cycles.displacement_method = "BOTH"   # 'BUMP' | 'DISPLACEMENT' | 'BOTH'
print(scene.cycles.displacement_method, scene.cycles.max_bounces)
```

> [!NOTE]
> Точное имя свойства метода смещения в Cycles и его значения отличаются между 3.x и 4.x. Прежде чем писать эту строку, напечатай `scene.cycles.bl_rna.properties.keys()` и найди нужное. Смысл остаётся один: смещение должно считаться в геометрии, иначе это просто параллакс-карта.

### 6. Масштаб и тайлинг

```python
import bpy

# Тайлинг задаётся нодой Mapping, а не в Image Texture
nt = bpy.data.materials["MS_WoodPlanks"].node_tree
mp = nt.nodes.new("ShaderNodeMapping")
mp.location = (-360, 200)
mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
src = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
nt.links.new(mp.outputs["Vector"], src.inputs["Vector"])

# Реальный размер плитки: displacement Scale в метрах = обратная величина тайлинга
print("displacement scale (m):", 0.1, "-> тайлинг на 2 м материала:", 1 / 0.1 * 2)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверить, что архив распаковался полностью (8K surface = 8 плиток на карту)
python -c "from pathlib import Path; p=Path(r'C:/assets/megascans/wood_planks'); print(sorted({f.name.split('_')[1] for f in p.glob('*_color*')}))"

# Батч-импорт всех скачанных .blend-бандлов в фоне
blender --background --python-expr "import bpy;bpy.ops.wm.open_mainfile(filepath=r'C:/assets/megascans/surface.blend')"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| Номер первой плитки | `1001` | всегда первая; в 10K-сетках бывает `1001` + отдельный набор |
| `Normal Map → Strength` | `1.0` | меньше — площе, больше — артефакты на рёбрах |
| `Displacement → Scale` | `0.1` м | это высота рельефа, а не процент |
| `Displacement → Midlevel` | `0.5` | сдвигает карту вверх/вниз, если рельеф «утоплен» |
| `Image Texture → Interpolation` | `Smart` | `Closest` для пиксельных масок, `Linear` для размытых карт |
| `cycles.displacement_method` | `BOTH` | `BUMP` — быстрее, `DISPLACEMENT` — честная геометрия |
| `cycles.max_bounces` | `4+` | для шершавых материалов |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Видна только первая плитка | UDIM не распознан | грузи `..._1001_...`, проверь `img.source == "TILED"` |
| Рельеф «плывёт» вдали | слишком мелкая геометрия | `decimate` + `subdivision surface` перед рендером, либо `BUMP` |
| Тени в нормалях инвертированы | карта в OpenGL-конвенции, а Blender ждёт DirectX | инвертируй зелёный канал через Separate/Combine XYZ |
| Материал чёрный | Color Management: очень тёмная EXR-карта | `scene.view_settings.exposure` вверх, проверь `Filmic/AgX` |
| Модель «плоская» при верном displacement | метод смещения = `BUMP` | выставить `BOTH`, смикрорельеф смикро-геометрией |
| Roughness-карта не влияет | Color → Float подключён не туда | связывай `Color` карты в `Roughness` (Blender сам сконвертирует) |
| Скан-лод без нормали | разный масштаб у LOD | прогони `normalize()` для каждого лода отдельно |
| Кириллица в пути — ошибка чтения | ограничение части обвязки | переноси каталоги в ASCII-путь |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 37: BLENDERKIT ASSETS](setup_37_blenderkit_assets.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 40: AMBIENTCG + POLYHAVEN BATCH](setup_40_ambientcg_polyhaven.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](../prompts/36_asset_licensing.md)
- **Теги:** #assets, #setup
