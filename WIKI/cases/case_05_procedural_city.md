---
id: case_05_procedural_city
lang: ru
category: cases
type: case
status: full
tags: [case, geometry-nodes, modeling, pipeline, render, vegetation]
---
# CASE 05: PROCEDURAL CITY

**ID:** CASE-05 | **Type:** Procedural Generation | **Difficulty:** ⭐⭐⭐ | **Time:** 2-4 hours

---

> Когда применять: когда нужно за минуты получить десятки кварталов для проверки композиции, а не готовый ассет: город флажка на заднем плане, панораму, окружение для рендера с большой глубиной.

## 🎯 ЦЕЛЬ

Собрать процедурный город на Geometry Nodes: сетка кварталов, зонирование, генератор зданий по зоне, дорожная сеть с движением, рассев пропов и растительности, LOD по расстоянию и облёт камерой.

Главное, что отличает город от набора кубиков, — **связи между системами**. Здание знает, в какой зоне оно стоит, и берёт высоту и материал оттуда. Дорога знает, где перекрёсток. Пропы рассеиваются по тротуарам, а не в воздухе. Каждая из этих связей — атрибут, и большую часть ошибок в этом кейсе дают именно атрибуты: не тот домен, потерянное поле при объединении геометрии, поле, которое не выжило `Set Position`.

Порядок работы поэтому жёсткий: сначала сетка и зоны, потом здания, и только потом всё, что рассыпается по готовому.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** 500 кадров облёта камеры по спирали вверх над городом 1×1 км, 4K, 30 fps, на одной видеокарте.

**Ограничения:**

- Город не должен быть полностью инстансингом: инстансы нельзя ни сдвинуть по высоте, ни отдать в запекание — нужен гибрид.
- Один материал на зону, иначе материалов будет больше, чем зданий.
- Движение должно быть цикличным и непрерывным: машина не должна прыгать в конце петли.
- Кадры считаются на CPU-рендере как минимум: 500 кадров × 4K × 512 сэмплов — это неделя.
- Дальние кварталы нельзя оставлять в LOD0: память уйдёт раньше, чем закончится рендер.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender + Geometry Nodes | актуальная | вся генерация |
| Коллекция с 5–10 вариантами деревьев | Poly Pizza или свой набор | инстансинг растительности |
| Коллекция с 8–12 вариантами машин | то же | инстансинг транспорта |
| HDRI дневного города | Poly Haven | базовое освещение |
| Сжатие EXR | ZIP | 500 кадров занимают место |

## 🛠️ НАСТРОЙКА

### Этап 1. Сетка кварталов и зонирование

```bash
# Base Grid 10x10 blocks, 100x100м каждый
"GN: Grid 10x10, spacing 100м
 Атрибут 'District': Random (0=Downtown, 1=Residential, 2=Industrial, 3=Park)
 Атрибут 'Density': по District (Downtown=1.0, Res=0.6, Ind=0.8, Park=0.1)"
```

### Этап 2. Генератор зданий

```bash
# Building Logic по District
"Downtown (0): Высота 50-200м, Glass/Concrete, Flat Roof + HVAC
 Residential (1): Высота 10-50м, Brick/Plaster, Pitched Roof + Balconies
 Industrial (2): Высота 5-20м, Metal/Concrete, Flat Roof + Vents
 Park (3): Нет зданий, только скеттер деревьев/лавочек

 # Building GN Tree:
 1. Grid → Random Scale/Offset → Extrude (Height by District)
 2. Window Array: фасад → Grid → Boolean/Inset → Glass Material
 3. Roof Details: HVAC units, Antennas, Green Roof (Downtown)
 4. LOD: Distance → Decimate (0.5 / 0.25 / 0.1)
 5. Instancing: Collection → Random Pick → Realize Instances"
```

