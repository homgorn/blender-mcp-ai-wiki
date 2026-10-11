---
id: case_16_dungeon_tileset
lang: ru
category: cases
type: case
status: full
tags: [case, game-assets]
---
# CASE 16: DUNGEON TILESET

**ID:** CASE-16 | **Type:** Tileset | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен модульный тайлсет уровня для игры: плиты пола, стены, углы, дверные проёмы, лестницы — всё в одной сетке, с общей текстурой и привязкой к сетке движка.

## 🎯 ЦЕЛЬ

Набор модулей под сетку 2×2 м: 12 плит пола, 8 стеновых модулей (прямая, угол внутренний/внешний, Т-образный, торец), 4 модуля перехода и 3 вариации на все случаи жизни. Всё в одной сетке, с одним материалом и одной атлас-картой 2048×2048, готовое к экспорту в Unity/Godot без ручной доводки.

Главное требование к тайлсету — **совместимость краёв**. Модули должны стыковаться без щелей и без перекрытий, иначе уровень соберётся с видимыми швами.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** подполье уровня 1: каменные плиты с трещинами, кирпичные стены, переходы в тоннель.

**Ограничения:**

- Сетка 2×2 м — под размер стандартного тайла Unity (2 units при 1 unit = 1 м).
- Один материал на весь тайлсет. Три материала — это три вызова шейдера на модуль и лишние вызовы отрисовки.
- Повторяющиеся части (кирпичи, плиты) — через UV, а не через геометрию.
- Модули не должны пересекаться между собой при повороте: угол 90° — это поворот на месте, а не зеркалирование.
- Три вариации на каждый модуль, чтобы уровень не читался как «одна и та же комната 40 раз».

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с UV-редактором | встроенный | атлас |
| Текстура 2048×2048 | рисуется или генерируется | один материал |
| Snapping в сцене | `Tool Settings → Snap` | ручная выкладка по сетке |
| Плагин FBX для экспорта | обычно включён | экспорт в движок |

## 🛠️ НАСТРОЙКА

### Этап 1. Сетка и привязка

```bash
RU: "Единица = 1 м, сетка 2 м, привязка INCREMENT 0.5 м.
     Создай плоскость 2x2 м как тайл, один материал M_Tileset,
     UV-карта на весь лист атласа 0..1"
EN: "Unit = 1 m, grid 2 m, snap INCREMENT 0.5 m.
     Create a 2x2 m plane as the tile, one material M_Tileset,
     UV map covering the whole 0..1 atlas"
```

```python
import bpy
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
sc.unit_settings.length_unit = 'METERS'

ts = sc.tool_settings
ts.use_snap = True
ts.snap_elements = {'INCREMENT'}
ts.snap_increment = 0.5           # половина тайла: стены прилипают к сетке

def make_tile(name, sx, sy, sz, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=max(2, int(sx / 0.25)),
                                    y_subdivisions=2, size=2, location=(0, 0, 0))
    grid = bpy.context.active_object
    mesh = grid.data
    # превращаем сетку-шаблон в нижнюю грань плитки: так контролируем число вершин
    v = [tuple(p.co * (sx / 2, sy / 2, 1)) for p in mesh.vertices]
    f = [tuple(p.vertices) for p in mesh.polygons]
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(v, [], f)
    me.update()
    grid.data = me
    me.materials.append(bpy.data.materials["M_Tileset"])
    grid.location = loc
    return grid
```

### Этап 2. Модули пола

```python
import bpy, math

M_TILESET = bpy.data.materials.new("M_Tileset")
M_TILESET.use_nodes = True

TILE = 2.0
floors = []
for i in range(3):
    t = make_tile(f"Floor_{i}", TILE, TILE, 0.10, (i * TILE, 0, 0))
    t.rotation_euler = (0, 0, math.radians(90 * i))   # три поворота = три вариации
    floors.append(t)

# трещины как отдельная деталь: тонкие V-образные прорези-инкрузии
bpy.ops.mesh.primitive_plane_add(size=1, location=(TILE / 2, 0.4, 0.0505))
crack = bpy.context.active_object
crack.name = "Crack_01"
crack.scale = (1.4, 0.02, 1.0)
crack.rotation_euler = (0, 0, math.radians(23))
crack.data.materials.append(bpy.data.materials["M_Tileset"])
```

