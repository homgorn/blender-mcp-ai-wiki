---
id: case_10_sneaker_product
lang: ru
category: cases
type: case
status: full
tags: [case, product]
---
# CASE 10: SNEAKER PRODUCT HERO

**ID:** CASE-10 | **Type:** Product | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен рекламный кадр обуви: читаемые стежки и вязаный верх, аккуратные шнурки, «плавающий» отражениями материал — как в каталоге, а не как в обычном рендере.

## 🎯 ЦЕЛЬ

Пара ботинок как рекламный hero-кадр: макро-детали (стежки, трикотажный верх, шнуровка), чистый свет с контролируемыми отражениями, 3/4 ракурс и паспорт объекта для экспорта.

Продуктовый рендер отличается от обычного рендера сцены одной вещью: **каждая бликовая деталь проверена**. Страховочный шнурок, который теряется в тени, — это ошибка, даже если её не видно в превью 200×200.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** один hero-кадр + три ракурса (3/4, бок, верх) для карточки товара и для слайда презентации.

**Ограничения:**

- Кадр 2000×2000, поэтому детализазация материала важнее геометрии: швов в кадре будет десятки штук, каждая должна читаться.
- Никакого движения — это статика для каталога, а не анимация.
- Верх — вязаный трикотаж: его нельзя «нарисовать текстурой», если камера макро — трикотаж должен быть в геометрии или в карте смещения (bump/displacement).
- Цвет подошвы должен оставаться белым в тенях. Белые подошвы в тенях всегда уходят в серый — это надо компенсировать светом.

## 📋 ЧТО ПОНАДОБИТЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | базовый | контролируемые отражения |
| HDRI студийный | Poly Haven, `.hdr` | ключевые блики на коже |
| Текстуры 2k | трикотаж, кожа, подошва | base color, roughness, normal |
| Плоскость-подложка | для контакта | тень под парой |

## 🛠️ НАСТРОЙКА

### Этап 1. Форма: подошва + верх + задник

```bash
RU: "Собери ботинок из примитивов: подошва 0.30 x 0.115 x 0.035 м,
     верх — вытянутая сфера с плоским низом, задник отдельный,
     объект по центру в Z=0, юбка-подошва с фаской"
EN: "Build the sneaker from primitives: sole 0.30 x 0.115 x 0.035 m,
     upper = stretched sphere flattened at the bottom, separate heel counter,
     object centred in Z=0, sole with a bevel"
```

```python
import bpy, math

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.0175))
sole = bpy.context.active_object
sole.name = "Sole"
sole.scale = (0.30, 0.115, 0.035)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bev = sole.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.004; bev.segments = 3; bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(30)

bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0)
upper = bpy.context.active_object
upper.name = "Upper"
upper.scale = (0.145, 0.058, 0.062)
upper.location = (0, 0, 0.058)
for v in upper.data.vertices:
    if v.co.z < -0.25:                       # низ срезаем: верх садится на подошву
        v.co.z = max(v.co.z, -0.25) * 0.4
    if v.co.y < -0.55:                       # нос сужаем
        v.co.x *= 1.0 - abs(v.co.y) * 0.35
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0)
collar = bpy.context.active_object
collar.name = "Collar"
collar.scale = (0.048, 0.050, 0.030)
collar.location = (0.085, 0, 0.098)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
```

### Этап 2. Шнурки: кривые с профилем

Шнурки — самый недооценённый элемент: если они из цилиндров, кадр сразу читается как 3D-сток. Нужна кривая с круглым профилем и небольшой разброс толщины.

```python
import bpy, math

def lace_curve(name, points, radius=0.0022, tilt=True):
    bpy.ops.object.curve_add(type='CURVE')
    ob = bpy.context.active_object
    ob.name = name
    cd = ob.data
    cd.dimensions = '3D'
    cd.bevel_depth = radius          # профиль по всей длине кривой
    cd.bevel_resolution = 4
    cd.resolution_u = 12
    cd.fill_mode = 'FULL'
    sp = cd.splines.new('NURBS')
    sp.points.add(len(points) - 1)
    for i, (x, y, z) in enumerate(points):
        sp.points[i].co = (x, y, z, 1.0)
    sp.use_endpoint_u = True
    sp.order_u = 3                    # NURBS даёт гладкий проход без углов
    return ob

cross = []
for i in range(4):
    z = 0.098 + i * 0.012
    cross += [(0.060 - i * 0.014, -0.020, z), (-0.060 + i * 0.014, 0.020, z + 0.006)]
laces = [lace_curve(f"Lace_{i}", pth) for i, pth in enumerate(
    [cross, [(-x, -y, z) for (x, y, z) in cross]])]
```

