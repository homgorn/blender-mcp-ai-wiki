---
id: case_13_hard_surface_gun
lang: ru
category: cases
type: case
status: full
tags: [case, modeling, render]
---
# CASE 13: HARD-SURFACE SCI-FI GUN

**ID:** CASE-13 | **Type:** Hardsurface | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

---

> Когда применять: когда нужно показать hard-surface модель в 3/4 ракурсе: форма собирается из прямых и фасок, читаемость держится на бликах по рёбрам и на износе по кромкам, а не на текстуре.

## 🎯 ЦЕЛЬ

Собрать стилизованный sci-fi «ствол» из примитивов: корпус, кожух ствола, магазинный отсек, скоба, рукоять, рельса прицела. Довести до чистых фасок по весам, запечь нормали с разрешения с высокополигонной копии, собрать PBR-материал с износом по кривизне и выгрузить с LOD-цепочкой 8k → 3k → 800.

Принцип, ради которого существует вся эта работа: **hard-surface читается фасками**. Не формой и не текстурой — фаской. Кромка шириной 2 мм на корпусе даёт линию света вдоль всего силуэта, и по этой линии зритель читает объём. Убрать фаску — значит убить читаемость, оставив серую коробку.

Второй принцип — **износ только по геометрии**. Потёртости берутся из кривизны (pointiness), а не рисуются в текстуре. Тогда износ сам переезжает на новую форму: поставил фаску — по ней пошла потёртость, и ни одна карта не поехала.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** hero-рендер 2048×2048 в 3/4 ракурсе плюс трим-вид, LOD-цепочка для движка.

**Ограничения:**

- Бюджет hero-версии: 8–12 тыс. треугольников. Hard-surface с множеством фасок на этом бюджете — уже тесно.
- Каждый boolean-вырез должен быть устойчивым: невыпуклые формы после вычитания дают невалидную топологию.
- Все фаски — через веса, а не через `Angle Limit`: одинаковый угол даёт одинаковую фаску и на рёбрах, и внутри вырезов, где она не нужна.
- Нормали запекаются один раз с высокополигонной копии; второй раз — только после смены формы.
- Три материала максимум: gunmetal, grip polymer, emissive accent.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | актуальный | примитивы, boolean, веса |
| Cycles | встроенный | запекание нормалей, pointiness |
| HDRI студийный | Poly Haven 2k | блики на фасках |
| Знание pointiness | — | износ по кривизне, без текстур |

## 🛠️ НАСТРОЙКА

### Этап 1. Блокаут примитивами

```python
import bpy, math

def box(name, size, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return ob

def cyl(name, r, depth, loc, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                        location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.shade_smooth()
    return ob

# Габарит: длина ~0.62 м, это и есть то, что потом уходит в движок как масштаб
body   = box("Body",       (0.30, 0.055, 0.085), (0.0,  0.0,   0.0))
shroud  = cyl("Shroud",    0.028, 0.34,          (0.16, 0.0,   0.005), (0, math.pi/2, 0))
magwell = box("MagWell",   (0.085, 0.040, 0.115), (0.02, 0.0, -0.075), (0, math.radians(-12), 0))
grip    = box("Grip",      (0.055, 0.038, 0.135), (-0.10, 0.0, -0.075), (0, math.radians(18), 0))
rail    = box("Rail",      (0.22, 0.030, 0.012), (-0.01, 0.0,  0.055))

# Скоба: рамка из четырёх боксов, склеенных в одну геометрию перед boolean
guard = bpy.data.objects.new("Guard", None)
parts = []
for size, loc in (
    ((0.010, 0.012, 0.010), (-0.075, 0.0, -0.020)),
    ((0.010, 0.012, 0.050), (-0.070, 0.0, -0.048)),
    ((0.048, 0.012, 0.010), (-0.050, 0.0, -0.068)),
):
    parts.append(box(f"_guard_{len(parts)}", size, loc))
bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
guard = bpy.context.active_object
```

### Этап 2. Boolean-вырезы

