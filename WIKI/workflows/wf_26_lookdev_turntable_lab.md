---
id: wf_26_lookdev_turntable_lab
lang: ru
category: workflows
type: workflow
status: full
tags: [lookdev, product, workflow]
---
# WF 26: LOOKDEV TURNTABLE LAB

**ID:** WF-26 | **Type:** Lookdev | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда модель готова, но непонятно, как она будет выглядеть — при каком свете, в каком материале и не ломается ли силуэт при повороте. Это диагностика, а не продакшн-рендер.

## 🎯 ЦЕЛЬ

Собирается матрица превью: объект × несколько HDRI × несколько световых схем × несколько вариантов материала, плюс turntable-облёт на 360°. На выходе — папка с именованными кадрами, по которым видно, какой свет врал, какой материал читается, и где модель «сдувается» сбоку.

Принцип, который отличает лабораторию от «посмотреть в рендере»: **все кадры делаются за один прогон одним скриптом с неизменной камерой**. Если каждый кадр снимается отдельно, камера и экспозиция «уплывают», сравнивать нечего.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | базовый | предсказуемый свет и отражения |
| Набор HDRI (`.hdr`) | 4–6 штук в `//hdri/` | лестница условий |
| Объект на чистом фоне | без реквизита | иначе непонятно, что видно |
| Плавный фон | плоскость или world | камешка не «висит в пустоте» |
| Таблица вариантов | можно прямо в статье как шаблон | воспроизводимость |

> [!NOTE]
> HDRIs с Poly Haven приходят файлами `.hdr`/`.exr` — их нужно скачать и положить в проект вручную; отдельного MCP-инструмента для скачивания HDRI в этом сервере нет. Имена файлов в примерах ниже условные.

## 🛠️ НАСТРОЙКА

### Этап 1. Лабораторная сцена

Ничего лишнего: объект, камера, пол. Никаких декораций — они съедают контраст и прячут ошибки материала.

```bash
RU: "Собери лабораторную сцену: плоскость 'Backdrop' 20x20 м,
     объект 'Product' по центру, камера 50 мм на расстоянии 2.2 м,
     рендер 1000x1000, без DOF, view_transform = Standard"
EN: "Build a lab scene: plane 'Backdrop' 20x20 m, object 'Product' at origin,
     50 mm camera at 2.2 m, render 1000x1000, no DOF, view_transform = Standard"
```

```python
import bpy, math
sc = bpy.context.scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.001))
back = bpy.context.active_object; back.name = "Backdrop"
m = bpy.data.materials.new("Mat_Backdrop"); m.use_nodes = True
b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
b.inputs['Base Color'].default_value = (0.18, 0.19, 0.21, 1)
b.inputs['Roughness'].default_value = 0.55      # не зеркало: иначе фон даёт лишний блик
back.data.materials.append(m)

bpy.ops.object.camera_add(location=(1.55, -1.55, 1.0))
cam = bpy.context.active_object; cam.data.lens = 50
cam.data.dof.use_dof = False                    # DOF выключен намеренно: размытие мешает оценке
c = cam.constraints.new('TRACK_TO'); c.target = bpy.data.objects["Product"]
c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
sc.camera = cam

sc.render.resolution_x = sc.render.resolution_y = 1000
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Standard'   # честная экспозиция, без плёночной сжалки
sc.view_settings.exposure = 0.0
```

> [!NOTE]
> Список доступных `view_transform` зависит от версии и цветовой конфигурации: `Standard`, `Filmic`, `AgX`, `Raw`, `False Color` встречаются в разных наборах. Узнать свои так: `[i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items]`.

### Этап 2. HDRI-лестница

Лестница строится по смыслу: нейтральная студия → жёсткий дневной свет → тёплый закат → холодное ночное окружение. Плюс один кадр с намеренно переэкспонированной средой — он показывает, где форма «разваливается» по светлоте.

```python
import bpy
LADDER = [                       # (файл, strength, подпись)
    ("//hdri/studio_soft.hdr", 0.6, "studio"),
    ("//hdri/sun_hard.hdr",    1.0, "sun"),
    ("//hdri/sunset.hdr",      0.8, "sunset"),
    ("//hdri/night_city.hdr",  0.5, "night"),
]

world = bpy.data.worlds.new("LabWorld")
sc = bpy.context.scene
sc.world = world
world.use_nodes = True
nt = world.node_tree
out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
env = nt.nodes.new("ShaderNodeTexEnvironment")
bg  = next(n for n in nt.nodes if n.type == 'BACKGROUND')
env.projection = 'EQUIRECTANGULAR'
nt.links.new(env.outputs['Color'], bg.inputs['Color'])
nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def use_hdri(path, strength):
    img = bpy.data.images.load(bpy.path.abspath(path), check_existing=True)
    env.image = img
    bg.inputs['Strength'].default_value = strength
    return img
```

