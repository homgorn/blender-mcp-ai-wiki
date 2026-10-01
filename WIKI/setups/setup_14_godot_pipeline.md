---
id: setup_14_godot_pipeline
lang: ru
category: setups
type: setup
status: full
tags: [blender, godot, pipeline, setup]
---
# SETUP 14: BLENDER + GODOT PIPELINE

**ID:** SETUP-14 | **Type:** Open-source Engine | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

---

> Когда применять: когда ассеты из Blender едут в Godot — а именно туда чаще всего, потому что glTF у Godot единственный нативный формат импорта.

## 🎯 ЦЕЛЬ

Собрать повторяемый путь `Blender → .glb → проект Godot`, на котором геометрия приезжает с правильным масштабом и нормалями, текстуры — с правильным цветовым пространством, а анимация и коллизии не требуют ручной доводки.

Принцип простой: **glTF — это контракт, а не формат**. Всё, что не выражено в контракте (материал Godot, шейдер, физика, LOD-конфигурация), живёт в движке и настраивается уже там. Из Blender в Godot едет геометрия, UV, материал в формате glTF и анимация. Всё остальное — на стороне проекта.

Вторая половина работы — вторая. Экспорт занимает минуту; настройка импорта в редакторе Godot (LOD, окклюзия, коллайдеры, сжатие текстур) занимает часы, и именно она определяет, сколько кадров в секунду получит проект.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | актуальная, со встроенным glTF-экспортёром | экспорт в GLB без плагинов |
| Godot | 4.x | нативный импорт glTF, `MeshInstance3D`, `AnimationPlayer` |
| Расширение текстур KTX2 / Basis | проверь, включено ли в проекте | в разы меньший VRAM, чем у PNG/JPEG |
| Соглашение об именах | одна на проект | без неё коллайдеры и LOD не подхватятся автоматически |
| Модуль Draco в Godot | встроенный | чтение геометрии со сжатием, если включишь его на экспорте |

## 🛠️ НАСТРОЙКА

### Шаг 1. Подготовка сцены перед экспортом

```python
import bpy

def prepare_for_godot(objects=None):
    objects = objects or [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        # Единый масштаб: без этого Godot применит свой корректирующий коэффициент
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        for mod in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)

        # Перевести оси на Y-up заранее, если в проекте это принято:
        # так геометрия в .glb читается без сюрпризов
        o.rotation_mode = 'XYZ'

prepare_for_godot()
```

### Шаг 2. Экспорт GLB

```python
bpy.ops.export_scene.gltf(
    filepath="//exports/godot/prop.glb",
    export_format='GLB',            # один файл: геометрия + текстуры + анимация
    use_selection=True,
    export_apply=True,              # применить модификаторы на лету
    export_yup=True,                # glTF и Godot оба Y-up, конвертация не нужна
    export_materials='EXPORT',
    export_image_format='AUTO',     # оставить исходный формат текстур
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,           # без тангентов не будет нормалей в шейдере
    export_animations=True,
    export_skins=True,
    export_morph=True,
    export_extras=True,             # custom properties -> метаданные в Godot
)
```

Нормали здесь не требуют переворота: glTF и Blender используют одно соглашение, и Godot тоже. Если в проекте вручную делают «Flip Green Channel», почти всегда виноват не формат, а один вручную сохранённый Normal map в стороннем редакторе.

> [!NOTE]
> Параметр режима экспорта анимации (`export_animation_mode`) принимает разные
> значения в разных версиях Blender — набор вариантов для NLA-дорожек, активного
> экшена и всей сцены менялся. Если сомневаешься, оставь значение по умолчанию
> и проверь результат: сколько клипов появилось в `AnimationPlayer` после
> импорта. Список допустимых значений — через
> `bpy.ops.export_scene.gltf.get_rna_type().properties`.

### Шаг 3. Сжатие: Draco и текстуры

```python
# Геометрия со сжатием Draco: файл меньше в разы, импорт чуть медленнее
bpy.ops.export_scene.gltf(
    filepath="//exports/godot/prop_draco.glb",
    export_format='GLB',
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,   # выше = меньше файл и дольше упаковка
)
```

Godot читает сжатую геометрию, но профиль совместимости зависит от версии редактора и наличия модуля Draco. Если проект должен открываться в чужих сборках, разумнее держать несжатый экспорт, а сжатие включать точечно для дальних ассетов.

Текстуры — отдельная история. PNG и JPEG распаковываются в VRAM как есть, и 4k-текстура весит там больше, чем на диске. Переключение проекта на импорт текстур KTX2 (внутри — Basis) даёт заметную экономию памяти, но качество при агрессивном сжатии страдает.

