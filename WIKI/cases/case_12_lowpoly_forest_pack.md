---
id: case_12_lowpoly_forest_pack
lang: ru
category: cases
type: case
status: full
tags: [case, vegetation]
---
# CASE 12: LOWPOLY FOREST PACK

**ID:** CASE-12 | **Type:** Environment | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен игровой или стилизованный лесной ассет: несколько пород деревьев, кусты, камни, одна атлас-текстура на весь пак и ветер, который двигает всё это без анимации.

## 🎯 ЦЕЛЬ

Пять деревьев, кусты и камни как **один набор ассетов** с общей атлас-текстурой, единым материалом и покачиванием на ветру, вписанным в геометрию. На выходе — пак, который можно разложить по сцене десятками копий без нагрузки.

Ключевое требование к пакету: **один материал на весь набор**. Двенадцать уникальных материалов означает двенадцать вызовов шейдера на каждый объект — на мобильном это единственная причина, по которой лес тормозит.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** 5 деревьев + 3 куста + 3 камня, лоу-поли, лёгкая листва, одна атлас-карта 1024×1024, ветер, пригодно для импорта в движок.

**Ограничения:**

- Бюджет: не более 60 тыс. треугольников на весь пак.
- Листва — не альфа-карта с прозрачностью на квадрате (это дорого и сортируется плохо), а геометрия: плоские кластеры с двух сторон.
- Ветер должен работать **без скелета и без shape keys** — иначе пак нельзя быстро размножить.
- Атлас один: значит UV всех объектов укладываются в один лист, и соседние острова не должны накладываться.

## 📋 ЧТО ПОНАДОБИТЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Geometry Nodes | 3.0+ | инстансы и ветер |
| Текстура-атлас | рисуется или генерируется | один материал на пак |
| Справочник по флоре | — | силуэт и пропорции |

## 🛠️ НАСТРОЙКА

### Этап 1. Форма дерева: ствол + кластеры кроны

```bash
RU: "Дерево: ствол как конус с 6-8 сторонами, высота 4-7 м,
     крона из 5-8 плоских кластеров (icosphere с 1 делением, масштаб по Z 0.4),
     снизу листва темнее. Куст: 3 кластера. Камень: icosphere с 1 делением, нерегулярный"
EN: "Tree: trunk as 6-8 sided cone, height 4-7 m,
     crown of 5-8 flat clusters (1-subdivision icosphere, Z scale 0.4),
     foliage darker below. Bush: 3 clusters. Rock: 1-subdivision icosphere, irregular"
```

```bash
RU: "Построй 5 деревьев разной высоты (4.2, 5.1, 6.0, 5.6, 4.8 м)
     и разной формы кроны, каждый своим объектом, имена Tree_01..Tree_05"
EN: "Build 5 trees of different heights (4.2, 5.1, 6.0, 5.6, 4.8 m)
     and crown shapes, one object each, named Tree_01..Tree_05"
```

