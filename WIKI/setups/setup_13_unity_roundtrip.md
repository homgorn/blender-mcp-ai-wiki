---
id: setup_13_unity_roundtrip
lang: ru
category: setups
type: setup
status: full
tags: [blender, setup, unity]
---
# SETUP 13: BLENDER + UNITY ROUNDTRIP

**ID:** SETUP-13 | **Type:** Game Engine | **Difficulty:** ⭐⭐ | **Time:** 20-30 min
**RU/EN:** Двуязычный файл / Bilingual

---

> Когда применять: когда ассеты делаются в Blender, а собираются и рендерятся в Unity — и нужно, чтобы импорт был предсказуемым, а не «повезло с осями и масштабом».

## 🎯 ЦЕЛЬ

Настроить двусторонний обмен Blender ↔ Unity так, чтобы геометрия приходила в правильном масштабе, с правильными нормалями и материалами, а мелкие правки из Unity возвращались обратно без разрушения исходника.

Главное в этом обмене — не формат файла, а **договор о состоянии сцены перед экспортом**: применённый масштаб, единицы, отсутствие модификаторов, которые ещё не применены, и согласованная система имён. Формат — это деталь; состояние — это то, из-за чего импорт ломается.

Отдельно стоит понимать разницу двух мостов: FBX (классический, с историей и багами) и glTF 2.0 (современный, с материалом и текстурами внутри одного файла). В Unity оба поддерживаются, выбор влияет на то, что переживает экспорт, а что нет.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | любая актуальная, экспортёр — в комплекте | FBX и glTF экспортируются штатно, плагины не нужны |
| Unity | актуальный LTS | импортёр FBX и glTF встроены в редактор |
| Пакет экспорта FBX из Unity | проверь, установлен ли | нужен только для обратного пути Unity → Blender |
| Текстуры | отдельными файлами либо вшитыми в GLB | для FBX — только отдельными файлами |
| Нейминг-конвенция | одна на проект | без неё префабы собираются вручную |

## 🛠️ НАСТРОЙКА

### Шаг 1. Единицы, масштаб и оси

Blender и Unity оба считают в метрах, поэтому масштабировать сцену для переноса не нужно. Нужно сделать так, чтобы Blender не «помнил» нестандартный масштаб объектов.

```python
import bpy

# Применить масштаб ко всем мешам: экспортировать объект с scale = (1, 1, 1)
def apply_scale_and_fix_rotation(objects=None):
    objects = objects or [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

apply_scale_and_fix_rotation()
```

Про оси: Blender — Z-up, Unity — Y-up. Это **не** требует ручного поворота объектов. Ориентация оси — свойство формата, и конвертер FBX/glTF переводит её сам. Поворот всего на 90° «на всякий случай» — самая частая причина ассетов, лежащих на боку.

> [!NOTE]
> Набор флагов оси у экспортёров (`axis_forward`, `axis_up` у FBX и `export_yup`
> у glTF) менялся между версиями Blender. Значения по умолчанию рассчитаны на
> Y-up-движки и менять их обычно не нужно. Если пришлось переопределять — сначала
> проверь, что не сломана сама сцена, и только потом крути флаги.

### Шаг 2. Применить модификаторы перед экспортом

Модификаторы вроде `Subdivision Surface`, `Mirror`, `Array` живут в файле и **не** переносятся в Unity: FBX и glTF несут только итоговую сетку. Дублировать их в движке — ручная работа, которая разъедется с исходником.

```python
import bpy

def apply_modifiers(objects=None):
    objects = objects or [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for ob in objects:
        bpy.context.view_layer.objects.active = ob
        for mod in list(ob.modifiers):
            # Для неразрушающих (Bevel, Solidify) применение не обязательно:
            # решает задача, а не инструмент. Здесь применяем всё геометрическое.
            bpy.ops.object.modifier_apply(modifier=mod.name)

apply_modifiers()
```

### Шаг 3. Экспорт FBX

