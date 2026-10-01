---
id: wf_14_cloth_fashion_show
lang: ru
category: workflows
type: workflow
status: full
tags: [animation, clothing, workflow]
---
# WF 14: CLOTH FASHION SHOW

**ID:** WF-14 | **Type:** Cloth | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: Marvelous import + wind + runway loop
EN: Marvelous import + wind + runway loop

Коллекция одежды, симулируемая тканью, с дефиле в 8-секундном цикле. Смысл воркфлоу —
в стыке двух систем: **Marvelous Designer** считает покрой (лекала, сетка, швы, вытачки),
**Blender** считает физику поверх уже готовой сетки. Ошибка номер один — симулировать
в том же файле, где лекала редактируются. Это невозможно: у Blender нет модификатора,
который считает покрой, а Designer не считает столкновения с телом.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Marvelous Designer | любая своя | лекала, посадка, швы |
| Blender | 4.x | Cloth, Collision, ветер |
| Rig (Armature) | FBX/GLB | посадка ткани на тело |
| Окружение с коллизией | сцена | модель тела + подиум как Collision |

> [!NOTE]
> Родной формат Marvelous Designer — `.mcx`, и Blender его **не импортирует**. Обмен
> идёт через экспорт из Designer в OBJ, FBX или Alembic. Импорт на стороне Blender
> переезжал между операторами: `bpy.ops.wm.obj_import` (актуально) против старого
> `bpy.ops.import_scene.obj`. Если первый недоступен — проверь, какой из них есть
> в твоей версии, через поиск операторов в Python-консоли.

## 🛠 НАСТРОЙКА

### Этап 1. Импорт сетки и рига

```python
import bpy

# Актуальный оператор Blender 3.3+. Fallback для старых версий — см. примечание выше.
try:
    bpy.ops.wm.obj_import(filepath=r"C:\lookbook\dress.obj")
except AttributeError:
    bpy.ops.import_scene.obj(filepath=r"C:\lookbook\dress.obj")
bpy.ops.import_scene.fbx(filepath=r"C:\lookbook\rig.fbx")

garment = bpy.data.objects["Dress"]
rig     = bpy.data.objects["Rig"]
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.pose.transforms_clear()      # сбросить позу перед симуляцией: A/T-поза, без выгибов
bpy.ops.object.mode_set(mode='OBJECT')
```

### Этап 2. Порядок модификаторов

Порядок в стеке решает всё: ткань считается на **низкополигональной** сетке, а гладкость
добавляется после. Если поставить Subdivision перед Cloth, физика станет в разы дороже
и не изменится качественно.

```python
# стек снизу вверх: Cloth -> Smooth/Subdivision
cloth = garment.modifiers.new("Cloth", 'CLOTH')
subd  = garment.modifiers.new("Subdivision", 'SUBSURF')
subd.levels, subd.render_levels = 1, 2
subd.show_only_control_edges = True  # видно исходную сетку — по ней и судишь о качестве
```

### Этап 3. Настройки ткани

```python
cs = cloth.settings
cs.quality = 10                       # 5 хватит для превью, 10 — рабочая цифра
cs.mass = 0.25                        # кг на вершину; меньше = легче, «шёлк»
cs.tension_stiffness = 12
cs.compression_stiffness = 12
cs.shear_stiffness = 5
cs.bending_stiffness = 0.35           # ключ к виду: плащ vs дублёнка
cs.air_damping = 1.2

# Кэш: пока не испечён, физика живёт только до конца диапазона кэша
cloth.point_cache.frame_start = 1
cloth.point_cache.frame_end = 240
cloth.point_cache.use_disk_cache = True

col = cloth.collision_settings
col.use_collision = True
col.distance_min = 0.015              # половина толщины ткани; меньше = больше «слипания»
col.collision_quality = 3
col.use_self_collision = True         # обязательно для юбок: без этого ткань проходит сквозь себя
col.self_distance_min = 0.015
col.friction = 5.0
```

### Этап 4. Приколотка к костям

Классический приём: ткань не «приклеивается» к кости напрямую — ей назначают vertex
group, веса которой берутся из весов деформации арматуры через Data Transfer.

```python
# 1) На арматуре подняты группы деформации (созданы при импорте FBX)
# 2) На одежде создаём пустую группу и переливаем в неё веса
vgroup = garment.vertex_groups.new(name="Pin")
dt = garment.modifiers.new("PinFromArmature", 'DATA_TRANSFER')
dt.object = rig
dt.data_types = {'VERTEX_GROUP'}
dt.vertex_group = "Pin"
dt.mix_mode = 'REPLACE'              # не смешивать со старыми весами
# Порядок: Cloth должен идти ПОСЛЕ Data Transfer, иначе он увидит пустую группу
garment.modifiers.move(garment.modifiers.find("Data Transfer") + 1,
                       garment.modifiers.find("Data Transfer"))

cs.vertex_group_mass = "Pin"          # это и есть «Pin Group» в UI
cs.pin_stiffness = 1.0                # 1.0 = полностью закреплено; 0.5 = слегка проседает
```

