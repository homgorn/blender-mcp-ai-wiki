---
id: wf_22_dataviz_3d_charts
lang: ru
category: workflows
type: workflow
status: full
tags: [dataviz, workflow]
---
# WF 22: DATAVIZ 3D CHARTS

**ID:** WF-22 | **Type:** Info | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда заказчик просит «красивые 3D-столбики» из CSV: демо-график, презентационный ролик, экран для лобби. Сознание о том, что 3D искажает сравнение длин, здесь — часть работы, а не формальность.

## 🎯 ЦЕЛЬ

Из CSV получается 3D-столбчатая диаграмма: столбцы по одной на строку, высота пропорциональна значению, цвет кодирует ту же величину, снизу подписи категорий, камера делает медленный облёт.

Первое, что нужно сказать честно: **3D-график хуже читается, чем плоский**. Перспектива сокращает дальние столбцы, и глаз сравнивает не длину, а площадь и положение. Если 3D обязателен (обычно это требование маркетинга, а не аналитика), компенсируй: ортогональная камера убирает перспективное сокращение, монотонная светлота палитры даёт порядок, а числовые подписи снимают задачу сравнения с глазу.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | базовый | сцена и рендер |
| CSV-файл | разделитель `;` или `,`, кодировка UTF-8 | данные |
| Модуль `csv` | входит в Python внутри Blender | разбор без внешних пакетов |
| Модуль `numpy` | входит в поставку Blender, но в коде ниже не нужен | — |
| Шрифт для подписей | встроенный Bfont достаточно | читаемость |

> [!NOTE]
> Не используй pandas: его нет в стандартной поставке Blender, и если он не установлен через pip в интерпретатор Blender, скрипт упадёт. `csv`, `json`, `math`, `random` — стандартные, работают всегда.

## 🛠️ НАСТРОЙКА

### Этап 1. Прочитать данные

```bash
RU: "Построй 3D-столбчатую диаграмму из //data/sales.csv:
     столбцы по месяцам, высота = выручка, цвет по тем же значениям,
     подписи снизу, камера — ортогональная, медленный облёт"
EN: "Build a 3D bar chart from //data/sales.csv:
     one bar per month, height = revenue, color by the same value,
     labels below, camera orthographic, slow orbit"
```

```python
import csv, os
path = bpy.path.abspath("//data/sales.csv")
rows = []
with open(path, newline='', encoding='utf-8') as fh:
    for r in csv.DictReader(fh, delimiter=','):
        rows.append((r['month'].strip(), float(r['revenue'].replace(' ', ''))))

if not rows:
    raise SystemExit("CSV пуст или нет заголовков month/revenue")

values = [v for _, v in rows]
vmin, vmax = min(values), max(values)
print(f"строк: {len(rows)}, диапазон: {vmin:.0f}..{vmax:.0f}")
```

### Этап 2. Построить столбцы

Столбцы строятся из одного «прототипа», который затем множится — так дешевле, чем создавать каждый отдельно, и вся группа остаётся одной сущностью.

```python
import bpy, math
from mathutils import Vector

BAR_W, BAR_D, GAP, MAX_H = 0.6, 0.6, 0.25, 4.0
values_max = max(values) or 1.0

def box_mesh(w, d, h, cx, cy):
    """Единичный параллелепипед с центром в основании — так проще масштабировать по Y."""
    hw, hd = w / 2, d / 2
    v = [(-hw, -hd, 0), (hw, -hd, 0), (hw, hd, 0), (-hw, hd, 0),
         (-hw, -hd, h), (hw, -hd, h), (hw, hd, h), (-hw, hd, h)]
    f = [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    me = bpy.data.meshes.new("BarMesh")
    me.from_pydata(v, [], f)
    me.update()
    return me

bars = []
x = 0.0
for i, (label, value) in enumerate(rows):
    h = MAX_H * value / values_max
    ob = bpy.data.objects.new(f"Bar_{i:02d}_{label}", box_mesh(BAR_W, BAR_D, h, x, 0))
    ob.location = (x, 0, 0)
    bpy.context.collection.objects.link(ob)
    # offset в custom property -> Object Info Random в шейдере (см. этап 3)
    ob["v_norm"] = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    bars.append((ob, label, value))
    x += BAR_W + GAP

bpy.ops.object.select_all(action='DESELECT')
for ob, _, _ in bars: ob.select_set(True)
bpy.context.view_layer.objects.active = bars[0][0]
bpy.ops.object.join()      # все столбцы — один объект, но с сохранёнными пропорциями
```