```python
import bpy

def cut(target, cutter, op='DIFFERENCE'):
    """Boolean применяется сразу, а не копится в стеке модификаторов:
    незавершённый boolean пересчитывается при каждой правке и молча
    меняет вершины, на которых уже стоят веса фасок."""
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target

    m = target.modifiers.new("Bool", 'BOOLEAN')
    m.operation = op
    m.object = cutter
    m.solver = 'EXACT'          # FAST даёт дыры на невыпуклых вырезах
    m.use_self = False
    bpy.ops.object.modifier_apply(modifier=m.name)

    bpy.data.objects.remove(cutter, do_unlink=True)   # инструмент удаляем сразу

def make_cutter(name, size, loc):
    c = box(name, size, loc)
    bpy.ops.object.shade_flat()
    return c

cut(rail, make_cutter("cut_rail", (0.20, 0.020, 0.020), (-0.01, 0.0, 0.062)))   # канавка рельса
cut(body, make_cutter("cut_grip",  (0.070, 0.070, 0.060), (-0.10, 0.0, -0.050))) # посадка рукояти
```

### Этап 3. Веса фасок

Фаски размечаются вручную: рёбра внешних кромок выделяются и получают вес 1.0, остальные остаются с весом 0. Визуально Ctrl+E мгновенно даёт именно то, что нужно, — берём рёбра, которые должны фаситься, и снимаем выделение с остальных.

Скриптом ставится сам Bevel и заполняются веса там, где разметка сделана вручную:

```python
import bpy

def apply_manual_bevel_weights(obj, default=0.0, width=0.0025, segments=2):
    """Веса на рёбрах лежат в generic attribute. Имя атрибута менялось
    между версиями Blender: ищи существующий, иначе создай свой."""
    me = obj.data
    name = None
    for candidate in ("bevel_weight_edge", "bevel_weight"):
        if me.attributes.get(candidate):
            name = candidate
            break
    if name is None:
        name = "bevel_weight_edge"
        me.attributes.new(name, 'FLOAT', 'EDGE')
        for i in range(len(me.edges)):
            me.attributes[name].data[i].value = default

    b = obj.modifiers.new("Bevel", 'BEVEL')
    b.limit_method = 'WEIGHT'          # не ANGLE: одинаковая фаска там, где есть вес
    b.width = width
    b.segments = segments
    b.harden_normals = True            # фаска остаётся плоской, а не замыливается
    b.miter_outer = 'MITER_ARC'
    b.use_clamp_overlap = True         # без него фаска self-intersect на узких рёбрах
    return obj

apply_manual_bevel_weights(bpy.data.objects["Body"], width=0.0025, segments=2)
```

> [!NOTE]
> Почему веса расставляются вручную, а не скриптом: **`bpy.types.MeshEdge` не
> отдаёт угол между гранями**. Это умеет только `bmesh` (`BMEdge.calc_face_angle()`),
> и пересчёт всех рёбер через bmesh на меше в десятки тысяч граней ощутимо медленный.
> Если всё же нужен автомат — пересчитывай рёбра через bmesh и пиши веса в
> атрибут оттуда, но держи в голове, что критерий «угол больше порога» отсекает
> ровно те внутренние острые рёбра вырезов, которые фасить не нужно.
> Имя атрибута весов и поле `Limit Method = Weight Weights` в самом Bevel
> проверяй в своей версии: там же в панели модификатора видно, какое имя
> атрибута Blender ищет.

### Этап 4. Вес и складка: чистые нормали

```python
import bpy

for name in ("Body", "Shroud", "MagWell", "Grip", "Rail"):
    ob = bpy.data.objects.get(name)
    if not ob:
        continue
    for p in ob.data.polygons:
        p.use_smooth = True          # гладкость, чтобы Weighted Normal работал

    wn = ob.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
    wn.keep_sharp = True
    wn.weight = 50
    wn.mode = 'FACE_AREA'           # крупные грани приоритетнее мелких фасок
```

> [!NOTE]
> `Weighted Normal` требует, чтобы меш был гладким, а в версиях до 4.1 — ещё и
> включённый Auto Smooth на меше. В 4.1 этот флаг убрали, и его роль выполняет
> модификатор *Smooth by Angle*. Если Weighted Normal «не работает» — проверь
> в своей версии, что именно включено: сглаживание по углу, заданное
> глобально, конфликтует с модификатором и результат выглядит как случайный.

### Этап 5. Материал с износом по кривизне