Шаг 5 в таком виде — источник почти всех проблем. Инстансы экономят память в сотни раз, но `Realize Instances` превращает их в обычную геометрию, и вся экономия испаряется. Реальный компромисс: инстансить **детали** (окна, кондиционеры, деревья), а сами корпуса зданий оставлять как готовую геометрию — их всё равно нужно двигать по высоте и красить по зоне.

### Этап 3. Дорожная сеть и трафик

```bash
# Roads (Curve-based)
"GN: Curve Grid 11x11 (между блоками)
 Road Width: Main=12м, Local=8м, Alley=4м
 Sidewalks: 2м each side, Curb height 0.15м
 Markings: Center line, Crosswalks, Lane dividers

 # Traffic (GN Animation)
 "Car Collection: 10 low-poly variants (Poly Pizza)
 Path Follow: Roads → Resample → Points → Instance Cars
 Speed: Random 30-60 км/ч, Loop на 500 фреймах
 Traffic Lights: Procedural на перекрёстках (Red/Yellow/Green cycle)"
```

Цикличность движения делается через **Scene Time** в поле позиции: индекс точки на кривой делится на общее число точек и умножается на диапазон кадров. Никаких «по кадрам» — сетка пересчитывается целиком, и любая попытка анимировать инстансы поштучно убьёт производительность.

### Этап 4. Пропы и растительность

```bash
# Street Props (Poly Pizza + GN)
"Streetlights: каждые 20м по тротуарам, вариант 3 типа
 Benches: в парках/у жилых, случайная ротация
 Trash cans, Hydrants, Signs: Scatter по тротуарам (Density=0.05)
 Trees: 5 видов (Poly Pizza), Scatter в парках/улицах
 Grass/Flowers: Geometry Nodes на парках (Weight Paint для путей)"

# GN Scatter Setup
"Distribute Points on Faces → Poisson Disk → Density Attribute
 Instance on Points → Random Pick from Collection → Random Rotation/Scale
 Realize Instances → Merge by Distance"
```

### Этап 5. LOD-система

```bash
# Distance-based LOD (GN)
"Attribute 'Distance' = length(Camera_Location - Position)
 LOD0 (0-50м): Full Geo, 4k textures
 LOD1 (50-200м): Decimate 0.5, 2k textures
 LOD2 (200-500м): Decimate 0.25, 1k textures
 LOD3 (500м+): Decimate 0.1, Billboard/Impostor"

# Impostors для дальнего плана
"Render Billboard: 8 углов → Sprite Sheet → Shader: Billboard + Alpha"
```

### Этап 6. Рендер облёта

```bash
# Camera: Drone fly-through
"Path: Spiral Up 500м за 500 фреймов
 DOF: Focus на центр города, f/4.0

 # Lighting
"HDRI 'city_day' 4k strength=1.0
 Sun: 5000W, angle 45°, shadows ON
 Volumetric: Light fog density=0.01"

# Render
"Cycles 128 samples, Denoising, 4K
 Viewport: 1/4 res для превью
 Output: EXR + MP4 (60fps)"
```

### Атрибуты: то, на чём держится вся связность

Зоны, плотность, тип и индекс варианта хранятся в именованных атрибутах. Поле, положенное во временную переменную, **не переживёт** ни `Join Geometry`, ни смену домена — и город молча рассыплется в однородную кашу.