> [!NOTE]
> После `join()` все столбцы — одна геометрия, и `Object Info → Random` вернёт одно и то же число на весь объект. Поэтому цвет по значению надо раздавать **до** join: крась по вершинам (attribute), либо вообще не join'ить. Здесь join сделан только ради удобства трансформации — если нужен цвет по значению, оставь столбцы отдельными объектами.

### Этап 3. Цвет по значению

Через `Object Info → Random` столбцы красятся сами: `Random` у каждого объекта стабильное число 0..1, ColorRamp с монотонной светлотой даёт читаемый порядок.

```python
import bpy
mat = bpy.data.materials.new("Mat_Data")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs['Roughness'].default_value = 0.45

oi = nt.nodes.new("ShaderNodeObjectInfo")
ramp = nt.nodes.new("ShaderNodeValToRGB")
cr = ramp.color_ramp
cr.interpolation = 'LINEAR'
cr.elements[0].position = 0.0
cr.elements[0].color = (0.05, 0.16, 0.30, 1)      # тёмно-синий: мало
cr.elements[1].position = 1.0
cr.elements[1].color = (0.95, 0.55, 0.18, 1)      # оранжевый: много
# средний стоп светлее обоих краёв -> порядок читается и по светлоте
mid = cr.elements.new(0.5); mid.color = (0.30, 0.52, 0.58, 1)

nt.links.new(oi.outputs["Random"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

for ob, _, _ in bars:
    ob.data.materials.append(mat)
```

Если всё-таки нужен цвет при join'е — пиши в вершинный атрибут до объединения:

```python
# по нижней грани столбца читаем z его вершины -> нормированное значение
for ob, label, value in bars:
    t = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    attr = ob.data.attributes.new(name="val", type='FLOAT', domain='POINT')
    for d in attr.data:
        d.value = t
    # в шейдере вместо ObjectInfo.Random: Attribute(attribute_name="val")
```

### Этап 4. Подписи категорий

Подписи всегда ставятся в плоскости кадры и всегда с числами: если график 3D, читатель обязан иметь возможность сверить глазом.

```python
import bpy
cam = bpy.data.objects["Cam_Chart"]
labels = []
for i, (ob, label, value) in enumerate(bars):
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.name = f"Lbl_{label}"
    t.data.body = f"{label}\n{value:,.0f}".replace(",", " ")   # разделитель тысяч принято ставить пробелом
    t.data.align_x = 'CENTER'
    t.data.size = 0.22
    t.data.extrude = 0.0
    t.location = (ob.location.x, -0.75, 0.0)
    c = t.constraints.new('TRACK_TO')
    c.target = cam; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    labels.append(t)
```

### Этап 5. Ось и сетка

```python
import bpy
axis_mat = bpy.data.materials.new("Mat_Axis")
axis_mat.use_nodes = True
nt = axis_mat.node_tree
b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
b.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1)
b.inputs['Roughness'].default_value = 0.7

extent = (len(bars) * (BAR_W + GAP)) + 1.0
for name, loc, dims in (("Axis_X", (extent/2 - GAP/2, -0.45, 0), (extent, 0.02, 0.02)),
                        ("Axis_Y", (extent/2 - GAP/2,  0.0, 0), (extent, 0.02, 0.02))):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = (dims[0], dims[1], dims[2])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(axis_mat)
```

### Этап 6. Камера и облёт

