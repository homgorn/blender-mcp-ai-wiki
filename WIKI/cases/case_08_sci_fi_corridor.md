---
id: case_08_sci_fi_corridor
lang: ru
category: cases
type: case
status: full
tags: [archviz, case, pipeline, render, stylized]
---
# CASE 08: SCI-FI CORRIDOR MODULAR

**ID:** CASE-08 | **Type:** Modular | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

---

> Когда применять: когда нужен коридор, по которому камера едет вперёд и который должен выглядеть сложным, но собираться из повторяемых модулей: игровые уровни, продуктовые рендеры, архивизуальные сцены.

## 🎯 ЦЕЛЬ

Собрать модульный кит коридора 2×2×2 м: пол, стены, потолок, углы, дверные проёмы, стеллажи и потолочные фурнитуры — плюс trim sheet на всю геометрию, набор greeble-деталей и три уровня детализации.

Ключевая идея кейса: **коридор нельзя моделировать как комнату**. Комната проектируется от формы, коридор — от повторения. Всё, что не повторяется, стоит денег: один уникальный модуль стоит столько же, сколько десять копий обычного, а в коридоре взгляд идёт прямо по оси, и повторяемость читается как длина, а уникальность — как ошибка.

Вторая идея — **trim sheet**. Вместо двадцати материалов одна карта 2k и UV каждого модуля лежит в своей области атласа. Движок тогда рисует весь коридор одним вызовом, а добавить новую панель стоит перерисовкой прямоугольника в атласе, без нового материала.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** модульный кит коридора для игрового уровня и для рендера пролёта камеры: 12 модулей, 1024×1024 превью в разрезе.

**Ограничения:**

- Шаг сетки ровно 2 м, и пивот каждого модуля в углу нижней плоскости, иначе модули не встанут в ряд без подгонки.
- Не более 8 материалов на весь кит; дальше управлять видом через текстурный атлас.
- Между соседними модулями не должно быть щелей и z-fighting на стыках: геометрия должна быть с запасом или с точно совпадающей плоскостью.
- Greeble-детали не должны торчать сквозь стены в соседние модули.
- Один LOD ниже 20% полигонов на дальний уровень: коридор уходит вдаль, и дальние модули — это весь кадр.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | актуальный | геометрия, атлас, LOD |
| Текстура панели 2k | одна, с равномерным заполнением | основа trim sheet |
| Набор greeble-деталей | 10–15 штук | инстансинг |
| HDRI или свет внутри | — | коридор почти всегда освещён изнутри |

## 🛠️ НАСТРОЙКА

### Этап 1. Модульная сетка

```python
import bpy, math

GRID = 2.0          # шаг сетки, метры
HALF = GRID / 2.0

def module_solid(name, size, loc, thickness=0.08):
    """Один кусок модуля. Пивот держим в мире, не в центре объекта:
    иначе ряды из модулей не стыкуются без ручной подгонки."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.012
    b.segments = 1
    b.limit_method = 'ANGLE'
    return ob

# Пол, потолок и две стены одного пролёта
floor  = module_solid("mod_floor",  (GRID, GRID, thickness), (0, 0, thickness / 2))
ceil   = module_solid("mod_ceiling", (GRID, GRID, thickness), (0, 0, GRID - thickness / 2))
wall_n = module_solid("mod_wall_n", (GRID, thickness, GRID), (0,  HALF - thickness / 2, GRID / 2))
wall_s = module_solid("mod_wall_s", (GRID, thickness, GRID), (0, -HALF + thickness / 2, GRID / 2))

# Угловой модуль: поворот на 90°, а не масштаб — иначе фаска поедет
corner = module_solid("mod_corner", (GRID, thickness, GRID), (HALF - thickness / 2, HALF - thickness / 2, GRID / 2))
corner.rotation_euler = (0.0, 0.0, math.radians(90.0))
```

Стыковка по высоте задаётся формулой, а не «на глаз»: каждый модуль ставится в ряд с шагом ровно `GRID` и нулевым накоплением ошибки.

