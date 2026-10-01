---
id: wf_16_npr_anime_render
lang: ru
category: workflows
type: workflow
status: full
tags: [render, stylized, workflow]
---
# WF 16: NPR ANIME RENDER

**ID:** WF-16 | **Type:** Stylized | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

## 🎯 ЦЕЛЬ / Goal
RU: Lineart + toon shader, paint texture, grease pencil FX
EN: Lineart + toon shader, paint texture, grease pencil FX

Аниме-кадр из трёх независимых слоёв, каждый из которых можно перерисовывать отдельно:
**цвет** (2–3 тональных плана, без градиентов), **линия** (контур, крест, перекрытие),
**краска** (hand-painted текстура поверх цвета) плюс Grease Pencil для FX. Такой разбор
нужен не для красоты: линия и цвет в аниме живут в разных темпах — перекрасили небо,
контур трогать не надо.

Ключевой технический факт, который определяет всю сборку: **`Shader to RGB` работает
только в EEVEE**. На Cycles cel-шейдер через `Shader to RGB` не считается — там нужен
либо Freestyle-обводка, либо инвертированная оболочка (inverted hull).

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | EEVEE Next + Freestyle |
| Grease Pencil (3D) | встроенный | FX-штрихи поверх 3D |
| Hand-painted текстура | 2k PNG | слой краски |
| Freestyle | встроенный | контур, отдельный рендер-пасс |

## 🛠 НАСТРОЙКА

### Этап 1. Cel-шейдер: три тона, без градиента

```python
import bpy

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'   # если нет — см. примечание про имя движка
# Плоские цвета «ломаются» при AgX/Filmic: тёмный тон уезжает в серый,
# светлый — в белый. Для сел-шейдера нужен Standard.
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0.0

mat = bpy.data.materials.new("Mat_Toon")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")   # EEVEE ONLY
ramp = nt.nodes.new("ShaderNodeValToRGB")
emis = nt.nodes.new("ShaderNodeEmission")
out  = nt.nodes.new("ShaderNodeOutputMaterial")

diff.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)   # белый: свет считает Shader to RGB
ramp.color_ramp.interpolation = 'CONSTANT'                  # ровные ступени, не градиент
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.12, 0.10, 0.16, 1.0)      # тень
ramp.color_ramp.elements[1].position = 0.42                   # свет
ramp.color_ramp.elements[1].color = (0.72, 0.60, 0.66, 1.0)
el = ramp.color_ramp.elements.new(0.78)                      # блик
el.color = (1.0, 0.96, 0.90, 1.0)

nt.links.new(diff.outputs["BSDF"],    s2rgb.inputs["Shader"])
nt.links.new(s2rgb.outputs["Color"],  ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"],   emis.inputs["Color"])
nt.links.new(emis.outputs["Emission"], out.inputs["Surface"])
```

Пороги 0.42 / 0.78 подбираются под сцену: слишком низкие — свет «съедает» тень,
слишком высокие — всё в один тон. Для персонажа обычно берут 3 ступени, для фона 2.

### Этап 2. Слой краски поверх цвета

Краска должна влиять только на цвет, не на свет. Поэтому её подключают к
`Emission Color`, а `Light Path → Is Camera Ray` позволяет отличить «для зрителя» от
«для отражений».

```python
paint = nt.nodes.new("ShaderNodeTexImage")
paint.image = bpy.data.images.load("//textures/handpaint_face.png")
paint.extension = 'CLIP'
texco = nt.nodes.new("ShaderNodeTexCoord")

lp    = nt.nodes.new("ShaderNodeLightPath")
mixrgb = nt.nodes.new("ShaderNodeMixRGB")
mixrgb.blend_type = 'MULTIPLY'
mixrgb.inputs["Fac"].default_value = 0.85      # 0.85 — краска слегка просвечивает

nt.links.new(texco.outputs["UV"],   paint.inputs["Vector"])
nt.links.new(ramp.outputs["Color"], mixrgb.inputs[1])
nt.links.new(paint.outputs["Color"], mixrgb.inputs[2])
nt.links.new(lp.outputs["Is Camera Ray"], mixrgb.inputs[0])
nt.links.new(mixrgb.outputs["Color"], emis.inputs["Color"])
```

### Этап 3. Обводка: Freestyle

