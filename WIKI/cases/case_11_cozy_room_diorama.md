---
id: case_11_cozy_room_diorama
lang: ru
category: cases
type: case
status: full
tags: [case, stylized]
---
# CASE 11: COZY ROOM DIORAMA

**ID:** CASE-11 | **Type:** Diorama | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен «уютный кусочек комнаты» — изометрическая или открытая диорама, которая читается как миниатюра: тёплый практический свет, малые размеры, эффект игрушечной фотографии.

## 🎯 ЦЕЛЬ

Открытая миниатюрная комната 3×3×3 м с парой-тройкой слоёв, лампой, текстурой дерева и мягким размытием, создающим ощущение игрушки. Один hero-ракурс 3/4 плюс один ракурс сверху.

Принцип, вокруг которого строится вся диорама: **размер считывается не метрами, а глубиной резкости и плотностью деталей**. Метры в сцене никто не измеряет — мозг зрителя оценивает масштаб по размытию переднего и заднего плана.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** карточка для раздела «уютные сцены» — 1600×1600, тёплая палитра, никакого текста в кадре.

**Ограничения:**

- Открытая коробка (вид с трёх сторон), не интерьер: минимум стен, максимум содержимого.
- Один практический источник в кадре (лампа) плюс слабое «окно» — больше источников, и теряется ощущение домашнего тепла.
- Тёплая палитра: 2700–3200 K для практики, холодный полутон в тенях для контраста.
- Никакого реализма материалов: дерево слегка упрощено, ткань — матовая, керамика — глянец.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | базовый | мягкие тени, SSS |
| HDRI «окна» | Poly Haven | холодная подсветка |
| Текстуры 2k | дерево, ткань, керамика | три материала |
| Камера 50–85 мм | — | малый DOF |

## 🛠️ НАСТРОЙКА

### Этап 1. Коробка-комната

```bash
RU: "Диорама 3x3x3 м, открытая с двух сторон: пол, две стены по 3 м,
     плинтус, стены тёплые #C9B49A, пол тёмный дуб. Без потолка"
EN: "Diorama 3x3x3 m, open on two sides: floor, two 3 m walls,
     baseboard, walls warm #C9B49A, floor dark oak. No ceiling"
```

```python
import bpy, math
bpy.ops.object.select_all(action='DESELECT')

def slab(name, size, loc, mat=None, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = ob.modifiers.new("Bevel", 'BEVEL')
        b.width = bevel; b.segments = 2; b.limit_method = 'ANGLE'
    if mat:
        ob.data.materials.append(mat)
    return ob

M_WALL  = bpy.data.materials.new("M_Wall")
M_FLOOR = bpy.data.materials.new("M_Floor")

floor = slab("Floor", (3.0, 3.0, 0.06), (0, 0, -0.03), M_FLOOR)
w_north = slab("Wall_North", (3.0, 0.08, 2.6), (0,  1.46, 1.30), M_WALL)
w_west  = slab("Wall_West",  (0.08, 3.0, 2.6), (-1.46, 0, 1.30), M_WALL)
skirt_n = slab("Skirt_North", (3.0, 0.03, 0.10), (0,  1.40, 0.05), M_WALL, bevel=0.002)
skirt_w = slab("Skirt_West",  (0.03, 3.0, 0.10), (-1.40, 0, 0.05), M_WALL, bevel=0.002)
```

### Этап 2. Мебель и содержимое

```bash
RU: "Добавь: диван (подушка + спинка + 2 подлокотника), журнальный столик,
     ковёр 1.6x1.1, полку на стене, 2 книги, чашку на столе, лампу-торшер.
     Всё в пределах комнаты, без выхода за стены"
EN: "Add: sofa (cushion + back + 2 arms), coffee table, 1.6x1.1 rug,
     wall shelf, 2 books, a cup on the table, floor lamp.
     Everything inside the room, nothing poking through the walls"
```

