---
id: case_03_product_viz
lang: ru
category: cases
type: case
status: full
tags: [case, compositing, lighting, pipeline, render, shading, texturing]
---
# CASE 03: PRODUCT VISUALIZATION

**ID:** CASE-03 | **Type:** Product Visualization | **Difficulty:** ⭐⭐ | **Time:** 1-2 hours

---

> Когда применять: когда предмет снимают для карточки товара, каталога или рекламы: нужен нейтральный фон, управляемые блики и кадр, в котором форма читается без усилий зрителя.

## 🎯 ЦЕЛЬ

Собрать предмет студийного качества из Blender: точная форма, материалы, которые держат блик, схема света, где каждый источник отвечает за свою задачу, макро-камера с малым DOF и композиторный грейд.

Ключевая мысль всего кейса: **продуктовая съёмка — это не «красивый рендер», а управление бликами**. Зритель не рассматривает текстуру; он считывает форму по тому, как свет скользит по фаскам и где гаснет. Ошибка в источнике света стоит дороже ошибки в модели.

Второе правило: масштаб сцены берётся из реальных габаритов. Предмет 40 мм в реальности должен быть 0.040 м в сцене — иначе площади источников, глубина резкости и поведение SSS/стекла будут не те, а пересчитывать их потом дорого.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** карточка часов на 1600×1600 для каталога, плюс три детальных кадра (циферблат, коронка, текстура ремня). Фон нейтральный, без отражений окружения.

**Ограничения:**

- Никакого окружения в кадре: только студийные источники, HDRI даёт мягкую заливку, но не отражения.
- Металл должен читаться металлом: без HDRI на отражениях полированная сталь выглядит серой пластиной.
- Стекло без видимых «внутренностей»: толщина и IOR задают всё, Absorption — цвет кромки.
- Один предмет, один материал на деталь — чтобы рендер можно было ускорить без потери качества.
- Никаких текстур с внешних сайтов: только процедурные, иначе вопрос лицензий.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender + Cycles | базовый | стекло, SSS, качественные блики |
| HDRI студийная | Poly Haven, 1k или 2k | заполняющий свет и отражения в металле |
| Процедурные текстуры | Noise, Voronoi | зерно металла, кожа ремня |
| Композитор | встроенный | грейд, glare, виньетка |

## 🛠️ НАСТРОЙКА

### Этап 1. Моделирование

```bash
# Case body
"Создай цилиндр 'Case_Body' радиус 0.022м глубина 0.012м вершин 64
 Позиция (0,0,0) материал 'Mat_Metal_Steel'"

# Bezel
"Создай цилиндр 'Bezel' радиус 0.024м глубина 0.003м вершин 64
 Позиция (0,0,0.006) материал 'Mat_Metal_Ceramic'"

# Crystal
"Создай цилиндр 'Crystal' радиус 0.021м глубина 0.004м вершин 64
 Позиция (0,0,0.008) материал 'Mat_Glass_Sapphire'"

# Crown
"Создай цилиндр 'Crown' радиус 0.004м глубина 0.008м вершин 32
 Позиция (0.024, 0, 0.004) материал 'Mat_Metal_Steel'
 Boolean DIFFERENCE для паза"

# Strap (Geometry Nodes)
"Создай плоскость 'Strap_Base' 0.2x0.02м
 GN: Curve to Mesh, профиль 0.004м, материал 'Mat_Leather_Black'
 Array по кривой длиной 0.25м"
```

### Этап 2. UV-развёртка

```bash
# Case body
"Smart Project angle_limit=66 island_margin=0.01"

# Crystal — Cube Projection
"Cube Project clip_to_bounds=True"

# Strap — Follow Active Quads
"Select edge loop → Mark Seam → Unwrap → Follow Active Quads"
```

### Этап 3. Материалы

```bash
# Steel (Case, Crown, Buttons)
"Mat_Metal_Steel:
BaseColor: #B8B8C0, Roughness: 0.15, Metallic: 1.0
Clearcoat: 0.3, ClearcoatRough: 0.05
Anisotropic: 0.3, Tangent: UV
Normal: brushed metal procedural"

# Ceramic Bezel
"Mat_Metal_Ceramic:
BaseColor: #1A1A1A, Roughness: 0.05, Metallic: 0.0
Transmission: 0, Clearcoat: 1.0, ClearcoatRough: 0.01
Normal: subtle ceramic texture"

# Sapphire Crystal
"Mat_Glass_Sapphire:
Transmission: 1.0, IOR: 1.77, Roughness: 0
Clearcoat: 0.5 (AR coating), ClearcoatRough: 0.001
Absorption: slight blue tint at edges"

# Leather Strap
"Mat_Leather_Black:
BaseColor: #0D0D0D, Roughness: 0.85, Metallic: 0
Sheen: 0.15, SheenTint: 0.3
Normal: leather grain procedural
Height: embossed pattern"
```

