---
id: wf_19_voxel_art_pipeline
lang: ru
category: workflows
type: workflow
status: full
tags: [pipeline, stylized, workflow]
---
# WF 19: VOXEL ART PIPELINE

**ID:** WF-19 | **Type:** Game | **Difficulty:** ⭐
**RU/EN Bilingual**

> Когда применять: когда нужно превратить любую форму — модель, скан, AI-генерацию — в узнаваемую блочную графику с ограниченной палитрой: для игровых ассетов, иконок, диорам.

## 🎯 ЦЕЛЬ

Любой объект пересобирается по регулярной сетке в объём из кубических ячеек, цвет ограничивается палитрой из 8–16 цветов, и на выходе получается ассет, который одинаково читается в рендере, в игровом движке и на иконке 64×64.

Ключевая мысль: вокселизация — это **пересборка формы**, а не декорация. Если поверх гладкой модели просто наложить кубики, получится «каша», потому что оригинальная поверхность никуда не делась. Сначала объём должен быть пересобран воксельным ремешем, и только потом раскрашен.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с модификатором Remesh | проверь: `Add Modifier → Remesh`, режимы `Blocks / Smooth / Sharp / Voxel` | пересборка геометрии по сетке |
| Исходная геометрия | своя, из библиотеки или из AI-генератора | форма, которую пересобираем |
| Image Editor | встроенный | уменьшение палитры до 8–16 цветов |
| Cycles или EEVEE | любой; для превью хватит EEVEE | финальный кадр |
| Оценка, а не замер | — | время рендера в таблице ниже — порядок величины |

> [!NOTE]
> Встроенного импортёра формата `.vox` (MagicaVoxel) в Blender нет. Обмен с MagicaVoxel идёт через OBJ + текстуру, либо через сторонний аддон. Если нужен именно `.vox` — сначала экспортируй OBJ с развёрткой, импортируй обратно и собери палитру через Remesh + ColorRamp.

## 🛠️ НАСТРОЙКА

### Этап 1. Подготовка: выбрать размер ячейки

Шаг ячейки (`voxel size`) — это главное решение всего пайплайна: он задаёт и объём файла, и читаемость силуэта.

```bash
RU: "Воксельная сетка 0.1 м. Возьми объект 'Sword' из blend, уменьши его до высоты 1.2 м,
     примени трансформации, сохрани копию как 'Sword_Orig'"
EN: "Voxel grid 0.1 m. Take object 'Sword', scale to 1.2 m tall,
     apply transforms, keep a copy as 'Sword_Orig'"
```

Проверка до ремеша: посчитай, сколько ячеек уйдёт. Объём габаритного параллелепипеда, делённый на размер ячейки в кубе, даёт верхнюю оценку.

```python
import bpy
obj = bpy.data.objects["Sword"]
cell = 0.10
dims = [d / cell for d in obj.dimensions]          # ячеек по каждой оси
print("габарит в ячейках:", [round(d) for d in dims],
      "верхняя оценка объёма:", int(dims[0] * dims[1] * dims[2]))
# Если оценка > 500 000 — ячейка слишком мелкая, уменьшай детализацию, а не размер ячейки.
```

### Этап 2. Генерация: воксельный ремеш

Два пути. Быстрый — оператор, который сразу переписывает меш. Контролируемый — модификатор, который можно крутить не генерируя результат.

```python
import bpy
obj = bpy.data.objects["Sword"]
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='OBJECT')   # ремеш не работает в Edit Mode; mode_set — оператор, не метод

# --- путь A: оператор, переписывает меш на месте ---
obj.data.remesh_voxel_size = 0.10          # размер ячейки в единицах сцены
obj.data.remesh_voxel_adaptivity = 0.0     # 0 = строгая сетка, больше = экономнее
obj.data.remesh_preserve_volume = True     # не давать объёму «схлопнуться» в местах сближения
bpy.ops.object.voxel_remesh()
```

Путь B — тот же результат, но через модификатор: у тебя остаётся исходная геометрия в стеке, можно менять параметры без перегенерации.

```python
mod = obj.modifiers.new("Voxel", 'REMESH')
mod.mode = 'BLOCKS'              # именно Blocks даёт кубические ступеньки
mod.octree_depth = 5             # больше = мельче ячейка; логарифмическая шкала
mod.use_remove_disconnected = True   # выкинуть мелкие островки
mod.use_smooth_shade = False     # для вокселей нужны плоские грани
bpy.ops.object.modifier_apply(modifier=mod.name)
```

### Этап 3. Look: палитра и раскраска

Квантование цвета делается штатно: ColorRamp с интерполяцией `Constant` — это и есть палитра. Важная деталь: стопы ставятся **на границах** между цветами (середина между соседними палитрами), иначе крайние значения интерполируются и получается каша.

```python
import bpy
mat = bpy.data.materials.new("Mat_VoxelAtlas")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs['Roughness'].default_value = 0.75

tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(r"//palette_ref.png")
tex.interpolation = 'Closest'          # без этогоimage сглаживает между вокселями

ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.interpolation = 'CONSTANT'

# 6 цветов палитры -> 7 стопов: 6 центров + границы
stops = [(0.00, (0.12, 0.10, 0.09, 1)),
         (0.18, (0.55, 0.20, 0.14, 1)),
         (0.36, (0.85, 0.62, 0.30, 1)),
         (0.55, (0.35, 0.55, 0.28, 1)),
         (0.74, (0.20, 0.35, 0.60, 1)),
         (0.90, (0.92, 0.90, 0.86, 1))]
cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = stops[0][0], stops[0][1]
cr.elements[1].position, cr.elements[1].color = stops[-1][0], stops[-1][1]
for pos, col in stops[1:-1]:
    cr.elements.new(pos).color = col

nt.links.new(tex.outputs['Color'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
obj.data.materials.clear(); obj.data.materials.append(mat)
```