> [!NOTE]
> Точное имя поля для переноса данных вершины называется `vertex_group`, а режим
> сопоставления выбирается в `mapping` — распространённые варианты: `TOPOLOGY`,
> `NEAREST_FACE_INTERPOLATED`. Проверь доступные значения: у Data Transfer список полей
> длинный и часть названий отличается от подписей в UI.

### Этап 5. Коллизии тела и подиума

```python
for name in ("Body", "Podium"):
    ob = bpy.data.objects.get(name)
    if ob and ob.modifiers.get("Collision") is None:
        ob.modifiers.new("Collision", 'COLLISION')
        ob.collision.thickness_outer = 0.02   # запас под сетку одежды
        ob.collision.damping = 0.3
        ob.collision.cloth_friction = 6.0
```

### Этап 6. Ветер

```python
bpy.ops.object.effector_add(type='WIND', location=(0, 4, 2), rotation=(1.5708, 0, 3.1416))
wind = bpy.context.object
wind.name = "RunwayWind"
f = wind.field
f.shape = 'PLANE'
f.strength = 900.0        # порыв дефиле: единицы привязаны к масштабу сцены
f.noise = 1.6             # без noise ветер «уставит» ткань как флаг
f.flow = 0.6              # flow создаёт «ветер по потоку» — струится вдоль шлейфа
f.falloff_power = 1.5
f.use_max_distance = True
f.distance_max = 14.0
f.seed = 7

# Зациклить ветер по кадрам цикла, иначе бесшовности не будет
for frame, val in ((1, 400.0), (60, 1200.0), (120, 500.0), (180, 1100.0), (241, 400.0)):
    f.strength = val
    f.keyframe_insert("strength", frame=frame)
fcu = wind.animation_data.action.fcurves[0]
mod = fcu.modifiers.new('CYCLES')     # 1-й и 241-й кадр совпадают → шва не видно
```

### Этап 7. Прогрев и запекание

```python
scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 240

# Пока не испечено, симуляция живёт только до конца кэша; прокрутка
# кадрами физику не считает — нужен bake.
for f in range(1, 241):
    scene.frame_set(f)
bpy.ops.ptcache.bake_all(bake=True)
```

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `bending_stiffness` | 0.35 | 0.05 — шёлк/шифон, 2.0 — кожа/деним |
| `mass` | 0.25 | выше — «тяжёлая» ткань, быстрее оседает |
| `self_distance_min` | 0.015 | при проколах юбки — увеличить вдвое |
| `quality` | 10 | выше 15 — только финальный прогон |
| `f.noise` | 1.6 | 0 = ровный поток, >3 = хаос |
| `pin_stiffness` | 1.0 | 0.3–0.7, если плечо должно слегка «плыть» |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Цикл | 240 кадров при 24 fps = **10 с** дефиле, бесшовно за счёт `CYCLES` на ветре |
| Что получается | запечённая симуляция Cloth в `.blend` + кэш на диске |
| Геометрия | 20–80 тыс. вершин до Subdivision, 200–600 тыс. после |
| Bake | **3–20 мин** (зависит от `quality` и числа коллизий) |
| Рендер | 1920×1080 Cycles 128 сэмплов: **40–120 мин** на 240 кадров |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Ткань «прилипает» к телу | `distance_min` слишком мал либо нет коллизии на Body | увеличить `distance_min`, добавить Collision на тело |
| Юбка проходит сквозь себя | выключен `use_self_collision` | включить и поднять `self_distance_min` |
| Одежда не следует за костями | Data Transfer стоит после Cloth | поднять его выше Cloth в стеке |
| Ткань «взрывается» на 1-м кадре | `mass` слишком мал при высокой жёсткости | снизить `tension_stiffness`, поднять `mass` до 0.3 |
| Ткань провисает ниже колен | `bending_stiffness` слишком низкий | 0.5–1.0 для костюма, 0.1 для плаща |
| Физика обрывается на кадре 240 | не испечён кэш | `ptcache.bake_all(bake=True)` |
| Ветер не двигает ткань | effector не попал в веса объекта | проверить `garment.effector_weights.wind` (должно быть 1.0) |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md), [WF 09: REALTIME VJ LOOP](wf_09_realtime_vj_loop.md), [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md), [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [CASE 06: ANIMATION LOOP](../cases/case_06_animation_loop.md), [P03: MODIFIERS STACK](../prompts/03_modifiers_stack.md)
- **Теги:** #animation, #clothing, #workflow