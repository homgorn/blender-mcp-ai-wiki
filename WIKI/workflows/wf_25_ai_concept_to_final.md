---
id: wf_25_ai_concept_to_final
lang: ru
category: workflows
type: workflow
status: full
tags: [ai-3d, workflow]
---
# WF 25: AI CONCEPT→FINAL

**ID:** WF-25 | **Type:** AI Pipe | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

> Когда применять: когда есть концепт-картинка или текстовое описание, и нужен финальный 3D-рендер быстрее, чем моделирование вручную. Честно: генератор даёт форму, а не ассет.

## 🎯 ЦЕЛЬ

Концепт → сгенерированная 3D-модель → приведённая к масштабу и нормалям → ретопология → PBR-материалы → рендер.

Ключевая честная оговорка, без которой статья врёт: **text/image-to-3D даёт болванку**. Почти всегда — непропорциональные формы, зеркальные UV, произвольный масштаб, иногда дырявая геометрия и текстура, которой нет. Генератор экономит время на блокауте; финальное качество всё равно делается руками. Этот пайплайн честно разделён на «то, что машина» и «то, что человек».

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| blender-mcp с генератором | проверить `get_addon_status` и статус конкретного генератора | генерация |
| Концепт-изображение 1024×1024 | — | вход для image-to-3D |
| Blender с Quad Remesher | аддон | равномерная топология |
| Материалы | процедурные или из набора | PBR поверх формы |
| HDRI + 3-point схема света | Poly Haven | рендер |

> [!NOTE]
> Имена MCP-инструментов ниже взяты из подключённого сервера (`generate_hyper3d_model_via_text`, `poll_rodin_job_status`, `import_generated_asset`, `get_tripo_status`, `poll_tripo_job_status`, `import_generated_asset_tripo`, `get_hunyuan3d_status`, `poll_hunyuan_job_status`, `import_generated_asset_hunyuan`). Набор и имена зависят от версии аддона: сначала вызови `get_addon_status()` и посмотри, что реально доступно, вместо того чтобы идти по списку.

## 🛠️ НАСТРОЙКА

### Этап 1. Проверить, что генератор вообще доступен

Не вызывай генерацию до проверки статуса: иначе потратишь итерацию на заведомо нерабочую интеграцию.

```bash
# 1) состояние аддона и версия Blender
get_addon_status

# 2) статусы конкретных генераторов — вызывай те, что есть в твоей сборке
get_tripo_status
get_hyper3d_status
get_hunyuan3d_status
```

Если статус показывает, что генератор помечен как платный/премиум — сначала спроси пользователя, прежде чем запускать платные задачи. Проверка лимитов и стоимости — часть работы, а не деталь.

### Этап 2. Генерация

```bash
# генерация по описанию; bbox_condition — желаемый габарит (в метрах, 6 чисел)
generate_hyper3d_model_via_text(
  text_prompt="stylized knight helmet, faceted plates, closed visor, dark steel",
  bbox_condition=[0.4, 0.35, 0.45, 0, 0, 0]      # ширина, глубина, высота, центр
)

# генерация по картинке концепта
generate_hyper3d_model_via_text(
  text_prompt="same asset as the reference image, single object, clean background",
  bbox_condition=[0.4, 0.35, 0.45, 0, 0, 0]
)

# дальше — опрос задачи и импорт результата по request_id
poll_rodin_job_status(request_id="<из ответа генерации>")
import_generated_asset(name="Helmet_Raw", task_uuid="<uuid задачи>")
```

Опрос задачи возвращает статус; импорт выполняется отдельно и только после того, как задача дошла до готового состояния. Вызывать импорт раньше — самая частая ошибка.

### Этап 3. Привести к масштабу и посадить на пол

Сразу после импорта — габаритный проверка и посадка. Генераторы не понимают метры.

```python
import bpy
from mathutils import Vector

ob = bpy.data.objects.get("Helmet_Raw")
if ob is None:
    raise SystemExit("объект не импортирован — проверь статус задачи")

def bbox_world(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    hi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    return lo, hi

lo, hi = bbox_world(ob)
size = hi - lo
print(f"импортирован габарит: {size.x:.3f} x {size.y:.3f} x {size.z:.3f} (в единицах сцены)")

TARGET_H = 0.45                      # шлем = 45 см
s = TARGET_H / max(size.z, 1e-6)
ob.scale = [s] * 3
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

lo, hi = bbox_world(ob)               # после применения трансформации пересчитываем
ob.location.z -= lo.z                 # нижняя точка в Z=0
print(f"после нормализации: {hi.x-lo.x:.3f} x {hi.y-lo.y:.3f} x {hi.z-lo.z:.3f} м")
```

Отдельно проверь зеркальность: сгенерированные модели часто приходят вывернуты наизнанку.

```python
# площадь нормалей наружу: если объём «вывернут», normal.dot(center - p) должен быть > 0
import bmesh
me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
bad = 0
for f in bm.faces:
    c = f.calc_center_median()
    if f.normal.dot(c) < 0:
        bad += 1
bm.free()
if bad > len(me.polygons) * 0.5:
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)   # доступность менялась между версиями
    bpy.ops.object.mode_set(mode='OBJECT')
    print("нормали были вывернуты — исправлено")
```

> [!NOTE]
> Операция пересчёта нормалей в наружу переименовывалась (`normals_make_consistent`, в более старых версиях `editnormals_make_consistent`). Если оператор не найден — выдели всё в Edit Mode и сделай `Mesh → Normals → Recalculate Outside` вручную; логика та же.

