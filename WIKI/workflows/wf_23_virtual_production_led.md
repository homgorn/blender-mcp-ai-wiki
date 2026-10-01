---
id: wf_23_virtual_production_led
lang: ru
category: workflows
type: workflow
status: full
tags: [animation, pipeline, render, texturing, workflow]
---
# WF 23: VIRTUAL PRODUCTION LED

**ID:** WF-23 | **Type:** VP | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

> Когда применять: когда снимают в павильоне с LED-стеной: нужно, чтобы 3D-сцена реально светила на актёров, отражалась в их глазах и совпадала с траекторией камеры.

## 🎯 ЦЕЛЬ

Blender в виртуальном продакшене играет **две разные роли**, и их путают чаще всего:

1. **Источник контента для стены.** Рендер с «виртуальной» камеры, отправленный на видеопроцессор LED-стены. Здесь важны: UV-развёртка 1:1, эмиссивный материал без засветки сцены, скорость кадра.
2. **Движок финального кадра.** Рендер с реальной камеры площадки, где стена уже отрендерена и вставлена композитом. Здесь важны: траектория камеры, тени от актёров, «shadow catcher», чистый альфа-кадр без стены.

Статья про оба режима. Физическое железо (стена, видеопроцессор, трекер, genlock) — вне Blender, поэтому здесь только то, что делается в сцене.

> [!NOTE]
> nDisplay и подобные системы виртуального продакшена — закрытые технологии с плагинами под конкретную версию Blender. Имена нод, панели и требуемые настройки у них свои и меняются; здесь описан общий принцип «камера + эмиссивная стена + трек», который работает с любым из этих решений и с самодельной связкой из нескольких инстансов и видеомикшера. Точные шаги настройки nDisplay бери из документации NVIDIA под свою версию плагина, не отсюда.

## 📋 ЧТО ПОНАДОБИТЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | шейдер `Light Path` обязателен | разделение «камера / отражение / засветка» |
| LED-стена | разрешение, напр. 2560×1360 | определяет шаг пикселя и требования к рендеру |
| Видеопроцессор стены | — | принимает кадры/поток от Blender |
| Система трекинга камеры | оптический трекер или моушен-капчер | траектория реальной камеры в сцене |
| HDRI площадки | с реальными приборами | чтобы свет стены совпадал с освещением павильона |

## 🛠️ НАСТРОЙКА

### Этап 1. Геометрия стены и развёртка 1:1

Стена — это не «декорация», а эмиттер с заданным числом пикселей. Развёртка обязана быть пиксель-в-пиксель: если в 2560 пикселях по горизонтали приходится 2561 UV-координата, изображение смазывается на швах.

```bash
RU: "LED-стена 2560x1360 пикселей, шаг пикселя 2.6 мм => плоскость 6.656 x 3.536 м.
     Создай плоскость 'LED_Wall' ровно такого размера, UV 1:1 без Scale и Crop,
     назначь эмиссивный материал 'Mat_LED'"
EN: "LED wall 2560x1360 px, 2.6 mm pitch => plane 6.656 x 3.536 m.
     Create plane 'LED_Wall' exactly that size, UV 1:1 with no Scale/Crop,
     assign emissive material 'Mat_LED'"
```

```python
import bpy
W_PX, H_PX, PITCH = 2560, 1360, 0.0026          # разрешение стены и шаг пикселя в метрах
wall_w, wall_h = W_PX * PITCH, H_PX * PITCH     # 6.656 x 3.536 м
print(f"геометрия стены: {wall_w:.3f} x {wall_h:.3f} м, "
      f"{wall_w/wall_h:.4f} против {W_PX/H_PX:.4f} — должно совпасть")

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -4.0, 1.75))
wall = bpy.context.active_object
wall.name = "LED_Wall"
wall.scale = (wall_w, wall_h, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

uv = wall.data.uv_layers.new(name="UVMap")      # ровно одна UV-карта, 0..1, без перекрытий
for poly in wall.data.polygons:
    for li in poly.loop_indices:
        co = wall.data.vertices[wall.data.loops[li].vertex_index].co
        uv.data[li].uv = (co.x / wall_w + 0.5, co.y / wall_h + 0.5)
```

### Этап 2. Материал: светит в камеру, но не засвечивает сцену

