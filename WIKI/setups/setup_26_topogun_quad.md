---
id: setup_26_topogun_quad
lang: ru
category: setups
type: setup
status: full
tags: [setup, topology]
---
# SETUP 26: TOPOGUN / QUAD DRAW RETOPO

**ID:** SETUP-26 | **Type:** Retopo | **Difficulty:** ⭐⭐ | **Time:** 35 min
**RU/EN Bilingual**

> Когда применять: тебе нужна лоу-поли сетка для анимации, и ручная лепка квадов в Edit Mode стала медленной.

## 🎯 ЦЕЛЬ
Собрать рабочий ретопо-пайплайн: подготовить исходный хиг-полис меш, построить по нему квадратную сетку и прижать её к форме так, чтобы при деформации не появлялись заломы. Два рабочих пути: встроенный в Blender инструмент Quad Draw — для лица и точечных правок, и отдельное приложение TopoGun — когда меш большой и квады идут сотнями в минуту. В конце — перенос весов с исходника на ретопо и проверка результата на экстремальной позе.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x; Quad Draw появился в 2.90 | Edit Mode, Shrinkwrap, Data Transfer |
| TopoGun | актуальный релиз | отдельный квад-дри для больших мешей |
| FBX-плагин | встроенный в Blender | обмен геометрией с TopoGun |
| Исходный меш | от ~30k до ~200k полигонов | «форма», к которой прижимается сетка |

> [!NOTE]
> Проверь доступность Quad Draw в своей сборке: `Edit Mode → Tool Shelf` или пицца-меню по `Shift+Q` (в списке есть Quad Draw). Точная клавиша менялась между релизами — сверься со своей раскладкой в `Preferences → Keymap`.

## 🛠️ НАСТРОЙКА

### 1. Подготовка «формы»
Ретопо строится поверх отдельной копии исходника. Копию сразу прячем и отключаем от рендера — иначе она будет мешать в превью и в весах.

```python
import bpy

src = bpy.context.view_layer.objects.active
src.name = "SRC_high"

# Копия геометрии — то, по чему рисуем ретопо
me = src.data.copy()
ret = bpy.data.objects.new("RET_low", me)
bpy.context.collection.objects.link(ret)
ret.parent = src          # едет вместе с исходником, сохраняя позицию
ret.matrix_parent_inverse = src.matrix_world.inverted()

src.hide_render = True
src.hide_viewport = True
```

### 2. Чистка исходника перед снятием формы
Скругления, на которых ретопо всё равно не ляжет ровно, мешают. Проще всего снять их одним Data Transfer с включённым Smooth.

```python
smooth = src.modifiers.new("Smooth_low", 'SMOOTH')
smooth.factor = 0.5
smooth.iterations = 3

# Нормали пересчитать, иначе Shrinkwrap будет цепляться к старым нормалям
for poly in src.data.polygons:
    poly.use_smooth = True
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = src
bpy.ops.object.modifier_apply(modifier="Smooth_low")
```

### 3. Рисуем квады
**Путь A — Quad Draw в Blender.** Перейди в `Edit Mode` на объекте `RET_low`, возьми Quad Draw и рисуй четырёхугольники кликом с зажатым `Shift`. Раскладку отключи (`Ribbon / Pie` выключены), иначе каждый клик открывает меню. Клавиша удаления/отмены — `Ctrl+Z` внутри Edit Mode работает штатно.

**Путь B — TopoGun.** Выгружаем форму в FBX с нулевой анимацией, рисуем в TopoGun, выгружаем обратно.

```python
# Экспорт формы наружу: только меш, без костей
bpy.ops.object.select_all(action='DESELECT')
ret.select_set(True)
bpy.context.view_layer.objects.active = ret
ret.hide_viewport = False

bpy.ops.export_scene.fbx(
    filepath=r"C:\work\retopo\src.fbx",
    use_selection=True,
    object_types={'MESH'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',      # OFF / EDGE / FACE — экспорт сглаживания
    path_mode='AUTO',
)
```

> [!NOTE]
> Ссылку на репозиторий TopoGun (`github.com/topogun/topogun`) проверь перед установкой — проекты с таким именем нередко переезжают и меняют владельца. Надёжный признак актуальности: в репозитории есть готовые сборки под твою ОС. Если репозиторий недоступен, Quad Draw в Blender закрывает те же задачи, просто медленнее.

### 4. Прижимаем сетку к форме
Shrinkwrap с офсетом порядка 0.001 единицы — рабочий диапазон: меньше — сетка тонет в исходнике, больше — появляется видимый зазор.

```python
sw = ret.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
sw.target = src
sw.wrap_method = 'NEAREST_SURFACEPOINT'
sw.wrap_mode = 'ON_SURFACE'
sw.offset = 0.001

# Смещение в нормальном направлении даёт одинаковый зазор на всех сторонах
sw.use_project_y = False
```