Зерно металла делается процедурно — это дешевле текстуры и не требует повторяющихся UV:

```python
import bpy, math

def brushed_metal(mat_name, scale=(1.0, 60.0), strength=0.06):
    """Анизотропные царапины: растянутый по одной оси шум + Tangent по UV."""
    mat = bpy.data.materials[mat_name]
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

    tex = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs['Scale'].default_value = scale       # anisotropy = ratio X/Y
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 220.0
    noise.inputs['Detail'].default_value = 4.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = 0.0002

    nt.links.new(tex.outputs['UV'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    a = bsdf.inputs.get('Anisotropic')
    if a:
        a.default_value = 0.3
    t = bsdf.inputs.get('Tangent')
    if t:
        nt.links.new(tex.outputs['UV'], t)

brushed_metal("Mat_Metal_Steel")
```

### Этап 4. Свет

```bash
# HDRI
"Poly Haven 'studio_small_01' 2k, strength=0.3"

# Key Light (Main)
"AREA 1000W, 0.3x0.3м, позиция (0.1, -0.2, 0.15), поворот к часам
 Shape: Rectangle, Spread: 45°"

# Fill Light
"AREA 300W, 0.5x0.5м, позиция (-0.15, 0.1, 0.1), мягкий"

# Rim Light
"AREA 200W, 0.2x0.2м, позиция (0, 0.15, 0.15), контрастный край"

# Accent (Sparkle on Crystal)
"POINT 50W, позиция (0.02, -0.02, 0.02), размер 0"
```

Ключевой к источникам — `spread`: у area-свет есть угол распространения, и его сужение до 30–50° превращает лампу из «заливки всего подряд» в инструмент для конкретной фаски.

```python
import bpy, math

def area_light(name, size, energy, loc, look_at, spread=45.0, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, type='AREA')
    data.shape = 'SQUARE'
    data.size = size                 # в метрах: 0.1 = панель 10 см
    data.energy = energy            # в ваттах, привязано к реальному масштабу
    data.color = color
    if hasattr(data, "spread"):      # доступно не во всех сборках
        data.spread = math.radians(spread)

    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc

    con = ob.constraints.new('TRACK_TO')
    con.target = bpy.data.objects["Case_Body"]
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    return ob

target = bpy.data.objects["Case_Body"]
area_light("Key",  0.30, 1000.0, (0.10, -0.20, 0.15), target, spread=45.0)
area_light("Fill", 0.50,  300.0, (-0.15, 0.10, 0.10), target, spread=90.0)
area_light("Rim",  0.20,  200.0, (0.00,  0.15, 0.15), target, spread=30.0)
```

### Этап 5. Камера

```bash
# Hero Shot
"Cam_Hero: позиция (0, -0.3, 0.05) focal=100mm sensor=36mm
 DOF: focus на циферблат, f-stop=2.8, blades=9
 Composition: Center + Rule of Thirds"

# Detail Shots
"Cam_Dial: (0, -0.15, 0.03) focal=150mm f/2.0 → крупно циферблат
 Cam_Crown: (0.025, 0, 0.005) focal=100mm f/4.0 → коронка
 Cam_Strap: (-0.1, -0.2, 0) focal=85mm f/2.8 → текстура ремня"
```

```python
import bpy

def product_cam(name, loc, lens, fstop, focus="Case_Body", sensor=36.0):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.sensor_width = sensor
    cam.clip_start = 0.005        # предмет 4 см: стандартный 0.1 его срежет
    cam.dof.use_dof = True
    cam.dof.focus_object = bpy.data.objects[focus]
    cam.dof.aperture_fstop = fstop
    cam.dof.aperture_blades = 9   # не круглая диафрагма = блики с гранями

    ob = bpy.data.objects.new(name, cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    return ob

hero = product_cam("Cam_Hero", (0.0, -0.30, 0.05), 100.0, 2.8)
bpy.context.scene.camera = hero
```

### Этап 6. Композитор

```bash
"Passes: Combined, Depth, Normal, Cryptomatte, Mist
 Color: Lift/Gamma/Gain (Teal & Orange), Glare (0.15 threshold),
 Vignette (0.1), Sharpen (Unsharp Mask 0.5),
 Chromatic Aberration (0.002)
 Output: 4K EXR 32-bit + 4K PNG 16-bit"
```

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Металл выглядел как крашеный пластик.** Первый вариант ставил только HDRI с `strength = 0.3` и один заполняющий источник. Логика была «студия = равномерный свет», и в итоге на корпусе не оказалось ни одного читаемого блика: сфера считывалась по цвету, а не по свету, и зритель видел плоскую запятку. Лечится не увеличением общей яркости, а постановкой: узкий key со `spread` около 40° напротив фаски, широкий fill, отдельный rim сзади. Площадь блика на металле должна быть узкой и яркой, а её форма — повторять форму детали.

