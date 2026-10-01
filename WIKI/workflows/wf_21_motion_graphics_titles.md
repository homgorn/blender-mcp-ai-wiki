---
id: wf_21_motion_graphics_titles
lang: ru
category: workflows
type: workflow
status: full
tags: [motion, workflow]
---
# WF 21: MOTION GRAPHICS TITLES

**ID:** WF-21 | **Type:** MoGraph | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужны заставки, логотипы, нижние трети и бегущие строки — текст и простые формы, которые живут 1–5 секунд и должны выглядеть отрендеренными, а не «дефолтными».

## 🎯 ЦЕЛЬ

Текстовый объект превращается в анимированную заставку: движение по кривой, появление по буквам, затухание, зацикливание — и всё это рендерится с прозрачным фоном, чтобы накладываться поверх видео.

Главная специфика моушн-графики по сравнению с 3D-сценой: **результат всегда временной**. Значит, главные настройки — это кадровая сетка (`fps`, длительность), тип интерполяции между ключами и то, чтобы первый и последний кадр совпали, если ролик зацикливается.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | версия с Curve Modifier и F-кривыми | основа |
| Шрифт | `.ttf`/`.otf`, желательно с кириллицей | сам текст; системные шрифты выглядят случайно |
| Кривая (Bezier) | создаётся в сцене | траектория движения |
| Композитор | встроенный, Alpha Over | склейка слоёв и прозрачность |
| VSE | встроенный | обрезка по таймингу, проверка цикла |
| Стартовый файл кадров | — | экспорт анимации |

> [!NOTE]
> Имена сокетов нод compositor (в частности у `Alpha Over`) различаются между версиями: где-то входы называются `Image`, `Image.001`, где-то `Background`/`Foreground`. Ниже код использует порядок входов и явные имена с проверкой — если имя не нашлось, код упадёт с понятной ошибкой, а не сделает тихо не то.

## 🛠️ НАСТРОЙКА

### Этап 1. Кадровая сетка

Всё дальше — в кадрах, не в секундах. Частая ошибка: анимировать в секундах при `fps = 24` и получать сдвиг на треть длительности.

```bash
RU: "Моушн-графика: 24 fps, длительность 2 секунды (48 кадров),
     рендер с прозрачным фоном, кадры в //renders/titles/"
EN: "Motion graphics: 24 fps, 2 s duration (48 frames),
     transparent film, frames to //renders/titles/"
```

```python
import bpy
sc = bpy.context.scene
FPS, SECONDS = 24, 2.0
sc.render.fps = FPS
sc.frame_start = 1
sc.frame_end = int(FPS * SECONDS)      # 48 кадров при 24 fps и 2 секундах
sc.frame_set(sc.frame_start)

for name, at in (("appear", 0.10), ("settle", 0.45), ("hold", 1.60), ("exit", 1.90)):
    sc.timeline_markers.new(name, frame=int(at * FPS))
print("кадров:", sc.frame_end, "маркеров:", len(sc.timeline_markers))
```

### Этап 2. Текст: объём, форма, ритм

```python
import bpy
bpy.ops.object.text_add(location=(0, 0, 0))
txt = bpy.context.active_object
txt.name = "Title_Text"
td = txt.data
td.body = "BLENDER AI"
td.align_x = 'CENTER'
td.align_y = 'CENTER'
td.size = 0.6
td.extrude = 0.03          # глубина букв
td.bevel_depth = 0.006     # скругление кромки — ключ к «премиальному» виду
td.bevel_resolution = 3
td.space_character = 1.05  # трекинг: 1.0 = по умолчанию шрифта
td.resolution_u = 8        # больше = глаже кривые букв
td.materials.append(bpy.data.materials["Mat_Title"])
```

### Этап 3. Движение по кривой

Кривая + `Follow Path` — надёжнее, чем ключевые кадры на каждом объекте: траекторию можно править интерактивно, а текст остаётся одним объектом.