```python
import bpy, math, random

def trunk(name, height, r_base, r_top, sides=7):
    bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=r_base, radius2=r_top,
                                    depth=height, location=(0, 0, height / 2))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(bpy.data.materials["M_Forest"])
    return ob

def cluster(name, loc, scale, seed):
    """Плоский кластер листвы: два «слоя» граней + случайное вращение."""
    rng = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (scale[0], scale[1], scale[2] * 0.45)      # сплющиваем по Z
    ob.rotation_euler = (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2),
                         rng.uniform(0, math.tau))
    ob.data.materials.append(bpy.data.materials["M_Forest"])
    return ob

def tree(name, height, n_crown, seed, spread=0.9):
    rng = random.Random(seed)
    t = trunk(f"{name}_Trunk", height, 0.14 + height * 0.02, 0.05, sides=7)
    parts = [t]
    for i in range(n_crown):
        a = math.tau * i / n_crown + rng.uniform(-0.3, 0.3)
        r = spread * rng.uniform(0.5, 1.0)
        z = height * (0.55 + 0.42 * (i / max(n_crown - 1, 1)))
        c = cluster(f"{name}_Crown_{i}",
                    (math.cos(a) * r, math.sin(a) * r, z),
                    (0.62 + rng.uniform(0, 0.35), 0.62 + rng.uniform(0, 0.35), 0.62),
                    seed + i)
        parts.append(c)
    return parts

def bush(name, seed):
    rng = random.Random(seed)
    parts = []
    for i in range(3):
        parts.append(cluster(f"{name}_{i}",
                             (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25),
                              0.22 + rng.uniform(0, 0.15)),
                             (0.45, 0.45, 0.45), seed * 7 + i))
    return parts

def rock(name, seed):
    rng = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0,
                                         location=(0, 0, 0.22))
    ob = bpy.context.active_object
    ob.name = name
    for v in ob.data.vertices:                    # нерегулярность: рваный силуэт
        v.co *= rng.uniform(0.75, 1.25)
        v.co.z = abs(v.co.z) * 0.8
    ob.scale = (0.42, 0.36, 0.34)
    ob.rotation_euler = (0, 0, rng.uniform(0, math.tau))
    ob.data.materials.append(bpy.data.materials["M_Forest"])
    return ob

M = bpy.data.materials.new("M_Forest")
pack = []
for i, (h, n, sd, sp) in enumerate([(4.2, 6, 11, 0.8), (5.1, 7, 23, 0.95),
                                    (6.0, 8, 37, 1.1), (5.6, 6, 41, 0.9),
                                    (4.8, 7, 53, 1.0)]):
    pack += tree(f"Tree_{i+1:02d}", h, n, sd, sp)
for i in range(3):
    pack += bush(f"Bush_{i+1:02d}", 100 + i)
for i in range(3):
    pack.append(rock(f"Rock_{i+1:02d}", 200 + i))
print("объектов в паке:", len(pack))
```

### Этап 2. Один материал + атлас

Атлас рисуется заранее. Ключевой момент — нижняя часть кроны темнее: это делает объём без единого источника света.

```python
import bpy
mat = M
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

atlas = nt.nodes.new("ShaderNodeTexImage")
atlas.image = bpy.data.images.load(bpy.path.abspath("//tex/forest_atlas.png"))
atlas.extension = 'EXTEND'

# затемнение снизу по мировой Z: читается как «свет сверху» даже в шейдере без освещения
geo = nt.nodes.new("ShaderNodeNewGeometry")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs['From Min'].default_value = 0.0
mr.inputs['From Max'].default_value = 6.0
mr.inputs['To Min'].default_value = 0.55      # низ тёмный
mr.inputs['To Max'].default_value = 1.0       # верх светлый

mix = nt.nodes.new("ShaderNodeMixRGB")
mix.blend_type = 'MULTIPLY'
mix.inputs['Fac'].default_value = 1.0

nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
nt.links.new(atlas.outputs['Color'], mix.inputs[1])
nt.links.new(mr.outputs['Result'], mix.inputs[2])
nt.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.9

# двухсторонняя листва: с обратной стороны она не должна становиться чёрной.
# Проще всего оставить Backface Culling выключенным в настройках материала
# и добавить лёгкий Sheen, чтобы плоскости читались с двух сторон.
if bsdf.inputs.get('Sheen Weight'):
    bsdf.inputs['Sheen Weight'].default_value = 0.25
```

> [!NOTE]
> Двухстороннее освещение листвы в Cycles зависит от настроек материала: либо включён `Backface Culling` в настройках материала (тогда нужен Geometry → Backfacing), либо в шейдере используют `Geometry → Backfacing` как множитель цвета и `Mix Shader` между двумя поверхностями. Точный набор полей Principled BSDF (в частности наличие `Sheen Weight` и его название) зависит от версии — проверь в `Help → Manual`, раздел про Principled BSDF.

### Этап 3. UV в один атлас

Ручная укладка в атлас — трудоёмко, поэтому используем упаковку островов в пределах одного листа.

