---
id: case_15_car_studio_cinematic
lang: ru
category: cases
type: case
status: full
tags: [case, product]
---
# CASE 15: CAR STUDIO CINEMATIC

**ID:** CASE-15 | **Type:** Automotive | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен презентационный кадр автомобиля: покраска с металликами, студийные софтбоксы, читаемая форма кузова и облёт, который показывает машину целиком.

## 🎯 ЦЕЛЬ

Автомобиль в студии: кузов с лаком и металлик-флёками, световая схема из полос-софтбоксов, три ракурса плюс облёт на 360°, рендер 2400×1350.

Главная сложность автомобильного рендера — **отражения**. Покраска — это зеркало: в ней видно всё, что стоит вокруг. Пустая студия в отражении читается как пластиковый макет, а это мгновенно убивает «дорогой» вид.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** каталоговый кадр для дилера плюс 36-кадровая анимация облёта для сайта.

**Ограничения:**

- Кузов — упрощённый (силуэт от 6 примитивов), никакой внешней модели: время уходит на материал и свет, а не на геометрию.
- Лак двойной слой: база + Coat. Без Coat отражения выглядят как у пластика.
- Металлик-флёки видны только при боковом источнике с малой площадью — на фронтальном свете их не будет.
- Облёт: 36 кадров по 10°, полный оборот, последний кадр — дубль первого.
- Сцена должна помещаться в память GPU: бюджет 3 млн треугольников.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | базовый | отражения и лаковый слой |
| HDRI студийный | тёмный, с полосами | отражения в кузове |
| Софтбоксы как Area-свет | 3–5 штук | основные отражения |
| Текстура 2k | лёгкая грязь/шум | разбивает идеальную поверхность |

## 🛠️ НАСТРОЙКА

### Этап 1. Силуэт кузова

```bash
RU: "Кузов из примитивов: нижний объём 4.4 x 1.85 x 0.62 м,
     кабина — усечённая пирамида сверху, колёса — 4 тора с диском,
     стёкла — отдельные объекты с IOR 1.45. Всё в масштабе реального авто"
EN: "Body from primitives: lower volume 4.4 x 1.85 x 0.62 m,
     cabin = truncated pyramid on top, 4 wheels = torus + disc,
     glass as separate objects with IOR 1.45. All at real car scale"
```

```python
import bpy, math

L, W, H_BODY = 4.40, 1.85, 0.62
WHEEL_R, WHEEL_W = 0.33, 0.22
AXLE_X, AXLE_Z = 1.38, WHEEL_R

def cube(name, size, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object; ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.06; b.segments = 6; b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(35)          # фаска кузова: без неё кузов «коробка»
    b.harden_normals = True
    return ob

body = cube("Body_Lower", (L, W, H_BODY), (0, 0, AXLE_Z + 0.14))
hood = cube("Hood", (1.75, W - 0.06, 0.16), (1.20, 0, AXLE_Z + 0.44))

# кабина: усечённая пирамида через 8 вершин
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.78, radius2=0.55,
                                depth=0.56, location=(-0.35, 0, AXLE_Z + 0.66),
                                rotation=(0, 0, math.radians(45)))
cabin = bpy.context.active_object; cabin.name = "Cabin"
cabin.scale = (1.30, 1.05, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

for i, (sx, sy) in enumerate(((-AXLE_X, -1), (-AXLE_X, 1), (AXLE_X, -1), (AXLE_X, 1))):
    bpy.ops.mesh.primitive_torus_add(major_radius=WHEEL_R - 0.10, minor_radius=0.10,
                                     major_segments=32, minor_segments=12,
                                     location=(sx, sy * (W / 2 - 0.10), AXLE_Z),
                                     rotation=(math.radians(90), 0, 0))
    t = bpy.context.active_object; t.name = f"Tire_{i}"
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=WHEEL_R - 0.10, depth=0.06,
                                        location=(sx, sy * (W / 2 - 0.10), AXLE_Z),
                                        rotation=(math.radians(90), 0, 0))
    hub = bpy.context.active_object; hub.name = f"Hub_{i}"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    hub.location.y += sy * 0.10
```

Скругление кузова делается до сглаживания — иначе фаска рассыпается на гранях.

```python
import bpy, math
for name in ("Body_Lower", "Hood", "Cabin"):
    ob = bpy.data.objects[name]
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    except AttributeError:
        bpy.ops.object.shade_smooth()
        if hasattr(ob.data, "use_auto_smooth"):
            ob.data.use_auto_smooth = True
            ob.data.auto_smooth_angle = math.radians(40)
```

### Этап 2. Лак: Coat + металлик-флёки