```python
import bpy

def sock(node, name, out=False, hint=None):
    """Найти сокет по имени.

    У многих нод (Random Value, Store Named Attribute) несколько одноимённых
    сокетов — по одному на тип данных. node.inputs['Min'] вернёт ПЕРВЫЙ, то
    есть не тот, что показан в интерфейсе при выбранном data_type.
    Поэтому ищем по имени И по типу; если hint не задан, берём первый.
    """
    seq = node.outputs if out else node.inputs
    for s in seq:
        if s.name == name and (hint is None or s.type == hint):
            return s
    for s in seq:
        if s.name == name:
            return s
    raise KeyError(f"{node.bl_idname}: no socket named {name!r}")

def set_sock(node, name, value, hint=None):
    s = sock(node, name, hint=hint)
    s.default_value = value
    return s

def store_zoning(node_tree, seed_value=17):
    """Записать случайный номер квартала и плотность застройки как именованные
    атрибуты — только так они переживают Join Geometry.

    node_tree — это nodes_tree самого модификатора Geometry Nodes.
    """
    nodes, links = node_tree.nodes, node_tree.links

    idx = nodes.new("GeometryNodeInputIndex")          # индекс точки в сетке

    rnd = nodes.new("FunctionNodeRandomValue")
    rnd.data_type = 'INT'
    set_sock(rnd, 'Seed', seed_value)                 # одно число на весь город
    set_sock(rnd, 'Min', 0, hint='INT')               # Downtown
    set_sock(rnd, 'Max', 3, hint='INT')               # Park
    links.new(idx.outputs[0], sock(rnd, 'ID'))        # без ID поле не привязано к точке

    store_zone = nodes.new("GeometryNodeStoreNamedAttribute")
    store_zone.data_type = 'INT'
    store_zone.domain = 'POINT'                       # не FACE: значение одно на вершину
    set_sock(store_zone, 'Name', "district")
    links.new(sock(rnd, 'Value', out=True, hint='INT'),
              sock(store_zone, 'Value', hint='INT'))

    # Плотность: 4 значения -> два числа. Линейная раскладка слегка неточна
    # для промежуточных зон, и это осознанно — визуально разницы не видно.
    density = nodes.new("ShaderNodeMapRange")
    links.new(sock(rnd, 'Value', out=True, hint='INT'), density.inputs['Value'])
    density.inputs['To Min'].default_value = 0.9      # плотная застройка
    density.inputs['To Max'].default_value = 0.1      # парк

    store_density = nodes.new("GeometryNodeStoreNamedAttribute")
    store_density.data_type = 'FLOAT'
    store_density.domain = 'POINT'
    set_sock(store_density, 'Name', "density")
    links.new(density.outputs['Result'],
              sock(store_density, 'Value', hint='VALUE'))
    links.new(store_zone.outputs['Geometry'], store_density.inputs['Geometry'])

    return store_density.outputs['Geometry']

# В редакторе это дерево собирается мышью за минуту. Скриптом имеет смысл
# только массовое изменение: mod = obj.modifiers.new("CityGN", 'NODES'),
# затем взять mod.node_group и пересобрать ноды. Имя атрибута и домен в
# редакторе видны сразу — в отличие от Python, где сокеты приходится искать.
```

```python
import bpy

def instance_zone(node_tree, collection_name="Props", seed=3):
    """Инстансить коллекцию, выбирая вариант по индексу точки.

    Collection Info с Separate Children + Instance on Points — это и есть
    «выбрать вариант»: целое число становится номером потомка коллекции.
    """
    nodes, links = node_tree.nodes, node_tree.links
    coll = bpy.data.collections[collection_name]

    col = nodes.new("GeometryNodeCollectionInfo")
    col.inputs['Collection'].default_value = coll
    col.inputs['Separate Children'].default_value = True
    col.inputs['Reset Children'].default_value = True
    col.transform_space = 'RELATIVE'

    idx = nodes.new("GeometryNodeInputIndex")
    pick = nodes.new("FunctionNodeRandomValue")
    pick.data_type = 'INT'
    set_sock(pick, 'Seed', seed)
    set_sock(pick, 'Min', 0, hint='INT')
    set_sock(pick, 'Max', max(len(coll.objects), 1), hint='INT')
    links.new(idx.outputs[0], sock(pick, 'ID'))

    on_pts = nodes.new("GeometryNodeInstanceOnPoints")
    on_pts.inputs['Pick Instance'].default_value = True
    links.new(sock(pick, 'Value', out=True, hint='INT'), on_pts.inputs['Instance Index'])
    links.new(col.outputs['Instances'], on_pts.inputs['Instance'])
    return on_pts.outputs['Instances']
```