Для 3D-графика ортогональная камера — не упрощение, а условие читаемости: она убирает перспективное сокращение, из-за которого дальние столбцы кажутся короче.

```python
import bpy, math
bpy.ops.object.camera_add(location=(0, -14, 5.2), rotation=(math.radians(68), 0, 0))
cam = bpy.context.active_object; cam.name = "Cam_Chart"
cam.data.type = 'ORTHO'
cam.data.ortho_scale = len(bars) * (BAR_W + GAP) + 1.5
bpy.context.scene.camera = cam

# медленный облёт: дуга в 40 кадров и обратно
bpy.ops.curve.primitive_bezier_curve_add(location=(0, -14, 5.2), radius=8.0)
path = bpy.context.active_object
for p in path.data.splines[0].bezier_points:
    p.handle_left_type = p.handle_right_type = 'AUTO'

con = cam.constraints.new('FOLLOW_PATH')
con.target = path
con.use_fixed_location = True
for frame, off in ((1, 0.0), (40, 0.5), (80, 0.0)):
    con.offset_factor = off
    con.keyframe_insert(data_path="offset_factor", frame=frame)

sc = bpy.context.scene
sc.frame_start, sc.frame_end, sc.frame_set = 1, 80, 1
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `camera.data.type` | `'ORTHO'` для диаграмм | перспектива допустима только для «рекламного» кадра |
| `ortho_scale` | ширина графика + запас | подгоняется под число столбцов |
| `ColorRamp` палитра | монотонная светлота | цветом кодируется порядок, а не категория |
| `MAX_H` | 3–5 м | при коротких столбцах подписи наезжают |
| `GAP` | 0.2–0.35 от ширины столбца | меньше — сливается, больше — теряется связь |
| `view_transform` | `'Standard'` | для графика: AgX/Filmic сжимают контраст и врут в контрасте палитры |

> [!NOTE]
> Список значений `view_settings.view_transform` зависит от версии и включённых OCIO-конфигов: встречаются `Standard`, `Filmic`, `AgX`, `Raw`, `False Color`. Прочитай доступные у себя так: `[i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]`.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Все столбцы одного цвета | `join()` слил столбцы, `Object Info → Random` дал одно число | красить до join либо использовать вершинный атрибут |
| CSV читается, но `KeyError: 'month'` | разделитель `;` при `delimiter=','` | подобрать `delimiter` под файл |
| `OverflowError` при `float()` | в значении пробелы, запятые или неразрывный пробел | чистить строку (`replace`, `strip`) до `float` |
| Дальние столбцы «короче» | перспективная камера | `ortho` + увеличение ракурса сверху |
| Подписи не читаются | они не в фокальной плоскости и не в кадре | `TRACK_TO` на камеру, вынести вперёд по Y |
| Цвета «не тем» на финальном кадре | `AgX`/`Filmic` сжали контраст | для проверки палитры рендерить с `view_transform='Standard'` |

## ✅ РЕЗУЛЬТАТ

На выходе: сцена со столбцами, осями и подписями, плюс 80 кадров 1920×1080 облёта (рендер одного кадра — основной результат; 80 кадров нужны только если делается ролик).

Характеристики — **оценка по порядку величины, а не измеренный результат**: 12 столбцов по 12 треугольников на столбец — единицы сотен треугольников на всю диаграмму, один материал столбцов + один материал осей, ноль текстур (подписи — геометрия текста, а не текстура). Один кадр 1920×1080 в Cycles, 64 сэмпла — секунды; в EEVEE — доли секунды. Восемьдесят кадров — от десятков секунд до нескольких минут.

**Это оценка.** Точное время зависит от числа объектов в сцене и железа; измеряй у себя.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md), [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md)
- **По темам:** [WF 06: ARCHVIZ WORKFLOW](wf_06_archviz_workflow.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md), [WF 08: BATCH PROCESSING](wf_08_batch_processing.md)
- **Теги:** #dataviz, #workflow