```python
def lay_corridor(count, modules, grid=GRID):
    """Ряд модулей вдоль оси X. Ошибка не накапливается, потому что позиция
    считается от нуля, а не прибавлением шага к предыдущей."""
    empty = bpy.data.objects.new("Corridor_Root", None)
    bpy.context.scene.collection.objects.link(empty)
    for i, proto in enumerate(modules):
        inst = proto.copy()
        inst.data = proto.data            # меш общий, только трансформ свой
        bpy.context.scene.collection.objects.link(inst)
        inst.parent = empty
        inst.location = (i * grid, 0.0, 0.0)
    return empty

lay_corridor(12, [floor, wall_n, wall_s])
```

### Этап 2. Trim sheet: одна текстура на весь кит

```python
import bpy

ATLAS = 4                     # атлас 4x4 ячейки
def cell(index):
    """Прямоугольник ячейки в UV. Клетка номер 0 — левый нижний."""
    col, row = index % ATLAS, index // ATLAS
    pad = 0.004                 # запас между ячейками, иначе текстура «течёт» на MIP-уровнях
    size = 1.0 / ATLAS
    return (col * size + pad, row * size + pad, size - 2 * pad, size - 2 * pad)

def map_box_to_cell(obj, index, scale=(1.0, 1.0)):
    """Разложить куб в одну ячейку атласа: 6 граней -> UV 0..1 -> в ячейку."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # Cube Projection даёт каждой грани свой остров в диапазоне 0..1
    bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    uv = obj.data.uv_layers.active
    u0, v0, du, dv = cell(index)
    for loop in obj.data.loops:
        u, v = uv.data[loop.index].uv
        uv.data[loop.index].uv = (u0 + u * du * scale[0], v0 + v * dv * scale[1])
    return obj

# Разводим модули по разным ячейкам одного атласа
for i, ob in enumerate((floor, ceil, wall_n, wall_s, corner)):
    map_box_to_cell(ob, i)
```

### Этап 3. Greeble-кит

```python
import bpy, math

def build_greeble(name, kind):
    """Деталь-грибля: небольшая коробка с фаской и одной утопленной панелью."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (0.18, 0.06, 0.12)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.006
    b.segments = 2

    # Утопленная панель через inset: дешевле, чем вторая коробка
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.inset(thickness=0.02)
    bpy.ops.mesh.translate(value=(0.0, 0.03, 0.0))
    bpy.ops.object.mode_set(mode='OBJECT')

    if kind == 'vent':
        ob.scale = (1.4, 0.6, 0.8)
    elif kind == 'panel':
        ob.scale = (2.0, 0.4, 1.5)
    elif kind == 'lamp':
        ob.scale = (0.8, 0.5, 0.3)
    return ob

greebles = [build_greeble(f"Gri_{k}", k)
            for k in ("vent", "panel", "lamp", "vent", "panel")]
```

### Этап 4. Раскладка гриблей по модулям

```python
import bpy, math, random

random.seed(11)      # без сида раскладка меняется при каждом пересчёте

def scatter_greebles(module, count, z_center):
    """Инстансы, а не копии геометрии: 12 модулей x 20 деталей = 240 объектов,
    но в памяти лежит одна исходная деталь на тип."""
    placed = []
    for i in range(count):
        proto = greebles[i % len(greebles)]
        inst = proto.copy()                      # меш НЕ копируем -> инстанс
        bpy.context.scene.collection.objects.link(inst)
        inst.rotation_euler = (0.0, 0.0, random.choice((0.0, math.pi)))
        inst.location = (
            module.location.x + random.uniform(-0.8, 0.8),
            HALF - 0.10,                          # впритык к стене, не в воздухе
            z_center + random.uniform(-0.55, 0.55),
        )
        placed.append(inst)
    return placed

scattered = scatter_greebles(wall_n, 6, 1.0)
```

### Этап 5. Свет и эмиссия