```python
import bpy, math
# дуга, по которой проезжает заголовок
bpy.ops.curve.primitive_bezier_curve_add(radius=4.0, location=(0, 0, 0))
path = bpy.context.active_object
path.name = "Path_Title"
path.data.dimensions = '3D'

con = txt.constraints.new('FOLLOW_PATH')
con.target = path
con.use_curve_follow = True      # объект поворачивается по касательной, а не едет боком
con.forward_axis = 'FORWARD_Y'
con.up_axis = 'UP_Z'
con.use_fixed_location = True

# появляется на 15% пути, уезжает на 100%
for frame, off in ((1, 0.0), (7, 0.15), (40, 0.92), (48, 1.0)):
    con.offset_factor = off
    con.keyframe_insert(data_path="offset_factor", frame=frame)
```

### Этап 4. Появление по буквам

Встроенного «выводить текст по буквам» у текстового объекта нет — текст появляется целиком. Два рабочих способа: дублировать по букве со сдвигом, либо обрезать кривую (Trim Curve в Geometry Nodes). Первый способ предсказуем и его видно на любой версии.

```python
import bpy
src = bpy.data.objects["Title_Text"]
src_body = src.data.body

# убираем оригинал, делаем по объекту на букву
bpy.data.objects.remove(src, do_unlink=True)
letters = []
for i, ch in enumerate(src_body):
    if ch == " ":
        continue
    bpy.ops.object.text_add(location=(0, 0, 0))
    ob = bpy.context.active_object
    ob.name = f"Ch_{i:02d}_{ch}"
    ob.data.body = ch
    ob.data.align_x = 'CENTER'
    ob.data.align_y = 'CENTER'
    ob.data.size = 0.6
    ob.data.extrude = 0.03
    ob.data.materials.append(bpy.data.materials["Mat_Title"])
    letters.append((i, ob))

STAGGER = 1.5          # кадров между буквами
for i, ob in letters:
    start = 4 + i * STAGGER
    ob.location = (0, 0, -1.2)                     # из-под маски
    ob.keyframe_insert(data_path="location", frame=1)
    ob.location = (0, 0, 0.0)
    for f, v in ((start, -1.2), (start + 6, 0.0)):
        ob.location.z = v
        ob.keyframe_insert(data_path="location", frame=f)
```

> [!NOTE]
> Более чистый вариант — одна кривая вместо 10 объектов, обрезанная нодой `Trim Curve` в Geometry Nodes с параметром Factor. Идентификатор ноды и набор входов (`Curve`, `Start`, `End`, режим `FACTOR`/`LENGTH`/`SPLINE`) менялись между версиями — проверь в поиске нод на своей версии.

### Этап 5. Интерполяция и easing

Дефолтный Bezier даёт «резиновое» движение. Для заставок обычно хотят резкий вход (back/out) и мягкое торможение.

```python
import bpy
act = bpy.data.objects["Title_Text"].animation_data.action
# В Blender 4.4+ действия стали слотамистыми: act.fcurves может быть пустым,
# тогда F-кривые лежат в act.layers[..].strips[..].channelbag(slot).fcurves.
fcurves = list(getattr(act, "fcurves", []))
if not fcurves and hasattr(act, "layers"):
    slot = bpy.data.objects["Title_Text"].animation_data.action_slot
    for layer in act.layers:
        for strip in layer.strips:
            cb = strip.channelbag(slot)
            if cb: fcurves.extend(cb.fcurves)

for fc in fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
        kp.easing = 'EASE_OUT'
        kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'   # без перелётов
    fc.update()
```

> [!NOTE]
> Значения `kp.easing` и набор `easing_property` зависят от версии: список (AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT, LINEAR, CONSTANT, QUAD, CUBIC, BACK, BOUNCE, ELASTIC, SINE…) приводится по одной версии и менялся. Если поле называется иначе — открой F-Curve в редакторе и выбери руками.