```python
import bpy

def hard_surface_material(name, base, metallic, roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*base, 1.0)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = roughness

    # Pointiness — геометрическая кривизна в Cycles. Главный инструмент
    # износа в hard-surface: он сам переезжает на новую форму, в отличие
    # от нарисованной текстуры. Но он реагирует на ОСТРЫЕ УГЛЫ, а не на
    # близость к краю, поэтому рейндж узкий.
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mask = nt.nodes.new("ShaderNodeValToRGB")
    mask.color_ramp.elements[0].position = 0.52   # ровные плоскости -> без износа
    mask.color_ramp.elements[1].position = 0.60   # кромки -> износ
    nt.links.new(geo.outputs['Pointiness'], mask.inputs['Fac'])

    worn = tuple(min(c * 2.2 + 0.18, 1.0) for c in base)

    # Цвет: износ светлее исходного металла
    mix_col = nt.nodes.new("ShaderNodeMixRGB")
    mix_col.blend_type = 'MIX'
    mix_col.inputs['Color1'].default_value = (*base, 1.0)
    mix_col.inputs['Color2'].default_value = (*worn, 1.0)
    nt.links.new(mask.outputs['Color'], mix_col.inputs['Fac'])
    nt.links.new(mix_col.outputs['Color'], b.inputs['Base Color'])

    # Шероховатость: на кромке ниже — полированный, отполированный металл.
    # Цвет в Roughness попадает как среднее по каналам, поэтому рейндж
    # задаётся чёрно-белым, а не цветным.
    rough_ramp = nt.nodes.new("ShaderNodeValToRGB")
    rough_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)  # без износа
    rough_ramp.color_ramp.elements[1].color = (
        max(1.0 - 0.28 / max(roughness, 0.05), 0.0),) * 3 + (1.0,)
    nt.links.new(mask.outputs['Color'], rough_ramp.inputs['Fac'])
    nt.links.new(rough_ramp.outputs['Color'], b.inputs['Roughness'])
    return m

M_GUNMETAL = hard_surface_material("M_Gunmetal", (0.055, 0.058, 0.062), 0.95, 0.34)
M_GRIP     = hard_surface_material("M_GripPoly", (0.022, 0.022, 0.024), 0.0,  0.62)

for name in ("Body", "Shroud", "MagWell", "Rail"):
    ob = bpy.data.objects.get(name)
    if ob:
        ob.data.materials.clear()
        ob.data.materials.append(M_GUNMETAL)

grip = bpy.data.objects.get("Grip")
if grip:
    grip.data.materials.clear()
    grip.data.materials.append(M_GRIP)
```

### Этап 6. High poly и запекание нормалей

```python
import bpy

body = bpy.data.objects["Body"]
high = body.copy()
high.data = body.data.copy()
high.name = "Body_HighPoly"
bpy.context.scene.collection.objects.link(high)

bevel = high.modifiers.new("Bevel", 'BEVEL')
bevel.width = 0.0025
bevel.segments = 6        # high-poly фаска гладкая — из неё и берётся нормаль
bevel.limit_method = 'WEIGHT'

sub = high.modifiers.new("Subdivision", 'SUBSURF')
sub.levels = 2
sub.render_levels = 2

img = bpy.data.images.new("Normal_4k", width=4096, height=4096)
img.filepath_raw = "//textures/body_normal.png"
img.file_format = 'PNG'

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
high.select_set(True)                     # high остаётся выделен как источник
bpy.context.view_layer.objects.active = body

bpy.context.scene.render.engine = 'CYCLES'
bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', use_selected_to_active=True)
img.save()
```

> [!NOTE]
> Cage и margin запекания нормалей с разрешения в интерфейсе настраиваются
> ползунками (Ray Distance, Cage Extrapolation, Cage Size) и зависят от
> расстояния между low и high. Значения по умолчанию рассчитаны на близкие
> копии; если копия «раздута» Subdivision'ом, её надо либо приблизить, либо
> уменьшить Ray Distance. Симптомы неверных настроек известны и легко
> узнаваемы: чёрные каймы на фасках, «шум» в углублениях, вывернутые фаски.

### Этап 7. LOD-цепочка

```python
import bpy

def build_lod(src, name, target_tris):
    """Decimate по доле считается вслепую, поэтому ориентируемся на
    результат: подбираем долю итеративно под целевой три-каунт."""
    lod = src.copy()
    lod.data = src.data.copy()
    lod.name = name
    bpy.context.scene.collection.objects.link(lod)

    ratio, tris = 1.0, None
    for _ in range(12):
        mod = lod.modifiers.new("Decimate", 'DECIMATE')
        mod.ratio = ratio
        bpy.ops.object.select_all(action='DESELECT')
        lod.select_set(True)
        bpy.context.view_layer.objects.active = lod
        bpy.ops.object.modifier_apply(modifier=mod.name)

        lod.data.calc_loop_triangles()
        tris = len(lod.data.loop_triangles)
        if tris <= target_tris * 1.1:
            break
        ratio *= max(target_tris / max(tris, 1), 0.35)
    print(f"{name}: {tris} tris (ratio {ratio:.3f})")
    return lod, tris

chain = [build_lod(body, "Body_LOD1", 3000), build_lod(body, "Body_LOD2", 800)]
```

