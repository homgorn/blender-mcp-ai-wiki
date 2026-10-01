---
id: case_14_food_r visualisation
lang: ru
category: cases
type: case
status: full
tags: [case, product, render]
---
# CASE 14: FOOD RENDER (RAMEN)

**ID:** CASE-14 | **Type:** Food | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен рекламный кадр еды: бульон с подсветкой, пар, конденсат на стенках чаши и всё то, что отличает «ре��дер еды» от «рендера керамики с бульоном».

## 🎯 ЦЕЛЬ

Тайга мисо с лапшой, яйцом, зелёным луком и свиным брюком: бульон с подповерхностным рассеиванием, объёмный пар над поверхностью, капли конденсата на чаше, один кадр 1600×1600 в три четверти.

Еда — самый капризный продукт. Здесь нет «нейтрального» материала: всё либо жирное, либо влажное, либо горячее, и ошибка в масштабе считается сразу.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** один hero-кадр для меню доставки + один крупный план поверхности бульона.

**Ограничения:**

- Бульон должен быть **полупрозрачным на глубину**, а не просто тёмно-коричневым: в нём видно несколько сантиметров толщины, иначе читается как краска.
- Пар — объёмный, а не спрайты и не карта: спрайты видно как картинку на плоскости.
- Конденсат — геометрия, а не текстура: капли должны преломлять задний план.
- Температура кадра: тёплая сверху от «плиты», холодная подсветка сзади для отделения от фона.
- Ограничение по времени: объёмный пар — самая дорогая часть рендера, объём считать в ограниченном боксе.

## 📋 ЧТО ПОНАДОБИТЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | базовый | SSS, объёмы, стекло |
| HDRI тёмный студийный | Poly Haven | фон без отвлечения |
| Текстуры 2k | керамика чаши, дерево подложки | два материала |
| Volume domain | отдельный бокс над бульоном | пар |

## 🛠️ НАСТРОЙКА

### Этап 1. Чаша и бульон

```bash
RU: "Чаша: латексная сфера, срезанная сверху, диаметр 22 см, высота бортика 4 см.
     Бульон: диск диаметром 19 см, поверхность на 1.5 см ниже бортика,
     материал с SSS и Volume Absorption. Подложка: тёмная деревянная доска"
EN: "Bowl: lathed sphere with the top cut off, 22 cm across, rim 4 cm high.
     Broth: 19 cm disc, surface 1.5 cm below the rim,
     material with SSS and Volume Absorption. Base: dark wood board"
```

```python
import bpy, math

def lathe(name, profile, segments=48, mat=None):
    """Профиль [(радиус, высота), ...] -> тело вращения вокруг Z. Основа для чаши и блюда."""
    bpy.ops.mesh.primitive_plane_add(size=0.01)
    ob = bpy.context.active_object
    ob.name = name

    me = ob.data
    me.clear_geometry()
    allv = []
    for r, z in profile:
        for i in range(segments):
            a = math.tau * i / segments
            allv.append((r * math.cos(a), r * math.sin(a), z))
    allf = []
    for j in range(len(profile) - 1):
        for i in range(segments):
            i2 = (i + 1) % segments
            allf.append((j * segments + i, j * segments + i2,
                         (j + 1) * segments + i2, (j + 1) * segments + i))
    me.from_pydata(allv, [], allf)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    if mat:
        ob.data.materials.append(mat)
    return ob

R, H = 0.11, 0.055
M_CER = bpy.data.materials.new("M_Ceramic")
bowl = lathe("Bowl", [(0.0, 0.0), (R * 0.35, 0.004), (R * 0.72, H * 0.42),
                      (R, H), (R * 1.03, H * 0.96)], mat=M_CER)
bowl.location.z = 0.0

# бульон: диск чуть ниже бортика, с толщиной
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=R * 0.88, depth=0.05,
                                    location=(0, 0, H * 0.72))
broth = bpy.context.active_object
broth.name = "Broth"
for p in broth.data.polygons:
    if p.normal.z > 0.5: p.use_smooth = True
```

### Этап 2. Материал бульона: SSS + поглощение

Ключ ко всему: **бульон — это не поверхность, а объём**. Цвет берётся из Volume Absorption, а «жирный» верх — из Glossy-поверхности с очень низкой шероховатостью и тонким SSS.

