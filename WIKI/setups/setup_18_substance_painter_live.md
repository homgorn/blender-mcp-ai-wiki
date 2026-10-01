---
id: setup_18_substance_painter_live
lang: ru
category: setups
type: setup
status: full
tags: [setup, substance]
---
# SETUP 18: SUBSTANCE PAINTER LIVE-LINK

**ID:** SETUP-18 | **Type:** Texturing Pro | **Difficulty:** ⭐⭐ | **Time:** 40-60 min
**RU/EN Bilingual**

> Когда применять: когда сцена уже в Blender, а текстуры пишет художник в Substance 3D Painter и результат должен возвращаться в материал без ручного «экспорт-импорт-потерялся». Для однократного прогона достаточно обычного экспорта; здесь — схема, где цикл можно повторять.

## 🎯 ЦЕЛЬ
Организовать повторяемый цикл Blender ↔ Substance 3D Painter: вытащить из Blender меш с корректной геометрией (для карт ID/curvature/curvature/AO), забрать из Painter готовые PBR-карты и автоматически подставить их в материал Blender, включая UDIM-тайлы. Отдельная цель — сделать так, чтобы повторный прогон после правок в Painter не требовал ручных кликов в Blender.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Substance 3D Painter | 9.x / 10.x (ранее Substance Painter) | текстурирование, smart materials, экспорт карт |
| Substance 3D Integration для Blender | см. примечание ниже | живая связь, если она есть для твоей версии |
| Blender | 4.2 LTS+ | сборка материала и приём карт |
| Разрешение текстур | 2K на тест, 4K в продакшене | Painter жрёт память пропорционально размеру карт |
| Расшаренная папка обмена | ASCII-путь | канал между Painter и Blender |

> [!NOTE]
> Официальные плагины Substance 3D Integration заявлены для 3ds Max, Maya и Unreal, и набор поддерживаемых DCC менялся от версии к версии. **Проверь на сайте Adobe, есть ли поддержка Blender в твоей версии Substance 3D** — если её нет, статья ниже описывает файловый roundtrip с автоподхватом, который работает всегда. Не выдумывай имя аддона: сначала посмотри, что предлагает Adobe.

## 🛠️ НАСТРОЙКА

### 1. Из Blender в Painter: меш, на котором считаются карты

```bash
# Batch-экспорт из Blender без GUI — удобно, когда скрипт гоняется по расписанию
blender --background scene.blend \
        --python-expr "import bpy; bpy.ops.object.select_all(action='SELECT'); \
bpy.ops.export_scene.fbx(filepath='C:/sp/asset.fbx', use_selection=True, \
path_mode='COPY', embed_textures=False, mesh_smooth_type='FACE')"
```

Ключевое: `mesh_smooth_type='FACE'` и развёртка. Painter строит карты ID/curvature/AO из геометрии; если в FBX приедут усреднённые нормали, карта curvature станет плоской и запечется пустой.

Внутри Blender, чтобы не собирать длинную строку:

```python
# export_for_painter.py — Blender: Text Editor → Run Script
import bpy, os

OUT = r"C:\sp"
os.makedirs(OUT, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH':
        ob.select_set(True)
bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]

bpy.ops.export_scene.fbx(
    filepath=os.path.join(OUT, "asset.fbx"),
    use_selection=True,
    path_mode='COPY',
    object_types={'MESH'},
    mesh_smooth_type='FACE',        # усреднённые нормали убивают карту curvature
    use_mesh_modifiers=True,        # subdivision должен быть применён ДО экспорта
    apply_unit_scale=True,
    axis_forward='-Z', axis_up='Y',   # согласование осей с Painter — главный источник «перевёрнутого» меша
)
print("FBX:", os.path.join(OUT, "asset.fbx"))
```

### 2. В Painter: export preset под Blender

Готовый пресет — это JSON-файл с расширением `.spexp`. Надёжный путь: в UI `File → Export Texture Preset → Export`, потом правишь полученный файл и закидываешь обратно в `Documents/Adobe/Adobe Substance 3D Painter/*/resources/presets/`.