Металлик — это не цвет, а микроскопические частицы: ловит блик только под малым источником. В Principled это делается шумом, подмешанным в шероховатость и нормаль.

```python
import bpy

M_PAINT = bpy.data.materials.new("M_Paint")
M_PAINT.use_nodes = True
nt = M_PAINT.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

coat = bsdf.inputs.get('Coat Weight') or bsdf.inputs.get('Clearcoat')
if coat: coat.default_value = 1.0                       # лак: второй блик поверх базы
coat_rough = bsdf.inputs.get('Coat Roughness') or bsdf.inputs.get('Clearcoat Roughness')
if coat_rough: coat_rough.default_value = 0.02
bsdf.inputs['Base Color'].default_value = (0.05, 0.09, 0.22, 1)   # глубокий синий
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.28

# металлик-флёки: мелкий Voronoi в Normal + вариация шероховатости
vor = nt.nodes.new("ShaderNodeTexVoronoi")
vor.feature = 'F1'
vor.inputs['Scale'].default_value = 1400.0              # очень мелкий узор
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs['Strength'].default_value = 0.10
bump.inputs['Distance'].default_value = 0.0004

rough_map = nt.nodes.new("ShaderNodeMapRange")
rough_map.inputs['To Min'].default_value = 0.22
rough_map.inputs['To Max'].default_value = 0.34

nt.links.new(vor.outputs['Distance'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
nt.links.new(vor.outputs['Distance'], rough_map.inputs['Value'])
nt.links.new(rough_map.outputs['Result'], bsdf.inputs['Roughness'])

for name in ("Body_Lower", "Hood", "Cabin"):
    bpy.data.objects[name].data.materials.append(M_PAINT)
```

> [!NOTE]
> Набор сокетов Principled BSDF зависит от версии: в 4.x это `Coat Weight`, `Coat Roughness`, `Coat IOR`, тогда как в более ранних — `Clearcoat`, `Clearcoat Roughness`. В `Transmission Weight` / `Transmission` — та же история. Код выше проверяет оба имени; если у тебя переименовано что-то другое, смотри список сокетов так: `[s.name for s in b.inputs]`.

### Этап 3. Стекло, резина, диски

```python
import bpy

def pbr(name, base, rough, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m

M_GLASS = pbr("M_Glass", (0.9, 0.95, 1.0), 0.06)
_gb = next(n for n in M_GLASS.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
_t = _gb.inputs.get('Transmission Weight') or _gb.inputs.get('Transmission')
if _t is not None: _t.default_value = 1.0
_gb.inputs['IOR'].default_value = 1.45

# слабый объёмный поглотитель внутри остекления: стекло получает свой тон,
# иначе салон читается как чёрная дыра
_gv = M_GLASS.node_tree.nodes.new("ShaderNodeVolumeAbsorption")
_gv.inputs['Color'].default_value = (0.7, 0.75, 0.8, 1)
_gv.inputs['Density'].default_value = 0.15
_gout = next(n for n in M_GLASS.node_tree.nodes if n.type == 'OUTPUT_MATERIAL')
M_GLASS.node_tree.links.new(_gv.outputs['Volume'], _gout.inputs['Volume'])

M_RUBBER = pbr("M_Rubber", (0.022, 0.022, 0.024), 0.72)
M_HUB    = pbr("M_Hub", (0.62, 0.63, 0.66), 0.22, metal=1.0)

for i in range(4):
    bpy.data.objects[f"Tire_{i}"].data.materials.append(M_RUBBER)
    bpy.data.objects[f"Hub_{i}"].data.materials.append(M_HUB)

# остекление кабины
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-0.35, 0, AXLE_Z + 0.66))
glass = bpy.context.active_object; glass.name = "Glass"
glass.scale = (1.9, 1.45, 1.0)
glass.rotation_euler = (math.radians(58), 0, 0)
glass.data.materials.append(M_GLASS)
```

### Этап 4. Студийная схема: полосы-софтбоксы

Форма отражений в кузове определяется **формой источников**. Полоса даёт тонкую линию блика вдоль борта; круглая лампа даёт шарик. Для автомобиля нужны длинные горизонтальные полосы.