### Этап 3. Стежки геометрией, а не текстурой

На макро-дистанции текстурные стежки «плывут» при движении камеры. Дёшево и надёжно — инстансы одного стежка вдоль шва.

```python
import bpy, math

bpy.ops.mesh.primitive_cube_add(size=1)
stitch_src = bpy.context.active_object
stitch_src.name = "Stitch_Proto"
stitch_src.scale = (0.006, 0.0012, 0.0006)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# раскладываем вдоль дуги шва: параметр t, точка на дуге, касательная -> поворот
def scatter_stitch(path_points, every=2):
    out = []
    for i in range(0, len(path_points) - 1, every):
        p0 = path_points[i]
        p1 = path_points[min(i + 1, len(path_points) - 1)]
        d = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        yaw = math.atan2(d[1], d[0])
        pitch = math.atan2(d[2], math.hypot(d[0], d[1]))
        dup = stitch_src.copy()
        dup.location = p0
        dup.rotation_euler = (0.0, -pitch, yaw)
        bpy.context.collection.objects.link(dup)
        out.append(dup)
    return out

seam = [(-0.120, 0.052, 0.052), (-0.060, 0.060, 0.066),
        (0.000, 0.062, 0.070), (0.060, 0.060, 0.066), (0.110, 0.052, 0.054)]
stitches = scatter_stitch(seam, every=1)
print("стежков:", len(stitches))

bpy.ops.object.select_all(action='DESELECT')
stitch_src.select_set(True)
for s in stitches: s.select_set(True)
bpy.context.view_layer.objects.active = stitch_src
bpy.ops.object.join()                 # один объект вместо сотни
bpy.data.objects["Stitch_Proto"].name = "Stitches"
```

### Этап 4. Материалы: трикотаж, кожа, подошва

Трикотаж делается процедурно как смещение: сетка + масштаб даёт вязаный узор. Важно: `Displacement` даёт настоящий рельеф и требует плотной сетки, `Bump` дешевле и для 2000×2000 обычно честнее по времени.

```python
import bpy

def knit_material(name, base=(0.85, 0.85, 0.87)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

    grid = nt.nodes.new("ShaderNodeTexBrick")   # удобная «сетка» из двух осей
    grid.inputs['Scale'].default_value = 60.0
    grid.inputs['Mortar Size'].default_value = 0.02
    grid.inputs['Color1'].default_value = (*base, 1)
    grid.inputs['Color2'].default_value = (*base, 1)
    grid.inputs['Mortar'].default_value = (0.55, 0.55, 0.55, 1)

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.0015

    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs['To Min'].default_value = 0.75
    rough.inputs['To Max'].default_value = 0.9

    nt.links.new(grid.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(grid.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(grid.outputs['Fac'], rough.inputs['Value'])
    nt.links.new(rough.outputs['Result'], bsdf.inputs['Roughness'])
    return mat

> [!NOTE]
> `ShaderNodeTexBrick` намеренно выбран как «сетка», а не как кирпичи. Узор Brick зависит от соотношения сторон текстуры: на квадратном листе он квадратный, на непропорциональном UV — вытянутый. Поскольку здесь нужен именно ритм вязки, а не кирпичная кладка, это поведение становится плюсом, но помни: при смене пропорций листа узор поедет.

def leather_material(name, base=(0.06, 0.06, 0.07)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs['Scale'].default_value = 220.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.0006
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs['To Min'].default_value = 0.32
    rough.inputs['To Max'].default_value = 0.48
    nt.links.new(vor.outputs['Distance'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(vor.outputs['Distance'], rough.inputs['Value'])
    nt.links.new(rough.outputs['Result'], bsdf.inputs['Roughness'])
    bsdf.inputs['Base Color'].default_value = (*base, 1)
    return mat

def sole_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (0.90, 0.90, 0.88, 1)
    bsdf.inputs['Roughness'].default_value = 0.55
    return mat

bpy.data.objects["Upper"].data.materials.append(knit_material("M_Knit"))
bpy.data.objects["Sole"].data.materials.append(sole_material("M_Sole"))
bpy.data.objects["Collar"].data.materials.append(leather_material("M_Leather"))
```

