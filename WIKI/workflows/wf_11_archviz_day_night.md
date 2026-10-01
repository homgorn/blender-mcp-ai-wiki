---
id: wf_11_archviz_day_night
lang: ru
category: workflows
type: workflow
status: full
tags: [archviz, workflow]
---
# WF 11: ARCHVIZ DAY→NIGHT

**ID:** WF-11 | **Type:** ArchViz | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: Sun+HDRI morph, lightmix, 2 renders blend
EN: Sun+HDRI morph, lightmix, 2 renders blend

Один `.blend`, который даёт **два состояния** — яркий день и ночь — без дублирования
сцены, и один параметр `daynight` от 0 (ночь) до 1 (день), который переключает их.
Ключевая мысль: день и ночь различаются не «яркостью», а **составом света**. Днём
источник один — солнце, и всё остальное почти не работает. Ночью источников много
(фонари, окна, интерьер), они разного цвета и стоят на разной высоте. Если просто
потушить `Sun.energy`, получится не ночь, а выключенный свет.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | Cycles (EEVEE годится для превью) |
| HDRI day + HDRI night | Poly Haven, 1–2k | рефлексы в стекле и на полу |
| Модель помещения/экстерьера | GLB/FBX | геометрия |
| Эмиссивные материалы на окнах | — | «живые» окна ночью |

## 🛠 НАСТРОЙКА

### Этап 1. Одна ручка на весь свет

Все источники, HDRIs и эмиссия завязываются на одно свойство сцены. Это и есть
«lightmix» из постановки — не микс-нода, а один параметр.

```python
import bpy, math

scene = bpy.context.scene
scene["daynight"] = 1.0                                  # 1 = день, 0 = ночь
scene.id_properties_ui("daynight").update(
    min=0.0, max=1.0, description="0 = ночь, 1 = день")

def drive(owner, path, index, expr):
    """Драйвер от scene['daynight'] с именем переменной t."""
    fc = owner.driver_add(path, index) if index >= 0 else owner.driver_add(path)
    d = fc.driver
    d.type = 'SCRIPTED'
    v = d.variables.new()
    v.name, v.type = "t", 'SINGLE_PROP'
    v.targets[0].id = scene
    v.targets[0].data_path = '["daynight"]'
    d.expression = expr
    return d
```

### Этап 2. Солнце: высота, энергия, температура

```python
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.object
sun.name = "Sun"

# Половина углового диаметра Солнца (~0.53°) — иначе тени неестественно резкие
sun.data.angle = math.radians(0.53)
sun.rotation_euler = (math.radians(52), 0, math.radians(-70))

# Ночью солнце уходит под горизонт и гаснет. Квадрат — чтобы в сумеречный
# момент не было вспышки на линейной шкале.
drive(sun, "rotation_euler", 0, "0.12 + 0.79*t")       # 7° → 52°
drive(sun.data, "energy", -1, "0.02 + 4.8*t*t")

# Цвет: ночью холодный и синий, днём тёплый. Три драйвера — по одному на канал.
drive(sun.data, "color", 0, "0.45 + 0.55*t")
drive(sun.data, "color", 1, "0.60 + 0.36*t")
drive(sun.data, "color", 2, "1.00 - 0.18*t")
```

### Этап 3. World: небо днём, HDRI ночью

```python
world = bpy.data.worlds.new("ArchViz") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()

tex_env = nt.nodes.new("ShaderNodeTexEnvironment")
tex_sky = nt.nodes.new("ShaderNodeTexSky")
mix     = nt.nodes.new("ShaderNodeMixShader")
bg      = nt.nodes.new("ShaderNodeBackground")
bg_day  = nt.nodes.new("ShaderNodeBackground")          # почти прозрачный — свет даёт Sun
bg_night= nt.nodes.new("ShaderNodeBackground")
out     = nt.nodes.new("ShaderNodeOutputWorld")

tex_sky.sky_type = 'NISHITA'
tex_sky.sun_elevation = math.radians(40)
tex_sky.sun_rotation = math.radians(-70)

tex_env.image = bpy.data.images.load("//hdri/night_street_1k.hdr")
bg_night.inputs["Strength"].default_value = 0.25
bg_day.inputs["Strength"].default_value = 0.0          # днём небо рисует Sun, а не фон

nt.links.new(tex_sky.outputs["Color"], bg.inputs["Color"])
nt.links.new(tex_env.outputs["Color"], bg_night.inputs["Color"])
nt.links.new(tex_sky.outputs["Color"], mix.inputs[1])
nt.links.new(bg_night.outputs["Background"], mix.inputs[2])
nt.links.new(bg.outputs["Background"], mix.inputs[1])
nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
```

> [!NOTE]
> У `ShaderNodeTexSky` в разных версиях менялись имена входов (`sun_elevation`,
> `sun_rotation`, `sun_intensity`) и набор режимов `sky_type`. Проверь список входов
> у ноды в своей версии — если поле называется иначе, код упадёт на `tex_sky.xxx`.

### Этап 4. Ночной свет: окна и интерьер

Окна — не лампы, а эмиссия на материале. Это даёт мягкое свечение, которое видно и
в отражениях, и на фасаде.