| Источник в Blender | Что выбрать в Godot | Комментарий |
|---|---|---|
| PNG / JPEG, цвет | Lossless или Lossy, зависит от канала | цветовые карты сжимать нельзя |
| Карта нормалей | Нормали сжаты отдельно, свой режим | сжатие карт нормалей даёт артефакты |
| Roughness / Metallic / AO | Каналы упаковываются в один файл | экономит сэмплеров и памяти |

> [!NOTE]
> Точные названия опций импорта текстур в Godot 4 менялись между релизами, а часть
> из них доступна только при включённом модуле KTX2. Список актуальных ключей
> импорта смотри в панели Import напротив файла и в документации Godot
> (`docs.godotengine.org`, раздел про импорт 3D-ассетов). Не переноси настройки
> из старого проекта вслепую.

### Шаг 4. Материалы

| Blender Principled | Godot `StandardMaterial3D` | Комментарий |
|---|---|---|
| Base Color | Albedo | совпадает напрямую |
| Metallic | Metallic | совпадает напрямую |
| Roughness | Roughness | совпадает напрямую |
| Normal | Normal Map (OpenGL) | переворот не нужен |
| Emission + Emission Strength | Emission / Emission Energy | в glTF интенсивность едет отдельным множителем |
| Alpha | Transparency, порог и режим | в glTF альфа есть, но режим смешивания — решение Godot |
| Transmission | не переносится | стекло придётся настраивать вручную |

Главное расхождение: **Blender и glTF не описывают прозрачность как «режим»**. Материал с `Alpha < 1` приедет в Godot непрозрачным, пока в настройках материала вручную не выставлен режим прозрачности и отключена отсечка по глубине. Для стекла и витражей это отдельная ручная работа на каждый материал.

### Шаг 5. Импорт в Godot и проверка

После копирования `.glb` в папку проекта Godot сам создаёт импортированный ресурс. Дальше — панель **Import** напротив файла: там задаются дополнительные параметры.

```bash
# Принудительный переимпорт без открытия редактора (для CI-скриптов):
godot --headless --path ./project --import
# Точный набор флагов и порядок аргументов сверяй по `godot --help`
# в своей версии: они отличаются между 3.x и 4.x.
```

Проверять после импорта стоит четыре вещи, и все четыре ловятся на первом кадре:

1. Масштаб — знакомый объект рядом с импортированным совпал по размеру.
2. Нормали — рельеф выпуклый, а не вдавленный; тени не «поплыли».
3. Материалы — количество материалов совпадает с числом в Blender, текстуры не серые.
4. Анимация — клипы появились в `AnimationPlayer` и проигрываются без рывков.

### Шаг 6. Коллизии через суффиксы имён

Godot умеет брать коллайдеры из тех же файлов. Объект, названный `Barrel-convex_col`, станет выпуклым коллайдером для `Barrel`.

```python
import bpy

# Обвязать главный объект коллайдером, который Godot подхватит сам
col = bpy.data.objects.get("Col_Barrel")
if col:
    col.name = "Barrel-convex_col"       # выпуклая оболочка, дёшево
    col.display_type = 'WIRE'
    col.hide_render = True

# Трюк с LOD: имена с суффиксом -lodN читаются как уровни детализации
for i, ratio in enumerate((1.0, 0.45, 0.15)):
    name = f"Barrel-lod{i}" if i else "Barrel"
    ob = bpy.data.objects.get(name)
    if ob:
        print(f"LOD{i}: {len(ob.data.polygons)} polys")
```

> [!NOTE]
> Набор суффиксов имён, которые Godot распознаёт при импорте, шире, чем два
> примера выше, и дополнялся между версиями. Полный актуальный список — в
> документации Godot, раздел про соглашения имён при импорте сцен. Не
> рассчитывай, что незнакомый суффикс просто проигнорируют: может вылететь
> ошибка импорта.

### Шаг 7. LOD и окклюзия в движке

Импортированная модель — это `MeshInstance3D`. LOD в Godot не декоративный: дальний объект действительно перестаёт отправляться на отрисовку.

```gdscript
# scripts/lod_setup.gd — повесь на корневой узел импортированной сцены
extends Node3D

## Дальность, с которой ближний уровень перестаёт быть виден
@export var lod_begin: float = 60.0
## Дальность, с которой исчезает самый дальний уровень
@export var lod_end: float = 160.0

func _ready() -> void:
	# Уровни приходят в порядке имён: Barrel-lod0 самый близкий
	var levels: Array[MeshInstance3D] = []
	for child in get_children():
		if child is MeshInstance3D:
			levels.append(child)

	levels.sort_custom(func(a: MeshInstance3D, b: MeshInstance3D) -> bool:
		return a.name.length() < b.name.length())

	for i in range(levels.size()):
		var mesh := levels[i]
		mesh.visibility_range_begin = 0.0 if i == 0 else lod_begin * float(i)
		mesh.visibility_range_end = lod_end
		mesh.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
		print(mesh.name, ": ", mesh.mesh.get_faces().size() / 3, " tris")
```

