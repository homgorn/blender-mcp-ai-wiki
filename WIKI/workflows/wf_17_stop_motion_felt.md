---
id: wf_17_stop_motion_felt
lang: ru
category: workflows
type: workflow
status: full
tags: [animation, pipeline, render, shading, texturing, workflow]
---
# WF 17: STOP-MOTION FELT LOOK

**ID:** WF-17 | **Type:** Stylized | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: Stepped interpolation, fuzz texture, fingerprint normal
EN: Stepped interpolation, fuzz texture, fingerprint normal

Пластилиновый кукольный мультфильм: кадры «встают» вместо плавного движения, поверх
материала торчит ворс, а вмятины от пальцев читаются в бликах. Три приёма дают 80 %
узнаваемости, остальное — свет.

Пластилин в stop motion — это не «серый материал»: у него **очень высокая шероховатость,
сильный sheen по краям и лёгкое подповерхностное рассеяние**. Ворс даёт мягкий ореол
вокруг силуэта. Вмятины читаются только если свет скользящий — при frontal-свете их не видно.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | Cycles, Hair-частицы |
| Модель скульпта | GLB/FBX | герой |
| Normal-карта вмятин | 2k, снятая со скульпта | отпечатки пальцев |
| HDRI «студия» | 1k | скользящий ключевой свет |

## 🛠 НАСТРОЙКА

### Этап 1. Тайминг: не 24 кадра в секунду, а позы

Стоп-моушен снимают на 12–15 кадров в секунду, и в каждом кадре поза **держится**. Реализуется
это двумя настройками: рендерим через кадр, а интерполяция — CONSTANT.

```python
import bpy

scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 72

# Каждый второй кадр => на выходе 12 fps. Это и есть «пластилиновый» темп.
scene.frame_step = 2

def set_constant_interpolation(objs):
    """Все ключи объектов -> CONSTANT: между позами нет перехода."""
    for ob in objs:
        ad = ob.animation_data
        if ad is None or ad.action is None:
            continue
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'CONSTANT'
            fc.update()

set_constant_interpolation([o for o in bpy.context.scene.objects if o.animation_data])
```

> [!NOTE]
> В Blender 4.4+ Actions стали многослойными (layered/slotted): `action.fcurves` может
> вернуть пустой список, потому что кривые лежат внутри `layer → strip → channelbag`
> слота. Если после вызова выше анимация всё ещё плавная — обойди дерево через
> `action.layers[*].strips[*].channelbag(ad.action_slot).fcurves` либо примени
> оператор из меню Animation вручную. Проверь структуру своего Action перед
> использованием функции в конвейере.

### Этап 2. Пластилиновый материал

```python
mat = bpy.data.materials.new("Mat_Felt")
mat.use_nodes = True
nt = mat.node_tree
p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

p.inputs["Base Color"].default_value = (0.72, 0.30, 0.22, 1.0)   # терракота
p.inputs["Roughness"].default_value = 0.92                      # почти мат, но не «мел»
p.inputs["Specular IOR Level"].default_value = 0.25             # минимум: пластик не «мокрый»
p.inputs["Sheen Weight"].default_value = 0.55                   # ореол по краям — ключ к «войлоку»
p.inputs["Sheen Roughness"].default_value = 0.25
p.inputs["Subsurface Weight"].default_value = 0.12              # тонкие уши/пальцы просвечивают
p.inputs["Subsurface Radius"].default_value = (0.02, 0.01, 0.008)
p.inputs["Subsurface Scale"].default_value = 0.01

# Мелкая зернистость: без неё пластилин выглядит как крашеный пластик
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 340.0
noise.inputs["Detail"].default_value = 6.0
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.15
bump.inputs["Distance"].default_value = 0.002
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
```

> [!NOTE]
> Названия сокетов Principled BSDF менялись в 4.0: `Sheen` стал `Sheen Weight`,
> `Specular` — `Specular IOR Level`, `Subsurface` — `Subsurface Weight`.
> В версиях до 4.0 использовать старые имена, иначе код упадёт на
> `p.inputs["Sheen Weight"]` с KeyError. Список актуальных имён:
> `[s.name for s in p.inputs]`.

### Этап 3. Ворс: hair-частицы с детьми

```python
hero = bpy.data.objects["Hero"]
bpy.ops.object.particle_system_add()
ps = hero.particle_systems[-1]
st = ps.settings

st.type = 'HAIR'
st.count = 4000            # на объекте ~100k — уже тяжело
st.hair_length = 0.035     # ворс 3.5 см на фигуре 30 см
st.render_type = 'PATH'
st.use_advanced_hair = True

# Дети дают плотность без роста числа частиц
st.child_type = 'INTERPOLATED'
st.child_percent = 5        # % от родителей
st.rendered_child_count = 60
st.child_radius = 0.05
st.child_roundness = 2.0

st.kink = 'CURL'           # ворс завивается, как на войлочной игрушке
st.kink_amplitude = 0.004
st.kink_frequency = 3.0
st.root_radius = 0.0002
st.tip_radius = 0.00005     # кончик тоньше — силуэт «дымит»
```

