---
id: wf_10_product_turntable
lang: ru
category: workflows
type: workflow
status: full
tags: [product, workflow]
---
# WF 10: PRODUCT TURNTABLE

**ID:** WF-10 | **Type:** Product | **Difficulty:** ⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: 360° turntable 120f, studio HDRI, DOF
EN: 360° turntable 120f, studio HDRI, DOF

На выходе — ровный 360°-облёт товара на белом/нейтральном фоне, пригодный и для
каталога, и для карточки на маркетплейсе. Ключевая сложность не в рендере, а в трёх
вещах, которые обычно и делают turntable плохим: неравномерный шаг вращения (кадры
«дёргаются»), пылающие блики от неудачного HDRI и уход формы к краям кадра из-за
перспективы. Все три лечатся настройкой, а не постом.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | сцена, Cycles |
| HDRI | Poly Haven, 1–2k | отражения на металле/лаке; фон перекрывается |
| Модель товара | GLB/FBX/OBJ | единый меш или набор, вращается целиком |
| GPU | желательно 8+ ГБ VRAM | 256 сэмплов по 1920×1920 |

## 🛠 НАСТРОЙКА

### Этап 1. Сцена: пол и «студийная» среда

```python
import bpy, math

scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 120      # 120 кадров = ровно 5.0 с

# Пол: не зеркало, но и не матовое стекло. Roughness 0.35 даёт мягкое
# «подложное» отражение, на котором товар читается, а не тонет.
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "StudioFloor"
mat = bpy.data.materials.new("Mat_Floor")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.86, 1.0)
bsdf.inputs["Roughness"].default_value = 0.35
floor.data.materials.append(mat)
```

### Этап 2. HDRI в World

```python
world = bpy.data.worlds.new("Studio") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()

env = nt.nodes.new("ShaderNodeTexEnvironment")
bg  = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
# strength низкий: HDRI здесь работает источником отражений, а не светом.
# Основной свет —Area-источники ниже, иначе будет двойное освещение.
bg.inputs["Strength"].default_value = 0.35
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
env.image = bpy.data.images.load("//hdri/studio_small_08_1k.hdr")
env.location = (math.radians(90), 0, math.radians(180))   # свет падает сзади-слева
```

### Этап 3. Три источника: key / fill / rim

```python
def area_light(name, loc, rot, energy, size, size_y=None):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.data.energy = energy
    ob.data.size = size
    if size_y:
        ob.data.shape = 'RECTANGLE'       # узкая полоса = длинный блик на цилиндре
        ob.data.size_y = size_y
    return ob

# key: основной, мягкий, сверху-слева
area_light("Key",  (1.2, -1.6, 1.8), (math.radians(-45), 0, math.radians(35)), 400, 1.5, 1.5)
# fill: в 4 раза слабее, без теней по краям
area_light("Fill", (-1.6, -1.0, 0.9), (math.radians(-70), 0, math.radians(-60)), 100, 2.0)
# rim: узкая полоса сзади, рисует контур против фона
area_light("Rim",  (0.0, 1.8, 1.4), (math.radians(-60), 0, 0), 250, 2.0, 0.35)
```

### Этап 4. Камера и DOF

```python
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# 85 мм — телеобъектив: минимальная перспективная дисторсия, товар «прижат» к кадру
cam_data.lens = 85
cam.location = (0.0, -1.9, 0.32)

# Направить на центр товара. aim — это track-to без лишнего пустого объекта.
import mathutils
direction = mathutils.Vector((0, 0, 0.09)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (mathutils.Vector((0, 0, 0.09)) - cam.location).length
cam_data.dof.aperture_fstop = 8.0        # f/8 — лёгкое размытие только по краям
```

### Этап 5. Вращение — драйвер, а не keyframe

Keyframe с интерполяцией даёт рывки на стыке и требует ручной правки easing. Драйвер
от `frame` даёт идеально линейный, математически бесшовный оборот.

```python
pivot = bpy.data.objects.new("Turntable", None)     # пустой — точка вращения
scene.collection.objects.link(pivot)
for ob in bpy.data.objects:
    if ob.type == 'MESH' and ob is not pivot:
        ob.parent = pivot

d = pivot.driver_add("rotation_euler", 2).driver
d.type = 'SCRIPTED'
d.expression = "2*pi*frame/120"     # 3° на кадр, кадр 121 ≡ кадр 1 → шва нет
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `frame_end` | 120 | 90 кадров = 4°/кадр (быстрее), 240 = 1.5°/кадр (плавнее) |
| `render.fps` | 24 | 30 → 4 с при тех же 120 кадрах |
| `cycles.samples` | 256 | 128 для превью, 512 для глянца |
| `view_settings.view_transform` | `'AgX'` | `'Filmic'` в версиях до 4.0 |
| `dof.aperture_fstop` | 8.0 | меньше — сильнее размытие краёв |

```python
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 256
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'

# Разрешение под карточку товара — квадрат
scene.render.resolution_x = scene.render.resolution_y = 1920
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '16'     # 16 бит — потом не жалко сводить в монтаже
scene.render.filepath = "//render/turntable_"
bpy.ops.render.render(animation=True)

