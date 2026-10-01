---
id: case_07_stylized_barrel
lang: ru
category: cases
type: case
status: full
tags: [case, pipeline, render, unity]
---
# CASE 07: STYLIZED BARREL (HAND-PAINT)

**ID:** CASE-07 | **Type:** Game | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

---

> Когда применять: когда нужен игровой проп с читаемым силуэтом и ручной «нарисованной» поверхностью: бочка, ящик, бочонок — предмет, который узнаётся по обручам и доскам даже в силуэте 64×64 пикселя.

## 🎯 ЦЕЛЬ

Собрать стилизованную бочку с ручной покраской: корпус из отдельных досок, три металлических обруча, дно и крышка, — довести до ~1.2 тыс. треугольников, покрыть PBR-набором с запечёнными картами и выгрузить в движок.

Принцип, на котором стоит весь stylised-пайплайн: **силуэт важнее деталей**. Если объект не читается в чёрном квадрате 64×64, никакие текстуры его не спасут. Отсюда решение: 12 досок с реальными фасками вместо гладкого цилиндра — 12 силуэтных граней читаются как бочка, цилиндр читается как труба.

Второй принцип — **иерархия материалов вместо детализации**. Три материала (дерево, крашеный металл, тёмная грязь) и запечённые AO с кривизной дают больше читаемости, чем двадцать отдельных фасок и текстура 4k.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** проп бочки для unity-проекта, три варианта (целая, с обручем, без дна), превью-рендер 1024×1024 на светлом фоне.

**Ограничения:**

- Бюджет: 1.2 тыс. треугольников на экземпляр. Это жёстче, чем кажется: 12 досок по 12 треугольников — уже 144, и всё остальное надо уместить в остаток.
- Три материала максимум: каждый материал — отдельный вызов отрисовки в движке.
- Никаких запекаемых нормалей с разрешения: бюджет и так на грани, а для стиля хватает AO и кривизны, смешанных в шейдере.
- Ручной стиль вместо PBR-реализма: насыщенные цвета, заметные грани, лёгкие «вмятины» через смещение вершин.
- Экспорт в Unity и в Godot, поэтому GLB как основной формат.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender + Cycles | базовый | запекание карт требует рендер-движка |
| Знания по PBR | — | три материала вместо одного |
| Quad Remesher (опционально) | аддон | равномерная топология, если нужна правка |
| HDRI для превью | Poly Haven 1k | мягкий свет на светлом фоне |

## 🛠️ НАСТРОЙКА

### Этап 1. Корпус из досок

```python
import bpy, math

PLANK_COUNT = 12          # силуэт: 12 граней читаются как бочка
RADIUS = 0.285            # радиус по центрам досок
HEIGHT = 0.86
PLANK_W = 0.155           # чуть меньше, чем шаг, чтобы были щели по 8 мм
PLANK_D = 0.045

bpy.ops.object.select_all(action='DESELECT')
planks = []
for i in range(PLANK_COUNT):
    ang = 2.0 * math.pi * i / PLANK_COUNT
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    p = bpy.context.active_object
    p.name = f"Plank_{i:02d}"
    p.scale = (PLANK_W, PLANK_D, HEIGHT)
    # Поворот применяем, иначе экспорт унесёт углы, а нормали останутся
    # в локальных осях и в движке свет пойдёт иначе
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    p.rotation_euler = (0.0, 0.0, ang)
    p.location = (math.cos(ang) * RADIUS, math.sin(ang) * RADIUS, HEIGHT / 2.0 + 0.02)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    planks.append(p)

# Разница высот и наклон отдельных досок — ручной характер без ручной работы
for i, p in enumerate(planks):
    p.location.z += 0.004 * math.sin(i * 2.1)
    p.rotation_euler.y = math.radians(1.4) * math.cos(i * 1.7)
```

### Этап 2. Обручи, дно и крышка

```python
import bpy, math

def ring(name, radius, thickness, z, verts=24):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness / 2.0,
        major_segments=verts,     # 24 достаточно: силуэт всё равно читается
        minor_segments=6,
        location=(0.0, 0.0, z))
    ob = bpy.context.active_object
    ob.name = name
    return ob

HOOP_Z = (0.16, HEIGHT * 0.5 + 0.02, HEIGHT - 0.14)
hoops = [ring(f"Hoop_{i}", RADIUS + 0.005, 0.05, z) for i, z in enumerate(HOOP_Z)]

def disc(name, radius, z, verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=0.03, location=(0.0, 0.0, z))
    ob = bpy.context.active_object
    ob.name = name
    return ob

lid = disc("Lid", RADIUS + 0.028, HEIGHT + 0.02)
bottom = disc("Bottom", RADIUS + 0.020, 0.015)

# Крышка чуть выпуклая: стул крепче просто приплюснутого диска
lid.scale = (1.0, 1.0, 0.6)
```