```python
scene.render.use_freestyle = True
scene.render.line_thickness = 1.6
scene.render.line_thickness_mode = 'ABSOLUTE'      # ABSOLUTE = пиксели, не « world units»

fs = bpy.context.view_layer.freestyle_settings
fs.mode = 'EDITOR'
fs.as_render_pass = True        # вынести линии в отдельный пасс — см. этап 5

ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Main")
ls.select_by_edge_types = True
ls.select_silhouette = True            # силуэт объекта
ls.select_border = True                # край меша: глаза, рот, разрез
ls.select_crease = True                # внутренние сгибы
ls.select_external_contour = True
ls.select_material_boundary = False    # иначе каждая грань обведётся
ls.select_edge_mark = False

style = ls.linestyle
style.color = (0.05, 0.04, 0.07)
style.thickness = 1.8
style.alpha = 1.0
style.caps = 'ROUND'                   # круглый конец штриха вместо плоского
```

> [!NOTE]
> Список `select_*` у FreestyleLineSet расширялся между версиями: часть флагов появилась
> позже и в старых сборках отсутствует. Перед продакшном вызови
> `[p.identifier for p in ls.bl_rna.properties if p.identifier.startswith("select")]` —
> это покажет ровно те переключатели, которые есть в твоей версии.

### Этап 4. Grease Pencil FX

```python
# 3D-объект Grease Pencil живёт поверх сцены и рендерится вместе с ней
try:
    bpy.ops.object.gpencil_add(type='3D', location=(0, 0, 0.5))
except TypeError:
    bpy.ops.object.gpencil_add(type='GREASEPENCIL', location=(0, 0, 0.5))
fx = bpy.context.object
fx.name = "FX_Speedlines"

gmat = bpy.data.materials.new("Mat_FX")
gmat.use_nodes = True
fx.data.materials.append(gmat)

# Анимация штрихов: появляются по кадрам, а не существуют все сразу
try:
    sa = fx.data.stroke_animation
    sa.draw_on_anim = True
    sa.frame_offset = 3          # задержка отрисовки на кадр
except AttributeError:
    pass                          # в части версий API анимации штрихов другой
```

> [!NOTE]
> Блок Grease Pencil активно переписывался между 4.0 и 4.3 (появились слои материалов,
> слои данных, новая система хранения). Имена вроде `stroke_animation`, `draw_on_anim`,
> `frame_offset` и способ включения рендера GP-объекта в сцену (`scene.render.use_grease_pencil`
> в старых версиях) — не то, на что стоит закладываться. Открой Grease Pencil в своей
> сборке и проверь по интерфейсу: Data-панель → Animation, Material-панель → Line Art.

### Этап 5. Два прохода: цвет дешевле, линия в полном разрешении

Это главное практическое отличие от фотореализма: **линия рисуется в два раза дороже
цвета**, потому что Freestyle обходит всю геометрию. Отсюда схема «цвет в 1/2, линия в 1:1».

```python
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080

# Проход 1 — цвет без линий
fs.as_render_pass = False
scene.render.use_freestyle = False
scene.render.filepath = "//render/anime_color_"
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(animation=True)

# Проход 2 — только Freestyle-пасс, в полном разрешении
fs.as_render_pass = True
scene.render.use_freestyle = True
scene.render.filepath = "//render/anime_lines_"
bpy.ops.render.render(animation=True)
```

### Этап 6. Сведение в композиторе

```python
scene.use_nodes = True
ntc = scene.node_tree
ntc.nodes.clear()
img_c = ntc.nodes.new("CompositorNodeImage");  img_c.image  = bpy.data.images["anime_color_0001.png"]
img_l = ntc.nodes.new("CompositorNodeImage");  img_l.image  = bpy.data.images["anime_lines_0001.png"]
over  = ntc.nodes.new("CompositorNodeAlphaOver")
comp  = ntc.nodes.new("CompositorNodeComposite")
ntc.links.new(img_c.outputs["Image"], over.inputs[2])   # база — цвет
ntc.links.new(img_l.outputs["Image"], over.inputs[1])   # сверху — линия
ntc.links.new(over.outputs["Image"], comp.inputs["Image"])
```

### Этап 7. Инвертированная оболочка — запасной контур

