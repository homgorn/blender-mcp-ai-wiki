---
id: wf_24_photogrammetry_cleanup
lang: ru
category: workflows
type: workflow
status: full
tags: [animation, archviz, photogrammetry, pipeline, render, texturing, workflow]
---
# WF 24: PHOTOGRAMMETRY CLEANUP

**ID:** WF-24 | **Type:** Scan | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда приехал скан — с реального объекта или из открытой библиотеки — и его надо превратить в ассет, который можно анимировать, поставить в сцену и отрендерить.

## 🎯 ЦЕЛЬ

Три миллиона полигонов из фотограмметрии превращаются в 20–60 тысяч чистых квадов с одной запечённой текстурой 2k, тремя уровнями детализации и готовым экспортом.

Логика та же, что в любом ретопо: **разделить форму и материал**. Форма живёт в низкополигональной геометрии, детали поверхности (надписи, сколы, патина) живут в текстуре, запечённой с исходного скана. Это единственный способ сохранить детализацию фотограмметрии, не таская её миллион полигонов в сцену.

> [!NOTE]
> Фотограмметрию (фото → 3D) в Blender не делают: это работа сторонних программ — RealityCapture и Agisoft Metashape, у которых свои экспортные опции и свои форматы (`.obj`, `.ply`, `.fbx`). Blender умеет импортировать OBJ и PLY штатно; FBX зависит от того, включён ли аддон. Точные параметры экспорта смотри в документации той программы, которой снимаешь.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles | запекание текстур — только в Cycles | bake карт |
| RealityCapture или Agisoft Metashape | сторонняя программа | сама фотограмметрия |
| Quad Remesher или другой ремешер quads | аддон, платный/сторонний | равномерная квадратная топология |
| Масштабная линейка в кадре | — | реальный размер скана |
| Папка `//tex/` под карты | — | base color, normal, AO |

> [!NOTE]
> Встроенного в Blender «ремешера квадами с равной длиной ребра» нет. `Decimate` в режиме `COLLAPSE` даёт нерегулярную сетку — она годится для LOD, но не для анимации. Если нужен ровный quad-flow, нужен аддон (например Quad Remesher) либо отдельная программа ретопологии. Ровный квад — обязательное условие для скиннинга и для нормалей, сглаженных по углу.

## 🛠️ НАСТРОЙКА

### Этап 1. Импорт и приведение к реальному размеру

```bash
RU: "Импортируй //scan/statue.obj как 'Scan_Hi', переведи в метры по линейке 1.42 м,
     поставь нижнюю точку в Z=0, удали дублирующие вершины и выверни нормали"
EN: "Import //scan/statue.obj as 'Scan_Hi', scale to metres using a 1.42 m tape reference,
     put the base at Z=0, remove duplicate verts and recalculate normals"
```

```python
import bpy, bmesh
from mathutils import Vector

scan = bpy.data.objects["Scan_Hi"]
# приводим к метрам по референсу из съёмки
MEASURED_M = 1.42
current_dz = max(v.co.z for v in scan.data.vertices) - min(v.co.z for v in scan.data.vertices)
scan.scale = [MEASURED_M / current_dz] * 3
bpy.ops.object.select_all(action='DESELECT')
scan.select_set(True); bpy.context.view_layer.objects.active = scan
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

zs = [(scan.matrix_world @ v.co).z for v in scan.data.vertices]
scan.location.z -= min(zs)                      # основание в нуле

# чистка меша: дубли, вырожденные ребра, нормали
bm = bmesh.new(); bm.from_mesh(scan.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context='VERTS')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(scan.data); bm.free()
scan.data.update()
print("после чистки:", len(scan.data.polygons), "полигонов")
```

### Этап 2. Базовый LOD сразу

Скан стоит упростить **до** ретопологии: ретопо на 3 миллионах полигонов занимает часы, на 200 тысячах — минуты.