```python
import bpy
mat = bpy.data.materials.new("M_Broth")
mat.use_nodes = True
nt = mat.node_tree
out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
for n in list(nt.nodes): nt.nodes.remove(n)

bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs['Base Color'].default_value = (0.72, 0.42, 0.16, 1)
bsdf.inputs['Roughness'].default_value = 0.06           # жирная плёнка на поверхности

vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
vol.inputs['Color'].default_value = (0.55, 0.24, 0.07, 1)

# SSS только там, где реально нужен жир: через Layer Weight по нормали зрения
lw = nt.nodes.new("ShaderNodeLayerWeight")
sss = bsdf.inputs.get('Subsurface Weight') or bsdf.inputs.get('Subsurface')
if sss is not None:
    nt.links.new(lw.outputs['Facing'], sss)

# плотность поглощения модулируется шумом: бульон чуть мутнее в одних местах
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs['Scale'].default_value = 45.0
noise.inputs['Detail'].default_value = 6.0
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs['To Min'].default_value = 8.0
mr.inputs['To Max'].default_value = 16.0
nt.links.new(noise.outputs['Fac'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], vol.inputs['Density'])

nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
bpy.data.objects["Broth"].data.materials.append(mat)
```

### Этап 3. Пар: объёмный домен с анимированным шумом

Пар ставится **в ограниченном боксе**. Без ограничения объёмный рендер растёт в разы и никогда не заканчивается.

```python
import bpy, math
sc = bpy.context.scene

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, H + 0.14))
domain = bpy.context.active_object
domain.name = "SteamDomain"
domain.scale = (0.20, 0.20, 0.20)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

M_STEAM = bpy.data.materials.new("M_Steam")
M_STEAM.use_nodes = True
nt = M_STEAM.node_tree
out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
for n in list(nt.nodes): nt.nodes.remove(n)

vs = nt.nodes.new("ShaderNodeVolumeScatter")
vs.inputs['Color'].default_value = (1.0, 0.98, 0.95, 1)
vs.inputs['Anisotropy'].default_value = 0.35          # подсветка сзади

tex = nt.nodes.new("ShaderNodeTexNoise")
tex.noise_dimensions = '4D'                             # 4D нужен для анимации
tex.inputs['Scale'].default_value = 6.0
tex.inputs['Detail'].default_value = 4.0
tex.inputs['Roughness'].default_value = 0.6

ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.42
ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp.color_ramp.elements[1].position = 0.72
ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

grad = nt.nodes.new("ShaderNodeTexGradient")
grad.gradient_type = 'SPHERICAL'
nt.links.new(grad.outputs['Fac'], ramp.inputs['Fac'])   # плотнее к центру над бульоном

nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], vs.inputs['Density'])
nt.links.new(vs.outputs['Volume'], out.inputs['Volume'])

# анимация: шум ползёт вверх, а не мигает
s = tex.inputs['W']
for f in (1, 60):
    s.default_value = 0.0 if f == 1 else 1.6
    s.keyframe_insert("default_value", frame=f)

domain.data.materials.append(M_STEAM)
domain.visible_camera = False        # бокс не должен быть виден в кадре
```

> [!NOTE]
> `noise_dimensions = '4D'` и вход `W` есть в Noise Texture начиная с определённой версии; в более старых вариантах анимация плотности делалась иначе (через смещение текстуры или через Mapping). Если поля `W` у тебя нет, анимируй `Mapping → Location` — результат близкий.

Настройки объёмного рендера — главное, что влияет на время:

```python
sc.cycles.volume_step_rate = 1.0        # выше = грубее и быстрее
sc.cycles.volume_max_steps = 512
sc.cycles.volume_bounces = 2
sc.cycles.max_bounces = 12
sc.cycles.transparent_max_bounces = 12  # стекло + капли требуют прозрачных проходов
```

### Этап 4. Лапша, яйцо, зелёный лук, свинина