```json
{
  "exportPresets": [
    {
      "name": "Blender_PBR_UDIM",
      "maps": [
        { "fileName": "$textureSet_BaseColor", "channels": [ { "destChannel": "R", "srcChannel": "R" },
                                                          { "destChannel": "G", "srcChannel": "G" },
                                                          { "destChannel": "B", "srcChannel": "B" } ],
          "parameters": { "fileFormat": "png", "bitDepth": "8", "dithering": false, "paddingAlgorithm": "infinite" } },
        { "fileName": "$textureSet_Metallic", "channels": [ { "destChannel": "R", "srcChannel": "L" } ],
          "parameters": { "fileFormat": "png", "bitDepth": "8", "dithering": false, "paddingAlgorithm": "infinite" } },
        { "fileName": "$textureSet_Roughness", "channels": [ { "destChannel": "R", "srcChannel": "R" } ],
          "parameters": { "fileFormat": "png", "bitDepth": "8", "dithering": false, "paddingAlgorithm": "infinite" } },
        { "fileName": "$textureSet_Normal", "channels": [ { "destChannel": "RGB", "srcChannel": "Normal" } ],
          "parameters": { "fileFormat": "png", "bitDepth": "16", "dithering": false, "ditheringIntensity": 0 } },
        { "fileName": "$textureSet_AO", "channels": [ { "destChannel": "R", "srcChannel": "AO" } ],
          "parameters": { "fileFormat": "png", "bitDepth": "8", "dithering": false, "paddingAlgorithm": "infinite" } },
        { "fileName": "$textureSet_Height", "channels": [ { "destChannel": "R", "srcChannel": "Height" } ],
          "parameters": { "fileFormat": "exr", "bitDepth": "32" } }
      ],
      "exportList": [ { "rootPath": "$textureSet" } ],
      "exportPresets": [ { "name": "Default" } ],
      "parameters": { "paddingAlgorithm": "infinite", "dithering": true, "sizeLog2": 11, "fileFormat": "png" }
    }
  ]
}
```

> [!NOTE]
> Схема `.spexp` — это то, что Painter сохраняет сам. Не собирай пресет вручную по памяти: выгрузи пресет из UI, открой его в текстовом редакторе и правь только те поля, которые реально нужно поменять (размер, формат, `paddingAlgorithm`). Точные имена токенов `$textureSet_BaseColor` у каждой карты свои — сверяйся с выгрузкой.

Три решения, которые чаще всего отличаются от «ожидаемого»:

- **Metallic в R, Roughness в G** — как ожидает Principled BSDF; отдельная карта metallic только в R, roughness только в R, если используешь отдельные ноды.
- **Normal в PNG 16-bit** — 8 бит на нормали дают заметный бандинг на гладких поверхностях.
- **Height в 32-bit EXR** — 8-битный height ломает Bump/Displace при сильном смещении.

### 3. В Painter: батч-экспорт по всем texture set

```python
# substance_export.py — запускается ВНУТРИ Painter: Python → Run Script,
# либо из меню Python в панели Scripting. Не из командной строки ОС.
import substance_painter.export
import substance_painter.project
import substance_painter.textures

CONFIG = substance_painter.export.ExportUASConfig(
    export_project_path="C:/sp/export",   # куда класть результат
    export_list=[substance_painter.export.ExportOutputConfig(
        output_name="Blender_PBR_UDIM",
        export_shader_params={}
    )],
)

def do_export():
    substance_painter.export.export_project_textures(CONFIG)
    print("exported", len(substance_painter.textures.all_texture_sets()), "texture sets")

# Экспорт нельзя запускать, пока Painter занят — отсюда обёртка
substance_painter.project.execute_when_not_busy(do_export)
```

> [!NOTE]
> Имена классов конфигурации экспорта в Painter менялись между мажорными версиями (например, `ExportUASConfig`/`ExportOutputConfig` против более ранних конструкторов). Сверься с `help(substance_painter.export)` в Python-консоли Painter — это надёжнее любой статьи.

### 4. В Blender: собрать материал из карт

```python
# build_pbr_material.py — Blender: Text Editor → Run Script
import bpy, os

EXPORT_DIR = r"C:\sp\export"

def _clear_and_build(mat, basecolor="BaseColor.png", metallic="Metallic.png",
                     roughness="Roughness.png", normal="Normal.png", ao="AO.png",
                     height="Height.exr"):
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    nodes, links = tree.nodes, tree.links

    out = nodes.new("ShaderNodeOutputMaterial"); out.location = (700, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (400, 0)

    def tex(filename, non_color=False):
        n = nodes.new("ShaderNodeTexImage"); n.location = (0, 0)
        path = os.path.join(EXPORT_DIR, filename)
        if not os.path.exists(path):
            print("нет карты:", filename); return None
        n.image = bpy.data.images.load(path, check_existing=False)
        n.image.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
        return n

    # sRGB только у BaseColor; Metallic/Roughness/AO — это данные
    for filename, key, non_color in [
        (basecolor,  "Base Color", False),
        (metallic,   "Metallic",   True),
        (roughness,  "Roughness",  True),
    ]:
        n = tex(filename, non_color)
        if n:
            links.new(n.outputs["Color"], bsdf.inputs[key])

    n = tex(normal, non_color=True)
    if n:
        nm = nodes.new("ShaderNodeNormalMap"); nm.location = (200, -300)
        nm.inputs["Strength"].default_value = 1.0
        links.new(n.outputs["Color"], nm.inputs["Color"])
        links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    n = tex(ao, non_color=True)
    if n:
        # Мультипликативное наложение AO на Base Color.
        mix = nodes.new("ShaderNodeMixRGB"); mix.location = (200, 250)
        mix.blend_type = 'MULTIPLY'; mix.inputs["Fac"].default_value = 1.0
        links.new(n.outputs["Color"], mix.inputs["Color2"])
        base = tex(basecolor)
        if base:
            links.new(base.outputs["Color"], mix.inputs["Color1"])
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

_clear_and_build(bpy.data.materials.get("M_Asset") or bpy.data.materials.new("M_Asset"))
```