```python
import bpy
def make_lod(src, ratio, name):
    """Копия объекта с упрощением; детализация падает, силуэт сохраняется."""
    dup = src.copy()                       # копия сохраняет и данные меша
    dup.data = src.data.copy()             # иначе все LOD делят один меш
    dup.name = name
    bpy.context.collection.objects.link(dup)
    m = dup.modifiers.new("Decimate", 'DECIMATE')
    m.decimate_type = 'COLLAPSE'
    m.ratio = ratio
    bpy.ops.object.select_all(action='DESELECT')
    dup.select_set(True); bpy.context.view_layer.objects.active = dup
    bpy.ops.object.modifier_apply(modifier=m.name)
    return dup

lod0 = make_lod(scan, 0.10, "Scan_LOD0")    # ~100 тыс. полигонов
lod1 = make_lod(scan, 0.03, "Scan_LOD1")    # ~30 тыс.
lod2 = make_lod(scan, 0.01, "Scan_LOD2")    # ~10 тыс.
```

### Этап 3. Ретопология под анимацию

Рабочая последовательность без сторонних ремешеров: сгладить форму → упростить в нерегулярную сетку → **это база для переразвёртки**, а равномерность достигается либо аддоном, либо вручную в режиме Edge Slide / To Sphere.

```python
import bpy, math
base = bpy.data.objects["Scan_LOD1"]
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True); bpy.context.view_layer.objects.active = base

sub = base.modifiers.new("Smooth", 'SUBSURF')   # база для переноса деталей в текстуру
sub.levels = 1; sub.render_levels = 1
bpy.ops.object.modifier_apply(modifier=sub.name)

sm = base.modifiers.new("SmoothCorrective", 'CORRECTIVE_SMOOTH')  # если нужен слайдер коррекции формы
bpy.ops.object.modifier_apply(modifier=sm.name)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

for p in base.data.polygons:
    p.use_smooth = True
```

> [!NOTE]
> `Smart UV Project` разворачивает всё в пару UV-карт с равными островами — это не то, что нужно для запекания. Для bake нужен **один** развёрнутый вручную или раскроенный вручную лист (лапки, спинка, бок), иначе карта сдвинется на каждом острове. Делай лист сам, запекание проверяй визуально.

### Этап 4. Запекание текстур с исходного скана

Суть: низкополигональная форма получает карты, запечённые с высокополигонального скана. Дальше исходный скан можно удалить.

```python
import bpy
hi = bpy.data.objects["Scan_Hi"]      # источник данных
lo = bpy.data.objects["Scan_LOD1"]    # приёмник

# временно даём обоим одинаковый материал с нужными картами
mat = bpy.data.materials.new("Mat_ScanBaked")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(bpy.path.abspath("//tex/statue_basecolor.png"))
nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
for ob in (hi, lo):
    ob.data.materials.clear(); ob.data.materials.append(mat)

bpy.ops.object.select_all(action='DESELECT')
lo.select_set(True); hi.select_set(True)
bpy.context.view_layer.objects.active = lo
bpy.ops.object.mode_set(mode='OBJECT')

bake = bpy.context.scene.render.bake          # Bake Settings сцены
bake.use_pass_direct = True                   # AO-подобное затемнение в затенённых зонах
bake.use_pass_indirect = False                # экономит время, обычно не нужно
bake.margin = 16                             # отступ, чтобы не было чёрных кромок
bake.cycles_samples = 32
bpy.ops.object.bake(type='EMIT', use_clear=True)   # EMIT = diffuse albedo, шероховатость не трогается

# normal-карта — вторая запекание, с включённым displacement исходника
bpy.ops.object.bake(type='NORMAL')
```

> [!NOTE]
> `type` в `bpy.ops.object.bake` принимает значения вроде `EMIT`, `DIFFUSE`, `NORMAL`, `AO`, `SHADOW`, `ROUGHNESS`, `DISPLACEMENT` — точный набор зависит от версии. Второй аргумент важнее самого списка: если он у тебя называется иначе, открой `Render Properties → Bake` и посмотри путь в Python-консоли через `bpy.ops.object.bake.get_rna_type().properties`.

### Этап 5. Нормали и материал

Скан после ретопо — это «мягкая» форма: нормали нужно сглаживать по углу, а не по касательной, иначе по кромкам появляется лестница.