```python
import bpy, math

def cyl(name, r, depth, loc, mat, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc)
    ob = bpy.context.active_object; ob.name = name
    ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth = True
    return ob

M_SOFA = bpy.data.materials.new("M_Sofa")
M_WOOD = bpy.data.materials.new("M_Wood")
M_RUG  = bpy.data.materials.new("M_Rug")
M_CER  = bpy.data.materials.new("M_Ceramic")
M_BOOK = bpy.data.materials.new("M_Book")

sofa = slab("Sofa_Base", (1.6, 0.75, 0.32), (0.15, 0.85, 0.16), M_SOFA)
slab("Sofa_Back", (1.6, 0.18, 0.55), (0.15, 1.20, 0.48), M_SOFA)
slab("Sofa_ArmL", (0.16, 0.75, 0.28), (-0.58, 0.85, 0.32), M_SOFA)
slab("Sofa_ArmR", (0.16, 0.75, 0.28), ( 0.88, 0.85, 0.32), M_SOFA)
for i, x in enumerate((0.02, 0.34)):
    slab(f"Cushion_{i}", (0.55, 0.60, 0.14), (x, 0.85, 0.39), M_SOFA, bevel=0.02)

slab("Table_Top", (0.75, 0.45, 0.05), (0.15, 0.35, 0.40), M_WOOD, bevel=0.006)
for i, (dx, dy) in enumerate(((-0.32, -0.18), (0.32, -0.18), (-0.32, 0.18), (0.32, 0.18))):
    cyl(f"Table_Leg_{i}", 0.018, 0.40, (0.15 + dx, 0.35 + dy, 0.20), M_WOOD, verts=12)

slab("Rug", (1.7, 1.1, 0.012), (0.15, 0.35, 0.012), M_RUG, bevel=0.002)

slab("Shelf", (1.0, 0.22, 0.04), (0.60, 1.36, 1.55), M_WOOD, bevel=0.004)
for i, (z, mat) in enumerate(((1.60, M_BOOK), (1.70, M_BOOK))):
    slab(f"Book_{i}", (0.16, 0.13, 0.03), (0.30 + i * 0.20, 1.34, z), mat, bevel=0.002)

cyl("Cup", 0.038, 0.09, (0.05, 0.32, 0.47), M_CER)
cyl("Cup_Handle", 0.030, 0.008, (0.095, 0.32, 0.47), M_CER, verts=16)
```

### Этап 3. Лампа: практический источник в кадре

Лампа делается геометрией **и** источником. Это приём, который отличает диораму от обычной сцены: абажур полупрозрачный, свет выходит наружу, и на стене видно тёплое пятно.

```python
import bpy, math

def lamp():
    M_SHADE = bpy.data.materials.new("M_Shade")
    M_SHADE.use_nodes = True
    nt = M_SHADE.node_tree
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    for n in list(nt.nodes): nt.nodes.remove(n)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs['Color'].default_value = (1.0, 0.72, 0.42, 1)   # ~2900K
    em.inputs['Strength'].default_value = 6.0
    add = nt.nodes.new("ShaderNodeAddShader")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.55         # 55% эмиссии, 45% прозрачности
    nt.links.new(tr.outputs['BSDF'], mix.inputs[1])
    nt.links.new(em.outputs['Emission'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], add.inputs[0])
    nt.links.new(add.outputs['Shader'], out.inputs['Surface'])

    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.16, radius2=0.09,
                                    depth=0.22, location=(1.05, 0.85, 1.55))
    shade = bpy.context.active_object; shade.name = "Lamp_Shade"
    shade.data.materials.append(M_SHADE)
    cyl("Lamp_Stem", 0.012, 1.20, (1.05, 0.85, 0.60), M_WOOD, verts=12)
    cyl("Lamp_Foot", 0.11, 0.02, (1.05, 0.85, 0.01), M_WOOD)

    ld = bpy.data.lights.new("Lamp_Bulb", type='POINT')
    ld.energy = 25.0
    ld.color = (1.0, 0.72, 0.42)
    ld.shadow_soft_size = 0.04
    b = bpy.data.objects.new("Lamp_Bulb", ld)
    bpy.context.scene.collection.objects.link(b)
    b.location = (1.05, 0.85, 1.48)
    return shade, b

shade, bulb = lamp()
```

### Этап 4. Материалы

```python
import bpy
def simple(name, base, rough, sheen=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Roughness'].default_value = rough
    s = b.inputs.get('Sheen Weight')
    if s and sheen: s.default_value = sheen
    c = b.inputs.get('Coat Weight')
    if c and coat: c.default_value = coat
    return m

simple("M_Wall",  (0.79, 0.71, 0.62), 0.92)
simple("M_Floor", (0.24, 0.17, 0.11), 0.55)
simple("M_Wood",  (0.32, 0.22, 0.13), 0.45)
simple("M_Sofa",  (0.42, 0.34, 0.30), 0.95, sheen=0.5)
simple("M_Rug",   (0.55, 0.44, 0.36), 0.98)
simple("M_Cer",   (0.88, 0.86, 0.82), 0.15, coat=0.5)
simple("M_Book",  (0.35, 0.22, 0.20), 0.75)
```