**2. Ключевой свет стоял в сантиметрах от предмета и всё пересвечивал.** Источник на 1000 Вт на расстоянии 20 см от объекта 4 см — это очень много. Пересвет выедал кромки безеля, а стекло превращалось в белое пятно с ореолом, потому что внутренние грани стекла получали свет со всех сторон. Пришлось увести key на 0.3–0.5 м, урезать энергию и поставить отдельный очень слабый источник для подсветки циферблата изнутри. Урок: при реальном масштабе предмета мощности источников из «метровых» сцен неприменимы напрямую — их надо подбирать заново, и на глаз это не считается.

**3. `clip_start` = 0.1 у макрокамеры.** Камера с фокусным 100 мм в сантиметрах от предмета — это уже макро, и стандартный клиппинг Blender по умолчанию буквально отсёкал переднюю часть коронки. Кадр получался «съеденным» по краям безо всякой видимой причины: ни ошибок, ни предупреждений. Лечится `clip_start` около 0.005, и это надо ставить в самом начале проекта, а не когда рендер уже потратил два часа.

**4. Glare на циферблате испортил читаемость.** Универсальный Bloom в композиторе добавил ореол вокруг стрелок и превратил мелкие детали в кашу. Пришлось ограничить glare только слоем циферблата, понизить порог и отключить его для детальных кадров, где блик на стекле и так должен быть единственным.

## 📊 ЧТО ПОЛУЧИЛОСЬ

**Оценка по порядку величины, конкретных замеров нет:**

- Объектов: ~14 (корпус, безель, стекло, коронка, 2 кнопки, ремень на 2 кривых, 4 источника, камера).
- Полигоны: цилиндры по 32–64 вершины с bevel по 2 сегмента, ремень — Curve to Mesh по кривой. Порядок **20–60 тыс. треугольников** для hero-ракурса.
- Материалов: 4. Текстур **ноль** — всё процедурное (шум + mapping на UV).
- Кадров: 4 (1 hero 1600×1600 + 3 детальных), плюс тестовые прогоны на 640×640 при 32 сэмплах.
- Рендер в Cycles на 512–1024 сэмплах с денойзингом: **десятки минут на кадр** на средней видеокарте. Тестовые превью — секунды.

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| масштаб сцены | реальные габариты (метры) | единственный способ получить верные мощности света и DOF |
| `Key.spread` | 30–45° | уже — блик превращается в точку, шире — в пятно без формы |
| `Key.energy` | подбирается по результату, 200–1000 Вт на метровом расстоянии | после смены масштаба сцены обязательно пересчитать |
| HDRI `strength` | 0.2–0.4 | выше — металл начинает отражать «фотостудию», а не предмет |
| `dof.aperture_fstop` | 2.0–2.8 для макро | меньше — задняя фаска ремня полностью исчезает |
| `dof.aperture_blades` | 7–9 | круглая диафрагма даёт «мыльный» боке вместо огранки |
| `clip_start` | 0.005 | обязательно при работе с предметами меньше 10 см |
| `Mat_Metal_Steel` roughness | 0.12–0.18 | выше — металл теряет отражения и становится серым |
| IOR сапфира | 1.76–1.77 | задаёт силу преломления и толщину каустик на кромке |
| Clearcoat на безеле | 0.9–1.0 | без него керамика не даёт одиночного блика |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Металл похож на пластик | нет узкого яркого блика, только равномерная заливка | key со `spread` 30–45°, отдельный rim |
| Всё пересвечено | мощности источников из метровой сцены на предмете 4 см | отвести источники дальше, пересчитать энергию |
| Края кадра «съедены» без ошибок | `clip_start` 0.1 на макро | `clip_start = 0.005` |
| Стекло — белое пятно | пересвет внутренних граней | уменьшить key, добавить слабый источник внутрь |
| Циферблат в ореоле | грейд/glare по всему кадру | glare только на слое циферблата, порог ниже |
| Ремень «лысый», текстуры нет | UV развёрнут Follow Active Quads и сел на ребро | переразвернуть, проверить масштаб текстуры |
| Детальные кадры мыльные | один f-stop на всех ракурсах | отдельный f-stop для каждого кадра |

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 13: HARD-SURFACE SCI-FI GUN](case_13_hard_surface_gun.md)
- **По темам:** [WF 17: STOP-MOTION FELT LOOK](../workflows/wf_17_stop_motion_felt.md), [P46: UDIM WORKFLOW](../prompts/46_udim_workflow.md), [WF 23: VIRTUAL PRODUCTION LED](../workflows/wf_23_virtual_production_led.md), [WF 24: PHOTOGRAMMETRY CLEANUP](../workflows/wf_24_photogrammetry_cleanup.md)
- **Теги:** #case, #compositing, #lighting, #pipeline, #render, #shading, #texturing