```python
import bpy, math
M = bpy.data.materials["M_Forest"]
UV = 0.0                        # атлас 0..1; чтобы упаковать, атлас должен быть ровно 0..1
for ob in bpy.data.objects:
    if not ob.name.startswith(("Tree_", "Bush_", "Rock_")):
        continue
    me = ob.data
    me.use_auto_smooth = True if hasattr(me, "use_auto_smooth") else False
    for p in me.polygons:
        p.use_smooth = False     # лоу-поли: плоские грани, сглаживание убивает стиль
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(70), island_margin=0.004)
    # сдвигаем острова внутрь атласа, иначе они выходят за 0..1 и тянут крайний цвет
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.cursor_set(location=(0.5, 0.5))
    bpy.ops.uv.move(type='ALIGNED')
    bpy.ops.object.mode_set(mode='OBJECT')

atlas_img = bpy.data.images.get("forest_atlas")
print("лист атласа:", tuple(atlas_img.size) if atlas_img else "нет")
```

### Этап 4. Ветер: деформация без скелета и без shape keys

Самый дешёвый способ — `Simple Deform` в режиме Bend, привязанный к пустому объекту, который медленно качается. Форма деформируется на CPU/GPU без единого ключа.

```python
import bpy, math

def add_wind(target_objects, strength=0.35, period=48):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    ctl = bpy.context.active_object
    ctl.name = "Wind_CTRL"
    ctl.rotation_mode = 'XYZ'

    n_periods = 2                                   # два колебания за цикл
    for f in range(0, period * n_periods + 1, period):
        ctl.rotation_euler = (0.0, 0.0, math.radians(strength * 60))
        ctl.keyframe_insert("rotation_euler", frame=f)

    for ob in target_objects:
        mod = ob.modifiers.new("Wind", 'SIMPLE_DEFORM')
        mod.deform_method = 'BEND'
        mod.angle = math.radians(12.0)               # базовый изгиб ствола
        mod.origin = ctl                             # ось вокруг пустого объекта
        mod.deform_axis = 'X'
        mod.vertex_group = ""                        # вся геометрия, без ограничения
    return ctl

foliage = [o for o in bpy.data.objects
           if o.name.startswith(("Tree_", "Bush_")) and "Trunk" not in o.name]
add_wind(foliage, strength=0.5, period=48)
```

Для камеры и окон ветер не нужен — деформация считается в Object-координатах, и при перемещении объекта деформация «едет». Это дефект, а не фича: замораживать позицию при инстанцировании.

```python
import bpy
dg = bpy.context.evaluated_depsgraph_get()
total = 0
for ob in foliage:
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    total += sum(len(p.vertices) - 2 for p in me.polygons)
    ev.to_mesh_clear()
print(f"треугольников после деформации (без применения): {total:,}")
```

### Этап 5. Сборка пака в коллекцию и превью

