---
id: wf_18_isometric_game_art
lang: ru
category: workflows
type: workflow
status: full
tags: [stylized, workflow]
---
# WF 18: ISOMETRIC GAME ART

**ID:** WF-18 | **Type:** Game | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: Ortho 54.7°, tileable, atlas, Godot export
EN: Ortho 54.7°, tileable, atlas, Godot export

Изометрические тайлы и ассеты для игры: тайл земли, который повторяется без шва,
набор спрайтов/моделей под одну и ту же проекцию, всё выверено под одну камеру и
экспортировано в движок. Главная сложность — **не геометрия, а согласованность**:
если один ассет снят при 54.736°, а второй при 60°, они не совпадут ни при каком
движении камеры, и переделать потом дорого.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | ortho-камера, тайлинг, glTF-экспорт |
| Бесшовные текстуры | Poly Haven / CC0 | тайл земли |
| Godot | 4.x | приём glTF / PNG |
| Спрайт-лист (атлас) | — | 1 текстура на много объектов |

## 🛠 НАСТРОЙКА

### Шаг 0. Сначала математика: 54.736° и 60° — это разное

Это главная путаница, и она не косметическая — от угла зависит сетка пикселей.

| Проекция | Наклон камеры (X) | След плитки на экране | Когда берут |
|---|---|---|---|
| True isometric | `54.7356°` | √3 : 1 | 3D-рендер без пиксель-арта |
| Dimetric 2:1 | `60°` | **2 : 1** | пиксель-арт и тайлы, «классическая изометрия» |

Закон простой: при повороте по Z на 45° отношение ширины к высоте следа плитки равно
`1 : cos(X)`. Отсюда `cos X = 0.5` → `X = 60°` для 2:1, а `cos 54.736° ≈ 0.577` → √3:1.

```python
import bpy, math

TRUE_ISO  = math.radians(54.7356)   # atan(sqrt(2))
PIXEL_ISO = math.radians(60.0)       # 2:1

def make_iso_camera(angle=PIXEL_ISO, ortho_scale=10.0, distance=40.0):
    cam_data = bpy.data.cameras.new("IsoCam")
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)

    cam_data.type = 'ORTHO'            # именно ортокамера: перспектива «плывёт» по глубине
    cam_data.ortho_scale = ortho_scale
    cam.rotation_euler = (angle, 0.0, math.radians(45.0))

    # Точку схода держим на Z = 0: сетка плиток уходит в горизонт, а не «в небо».
    # Для true iso направление взгляда единичное = (0.5774, -0.5774, 0.8165).
    v = (math.sin(angle) * math.sqrt(0.5),
         -math.sin(angle) * math.sqrt(0.5),
         math.cos(angle))
    cam.location = (v[0] * distance, v[1] * distance, v[2] * distance)
    cam_data.clip_end = distance * 4.0
    bpy.context.scene.camera = cam
    return cam
```

### Этап 1. Тайл земли: сетка 1×1 и UV вне диапазона

```python
import bpy
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# 1 юнит = 1 метр = 1 тайл. Это обязательное условие: иначе тайл «поедет»
# при масштабировании коллизий в движке.
bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=2, size=1.0)
tile = bpy.context.object
tile.name = "Tile_Ground"
```

Тайл делается **больше 1×1 в UV**, а Image Texture ставится в `REPEAT`. Так он
бесшовный при любом масштабе и не зависит от того, как разложены UV.

```python
uv = tile.data.uv_layers.active
for loop in tile.data.loops:
    uv.data[loop.index].uv = (loop.vertex.co.x * 2.0, loop.vertex.co.y * 2.0)

mat = bpy.data.materials.new("Mat_Tile")
mat.use_nodes = True
nt = mat.node_tree
p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load("//textures/grass_bare.png")
tex.extension = 'REPEAT'                 # повтор по краям кадра текстуры
nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
```

> [!NOTE]
> Бесшовность берётся либо из флага источника изображения, либо из подготовки
> самого файла. В свойствах Image (Properties → Image → Source) есть вариант
> `SEAMLESS`, который пересобирает текстуру в tile-паттерн; альтернатива —
> `extension = 'MIRROR'` у ноды, дающая бесшовный повтор за счёт зеркальных
> половин. Оба способа реальны, но дают разный рисунок: выбирай осознанно.

### Этап 2. Атлас: padding обязателен

В атласе билинейная интерполяция соседних UV тянет цвет из соседней плитки, и по
краям каждого спрайта появляется светлая кайма. Лечится только отступами.

```python
# Плитка 2x2 с отступом 4 px при атласе 1024 => 4 тайла по 256 без каймы
PAD, TILE = 4, 256
ATLAS = 1024
uv = tile.data.uv_layers.active

def atlas_uv(col, row, cells=2):
    step = TILE / ATLAS
    off = (PAD / ATLAS) * cells
    uv.data[loop.index].uv = (
        col * step + off, row * step + off)

for loop in tile.data.loops:
    atlas_uv(0, 0)   # пример: один тайл в левом нижнем углу атласа
```