> [!NOTE]
> Имена полей `visibility_range_*` и значения перечисления режима затухания
> (`VISIBILITY_RANGE_FADE_*`) берутся из класса `GeometryInstance3D` и дополнялись
> между версиями Godot. Если редактор ругается на неизвестное поле — открой
> документацию класса в своей сборке (`GeometryInstance3D` в поиске редактора
> покажет реальный список свойств) и поправь имена.

Отдельная тема — **окклюзия**. Дальний LOD не помогает, если объект всё равно проходит через frustum и отсечение по расстоянию. Реальную экономию дают `OccluderInstance3D` вокруг крупных непрозрачных форм: движок перестаёт отправлять на рендер всё, что за ними.

### Шаг 8. Материал и шейдер — только в Godot

```gdscript
# scripts/one_material.gd — один материал на всё дерево вместо материалов на мешах
extends Node3D

## Материал, который подставляется всем потомкам
@export var shared_material: Material

func _ready() -> void:
	for child in get_children():
		if child is GeometryInstance3D:
			# material_override сильнее материалов, заданных на самом меше,
			# и рисуется одним вызовом на всё дерево
			child.material_override = shared_material
```

### Шаг 9. Проверка `.glb` без движка

GLB — обычный файл, его можно открыть в Blender обратно и проверить, не запуская Godot. Это дешёвый способ поймать сломанный экспорт до того, как файл уедет в репозиторий.

```python
# scripts/check_glb.py — blender -b --python scripts/check_glb.py -- ./exports/godot/prop.glb
import bpy, sys, os

argv = sys.argv[sys.argv.index("--") + 1:]
problems = []

for path in argv:
    if not os.path.exists(path):
        problems.append(f"missing file: {path}")
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    tris = sum(len(o.data.loop_triangles) for o in meshes)
    mats = sum(len(o.data.materials) for o in meshes)
    print(f"{path}: {len(meshes)} meshes, {tris} tris, {mats} material slots")
    if tris == 0:
        problems.append(f"empty geometry in {path}")
    if mats == 0:
        problems.append(f"no materials in {path}")

if problems:
    for p in problems:
        print("ERROR:", p)
    sys.exit(1)
print("check_glb: OK")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|
| `export_format` | `GLB` для одного файла, `GLTF_SEPARATE` для инспекции | `GLTF_SEPARATE` удобен при отладке: видно, что лежит внутри |
| `export_yup` | `True` | Godot и glTF оба Y-up, отключать не нужно |
| `export_tangents` | `True` | без тангентов не будет корректных нормалей в шейдере |
| `export_apply` | `True` | иначе модификаторы в `.glb` не попадут |
| `export_extras` | `True` | переносятся пользовательские свойства в метаданные |
| Draco | выключен по умолчанию | включать для дальних ассетов после проверки импорта |
| текстуры | KTX2 / Basis | экономия VRAM; сжатые карты нормалей проверять отдельно |
| суффикс `-convex_col` | для выпуклых коллайдеров | сложную геометрию коллайдера лучше делать в Godot вручную |
| `visibility_range_begin/end` | по дистанции LOD | подбирается замером в реальной сцене, а не на глаз |
| `material_override` | один материал на дерево | меньше вызовов отрисовки, но теряются материалы отдельных мешей |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Модель в 100 раз больше | не применён масштаб | `transform_apply(scale=True)` перед экспортом |
| Материал серый | текстура не на месте в момент импорта | импортировать файл заново после копирования текстур |
| Стекло выглядит как непрозрачный пластик | glTF не несёт режим прозрачности | выставить Transparency в `StandardMaterial3D` вручную |
| Анимация не появилась | не совпал режим экспорта анимации | сверить число клипов с Blender, попробовать другой режим |
| Нормали вдавленные | вручную переворачивали карту нормалей | вернуть OpenGL-конвенцию, убрать ручной флип |
| Коллайдера нет в сцене | суффикс имени не распознан | сверить суффикс со списком соглашений имён Godot |
| VRAM растёт быстрее, чем ожидалось | текстуры импортированы как PNG/JPEG | переключить импорт на KTX2 и переимпортировать проект |
| LOD не переключается | границы заданы только на корневом узле | задать `visibility_range_*` на каждом `MeshInstance3D` |
| Тормозит вдали от игрока | дальние объекты всё ещё в кадре | добавить окклюзию, а не только LOD |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P39: EXPORT PRESETS (GLB/FBX/USD)](../prompts/39_export_presets.md), [P46: UDIM WORKFLOW](../prompts/46_udim_workflow.md)
- **Теги:** #blender, #godot, #pipeline, #setup