> [!NOTE]
> Точные имена и набор входов у нод Geometry Nodes (`Collection Info`,
> `Store Named Attribute`, `Map Range`, `Random Value`) менялись между версиями
> Blender: ноды переезжали из Geometry Nodes в Shader, поля добавлялись, часть
> входов переименовывалась. Не пиши дерево по памяти — открой ноду в своём
> редакторе и сверь входы. Проверка из Python: у ноды есть `inputs` с именами,
> и лишний именованный аргумент в скрипте даст `TypeError`, а отсутствующий
> вход — пустую ноду, которая молча ничего не делает.

### Рендер: параметры, без которых облёт не запустится

```python
import bpy, os

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'GPU'
sc.cycles.samples = 128
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.02       # для 500 кадров важнее, чем samples
sc.cycles.use_denoising = True

sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
sc.render.resolution_percentage = 50      # превью всего пролёта — в 4 раза дешевле
sc.render.use_persistent_data = True      # без этого движок пересобирает BVH каждый кадр
sc.frame_start, sc.frame_end = 1, 500
sc.frame_step = 2                          # 250 кадров = 25 секунд при 10 fps

sc.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
sc.render.image_settings.color_mode = 'RGBA'
sc.render.image_settings.exr_codec = 'ZIP'
sc.render.filepath = "//renders/city/frame_"
os.makedirs(bpy.path.abspath("//renders/city"), exist_ok=True)
```

> [!NOTE]
> Флаг `use_persistent_data` в интерфейсе называется **Persistent Data** и лежит
> в свойствах рендера. Для сцены с анимацией Geometry Nodes он даёт основную
> экономию времени: без него вся сетка пересобирается заново на каждом кадре.

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. `Realize Instances` на пятом шаге съел всю память.** По инструкции на этапе 2 инстансы реализовывались целиком, и город из 1000 корпусов превратился в 80–100 миллионов реальных треугольников. Blender стоял несколько минут на каждом кадре, а потом падал по памяти, и это выглядело как «сцена слишком тяжёлая», хотя в терминах Blender она была лёгкой — просто не инстансинг. Пришлось оставить инстансинг на деталях (окна, HVAC, деревья, машины), а корпуса зданий реализовать один раз на этапе сборки и больше не трогать. Побочный эффект: корпуса перестали быть одинаковыми, что для города, если честно, скорее плюс.

**2. Атрибут зоны молча пропадал, и город становился однородным.** Кварталы генерировались корректно, но через `Join Geometry` значение `district` исчезало: поле было записано в домене `POINT`, а присоединяли геометрию, где те же вершины принадлежали другой геометрии, и без явного `Store Named Attribute` на выходе значение просто не доезжало. Симптом был обманчивым: город выглядел нормально, но все здания получали высоту и материал первой зоны. Поймать это помог только рендер одного кадра с включённой отладкой атрибутов. Лечится тем, что **любой** атрибут, который должен пережить `Join Geometry`, записывается именованным и последним шагом дерева.

**3. Случайность не была повторяемой.** `Random Value` без явного `Seed` давал другой город при каждом пересчёте — то есть при каждом кадре анимации. Город «мерцал»: окна переезжали, машины меняли цвет. Оказалось, что у ноды `Random Value` поле `Seed` не имеет значения по умолчанию, которое «просто работает», и его надо задавать явно; более того, у ноды `Instance on Points` свой индекс варианта берётся из индекса точки, и если точки перегенерировались, варианты тоже менялись. После явного `Seed` город стал стабильным между кадрами.

**4. 500 кадров считались месяц.** Первая версия рендерила 500 кадров в 4K при 512 сэмплах с полным BVH на кадр. Пересчёт до 128 сэмплов с адаптивным порогом 0.02, включение `use_persistent_data` и шаг кадра 2 урезали время примерно в двадцать раз — и это при том же видеорезультате, который для фонового плана не отличить. Вывод, который стоило сделать раньше: **для фонового плана разрешение и сэмплы — первое, что можно отдать**.