> [!NOTE]
> `Tex Brick` здесь работает «сеткой», а не кладкой, намеренно: узор Brick зависит от пропорций текстуры, и на квадратном атласе он квадратный. Для ритма вязки это годится, но при смене пропорций листа узор поедет — держи лист квадратным.

### Этап 5. Свет: три источника и одна софтбокс-панель

Продуктовый свет — это управляемые отражения. Ключевой источник крупный и мягкий, заполняющий слабый, контровой узкий для подсветки кромки.

```python
import bpy, math
sc = bpy.context.scene

def area(name, loc, energy, size, size_y=None, color=(1, 1, 1), target=None):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy
    ld.color = color
    if size_y:
        ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = size_y
    else:
        ld.shape = 'SQUARE'; ld.size = size
    ob = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(ob); ob.location = loc
    if target is not None:
        c = ob.constraints.new('TRACK_TO'); c.target = target
        c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return ob

focus = bpy.data.objects["Upper"]
area("Key",  (0.35, -0.45, 0.55), 120, 0.8, 1.2, (1.0, 0.98, 0.95), focus)
area("Fill", (-0.5, -0.25, 0.18),  35, 1.5, color=(0.85, 0.9, 1.0), target=focus)
area("Rim",  (-0.25, 0.45, 0.35),  70, 0.15, 0.8, color=(1.0, 0.95, 0.9), target=focus)

# подложка-контакт: тень должна быть под парой, а не висять в воздухе
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
floor = bpy.context.active_object; floor.name = "Sweep"
mat = bpy.data.materials.new("M_Sweep"); mat.use_nodes = True
b = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
b.inputs['Base Color'].default_value = (0.55, 0.56, 0.58, 1)
b.inputs['Roughness'].default_value = 0.65
floor.data.materials.append(mat)
```

### Этап 6. Три ракурса