### Этап 8. Рендер

```python
import bpy, math, os

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 512
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.005
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8            # металл требует отражений; меньше — грязь

# HDRI как единственный источник: на металле отражения важнее света
world = bpy.data.worlds.new("StudioWorld")
sc.world = world
world.use_nodes = True
nt = world.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
env_path = "//hdri/studio_small_09_1k.hdr"
try:
    env.image = bpy.data.images.load(env_path, check_existing=True)
    nt.links.new(env.outputs['Color'], bg.inputs['Color'])
except RuntimeError:
    pass                                # без HDRI остаётся ровный серый фон
bg.inputs['Strength'].default_value = 0.6

# Один жёсткий ключ поверх HDRI: он рисует линию света вдоль фасок
ld = bpy.data.lights.new("Key", type='AREA')
ld.shape = 'RECTANGLE'
ld.size, ld.size_y = 1.2, 0.25
ld.energy = 400.0
key = bpy.data.objects.new("Key", ld)
sc.collection.objects.link(key)
key.location = (-0.7, -0.9, 1.1)
key.rotation_euler = (math.radians(48.0), 0.0, math.radians(-36.0))

cam_data = bpy.data.cameras.new("Cam_Hero")
cam_data.lens = 85.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.01
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 5.6
cam_data.dof.focus_object = body
cam = bpy.data.objects.new("Cam_Hero", cam_data)
sc.collection.objects.link(cam)
cam.location = (0.42, -0.62, 0.30)
cam.rotation_euler = (math.radians(78.0), 0.0, math.radians(34.0))
sc.camera = cam

os.makedirs(bpy.path.abspath("//renders/gun"), exist_ok=True)
sc.render.resolution_x = sc.render.resolution_y = 2048
sc.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
sc.render.filepath = "//renders/gun/hero_"
bpy.ops.render.render(write_still=True)
```

### Этап 9. Экспорт

```python
import bpy, os

os.makedirs(bpy.path.abspath("//exports/gun"), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath("//exports/gun/gun.glb"),
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_extras=True,
)

for name in ("Body", "Body_LOD1", "Body_LOD2"):
    ob = bpy.data.objects.get(name)
    if ob:
        ob.data.calc_loop_triangles()
        print(f"{name}: {len(ob.data.loop_triangles)} tris")
print("materials:", len(bpy.data.materials))
```

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Boolean на кожухе дал невалидную топологию, и фаски «поехали».** Первый вариант резал кожух цилиндром-инструментом с `solver = 'FAST'`. Результат выглядел нормально до добавления Bevel, а потом фаски на месте выреза начали self-intersect: рёбра в зоне пересечения оказались короче, чем ширина фаски, и `use_clamp_overlap` не успевал среагировать на узкие грани. Помогла смена решателя на `EXACT` и применение boolean сразу при создании, а не «сложить всё в стек и применить в конце»: пока boolean висел неприменённым модификатором, любая последующая правка пересчитывала вырез и меняла вершины, на которых уже стояли веса.

**2. `limit_method = 'ANGLE'` дал фаски там, где их быть не должно.** С первым вариантом Bevel фаска появлялась на всех рёбрах с углом больше порога — включая рёбра внутри магазинного отсека, где после выреза острые углы стояли под 45°. Результат: отсек выглядел «съеденным» и потерял читаемость. Перевёл на `limit_method = 'WEIGHT'` с весами, проставленными вручную по Ctrl+E. Это дольше на один шаг, но фаска появляется ровно там, где нужна, и ширину можно задавать отдельно для внешних кромок и для внутренних переходов.

**3. Pointiness на кромках вел себя непредсказуемо.** Первый рейндж был выставлен на 0.45–0.52, и износ появлялся не только на фасках, но и на отдельных гранях внутри углублений — там, где геометрия сходилась под острым углом, хотя визуально это были ровные плоскости. Оказалось, что pointiness реагирует на **острые углы между гранями**, а не на близость к краю: внутренние пересечения для него «острые» ровно так же, как кромки. Пришлось сузить диапазон до 0.52–0.60 и добавить маску по нормали, отсекающую поверхности, смотрящие вбок. После этого износ остался ровно на кромках.