> [!NOTE]
> Увеличение шага и добавление рамки — упрощённая схема; в продакшне атлас либо
> собирают внешним инструментом, либо выносят тайлы в отдельные материалы.
> Альтернатива атласу — текстурный массив: в нём нет соседних плиток, поэтому
> каймы не бывает by design. Проверь, поддерживает ли твой экспортёр/движок
> текстурные массивы, прежде чем выбирать этот путь.

### Этап 3. Свет и схема: три направления, никаких новых

При изометрии источник света «виден» только если он даёт ровно три градации на
каждой из 6 граней куба — иначе тайлы читаются как разноцветные ромбы, а не как
объёмные блоки.

```python
import math
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), 0, math.radians(35)))
sun = bpy.context.object
sun.data.energy = 3.0
sun.data.angle = math.radians(3.0)      # мягче = меньше «каши» на мелких тайлах

scene.view_settings.view_transform = 'Standard'   # плоские цвета, как в игре
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in \
    {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items} \
    else 'BLENDER_EEVEE'
```

### Этап 4. Рендер тайла и ассет-прототипов

```python
scene.render.film_transparent = True    # обязательно: фон должен быть альфой
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_x = scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.filepath = "//game/tiles/iso_tile_"
bpy.ops.render.render(write_still=True)

# Спрайт-лист персонажа: 4 направления × 4 кадра
scene.render.resolution_x, scene.render.resolution_y = 2048, 2048
scene.frame_start, scene.frame_end = 1, 4
scene.render.filepath = "//game/sprites/hero_"
bpy.ops.render.render(animation=True)
```

Тени на изометрии — отдельный трюк: включи **shadow catcher** на плоскости под
объектом, чтобы тень стала альфой в том же файле, что и спрайт.

```python
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0.001))
shadow = bpy.context.object
shadow.is_shadow_catcher = True          # Cycles; в EEVEE это не работает
```

### Этап 5. Экспорт в движок

```python
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type == 'MESH':
        ob.select_set(True)
bpy.ops.export_scene.gltf(
    filepath="//game/export/iso_level.glb",
    export_format='GLB',
    use_selection=True,
    export_apply=True,        # применить модификаторы на экспорт
    export_texcoords=True,
    export_normals=True,
    export_yup=True,          # Blender Z-up -> glTF Y-up. Не выключай.
)
```

> [!NOTE]
> Список параметров glTF-экспортёра менялся между версиями: часть флагов переехала
> в другую вкладку и переименована. Точный набор для твоей сборки смотри так:
> `[p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties]`.
> Универсально безопасны только `filepath`, `export_format`, `use_selection`.

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| Наклон камеры | 60° (2:1) или 54.7356° (true iso) | менять только до начала ассетов |
| `ortho_scale` | ширина тайла в пикселях / 1024 | подгонять под сетку |
| `film_transparent` | `True` | для спрайтов обязательно |
| `view_transform` | `'Standard'` | AgX «приближает» цвета к реализму |
| Атлас padding | 4 px на 256 | при мыльном рендере — до 8 px |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Тайл земли | `iso_tile.png`, 1024×1024, RGBA, бесшовный |
| Спрайт-лист | `hero_0001…0004.png`, 2048×2048 × 4 кадра, альфа в отдельном канале |
| 3D-экспорт | `iso_level.glb`, ~2–20 МБ |
| Рендер | тайл — **секунды**, спрайт-лист 4 кадра — **1–4 мин** EEVEE |
| Тайминг | один тайл + один спрайт-лист = рабочий атом ассет-пака |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Тайл видно швом | UV ровно 0–1 и `extension = 'CLIP'` | `extension = 'REPEAT'` + UV 0–2 |
| Светлая кайма по краям спрайта | нет padding в атласе | 4–8 px отступа либо текстурный массив |
| Соседние тайлы «плывут» | не совпадает масштаб UV и единицы сцены | `unit_settings.scale_length = 1.0`, UV = миры × N |
| Тайлы не стыкуются в игре | экспорт с неприменённым скейлом | `export_apply=True`, в движке не масштабировать |
| Всё «плоское», нет объёма | источник света фронтально | поднять угол солнца до 45–60°, убрать ambient |
| Взлетело не туда при импорте | Z-up против Y-up | `export_yup=True` при экспорте |
| Часть ассетов не совпала | их снимали с другим углом камеры | переснять всё с одной камеры |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 16: NPR ANIME RENDER](wf_16_npr_anime_render.md), [WF 19: VOXEL ART PIPELINE](wf_19_voxel_art_pipeline.md), [WF 20: KITBASH GREEBLE CITY](wf_20_kitbash_greeble.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md)
- **По темам:** [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md), [CASE 09: ANIME HEAD BUST](../cases/case_09_anime_head_bust.md), [CASE 11: COZY ROOM DIORAMA](../cases/case_11_cozy_room_diorama.md)
- **Теги:** #stylized, #workflow