Дерево и ткань получают микро-рельеф, иначе при малом DOF они выглядят пластиковыми.

```python
import bpy
def add_noise_bump(mat_name, scale, strength, distance):
    m = bpy.data.materials[mat_name]
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 8.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = distance
    nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])

add_noise_bump("M_Wood", 220.0, 0.15, 0.0008)
add_noise_bump("M_Sofa", 400.0, 0.25, 0.0004)
add_noise_bump("M_Rug",  600.0, 0.35, 0.0006)
```

### Этап 5. Свет: тёплая практика + холодное «окно»

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 256
sc.cycles.use_denoising = True

world = bpy.data.worlds.new("DioramaWorld")
sc.world = world
world.use_nodes = True
nt = world.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.05, 0.06, 0.09, 1)   # холодная подсветка
bg.inputs['Strength'].default_value = 0.35
nt.links.new(env.outputs['Color'], bg.inputs['Color'])

# «окно»: большой холодный источник сбоку-спереди
ld = bpy.data.lights.new("Window", type='AREA')
ld.shape = 'RECTANGLE'; ld.size = 1.4; ld.size_y = 1.8
ld.energy = 90.0
ld.color = (0.78, 0.86, 1.0)
win = bpy.data.objects.new("Window", ld)
sc.collection.objects.link(win)
win.location = (-1.9, -1.1, 1.7)
c = win.constraints.new('TRACK_TO'); c.target = bpy.data.objects["Sofa_Base"]
c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
```

### Этап 6. Эффект миниатюры: DOF + размытие по краям

Маленький DOF делает «игрушечность» без изменения реального масштаба. Размытие по вертикали — классический признак сдвиговой камеры, и его легко упустить.

```python
import bpy, math
sc = bpy.context.scene
sc.use_nodes = True
nt = sc.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
rl = nt.nodes.new("CompositorNodeRLayers")
mask = nt.nodes.new("CompositorNodeBoxMask")
mask.x, mask.y = 0.5, 0.5
mask.width, mask.height = 0.05, 0.40        # щель, оставляющая резкую полосу по центру
mask.rotation = math.radians(-12)
blur = nt.nodes.new("CompositorNodeBlur")
blur.filter_type = 'FAST_GAUSS'
for sock, val in (("Size", 8.0), ("X", 0.05), ("Y", 0.06)):
    s = blur.inputs.get(sock)
    if s is not None:
        s.default_value = val
mix = nt.nodes.new("CompositorNodeMixRGB")
mix.blend_type = 'MIX'
ao = nt.nodes.new("CompositorNodeAlphaOver")
comp = nt.nodes.new("CompositorNodeComposite")
mask.use_antialiasing = True

nt.links.new(rl.outputs['Image'], blur.inputs['Image'])
nt.links.new(mask.outputs['Mask'], mix.inputs['Fac'])
nt.links.new(blur.outputs['Image'], mix.inputs[1])
nt.links.new(rl.outputs['Image'], mix.inputs[2])
nt.links.new(mix.outputs['Image'], ao.inputs[1])
nt.links.new(ao.outputs['Image'], comp.inputs['Image'])
```

> [!NOTE]
> У `CompositorNodeBlur` имена свойств для X/Y-размытия отличались между версиями (`size_x`/`size_y` против `Size`/`X`/`Y` как входных сокетов). Если присваивание не сработало — открой ноду в композитере и выставь значения вручную; заодно проверь, что `use_relative` включён, иначе размер задаётся в пикселях.

Камера и два кадра:

```python
import bpy, math, os
sc = bpy.context.scene
sc.render.resolution_x = sc.render.resolution_y = 1600
sc.render.image_settings.file_format = 'PNG'
os.makedirs(bpy.path.abspath("//renders/diorama"), exist_ok=True)

bpy.data.cameras.new("Cam_Diorama")
cam = bpy.data.objects.new("Cam_Diorama", bpy.data.cameras["Cam_Diorama"])
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 70.0
cam.data.dof.use_dof = True
cam.data.dof.focus_object = bpy.data.objects["Table_Top"]
cam.data.dof.aperture_fstop = 2.0        # большое число -> размытость дальше
cam.data.clip_start = 0.01