Ключевой приём — разделение по типу луча через `Light Path`. В камеру стена выглядит как источник изображения; в отражениях она даёт слабый диффузный отклик; в диффузном освещении сцены она почти не участвует, иначе свет «из стены» заливает павильон.

```python
import bpy
mat = bpy.data.materials.new("Mat_LED")
mat.use_nodes = True
nt = mat.node_tree
out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
em = nt.nodes.new("ShaderNodeEmission")
lp = nt.nodes.new("ShaderNodeLightPath")
tex = nt.nodes.new("ShaderNodeTexImage")
mix = nt.nodes.new("ShaderNodeMixShader")
glow = nt.nodes.new("ShaderNodeEmission")      # «диффузный» отклик для отражений

tex.image = bpy.data.images.load(r"//renders/wall_0001.png")
tex.extension = 'EXTEND'
em.inputs['Strength'].default_value = 3.0      # пересвеченность стены в кадре
glow.inputs['Color'].default_value = (0.05, 0.06, 0.08, 1)
glow.inputs['Strength'].default_value = 0.25   # насколько «виден» экран в глазах актёра

# Mix Shader: Is Camera Ray = 1 -> верхний сокет (изображение), иначе нижний (glow)
nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
nt.links.new(tex.outputs['Color'], em.inputs['Color'])
nt.links.new(glow.outputs['Emission'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
wall.data.materials.append(mat)
```

### Этап 3. Стены не должно быть в финальном кадре

Для финального рендера стена — источник света, но не видимая геометрия. Иначе получишь изображение стены поверх записанного видео.

```python
import bpy
wall = bpy.data.objects["LED_Wall"]
# в финальном кадре стена не рисуется, но продолжает освещать
wall.visible_camera = False      # не видно в primary rays
wall.visible_glossy = True       # отражения в глазах/на одежде оставляем

# пол в павильоне — shadow catcher: принимает тень, не рисуется сам
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
floor = bpy.context.active_object; floor.name = "Stage_Floor"
floor.is_shadow_catcher = True
```

> [!NOTE]
> Флаги видимости по типам лучей и `is_shadow_catcher` относятся к Cycles и переезжали между версиями (в некоторых имена менялись). Надёжно проверить наличие у себя так: `hasattr(bpy.types.Object, "visible_camera")` и `hasattr(bpy.types.Object, "is_shadow_catcher")`. Если поля нет — см. `Object Properties → Visibility → Ray Visibility` в своей версии.

### Этап 4. Трекинг реальной камеры

Трекер отдаёт последовательность положений и ориентаций камеры. Большинство систем умеют экспортировать текст/CSV; в Blender Camera Motion есть аддон-модуль Camera Solver, который умеет решать такое прямо в VSE.

```bash
RU: "Импортируй solves камеры из //trk/cam_solve.txt в VSE как полосу Movie,
     запусти Camera Motion -> Camera Motion, примени solve к камере Cam_OnStage"
EN: "Import camera solves from //trk/cam_solve.txt as a Movie strip in the VSE,
     run Camera Motion -> Camera Motion, apply the solve to Cam_OnStage"
```

```python
import bpy, math
from mathutils import Euler, Vector

cam = bpy.data.objects["Cam_OnStage"]
keys = []
with open(bpy.path.abspath("//trk/cam_solve.txt"), encoding="utf-8") as fh:
    for line in fh:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        p = line.split()
        if len(p) < 6:
            continue
        keys.append((float(p[0]), Vector(map(float, p[1:4])),
                     Euler(tuple(map(math.radians, map(float, p[4:7]))), 'XYZ').to_quaternion()))

if not keys:
    raise SystemExit("не разобрано ни одной строки — проверь формат файла solves")

# Blender всегда едет с 0 по возрастанию, а таймкод трекера может начинаться с чего угодно
keys.sort(key=lambda k: k[0])
sc = bpy.context.scene
t0 = int(keys[0][0])
cam.rotation_mode = 'QUATERNION'
for i, (tc, loc, rot) in enumerate(keys):
    frame = sc.frame_start + i
    cam.location = loc
    cam.quaternion = rot
    cam.keyframe_insert("location", frame=frame)
    cam.keyframe_insert("quaternion", frame=frame)

sc.frame_start = sc.frame_start
sc.frame_end = sc.frame_start + len(keys) - 1
print(f"решено кадров: {len(keys)}, таймкод трекера начинался с {t0}, "
      f"в сцене: {sc.frame_start}..{sc.frame_end}")

# камера должна попасть в кадр
cam.data.clip_start = 0.1
cam.data.clip_end = 100.0
cam.data.dof.use_dof = False        # трекер не даёт дистанцию: DOF по фокусу сработает неверно
```

