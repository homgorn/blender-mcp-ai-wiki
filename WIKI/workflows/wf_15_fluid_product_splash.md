---
id: wf_15_fluid_product_splash
lang: ru
category: workflows
type: workflow
status: full
tags: [simulation, workflow]
---
# WF 15: FLUID PRODUCT SPLASH

**ID:** WF-15 | **Type:** Fluid | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: FLIP splash around product, meshing, whitewater
EN: FLIP splash around product, meshing, whitewater

Бьющая вверх струя вокруг товара: капли расходятся по форме изделия, превращаются в
меш, от него отрывается аэрозоль (whitewater). Три разных рендера в одном кадре —
жидкость, меш и пена — это три разных требования к памяти, и именно на этом воркфлоу
обычно кончается RAM. Здесь обязательна дисциплина: маленький домен, честный масштаб,
`cache_type = 'ALL'` до конца расчёта и запись кэша на диск.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | Mantaflow (встроенный) |
| ОЗУ | 16 ГБ+ | при `resolution_max = 256` домен — это ~16 млн ячеек |
| Меш товара | замкнутый | иначе эффектор не считается |
| Диск | 20 ГБ+ | кэш жидкости весит больше, чем сам рендер |

> [!NOTE]
> Названия полей Mantaflow менялись заметно (`cache_data_format`, `simulation_method`,
> `resolution_max`, `spray_scale` и соседние). Ниже приведены те имена, которые
> использовались в ветке 4.x, но перед продакшном обязательно сверь список: в Python-консоли
> набери `dir(bpy.data.objects["Domain"].fluid_settings)` — выведет реальные поля твоей
> сборки, и это надёжнее, чем любая документация.

## 🛠 НАСТРОЙКА

### Этап 1. Масштаб решает всё

Домен должен быть **плотным**: 1 unit = 1 метр, товар внутри, а не «комната 10 метров
вокруг банки». Каждая лишняя единица сетки — это куб памяти вчетверо.

```python
import bpy, math

scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 90     # 90 кадров ≈ 3.75 с

# Домен: куб 2×2×2 м вокруг товара. Максимальный габарит товара
# должен занимать не меньше трети ширины домена, иначе сетка грубая.
bpy.ops.object.fluid_add(type='DOMAIN', location=(0, 0, 1.0))
dom = bpy.context.object
dom.name = "Domain"
dom.scale = (1.0, 1.0, 1.0)

fs = dom.fluid_settings
fs.domain_type = 'LIQUID'
fs.resolution_max = 256        # 128 — черновик, 256 — рабочая, 512 — уже 64 ГБ RAM
```

### Этап 2. Влияние: струя снизу вверх

```python
# Цилиндр-источник под товаром: жидкость выходит из-под изделия,
# расходится по его форме и срывается каплями — классический «waterfall»
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.35, depth=0.4,
                                    location=(0, 0, 0.12))
src = bpy.context.object
src.name = "Source"
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bpy.ops.object.fluid_add(type='FLOW', location=(0, 0, 0))
flw = bpy.context.object
flw.name = "Flow"
fset = flw.fluid_settings
fset.flow_type = 'LIQUID'
fset.flow_behavior = 'INFLOW'
fset.use_inflow = True
fset.use_plane_init = False     # False = непрерывный поток, True = разовый «поршень»
```

### Этап 3. Товар как эффектор

```python
product = bpy.data.objects["Product"]
bpy.ops.object.fluid_add(type='EFFECTOR', location=product.location)
eff = bpy.context.object
eff.name = "ProductEffector"
eset = eff.fluid_settings
eset.effector_type = 'COLLISION'
eset.use_effector = True

# Насколько жидкость «обтекает» форму до того, как считает себя внутри.
# Больше = объёмнее жидкость вокруг изделия, меньше = тонкая плёнка.
eset.surface_distance = 0.02
eset.use_plane_init = False

# Подвижное тело: если товар падает/вращается — эффектор должен это знать
eset.subframes = 1              # промежуточные кадры: без них быстрые объекты «протыкают» воду
```

### Этап 4. Параметры домена и whitewater

```python
fs.cache_type = 'ALL'          # 'ALL' = сохраняем весь кэш. Иначе после смены кадра
                               # физика пересчитается и результат «поплывёт»
fs.cache_frame_start = 1
fs.cache_frame_end = 90
fs.cache_directory = "//cache/fluid"
fs.cache_data_format = 'OPENVDB'

# Аэрозоль: то, что читается как брызги и пена. Без этого будет
# гладкая «желевая» вода без капель.
ew = fs.effector_weights
ew.spray_emission = 12.0        # капли в воздухе
ew.foam_emission = 6.0          # пена на поверхности
ew.surface_distance = 0.02
```