### Этап 3. Световые лестницы

Четыре схемы: чистый HDRI, студийная трёхточка, один жёсткий источник, верхний свет. Разница между ними и есть ответ на вопрос «почему модель выглядит плохо».

```python
import bpy
from mathutils import Vector

def clear_lights():
    for ob in list(bpy.data.objects):
        if ob.type == 'LIGHT':
            bpy.data.objects.remove(ob, do_unlink=True)

def add_area(name, loc, energy, size, target, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy; ld.size = size; ld.color = color
    ob = bpy.data.objects.new(name, ld); bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    c = ob.constraints.new('TRACK_TO'); c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return ob

def rig(kind, target):
    clear_lights()
    if kind == "three_point":
        add_area("K", (1.8, -1.8, 2.2), 500, 1.5, target)
        add_area("F", (-2.0, -1.2, 1.0), 150, 2.5, target)
        add_area("R", (-1.0, 2.2, 1.8), 300, 0.6, target, (0.85, 0.9, 1.0))
    elif kind == "hard":
        add_area("K", (2.2, -2.2, 2.6), 900, 0.25, target)   # маленький источник = резкая тень
    elif kind == "top":
        add_area("T", (0, 0, 3.0), 700, 2.0, target)
    elif kind == "bounce":
        add_area("K", (1.6, -1.6, 1.6), 400, 1.2, target)
        add_area("B", (0, 0.5, 0.15), 120, 4.0, target, (1.0, 0.95, 0.9))  # отражение снизу
```

### Этап 4. Варианты материала

Меняй только то, что реально меняет восприятие. Десять «почти одинаковых» вариантов — это десять зря потраченных кадров.

```python
import bpy
VARIANTS = {
    "matte":     dict(metallic=0.0, rough=0.65, coat=0.0),
    "satin":     dict(metallic=0.0, rough=0.25, coat=0.0),
    "gloss":     dict(metallic=0.0, rough=0.08, coat=0.0),
    "coat":      dict(metallic=0.0, rough=0.15, coat=0.8),   # лак: автоприрода, посуда, мебель
    "metal_raw": dict(metallic=1.0, rough=0.35, coat=0.0),
    "metal_pol": dict(metallic=1.0, rough=0.12, coat=0.0),
}

def apply_variant(obj, name):
    v = VARIANTS[name]
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes:
            continue
        b = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        for sock, key in (('Metallic', 'metallic'), ('Roughness', 'rough')):
            s = b.inputs.get(sock)
            if s: s.default_value = v[key]
        coat = b.inputs.get('Coat Weight') or b.inputs.get('Clearcoat')
        if coat: coat.default_value = v['coat']
        return True
    return False
```

> [!NOTE]
> Сокеты `Coat Weight` / `Clearcoat` — это одно и то же поле в разных версиях: в 4.x Principal BSDF переименован и получил `Coat Weight`, `Coat Roughness`, `Specular IOR Level`. Код выше проверяет оба имени; на других переименованиях (например `Transmission Weight` вместо `Transmission`) может понадобиться добавить вариант — смотри фактические имена сокетов, а не этот список.

### Этап 5. Прогон матрицы

Имена файлов кодируют всё, что нужно для сравнения. Это дешевле, чем «какой это был кадр».

```python
import bpy, os
sc = bpy.context.scene
obj = bpy.data.objects["Product"]
target = obj

MATRIX = [(hd, st, rig_k, var)
          for hd, (_, st, _) in LADDER
          for rig_k in ("hdri_only", "three_point", "hard")
          for var in ("matte", "satin", "coat")]
# это 4x3x3 = 36 кадров — много; для первого прохода бери 2 HDRI x 2 схемы x 3 материала = 12

os.makedirs(bpy.path.abspath("//lab"), exist_ok=True)
sc.cycles.samples = 32          # черновик лестницы: быстро и шумно
done = 0
for hdri_path, strength, hdri_name in LADDER[:2]:
    for rig_kind in ("hdri_only", "three_point"):
        if rig_kind == "hdri_only":
            use_hdri(hdri_path, strength)
            clear_lights()
        else:
            rig(rig_kind, target)
            bg.inputs['Strength'].default_value = 0.15   # лампы главные, HDRI — заполнение
        for var in ("matte", "satin", "coat"):
            apply_variant(obj, var)
            sc.render.filepath = f"//lab/{hdri_name}__{rig_kind}__{var}.png"
            bpy.ops.render.render(write_still=True)
            done += 1
print("кадров:", done)
```