Материал ворса: полупрозрачный Principled с `Sheen`, а не чёрный — иначе по краям
появится грязная кайма.

```python
fmat = bpy.data.materials.new("Mat_Fuzz")
fmat.use_nodes = True
fp = next(n for n in fmat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
fp.inputs["Base Color"].default_value = (0.85, 0.55, 0.45, 1.0)
fp.inputs["Roughness"].default_value = 0.9
fp.inputs["Sheen Weight"].default_value = 0.8
# Рендер с задержкой в несколько кадров: strand-ов очень много, лучше просчитать один раз
st.render_step = 3
```

### Этап 4. Вмятины от пальцев

Отпечатки — это **микрорельеф**, а не цвет. Поэтому он делается либо нормаль-картой,
либо впечатывается в геометрию.

```python
# Вариант A: нормаль-карта со скульпта
tex = bpy.data.textures.new("Fingerprints", type='IMAGE')
tex.image = bpy.data.images.load("//textures/fingerprints_n.png")
nm = fmat.node_tree.nodes.new("ShaderNodeNormalMap")
nm.inputs["Strength"].default_value = 0.6
fmat.node_tree.links.new(nm.outputs["Color"], fp.inputs["Normal"])

# Вариант B: вмятины в геометрии через Displace
bpy.ops.object.modifier_add(type='DISPLACE')  # на выделенном объекте
disp = bpy.context.object.modifiers["Displace"]
disp.texture = tex
disp.texture_coords = 'LOCAL'
disp.direction = 'NORMAL'
disp.strength = -0.004     # отрицательный = вдавливаем, а не выдавливаем
disp.mid_level = 0.5
```

### Этап 5. Свет: скользящий, иначе вмятины пропадут

```python
import math
bpy.ops.object.light_add(type='AREA', location=(-0.9, -0.7, 1.1),
                        rotation=(math.radians(-40), 0, math.radians(-55)))
key = bpy.context.object
key.name = "KeySlide"
key.data.shape = 'RECTANGLE'
key.data.size, key.data.size_y = 0.35, 1.2    # узкая полоса = скользящий блик
key.data.energy = 120

# Заполняющий очень слабый: контраст = читаемость микрорельефа
bpy.ops.object.light_add(type='AREA', location=(1.2, -1.0, 0.5))
fill = bpy.context.object
fill.data.energy = 15
fill.data.size = 1.5

# Камера: макро-объектив и малая глубина резкости — «кукольность»
cam = bpy.data.objects["Camera"]
cam.data.lens = 85
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 1.4
cam.data.dof.aperture_fstop = 2.8
```

### Этап 6. Дрожание камеры

Рукотворность дают не только позы, но и «дыхание» камеры между дублями.

```python
import math, random
rng = random.Random(11)
for pose, frame in enumerate(range(1, 73, 2), start=1):
    cam.location = (rng.uniform(-0.004, 0.004), rng.uniform(-0.004, 0.004), rng.uniform(-0.002, 0.002))
    cam.rotation_euler.z = math.radians(rng.uniform(-0.4, 0.4))
    cam.keyframe_insert("location", frame=frame)
    cam.keyframe_insert("rotation_euler", index=2, frame=frame)
set_constant_interpolation([cam])
```

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `scene.frame_step` | 2 | 3 при 8 fps, 1 для 24 fps |
| `Sheen Weight` | 0.55 | выше 0.8 — «бархад», а не войлок |
| `Roughness` | 0.92 | 1.0 — крашеный мел |
| `hair_length` | 0.035 | для крупных кукол 0.08 |
| `rendered_child_count` | 60 | выше 150 — рендер встаёт колом |
| `aperture_fstop` | 2.8 | 5.6, если ворс не в фокусе |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Объём | 72 отрендеренных кадра через один = **6 с при 12 fps** |
| Файлы | `felt_0001.png …`, `frame_step = 2`, 1920×1080, Cycles |
| Рендер | 40–180 с/кадр с ворсом и SSS → **1–3.5 часа** на 72 кадра |
| Проход | можно рендерить в 4 раза ниже и апскейлить — стоп-моушен это прощает |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Движение всё равно плавное | `frame_step` не влияет на анимацию, только на рендер | интерполяция должна быть `CONSTANT` |
| `KeyError: "Sheen Weight"` | версия до 4.0 | использовать имя `Sheen` |
| Ворс не рендерится | не задан материал или слишком мал `tip_radius` | назначить материал, поднять `root_radius` до 0.0005 |
| Рендер считается вечно | `rendered_child_count` завышен | 30–60 достаточно, а `child_percent` поднять |
| Вмятины не видны | свет frontal | поставить key сбоку-сверху, узкой полосой |
| Материал выглядит как резина | нет подповерхностного слоя | `Subsurface Weight` 0.1–0.15 |
| Модель «плывёт» между дублями | не применён CONSTANT к камере | прогнать `set_constant_interpolation` и по камере |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [P46: UDIM WORKFLOW](../prompts/46_udim_workflow.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 07: STYLYZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md)
- **Теги:** #animation, #pipeline, #render, #shading, #texturing, #workflow