### Этап 3. Стеновые модули

Стены делаются из тех же кирпичных сегментов, но собранных в L и Т. Важно: угол — это **поворот на месте**, а не зеркалирование.

```python
import bpy, math

WALL_H = 3.0
WALL_T = 0.30

def wall_piece(name, sx, sy, loc, rot_z=0.0):
    ob = make_tile(name, sx, sy, WALL_H, loc)
    ob.rotation_euler = (0, 0, rot_z)
    ob.location = (loc[0], loc[1], WALL_H / 2)
    return ob

walls = []
for i in range(3):
    walls.append(wall_piece(f"Wall_Straight_{i}", TILE, WALL_T,
                            (i * TILE, TILE / 2, 0)))

# внутренний угол: два сегмента, поворот 90° на месте
for i, (sx, sy, dx, dy, rz) in enumerate((
        (TILE, WALL_T, -TILE / 2,  0.0, 0.0),
        (WALL_T, TILE,  0.0,    -TILE / 2, math.radians(90)))):
    walls.append(wall_piece(f"Corner_In_{i}", sx, sy, (TILE / 2 + dx, TILE / 2 + dy, 0), rz))

# внешний угол и торец
walls.append(wall_piece("Corner_Out_0", WALL_T, TILE, (TILE / 2 + TILE / 2, TILE / 2, 0),
                        math.radians(90)))
walls.append(wall_piece("Wall_End_0", TILE, WALL_T, (TILE * 1.5, TILE / 2, 0)))

# Т-образный стык: три сегмента от центра
for i, (sx, sy, dx, dy, rz) in enumerate((
        (TILE, WALL_T, 0.0, -TILE / 2, 0.0),
        (TILE, WALL_T, 0.0,  TILE / 2, 0.0),
        (WALL_T, TILE, -TILE / 2, 0.0, math.radians(90)))):
    walls.append(wall_piece(f"Wall_T_{i}", sx, sy, (TILE * 2 + dx, TILE / 2 + dy, 0), rz))

# дверной проём: два столба + перемычка, проём 1.2 x 2.1 м
DOOR_W, DOOR_H = 1.2, 2.1
POST = (TILE - DOOR_W) / 2
for i, dx in enumerate((-DOOR_W / 2 - POST / 2, DOOR_W / 2 + POST / 2)):
    walls.append(wall_piece(f"Door_Post_{i}", POST, WALL_T,
                            (TILE * 3 + dx, TILE / 2, 0)))
lintel_h = (WALL_H - DOOR_H) / 2
walls.append(wall_piece("Door_Lintel", DOOR_W, WALL_T, (TILE * 3, TILE / 2, 0)))
bpy.data.objects["Door_Lintel"].scale.z = lintel_h / WALL_H
bpy.data.objects["Door_Lintel"].location.z = DOOR_H + lintel_h / 2

# лестница: 4 ступени
for i in range(4):
    step = make_tile(f"Stair_{i}", TILE, TILE * 0.25, 0.18 * (i + 1),
                     (TILE * 4, TILE / 2 - TILE * 0.4 + i * TILE * 0.25, 0))
    step.location.z = 0.09 * (i + 1)

print("модулей стен:", len(walls))
```

### Этап 4. Один материал с процедурными кирпичами

Один материал — ключевое требование. Кирпичи и плиты считаются в Generated-координатах, поэтому тайлы не «плывут» при повороте.

```python
import bpy
nt = M_TILESET.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs['Roughness'].default_value = 0.88

geo = nt.nodes.new("ShaderNodeNewGeometry")
brick = nt.nodes.new("ShaderNodeTexBrick")
brick.inputs['Scale'].default_value = 4.0
brick.inputs['Mortar Size'].default_value = 0.018
brick.inputs['Brick Width'].default_value = 0.55
brick.inputs['Row Height'].default_value = 0.22
brick.inputs['Color1'].default_value = (0.22, 0.19, 0.17, 1)
brick.inputs['Color2'].default_value = (0.27, 0.23, 0.20, 1)
brick.inputs['Mortar'].default_value = (0.11, 0.10, 0.10, 1)

noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs['Scale'].default_value = 22.0
noise.inputs['Detail'].default_value = 8.0
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs['Strength'].default_value = 0.4
bump.inputs['Distance'].default_value = 0.006

nt.links.new(geo.outputs['Position'], brick.inputs['Vector'])   # мировые -> не плывёт
nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])

# оттенок снизу вверх: у пола темнее (грязь), у верха светлее (пыль)
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs['From Min'].default_value = 0.0
mr.inputs['From Max'].default_value = 2.0
mr.inputs['To Min'].default_value = 0.55
mr.inputs['To Max'].default_value = 1.0
mixc = nt.nodes.new("ShaderNodeMixRGB")
mixc.blend_type = 'MULTIPLY'
mixc.inputs['Fac'].default_value = 0.6
nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
nt.links.new(brick.outputs['Color'], mixc.inputs[1])
nt.links.new(mr.outputs['Result'], mixc.inputs[2])
nt.links.new(mixc.outputs['Color'], bsdf.inputs['Base Color'])
```