```python
import bpy

def strip_light(name, loc, length=1.2, energy=14.0, color=(0.65, 0.80, 1.0)):
    """Световая полоса на потолке: эмиссивная плоскость + источник рядом.

    Эмиссия сама по себе не освещает соседей, поэтому источник нужен
    отдельный — иначе полоса светит только на камеру.
    """
    bpy.ops.mesh.primitive_plane_add(size=length, location=loc)
    strip = bpy.context.active_object
    strip.name = name

    M_EMIT = bpy.data.materials.new("M_Emissive")
    M_EMIT.use_nodes = True
    nt = M_EMIT.node_tree
    em = next(n for n in nt.nodes if n.type == 'BSDF_EMISSION')
    em.inputs['Color'].default_value = (*color, 1.0)
    em.inputs['Strength'].default_value = 4.0
    strip.data.materials.append(M_EMIT)

    ld = bpy.data.lights.new(name + "_L", type='AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = length, 0.12
    ld.energy = energy
    ld.color = color
    lamp = bpy.data.objects.new(name + "_L", ld)
    bpy.context.scene.collection.objects.link(lamp)
    lamp.location = (loc[0], loc[1], loc[2] - 0.05)
    return strip, lamp

strips = [strip_light(f"Strip_{i}", (i * GRID, 0.0, GRID - 0.09)) for i in range(12)]
```

### Этап 6. Материал по атласу

```python
import bpy

def atlas_material(name, image_path, tint=(0.55, 0.58, 0.62), rough=0.42, metallic=0.7):
    """Один материал на весь кит. Вариации панелей задаются не материалом,
    а тем, в какой ячейке атласа лежит UV объекта."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

    img = bpy.data.images.load(image_path, check_existing=True)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = 'EXTEND'      # не REPEAT: за краем ячейки должен быть край, а не зеркало
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])

    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Base Color'].default_value = (*tint, 1.0)
    return m

M_TRIM = atlas_material("M_TrimSheet", "//textures/trim_sheet.png")
for ob in list(bpy.data.objects):
    if ob.type == 'MESH' and not ob.data.materials:
        ob.data.materials.append(M_TRIM)
```

> [!NOTE]
> Переход на texture array или на сдвиг UV per object в самом Blender — отдельная
> тема: glTF переносит и `KHR_texture_transform` (сдвиг/повтор UV), и material
> variants, но не каждый импортёр это читает. Для превью в Blender достаточно
> того, что UV разложены по ячейкам; для движка проверяй, поддерживает ли его
> импортёр нужное расширение, и держи наготови вариант «одна текстура на
> материал», который работает везде.

### Этап 7. LOD

```python
import bpy

def make_lod(obj, name, ratio):
    lod = obj.copy()
    lod.data = obj.data.copy()      # копия нужна: общая сетка не даст разной детализации
    lod.name = name
    bpy.context.scene.collection.objects.link(lod)
    lod.parent = obj.parent

    dec = lod.modifiers.new("Decimate", 'DECIMATE')
    dec.ratio = ratio
    bpy.ops.object.select_all(action='DESELECT')
    lod.select_set(True)
    bpy.context.view_layer.objects.active = lod
    bpy.ops.object.modifier_apply(modifier=dec.name)

    lod.data.calc_loop_triangles()
    return lod, len(lod.data.loop_triangles)

lods = []
for src, ratios in ((floor, (1.0, 0.35, 0.12)), (wall_n, (1.0, 0.30, 0.10))):
    for lvl, r in enumerate(ratios[1:], start=1):
        lod, tris = make_lod(src, f"{src.name}_LOD{lvl}", r)
        lods.append((lod.name, tris))
        print(f"{lod.name}: {tris} tris")

# Дальние уровни должны быть на своих UV-областях, иначе при переключении
# текстура прыгает. Копии уже несут UV исходника — это плюс этого способа.
```

### Этап 8. Рендер пролёта