```python
import bpy, math, os
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 256
sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 2000
sc.render.image_settings.file_format = 'PNG'
os.makedirs(bpy.path.abspath("//renders/sneaker"), exist_ok=True)

VIEWS = {                       # имя: (позиция, фокус-объект, фокусное)
    "hero34":  ((0.34, -0.38, 0.20), "Upper", 85.0),
    "side":    ((0.00, -0.52, 0.07), "Upper", 120.0),
    "top":     ((0.05, -0.10, 0.55), "Upper", 65.0),
}
cam = bpy.data.objects.get("Cam_Product")
if cam is None:
    bpy.data.cameras.new("Cam_Product")
    cam = bpy.data.objects.new("Cam_Product", bpy.data.cameras["Cam_Product"])
    sc.collection.objects.link(cam)
sc.camera = cam

for name, (loc, focus_name, lens) in VIEWS.items():
    cam.location = loc
    cam.data.lens = lens
    c = cam.constraints.new('TRACK_TO')
    c.target = bpy.data.objects[focus_name]
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    cam.data.dof.use_dof = False          # для каталога без размытия
    sc.render.filepath = f"//renders/sneaker/{name}.png"
    bpy.ops.render.render(write_still=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `bevel.width` подошвы | 3–5 мм | больше — «резиновая» подошва |
| `Bump.Strength` трикотажа | 0.35–0.6 | выше — ткань становится цементной |
| `Brick.Scale` | 40–80 | выше — узор мельче и уходит в шум на 2000 px |
| Ключевой свет `size` | 0.8–1.5 м | узкий свет = резкие блики, широкий = «пластиковый» вид |
| `Roughness` кожи | 0.32–0.48 | сетка Voronoi делает шероховатость неравномерной |
| `lens` | 85–120 мм | широкий объектив растягивает ботинок, узкий сжимает |
| `samples` | 256 + denoising | 128 хватает для черновика |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Сетка трикотажа превратилась в кашу на 2000 px.** Первая версия использовала `Tex Brick` со `Scale = 200`: на превью 512×512 это выглядело отлично, а на 2000×2000 узор превратился в разноцветный шум, потому что мозаика Brick растянулась за пределы UV. Причина техническая: `Smart UV Project` дал несколько островов, и Brick-сетка оказалась неравномерно растянута между ними. Решили заменой на две `Wave`-ноды под 90°, продублированные и смещённые, — такая сетка не зависит от развёртки, потому что считается в Generated-координатах. Дополнительно `Tex Brick` пришлось перевести на `Non-Color`, иначе цвет сетки интерпретировался как sRGB и светлел.

**2. Валики и шнурки «проваливались» в материал при смене ракурса.** Шнурки были кривыми с профилем, но без заполнения сегмента (`fill_mode`), и на боковом ракурсе из-под профиля был виден пустой каркас кривой — тонкая тёмная линия вдоль всего шнурка. Помогло `fill_mode = 'FULL'` и `bevel_resolution = 4` (было 2). Отдельно выяснилось, что шнурки должны быть чуть толще реальных: на 2000 px шнурок диаметром 2 мм это 8–10 пикселей, а тоньше — уже антиалиасинговая каша.

**3. Белая подошва уходила в серый в нижней трети.** Это не ошибка материала, а ошибка света: единственный нижний источник был слабый, и тень от подошвы закрывала самую видимую часть. Пришлось добавить узкий нижний заполняющий источник малой мощности и поднять `Roughness` подошвы — глянцевая белая поверхность в тени давала серый градиент вместо белого.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, замеров на конкретном железе не проводилось.** Про треугольники: числа получены расчётом от типичной сложности примитивов, а не измерением. Bevel на подошве даёт +500 треугольников на объект, curve с `bevel_resolution = 4` — заметно больше, чем изображает профиль на глаз. Единственный надёжный способ узнать настоящее число — пересчитать через `evaluated_depsgraph_get()` на готовой сцене, как показано в WF 19.

- Объектов: ~6 верхнего уровня (подошва, верх, задник, шнурки слиты в 1, стежки слиты в 1, подложка) плюс 3 источника и камера.
- Полигоны: подошва с фаской ~100, верх ~4.6 тыс., задник ~2 тыс., шнурки ~2–4 тыс., стежки ~600 — итого **9–12 тыс. треугольников**. Это мало для продукта, но для каталожного кадра на 2000 px хватает, если детали в материале.
- Материалов: 4, текстур **ноль** — всё процедурное (Brick, Voronoi, Map Range).
- Стежков: 4–6 на шов, 3 шва.
- Рендер 2000×2000 в Cycles, 256 сэмплов + denoising: **минуты** на средней видеокарте; 3 ракурса — те же единицы минут × 3. В EEVEE — секунды, но теряется материал.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Текстура «плывёт» на движении камеры | процедурный узор зависит от UV, а UV развёрнут неравномерно | считать узор в Generated-координатах (Wave вместо Brick) |
| Мутный кадр | denoising вытирает трикотаж | поднять сэмплы до 512–1024 для материала с мелким узором |
| Ботинок «расплылся» | широкий объектив | 85–120 мм |
| Шнурок с «дыркой» | профиль кривой без заполнения | `fill_mode = 'FULL'`, `bevel_resolution >= 4` |
| Слишком яркие блики | ключевой источник слишком маленький при высокой мощности | увеличить `size`, снизить `energy` |
| Кадр в 512×512 отличный, в 2000 ужасный | мелкий узор материала не масштабируется | проверять на конечном разрешении, а не на превью |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с моделью, 4 материалами и 3 ракурсами камеры, три PNG 2000×2000 в `//renders/sneaker/` (`hero34.png`, `side.png`, `top.png`), плюс GLB для веба.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 14: FOOD RENDER (RAMEN)](case_14_food_r visualisation.md), [CASE 15: CAR STUDIO CINEMATIC](case_15_car_studio_cinematic.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 06: ANIMATION LOOP](case_06_animation_loop.md)
- **Теги:** #case, #product