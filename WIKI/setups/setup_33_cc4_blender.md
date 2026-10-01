---
id: setup_33_cc4_blender
lang: ru
category: setups
type: setup
status: full
tags: [blender, setup]
---
# SETUP 33: CHARACTER CREATOR 4 → BLENDER

**ID:** SETUP-33 | **Type:** CC Pipeline | **Difficulty:** ⭐⭐ | **Time:** 35 min
**RU/EN Bilingual**

> Когда применять: персонаж сделан в Reallusion Character Creator 4 и нужно либо живую связь с Blender, либо честный FBX-экспорт с shape keys, LOD и нормалями.

## 🎯 ЦЕЛЬ
Настроить пайплайн Reallusion Character Creator 4 → Blender: выбрать правильный режим выгрузки (живой пайплайн против файлового экспорта), корректно перенести материалы, морфы лица и LOD, и проверить, что нормали и микрокарты не развалились. Разбираем разницу между двумя подходами и её последствия для анимации.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Character Creator 4 | подписка (есть триал) | источник персонажа |
| Blender Pipeline Plugin for Blender | ставится из самого CC4 | живая связь CC4 → Blender |
| Blender | версия, поддержанная плагином | приёмник |
| CC-ресурсы | одежда, волосы, детали лица | сам персонаж |

> [!NOTE]
> Blender-пайплайн — не сторонний аддон: его файлы генерирует сама CC4. Устанавливается через `Edit → Preferences → Add-ons → Install` в Blender, при этом путь к файлам плагина задаётся в самой CC4 (`Pipeline → Blender`). Проверь, какая версия Blender поддерживается твоей сборкой CC4 — плагин версионно-чувствителен.

## 🛠️ НАСТРОЙКА

### 1. Сборка персонажа в CC4
Сначала собираем персонажа в самом CC4: тело (Base), одежда, детали лица, материалы. Принцип: всё, что нужно в Blender, должно быть применено **до** выгрузки — на стороне Blender часть параметров уже недоступна.

| Что задать в CC4 | Зачем | Типичная ошибка |
|---|---|---|
| Material Type (Standard / HD) | определяет, какие карты вообще будут выгружены | оставить Standard, потом удивляться отсутствию roughness |
| Sub-division level | влияет на плотность сетки и размер FBX | выставить слишком высокое и получить 3 млн полигонов |
| Morph targets лица | они станут shape keys в Blender | не отметить и потерять мимику |
| Auto-LOD | генерация упрощённых уровней для движка | не включить и грузить LOD0 везде |

### 2. Подготовка Blender
```python
import bpy

# Единицы: CC4 работает в сантиметрах, Blender — в метрах.
# Неверная настройка = персонаж ростом 3 метра или 3 сантиметра.
us = bpy.context.scene.unit_settings
print("scale_length:", us.scale_length, "system:", us.system)

# Чистая сцена — иначе плагин подцепит чужие объекты
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
```

### 3. Вариант A — живой пайплайн CC4
В CC4 открываешь `Pipeline → Blender`, запускаешь соединение, в Blender в появившейся панели выбираешь сцену и нажимаешь импорт. Меш появляется в сцене, и дальше работаешь как с обычной геометрией.

Плюсы: можно перезалить после правок в CC4 без ручного экспорта. Минусы: связь хрупкая — падение коннекта оставляет сцену в промежуточном состоянии, и перед любой тяжёлой операцией (рендер фермы, экспорт) лучше запечь результат в обычные объекты.

```python
# Что реально приехало в сцену
for o in bpy.data.objects:
    if o.type == 'MESH':
        keys = len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0
        print(f"{o.name}: вершин={len(o.data.vertices)} shape_keys={keys}")
```

### 4. Вариант B — файловый экспорт FBX
Когда плагина нет или нужна воспроизводимая выгрузка. В CC4: `Pipeline → Export Settings`, формат FBX, затем экспорт в файл; в Blender — импорт.

```python
bpy.ops.import_scene.fbx(
    filepath=r"C:\work\cc4\char.fbx",
    automatic_bone_orientation=True,
    use_anim=True,
    mesh_smooth_type='FACE',
)
```
В настройках импорта FBX решающими являются `mesh_smooth_type` (как сглаживание выгружено) и `use_custom_normals`, если он доступен в твоей версии.