### Этап 6. Turntable

Поворот объекта, а не камеры: свет остаётся тем же, и ты видишь, как форма ведёт себя при смене ракурса к источнику.

```python
import bpy, math
pivot = bpy.data.objects.new("Turntable_Pivot", None)
bpy.context.scene.collection.objects.link(pivot)
obj = bpy.data.objects["Product"]
obj.parent = pivot
obj.matrix_parent_inverse = pivot.matrix_world.inverted()

FRAMES = 24                                  # 15° на кадр
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, FRAMES
pivot.rotation_mode = 'XYZ'
for f in range(1, FRAMES + 1):
    pivot.rotation_euler = (0.0, 0.0, math.radians(360.0 * (f - 1) / FRAMES))
    pivot.keyframe_insert("rotation_euler", frame=f)

# цикл замыкается без скачка: последний кадр не доводим до 360
pivot.rotation_euler = (0.0, 0.0, 0.0)
pivot.keyframe_insert("rotation_euler", frame=FRAMES + 1)

sc.render.filepath = r"//lab/turntable_"
bpy.ops.render.render(animation=True)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `view_transform` | `'Standard'` для оценки | в продакшн-кадре — по вкусу |
| `DOF` | выключен | DOF прячет ошибки силуэта |
| HDRI `Strength` | 0.4–1.0 | насколько окружение сильнее ламп |
| Площадь источника | 0.2 м = жёсткий, 2.5 м = мягкий | размер источника, а не расстояние, даёт жёсткость тени |
| `samples` лестницы | 32 | лестница нужна для сравнения, не для красоты |
| `samples` финала | 256–512 | только отобранные варианты |
| Кадров turntable | 24 (15°) | 12 кадров — слишком редко, 48 — избыточно |

| Что смотрим | Где видно ошибку |
|---|---|
| Силуэт | turntable: провалы, «пузыри», вывернутые участки |
| Материал | жёсткий источник: блик должен быть узким и иметь форму, а не пятно |
| Экспозиция | переэкспонированный кадр: где форма теряет границы |
| Отражения | coat-вариант: лак должен давать двойной блик, а не один |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Кадры не сравнимы между собой | экспозиция/камера менялись вручную | один скрипт, неизменная камера, фиксированный `view_transform` |
| Форма «пластиковая» при нулевом HDRI | только HDRI без ламп: нет бликов с формой | добавить жёсткий источник маленького размера |
| Всё чёрное | HDRI не загрузился, `Strength` = 0 | проверить `env.image` не `None` |
| Turntable дёргается на стыке | последний кадр = 360° и дублирует первый | последний кадр ставить в 0°, а не в 360° |
| Матрица заняла час | 36 кадров по 256 сэмплов | сначала черновик 32 сэмпла, потом 3–5 финальных |
| Цвета на кадрах «прыгают» | включён авто-экспотер/авто-баланс | отключить авто-настройки, фиксировать экспозицию вручную |

## ✅ РЕЗУЛЬТАТ

На выходе: папка `//lab/` с 12–36 превью 1000×1000 (имена вида `sun__three_point__coat.png`) и 24 кадра turntable 1000×1000.

Характеристики — **оценка по порядку величины, а не измеренный результат**: сцена из одного объекта, пола и источников — десятки тысяч полигонов, 1–3 материала, одна HDRI-карта (2k HDR — десятки мегабайт в памяти). Один кадр 1000×1000 в Cycles на 32 сэмплах — секунды; 36 кадров лестницы — минуты на средней видеокарте. 24 кадра turntable на 64 сэмплах — те же единицы минут. Кадр PNG 1000×1000 — 1–3 МБ.

**Это оценка.** Реальное время определяется числом источников, объёмом геометрии и железа; измеряй у себя.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 10: PRODUCT TURNTABLE](wf_10_product_turntable.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md)
- **По темам:** [CASE 10: SNEAKER PRODUCT HERO](../cases/case_10_sneaker_product.md), [CASE 14: FOOD RENDER (RAMEN)](../cases/case_14_food_r visualisation.md), [CASE 15: CAR STUDIO CINEMATIC](../cases/case_15_car_studio_cinematic.md), [P50: PORTFOLIO TURNTABLE & QA](../prompts/50_turntable_qa.md)
- **Теги:** #lookdev, #product, #workflow