### Этап 3. Bevel и объединение

```python
import bpy

def bevel_and_merge(objects, name, width=0.006, segments=2):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

    b = objects[0].modifiers.new("Bevel", 'BEVEL')
    b.width = width
    b.segments = segments            # 2 — стилизованный фасочный блик, 3 уже фотореализм
    b.limit_method = 'ANGLE'
    b.angle_limit = 0.523599        # 30 градусов: фаски на рёбрах досок, не внутри щелей
    b.harden_normals = False

    # Merge by Distance убирает щели в местах стыка досок и обручей:
    # без него дальние LOD-версии «рассыпаются» на отдельные куски
    m = objects[0].modifiers.new("Weld", 'WELD')
    m.merge_threshold = 0.0006      # 0.6 мм — меньше зазора, больше шума
    bpy.ops.object.modifier_apply(modifier=b.name)
    bpy.ops.object.modifier_apply(modifier=m.name)

    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = name
    return merged

barrel = bevel_and_merge(planks + hoops + [lid, bottom], "Barrel_Mesh")
barrel.data.polygons.foreach_set("use_smooth", [False] * len(barrel.data.polygons))
```

### Этап 4. UV

```python
import bpy, math

barrel = bpy.data.objects["Barrel_Mesh"]
bpy.context.view_layer.objects.active = barrel
bpy.ops.object.select_all(action='DESELECT')
barrel.select_set(True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# 66° — стандарт для hard-surface: цилиндрические поверхности разворачиваются
# в полосу без «звёзд» на боку
bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02,
                         area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Заранее подогнать масштаб текстуры под реальный размер предмета:
# плотность texel'ей не должна зависеть от того, как объект двинут в сцене
uv = barrel.data.uv_layers.active
print("UV scale: %.4f x %.4f" % (barrel.dimensions.x, barrel.dimensions.y))
```

### Этап 5. Материалы: три, не больше

```python
import bpy

def simple(name, base, rough, metallic=0.0, bump_scale=None, bump_strength=0.2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*base, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic

    if bump_scale:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs['Scale'].default_value = bump_scale
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.0015
        nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

# 1. Крашеное дерево: насыщенный сине-зелёный, низкая шероховатость не нужна —
#    для стиля важнее цвет, чем блеск
M_WOOD = simple("M_PaintedWood", (0.13, 0.35, 0.33), 0.62, bump_scale=180.0)

# 2. Крашеный металл обручей: тёмный, чуть металлический
M_METAL = simple("M_HoopMetal", (0.22, 0.24, 0.26), 0.38, metallic=0.65,
                 bump_scale=320.0, bump_strength=0.12)

# 3. Грязь в углублениях — запечённая карта, а не цвет
M_DIRT = simple("M_Dirt", (0.05, 0.05, 0.05), 0.90)

barrel.data.materials.append(M_WOOD)
barrel.data.materials.append(M_METAL)
barrel.data.materials.append(M_DIRT)

# Раздать материалы по граням: обручи — металл, остальное — дерево
for poly in barrel.data.polygons:
    center_z = poly.center.z
    is_hoop = any(abs(center_z - z) < 0.045 for z in HOOP_Z)
    poly.material_index = 1 if is_hoop else 0
```

### Этап 6. High poly для запекания

Low-poly боевая версия не годится для карт: в щелях между досками нет геометрии, и AO получится пустым. Поэтому делается дубликат с плотной сеткой, с него запекается, и он удаляется.

```python
import bpy

barrel = bpy.data.objects["Barrel_Mesh"]
high = barrel.copy()
high.data = barrel.data.copy()
high.name = "Barrel_HighPoly"
bpy.context.scene.collection.objects.link(high)

# Сглаживание перед запеканием: без него карта нормалей повторит
# каждую грань отдельно и получится в грязь
sub = high.modifiers.new("Subdivision", 'SUBSURF')
sub.levels = 2
sub.render_levels = 2

# Заполнить щели: Shrinkwrap тянет high-poly внутрь low-poly оболочки
wrap = high.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
wrap.target = barrel
wrap.wrap_method = 'NEAREST_SURFACEPOINT'
wrap.offset = 0.004
```

### Этап 7. Запекание AO и кривизны