> [!NOTE]
> `use_custom_normals` был удалён из импортёра FBX в ветке 4.x, где нормали считаются через атрибут mesh. Если параметра нет в списке — это не ошибка установки, а изменение API. Ориентируйся на `mesh.use_auto_smooth` (до 4.1) либо на операторы `shade_smooth_by_angle` / `shade_auto_smooth` в 4.1+.

### 5. Материалы
Материалы CC4 приезжают как набор карт, а не как готовый шейдер Blender. Собираем Principled вручную или через скрипт.

```python
import bpy

mat = bpy.data.materials.get("CC4_Skin") or bpy.data.materials.new("CC4_Skin")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

# Имена сокетов Principled менялись в 4.0 — печатаем, а не угадываем
print("сокеты:", [s.name for s in bsdf.inputs])

for path in ("diffuse", "normal", "roughness", "metallic", "opacity"):
    img = bpy.data.images.load(rf"C:\work\cc4\textures\skin_{path}.jpg",
                               check_existing=True)
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.location = (-600, 200)
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
```

> [!NOTE]
> В Blender 4.0 сокеты Principled BSDF были переименованы (например, `Specular` → `Specular IOR Level`, `Subsurface` → `Subsurface Weight`, `Emission` → `Emission Color`). Сопоставляй по выведенному списку сокетов, а не по памяти.

### 6. Микрокарты и нормали
Отдельная боль CC4: мелкие детали (поры, складки) живут в картах. Без них персонаж выглядит резиновым.

```python
# Проверить, что карты действительно подключены, а не просто лежат в файле
nt = bpy.data.materials["CC4_Skin"].node_tree
for n in nt.nodes:
    if n.type == 'TEX_IMAGE':
        print(n.image.filepath, "| size:", tuple(n.image.size))
```

### 7. LOD для движка
```python
# Считаем бюджет: во сколько раз должен упасть LOD1 относительно LOD0
def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)

for o in bpy.data.objects:
    if o.type == 'MESH':
        print(f"{o.name}: {tris(o)} треугольников")
```
LOD-объекты в CC4 приходят отдельными мешами с готовыми упрощениями; в Blender их нужно либо оставить отдельными объектами, либо вручную применить Decimate.

```python
lod0 = bpy.data.objects.get("char_lod0")
if lod0:
    dec = lod0.modifiers.new("Decimate", 'DECIMATE')
    dec.ratio = 0.5
    dec.use_collapse_triangulate = True
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Сводка перед экспортом в движок
sc = bpy.context.scene
print("объектов:", len(sc.objects))
print("материалов:", len(bpy.data.materials))
print("изображений:", len(bpy.data.images))
print("unit scale:", sc.unit_settings.scale_length)
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `scene.unit_settings.scale_length` | соответствует единицам CC4 | расхождение размера в 100 раз — классика |
| `mesh_smooth_type` | `FACE` | `EDGE` — когда нужны хард-нормали на рёбрах |
| `Decimate.ratio` | `0.5` | меньше — для агрессивного LOD, больше — почти не заметно |
| Material Type в CC4 | `HD` для крупных планов | `Standard` — для игровых ассетов |
| Sub-division level в CC4 | по бюджету полигонов | выше — студийный рендер, ниже — реальное время |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Персонаж в 100 раз больше/меньше | не совпали единицы сцены | Проверить `unit_settings.scale_length` и применить трансформации |
| Плагин Blender в CC4 не находит сцену | не задан путь к Blender в настройках пайплайна | Указать путь в `Pipeline → Blender` и перезапустить CC4 |
| Мимица не переехала | в CC4 не включён экспорт морфов | Отметить Morph targets и перевыгрузить |
| Кожа «резиновая» | не приехали карты деталей | Проверить наличие карт в `bpy.data.images` и подключить к материалу |
| Чёрные полосы на сгибах | нормали не импортированы | `shade_smooth_by_angle` либо настройки сглаживания в CC4 |
| Потеряны RL-специфичные данные | в FBX нет формата для этих данных | Экспортировать в glTF/GLB вместо FBX, если приёмник умеет |
| Экспорт не повторяется из CC4 | ручные правки в Blender не попали обратно | Живой пайплайн — только в одну сторону, правки держи в CC4 |

## 🖥 MCP-ПРОМПТ

```text
RU: "Проверь unit scale, собери Principled из карт CC4,
     выведи список shape keys и LOD-объектов с числом треугольников" /
EN: "Check unit scale, build a Principled shader from CC4 maps,
     list shape keys and LOD objects with triangle counts"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #setup