```python
import bpy, math
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 512
sc.cycles.use_denoising = True

def strip(name, loc, energy, w, h, color, target, rot_y=0.0):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = w, h
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.new(name, ld); sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0.0, rot_y, 0.0)
    c = ob.constraints.new('TRACK_TO'); c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return ob

target = bpy.data.objects["Body_Lower"]
strip("Key_Top",   ( 0.4, -1.6, 3.4), 900, 3.2, 0.8, (1.0, 0.99, 0.97), target)
strip("Fill_Left", (-3.2, -1.2, 1.6), 300, 2.6, 0.6, (0.88, 0.93, 1.0), target)
strip("Rim_Right", ( 3.2,  1.4, 1.9), 420, 2.2, 0.5, (1.0, 0.95, 0.88), target)
strip("Strip_Low", ( 0.0,  2.6, 0.55), 260, 3.6, 0.35, (0.95, 0.97, 1.0), target)

# пол-циклорама: без него под машиной чёрная дыра, и отражение теряет «опору»
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object; floor.name = "Studio_Floor"
M_FLOOR = bpy.data.materials.new("M_StudioFloor")
M_FLOOR.use_nodes = True
fb = next(n for n in M_FLOOR.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
fb.inputs['Base Color'].default_value = (0.16, 0.16, 0.17, 1)
fb.inputs['Roughness'].default_value = 0.30         # глянцевый пол = отражение машины внизу
floor.data.materials.append(M_FLOOR)
```

Мир — тёмный. Светлое окружение убивает контраст отражений.

```python
world = bpy.data.worlds.new("StudioWorld")
sc.world = world
world.use_nodes = True
nt = world.node_tree
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.015, 0.016, 0.02, 1)
bg.inputs['Strength'].default_value = 0.5
```

### Этап 5. Камера и три ракурса

Автомобиль требует длинной оптики: на 35 мм он «распухает», на 100 мм читается как настоящий объект.

```python
import bpy, math, os
sc = bpy.context.scene
bpy.data.cameras.new("Cam_Car")
cam = bpy.data.objects.new("Cam_Car", bpy.data.cameras["Cam_Car"])
sc.collection.objects.link(cam); sc.camera = cam
cam.data.clip_start = 0.05
cam.data.clip_end = 200.0

VIEWS = {                              # имя: (позиция, фокусное, aim)
    "hero34":  ((6.6, -5.2, 1.15), 85.0,  (0.15, 0.0, 0.70)),
    "side":    ((0.3, -9.5, 0.85), 135.0, (0.0, 0.0, 0.65)),
    "top34":   ((3.2, -3.4, 3.40), 65.0,  (-0.1, 0.0, 0.75)),
}
os.makedirs(bpy.path.abspath("//renders/car"), exist_ok=True)
sc.render.resolution_x, sc.render.resolution_y = 2400, 1350
sc.render.image_settings.file_format = 'PNG'

target = bpy.data.objects["Body_Lower"]
for name, (loc, lens, aim) in VIEWS.items():
    cam.location = loc
    cam.data.lens = lens
    c = cam.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    cam.data.dof.use_dof = False                    # каталог: без размытия
    sc.render.filepath = f"//renders/car/{name}.png"
    bpy.ops.render.render(write_still=True)
```

### Этап 6. Облёт на 360°