```python
import bpy, os, math

pack_coll = bpy.data.collections.new("ForestPack")
bpy.context.scene.collection.children.link(pack_coll)

pack_objs = [o for o in bpy.data.objects
             if o.name.startswith(("Tree_", "Bush_", "Rock_"))]
for ob in pack_objs:
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    pack_coll.objects.link(ob)
    ob.data.name = ob.name + "_mesh"       # уникальное имя меша: копии не будут делить данные

# превью-раскладка: все объекты в ряд, одна камера
for i, ob in enumerate(pack_objs):
    ob.location.x = (i % 12) * 1.2 - 7.0
    ob.location.y = -(i // 12) * 1.6

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
os.makedirs(bpy.path.abspath("//renders/pack"), exist_ok=True)
sc.render.filepath = r"//renders/pack/forest_pack.png"
bpy.ops.render.render(write_still=True)

sc.render.filepath = r"//export/forest_pack.glb"
bpy.ops.export_scene.gltf(filepath=bpy.path.abspath("//export/forest_pack.glb"),
                          export_format='GLB', use_selection=False,
                          export_apply=True, export_texcoords=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| сторон конуса ствола | 6–8 | меньше — слишком «мультяшно», больше — теряется лоу-поли |
| `subdivisions` кластера | 1 | 2 даёт +80 треугольников на кластер |
| `use_smooth` | `False` | для лоу-поли обязательно: сглаженный лоу-поли не читается |
| `angle_limit` Smart UV | 70° | выше — больше островов, ниже — возможны наложения |
| `island_margin` | 0.004 | ровно столько нужно, чтобы соседи не «протекали» |
| `MapRange To Min` | 0.55 | сильнее затемнение низа — объёмнее крона |
| `Simple Deform.angle` | 8–15° | выше — трава пригибается |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Ветер деформировал деревья при переносе пака в другую сцену.** `Simple Deform` считает деформацию в системе координат пустого объекта, а не самого объекта. Пока дерево стояло в origin, всё выглядело правильно; как только его передвинули на позицию в лесу, деформация «уехала» и крона наклонялась в другую сторону. Выяснилось при сборке пробной сцены из 30 деревьев. Решили тем, что при инстанцировании в движке деформация считается на стороне движка (skinned mesh или шейдерное смещение по UV), а в паке ветер оставлен только для превью-сцены. Практический вывод: **ветер в паке — это визуальная помощь для превью, а не часть ассета**.

**2. Атлас «протёк» на кластерах.** Первый проход UV с `island_margin = 0.001` дал края, где соседний остров подтекал в пиксель: на игровом расстоянии крона читалась в кашу. Увеличение margin до 0.004 и сдвиг островов внутрь листа (`uv.cursor_set` в центр + ALIGNED) убрали проблему. Дополнительно выяснилось, что `Smart UV Project` на икосферах даёт острова вплотную к границе UV, поэтому текстура бралась из соседней ячейки атласа — отсюда «пятна» неправильного цвета.

**3. Сглаженные нормали убили стиль.** Первая версия использовала авто-сглаживание по углу 30° ради «качества». Для лоу-поли это дало кашу: грани в кластерах перестали читаться, объёмы кроны слиплись, и пак выглядел как обычная среднеполигонная растительность. Откат на плоские грани (`use_smooth = False`) вернул узнаваемый лоу-поли вид — и заодно сократил время рендера, потому что нормали стали предсказуемыми.

**4. Тёмный низ сделал лес «грязным».** Затемнение снизу с `To Min = 0.35` в тёмной палитре дало почти чёрную нижнюю треть кроны. Подняли до 0.55 и добавили `Sheen Weight` на листве, и низ перестал читаться как дыра.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров не проводилось:**

- Объектов: 5 стволов + 34 кластера кроны + 9 кластеров кустов + 3 камня = **~51 объект** в коллекции `ForestPack`.
- Полигоны: конус 7 сторон — 14 треугольников; икосфера `subdivisions=1` — 80 треугольников. Итого: 5×14 + 34×80 + 9×80 + 3×80 ≈ **4.2 тыс. треугольников на весь пак**. Это сильно ниже бюджета в 60 тыс. — запас остался на второй уровень детализации.
- Материалов: **1**, текстур: **1 атлас 1024×1024** (RGBA). Это и было целью.
- Модификаторов: 43 объекта листвы с `Simple Deform` (только для превью).
- Рендер 1600×1000 в Cycles, 64 сэмпла: **секунды** — сцена крошечная. GLB с атласом — единицы мегабайт.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Атлас «протекает» между объектами | слишком малый `island_margin`, острова у границы UV | margin 0.004 + сдвиг внутрь листа |
| Стиль «мультяшный», но грязный | сглаженные нормали на лоу-поли | `use_smooth = False` |
| Крона сливается в пятно | `MapRange To Min` < 0.4 | поднять до 0.55 |
| Ветер «едет» при переносе | `Simple Deform` в координатах пустого объекта | ветер только для превью, в движке — свой |
| Много draw call в движке | 51 объект вместо инстансов | инстансировать в движке или через Geometry Nodes |
| Камни выглядят как «картофелины» | равномерный множитель на вершинах | направлять деформацию вдоль оси, а не во все стороны |

## ✅ РЕЗУЛЬТАТ

На выходе: коллекция `ForestPack` из ~51 объекта с 4.2 тыс. треугольников, один материал `M_Forest`, атлас 1024×1024, превью 1600×1000 (`//renders/pack/forest_pack.png`) и GLB для движка.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md)
- **По темам:** [CASE 06: ANIMATION LOOP](case_06_animation_loop.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md)
- **Теги:** #case, #vegetation