### 5. Размечаем рёбра деформации
Кромки вдоль позвоночника, в локтях и подмышках ломаются первыми. Помечай их как sharp или crease — тогда при изгибе сетка не «тянет» за собой гладкие участки.

```python
me = ret.data

# 1.0 — максимум crease по всем рёбрам; точечно лучше выставлять в UI
me.edges.foreach_set("crease", [0.0] * len(me.edges))

# Порог нормалей: угол выше него считается жёсткой кромкой
for p in me.polygons:
    p.use_smooth = True
bpy.context.view_layer.objects.active = ret
bpy.ops.object.shade_smooth_by_angle(angle=0.523599)  # 30°
```

> [!NOTE]
> `shade_smooth_by_angle` существует в Blender 4.1+. В 4.0 и раньше это была галочка `Mesh → Shade Auto Smooth` (свойства `mesh.use_auto_smooth` и `mesh.auto_smooth_angle`). Проверь, что есть в твоей версии.

### 6. Переносим веса с исходника
Ретопо — отдельная геометрия, весов у неё нет. Data Transfer копирует vertex groups с исходника.

```python
dt = ret.modifiers.new("DataTransfer", 'DATA_TRANSFER')
dt.object = src
dt.mix_mode = 'REPLACE'
dt.mix_factor = 1.0
dt.use_max_face_angle = False

# Дальше через UI: Modifier → Data Transfer → Vertex Data / Mesh Data,
# переключатель "All Layers", затем Apply
```

> [!NOTE]
> Имена свойств модификатора Data Transfer отличаются между версиями: включение переноса вершин называлось `use_mesh_data`, а в новых сборках — `use_vert_data`. Уточни точные поля в `DataTransferModifier` через поиск по `Help → Manual → API`, и не полагайся на приведённый выше список как на полный.

### 7. Проверяем на позе
Гоняй крайние позы, а не нейтральную: именно на них видно заломы, которые не видны в T-pose.

```python
sc = bpy.context.scene
sc.frame_set(1)

# Удобный способ: поставить кадр и посмотреть, не проткнула ли сетка форму
for f in (0, 25, 50, 75):
    sc.frame_set(f)
    print(f"frame {f}: retopo verts={len(ret.data.vertices)}")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Замерить результат — до/после должно быть видно в консоли
def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)

print("src tris:", tri_count(src))
print("ret tris:", tri_count(ret))
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `Shrinkwrap.offset` | `0.001` | больше — если сетка тонет в исходнике при сгибе |
| `Shrinkwrap.wrap_method` | `NEAREST_SURFACEPOINT` | `PROJECT` — когда есть направление проекции |
| `Shrinkwrap.wrap_mode` | `ON_SURFACE` | `ABOVE_SURFACE` — чтобы сетка не проваливалась внутрь |
| `DataTransfer.mix_mode` | `REPLACE` | `ADD` — когда переносишь поверх уже готовых весов |
| `DataTransfer.mix_factor` | `1.0` | `0.5` — для частичного переноса при ручной правке |
| crease рёбер | `0.0 – 1.0` | `1.0` на позвоночнике и в сгибах |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Retopo проваливается внутрь формы | `wrap_mode` не задан или `offset` отрицательный | Поставь `ON_SURFACE` и положительный `offset` |
| Сетка «плывёт» при движении | ретопо не в иерархии исходника | `ret.parent = src` + `matrix_parent_inverse` |
| Данные Data Transfer не переносятся | несовпадение расстояния между сетками | Сначала Shrinkwrap, потом Transfer; либо поднять `max_angle` |
| Квады не создаются, вместо них треугольники | активен не Quad Draw, а обычное выделение | Взять инструмент Quad Draw в Tool Shelf, рисовать с `Shift` |
| Залом на локте после Apply | не выставлен crease на рёбрах сгиба | Выделить рёбра → `Edge → Crease`, значение 0.5–1.0 |
| Ретопо тормозит при рисовании | в сцене виден исходник в 200k полигонов | `src.hide_viewport = True` во время рисования |
| Текстура «поехала» после Apply | UV разъехались после Shrinkwrap | Перенеси UV через Data Transfer (UV Data) до применения |

## 🖥 MCP-ПРОМПТ

```text
RU: "Сделай копию SRC как RET_low, навесь Shrinkwrap 0.001 к SRC,
     перенеси веса Data Transfer, проверь на кадрах 1 и 50" /
EN: "Duplicate SRC as RET_low, Shrinkwrap 0.001 onto SRC,
     Data Transfer weights, check frames 1 and 50"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 22: RIZOMUV BRIDGE](setup_22_rizomuv_bridge.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #topology