Одного материала на весь тайлсет мало, если пол и стены выглядят одинаково. Переключатель по ориентации поверхности решает это, не заводя второго материала: горизонтальные грани (нормаль смотрит вверх) получают крупную плиту, остальные — кирпич.

```python
import bpy
nt = M_TILESET.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

norm = nt.nodes.new("ShaderNodeNewGeometry")
sep_n = nt.nodes.new("ShaderNodeSeparateXYZ")
thresh = nt.nodes.new("ShaderNodeMapRange")      # резкий переход: 0 -> 1 при Z > 0.9
thresh.interpolation_type = 'CONSTANT'
thresh.clamp = True
thresh.inputs['From Min'].default_value = 0.90
thresh.inputs['From Max'].default_value = 0.92
thresh.inputs['To Min'].default_value = 1.0      # фактор Mix: 1 = верхний вход
thresh.inputs['To Max'].default_value = 0.0

slab = nt.nodes.new("ShaderNodeTexBrick")        # крупная плитка пола
slab.inputs['Scale'].default_value = 1.6
slab.inputs['Mortar Size'].default_value = 0.012
slab.inputs['Brick Width'].default_value = 0.85
slab.inputs['Row Height'].default_value = 0.85
slab.inputs['Color1'].default_value = (0.26, 0.25, 0.23, 1)
slab.inputs['Color2'].default_value = (0.30, 0.29, 0.26, 1)
nt.links.new(norm.outputs['Normal'], sep_n.inputs['Vector'])
nt.links.new(sep_n.outputs['Z'], thresh.inputs['Value'])

pick = nt.nodes.new("ShaderNodeMixRGB")
nt.links.new(thresh.outputs['Result'], pick.inputs['Fac'])
nt.links.new(brick.outputs['Color'], pick.inputs[1])    # кирпич = нижний
nt.links.new(slab.outputs['Color'], pick.inputs[2])     # плита  = верхний
# далее pick ведёт в цепочку затемнения и в Base Color вместо mixc
for l in list(nt.links):
    if l.to_node == mixc and l.to_socket == mixc.inputs[1]:
        nt.links.remove(l)
nt.links.new(pick.outputs['Color'], mixc.inputs[1])
nt.links.new(norm.outputs['Normal'], slab.inputs['Vector'])
nt.links.new(norm.outputs['Normal'], brick.inputs['Vector'])
```

### Этап 5. Раскладка превью и проверка стыков

Самый полезный тест — собрать из модулей реальную комнату с закрытым углом и посмотреть на швы.

```bash
RU: "Собери тестовую комнату 6x6 м из тайлов: пол 3x3, стены по периметру,
     дверной проём в одной стене, один внешний угол. Рендер сверху-сбоку"
EN: "Build a test room 6x6 m from the tiles: 3x3 floor, perimeter walls,
     one door opening, one outer corner. Render from an elevated 3/4 angle"
```