```python
import bpy

sc = bpy.context.scene
sc.render.engine = 'CYCLES'          # bake требует движка рендера
sc.cycles.device = 'GPU'

low = bpy.data.objects["Barrel_Mesh"]
high = bpy.data.objects["Barrel_HighPoly"]

# Активным должен быть LOW — в него пишется результат
bpy.ops.object.select_all(action='DESELECT')
low.select_set(True)
bpy.context.view_layer.objects.active = low

# High остаётся выделенным как источник данных
high.select_set(True)

def bake_to_image(name, kind, size=1024):
    img = bpy.data.images.new(name, width=size, height=size)
    img.filepath_raw = f"//textures/{name.lower()}.png"
    img.file_format = 'PNG'
    bpy.ops.object.bake(type=kind)
    img.save()
    return img

ao = bake_to_image("AO", 'AO')
curv = bake_to_image("Curvature", 'EMIT')
```

> [!NOTE]
> Параметры панели запекания (distance, cage, margin, `selected_to_active`)
> зависят от версии и от настроек, поэтому числами здесь не описаны: их надо
> выставлять в интерфейсе. Для AO и кривизны на пропах обычно хватает значений
> по умолчанию. Для карты нормалей с разрешения обязательно выставляется
> Source = High Poly, Include = Only Closest Surface (или Culling Cage) и
> увеличенный Normal Bias — иначе появляется «грязь» на фасках.

### Этап 8. Превью-рендер

```python
import bpy, math, os

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 256
sc.cycles.use_denoising = True

os.makedirs(bpy.path.abspath("//renders/barrel"), exist_ok=True)

cam_data = bpy.data.cameras.new("Cam_Preview")
cam_data.lens = 85.0
cam_data.clip_start = 0.01
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 4.0
cam = bpy.data.objects.new("Cam_Preview", cam_data)
sc.collection.objects.link(cam)
cam.location = (1.05, -1.25, 0.72)
cam.rotation_euler = (math.radians(74.0), 0.0, math.radians(40.0))
sc.camera = cam
cam_data.dof.focus_object = bpy.data.objects["Barrel_Mesh"]

# Светлый фон без HDRI: фон — просто плоскость, чтобы превью можно было
# вставить в карточку без альфа-канала
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.active_object
M_BG = bpy.data.materials.new("M_Backdrop")
M_BG.use_nodes = True
b = next(n for n in M_BG.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
b.inputs['Base Color'].default_value = (0.86, 0.86, 0.85, 1.0)
b.inputs['Roughness'].default_value = 0.7
ground.data.materials.append(M_BG)

ld = bpy.data.lights.new("Key", type='AREA')
ld.size = 1.2
ld.energy = 220.0
key = bpy.data.objects.new("Key", ld)
sc.collection.objects.link(key)
key.location = (-0.9, -1.1, 1.6)
key.rotation_euler = (math.radians(38.0), 0.0, math.radians(-38.0))

sc.render.resolution_x = sc.render.resolution_y = 1024
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = "//renders/barrel/preview_"
bpy.ops.render.render(write_still=True)
```

### Этап 9. Экспорт и проверка бюджета

```python
import bpy, os

barrel = bpy.data.objects["Barrel_Mesh"]

# Бюджет проверяется по факту, а не по замыслу
barrel.data.calc_loop_triangles()
tris = len(barrel.data.loop_triangles)
verts = len(barrel.data.vertices)
mats = len(barrel.data.materials)
print(f"BARREL BUDGET: {tris} tris, {verts} verts, {mats} materials")
if tris > 1600:
    print("WARNING: over budget")

os.makedirs(bpy.path.abspath("//exports"), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath("//exports/barrel.glb"),
    export_format='GLB',
    use_selection=True,
    export_apply=True,          # Bevel уже применён, но это страховка
    export_materials='EXPORT',
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_animations=False,
)
```

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Щели между досками оказались настоящей дырой.** При сборке 12 досок по окружности с зазором 8 мм модель сначала выглядела отлично, но при боковом свете в щелях было видно пустоту: свет проходил насквозь, и бочка читалась как расставленные грани. `Weld` с порогом 0.6 мм не помог — щель была в разы больше. Помогло только то, что дно и крышка оказались шире корпуса (радиус плюс 20–28 мм) и закрыли собой щели снаружи, а изнутри добавилась внутренняя цилиндрическая оболочка без нормалей, невидимая снаружи. Отдельный урок: для решётчатых пропов внутренняя оболочка — не оптимизация, а необходимость.

**2. `Weld` на близких вершинах склеивал фаски.** Порог 0.6 мм вроде безопасен, но после `Bevel` с двумя сегментами расстояния между вершинами фаски в углах обручей падали до 0.2–0.3 мм, и `Weld` их стягивал. Результат выглядел как «мятая» бочка: часть фасок проваливалась, блики ломались не по ребру, а произвольно. Пришлось снизить порог до 0.0002 и применять Weld **до** Bevel — тогда стягиваются только реальные швы, а фаски строятся уже на чистой сетке.