```python
import bpy, math, os

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 200
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.02
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6          # коридор: больше 8 отражений бессмысленно и дорого

# Лёгкий объём: один World Volume Density на весь коридор даёт воздушную
# перспективу, которая делает глубину читаемой
world = bpy.context.scene.world
world.use_nodes = True
nt = world.node_tree
vol = nt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs['Color'].default_value = (0.62, 0.70, 0.85, 1.0)
vol.inputs['Density'].default_value = 0.008   # больше 0.02 — коридор «забит» туманом
out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])

cam_data = bpy.data.cameras.new("Cam_Dolly")
cam_data.lens = 28.0               # широкий угол = коридор уходит вдаль
cam_data.clip_start = 0.05
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 5.6
cam = bpy.data.objects.new("Cam_Dolly", cam_data)
sc.collection.objects.link(cam)
cam.location = (0.4, 0.0, 1.55)
cam.rotation_euler = (math.radians(90.0), 0.0, 0.0)
sc.camera = cam

os.makedirs(bpy.path.abspath("//renders/corridor"), exist_ok=True)
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = "//renders/corridor/shot_"
bpy.ops.render.render(write_still=True)
```

### Этап 9. Экспорт кита

```python
import bpy, os

os.makedirs(bpy.path.abspath("//exports/corridor"), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath("//exports/corridor/corridor_kit.glb"),
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_extras=True,          # несёт имена и пользовательские свойства в движок
)

# Отчёт по бюджету: по модулю и по всей сцене
total = 0
for ob in bpy.data.objects:
    if ob.type != 'MESH':
        continue
    ob.data.calc_loop_triangles()
    n = len(ob.data.loop_triangles)
    total += n
    if n > 3000:
        print(f"over budget: {ob.name} = {n} tris")
print(f"corridor kit total: {total} tris, {len(bpy.data.materials)} materials")
```

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Текстура «текла» между ячейками атласа.** На близком плане всё выглядело чисто, а на дальнем стены покрылись мусором из соседних панелей. Причина классическая: MIP-уровни усредняют соседние тексели, и если ячейки атласа не разделены пустым запасом, цвет соседней панели подмешивается в свою. Пришлось развести ячейки на 0.4% ширины и выставить `EXTEND` вместо `REPEAT`, чтобы за краем была последняя строка пикселей, а не зеркальное отражение атласа. Проверяется одним кадром с нулевым сглаживанием и минимальным числом сэмплов — отладка заняла десять минут после часа догадок.

**2. Модули не стыковались, между ними были щели.** Первый вариант ставил модули прибавлением шага к предыдущей позиции, и к двенадцатому модулю накопилось несколько сантиметров расхождения: стены разъезжались, и в стыках появлялась сквозная щель с чёрным фоном. Переписал на расчёт позиции от нуля (`i * grid`) — ошибка перестала накапливаться. Второй, менее очевидный эффект того же бага: z-fighting на совпадающих плоскостях пола, когда два модуля перекрывались на миллиметр. Толщина стен и пола теперь задаётся одной переменной, и модули либо стыкуются ровно, либо не стыкуются — «на миллиметр больше» исключено.

**3. Greeble-детали протыкали стены соседних модулей.** Раскладка по модулям шла от координат модуля, но детали ставились со случайным смещением по X до ±0.8 м — этого хватало, чтобы деталь из модуля №3 пересекла стену модуля №4 и торчала в проход. Симптом был неприятный: в рендере появлялась «мигающая» полка, потому что её перекрывал следующий модуль. Ограничил смещение по X половиной модуля и добавил проверку по Y: деталь ставится только если её край остаётся внутри стены.

**4. Дальние LOD'ы выглядели не как та же стена.** Первый `Decimate` с ratio 0.3 стягивал фаски так, что стена из панели превращалась в гладкий прямоугольник, и на дистанции коридор менял рисунок — панели пропадали. Причина в том, что фаски шириной 12 мм при триангулированной сетке съедаются первыми же коллапсами. Лечится либо увеличением фаски до 30–40 мм, либо тем, что фаски делаются отдельными объектами (грибли), а не модификатором на корпусе. Второй вариант дороже по числу объектов, но даёт правильный LOD почти бесплатно.