### Этап 6. Склейка и прозрачный вывод

```python
import bpy
sc = bpy.context.scene
sc.render.film_transparent = True       # альфа-канал в PNG 16-bit или EXR
sc.use_nodes = True
nt = sc.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)

rl = nt.nodes.new("CompositorNodeRLayers")
ao = nt.nodes.new("CompositorNodeAlphaOver")
comp = nt.nodes.new("CompositorNodeComposite")

# входы Alpha Over: [0]=Fac, [1]=нижний слой, [2]=верхний слой
ao.inputs[0].default_value = 1.0
nt.links.new(rl.outputs["Image"], ao.inputs[1])
nt.links.new(rl.outputs["Alpha"], ao.inputs[2])
nt.links.new(ao.outputs["Image"], comp.inputs["Image"])
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `render.fps` | 24 / 25 / 30 | под требования площадки |
| `frame_end` | `fps × секунды` | длина ролика |
| `bevel_depth` | 0.004–0.01 от `size` | больше — «резиновый» пластик, меньше — плоская печать |
| `space_character` | 0.95–1.15 | трекинг: ниже 0.9 текст слипается, выше 1.3 разваливается |
| `Follow Path.offset_factor` | 0 → 1 | 1 = конец пути, а не «длина» |
| `use_curve_follow` | `True` | объект доворачивается по касательной |
| `interpolation` | `'BEZIER'` | `'LINEAR'` для механических проездов, `'CONSTANT'` для ступеней |
| `film_transparent` | `True` | для наложения поверх видео |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Текст целиком, без появления по буквам | у Text-объекта нет пер-буквенной анимации | дублировать по буквам со сдвигом либо Trim Curve в GN |
| Анимация «на полкадра позади» | считали секунды при `fps=24` | пересчитать всё в кадры: `frames = seconds × fps` |
| Движение с перелётом, значение улетает за пределы | `AUTO_CLAMPED` не задан | `handle_left_type = handle_right_type = 'AUTO_CLAMPED'` |
| `action.fcurves` пуст | версия 4.4+ со слотистыми действиями | брать F-кривые из `act.layers[..].strips[..].channelbag(slot)` |
| Цикл дёргается на стыке | кадр 1 и кадр N не совпадают | сделать `frame_end = N`, а последний кадр сдвинуть на один назад, либо F-кривая должна иметь период ровно `N-1` |
| При переносе в монтажку фон чёрный | `film_transparent` выключен | включить и сохранять PNG 16-bit / EXR с альфой |
| Шрифт выглядит «не тем» | системный шрифт без нужного начертания | подключить свой `.ttf` в `Preferences → File Paths → Fonts` |

## ✅ РЕЗУЛЬТАТ

На выходе: 48 кадров 1920×1080 (или под требуемое соотношение) с прозрачным фоном — PNG 16-bit с альфой либо EXR, плюс `.blend` с одним текстовым объектом (или набором букв) и кривой-траекторией.

Характеристики — **оценка по порядку величины**: сцена из 10 текстовых объектов с экструзией и bevel — единицы тысяч треугольников, один материал, ноль текстур. Рендер 48 кадров 1920×1080 в Cycles на 64 сэмплах — секунды на кадр, то есть десятки секунд на весь ролик; в EEVEE — доли секунды на кадр. Объём PNG 16-bit с альфой — десятки мегабайт на 48 кадров.

**Это оценка, а не измеренный результат.** Реальное время зависит от разрешения, сэмплов, наличия DOF/motion blur и железа. Движение (motion blur) включается в рендере, но конкретные свойства blur в разных версиях лежат в разных местах — проверь в `Render Properties` своей версии, а не по этому тексту.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 28: LOCALIZATION TITLES](wf_28_localization_dub_titles.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md)
- **По темам:** [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md), [WF 06: ARCHVIZ WORKFLOW](wf_06_archviz_workflow.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md)
- **Теги:** #motion, #workflow