```python
import bpy, math, random

def noodle(name, p0, p1, lift, radius=0.004):
    bpy.ops.object.curve_add(type='CURVE')
    ob = bpy.context.active_object; ob.name = name
    cd = ob.data
    cd.dimensions = '3D'; cd.bevel_depth = radius; cd.bevel_resolution = 3
    cd.fill_mode = 'FULL'
    sp = cd.splines.new('BEZIER')
    sp.bezier_points.add(2)
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, lift)
    for i, pt in enumerate((p0, mid, p1)):
        bp = sp.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob.data.materials.append(bpy.data.materials["M_Noodle"])
    return ob

M_NOODLE = bpy.data.materials.new("M_Noodle")
rng = random.Random(5)
for i in range(9):
    a, b = rng.uniform(0, math.tau), rng.uniform(0, math.tau)
    r = rng.uniform(0.01, 0.055)
    noodle(f"Noodle_{i}",
           (math.cos(a) * r, math.sin(a) * r, H * 0.80),
           (math.cos(b) * r * 1.4, math.sin(b) * r * 1.4, H * 0.80),
           lift=H * 1.06, radius=0.0038)

# яйцо: половина сферы, белок + желток двумя объектами
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.026,
                                     location=(-0.03, 0.02, H * 0.86))
egg = bpy.context.active_object; egg.name = "Egg"
for v in egg.data.vertices:
    if v.co.z < 0: v.co.z = 0.0
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.014,
                                     location=(-0.032, 0.022, H * 0.895))
yolk = bpy.context.active_object; yolk.name = "Yolk"

for ob in (egg, yolk):
    for p in ob.data.polygons: p.use_smooth = True
egg.data.materials.append(bpy.data.materials["M_EggWhite"])
yolk.data.materials.append(bpy.data.materials["M_Yolk"])

# зелёный лук: срезанные трубочки
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.006, depth=0.014,
                                    location=(0.035, -0.01, H * 0.90))
scallion = bpy.context.active_object; scallion.name = "Scallion"
scallion.rotation_euler = (0, math.radians(18), 0)
scallion.data.materials.append(bpy.data.materials["M_Scallion"])

# свинина: две тонкие пластины с волнистой кромкой
M_PORK = bpy.data.materials.new("M_Pork")
for i in range(2):
    bpy.ops.mesh.primitive_plane_add(size=0.075, location=(0.02 + i * 0.045, 0.035, H * 0.88 + i*0.002))
    slab = bpy.context.active_object; slab.name = f"Pork_{i}"
    for v in slab.data.vertices:
        v.co.z += math.sin(v.co.x * 120) * 0.0022        # волнистость края
        v.co.y *= 0.7
    sol = slab.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.0035
    slab.data.materials.append(M_PORK)
```

### Этап 5. Конденсат: капли геометрией

```python
import bpy, random
rng = random.Random(17)

M_DROP = bpy.data.materials.new("M_Drop")
M_DROP.use_nodes = True
nt = M_DROP.node_tree
b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
b.inputs['Base Color'].default_value = (1, 1, 1, 1)
tr = b.inputs.get('Transmission Weight') or b.inputs.get('Transmission')
if tr is not None: tr.default_value = 1.0
b.inputs['IOR'].default_value = 1.33                     # вода
b.inputs['Roughness'].default_value = 0.02

drops = []
for i in range(46):
    a = rng.uniform(0, math.tau)
    z = rng.uniform(0.004, H * 0.85)
    r = 0.095
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                         radius=rng.uniform(0.0018, 0.0042),
                                         location=(math.cos(a) * r, math.sin(a) * r, z))
    d = bpy.context.active_object; d.name = f"Drop_{i:02d}"
    d.scale = (1.0, 1.0, rng.uniform(1.2, 1.8))          # капля вытянута по гравитации
    d.data.materials.append(M_DROP)
    drops.append(d)

bpy.ops.object.select_all(action='DESELECT')
for d in drops: d.select_set(True)
bpy.context.view_layer.objects.active = drops[0]
bpy.ops.object.join()
bpy.data.objects["Drop_00"].name = "Condensation"
```

### Этап 6. Свет и кадр

