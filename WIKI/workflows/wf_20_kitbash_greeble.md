---
id: wf_20_kitbash_greeble
lang: ru
category: workflows
type: workflow
status: full
tags: [stylized, workflow]
---
# WF 20: KITBASH GREEBLE CITY

**ID:** WF-20 | **Type:** Kitbash | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда крупная форма уже собрана из блоков, но выглядит «пустой»: нужно заполнить поверхности мелкими деталями — трубами, панелями, антеннами, решётками — не моделируя их вручную.

## 🎯 ЦЕЛЬ

Мы берём готовую китбаш-коробку и автоматически расставляем по её граням библиотеку мелких модулей — греблей (greebles). Форма перестаёт читаться как набор чистых прямоугольников и начинает читаться как техника или здание.

Принцип, который отличает нормальный китбаш от мусора: **детали разного масштаба, разной плотности и с разной ориентацией**. Модули не должны повторяться рядами и не должны одинаково ориентироваться. Поэтому три параметра, которые настраивают в первую очередь: плотность, минимальное расстояние между модулями и фильтр по размеру грани.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Geometry Nodes | 3.0+; интерфейс нод менялся в 4.0 | автоматическая расстановка модулей |
| Коллекция модулей | 20–80 мелких объектов, единый масштаб | источник деталей |
| Базовая форма (коробка) | из китбаш-библиотеки или собрана вручную | поверхность, на которую сажаем модули |
| Процедурные материалы | без текстур можно обойтись | материал читается лучше с вариативностью |
| HDRI | Poly Haven | окружение для рендера |

> [!NOTE]
> Имена нод Geometry Nodes (например `GeometryNodeDistributePointsOnFaces`) — это внутренние идентификаторы, а не то, что видишь в интерфейсе. В поиске нод в Blender они находятся по человекочитаемому имени: `Distribute Points on Faces`, `Instance on Points`, `Pick Instance`, `Collection Info`. Полный список идентификаторов твоей версии смотри из Python-консоли: `[t for t in dir(bpy.types) if t.startswith("GeometryNode")]`.

## 🛠️ НАСТРОЙКА

### Этап 1. Подготовка: привести модули к общему виду

Модули должны быть одного масштаба, иначе «гребля» будет выглядеть как случайный мусор. К каждому модулю: origin в основании (не в центре), нормали наружу, без оставшихся модификаторов.

```bash
RU: "Собери коллекцию 'GreebleLib': импортируй 24 модуля в 1 unit = 1 m,
     для каждого origin_set(type='ORIGIN_CURSOR', center='MEDIAN') в нижнюю точку,
     вычисти модификаторы, применяй трансформации"
EN: "Build collection 'GreebleLib': 24 modules at 1 unit = 1 m,
     origin_set(type='ORIGIN_CURSOR', center='MEDIAN') to the base,
     clear modifiers, apply transforms"
```

```python
import bpy
lib = bpy.data.collections["GreebleLib"]
bpy.ops.object.select_all(action='DESELECT')
for ob in lib.objects:
    ob.select_set(True)
bpy.context.view_layer.objects.active = lib.objects[0]

for ob in lib.objects:
    # origin внизу: так модуль «садится» на поверхность, а не висит в воздухе
    zs = [ (ob.matrix_world @ v.co).z for v in ob.data.vertices ]
    cursor_z = min(zs)
    scene_cursor = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = (ob.location.x, ob.location.y, cursor_z)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.scene.cursor.location = scene_cursor
    ob.scale = [s / 1.0 for s in ob.scale]          # нормализация к 1 m
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
```

### Этап 2. Расстановка: Geometry Nodes

Схема: `Distribute Points on Faces` → `Instance on Points` (по коллекции) → `Pick Instance` (случайный ребёнок на точку) → `Realize Instances` (опционально).