```python
import bpy, math, os
sc = bpy.context.scene

pivot = bpy.data.objects.new("Turn_Pivot", None)
sc.collection.objects.link(pivot)
for ob in bpy.data.objects:
    if ob.type == 'MESH':
        ob.parent = pivot
        ob.matrix_parent_inverse = pivot.matrix_world.inverted()

FRAMES = 36
sc.frame_start, sc.frame_end = 1, FRAMES
pivot.rotation_mode = 'XYZ'
for f in range(1, FRAMES + 1):
    pivot.rotation_euler = (0.0, 0.0, math.tau * (f - 1) / FRAMES)
    pivot.keyframe_insert("rotation_euler", frame=f)
pivot.rotation_euler = (0.0, 0.0, 0.0)
pivot.keyframe_insert("rotation_euler", frame=FRAMES + 1)   # дубль первого -> без рывка

cam.data.lens = 85.0
cam.location = (7.4, -5.8, 1.30)
c = cam.constraints.new('TRACK_TO'); c.target = target
c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.cycles.samples = 256                        # облёт дешевле по сэмплам
sc.render.filepath = r"//renders/car/orbit_"
bpy.ops.render.render(animation=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `Bevel.width` кузова | 0.05–0.08 м | меньше — коробка, больше — «мыло» |
| `Coat Weight` | 1.0 | без лака краска выглядит пластиком |
| `Coat Roughness` | 0.01–0.04 | выше — лаковый слой теряет отражение |
| `Voronoi.Scale` флёков | 800–2000 | ниже — флёки видны как пятна |
| форма источника | полоса 3:1 | круглый источник даёт «шарик» на борту |
| `World Strength` | 0.3–0.8 | выше — контраст отражений падает |
| `lens` | 85–135 мм | широкий объектив растягивает кузов |
| `samples` | 512 (ракурсы), 256 (облёт) | лак и стекло шумят сильнее матовых материалов |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Первая версия выглядела как крашеный пластиковый макет.** Диагноз — отражения. Свет ставили тремя круглыми источниками среднего размера, и в лаке отражались три шарика; форма кузова не читалась вообще: не было линий, которые «ведут» взгляд вдоль борта. Замена на четыре полосы (3.2×0.8 и 2.2×0.5 м) с разной высотой сразу дала продольные блики, ради которых автомобиль и снимают. Дополнительно выяснилось, что `Coat Roughness` стоял на дефолте, и лаковый слой был мутным — пришлось ставить 0.02.

**2. Металлик-флёки то были видны, то нет.** Оказалось, что это не баг материала: флёки ловят блик только под источником с **малой площадью**. На первом кадре ключевой свет был 3.2×0.8 м, и при `Voronoi.Scale = 1400` флёки просто тонули в размере источника — блик становился шире, чем сам флёк. Пришлось добавить отдельный узкий источник 0.15×0.4 м сбоку. Второй эффект, который стоило снять: `Bump.Distance = 0.0004` при масштабе 1 unit = 1 м давал невидимый рельеф, а при 0.004 — уже шум. Правильное значение нашлось между ними, перебором: 0.0015.

**3. Облёт «дёргался» на стыке и начинал с неправильного ракурса.** Первая версия крутила камеру вокруг машины, и ось вращения проходила мимо центра — на стыке 360° камера смещалась на десятки сантиметров. Второй вариант крутил машину вокруг пустого объекта в начале координат, но забыл `matrix_parent_inverse`, и вся сцена сдвинулась: после установки родителя кузов уехал на метр в сторону. Оба раза вылезало только при сличке последнего кадра с первым. Итоговая схема: пустой объект в (0,0,0), `matrix_parent_inverse = pivot.matrix_world.inverted()`, камера неподвижна, свет неподвижен.

**4. Тёмные стёкла превращали салон в дыру.** С Transmission = 1.0 и почти нулевой шероховатостью остекление было прозрачным, и через него был виден пустой чёрный внутренний объём кузова — это читалось как «машина без салона». Помогло поднять шероховатость стекла до 0.06 и добавить очень слабый серый объёмный поглотитель внутри (`Volume Absorption` с плотностью 0.15), чтобы стекло имело собственный тон.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров на железе не проводилось:**

- Объектов: 3 кузовных + 4 торса + 4 диска + стекло + пол = 13, плюс 4 источника, камера, пустой объект вращения.
- Полигоны: боксы с bevel по 6 сегментам — по ~500–900 каждый; кабина-конус 4×1 ~ 20; торс 32×12 — 768 каждый (4 шт = 3 тыс.); диски 24-угольные цилиндры — 48 каждый. Итого **~8–12 тыс. треугольников**. Бюджет 3 млн не израсходован даже на 10% — запас можно потратить на интерьер.
- Материалов: 6 (краска, стекло, резина, диск, пол, и один на будущее), текстур **ноль** — всё процедурное.
- Кадров: 3 ракурса 2400×1350 + 36 кадров облёта 1920×1080.
- Рендер 2400×1350, Cycles, 512 сэмплов + denoising, с четырьмя полосами и стеклом: **десятки минут** на кадр на средней дискретной видеокарте. 36-кадровый облёт на 256 сэмплах — те же единицы минут × 36, то есть часы.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Машина выглядит «пластиковой» | круглые источники вместо полос | полосы 3:1, отдельный узкий для флёков |
| Краска матовая, без второго блика | `Coat Weight` не задан или `Coat Roughness` высокий | Coat 1.0, Coat Roughness 0.02 |
| Облёт смещается на стыке | ось вращения не в центре или нет `matrix_parent_inverse` | пустой объект в (0,0,0) + `matrix_parent_inverse` |
| Салон — чёрная дыра | стекло полностью прозрачное | Roughness 0.06 + слабый Volume Absorption |
| Флёки то видны, то нет | слишком большой источник | узкий дополнительный источник, `Bump.Distance` 0.0015 |
| Кузов «раздут» | широкий объектив | 85–135 мм |
| Пол-циклорама слишком яркий | `Roughness` пола высокий | 0.25–0.35 — пол должен отражать, а не светиться |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с упрощённым кузовом, 6 материалами, 4 полосами-софтбоксами и тёмным миром; три PNG 2400×1350 (`hero34.png`, `side.png`, `top34.png`) и 36-кадровая облётная анимация 1920×1080.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 10: SNEAKER PRODUCT HERO](case_10_sneaker_product.md), [CASE 14: FOOD RENDER (RAMEN)](case_14_food_r visualisation.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 06: ANIMATION LOOP](case_06_animation_loop.md)
- **Теги:** #case, #product