Если линия нужна «жирная» и с переменной толщиной (обводка от руки), Freestyle не
умеет: он рисует в экранных пикселях, и толщина постоянная. Тогда контур делается
геометрией — второй оболочкой с вывернутыми нормалями.

```python
hero = bpy.data.objects["Hero"]

# Оболочка: копия геометрии, вывернутая наружу, с чёрным самосветящимся материалом
shell = hero.copy()
shell.data = hero.data.copy()
shell.name = "Hero_Outline"
hero.users_collection[0].objects.link(shell)

solid = shell.modifiers.new("Solidify", 'SOLIDIFY')
solid.thickness = 0.006        # толщина обводки в мире, НЕ в пикселях
solid.offset = 1.0
solid.use_flip_normals = True  # нормали наружу — иначе оболочка «съест» модель
solid.use_rim = True

om = bpy.data.materials.new("Mat_Outline")
om.use_nodes = True
oe = om.node_tree.nodes["Principled BSDF"]
oe.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
oe.inputs["Emission Color"].default_value = (0.02, 0.02, 0.03, 1.0)
oe.inputs["Emission Strength"].default_value = 1.0
om.use_backface_culling = True  # видны только «наружные» грани оболочки
shell.data.materials.clear()
shell.data.materials.append(om)
```

> [!NOTE]
> Метод прорисовки прозрачности в EEVEE менялся: в версиях до 4.2 это
> `material.blend_method` (плюс `shadow_method`), начиная с 4.2 (EEVEE Next) —
> `material.surface_render_method`. Если присваивание не сработало, посмотри, что
> доступно: `[p.identifier for p in bpy.types.Material.bl_rna.properties if "blend" in p.identifier or "render_method" in p.identifier]`.

## ⚙️ КЛЮЧЕВЫЕ ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `view_transform` | `'Standard'` | AgX «съедает» плоские тона |
| Ramp positions | 0.42 / 0.78 | 3 тона для героя, 2 (0.55) для фона |
| `line_thickness` | 1.6 | для «крупного плана» 2.2, для общего плана 1.0 |
| `line_thickness_mode` | `'ABSOLUTE'` | `'RELATIVE'` — толщина зависит от расстояния |
| `crease_angle` | ~134° | больше — меньше лишних штрихов на сгибах |

## 📤 РЕЗУЛЬТАТ

| Параметр | Значение |
|---|---|
| Цикл | 96 кадров при 24 fps = **4 с**, 1080p |
| Файлы | `anime_color_####.png` + `anime_lines_####.png` + `anime_####.png` после сведения |
| Слои | цвет (EEVEE cel), Freestyle-пасс, Grease Pencil FX, hand-paint текстура |
| Рендер | EEVEE: цвет 3–8 с/кадр; Freestyle 15–40 с/кадр. Итого **40–90 мин** на 96 кадров |
| Особенность | линия и цвет разделены → перекраска не трогает обводку |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Cel-шейдер чёрный | `Shader to RGB` в Cycles | переключить на EEVEE; в Cycles использовать инвертированную оболочку |
| Тона «плывут» при смене кадра | `ColorRamp` в шейдере не привязан к реальному освещению | добавить Ambient Occlusion node в diffuse-свет |
| Линия обводит каждую грань | включён `select_material_boundary` | выключить, оставить только silhouette/crease/border |
| Толщина линии зависит от кадра | `line_thickness_mode = 'RELATIVE'` | переключить на `'ABSOLUTE'` |
| GP-объект не виден в рендере | слой/видимость GP в новой версии переехала | проверить Data-панель → слои и рендер-флаги Grease Pencil |
| Краска не ложится | нет UV или текстура не в диапазоне 0–1 | `UV → Smart UV Project`, `image.source = 'SEAMLESS'` для бесшовной |
| Рендер в разы медленнее ожидаемого | Freestyle считается по всей геометрии | упростить сетку для прохода линий, отключить Freestyle на невидимых объектах |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md), [WF 18: ISOMETRIC GAME ART](wf_18_isometric_game_art.md), [WF 19: VOXEL ART PIPELINE](wf_19_voxel_art_pipeline.md), [WF 20: KITBASH GREEBLE CITY](wf_20_kitbash_greeble.md)
- **По темам:** [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md), [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md)
- **Теги:** #render, #stylized, #workflow