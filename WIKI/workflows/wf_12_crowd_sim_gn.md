---
id: wf_12_crowd_sim_gn
lang: ru
category: workflows
type: workflow
status: full
tags: [geometry-nodes, simulation, workflow]
---
# WF 12: CROWD SIM GN

**ID:** WF-12 | **Type:** Simulation | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: GN points+instances, avoidance, LOD
EN: GN points+instances, avoidance, LOD

Толпа из сотен и тысяч агентов, которые идут по сцене, не наезжая друг на друга, при
60 fps во вьюпорте и при этом не съедают память. Реальный путь здесь один: **не**
объекты с физикой, а точки + инстансы в Geometry Nodes. Тысяча объектов — это тысяча
итераций зависимостей и провал по времени кадра; тысяча инстансов — это один вызов
 отрисовки.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.0+ | интерфейс нод через `node_group.interface` |
| Geometry Nodes | встроенный | вся логика толпы |
| Коллекция с мешами агента | `bpy.data.collections` | источник инстансов |
| Коллекция `LOD_High` / `LOD_Low` | — | два уровня детализации |

> [!NOTE]
> API интерфейса нодового дерева сменился в Blender 4.0: вместо `group.inputs.new(...)` /
> `group.outputs.new(...)` используется `group.interface.new_socket(...)`. Если пишешь
> под 3.x — проверь по руководству своей версии, старые вызовы падают.

## 🛠 НАСТРОЙКА

### Этап 1. Каркас: группа нод и выход

```python
import bpy

ground = bpy.data.objects["Ground"]
mod = ground.modifiers.new("Crowd", 'NODES')

ng = bpy.data.node_groups.new("CrowdGN", 'GeometryNodeTree')
mod.node_group = ng

# Blender 4.0+ — интерфейс создаётся явно. Без выхода дерево не запустится.
ng.interface.new_socket(name="Geometry", in_out='INPUT',  socket_type='NodeSocketGeometry')
ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
gin  = ng.nodes.new("NodeGroupInput");  gin.location  = (-800, 0)
gout = ng.nodes.new("NodeGroupOutput"); gout.location = (1200, 0)

# Удобный хелпер: нода + линк одной строкой
def add(idname, x, y, **props):
    n = ng.nodes.new(idname)
    n.location = (x, y)
    for k, v in props.items():
        setattr(n, k, v)
    return n

def link(a, sa, b, sb):
    return ng.links.new(a.outputs[sa], b.inputs[sb])
```

### Этап 2. Точки на полу с «слепыми зонами»

```python
dist = add("GeometryNodeDistributePointsOnFaces", -500, 0)
dist.distribute_method = 'POISSON'          # равномернее, чем RANDOM, и быстрее рендерится
dist.inputs["Density"].default_value = 0.8  # точек на м²

# Слепые зоны: Delete Geometry по маске «точка попала в камеру/в стену»
delete = add("GeometryNodeDeleteGeometry", -200, -250)
delete.domain = 'POINT'
delete.mode = 'ALL'
link(gin,  "Geometry",     dist,   "Mesh")
link(dist, "Points",       delete, "Geometry")
```

Маска «не ставить людей в этих зонах» делается отдельной нодой
`GeometryNodeProximity` (входы `Target` и `Source Position`, выход `Distance`) плюс
`Math (Less Than)` — то есть расстояние до объекта-исключения меньше порога ⇒ удалить.
Тот же приём оставляет «коридор» для прохода и пустое пятно перед камерой.

### Этап 3. Два уровня детализации

```python
col_hi = add("GeometryNodeCollectionInfo", -200,  250)
col_hi.transform_space = 'ORIGINAL'
col_hi.inputs["Collection"].default_value = bpy.data.collections["LOD_High"]
col_hi.inputs["Separate Children"].default_value = True

col_lo = add("GeometryNodeCollectionInfo", -200,  -50)
col_lo.transform_space = 'ORIGINAL'
col_lo.inputs["Collection"].default_value = bpy.data.collections["LOD_Low"]
col_lo.inputs["Separate Children"].default_value = True

# Первые N индексов — дорогой меш, остальные — дешёвый силуэт
idx   = add("GeometryNodeInputIndex", -200, 400)
cmp   = add("ShaderNodeMath", 0, 400, operation='LESS_THAN')
cmp.inputs[1].default_value = 150           # порог близости, подбирай на глаз
link(idx, "Index", cmp, "Value")

lod = add("GeometryNodeSwitch", 200, 150, input_type='GEOMETRY')
link(cmp, "Value", lod, "Switch")
link(col_lo, "Instances", lod, "False")
link(col_hi, "Instances", lod, "True")
```

### Этап 4. Движение по траектории — без кэша

Ключ ко всему: `Scene Time` даёт секунды, умноженные на скорость, дают позицию вдоль
кривой. Это детерминированно, считается за кадр и не требует запекания.