#> [!NOTE]
> `ShaderNodeMixRGB` — это legacy-идентификатор: в Blender 4.x нода Mix в меню Add переехала в `ShaderNodeMix` с полем `data_type`, и старый тип оставлен для совместимости скриптов. Если в твоей версии `nodes.new("ShaderNodeMixRGB")` бросает `TypeError`, замени на `ShaderNodeMix` с `data_type='RGBA'` и `blend_type='MULTIPLY'`; входы у новой ноды продублированы по типам, так что обращайся к ним по индексам, а не по именам.

## 5. UDIM: импорт тайлов в Blender

Painter пишет тайлы отдельными файлами (`<Set>_1001.png` и далее). Blender читает их как **одну** текстуру, если при импорте указать номера тайлов.

```text
Blender → Image Editor → Image → Open
  → в файловом диалоге выбрать НЕСКОЛЬКО файлов с именами вида 1001.png, 1002.png …
  → Blender соберёт их в один tile-датаблок
  → в ноде Image Texture ничего менять не нужно: проекция уже UDIM
```

Программно через `bpy.data`:

```python
import bpy, os

EXPORT_DIR = r"C:\sp\export"

tiles = sorted(
    f for f in os.listdir(EXPORT_DIR)
    if f.endswith(".png") and f.rsplit("_", 1)[-1].split(".")[0].isdigit()
)
print("тайлов найдено:", len(tiles), tiles[:4])

# Важно: bpy.data.images.load() на каждый файл по отдельности НЕ собирает
# тайлы — получится N отдельных датаблоков. Тайлы собирает оператор
# image.open, когда ему передают список файлов.
bpy.ops.image.open(
    directory=EXPORT_DIR + os.sep,
    files=[bpy.types.FileSelectEntry(name=n) for n in tiles],
)

# Проверка: у собра изображения должен появиться список тайлов
for img in bpy.data.images:
    if getattr(img, "source", None) == 'TILED':
        print("UDIM-датаблок:", img.name, "тайлов:", len(img.tiles))
```

Через UI это делается ровно так же: `Image Editor → Image → Open`, выбрать в диалоге все файлы `*_1001.png … *_1004.png` сразу — и Blender соберёт их в один датаблок. Отдельно тайлы раскладываются сеткой оператором UV-редактора:

```python
# Разложить UV по сетке тайлов. Оператор живёт в контексте UV-редактора,
# поэтому включи контекст явно — из Text Editor он может не сработать.
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)   # на случай, если развёртки нет
with bpy.context.temp_override(area=bpy.context.screen.areas[0]):
    bpy.ops.uv.uv_layout_generate_tile_grid(image=bpy.data.images["BaseColor"], grid_x=4, grid_y=4)
```

> [!NOTE]
> `uv_layout_generate_tile_grid` — оператор UV-редактора, и его сигнатура (а также то, обязателен ли для него активный объект и открытый UV-редактор) менялась между версиями Blender. Проверь `bpy.ops.uv.uv_layout_generate_tile_grid.get_rna_type().properties` в своей версии; если оператора нет — разложи тайлы вручную через Image Editor.

### 6. «Живой» цикл: Blender сам подхватывает новые файлы