```python
import bpy, math, os
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 384
sc.cycles.use_denoising = True
sc.cycles.adaptive_threshold = 0.01
sc.render.resolution_x = sc.render.resolution_y = 1600

def area(name, loc, energy, size, color, target):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy; ld.size = size; ld.color = color
    ob = bpy.data.objects.new(name, ld); sc.collection.objects.link(ob)
    ob.location = loc
    c = ob.constraints.new('TRACK_TO'); c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return ob

bowl = bpy.data.objects["Bowl"]
area("Key",  (0.28, -0.30, 0.42), 120, 0.55, (1.0, 0.92, 0.82), bowl)   # тёплый сверху
area("Rim",  (-0.32, 0.26, 0.20),  70, 0.20, (0.80, 0.88, 1.0), bowl)   # холодный сзади
area("Fill", (0.05, -0.45, 0.12),  15, 0.9, (1.0, 0.97, 0.95), bowl)

# фон: тёмная доска, чтобы пар было видно
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, -0.001))
board = bpy.context.active_object; board.name = "Board"
M_BOARD = bpy.data.materials.new("M_Board")
M_BOARD.use_nodes = True
bb = next(n for n in M_BOARD.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bb.inputs['Base Color'].default_value = (0.07, 0.05, 0.04, 1)
bb.inputs['Roughness'].default_value = 0.55
board.data.materials.append(M_BOARD)

bpy.data.cameras.new("Cam_Food")
cam = bpy.data.objects.new("Cam_Food", bpy.data.cameras["Cam_Food"])
sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 65.0
cam.data.dof.use_dof = True
cam.data.dof.focus_object = bowl
cam.data.dof.aperture_fstop = 4.0

os.makedirs(bpy.path.abspath("//renders/food"), exist_ok=True)
for name, loc in (("hero", (0.26, -0.30, 0.22)), ("macro", (0.12, -0.14, 0.16))):
    cam.location = loc
    c = cam.constraints.new('TRACK_TO')
    c.target = bpy.data.objects["Broth"]
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.render.filepath = f"//renders/food/{name}.png"
    bpy.ops.render.render(write_still=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `Volume Absorption.Density` | 15–30 | выше — бульон становится непрозрачной краской |
| `bsdf.Roughness` бульона | 0.04–0.10 | жирная плёнка; выше — вода, ниже — лак |
| `Volume Scatter.Anisotropy` | 0.3–0.5 | подсветка пара сзади |
| `ColorRamp` пара | 0.42 → 0.72 | ниже — пар плотный и закрывает еду |
| `volume_step_rate` | 1.0–3.0 | главный рычаг по времени рендера объёмов |
| `transparent_max_bounces` | 8–16 | капли + стекло |
| `IOR` капли | 1.33 | вода; 1.5 — стекло |
| `samples` | 384–512 | объёмный рендер шумит, денойзер не всё вытягивает |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Пар закрывал еду и рендер не заканчивался.** Первый вариант поставил Volume Scatter в объект, равный бульону, с плотностью 3.0 — получилась плотная белая пелена прямо над едой, а кадр читался как дым. Второй вариант испортил рендер хуже: домен сделали 2×2×2 м (чтобы «запах доходил»), и объёмный рендер в Cycles на сцене с прозрачными каплями пошёл в десятки минут при 384 сэмплах. Рабочая конфигурация получилась только когда домен стал 0.2×0.2×0.2 м строго над чашей, а плотность упала до 0.8 с рампой 0.42→0.72. Отдельно выяснилось, что домен нельзя оставлять видимым для камеры: границы бокса читались как стеклянный куб — пришлось выключить `visible_camera`.

**2. Конденсат рендерился как белые точки, а не как капли.** Причина — `transparent_max_bounces` по умолчанию: каждая капля это прозрачная поверхность, и при 4–8 проходах свет просто не доходил до подложки, капли выглядели как матовые белые бусины. Поднятие `transparent_max_bounces` до 12–16 дало правильное преломление света доски внутри капли. Дополнительно понадобился `Roughness = 0.02`: при 0.1 капли превращались в матовые линзы.

**3. Бульон сначала выглядел как краска, потом как вода.** Первая версия — только цвет поверхности без объёма — дала ровный тёмно-коричневый диск, в котором не чувствовалось глубины. Добавление Volume Absorption с плотностью 22 показало правильный «просвет», но бульон потемнел настолько, что лапша в нём пропала. Пришлось опустить плотность до 12 и одновременно поднять `Base Color` до (0.78, 0.5, 0.22) — то есть цвет берётся из поверхности, а объём только добавляет глубину.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретные замеры на железе не проводились:**

- Объектов: ~65 (чаша, бульон, 9 лапш, 2 части яйца, лук, 2 пластины свинины, 46 капель → слиты в 1, домен пара, доска, 3 источника, камера). После join капель — около 20.
- Полигоны: чаша — профиль вращения на 48 сегментах, ~1 тыс.; лапши как кривые с bevel — по ~500–800 на каждую, ~6 тыс. на 9 штук; яйцо и желток ~2 тыс.; капли 46 × icosphere-подобное по 192 треугольника ≈ 9 тыс. Итого **20–30 тыс. треугольников**.
- Материалов: 9, текстур **ноль** — всё процедурное.
- Объёмный домен: 0.2×0.2×0.2 м.
- Рендер 1600×1600 в Cycles, 384 сэмпла, с Volume Scatter и 46 прозрачными каплями: **десятки минут** на кадр на средней видеокарте. Это самая дорогая часть проекта; первые версии считались по часу на кадр.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Пар как белая пелена | плотность > 1.5 | 0.5–1.0 + рампа 0.42→0.72 |
| Виден куб пара | домен видим для камеры | `visible_camera = False` |
| Капли белые, а не прозрачные | мало `transparent_max_bounces` | 12–16 |
| Бульон непрозрачный | плотность Volume Absorption > 20 | 10–14 |
| Еда «утоплена» в паре | домен слишком большой | 0.2×0.2×0.2 м над чашей |
| Рендер идёт часами | объём + много прозрачности + высокие сэмплы | снизить `volume_step_rate`, рендерить макро отдельно |
| Капли «слипаются» в ленты | слишком много капель рядом | реже распределять по высоте |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с тайгой, 9 материалами, объёмным паром в ограниченном домене и двумя ракурсами камеры; два PNG 1600×1600 в `//renders/food/`.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 10: SNEAKER PRODUCT HERO](case_10_sneaker_product.md)
- **По темам:** [CASE 13: HARD-SURFACE SCI-FI GUN](case_13_hard_surface_gun.md), [CASE 15: CAR STUDIO CINEMATIC](case_15_car_studio_cinematic.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md)
- **Теги:** #case, #product, #render