```python
import bpy, math, os
sc = bpy.context.scene

TILE = 2.0
room = bpy.data.collections.new("TestRoom")
sc.collection.children.link(room)
test_objs = []

# пол 3x3
for ix in range(3):
    for iy in range(3):
        src = bpy.data.objects[f"Floor_{(ix + iy) % 3}"]
        d = src.copy(); d.data = src.data.copy(); d.name = f"T_Floor_{ix}{iy}"
        room.objects.link(d)
        d.location = (ix * TILE + TILE / 2, iy * TILE + TILE / 2, 0)
        d.rotation_euler = (0, 0, math.radians(90 * ((ix + iy) % 3)))
        test_objs.append(d)

# периметр: прямые стены + два угла
n = 4
for i in range(n):
    src = bpy.data.objects[f"Wall_Straight_{i % 3}"]
    for side in range(4):
        d = src.copy(); d.data = src.data.copy(); d.name = f"T_Wall_{i}{side}"
        room.objects.link(d)
        if side < 2:
            d.location = (i * TILE + TILE / 2, side * TILE * 3 + TILE / 2, 1.5)
        else:
            d.location = (side * TILE * 3 - TILE / 2, i * TILE + TILE / 2, 1.5)
            d.rotation_euler = (0, 0, math.radians(90))
        test_objs.append(d)

bpy.ops.object.select_all(action='DESELECT')
for o in test_objs: o.select_set(True)
bpy.context.view_layer.objects.active = test_objs[0]

bpy.ops.object.camera_add(location=(8.0, -8.0, 7.0))
cam = bpy.context.active_object; cam.data.lens = 45.0
c = cam.constraints.new('TRACK_TO'); c.target = test_objs[0]
c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
sc.camera = cam

ld = bpy.data.lights.new("Sun", type='SUN')
ld.energy = 3.0; ld.angle = math.radians(8)
sun = bpy.data.objects.new("Sun", ld); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))

sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
os.makedirs(bpy.path.abspath("//renders/tileset"), exist_ok=True)
sc.render.filepath = r"//renders/tileset/room_test.png"
bpy.ops.render.render(write_still=True)
```

### Этап 6. Экспорт в движок

```python
import bpy, math
sc = bpy.context.scene

# pivot в основании модуля: иначе в движке модули «прыгают» при размещении
for ob in bpy.data.objects:
    if ob.name.startswith(("Floor_", "Wall_", "Corner_", "Door_", "Stair_")):
        zs = [(ob.matrix_world @ v.co).z for v in ob.data.vertices]
        if not zs:
            continue
        cur = bpy.context.scene.cursor.location.copy()
        bpy.context.scene.cursor.location = (ob.location.x, ob.location.y, min(zs))
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
        bpy.context.scene.cursor.location = cur

mod_objs = [o for o in bpy.data.objects
            if o.name.startswith(("Floor_", "Wall_", "Corner_", "Door_", "Stair_"))]

bpy.ops.object.select_all(action='DESELECT')
for o in mod_objs: o.select_set(True)
bpy.context.view_layer.objects.active = mod_objs[0]

bpy.ops.export_scene.fbx(filepath=bpy.path.abspath("//export/dungeon_tileset.fbx"),
                         use_selection=True,
                         apply_unit_scale=True,
                         global_scale=1.0,
                         axis_forward='-Z', axis_up='Y',
                         object_types={'MESH'},
                         path_mode='AUTO',
                         mesh_smooth_type='FACE')
```

> [!NOTE]
> Имена аргументов экспорта FBX менялись между версиями (`use_mesh_modifiers` против `apply_unit_scale`/`global_scale`/`object_types`, добавление `path_mode`). Набор допустимых аргументов смотри так: `[p.identifier for p in bpy.ops.export_scene.fbx.get_rna_type().properties]` — это выведет точный список для твоей версии. Ось `axis_forward='-Z'`, `axis_up='Y'` — стандарт для Unity; для Godot/других движков значения другие.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `snap_increment` | 0.5 м | половина тайла — стены прилипают к сетке |
| `Brick Scale` | 3–6 | на 2-метровом модуле ~5 кирпичей в ряд |
| `Brick Width` / `Row Height` | 0.55 / 0.22 | соотношение 2.5:1 — нормальный кирпич |
| `Mortar Size` | 0.015–0.02 | выше — раствор выглядит толстым |
| `MapRange To Min` | 0.55 | затемнение низа = грязь внизу комнаты |
| `Bump.Distance` | 0.004–0.008 | крупнее — «кирпич из пенопласта» |
| поворот вариации | 90° шаг | 3 вариации дешевле, чем 3 отдельных модуля |
| `face_smooth_mode` | `FACE` | тайлы должны быть плоскими, иначе в игре каша |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Щели на стыках модулей появлялись при повороте.** Первая версия использовала `Smart UV Project` с `island_margin = 0.01` и рассчитывала, что этого хватит. При сборке комнаты из 16 модулей на трёх стыках появились вертикальные щели в 2–3 мм — они были видны даже на превью 1600×1200. Причина: после поворота объекта на 90° острова UV оставались в тех же местах листа, но соседний модуль брал соседний участок атласа, и на границе попадал интерполированный край. Решили отказом от атласа в пользу процедурной кирпичной текстуры, считаемой в `Geometry → Position`: у неё нет UV вообще, поэтому стык физически не может «протечь». Для плит пола отдельно уменьшили зазор до нуля за счёт `translate` геометрии на половину плитки.

