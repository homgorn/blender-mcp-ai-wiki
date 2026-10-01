---
id: setup_41_hdri_lighting_lab
lang: ru
category: setups
type: setup
status: full
tags: [lighting, setup]
---
# SETUP 41: HDRI LIGHTING LAB

**ID:** SETUP-41 | **Type:** Lighting | **Difficulty:** ⭐⭐ | **Time:** 30 min

> Когда применять: когда сцена «мылит» или наоборот слепит, и нужно за один прогон сравнить поворот HDRI, силу света, варианты Color Management и наличие запечённого GI — и выбрать вариант, а не угадывать.

## 🎯 ЦЕЛЬ

Делаем в Blender повторяемый стенд для оценки освещения: одна HDRI, четыре поворота по Z, три значения силы, два варианта Color Management, сравнение с и без Light Probe. Всё это прогоняется скриптом и рендерится в превью-разрешении, чтобы решение принималось на картинках, а не на глазок в сцене. Заодно проверяем, как HDRI ведёт себя как фон (`film_transparent`) и как добавляет объём — потому что «просто HDRI» и «HDRI как видимый свет» — это разные задачи.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x LTS | стенд |
| HDRI | 2K или 4K EXR | источник и фон |
| Cycles | — | честный GI и запекание |
| GPU | 8+ ГБ VRAM | лестница рендеров |
| Python `itertools` | stdlib | построение комбинаций |

## 🛠️ НАСТРОЙКА

### 1. Готовим стенд: HDR + нейтральная геометрия

```python
import bpy
from mathutils import Euler

scene = bpy.context.scene
scene.render.resolution_x, scene.render.resolution_y = 640, 360
scene.render.film_transparent = False          # False = HDRI виден как фон

def ensure_world() -> bpy.types.World:
    w = scene.world or bpy.data.worlds.new("World")
    scene.world = w
    w.use_nodes = True
    return w

world = ensure_world()
nt = world.node_tree
nt.nodes.clear()

env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(r"C:/assets/hdri/studio_small_08_4k.hdr")
env.location = (-600, 0)

# Поворот HDRI: отдельная нода Mapping, Z-ось = азимут солнца
mp = nt.nodes.new("ShaderNodeMapping")
mp.name = "HDRI_ROT"; mp.location = (-380, 0)
nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])

bg = nt.nodes.new("ShaderNodeBackground"); bg.location = (-120, 0)
out = nt.nodes.new("ShaderNodeOutputWorld"); out.location = (120, 0)
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
print("world готов:", world.name, env.image.name)
```

### 2. Тестовые объекты

Смысл набора в том, что три объекта показывают разные стороны освещения: матовый шар даёт общий уровень и мягкость, тёмный куб — контраст теней и насыщенность, а металлический шар — то, чего не видно больше нигде: блики и форму источников. Именно по металлу видно, что HDRI плохо работает в интерьере: в отражении сразу читаются её световые пятна, а не мягкий градиент.

```python
import bpy

def grey_material(name="M_Grey", v=0.5):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (v, v, v, 1.0)
    b.inputs["Roughness"].default_value = 0.5
    return m

bpy.ops.mesh.primitive_uv_sphere_add(location=(-1, 0, 1), radius=1)
sphere = bpy.context.object
sphere.data.materials.append(grey_material("M_Sphere", 0.5))

bpy.ops.mesh.primitive_cube_add(location=(0.6, 0, 0.5), size=1)
cube = bpy.context.object
cube.data.materials.append(grey_material("M_Cube", 0.18))

bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 2.5, 1), radius=1)
mirror = bpy.context.object           # металл-эталон: сразу видно блики HDRI
mb = bpy.data.materials.new("M_Mirror"); mb.use_nodes = True
mb.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
mb.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.02
mirror.data.materials.append(mb)
print("стенд готов:", [o.name for o in (sphere, cube, mirror)])
```

### 3. Лестница поворотов и силы

```python
import math
import bpy

def set_hdri(rot_z_deg: float, strength: float):
    nt = scene.world.node_tree
    nt.nodes["HDRI_ROT"].inputs["Rotation"].default_value = (0, 0, math.radians(rot_z_deg))
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    bg.inputs["Strength"].default_value = strength
    return rot_z_deg, strength

LADDER = []
for rot in (0, 90, 180, 270):
    for st in (0.5, 1.0, 2.0):
        LADDER.append(set_hdri(rot, st))
print("вариантов:", len(LADDER), LADDER[:3])
```

### 4. Рендерим лестницу в превью

```python
import bpy
from pathlib import Path

OUT = Path(r"C:/renders/hdri_lab")
OUT.mkdir(parents=True, exist_ok=True)

scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

for rot, st in LADDER:
    set_hdri(rot, st)
    scene.render.filepath = str(OUT / f"rot{rot:03d}_st{st:g}.png")
    bpy.ops.render.render(write_still=True)
print("готово:", len(list(OUT.glob("*.png"))), "кадров")
```

### 5. Color Management: смотрим, а не угадываем

```python
import bpy

scene = bpy.context.scene
vs = scene.view_settings
print("view_transform:", vs.view_transform)
print("доступные:", [i.identifier for i in
      type(vs).bl_rna.properties["view_transform"].enum_items])
print("look:", vs.look)
print("available looks:", [i.identifier for i in
      type(vs).bl_rna.properties["look"].enum_items])

for transform in [i.identifier for i in
                  type(vs).bl_rna.properties["view_transform"].enum_items][:6]:
    vs.view_transform = transform
    scene.render.filepath = str(OUT / f"vt_{transform}.png")
    bpy.ops.render.render(write_still=True)
```