# Сборка в видео
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.filepath = "//render/turntable.mp4"
bpy.ops.render.render(animation=True)
```

> [!NOTE]
> Идентификаторы в `view_transform` зависят от версии: `AgX` появился в Blender 4.0,
> до этого был `Filmic`. Если присваивание падает с TypeError — перечисли доступные
> значения `[i.identifier for i in scene.view_settings.bl_rna.properties['view_transform'].enum_items]`.

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Объём | 120 кадров × 3° = полный оборот, 5 с при 24 fps |
| Файлы | `turntable_0001.png … turntable_0120.png` (16 бит) + `turntable.mp4` |
| Разрешение | 1920 × 1920 (квадрат под карточку) |
| Шов | нет: кадр 121 математически совпадает с кадром 1 |
| Рендер | ~1.5–4 с/кадр на GPU среднего класса → **3–8 минут** на 120 кадров |

Побочный, но полезный выход: `.blend` с драйвером и тремя источниками — это же
заготовка для WF 26 (LOOKDEV TURNTABLE LAB), где тот же риг крутится для подбора
материала.

## ✅ QA перед сдачей

Ротация «проходит» в трёх местах, и все три ловятся глазом на нескольких кадрах:
момент, когда товар стоит боком (виден самый толстый блик), момент с отражением в
полу, и момент, когда блик уходит за контур силуэта. Если блик не «съезжает» с
изделия между кадрами — свет стоит слишком широко или HDRI слишком мягкий.

```python
import bpy, glob

# Контрольный скрипт: все кадры на месте, ни один не чёрный
out = sorted(glob.glob("//render/turntable_*.png"))
missing = [i for i in range(1, 121) if f"turntable_{i:04d}.png" not in out]
print("кадров:", len(out), "| пропущено:", missing)

for path in out[::20]:                      # каждый 20-й, а не все 120
    img = bpy.data.images.load(path)
    px = list(img.pixels[:4000])            # угол кадра: там всегда фон
    if max(px) < 0.02:
        print("ПУСТОЙ/ЧЁРНЫЙ:", path)
```

Второй контрольный скрипт — про сам риг, а не про файлы. Он ловит две поломки, которых
не видно на превью: ключи поверх драйвера (тогда шаг не постоянен) и незамкнутый оборот
(тогда стык всплывёт при сведении). Заодно печатает реальную стоимость геометрии — это и
есть то, из чего складывается время рендера.

```python
import bpy, math, glob, os

scene = bpy.context.scene
pivot = bpy.data.objects["Turntable"]
prod  = next(o for o in scene.objects if o.type == 'MESH' and o.name != "StudioFloor")

# 1. Пять СОСЕДНИХ кадров должны дать пять одинаковых приращений
seq = []
for f in range(1, 6):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    seq.append(pivot.rotation_euler.z)
steps = [round(b - a, 6) for a, b in zip(seq, seq[1:])]
print("шаг/кадр, рад:", steps, "| шагов:", len(steps))

# 2. Замкнутость: за frame_end кадров должно набежать ровно 2*pi
scene.frame_set(scene.frame_end + 1)
bpy.context.view_layer.update()
sweep = pivot.rotation_euler.z - seq[0]
print("оборот за", scene.frame_end, "кадров, рад:", round(sweep, 6),
      "| 2*pi =", round(2 * math.pi, 6))

# 3. Полигоны против треугольников: считает движок вторые, поэтому
#    calc_loop_triangles() — честная мера тяжести сцены
me = prod.data
me.calc_loop_triangles()
print(prod.name, "| вершин:", len(me.vertices),
      "| полигонов:", len(me.polygons),
      "| треугольников:", len(me.loop_triangles))

# 4. Кадры на диске
files = sorted(glob.glob(os.path.join(bpy.path.abspath("//render"), "turntable_*.png")))
print("кадров на диске:", len(files), "| ожидалось:", scene.frame_end)
```

Если шаги не равны — в сцене остались keyframe поверх драйвера. Если `sweep` меньше `2*pi` —
в выражении стоит не тот знаменатель: должно быть `2*pi*frame/120` при 120 кадрах, а не
`2*pi*frame/24`. Расхождение треугольников и полигонов (968 против 500 на monkey Suzanne)
нормально: n-угольник — это n−2 треугольника, и движок раскладывает так всю геометрию.

Проверка на стыке цикла: открой кадры `turntable_0001.png` и `turntable_0120.png`
рядом. Между ними должен быть ровно один шаг (3°) — такой же, как между 0001 и 0002.
Если между ними заметный «перескок», в сцене остались keyframe поверх драйвера.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Товар «прыгает» в кадре по высоте | пивот не в центре масс, сетка смещена по Z | совмести центр `pivot` с центром габаритов: `bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')` |
| Стык дёргается | keyframe-анимация с easing вместо драйвера | заменить на `driver` с выражением `2*pi*frame/N` |
| Пятна на металле | HDRI со «съеденными» деталями в отражении | взять HDRI с резкими источниками, снизить `Strength` до 0.3 |
| Товар обрезан по краям | камера слишком близко | отдали камеру или уменьши `lens` |
| Блик полоской по всему изделию | источник слишком узкий и яркий | увеличить `size`, снизить `energy`, добавить fill |
| Тёмные углы, плоская картинка | `world` с пустым `Background` вместо HDRI | проверь, что `env.image` назначен и `Strength > 0` |
| Размыто всё, а не только края | слишком малое расстояние фокуса | `focus_distance` = расстояние до центра товара, `fstop` ≥ 5.6 |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 26: LOOKDEV TURNTABLE LAB](wf_26_lookdev_turntable_lab.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md)
- **По темам:** [CASE 10: SNEAKER PRODUCT HERO](../cases/case_10_sneaker_product.md), [CASE 14: FOOD RENDER (RAMEN)](../cases/case_14_food_r visualisation.md), [CASE 15: CAR STUDIO CINEMATIC](../cases/case_15_car_studio_cinematic.md), [P50: PORTFOLIO TURNTABLE & QA](../prompts/50_turntable_qa.md)
- **Теги:** #product, #workflow