```python
# watcher.py — следит за папкой экспорта и перезагружает текстуры
import bpy, os

EXPORT_DIR = r"C:\sp\export"
_seen = {}

def _poll():
    if not os.path.isdir(EXPORT_DIR):
        return 2.0
    for img in list(bpy.data.images):
        if not img.filepath_raw or not os.path.isabs(bpy.path.abspath(img.filepath_raw)):
            continue
        path = bpy.path.abspath(img.filepath_raw)
        if os.path.dirname(path).lower() != os.path.normcase(EXPORT_DIR).lower():
            continue
        mtime = os.path.getmtime(path)
        if _seen.get(img.name) != mtime:
            _seen[img.name] = mtime
            img.reload()
            img.update()
            print("[painter] обновлено:", os.path.basename(path))
    return 1.5

if _poll not in bpy.app.timers:
    bpy.app.timers.register(_poll, first_interval=1.5)
```

Чтобы цикл не ждал перерисовки вручную, добавь перерисовку вьюпорта:

```python
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.tag_redraw()
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Painter: повторный батч-экспорт всех texture set с одним пресетом
# (через встроенную Python-консоль Painter, не через системный Python)
# substance_painter.project.execute_when_not_busy(do_export)

# Blender: headless-пересборка материалов после экспорта — для CI
blender --background scene.blend --python build_pbr_material.py -- --out C:/sp/export
```

```python
# Проверка, что все карты на месте, до того как начнётся сборка нод
import os
EXPORT_DIR = r"C:\sp\export"
required = ["BaseColor.png", "Metallic.png", "Roughness.png", "Normal.png", "Height.exr"]
for f in required:
    p = os.path.join(EXPORT_DIR, f)
    print(f"{'OK ' if os.path.exists(p) else 'MISS'} {f}"
          + (f"  {os.path.getsize(p)//1024} KB" if os.path.exists(p) else ""))
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| `sizeLog2` / размер карт | 11 = 2K, 12 = 4K | 4K на 4GB VRAM — уже тесно, считай окно Painter |
| Normal: bitDepth | 16 | 8 бит даёт бандинг на больших гладких поверхностях |
| Height: fileFormat | `exr`, 32 bit | если используешь Displace, а не Bump |
| `paddingAlgorithm` | `infinite` для тайлов, `finite` для отдельных карт | UDIM требует бесшовности по краю |
| `dithering` | 8-бит карты — да, 16-бит normal — нет | dithering ломает карты, считываемые как данные |
| `use_mesh_modifiers` при экспорте FBX | `True` | выключи, если не хочешь применять модификаторы |
| Таймер опроса | 1.0–2.0 с | меньше 0.5 — нагрузка на диск без пользы |
| colorspace карты | BaseColor `sRGB`, остальные `Non-Color` | ошибка здесь не видна в viewport, но видна в рендере |

### Про smart materials и экспорт

Smart materials (и вообще весь процедурный слой Painter) **не экспортируются**. Выход — только разрешённые каналы: Base Color, Metallic, Roughness, Normal, Height, AO, Opacity, Emissive. Если в сцене нужен процедурный слой, вариантов два: оставить Artist Tool поверх карты в Blender, или генерировать процедурный слой в Substance Designer (см. SETUP 19).

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| Текстура плоская, curvature/AO пустые | В FBX усреднённые нормали или не применён Subdivision | `mesh_smooth_type='FACE'`, `use_mesh_modifiers=True`; в Painter проверь карту curvature на глаз |
| Меш в Painter лежит/повёрнут не так | Несовпадение систем осей | Правь `axis_forward`/`axis_up` в экспорте; для FBX в Painter есть переключатель оси |
| Меш в Blender после импорта вверх ногами | Обратная задача | Импортируй FBX с теми же `axis_forward`/`axis_up`, что и экспортировал |
| Карты с чёрными рамками по краям | Не задан `paddingAlgorithm` | Для UDIM — `infinite`; переэкспортируй |
| Нормали «пластиковые» / полосатые | 8-битный PNG для normal | 16 бит, и dithering выключить |
| Металл выглядит как пластик | Metallic/Roughness подключены как sRGB или AO перемножен в Base Color с инверсией | Обе карты — `Non-Color`; AO только MULTIPLY, Fac = 1.0 |
| UDIM-текстура не занимает весь меш | При импорте указаны не все тайлы | Переимпортируй, выбрав все файлы `*_10xx.png` разом |
| Новые файлы из Painter не подхватываются | Таймер не зарегистрирован или сцена открыта в background | Проверь `bpy.app.timers.is_registered(_poll)`; в headless это не сработает |
| Painter молча ничего не экспортирует | Экспорт вызвался в занятом состоянии | Оборачивай в `execute_when_not_busy` |
| Долгая пауза перед появлением карты | Painter считает карты и dithering одновременно | Считай по одной карте, dithering — только на цветовых |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 19: SUBSTANCE DESIGNER SBSAR](setup_19_substance_designer_sbsar.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #substance