**2. Привязка к сетке работала, но объекты «прыгали» в экспорте.** У всех модулей origin был в центре объекта, и при расстановке в редакторе уровня каждый модуль приходилось ставить вручную с поправкой на половину своей высоты. Пришлось переставить origin в основание (`origin_set` с курсором в нижней точке). Отдельно выяснилось, что масштаб объектов был 1.0, но применён не был — после экспорта в Unity часть модулей приходила с масштабом 0.999999 и визуально «щелкала» на стыках. Причина — неприменённый `transform_apply`, а не экспортёр.

**3. Один материал на весь тайлсет оказался сложнее, чем казалось.** Плата была простой: один материал и процедурный кирпич. Проблема вылезла в том, что **пол и стены выглядели одинаково**: та же кирпичная текстура, только с разным затенением. Три вариации на модуль стало три, но стены перестали отличаться от пола — читалось, что это одна и та же кладка. Вышло из этого через добавление переключателя по нормали: у `Geometry → Normal` Z-компонента > 0.9 (горизонтальная поверхность) шейдер уходил в крупную плиту, иначе — в кирпич. Один материал сохранился, но теперь он различает два типа поверхностей.

**4. Лестница не стыковалась с полом.** Первые три ступени получились, четвёртая вылезла на стену: шаг 0.18 м при глубине ступени 0.5 м дал подъём 0.72 м, а перепад между этажами был 0.6 м. Помогло согласовать: высоту ступени считать от перепада, а не от нуля, и глубину ступени брать 0.4 м при перепаде 0.6 м. Это не ошибка Blender, а ошибка проектирования — но на экспорте она стоила полдня.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров не проводилось:**

- Модулей: 3 плиты пола + 3 прямые стены + 2 внутренних угла + 1 внешний угол + 1 торец + 3 Т-стыка + 3 дверных элемента + 4 ступени + 1 трещина = **21 модуль**.
- Полигоны: каждый модуль — сетка 8×2 (16 квадов) или бокс с 6 гранями, плюс bevel не используется. Итого **~400–800 треугольников на весь тайлсет**.
- Материалов: **1** (`M_Tileset`), текстур **ноль** — вся фактура процедурная.
- Тестовая комната: 9 плит + 16 стеновых сегментов = 25 объектов, инстансы одного меша.
- Рендер 1600×1200, Cycles, 96 сэмплов: **секунды** — сцена крошечная.
- FBX: единицы мегабайт (одна геометрия, ноль текстур).

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Щели на стыках | UV-атлас + поворот объекта | процедурная текстура в `Geometry → Position` |
| Модули «прыгают» при расстановке | origin в центре | `origin_set` в нижнюю точку |
| Модули «щёлкают» в движке | неприменённый масштаб | `transform_apply(scale=True)` перед экспортом |
| Пол и стены выглядят одинаково | один узор на всё | переключатель по `Normal → Z` в шейдере |
| Лестница не стыкуется | высота шага не равна перепаду | считать шаг от перепада этажей |
| Стены «плывут» при перемещении | текстура в UV | текстура в Position, а не в UV |
| Слишком много draw call | вариации как отдельные объекты | три поворота одного меша вместо трёх модулей |

## ✅ РЕЗУЛЬТАТ

На выходе: коллекция из 21 модуля в сетке 2×2 м с одним материалом `M_Tileset`, тестовая комната 6×6 м, превью `//renders/tileset/room_test.png` (1600×1200) и FBX для движка.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md)
- **По темам:** [CASE 06: ANIMATION LOOP](case_06_animation_loop.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md)
- **Теги:** #case, #game-assets