```python
import bpy, math
mat = bpy.data.materials.new("Mat_ScanFinal")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
base_tex = nt.nodes.new("ShaderNodeTexImage")
base_tex.image = bpy.data.images.load(bpy.path.abspath("//tex/statue_basecolor.png"))
norm_tex = nt.nodes.new("ShaderNodeTexImage")
norm_tex.image = bpy.data.images.load(bpy.path.abspath("//tex/statue_normal.png"))
norm_tex.colorspace_settings.name = 'Non-Color'      # для карты нормалей цвет не интерпретируется
nt.links.new(base_tex.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(norm_tex.outputs['Color'], bsdf.inputs['Normal'])
bsdf.inputs['Roughness'].default_value = 0.7

for ob in bpy.data.objects:
    if ob.name.startswith("Scan_LOD"):
        ob.data.materials.clear(); ob.data.materials.append(mat)
```

Сглаживание по углу: в Blender 4.1+ это отдельная операция, до 4.1 — флаги меша.

```python
import bpy, math
bpy.ops.object.select_all(action='DESELECT')
lo = bpy.data.objects["Scan_LOD1"]; lo.select_set(True)
bpy.context.view_layer.objects.active = lo
try:
    bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
except AttributeError:
    lo.data.use_auto_smooth = True
    lo.data.auto_smooth_angle = math.radians(40)
```

### Этап 6. Экспорт

```python
import bpy
bpy.ops.export_scene.gltf(filepath=r"//export/statue.glb", export_format='GLB',
                          export_apply=True, export_texcoords=True, export_normals=True)
bpy.ops.wm.save_as_mainfile(filepath=r"//export/statue.blend")
```

> [!NOTE]
> До 4.x экспорт OBJ делался через `bpy.ops.export_scene.obj`, в 4.x он переехал в `bpy.ops.wm.obj_export`. Если первый вариант у тебя не существует — это не ошибка сцены, а смена имени. Проверь: `hasattr(bpy.ops.wm, "obj_export")`.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `Decimate.ratio` для LOD0 | 0.10 | насколько сильно проседать до ретопо |
| `Decimate.decimate_type` | `'COLLAPSE'` | для упрощения формы; `'UNSUBDIV'` сглаживает, но не снижает число полигонов столько |
| `bake.margin` | 8–32 | больше = меньше «чёрных кромок» на швах |
| `bake.use_pass_direct` | `True` | добавляет мягкое затемнение; выключай, если результат слишком грязный |
| `bake.cycles_samples` | 16–64 | качество AO/нормалей |
| `colorspace_settings` нормали | `'Non-Color'` | обязательно, иначе карта «поплывёт» |
| `texture` | 2048×2048, одна на объект | 8k на скан почти никогда не нужно |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Модель в 100 раз меньше, чем ожидалось | скан в произвольных единицах | привести по референсу-линейке в кадре съёмки |
| Чёрные кромки на запечённой карте | `margin` мал или UV-швы за пределами карты | увеличить `margin`, сдвинуть UV внутрь листа |
| Нормали «поплыли», рельеф стал плоским | карта нормалей в sRGB вместо `Non-Color` | выставить `colorspace_settings.name = 'Non-Color'` |
| Запекается чёрное | приёмник и источник в разных слоях видимости или нет общей карты | оба объекта — в одной коллекции, материал с картой общий |
| Камера проваливается внутрь модели при анимации | топология нерегулярная, нет edge loops | ретопо квадами (аддон) либо хотя бы ручная правка рёбер |
| Файл весит гигабайты | 8k карты × 5 карт × 5 LOD | одна карта 2k, три LOD, остальное вырезано |
| Разные LOD «прыгают» при переключении | упрощение сдвигает силуэт | упрощать с сохранением объёма и крайних точек, не постепенно |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с тремя уровнями детализации, один материал с картами base color 2k и normal 2k, плюс GLB.

Характеристики — **оценка по порядку величины, а не измеренный результат**: исходный скан — миллионы полигонов; LOD0 порядка 100 тыс., LOD1 порядка 30 тыс., LOD2 порядка 10 тыс. Две текстуры 2048×2048 — порядка 30–60 МБ в памяти (RGB + RGBA, сжатие PNG/JPEG уменьшает файл вдвое-втрое, но не память). Запекание двух карт на объекте среднего размера — минуты; в реальности дольше, если источник с миллионами полигонов. Рендер итоговой сцены — обычный рендер, минуты.

**Это оценка.** Замеры зависят от объёма исходного скана и железа; измеряй на своём материале.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md), [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md)
- **Теги:** #animation, #archviz, #photogrammetry, #pipeline, #render, #texturing, #workflow