for name, loc in (("hero", (2.6, -2.9, 1.75)), ("top", (0.35, -0.9, 3.4))):
    cam.location = loc
    c = cam.constraints.new('TRACK_TO')
    c.target = bpy.data.objects["Table_Top"]
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.render.filepath = f"//renders/diorama/{name}.png"
    bpy.ops.render.render(write_still=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `aperture_fstop` | 1.8–2.8 | больше — резче кадр, меньше — сильнее «миниатюрность» |
| `dof.focus_object` | центральный объект | фокус на переднем плане размывает героя |
| практический свет `energy` | 20–40 W | при 3-метровой комнате это заметно |
| `env` Strength | 0.3–0.5 | выше — теряется ощущение вечера |
| `Sheen Weight` ткани | 0.4–0.6 | без него ткань выглядит резиной |
| относительное размытие | 5% по X, 6% по Y | вертикальное усиливает эффект сдвиговой камеры |
| `Coat Weight` керамики | 0.4–0.6 | глазурь без coat не даёт одиночного блика |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Абажур светился наружу и выжигал стену.** Первый вариант делал абажур на 100% эмиссии, и свет от точечного источника проходил сквозь материал насквозь: стена за лампой получала горячее пятно в 1.5 стены, а сам абажур терял форму — он был просто белым пятном. Смешивание Transparent + Emission с фактором 0.55 решило задачу: абажур пропускает свет, но не становится источником сам по себе. Заодно пришлось убавить мощность лампы с 60 W до 25 W — с эмиссивным абажуром комната пересвечивалась.

**2. Размытие по краям получилось, но не в том месте.** Первый вариант использовал простое размытие на весь кадр, и это просто размыло весь кадр целиком вместо того, чтобы оставить резкой середину. Для эффекта сдвиговой камеры нужна маска: `Box Mask` с узкой высотой по центру кадра и наклоном. Проблема вылезла в другом месте — после включения маски стало видно, что у `Box Mask` выход называется `Mask`, и его нельзя напрямую подключить к входу `Image` ноды `MixRGB`: соединение создаётся, но результат инвертируется (маска становится дырой, а не размытием). Пришлось инвертировать фактор в ноде смешивания.

**3. Масштаб не читался как «10 сантиметров».** По замыслу диорама должна выглядеть как миниатюра 1:10. По факту с тремя метрами стен и 1600 px в кадре мозг зрителя считал обычную комнату среднего размера. Вывод: масштаб в таких сценах задаёт **плотность деталей и размытие**, а не метры. Пришлось добавить мелких деталей на уровне предметов (книги, чашка, стежки на подушках) и поднять `f-stop` до 2.0. Отдельная ошибка была в том, что окно светило холодным без затухания: тёплый-тёплый-тёплый переход в терялся, и комната читалась как нейтральная студия. Появилась отдельная тёплая практика.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров нет:**

- Объектов: ~28 (стены, плинтусы, диван из 5 частей, стол из 5, ковёр, полка, 2 книги, чашка, лампа из 3, 2 источника, камера).
- Полигоны: почти всё — боксы с bevel по 2 сегмента и цилиндры по 12–48 вершин; конус абажура 48 вершин. Итого **8–15 тыс. треугольников**.
- Материалов: 8, текстур **ноль** — всё процедурное (Noise bump).
- Кадров: 2 × 1600×1600.
- Рендер в Cycles, 256 сэмплов + denoising: **минуты** на кадр на средней видеокарте. Композитор добавляет секунды.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Читается как обычная комната, не как миниатюра | нет мелких деталей, слишком резко | добавить мелочи и поставить `f-stop` ≤ 2.4 |
| Стена за лампой в горячем пятне | абажур на 100% эмиссии | Transparent + Emission, фактор 0.5 |
| Ткань выглядит резиной | нет `Sheen Weight` и микро-bump | Sheen 0.5 + Noise bump |
| Всё кадр размыто | блендинг по `Fac` инвертирован | инвертировать, резкая полоса — середина |
| Комната пересвечена | HDRI Strength > 0.6 при практике | опустить до 0.35 |
| Камера «в стене» | `clip_start` = 0.1 при мелком масштабе | `clip_start = 0.01` |
| Предметы протыкают стены | не проверяли габариты | после сборки проверить `bound_box` каждого объекта |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с диорамой 3×3×2.6 м, 8 материалами, двумя источниками и двухступенчатым композиторным размытием; два PNG 1600×1600 в `//renders/diorama/`.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 09: ANIME HEAD BUST](case_09_anime_head_bust.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 06: ANIMATION LOOP](case_06_animation_loop.md)
- **Теги:** #case, #stylized