### 6. Light Probe и запекание

```python
import bpy

scene = bpy.context.scene
probe = bpy.data.objects.get("LP_Sphere")
if probe is None:
    # Типы LightProbe отличаются между версиями — создаём и смотрим, что получилось
    bpy.ops.object.lightprobe_add(type="SPHERE", location=(0, 0, 1))
    probe = bpy.context.object
    probe.name = "LP_Sphere"
print("probe:", probe.name, probe.data.type)

scene.render.engine = "CYCLES"
scene.cycles.samples = 128
bpy.ops.object.lightprobe_cache_bake(subset="ALL")   # subset: 'ALL' | 'VISIBLE' | 'SELECTED'
print("light cache baked")
```

### 7. HDRI как видимый свет vs как только источник

```python
import bpy

scene = bpy.context.scene
# 1) HDRI светит, фон — прозрачный (для композита поверх рендера в Nuke/AE)
scene.render.film_transparent = True
# 2) HDRI светит и виден в кадре
scene.render.film_transparent = False

# Объём: World Volume Scatter добавляет туман, который читает ту же HDRI
vol = scene.world.node_tree.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Color"].default_value = (0.8, 0.85, 0.95, 1.0)
vol.inputs["Density"].default_value = 0.02
scene.world.node_tree.links.new(
    vol.outputs["Volume"], scene.world.node_tree.nodes["World Output"].inputs["Volume"])
scene.render.filepath = str(OUT / "volumetric.png")
bpy.ops.render.render(write_still=True)
print("volume on")
```

### 8. Рендер-движок: выбираем осознанно

```python
import bpy

scene = bpy.context.scene
# scene.render.engine — динамический enum, состав которого зависит от того,
# какие аддоны включены. Поэтому читаем текущее значение и перебираем варианты
# в try/except, а не полагаемся на список из памяти.
print("сейчас:", scene.render.engine)

for engine in ("CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
    try:
        scene.render.engine = engine
        print("доступен:", engine)
    except TypeError:
        print("недоступен:", engine)

scene.render.engine = "CYCLES"
# EEVEE Next в 4.2+ сильно отличается от старого EEVEE: настройки лучей и AO
# переехали, старые флаги исчезли. Если нужен быстрый превью — сначала Workbench.
print("итог:", scene.render.engine)
```

> [!NOTE]
> Имя `BLENDER_EEVEE_NEXT` существовало только в переходный период, а в 4.2+ движок снова называется `BLENDER_EEVEE`. Поэтому код выше перебирает оба и опирается на `try/except`, а не на зашитое имя.

### 9. Диапазон: почему картинка то «нормальная», то серая

```python
import bpy

scene = bpy.context.scene
vs = scene.view_settings

# Ступеньки экспозиции — самый быстрый способ понять, «серая» картинка из-за
# экспозиции или из-за неверного view transform
for e in (-2.0, -1.0, 0.0, 1.0, 2.0):
    vs.exposure = e
    print(f"exposure {e:+.1f} -> transform {vs.view_transform}, look {vs.look}")

# Сброс и фиксация того, что подходит — иначе стенд невоспроизводим
vs.exposure = 0.0
print("зафиксировано:", vs.view_transform, "|", vs.look)
```

Диапазон источника стоит проверить до рендера, а не после: у HDR-окружения он шире, чем у любого 8-битного формата, и часть яркостей срезается ещё на этапе HDRI, если карта была пережата в LDR.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Прогнать лестницу без открытого Blender
blender --background hdri_lab.blend --python hdri_ladder.py
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `Mapping → Rotation.z` | `0…360°` | «позолотить» сцену — двигай азимут |
| `Background → Strength` | `0.5 / 1 / 2` | больше 2 выжигает, меньше 0.3 даёт плоский свет |
| `view_transform` | `AgX` в 4.x | `Filmic` в 3.x, `Standard` для контроля пересветов |
| `view_settings.exposure` | `-2…+2` | в ступеньках по 0.5 |
| `cycles.samples` | `64` превью / `512` финал | деноизер съедает шум |
| `film_transparent` | `True` для композита | `False` когда HDRI должен быть в кадре |
| `lightprobe_cache_bake` | `subset="ALL"` | `VISIBLE` быстрее, `SELECTED` для отладки одной зоны |
| Volume Scatter `Density` | `0.005–0.05` | выше — «молоко» |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| HDRI не крутится | поворот повешен на объект, а не на Mapping | крути `ShaderNodeMapping`, а не Environment Texture |
| Сцена «кислотная» | `view_transform` = `Standard` при яркой HDRI | `AgX` / `Filmic` |
| Metal-эталон чёрный | HDRI без солнца, только мягкий свет | возьми HDRI с ярким источником в кадре |
| Тени не появляются | HDRI-окружение, а не Area/Sun | HDRI даёт мягкий свет без теней; нужен отдельный источник |
| `lightprobe_add` падает | тип `SPHERE` переименован | напечатай `[i.identifier for i in ...properties['type'].enum_items]` |
| `lightprobe_cache_bake` не найден | запекание только в Cycles | переключи `render.engine` на `CYCLES` |
| Один из 12 кадров чёрный | рендер прервался на долгом кадре | проверь `scene.cycles.max_bounces` и память |
| Volume-туман не видно | нет ограничивающего объёма | добавь куб с Volume Scatter или World Volume |
| Фон виден, а сцены нет | `film_transparent=True` | сохраняй PNG с альфа-каналом |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [P13: LIGHTING & HDRI](../prompts/13_lighting_hdri.md), [P14: CAMERA & COMPOSITION](../prompts/14_camera_composition.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #lighting, #setup