```python
curve = add("GeometryNodeCurveToPoints", -500, -500)
curve.inputs["Count"].default_value = 400
resample = add("GeometryNodeResampleCurve", -300, -500)
resample.mode = 'COUNT'
resample.inputs["Count"].default_value = 400
link(gin, "Geometry", resample, "Curve")

t    = add("GeometryNodeInputSceneTime", -500, -700)
mul  = add("ShaderNodeMath", -300, -700, operation='MULTIPLY')
mul.inputs[1].default_value = 0.6           # скорость «единиц кривой в секунду»
frac = add("ShaderNodeMath", -100, -700, operation='WRAP')
frac.inputs[1].default_value = 1.0          # бесшовность: ходим по кругу
link(t, "Seconds", mul, "Value")
link(mul, "Value", frac, "Value")

# инстансы двигаем Set Position вдоль оси Y, а поворот ставим через tangent
setpos = add("GeometryNodeSetPosition", 600, 0)
setpos.inputs["Selection"].default_value = True
```

### Этап 5. Инстансы

```python
inst = add("GeometryNodeInstanceOnPoints", 850, 0)
link(delete, "Geometry", inst, "Points")
link(lod,    "Output",   inst, "Instance")
link(resample, "Mesh",   inst, "Rotation")   # Rotation-порт принимает и вектор, и поле
link(setpos,  "Geometry", gout, "Geometry")

# Разброс по высоте/повороту, чтобы толпа не была «сеткой»
rnd = add("FunctionNodeRandomValue", 400, -400, data_type='FLOAT_VECTOR')
rnd.inputs["Min"].default_value = (-0.02, 0.0, -0.02)
rnd.inputs["Max"].default_value = ( 0.02, 0.0,  0.02)
link(rnd, "Value", inst, "Scale")
```

### Этап 6. Производительность и проверка

```python
# Тени от инстансов — самая дорогая часть; если не нужны, гасим на объекте
ground.visible_shadow = False

# Счётчик агентов в сцене — единственный честный способ проверить «сколько людей»
bpy.context.view_layer.update()
def count_points(obj, gname):
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    for m in ev.modifiers:
        if m.name == gname:
            return len(m.evaluated_get(bpy.data.meshes.new("tmp")))
    return 0
```

> [!NOTE]
> Точный способ достать количество точек из модификатора зависит от того, где стоит
> Realize Instances. Практичный вариант для QA — временно добавить `Realize Instances`
> и посмотреть счётчик вершин в Edit Mode, либо использовать `Statistics` в системной
> панели. Не рассчитывай на точный API-запрос: реализации отличаются между версиями.

### Этап 7. Раскладка по кадрам в композиторе

Для QA толпу удобно смотреть не в 3D, а в виде линейки кадров: сразу видно, где
агенты стоят стеной, а где разбежались.

```python
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in \
    {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items} \
    else 'BLENDER_EEVEE'
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 120
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "//crowd/prev_"
bpy.ops.render.render(animation=True)
```

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `Distribute Points density` | 0.8 /м² | выше 3 — упрётесь во время кадра |
| `Distribute Points method` | `'POISSON'` | `'RANDOM'` быстрее, но даёт «сгустки» |
| Порог LOD (`LESS_THAN`) | 150 | подбирай по расстоянию до камеры |
| `Scene Time → Speed` | 0.6 | скорость шага |
| `visible_shadow` | `False` | включай, когда тени нужны в кадре |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Агентов | 400–3 000 на одну сцену без кэша |
| Что получается | **не файл**, а живая сцена: вьюпорт 30–60 fps на средней видеокарте |
| Кэш | не нужен — вся анимация детерминированная от `Scene Time` |
| Превью-рендер | 120 кадров (5 с при 24 fps), 1920×1080, EEVEE, **~1–3 мин** |
| Что можно забрать дальше | `Realize Instances` + Alembic — если нужно отдать в движок |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Модификатор красный, дерево не считается | не создан выход через `interface` | добавить `OUTPUT`-сокет `NodeSocketGeometry` |
| `AttributeError` на `node_group.inputs` | API 4.0+ | использовать `node_group.interface.new_socket(...)` |
| Агенты стоят столбом в ряд | точки распределены по сетке, а не случайно | `Distribute Points` с `Density` вместо ручного массива, увеличить `Seed` |
| FPS падает на 1–2 объектах рядом с камерой | они попали в ветку `LOD_High` | снизить порог `LESS_THAN`, вынести тяжёлые детали в отдельную коллекцию |
| Толпа «едет» рывками | скорость не согласована с длиной кривой | `Speed` = длина кривой / длительность цикла |
| Экспорт в движок пустой | инстансы не realizes | `Realize Instances` перед Alembic, иначе движок не увидит геометрию |
| Пропали агенты при смене коллекции | `Collection Info` не назначен | проверить `Separate Children` и путь к коллекции |

> [!NOTE]
> Полноценное избегание «агент-агент» в GN требует состояния между кадрами
> (Simulation Zone) и поиска соседей. Встроенной пространственной хеш-таблицы у GN нет:
> либо считают соседей вручную по сетке, либо выносят расталкивание в скриптовый
> handler. Проверь, какие ноды зоны симуляции доступны в твоей версии, прежде чем
> строить на них продакшн-пайплайн.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md), [WF 13: DESTRUCTION RBD](wf_13_destruction_rbd.md), [WF 15: FLUID PRODUCT SPLASH](wf_15_fluid_product_splash.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md)
- **По темам:** [P45: GEOMETRY NODES SIMULATION ZONES](../prompts/45_gn_simulation.md), [SIMULATION & PHYSICS: GEOMETRY NODES 4.0+](../simulation/rigid_body_gn.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [P07: INSTANCING & ARRAYS](../prompts/07_instancing_arrays.md)
- **Теги:** #geometry-nodes, #simulation, #workflow