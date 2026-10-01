---
id: wf_13_destruction_rbd
lang: ru
category: workflows
type: workflow
status: full
tags: [simulation, workflow]
---
# WF 13: DESTRUCTION RBD

**ID:** WF-13 | **Type:** FX | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: Cell fracture + RBD + dust, cache Alembic
EN: Cell fracture + RBD + dust, cache Alembic

Разрушаемая стена: разлетается на куски под ударом, куски физически падают и
сталкиваются, в воздухе стоит пыль. И — кэш в Alembic, чтобы рендер считался
много раз без повторной физики. Разрушение и пыль — это два разных рейдера с разными
требованиями, и главная ошибка новичка — пытаться сделать обе части в один проход.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | встроенная физика и Fracture-модификатор |
| Модель разрушаемого объекта | GLB/FBX | манifold-геометрия обязательна |
| Alembic | встроенный | формат кэша симуляции |
| VRAM | 8+ ГБ | 500 активных тел |

> [!NOTE]
> Fracture-модификатор требует **замкнутой (manifold) геометрии**. Модель с
> неразрешёнными нормалями, двойными оболостями или незамкнутыми краями разобьётся
> «в молоко» либо вообще не даст трещин. Проверяй `Select → All by Trait → Non Manifold`
> до начала, а не после.

## 🛠 НАСТРОЙКА

### Этап 1. Fracture-модификатор: разбивка на ячейки

```python
import bpy

wall = bpy.data.objects["Wall"]
mod = wall.modifiers.new("Fracture", 'FRACTURE')
mod.fracture_type = 'CELL_FRACTURE'     # вариантное разбиение: дёшево, стабильно
mod.cell_type = 'RANDOM'
mod.cell_divide = 12                    # 12 = примерно 1728 ячеек на куб; начни с 6–8
mod.cell_size = 0.4
mod.use_separate_verts = True           # критично: без этого куски не разделятся
mod.show_viewport = True
mod.show_render = True
```

Типы `fracture_type` и их поведение:

| Тип | Когда использовать | Цена |
|---|---|---|
| `CELL_FRACTURE` | стены, панели, «кирпич» | дёшево, но видно регулярность |
| `VORONOI_FRACTURE` | бетон, камень — нужна неправильная форма | дороже, сильнее зависит от топологии |
| `RADIAL_FRACTURE` | взрыв от точки: `Number of Cuts` + `Range` | дёшево, хорош для стекла/зеркал |
| `WEIGHTED_FRACTURE` | разрушение по весам из карты плотности | требует подготовки весов |

### Этап 2. Тела физики

```python
bpy.ops.rigidbody.world_add()   # не bpy.ops.object.rigidbody: там такого оператора нет
rbw = bpy.context.scene.rigidbody_world
rbw.substeps_per_frame = 10          # растёт вместе с числом тел
rbw.solver_iterations = 20
pc = rbw.point_cache
pc.frame_start, pc.frame_end = 1, 120
pc.use_disk_cache = True              # кэш на диск — переживёт перезапуск Blender
pc.compression = 'LIGHT'

# Полу нужна коллизия. Добавь её вручную: Physics → Collision,
# либо bpy.ops.object.modifier_add(type='COLLISION') на выделенном объекте.
# Пол — пассивное тело: неподвижно, но участвует в столкновениях.
floor = bpy.data.objects["Floor"]
floor.rigid_body.type = 'PASSIVE'

# Оригинал стены — источник удара, он сам не падает
wall.rigid_body.type = 'KINEMATIC'
wall.rigid_body.kinematic = True      # включить анимацию/ключ в момент удара
wall.rigid_body.use_deactivation = True
```

### Этап 3. Получить куски как настоящие объекты

У модификатора Fracture есть два режима работы: интерактивный (через панель Physics,
где куски создаются как внутренний объект) и «честный» — когда геометрия реально
становится объектами. Второй надёжнее для скриптов и для Alembic.

```python
# Путь A: внутренний объект раскола (имя зависит от версии — ищем по шаблону)
frac = None
for ob in bpy.data.objects:
    if ob.type == 'MESH' and "fracture" in ob.name.lower():
        frac = ob
        break

if frac is None:
    # Путь B: применяем модификатор и разделяем на отдельные объекты.
    # Минус: трещины больше не появятся позже, все куски существуют с кадра 1.
    bpy.context.view_layer.objects.active = wall
    bpy.ops.object.modifier_apply(modifier="Fracture")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')   # каждая несвязанная часть → свой объект
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
chunks = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o is not wall]
for o in chunks:
    o.select_set(True)
bpy.ops.rigidbody.objects_add(type='ACTIVE')   # одним вызовом на всё выделенное
bpy.ops.object.select_all(action='DESELECT')

# Активация по очереди — иначе 500 тел стартуют в один кадр и «выстреливают»
for i, o in enumerate(chunks):
    o.rigid_body.use_start_deactivated = True
    o.rigid_body.use_deactivation = True
```

> [!NOTE]
> Имя объекта раскола (`<имя>_fracture` и его варианты) — внутренняя деталь Blender и
> менялась между версиями. Поэтому в коде выше путь A ищет объект по подстроке, а если
> не находит — откатывается на путь B. Не закладывайся на конкретное имя.

### Этап 4. Пыль: объёмный куб, а не частицы

Для пыли в одном кадре объёмный куб дешевле частиц на порядок и не требует кэша.