### Этап 5. Меширование жидкости

Домен создаёт частицы «Liquid Mesh»; из них строится поверхность, а не из объёма сетки.

```python
# Настройки частиц меша живут в particle system домена
for ps in dom.particle_systems:
    if "mesh" in ps.name.lower():
        ps.settings.liquid_render = 'MESH'     # иначе на выходе будет пузырьки, а не поверхность
        ps.settings.sphere_scale = 1.0
        ps.settings.sphere_radius = 1.0        # >1 = поверхность «натягивается», меньше капель
```

> [!NOTE]
> Имя частичной системы, создаваемой доменом, и поля `liquid_render` / `sphere_scale`
> внутренние и версионно-зависимые. Надёжнее найти её в интерфейсе: вкладка Physics →
> Type: Liquid → раздел Liquid Mesh. Если в твоей версии поля называются иначе —
> сверься с руководством, а не с этим списком.

### Этап 6. Материал жидкости и пены

```python
mat = bpy.data.materials.new("Mat_Liquid")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs["Base Color"].default_value = (0.75, 0.85, 0.9, 1.0)
bsdf.inputs["Transmission Weight"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.02
bsdf.inputs["IOR"].default_value = 1.333        # вода, не стекло: 1.45 было бы «стеклянной»
product.data.materials.append(mat)

# Пена — объёмный Principled Volume: цвет, плотность, эмиссия и
# два входа whitewater, которые появляются у ноды в контексте флюида
foam = bpy.data.materials.new("Mat_Foam")
foam.use_nodes = True
ntf = foam.node_tree
ntf.nodes.clear()
pv = ntf.nodes.new("ShaderNodeVolumePrincipled")
out = ntf.nodes.new("ShaderNodeOutputMaterial")
ntf.links.new(pv.outputs["Volume"], out.inputs["Volume"])
pv.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
pv.inputs["Density"].default_value = 0.35
dom.data.materials.append(foam)
```

### Этап 7. Расчёт

```python
# Порядок: сначала белкастер, потом рендер. Порог в память — 16 ГБ
bpy.ops.fluid.bake_all()

# Проверка: кэш лежит на диске и весит сотни мегабайт — это нормально
# ls -lh cache/fluid/
```

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `resolution_max` | 128 / 256 / 512 | черновик / рабочий / премиум |
| `cache_type` | `'ALL'` | иначе результат нестабилен между прогонами |
| `spray_emission` | 8–20 | выше 25 — кадр в молоке |
| `foam_emission` | 3–10 | для мыла/молока |
| `subframes` | 1–3 | обязательно 3, если товар быстро движется |
| `IOR` | 1.333 | стекло — 1.45 |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Симуляция | 90 кадров (3.75 с при 24 fps), домен 2×2×2 м, `resolution_max = 256` |
| Кэш | `//cache/fluid/` на диске, ориентировочно 1–8 ГБ |
| Меш | поверхность жидкости из частиц Liquid Mesh, отдельный меш для пены |
| Рендер | 1920×1080 Cycles 256 сэмплов: **40–120 мин** (жидкость с преломлением дороже всего) |
| Экспорт | Alembic жидкости для последующего композитинга |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Жидкость проходит сквозь товар | товар не EFFECTOR либо `subframes = 0` | добавить эффектор, поднять `subframes` до 3 |
| Картинка «плывёт» между прогонами | `cache_type` не `'ALL'` | выставить `'ALL'` и перезапечь |
| Вылет по памяти | домен слишком большой или `resolution_max` велик | уменьшить габарит домена, `resolution_max` до 128 |
| Капли выглядят как пузырьки | не переключено `liquid_render` в `'MESH'` | переключить в интерфейсе Liquid Mesh |
| Нет брызг, только «желе» | `spray_emission = 0` и нет whitewater | поднять `spray_emission`, назначить пеноматериал |
| Поверхность в сетку | мало итераций меширования | увеличить `surface_distance`, проверить итерации в UI |
| Товар «висит» в воздухе после удара | нет гравитации для эффектора | эффектор по умолчанию статичен — либо кинематика, либо внешняя анимация |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 12: CROWD SIM GN](wf_12_crowd_sim_gn.md), [WF 13: DESTRUCTION RBD](wf_13_destruction_rbd.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md)
- **По темам:** [P21: PHYSICS SIMULATION](../prompts/21_physics_simulation.md), [P45: GEOMETRY NODES SIMULATION ZONES](../prompts/45_gn_simulation.md), [P47: ALEMBIC CACHE PIPELINE](../prompts/47_alembic_cache.md), [SIMULATION & PHYSICS: GEOMETRY NODES 4.0+](../simulation/rigid_body_gn.md)
- **Теги:** #simulation, #workflow