### Этап 4. Ретопология и UV

```python
import bpy, math
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True); bpy.context.view_layer.objects.active = ob

# грубое упрощение до рабочего объёма
d = ob.modifiers.new("Decimate", 'DECIMATE')
d.decimate_type = 'COLLAPSE'; d.ratio = 0.12
bpy.ops.object.modifier_apply(modifier=d.name)

# гладкие нормали: без этого ретопо-поверхность будет «гранёной»
try:
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
except AttributeError:
    bpy.ops.object.shade_smooth()

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01)
bpy.ops.object.mode_set(mode='OBJECT')
```

Равномерные квады даёт аддон-ремешер — см. [WF 24](wf_24_photogrammetry_cleanup.md): встроенного в Blender квад-ремешера с ровным ребром нет.

### Этап 5. Материалы

Если генератор принёс текстуру, сначала проверь, что она вообще есть и в том ли цветовом пространстве.

```python
import bpy
img = bpy.data.images.get("Helmet_Raw texture")
print("текстуры на объекте:", [i.name for i in bpy.data.images if i.users])
if img:
    print("размер:", tuple(img.size), "colorspace:", img.colorspace_settings.name)

mat = bpy.data.materials.new("Mat_Helmet")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value = (0.06, 0.07, 0.09, 1)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.38

# потёртости без текстуры: Noise -> Roughness, иначе металл выглядит пластиковым
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs['Scale'].default_value = 40.0
noise.inputs['Detail'].default_value = 6.0
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs['To Min'].default_value = 0.25
mr.inputs['To Max'].default_value = 0.55
nt.links.new(noise.outputs['Fac'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], bsdf.inputs['Roughness'])

ob.data.materials.clear(); ob.data.materials.append(mat)
```

### Этап 6. Камера, свет, рендер

```python
import bpy, math
sc = bpy.context.scene
# плоский продуктовый свет: две софтбокс-панели + заполняющий
for name, loc, energy, size in (("Key",  (1.2, -1.6, 1.6), 400, 1.5),
                                ("Fill", (-1.6, -0.8, 0.9), 120, 2.0)):
    bpy.data.lights.new(name, type='AREA')
    l = bpy.data.objects.new(f"L_{name}", bpy.data.lights[name])
    sc.collection.objects.link(l); l.location = loc
    l.data.energy = energy; l.data.size = size
    c = l.constraints.new('TRACK_TO'); c.target = ob
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

bpy.ops.object.camera_add(location=(0.9, -1.5, 0.55))
cam = bpy.context.active_object; cam.data.lens = 85
c = cam.constraints.new('TRACK_TO'); c.target = ob
c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
sc.camera = cam

sc.render.engine = 'CYCLES'
sc.cycles.samples = 256
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1600
sc.render.filepath = r"//renders/helmet_hero.png"
bpy.ops.render.render(write_still=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `bbox_condition` при генерации | желаемый габарит | задавай сразу: экономит одну итерацию нормализации |
| `Decimate.ratio` | 0.10–0.20 | сильнее — теряются мелкие пластины шлема |
| `Metallic` / `Roughness` | 1.0 / 0.25–0.55 | металл без вариации шероховатости читается как пластик |
| `lens` камеры | 50–100 мм для продукта | широкий объектив растягивает объект |
| `samples` | 128 черновик / 256–512 финал | шумоподавление обязательно на обоих |
| `RESOLUTION` | 1024 черновик / 1600–2048 финал | — |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Импорт вернул объект, которого нет в сцене | задача ещё не готова, `request_id` от другого запуска | опросить статус, дождаться готового, импортировать по правильному id |
| Объект «утоплен» в полу или висит | не посажен на нулевую Z | пересчитать `bound_box` в мировых координатах и сдвинуть |
| Модель в 10 раз больше комнаты | генератор не знает про метры | привести к нужной высоте через `scale` + `transform_apply` |
| Форма вывернута, рендер чёрный | нормали наружу | `Recalculate Outside` или вывернуть объект |
| Текстуры нет, материал серый | генератор не отдаёт карту | процедурный материал (см. этап 5), UV развернуть вручную |
| Сцена «в пятне», форма не читается | слишком мягкий свет | жёстче ключевой, ниже фон, добавить контровой |

## ✅ РЕЗУЛЬТАТ

На выходе: нормализованный объект на Z=0 с одним PBR-материалом и рендер 1600×1600 в PNG, плюс `.blend`.

Характеристики — **оценка по порядку величины, а не измеренный результат**: сгенерированная болванка — обычно сотни тысяч треугольников; после `Decimate 0.12` — десятки тысяч, после квад-ремешера с ребром 2–3 см на модели 45 см — 20–60 тыс. Рендер 1600×1600 в Cycles, 256 сэмплов, шумоподавление включено, сцена из одного объекта с процедурным материалом — от десятков секунд до единиц минут на средней дискретной видеокарте.

**Это оценка.** Генерация сама занимает от десятков секунд до нескольких минут на задачу в зависимости от сервиса; измеряй на своём ключе и учитывай лимиты.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md), [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md)
- **По темам:** [SETUP 42: TRIPO AI API](../setups/setup_42_tripo_ai_api.md), [SETUP 43: MESHY API V4](../setups/setup_43_meshy_api_v4.md), [SETUP 44: RODIN / HYPER3D GEN](../setups/setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](../setups/setup_45_hunyuan3d_21.md)
- **Теги:** #ai-3d, #workflow