```python
bpy.ops.mesh.primitive_cube_add(size=6, location=(0, 0, 2))
dust = bpy.context.object
dust.name = "DustVolume"
dust.display_type = 'WIRE'             # в сцене видно только гало, в рендере — объём

mat = bpy.data.materials.new("Mat_Dust")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
vol = nt.nodes.new("ShaderNodeVolumeScatter")   # одностороннее рассеяние: дешево и мягко
vol.inputs["Color"].default_value = (0.62, 0.58, 0.52, 1.0)
vol.inputs["Density"].default_value = 0.0
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
dust.data.materials.append(mat)

# Плотность появляется в момент удара и оседает
for frame, val in ((1, 0.0), (28, 0.35), (75, 0.06), (120, 0.0)):
    vol.inputs["Density"].default_value = val
    vol.inputs["Density"].keyframe_insert("default_value", frame=frame)
```

Куб обязательно должен быть **замкнутым** и достаточно мелко разбит по сетке:
взрослее объём выглядит «ватой». Проверь `bpy.context.scene.render.engine` — в Cycles
объёмы считаются точно, в EEVEE быстрее, но с другими ограничениями на разрешение.

### Этап 5. Прогрев кэша

Кэш считается только если сцена реально «проиграна», а не прокручена на кадрах.

```python
scene = bpy.context.scene
scene.frame_set(1)
for f in range(1, 121):          # покадровый прогон — сбрасывает инерцию и промахи
    scene.frame_set(f)
bpy.ops.ptcache.bake_all(bake=True)
```

### Этап 6. Экспорт в Alembic

```python
bpy.ops.object.select_all(action='DESELECT')
for o in chunks:
    o.select_set(True)
bpy.ops.wm.alembic_export(
    filepath="//cache/wall_destruction.abc",
    start=1, end=120,
    selected=True,            # только куски, без стены и пыли
    flatten=True,             # общая трансформация — файл переносится без иерархии
    uvs=True, normals=True,
    apply_modifiers=True,
)
```

> [!NOTE]
> Полный список флагов `wm.alembic_export` менялся; в частности, применение
> модификаторов при экспорте управляется параметром, который в разных версиях называется
> по-разному. Проверь актуальный список: наведи курсор на оператор в Python-консоли или
> вызови `bpy.ops.wm.alembic_export.get_rna_type().properties.keys()`.

### Этап 7. Удар: кинематика как «пушка»

Стена не падает сама — её нужно толкнуть в нужном кадре. Кинематическое тело с
анимированным ключом позиции работает как импульс.

```python
wall = bpy.data.objects["Wall"]
wall.location.z = 0.0
wall.keyframe_insert("location", index=2, frame=1)
wall.location.z = -0.8          # за 1 кадр вниз = резкий удар
wall.keyframe_insert("location", index=2, frame=3)
wall.location.z = -0.8          # дальше стоит: пока не пересчитаешь кэш
wall.keyframe_insert("location", index=2, frame=4)

# Порядок обязателен: удар -> прогрев -> запекание -> экспорт.
# Если запечь до удара, кэш будет пустым.
for f in range(1, 121):
    bpy.context.scene.frame_set(f)
bpy.ops.ptcache.bake_all(bake=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `cell_divide` | 6–8 | выше 12 — каждый кусок тоньше пыли и тормозит |
| `rbw.substeps_per_frame` | 10 | 20 при >300 активных тел |
| `rbw.solver_iterations` | 20 | выше при «протекающих» столкновениях |
| `pc.compression` | `'LIGHT'` | `'NO'` при артефактах, `'HEAVY'` для экономии места |
| `DustVolume density` | 0.35 в пике | выше — стена уходит в молоко |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Симуляция | 120 кадров (5 с при 24 fps), 200–800 активных кусков |
| Кэш | `//cache/wall_destruction.abc`, ориентировочно 50–400 МБ |
| Пыль | отдельный объект `DustVolume` — в Alembic не входит, рендерится отдельно |
| Рендер | 1920×1080, Cycles 256 сэмплов, **15–45 мин** (объём доминирует) |
| Повторный прогон | физика не пересчитывается: рендер идёт по кэшу |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Трещин нет, стена целая | не manifold-геометрия | `Select Non Manifold`, либо Decimate до цельности |
| Куски не падают | куски не получили `rigid_body` | выделить и `rigb.objects_add(type='ACTIVE')` заново |
| Взрыв на первом кадре | нет `use_start_deactivated` | включить у всех активных тел |
| Симуляция каждый кадр разная | кэш не запечён, `use_disk_cache` выключен | `ptcache.bake_all(bake=True)` + дисковый кэш |
| Кусок проваливается сквозь пол | `substeps_per_frame` мало при быстрых телах | поднять до 15–20 |
| Пыль в кубе, а не в воздухе | куб не замкнут | применить `Scale`-одну операцию, проверить нормали |
| Alembic пустой на выходе | не выделены куски | `selected=True` требует явного `select_set` для каждого |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 12: CROWD SIM GN](wf_12_crowd_sim_gn.md), [WF 15: FLUID PRODUCT SPLASH](wf_15_fluid_product_splash.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md)
- **По темам:** [P21: PHYSICS SIMULATION](../prompts/21_physics_simulation.md), [P45: GEOMETRY NODES SIMULATION ZONES](../prompts/45_gn_simulation.md), [P47: ALEMBIC CACHE PIPELINE](../prompts/47_alembic_cache.md), [SIMULATION & PHYSICS: GEOMETRY NODES 4.0+](../simulation/rigid_body_gn.md)
- **Теги:** #simulation, #workflow