### Этап 5. Два режима рендера в одной сцене

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32                     # для стены хватает немного: картинка плоская
sc.cycles.use_denoising = True

# режим 1: контент стены — отдельная камера, отдельный файл, свой набор объектов
sc.camera = bpy.data.objects["Cam_OnWall"]
sc.render.resolution_x, sc.render.resolution_y = 2560, 1360
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGB'
sc.render.filepath = r"//led/frame_"
sc.frame_start, sc.frame_end = 1, 600
bpy.ops.render.render(animation=True)      # 600 кадров — чаще всего очередью, не вручную

# режим 2: финальный кадр — камера площадки, стена выключена, вывод с альфой
sc.camera = bpy.data.objects["Cam_OnStage"]
sc.render.film_transparent = True
sc.render.image_settings.color_mode = 'RGBA'
sc.render.filepath = r"//final/plate_"
```

> [!NOTE]
> Genlock (синхронизация по внешнему тактовому сигналу) и реальный вывод в стену — это уровень сервера рендера и видеопроцессора, а не Blender. В Blender нет функции «принимать внешний синхроимпульс». Настройкой частоты кадров в сцене (`fps`) и перезапуском рендера по таймеру управляют снаружи. Протоколы и конкретные утилиты бери из документации твоего оборудования.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| Геометрия стены | `px × pitch` по каждой оси | всегда; расхождение с соотношением пикселей даёт «резиновую» картинку |
| `Emission.Strength` | 2–4 | яркость стены для камеры |
| `Light Path.Is Camera Ray` | ключ ко всему | без него стена засвечивает сцену |
| `visible_camera = False` | для финального кадра | иначе стена попадёт в кадр поверх видео |
| `is_shadow_catcher` | на полу павильона | тени от актёров без рисования пола |
| `fps` сцены | ровно тот же, что у трекера и камеры | расхождение = рассинхрон нарастающий по времени |
| `samples` | 16–64 для контента стены | стена почти не имеет шума |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Швы и «мыло» на стене | UV не 1:1, растянут Aspect Ratio | перегенерировать UV ровно по формуле `px × pitch` |
| Сцена засвечена, контраст «поплыл» | стена светит во все стороны | `Light Path` + разделение по лучам, понизить `glow` |
| Синхрон уходит к концу съёмки | `fps` сцены не равен `fps` камеры/трекера | выставить одинаково, кадр-в-кадр |
| Камера «прыгает» в моменты проходов | solves с дырами, нет интерполяции | интерполировать ключи, дублировать соседние при пропусках |
| DOF едет не туда | трекер не даёт дистанцию до объекта | фокус ставить вручную или по маркеру, `use_dof` гасить на превью |
| Финальный кадр с «двойной стеной» | стена не выключена из камеры | `visible_camera = False` для финального прохода |
| Цвет стены и реальный свет не совпадают | HDRI павильона не соответствует приборам | снять HDRI на пустой площадке и использовать её |

## ✅ РЕЗУЛЬТАТ

На выходе: сцена с эмиссивной стеной, одной камерой «на стену» и одной камерой «на площадке», плюс две последовательности: контент стены (RGB PNG, 2560×1360, 600 кадров) и финальные плашки с альфой (RGBA, 1600×900 или выше).

Характеристики — **оценка по порядку величины, а не измеренный результат**: 600 кадров 2560×1360 в Cycles на 32 сэмплах с одной плоскостью-эмиттером — от долей секунды до нескольких секунд на кадр на дискретной видеокарте, то есть от единиц минут до десятков минут на всю смену. Реальный стенд с полноценной сценой в 100–300 тыс. полигонов идёт в десятки раз дольше. Объём: один кадр контента стены — единицы мегабайт в PNG; 600 кадров — сотни мегабайт.

**Это оценка.** В реальном продакшене сцену рендерят не в Cycles в одиночку, а распределённо, и скорость определяется узким местом конвейера, а не Blender. Замеряй на своём железе.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md)
- **Теги:** #animation, #pipeline, #render, #texturing, #workflow