```python
import bpy

bpy.ops.export_scene.fbx(
    filepath="//exports/unity/prop.fbx",
    use_selection=True,
    apply_unit_scale=True,
    object_types={'ARMATURE', 'MESH'},
    # Только кости деформации: служебные кости в Unity мешают и раздувают скелет
    use_armature_deform_only=True,
    add_leaf_bones=False,
    bake_anim=True,
    # Кадр 1 = текущий кадр сцены. Без этого скелет уезжает в дефолтный позу
    bake_anim_use_nla_strips=True,
)
```

`path_mode` стоит выставить явно: `'COPY'` копирует текстуры рядом с `.fbx`, `'RELATIVE'` оставляет ссылку на исходный путь. `'AUTO'` по умолчанию ведёт себя по-разному в зависимости от того, запущен ли Blender из интерфейса или в фоне — а это ровно тот случай, когда локально работает, а в CI нет.

```python
bpy.ops.export_scene.fbx(
    filepath="//exports/unity/prop.fbx",
    use_selection=True,
    path_mode='COPY',
    embed_textures=False,     # True упакует текстуры внутрь FBX — крупный файл
)
```

> [!NOTE]
> Полный список допустимых значений `path_mode` и `mesh_smooth_type` смотри
> в `File → Export → FBX` или через
> `bpy.ops.export_scene.fbx.get_rna_type().properties["path_mode"].enum_items`.
> Значения `path_mode` и состав свойств менялись между версиями Blender.

### Шаг 4. Альтернатива: glTF 2.0

Если проект не привязан к FBX, glTF обычно предпочтительнее: материал, текстуры и анимация лежат в одном файле, а не рядом пачкой, и не нужно гадать, куда экспортировались текстуры.

```python
bpy.ops.export_scene.gltf(
    filepath="//exports/unity/prop.glb",
    export_format='GLB',            # GLB = один файл; GLTF_SEPARATE = .gltf + .bin + текстуры
    use_selection=True,
    export_apply=True,              # применить модификаторы на лету
    export_yup=True,                # glTF по спецификации Y-up
    export_materials='EXPORT',
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_animations=True,
    export_frame_range=True,
    export_skins=True,
)
```

Сжатие Draco в glTF даёт сильно меньший файл, но требует поддержки на стороне импорта: в Unity и в Godot Draco воспринимается по-разному в зависимости от импортёра и версии. Если размер не критичен, держите сжатие выключенным — сэкономите много времени на отладке.

### Шаг 5. Текстуры: цвет против данных

Цветовая текстура и карта данных — это разные миры, и путаница между ними даёт классические артефакты: слишком тёмное зерно, «вывернутые» блики, странные тени.

| Blender | Тип в Unity | Что произойдёт при ошибке |
|---|---|---|
| Base Color | sRGB | корректно |
| Metallic | Non-Color (Raw) | каналы пересчитаются, металл станет грязным |
| Roughness | Non-Color | зеркальность «поплывёт» по тону |
| Normal map (OpenGL) | Normal map | без флага Flip Y свет будет инвертирован по вертикали |
| Ambient Occlusion | Non-Color | тени слишком тёмные |
| Emission | sRGB | свечение темнее ожидаемого |

Нормали из Blender используют соглашение OpenGL: ось Y вниз. Unity ожидает ось Y вверх. Если рельеф выглядит «вдавленным» вместо выпуклого — это переворот, и лечится флагом **Flip Green Channel** в импортёре, а не перевёрнутой текстурой в редакторе.

### Шаг 6. Метаданные, по которым Unity собирает префабы

Unity не знает, что такое Blender-объект. Всё, что не выражено геометрией и именем, переносится через пользовательские свойства (custom properties) или через соглашение об именах.

```python
import bpy

# Соглашение об именах + метаданные, которые переживают экспорт.
# Unity собирает префаб по префиксу и читает поля как строки.
obj = bpy.data.objects["Barrel_Mesh"]
obj["ucx_enabled"] = True           # коллайдер: бокс по габаритам
obj["ucx_width"] = 0.65
obj["ucx_depth"] = 0.45
obj["ucx_height"] = 0.95
obj["lod1_screen"] = 0.45           # порог переключения LOD в долях экрана
obj["material_guide"] = "wood_painted"

# Переименовать коллайдеры так, чтобы Unity их подхватил
collider = bpy.data.objects.get("Col_Barrel")
if collider:
    collider.name = "UCX_Barrel_00"
```