**5. Отражения в окнах давали «кашу» из соседних зданий.** Здания стояли впритык, и зеркальные фасады показывали геометрию, которая тут же исчезала — получалось мерцание при движении камеры. Решилось двумя настройками: уменьшить отражающую долю на материале стекла и поднять шероховатость до ~0.15, чтобы отражения слегка размывались и не показывали чужую геометрию резко.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров нет:**

- Сетка: 10×10 кварталов по 100 м, то есть примерно 1 км².
- Зданий: порядка 1000 корпусов, из них инстансингом собраны детали — окна, HVAC, венты.
- Дороги: порядка 30–50 км кривых, с тротуарами и разметкой.
- Пропов: десятки тысяч инстансов (фонари, урны, гидранты, знаки), деревья — десятки тысяч.
- Полигоны в кадре после LOD: **десятки миллионов** на близких кадрах, единицы миллионов на дальних.
- Текстуры: 2k на близкие зоны, 1k на дальние, одна HDRI 4k.
- Кадров: 500 при 3840×2160, из них отрендерено 250 (шаг 2), плюс превью по 960×540.
- Рендер в Cycles со 128 сэмплами и денойзингом: **часы, а не минуты**, на средней видеокарте. Это фон для 25-секундного фрагмента — и это главный вывод по соотношению усилий и пользы.

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| размер квартала | 100 м | меньше — город читается как улей, больше — как пустыня |
| `Random Value.Seed` | одно число на всю сцену | сменил — пересобрался весь город, включая окна |
| домен атрибута `district` | `POINT` | при `FACE` зона «съезжает» на гранях у швов |
| плотность в Downtown | 0.9 | выше — квартал без воздуха, читается как монолит |
| доля инстансов | детали инстансятся, корпуса реализуются | реализация корпусов — главный расход памяти |
| `Decimate` по расстоянию | 0.5 / 0.25 / 0.1 | ниже 0.1 силуэт здания рассыпается |
| шероховатость стекла фасадов | 0.1–0.2 | 0.0 даёт резкие отражения соседей и мерцание |
| `cycles.samples` | 128 + адаптивный порог 0.02 | 512 — вчетверо дольше при том же видеорезультате |
| `use_persistent_data` | включать для любой анимации | выключить только если BVH не влезает в память |
| `frame_step` | 2 | 10 fps для фона достаточно |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Город мерцает между кадрами | не задан `Seed` у `Random Value` | задать `Seed` явно, один на сцену |
| Все здания одинаковые | атрибут зоны потерялся при `Join Geometry` | `Store Named Attribute` последним шагом |
| Blender падает по памяти | `Realize Instances` на корпусах | инстансить детали, корпуса реализовать один раз |
| Зона «съезжает» на швах | атрибут в домене `FACE` | перенести в `POINT` |
| Окна показывают соседние здания | зеркальный фасад без размытия | поднять шероховатость до 0.15 |
| Облёт идёт вчетверо дольше | `use_persistent_data` выключен | включить в свойствах рендера |
| Рендер не месяц, а недели | адаптивное семплирование выключено | `use_adaptive_sampling` + порог 0.02 |
| Нода молча ничего не делает | поле не выжило `Set Position` | хранить в именованном атрибуте, а не во временной переменной |
| `TypeError` на входе ноды | нода переехала между версиями Blender | сверить входы в редакторе или через `nodes[...].inputs` |

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 13: HARD-SURFACE SCI-FI GUN](case_13_hard_surface_gun.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md)
- **По темам:** [P22: PARTICLE SYSTEMS](../prompts/22_particles.md), [WF 05: PROCEDURAL ASSETS](../workflows/wf_05_procedural_assets.md), [CASE 12: LOWPOLY FOREST PACK](case_12_lowpoly_forest_pack.md)
- **Теги:** #case, #geometry-nodes, #modeling, #pipeline, #render, #vegetation