```python
import bpy

ng = bpy.data.node_groups.new("GN_Greeble", 'GeometryNodeTree')

# --- интерфейс группы. В Blender 4.0+ это ng.interface.new_socket(...),
# --- в более старых версиях — ng.inputs.new("NodeSocketFloat", "Name").
def iface(name, stype, in_out):
    try:
        return ng.interface.new_socket(name, in_out=in_out, socket_type=stype)
    except AttributeError:
        coll = ng.outputs if in_out == 'OUTPUT' else ng.inputs
        return coll.new(stype, name)

iface("Geometry", "NodeSocketGeometry", 'INPUT')
iface("Geometry", "NodeSocketGeometry", 'OUTPUT')
iface("Density",  "NodeSocketFloat",    'INPUT')
iface("Seed",     "NodeSocketInt",      'INPUT')

gi_in  = next(s for s in ng.interface.items_tree if s.item_type=='SOCKET'
              and s.in_out=='INPUT'  and s.name=="Geometry")
gi_out = next(s for s in ng.interface.items_tree if s.item_type=='SOCKET'
              and s.in_out=='OUTPUT' and s.name=="Geometry")

def N(t, **kw):
    n = ng.nodes.new(t)
    for k, v in kw.items(): setattr(n, k, v)
    return n
def S(n, name):
    s = n.inputs.get(name)
    if s is None: raise KeyError(f"{n.bl_idname}: нет входа '{name}' — проверь имена в своей версии")
    return s
def L(a, b): ng.links.new(a, b)

grp_in  = N("NodeGroupInput");  grp_out = N("NodeGroupOutput")
dist   = N("GeometryNodeDistributePointsOnFaces")
inst   = N("GeometryNodeInstanceOnPoints")
pick   = N("GeometryNodePickInstance")
coll   = N("GeometryNodeCollectionInfo")
rnd    = N("FunctionNodeRandomValue"); rnd.data_type = 'INT'
real   = N("GeometryNodeRealizeInstances")

coll.inputs["Collection"].default_value = bpy.data.collections["GreebleLib"]
coll.inputs["Separate Children"].default_value = True
coll.inputs["Reset Children"].default_value = True

rnd.inputs["Min"].default_value = 0
rnd.inputs["Max"].default_value = len(coll.inputs["Collection"].default_value.objects) - 1
rnd.inputs["Seed"].default_value = 7

L(grp_in.outputs["Geometry"], dist.inputs["Mesh"])
L(dist.outputs["Points"], inst.inputs["Points"])
L(grp_in.outputs["Density"], dist.inputs["Density"])
L(coll.outputs["Geometry"], inst.inputs["Instance"])
L(inst.outputs["Instances"], pick.inputs["Geometry"])
L(grp_in.outputs["Seed"], pick.inputs["Instance Index"])
L(rnd.outputs["Value"], pick.inputs["Instance Index"])
L(pick.outputs["Geometry"], real.inputs["Geometry"])
L(real.outputs["Geometry"], grp_out.inputs["Geometry"])

base = bpy.data.objects["Block_Main"]
mod = base.modifiers.new("Greeble", 'NODES')
mod.node_group = ng
base.modifiers["Greeble"]["Socket_2"] = 6.0     # Density: модулей на м²
base.modifiers["Greeble"]["Socket_3"] = 7       # Seed
```

> [!NOTE]
> Значения `Socket_N` в списке модификаторов зависят от того, в каком порядке интерфейс группы создаёт сокеты. Надёжнее после создания группы пройти по `mod` через интерфейс и записать значения по имени, либо задавать их руками в панели модификатора. Порядок и имена сокетов проверь в UI на своей версии.

### Этап 3. Фильтр по размеру грани и по ориентации

Модули одного размера на всех гранях дают «гвозди». Два приёма: (1) отбирать модули по площади грани через `Distribute Points on Faces` + `Delete Geometry` по полю, (2) добавить рандомный поворот через `Random Value` (Vector) → `Instance on Points.Rotation`.

```python
# Продолжение графа: случайный поворот каждого экземпляра
rot = ng.nodes.new("FunctionNodeRandomValue")
rot.data_type = 'FLOAT_VECTOR'
for name, v in (("Min", (-3.14, -3.14, -3.14)), ("Max", (3.14, 3.14, 3.14))):
    for s in rot.inputs:
        if s.name == name and s.type == 'VECTOR':
            s.default_value = v
            break
rot.inputs["Seed"].default_value = 11
ng.links.new(rot.outputs["Value"], inst.inputs["Rotation"])
```

### Этап 3a. Проверка плотности, а не «на глаз»

Плотность в модулях на м² нельзя прикидывать: можно получить и гвозди, и кашу. Считаем фактическое число инстансов и площадь покрытия на грани.

```python
import bpy
dg = bpy.context.evaluated_depsgraph_get()
base = bpy.data.objects["Block_Main"]
ev = base.evaluated_get(dg)
me = ev.to_mesh()
me.calc_loop_triangles()

area = 0.0
for t in me.loop_triangles:
    p = [ev.matrix_world @ me.vertices[i].co for i in t.vertices[:3]]
    area += ((p[1] - p[0]).cross(p[2] - p[0])).length / 2.0

mods = base.modifiers["Greeble"]
density = float(mods.get("Socket_2", 0.0) or 0.0)
est = area * density
print(f"площадь граней: {area:.1f} м², density={density:.1f}, модулей примерно {est:.0f}")
ev.to_mesh_clear()

# ориентир: меньше 3 на м² — пусто, больше 12 — начинается каша
if est and area:
    print("плотность в норме" if 3 <= est / area <= 12 else "плотность вне диапазона 3..12")
```

### Этап 4. Вариативность без новых объектов

Object Info → `Random` даёт каждому объекту стабильное число 0..1. Через ColorRamp оно превращается в сдвиг цвета и шероховатости. Это самый дешёвый способ сделать 40 одинаковых модулей неодинаковыми.