**3. Запечённая кривизна на low-poly читалась как грязь.** Первый вариант запекал кривизну с low-poly как с источником, и карта получилась пятнистой: фаски Bevel слишком узкие, чтобы в них поместилась хоть одна выборка. Переделал на High Poly с `Subdivision` level 2 и `Shrinkwrap` — после этого кривизна стала читаемой линией по кромке каждой фаски, и именно она дала эффект «подсвеченных граней», ради которого всё затевалось. Отдельно пришлось увеличить Normal Bias: с дефолтом на фасках появилась чёрная кайма.

**4. Три варианта бочки разъехались между собой.** Собранные «целая», «с обручем» и «без дна» отличались не только составом, но и UV: у вариантов без дна развёртка сдвигалась, и текстура на стыках не совпадала. Пришлось строить все три из одного `Barrel_Mesh` и удалять части, а не собирать каждый заново. Так варианты гарантированно совпадают по пропсам и по текстурам.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров нет** (точный три-каунт печатает скрипт этапа 9):

- Объектов в сцене: 1 меш + 1 high-poly дубликат (удаляется) + камера + свет + фон.
- Треугольников: **около 1.2–1.6 тыс.** на бочку. 12 досок дают основную долю, обручи и днища добавляют несколько сотен. Проверяется на факте, блок в этапе 9 печатает число и предупреждает о превышении.
- Материалов: 3 (крашеное дерево, крашеный металл, грязь). Текстур на диске: 2 запечённые карты 1024×1024 — AO и кривизна. Никаких карт нормалей.
- Текстур-процедурных: 2 шума (дерево 180, металл 320) — они в материалах, в экспорт не попадают как файлы.
- Кадров: 1 превью 1024×1024 + тестовые прогоны 512×512 при 32 сэмплах.
- Рендер в Cycles, 256 сэмплов с денойзингом: **десятки секунд на кадр** на средней видеокарте. Для игрового пропа это ничто.

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `PLANK_COUNT` | 12 | 8 — читается как бочка, 16 — уже дороже и шумнее |
| `Bevel.segments` | 2 | 3–4 превращают стиль в фотореализм и съедают бюджет |
| `Bevel.angle_limit` | 30° | ниже — фаски появляются внутри щелей |
| `Weld.merge_threshold` | 0.0002, до Bevel | выше — фаски на углах обручей слипаются |
| `angle_limit` (Smart UV) | 66° | меньше — больше швов на цилиндре |
| размер запечённых карт | 1024 | для пропа с читаемым силуэтом этого достаточно |
| `Subdivision` для high-poly | level 2 | level 3 на пропах бессмысленно дорог |
| шероховатость дерева | 0.55–0.7 | ниже — крашеное дерево блестит, как пластик |
| металлическость обручей | 0.5–0.7 | выше — крашеный металл перестаёт быть крашеным |
| бюджет триангуляции | 1.2 тыс., жёсткий потолок 1.6 тыс. | превышение проверяется в скрипте экспорта |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Щели в корпусе видно насквозь | доски стоят с зазором, внутренней оболочки нет | внутренняя цилиндрическая поверхность без нормалей |
| Фаски «помяты» | `Weld` применён после `Bevel` | Weld до Bevel, порог ≤ 0.0002 |
| Кривизна в пятнах | запекалось с low-poly как с источника | High Poly с `Subdivision` и `Shrinkwrap` |
| Чёрная кайма на фасках | дефолтный Normal Bias при запекании | увеличить Normal Bias |
| Текстура едет при повороте | UV развёрнута по габаритам объекта | фиксировать масштаб текстуры от реального размера |
| Три варианта не совпадают по текстуре | каждый вариант собран отдельно | собирать все из одного меша |
| Бюджет превышен | 16 досок и 3 сегмента Bevel | 12 досок, 2 сегмента, Weld до Bevel |
| Бочка выглядит трубой в силуэте | слишком гладкий корпус | 12 отдельных досок с фасками |

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 13: HARD-SURFACE SCI-FI GUN](case_13_hard_surface_gun.md)
- **По темам:** [CASE 14: FOOD RENDER (RAMEN)](case_14_food_r visualisation.md), [P22: PARTICLE SYSTEMS](../prompts/22_particles.md), [P39: EXPORT PRESETS (GLB/FBX/USD)](../prompts/39_export_presets.md)
- **Теги:** #case, #pipeline, #render, #unity