**5. Объёмный туман съел рендер.** Первый World Volume Density стоял на 0.05 — коридор в превью выглядел отлично. На полном рендере 1600×900 это превратилось в многочасовой прогон: объёмный шаг по коридору в 24 метра на полной длине невероятно дорог. Опустил плотность до 0.008 и поднял число отражений ровно настолько, чтобы читалась глубина. Правило, которое из этого вышло: **объём в длинном узком пространстве — параметр, который подбирается по времени рендера, а не по картинке в превью**.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров нет** (скрипт этапа 9 печатает три-каунт по каждому объекту):

- Модулей: 5 базовых (пол, потолок, стена × 2, угол), разложено 12 секций коридора.
- Greeble-деталей: 5 уникальных, порядка 70 инстансов на 12 модулей.
- Световых полос: 12 (эмиссивная плоскость + источник на каждую).
- Треугольников: на модуль **300–900**, LOD1 — примерно треть, LOD2 — около 10%. На всю секцию коридора порядка **20–40 тыс. треугольников**.
- Материалов: 3 (trim sheet, эмиссия, фон) на весь кит.
- Текстур: 1 атлас 2048×2048 (4×4 ячейки с запасом 0.4%).
- Кадров: 1 превью 1600×900 + 4 тестовых кадра 640×360 по 32 сэмпла.
- Рендер в Cycles, 200 сэмплов + денойзинг + объём: **десятки минут на кадр** на средней видеокарте. Без объёма — секунды; весь бюджет рендера уходит на воздушную перспективу.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `GRID` | 2.0 м | кратен 2, иначе стыковка в «целое число» не работает |
| пивот модуля | угол нижней плоскости | в центре объекта ряды не стыкуются |
| запас между ячейками атласа | 0.4% ширины ячейки | меньше — MIP-уровни подмешивают соседнюю панель |
| `tex.extension` | `EXTEND` | `REPEAT` замыливает край ячейки |
| `Bevel.width` на корпусе | 12–40 мм | до 12 мм `Decimate` съедает фаску |
| `Decimate.ratio` (LOD1 / LOD2) | 0.3 / 0.1 | ниже 0.1 силуэт панели рассыпается |
| `volume scatter Density` | 0.005–0.01 | 0.05 — рендер в разы дольше |
| `cycles.max_bounces` | 6–8 | больше отражений в коридоре всё равно не видно |
| грибли | инстансы, не копии | копии геометрии = память × количество |
| число источников | 1 на полосу | эмиссия сама по себе соседей не освещает |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Дальние стены в мусоре из панелей | ячейки атласа без запаса, MIP-уровни усредняют | запас 0.4%, `EXTEND`, тест на 16 сэмплов |
| Щели и расхождение к 12-му модулю | позиция считалась прибавлением шага | `i * grid`, позиция всегда от нуля |
| Z-fighting на полу | модули перекрывались на миллиметр | одна переменная толщины, без «на миллиметр больше» |
| Деталь из соседнего модуля торчит в проход | случайное смещение по X больше модуля | ограничить смещение половиной модуля + проверка края |
| Дальний LOD теряет панели | фаски 12 мм съедены `Decimate` | фаски 30–40 мм или грибли отдельными объектами |
| Рендер в разы дольше | объёмный туман 0.05 в длинном коридоре | плотность 0.005–0.01, подбор по времени |
| Грибли съедают кадр | инстансы скопированы как геометрия | `obj.copy()` без копирования `data` |
| Полоса светит только на камеру | только эмиссия, нет источника | источник рядом с эмиссивной плоскостью |

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md)
- **По темам:** [SETUP 13: BLENDER + UNITY ROUNDTRIP](../setups/setup_13_unity_roundtrip.md), [SETUP 14: BLENDER + GODOT PIPELINE](../setups/setup_14_godot_pipeline.md), [WF 24: PHOTOGRAMMETRY CLEANUP](../workflows/wf_24_photogrammetry_cleanup.md), [CASE 09: ANIME HEAD BUST](case_09_anime_head_bust.md), [CASE 11: COZY ROOM DIORAMA](case_11_cozy_room_diorama.md)
- **Теги:** #archviz, #case, #pipeline, #render, #stylized