Если воксели должны быть разноцветными (не одним материалом), крась по правилам — высота, нормаль или случай:

```python
import bpy, random
random.seed(7)                       # повторяемость: без сида каждый запуск даёт новый результат
me = obj.data
attr = me.color_attributes.new(name="Col", type='FLOAT_COLOR', domain='POINT')
zmin, zmax = min(v.co.z for v in me.vertices), max(v.co.z for v in me.vertices)
palette = [(0.12,0.10,0.09,1), (0.55,0.20,0.14,1), (0.85,0.62,0.30,1),
           (0.35,0.55,0.28,1), (0.92,0.90,0.86,1)]
for item in attr.data:
    t = (item.vector.z - zmin) / max(zmax - zmin, 1e-6)
    if t < 0.25:                      # низ — тень
        item.color = palette[0]
    elif random.random() < 0.15:      # редкий блик-«шум»
        item.color = palette[random.randint(1, 4)]
    else:
        item.color = palette[2 if t < 0.6 else 4]
```

Материал для чтения атрибута — `Attribute`, имя атрибута `Col`. Плоские грани обязательны, иначе кубики скругляются и стиль пропадает:

```python
for p in me.polygons:
    p.use_smooth = False             # воксель — всегда плоская грань

mat2 = bpy.data.materials.new("Mat_VoxelVertexColor")
mat2.use_nodes = True
nt = mat2.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
a = nt.nodes.new("ShaderNodeAttribute")
a.attribute_type = 'GEOMETRY'
a.attribute_name = "Col"
nt.links.new(a.outputs['Color'], bsdf.inputs['Base Color'])
obj.data.materials.clear(); obj.data.materials.append(mat2)
```

> [!NOTE]
> `mesh.color_attributes.new(...)` с типом `FLOAT_COLOR` появился в Blender 3.2+. В более старых версиях цвет лежит в вершинных цветах, и доступ другой — проверь в `Help → Manual` раздел про цветовые атрибуты для своей версии.

### Этап 4. Deliver: рендер и экспорт

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1024, 1024
sc.render.film_transparent = False
sc.render.filepath = r"//renders/voxel_sword.png"
bpy.ops.render.render(write_still=True)

bpy.ops.export_scene.gltf(filepath=r"//export/sword_voxel.glb",
                          export_format='GLB', use_selection=True, export_apply=True)
```

Считать геометрию надо через evaluated-объект: модификаторы в исходном меше не лежат.

```python
dg = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(dg)
me = ev.to_mesh()
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print(f"треугольников: {tris:,}, вершин: {len(me.vertices):,}")
ev.to_mesh_clear()      # без этого копия меша остаётся в памяти и утекает при цикле
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `remesh_voxel_size` / `octree_depth` | 0.1 м / 5 | мельче — детализация растёт, файл и память растут кубически |
| `mod.mode` | `'BLOCKS'` | `'SMOOTH'` — если нужен не блочный, а сглаженный воксельный ремеш |
| `remesh_voxel_adaptivity` | 0.0 | поднимать, если память кончается; растёт «шаг» в пустых местах |
| `color_ramp.interpolation` | `'CONSTANT'` | ровно это и даёт квантование в палитру |
| `tex.interpolation` | `'Closest'` | `Linear` размоет границы вокселей |
| `octree_depth` | +1 | ≈ в 2 раза мельче ячейка по линейной оси |
| `use_remove_disconnected` | `True` | выкидывает мусорные островки меньше порога |

| Шаг ячейки | Что читается | Порядок объёма |
|---|---|---|
| 0.02–0.05 м | детали механизма, оружие | десятки–сотни тысяч ячеек |
| 0.1 м | персонаж, проп, мебель | десятки тысяч ячеек |
| 0.25–0.5 м | окружение, здания, landscape | тысячи ячеек |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Поверх кубиков видны следы исходной модели | вокселизация сделана как декорация, ремеш не применён | применить Remesh до раскраски, проверить `octree_depth` |
| Всё слито в одну кашу | ячейка мельче, чем самая тонкая деталь | увеличить `voxel_size`, упростить исходную форму |
| Файл весит сотни мегабайт | `remesh_voxel_adaptivity = 0` на большой сцене | поднять адаптивность, ограничить габарит |
| Цвета «в грязь», ступенек не видно | стопы ColorRamp поставлены на сами значения палитры, а не на границы | ставить стопы в середине между соседними цветами |
| Грани вокселя скруглены | сглаженные нормали после ремеша | `polygon.use_smooth = False` для всех граней |

## ✅ РЕЗУЛЬТАТ

На выходе: один объект из воксельных ячеек + один материал (атлас-текстура с 6–16 цветами либо чтение цветового атрибута), плюс превью 1024×1024 и GLB.

Характеристики типового ассета — **оценка, а не измеренный результат**: проп высотой 1.2 м при ячейке 0.1 м даёт порядка 20–60 тыс. треугольников (шесть граней на ячейку), один материал, одна текстура 1024×1024. Рендер одного кадра 1024×1024 в Cycles на 64 сэмплах с шумоподавлением — секунды, десятки секунд; на 256 сэмплах без шумоподавления — минуты. Размер GLB с текстурой в PNG/JPEG — единицы мегабайт.

**Это оценка по порядку величины.** Точное время рендера зависит от железа, версии Cycles, числа материалов и объёма; измеряй на своей машине, а не по этой таблице.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md)
- **По темам:** [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md), [WF 16: NPR ANIME RENDER](wf_16_npr_anime_render.md), [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md)
- **Теги:** #pipeline, #stylized, #workflow