**4. Запечённые нормали 4k весили 60 МБ на объект и тормозили импорт.** Три LOD-версии с собственной картой нормалей 4k — это почти 200 МБ ассетов на одну модель. Уменьшил до 2k для hero и до 1k для LOD1/LOD2: разница на экране не видна, а вес упал вчетверо. Отдельно перевёл карту нормалей в сжатый формат — без сжатия экспорт в 4k стоит дороже, чем сама геометрия.

**5. Запечённая нормаль ломалась при смене Bevel.** После добавления ещё одной фаски нормали перестали совпадать с формой: фаска появилась, а нормаль осталась от старой high-poly. Это не баг, а прямое следствие подхода: карта нормалей — снимок конкретной версии high-poly. Пришлось ввести правило: **любое изменение формы = повторное запекание**, и запись шага запекания рядом с шагом изменения в скрипте, чтобы нельзя было поменять одно и забыть другое.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров нет** (скрипты этапов 7 и 9 печатают реальный три-каунт):

- Объектов: 6 частей (корпус, кожух, магазинный отсек, рукоять, рельса, скоба) плюс high-poly копия и 2 LOD.
- Треугольников: hero **8–12 тыс.**, LOD1 около 3 тыс., LOD2 около 800. Считается `Decimate` итеративно под целевой бюджет.
- Материалов: 2 (gunmetal с износом по кривизне, grip polymer). Текстуры на диске: **2** — карта нормалей 2k hero плюс 1k для LOD.
- Текстур-процедурных: 1 pointiness-райндж на материал, в файлы не выходит.
- Кадров: 1 hero 2048×2048 в EXR multilayer, плюс тестовые 640×640 при 48 сэмплах.
- Рендер в Cycles, 512 сэмплов с адаптивным порогом 0.005 и денойзингом: **десятки минут** на кадр на средней видеокарте. Тестовые прогоны — секунды.

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `Bevel.width` | 0.0025 (2.5 мм) | 1 мм блик теряется, 4 мм — уже «пила» |
| `Bevel.segments` (hero) | 2 | на high-poly 6, чтобы нормаль была гладкой |
| `Bevel.limit_method` | `WEIGHT` | `ANGLE` фаскает внутренние острые рёбра вырезов |
| `use_clamp_overlap` | включать | без него фаски self-intersect на узких рёбрах |
| Boolean `solver` | `EXACT` | `FAST` даёт невалидную топологию на невыпуклых вырезах |
| pointiness `color_ramp` | 0.52–0.60 | шире — износ лезет на внутренние острые углы |
| шероховатость gunmetal | 0.30–0.40, на кромке −0.28 | полированная кромка читается как потёртая |
| `adaptive_threshold` | 0.005 | 0.02 хватает для превью, но на металле остаётся шум |
| `cycles.max_bounces` | 8 | меньше — отражения в металле обрываются в грязь |
| бюджет hero | 8–12 тыс. | больше — фаски начинают сливаться при ретопологии |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Фаски self-intersect в зоне выреза | `FAST`-решатель + узкие грани после boolean | `solver='EXACT'`, применять boolean сразу |
| Фаски появились внутри отсека | `limit_method='ANGLE'` ловит острые внутренние углы | `limit_method='WEIGHT'`, веса вручную |
| Нормали не совпадают с формой | high-poly не перезапечена после изменения | правило «изменил форму = перезапеки» |
| Normal map весит десятки МБ | 4k на каждую LOD-версию | 2k для hero, 1k для LOD |
| Износ лезет на плоскости | pointiness реагирует на острые углы, а не на кромку | сузить рейндж 0.52–0.60 + маска по нормали |
| Грязь в отражениях | `max_bounces` меньше 6 на металле | 8 отражений |
| Модель «мягкая», не hard-surface | гладкое сглаживание без Weighted Normal | Weighted Normal + `FACE_AREA`, шовные рёбра оставить острыми |
| LOD рассыпается | `Decimate` одной долей от начала | итеративно под целевой три-каунт |

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 14: FOOD RENDER (RAMEN)](case_14_food_r visualisation.md)
- **По темам:** [P22: PARTICLE SYSTEMS](../prompts/22_particles.md), [P43: CAMERA SWITCHING & MARKERS](../prompts/43_camera_switching.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [SETUP 13: BLENDER + UNITY ROUNDTRIP](../setups/setup_13_unity_roundtrip.md)
- **Теги:** #case, #modeling, #render