```python
import bpy
mat = bpy.data.materials.new("Mat_Kitbash")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

oi = nt.nodes.new("ShaderNodeObjectInfo")
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.18, 0.19, 0.21, 1)   # «грязный» вариант
ramp.color_ramp.elements[1].color = (0.42, 0.44, 0.47, 1)   # «чистый» вариант
nt.links.new(oi.outputs["Random"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

rough = nt.nodes.new("ShaderNodeMapRange")
rough.inputs["To Min"].default_value = 0.25
rough.inputs["To Max"].default_value = 0.65
nt.links.new(oi.outputs["Random"], rough.inputs["Value"])
nt.links.new(rough.outputs["Result"], bsdf.inputs["Roughness'])
```

### Этап 5. Декали и грязь

Декаль — тонкая плоскость с альфа-текстурой, прижатая к поверхности. Грязь — Attribute/Vertex Color, покрашенный по высоте.

```python
import bpy
# декаль-плоскость с альфой
bpy.ops.mesh.primitive_plane_add(size=0.8, location=(0, -2.0, 1.2))
dec = bpy.context.active_object
dec.name = "Decal_07"
m = bpy.data.materials.new("Mat_Decal"); m.use_nodes = True
nt = m.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(r"//textures/decal_07.png")   # PNG с альфой
tex.extension = 'CLIP'
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
# в Cycles можно вместо этого использовать ноду Decal — она есть только в Cycles
dec.data.materials.append(m)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `Distribute Points on Faces.Density` | 4–8 модулей на м² | ниже 3 — пусто, выше 12 — каша |
| `Distribute Points on Faces.Seed` | любое целое | менять, чтобы получить другой расклад, а не чтобы «починить» |
| `Collection Info.Separate Children` | `True` | иначе все модули слипнутся в один инстанс |
| `Collection Info.Reset Children` | `True` | сбрасывает трансформации детей к нулю |
| `Pick Instance.Instance Index` | Random Value (Int) | без него все точки получат одинаковый модуль |
| `Random Value` rotation range | ±π по всем осям | ±π/6 по Z — чтобы модули выглядели «прикрученными» |
| `ObjectInfo.Random → ColorRamp` | 2–3 стопа | больше стопов — больше разброса |

| Масштаб формы | Плотность | Размер модулей |
|---|---|---|
| Панель 1×1 м | 20–40 | 2–8 см |
| Стена здания 10×5 м | 3–6 | 10–40 см |
| Корпус аппарата 3×2×2 м | 6–12 | 5–20 см |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Все точки получили один и тот же модуль | нет `Pick Instance` с рандомным индексом | добавить `Random Value` (Int) → `Pick Instance` |
| Модули торчат из стены наполовину | origin не в основании | `origin_set` в нижнюю точку перед расстановкой |
| Модули «плывут» при движении камеры | точки считаются в локальных координатах | проверить систему координат в группе и `Reset Children` |
| Density не меняется после правки | сокет не тот, либо значение не применилось | проверить `Socket_N` в панели модификатора, сверить имена сокетов |
| Материал на модулях чёрный | нет UV после расстановки | инстансы наследуют UV коробки — добавь `UV Unwrap` или `Store Named Attribute` |
| Сцена встала при 60 модулях | инстансы не реализованы, движок считает каждый | `Realize Instances` только если правда нужно, иначе оставить инстансы |

## ✅ РЕЗУЛЬТАТ

На выходе: одна коробка с одним модификатором Geometry Nodes, на гранях которой сидит библиотека модулей, и один материал с вариативностью по `Object Info → Random`. Плюс превью 1600×900 и GLB.

Характеристики — **оценка по порядку величины, а не измеренный результат**: коробка 10×5×3 м при плотности 6 даёт порядка 900–1500 модулей; если каждый модуль — 200–600 треугольников, это от 0.2 до 0.9 млн треугольников **инстансами** (то есть один модуль в памяти, а не тысяча копий). После `Realize Instances` тот же объём распухает до десятков мегабайт в памяти. Рендер 1600×900 в Cycles, 128 сэмплов — минуты на средней видеокарте; в EEVEE — секунды.

**Это оценка.** Реальное время рендера зависит от числа уникальных материалов, объёма инстансов и железа — измеряй у себя.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 16: NPR ANIME RENDER](wf_16_npr_anime_render.md), [WF 18: ISOMETRIC GAME ART](wf_18_isometric_game_art.md), [WF 19: VOXEL ART PIPELINE](wf_19_voxel_art_pipeline.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md)
- **По темам:** [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md), [CASE 09: ANIME HEAD BUST](../cases/case_09_anime_head_bust.md), [CASE 11: COZY ROOM DIORAMA](../cases/case_11_cozy_room_diorama.md)
- **Теги:** #stylized, #workflow