> [!NOTE]
> Экспорт пользовательских свойств в FBX зависит от версии Blender и от флага
> экспорта свойств объекта — в разных сборках он то включается, то требует
> явного флага. Проверь, доезжают ли свойства, простым тестом: экспортируй один
> объект, открой `.fbx` текстовым редактором и поищи своё имя. Если его нет —
> не полагайся на этот канал и переходи на соглашение об именах.

### Шаг 7. Обратный путь: из Unity в Blender

Импорт из Unity нужен, когда асет уехал в движок и вернулся с правками рига или формы. Шаги обратные, но ловушки те же.

```bash
# Экспорт из Unity: в редакторе выделить модель,
# Assets → Export → FBX..., выбрать, что включать в файл, и нажать Export.
# Проверь, что пакет экспорта FBX установлен в твоей версии редактора.

# Импорт результата в Blender
blender -b --python-expr "import bpy; bpy.ops.import_scene.fbx(filepath='D:/exports/unity/Barrel.fbx', automatic_bone_orientation=True)"
```

Обратный импорт почти всегда приносит масштаб, отличный от ожидаемого, и переименованные кости. Перед записью обратно в исходный файл результат надо проверить и, если нужно, привести трансформации к тому же состоянию, что было до экспорта.

### Шаг 8. Пакетная выгрузка каталога

```python
# scripts/export_for_unity.py
import bpy, os, sys, argparse

argv = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser()
p.add_argument("--out", default="//exports/unity/")
p.add_argument("--format", choices=["FBX", "GLB"], default="GLB")
args = p.parse_args(argv)

os.makedirs(bpy.path.abspath(args.out), exist_ok=True)

for ob in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    path = os.path.join(bpy.path.abspath(args.out), ob.name + "." + args.format.lower())
    if args.format == "FBX":
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, path_mode='COPY')
    else:
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB',
                                  use_selection=True, export_apply=True)
    print("exported:", path)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `apply_unit_scale` | `True` | иначе Unity применит свой `Scale Factor` поверх |
| `use_selection` | `True` в скриптах | в интерактивном режиме выбор делает пользователь |
| `use_armature_deform_only` | `True` | кости управления нужны только если их импортируют обратно |
| `path_mode` (FBX) | `COPY` | `RELATIVE` ломается при переносе проекта, `AUTO` ведёт себя по-разному в фоне |
| `export_apply` (glTF) | `True` | применение модификаторов на лету вместо ручного |
| `embed_textures` | `False` | `True` даёт один большой файл, который неудобно версионировать |
| Flip Green Channel (Unity) | `True` для нормалей из Blender | выключать только если в проекте используется DirectX-конвенция |
| Texture Type (Unity) | sRGB для Base Color, Non-Color для карт данных | ошибка здесь видна как «грязный» металл и проваленные тени |
| масштаб объекта перед экспортом | строго `1.0` | применить один раз в скрипте, а не руками |
| система координат вручную | не трогать | Unity сам приводит ориентацию при импорте |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Ассет в Unity в 100 раз больше | не применён масштаб объекта | `transform_apply(scale=True)` перед экспортом |
| Ассет лежит на боку | ручной поворот сцены «под движок» поверх встроенной конвертации | вернуть объекты в исходную ориентацию, оставить `export_yup` |
| Кадр анимации импортируется в позу «T» | `bake_anim` без кадра | указать кадр диапазона, проверить результат в редакторе |
| Нормали вдавленные | соглашение OpenGL против Unity | Flip Green Channel в импортёре |
| Металл выглядит грязным | карта Metallic импортирована как sRGB | сменить Texture Type на Normal/Single channel |
| Текстуры потерялись при переносе папки | `path_mode='RELATIVE'` или `'AUTO'` | явно `path_mode='COPY'` |
| Превью в Unity темнее, чем рендер | сцена без HDRI и без правильных light probes | это не ошибка экспорта; настрой освещение в движке |
| Кастомные свойства не доехали | FBX-экспорт свойств зависит от версии | перейти на соглашение об именах и префиксы |
| Ошибка `TypeError` на флаге экспорта | флаг из другой версии Blender | сверить список через `get_rna_type().properties` |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #setup, #unity