```python
# Окна
mat_win = bpy.data.materials["Mat_Window"]
pbsdf = mat_win.node_tree.nodes["Principled BSDF"]
drive(pbsdf.inputs["Emission Strength"], "default_value", -1, "6.0*(1.0 - t)")

# Уличные фонари: Point/Area, гаснут днём
for name, energy_day in (("Lamp_01", 180.0), ("Lamp_02", 140.0)):
    ob = bpy.data.objects.get(name)
    if ob:
        drive(ob.data, "energy", -1, f"{energy_day}*(1.0 - t)")

# Интерьерный свет — самый слабый по мощности, но самый заметный для глаза
drive(bpy.data.objects["Interior_Fill"].data, "energy", -1, "45.0*(1.0 - t)")
```

### Этап 5. Рендер двух состояний

```python
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'

for name, t in (("day", 1.0), ("night", 0.0)):
    scene["daynight"] = t
    bpy.context.view_layer.update()          # без этого драйверы не пересчитаются
    scene.render.filepath = f"//render/interior_{name}.png"
    bpy.ops.render.render(write_still=True)
```

### Этап 6. Сведение в композит-нодах

```python
scene.use_nodes = True
nt = scene.node_tree
nt.nodes.clear()

img_day   = nt.nodes.new("CompositorNodeImage"); img_day.image  = bpy.data.images.load("//render/interior_day.png")
img_night = nt.nodes.new("CompositorNodeImage"); img_night.image= bpy.data.images.load("//render/interior_night.png")
glare = nt.nodes.new("CompositorNodeGlare")
glare.glare_type = 'FOG_GLOW'                # только ночью; для дня отключи ноду
mixc = nt.nodes.new("CompositorNodeMixRGB")
comp = nt.nodes.new("CompositorNodeComposite")

nt.links.new(img_day.outputs["Image"],   mixc.inputs[1])
nt.links.new(img_night.outputs["Image"], mixc.inputs[2])
nt.links.new(glare.outputs["Image"],     mixc.inputs[2])
nt.links.new(mixc.outputs["Image"],       comp.inputs["Image"])
drive(mixc.inputs[0], "default_value", -1, "1.0 - t")   # t=1 → день, t=0 → ночь
scene.render.filepath = "//render/interior_dn_"
bpy.ops.render.render(animation=True)
```

> [!NOTE]
> В свежих версиях Blender нода Glare получила порты вместо полей: `Threshold`,
> `Strength` и `Quality` могут быть входами. Если `glare.glare_type` не пишется —
> открой ноду в композиторе и посмотри, что осталось свойством, а что стало входом.

### Этап 7. Анимация перехода «день → ночь»

Сам переход делается анимацией одного ключа: 48 кадров (2 с при 24 fps) с линейной
интерполяцией. Все источники разъезжаются сами, потому что завязаны на `daynight`.

```python
# Ключ на самом свойстве сцены — единственное, что нужно анимировать
scene["daynight"] = 1.0
scene.keyframe_insert('["daynight"]', frame=1)
scene["daynight"] = 0.0
scene.keyframe_insert('["daynight"]', frame=48)

# Тип интерполяции задаётся в Graph Editor (F-кривая сцены).
# Линейная обязательна, иначе между ключами будет «плато».
scene.frame_start, scene.frame_end = 1, 48
scene.render.filepath = "//render/dn_transition_"
bpy.ops.render.render(animation=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `scene["daynight"]` | 0…1 | единственная ручка; 0.3–0.7 даёт «сумерки» |
| `sun.data.angle` | 0.53° | до 2° = мягкие тени, «пасмурно» |
| `bg_night.Strength` | 0.25 | поднимать, если ночью не видно отражений |
| `Emission Strength` | 6.0 | выше 10 — окна «сгорают» в чистом виде |
| `cycles.samples` | 256 | 512 для финального света с окнами |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Файлы | `interior_day.png`, `interior_night.png` (1920×1080, 16 бит) + `interior_dn_####.png` |
| Сегмент анимации | 2 состояния × 1 кадр, либо 24-кадровый переход при анимации `daynight` |
| `.blend` | один файл, в котором слайдер переключает свет без пересборки |
| Рендер | 256 сэмплов, 1920×1080, interior: **4–12 мин/кадр**; два состояния ≈ 10–25 мин |

Переход «день→ночь» как видео делается анимацией одного ключа на `scene["daynight"]`
с линейным интерпейсом: 48 кадров (2 с при 24 fps) — и микшёр сам разедет свет,
HDRIs, эмиссию и фонари синхронно.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Ночью сцена чёрная | `Sun` всё ещё даёт энергию либо HDRI не назначен | проверить `scene.world` и `tex_env.image`; при `t=0` энергия солнца должна быть ≈ 0 |
| Днём небо плоское | в Background дневного неба `Strength = 0` | это нормально: небо рисует `Sun`; если нужно и небо — верни небо в Background |
| Переключил `daynight`, картинка не изменилась | драйверы не пересчитались | `bpy.context.view_layer.update()` или `scene.frame_set(frame + 1)` |
| Слишком жёлтый ночной свет | не разделён цвет фонарей и окон | температуру задавать в `light.data.color`, а не тонировать кадр в композитe |
| Окна светятся днём | забыл `Emission Strength` в драйвер | `(1.0 - t)` обязателен на каждой эмиссии |
| Тени «плывут» при анимации | солнце ключевано без `Rotation`/`Rotation Mode` | проверить `sun.rotation_mode` и единицы (`DEGREES`) |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 06: ARCHVIZ WORKFLOW](wf_06_archviz_workflow.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md)
- **По темам:** [CASE 01: ARCHVIZ INTERIOR](../cases/case_01_archviz_interior.md), [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md)
- **Теги:** #archviz, #workflow