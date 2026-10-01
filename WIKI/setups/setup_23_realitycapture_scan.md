---
id: setup_23_realitycapture_scan
lang: ru
category: setups
type: setup
status: full
tags: [blender, photogrammetry, setup]
---
# SETUP 23: REALITYCAPTURE SCAN TO BLENDER

**ID:** SETUP-23 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 90-180 min
**RU/EN Bilingual**

> Когда применять: когда объект существует физически и его нужно «оцифровать»: ремонтный участок, артефакт, помещение, референс для пропов. Фотограмметрия даёт точную форму и цвет, но не даёт ни чистую топологию, ни пригодных для рендера карт — эти два шага делаются в Blender.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| RealityCapture | 1.3 / 1.4 (для 1.4 — редакция и лицензия Epic) | выравнивание фото, построение модели и текстуры |
| Камера с ручным фокусом | любая | съёмка с перекрытием кадров |
| Мишени (кодовые метки) | опционально, но сильно помогают | ускоряют выравнивание |
| Blender | 4.2 LTS+ | ретопология, запекание карт, подготовка к экспорту |
| Quad Remesher или QuadriFlow | см. примечание | превращение треугольников в квады |
| Достаточно VRAM | 8–12 ГБ для текстурирования 8K | текстура считается на GPU |

> [!NOTE]
> RealityCapture — коммерческий продукт, и условия использования менялись (после перехода к Epic). Проверь актуальную лицензию у Epic/Capturing Reality перед использованием в коммерческом проекте. Команды `rc-cli` в 1.3 и в 1.4 отличаются — ниже дана логика команд, а точный синтаксис стоит проверить через `rc-cli --help`.

## 🎯 ЦЕЛЬ
Получить из фотосъёмки геометрию и цвет, которые можно поставить в сцену Blender: отфильтровать мусор, построить ретопологию для рендера, перенести фототекстуру на новую сетку через запекание и подготовить экспорт в игру или в рендер-ферму.

## 🛠️ НАСТРОЙКА

### 1. Съёмка: требования, которые решают всё

```text
• Перекрытие между кадрами: 60–70% сбоку, 70–80% снизу вверх
• Текстура не должна быть однотонной (проблема белых стен):
  либо метки, либо временная текстура изолентой / краской-спреем
• Не снимать при прямом солнце: блики убивают текстурирование
• Не двигать объект между кадрами
• Снимать с расстояния, при котором объект занимает 60–80% кадра
• Для мелких деталей — отдельная серия с макросъёмкой
```

### 2. Обработка в RealityCapture: CLI-пайплайн

```text
RealityCapture умеет работать без GUI через rc-cli. Логика команд
(названия именно так и выглядят в ветке 1.x, но набор флагов
проверяй через rc-cli --help):

  import          — добавить фотографии в проект
  align           — сопоставить кадры между собой (alignCameras в GUI)
  reconstruct     — построить поверхность
  texture         — развернуть текстуру
  calculate normals
  export          — выгрузить модель (obj/fbx/ply)
  cleanup         — удалить лишние части (scale-aware)

Типичный порядок:
  rc-cli import --inputPath=photos/ --project=scan.rcp
  rc-cli align
  rc-cli reconstruct
  rc-cli texture
  rc-cli export --outputFile=scan.obj
```

В GUI тот же пайплайн выглядит так: `Align Images` → `Reconstruct` → `Texture` → `Export`.

**Что важно выставить в GUI до текстурирования:**

```text
Reconstruction → Model Quality: Medium/High
Reconstruction → Decimation: 0.5–0.8 (меньше = грубее)
Texturing → Texturing Mode:
    Basic          — быстро, только цвет
    Consistent     — средне, стабильнее на больших поверхностях
    Detail         — долго, лучший результат
Texturing → Texture Size: 4096 / 8192
Project → Metric Scale: задать по измерению — иначе модель будет
                       произвольного масштаба
```

> [!NOTE]
> Точные названия опций и их значения (в том числе `Max Decimation` и режимы текстурирования) менялись между версиями RealityCapture. Сверяйся с панелью своей версии и с `rc-cli --help`, а не с этим списком.

### 3. Импорт в Blender и оценка качества

```python
# scan_import.py — Blender: Text Editor → Run Script
import bpy, os

SCAN = r"C:\scans\scan.obj"

def import_scan(filepath=SCAN, target_size_m=None):
    """
    Сразу фиксируем масштаб: фотограмметрия не знает реального размера,
    а сцена — знает. Ориентир: человек ~1.75 м, дверь ~2.0 м,
    автомобиль ~4.5 м.
    """
    if not os.path.exists(filepath):
        print("нет файла:", filepath); return

    with bpy.context.temp_override():
        bpy.ops.wm.obj_import(
            filepath=filepath,
            forward_axis='NEGATIVE_Z', up_axis='Y',
            global_scale=1.0,
        )

    ob = bpy.context.view_layer.objects.active
    if not ob:
        print("импорт не дал активного объекта"); return

    print(f"{ob.name}: {len(ob.data.vertices):,} вершин, "
          f"{len(ob.data.polygons):,} полигонов")

    if target_size_m:
        import mathutils
        dims = ob.dimensions
        biggest = max(dims)
        factor = target_size_m / max(biggest, 1e-6)
        ob.scale = (factor, factor, factor)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        print(f"масштабировано до {target_size_m} м по наибольшей стороне, "
              f"коэффициент {factor:.4f}")
    return ob

ob = import_scan(target_size_m=1.75)
```

```python
# Диагностика скана: размеры, материалы, состояние UV
import bpy

def scan_report(ob):
    d = ob.dimensions
    print("размеры (м):", f"{d.x:.2f} × {d.y:.2f} × {d.z:.2f}")
    print("UV-слои    :", [uv.name for uv in ob.data.uv_layers] or "НЕТ")
    print("материалы  :", [m.name if m else None for m in ob.data.materials] or "НЕТ")
    print("шейдинг    :", "smooth" if any(p.use_smooth for p in ob.data.polygons) else "flat")

    # Отдельные острова-обломки обычно не примыкают к основной поверхности
    import bmesh
    bm = bmesh.new(); bm.from_mesh(ob.data)
    loose = sum(1 for v in bm.verts if not v.link_faces)
    print(f"висячих вершин: {loose:,}")
    bm.free()

scan_report(ob)
```

### 4. Очистка геометрии

```python
# cleanup.py — Blender: Text Editor → Run Script
import bpy, bmesh

def cleanup_scan(obj_name="scan", merge_threshold=0.001, decimate_ratio=0.25):
    ob = bpy.data.objects.get(obj_name)
    if not ob:
        print("нет объекта"); return

    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')

    # 1) Слить почти совпадающие вершины — убирает дырявую сетку
    bpy.ops.mesh.remove_doubles(threshold=merge_threshold)
    # 2) Удалить висячие вершины
    bpy.ops.mesh.delete(type='VERT')
    # 3) Удалить мелкие грани-обломки
    try:
        bpy.ops.mesh.dissolve_degenerate(dist=merge_threshold, edges=True)
    except RuntimeError:
        pass
    bpy.ops.object.mode_set(mode='OBJECT')

    before = len(ob.data.polygons)

    # 4) Прореживание: у фотограмметрии бывает 5–50 млн полигонов
    if decimate_ratio < 1.0:
        bpy.ops.object.modifier_add(type='DECIMATE')
        dec = ob.context.view_layer.objects.active.modifiers["Decimate"]
        dec.decimate_type = 'COLLAPSE'      # для треугольников
        dec.ratio = decimate_ratio
        dec.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=dec.name)

    print(f"полигонов: {before:,} → {len(ob.data.polygons):,}")

cleanup_scan()
```

> [!NOTE]
> `dissolve_degenerate` в некоторых версиях требует явного выделения рёбер и падает с `RuntimeError` при пустом выделении. Если так — пропусти этот шаг и сделай только слияние вершин: `remove_doubles` убирает 90% артефактов фотограмметрии.

### 5. Ретопология для рендера

```text
Фотограмметрическая сетка годится только как референс формы и как
источник запекания. Для рендера нужна quadrongon.

Вариант A — Quad Remesher (аддон, платный/подписочный):
  Blender → Quad Remesher → Target = (очищенный скан или его проекция)
  Target Preset = Quad, Target Surface = Scan
  Получаем квадратную сетку на месте скана.

Вариант B — QuadriFlow (аддон от Blender):
  Работает как «Remesh» в режиме Quad с направляющими кривыми.

Вариант C — встроенный Voxel Remesh (бесплатно, но теряет детали):
  Object → Remesh → Octree Depth 7–8, Scale 0.9
  Хорош как промежуточный этап перед бейком, плох как финал.
```

```python
# Промежуточный этап: воксельная ремеш-сетка, чтобы потом запечь на неё
def voxel_remesh(obj_name="scan", voxel_size=0.01, adaptivity=0.0):
    ob = bpy.data.objects[obj_name]
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob

    bpy.ops.object.voxel_remesh()          # использует настройки ниже
    remesh = ob.data.remesh_voxel_size
    ob.data.remesh_voxel_size = voxel_size
    ob.data.remesh_voxel_adaptivity = adaptivity
    print("воксели:", voxel_size, "| адаптивность:", adaptivity)

voxel_remesh()
```

### 6. Запекание фототекстуры на новую сетку

```text
Только в Cycles. Порядок:

1. Ретопология (low) и скан (high) в одной точке, рядом.
2. На low-меше — Image Texture с пустым изображением 2048×2048,
   НЕ Non-Color, привязанный к активной UV-карте.
3. Выделить low-меш (active) → выделить скан (в Shift выделения).
4. Baking → Type: Diffuse → нажать Bake.
5. Проверить результат: растянутые участки должны быть у краёв островов.
```

```python
# bake_setup.py — Blender: Text Editor → Run Script
import bpy

def setup_bake(low_name="scan_low", high_name="scan", bake_type='DIFFUSE', size=2048):
    scene = bpy.context.scene
    if scene.render.engine != 'CYCLES':
        print("внимание: активен", scene.render.engine, "— запекание только в Cycles")
        return

    low = bpy.data.objects[low_name]
    if not low:
        print("нет low-меша:", low_name); return

    # Пустое изображение — цель запекания
    img = bpy.data.images.get("BakeTarget")
    if img is None:
        img = bpy.data.images.new("BakeTarget", width=size, height=size)
    img.colorspace_settings.name = 'sRGB'   # для DIFFUSE; для NORMAL — 'Non-Color'

    mat = low.data.materials[0] if low.data.materials else low.data.materials.new("M_Bake")
    if not mat.use_nodes:
        mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.uv_map = low.data.uv_layers.active.name if low.data.uv_layers else ""
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(tex.outputs["Color"], out.inputs["Surface"])
    mat.use_fake_user = True

    bpy.ops.object.select_all(action='DESELECT')
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    high = bpy.data.objects[high_name]
    if high:
        high.select_set(True)
        # Активным остаётся low — в high выбранном запекается цвет из его текстур
        print("high:", high.name, "| материалы:", [m.name for m in high.data.materials if m])

    print("готово к запеканию:", bake_type, "→", img.name, size, "px")
    print("теперь Baking → Bake")

setup_bake()
```

### 7. Масштаб: как не ошибиться с размером

Фотограмметрия без Metric Scale даёт модель произвольного размера. Три способа это починить, от лучшего к худшему:

```text
1. Scale bar в проекте RC (точный путь):
   Панель Measurements → Add Scale Bar → выбрать 2 точки → вписать расстояние.
   Точки ставятся на грани, между которыми ты знаешь реальное расстояние.

2. Известный объект в кадре:
   В кадр кладётся предмет известного размера (плинтус, монета, кубик
   калибровочный). По нему ставится scale bar. Удобно, когда объект
   мелкий и точный масштаб не критичен.

3. Масштабирование в Blender по измеренной оси (шаг 3):
   Измерить в кадре высоту спинки стула и подогнать.
   Ошибка 10–20% — приемлемо для большинства задач.
```

```python
# Масштабирование по оси с измерением: тот же fit_by_measured_dimension,
# но в применении к скану
def fit_by_reference_object(scan_name="scan", reference_name="chair_ref",
                            reference_height_m=0.92):
    """
    Если в сцене есть эталонный объект известного размера —
    масштабируем скан под него.
    """
    scan = bpy.data.objects.get(scan_name)
    ref  = bpy.data.objects.get(reference_name)
    if not scan or not ref:
        print("нужны оба объекта"); return
    factor = reference_height_m / max(ref.dimensions.z, 1e-6)
    scan.scale = (factor, factor, factor)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print(f"эталон {ref.name}: {ref.dimensions.z:.3f} м → коэффициент {factor:.4f}")
    print(f"скан {scan.name}: {tuple(round(d, 3) for d in scan.dimensions)}")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Реалистичный ориентир по размеру сцены:
# фото 24 МП, средняя дистанция, объект 1 м:
#   ~600–1200 снимков  →  1–4 млн полигонов  →  текстура 4K
# фото 45 МП, тот же объект:
#   ~300–600 снимков   →  2–8 млн полигонов
# Больше снимков лучше по качеству, но не линейно: 400 снимков
# обычно дают 90% результата, 1200 — оставшиеся 10%.

# Порядок команд: сначала выравнивание, потом всё остальное.
# Если выравнивание плохое, остальные команды тратят время впустую.
```

```python
# Считаем «качество» скана до запекания — быстрый чек-лист
import bpy

def scan_checklist(obj_name="scan"):
    ob = bpy.data.objects.get(obj_name)
    checks = {
        "UV-слой есть": bool(ob.data.uv_layers),
        "Материал с текстурой": any(m and m.use_nodes for m in ob.data.materials),
        "Сглаженные нормали": any(p.use_smooth for p in ob.data.polygons),
        "Нет незамкнутых краёв": not any(len(p.vertices) < 3 for p in ob.data.polygons),
        "Разумный размер (0.1–100 м)": 0.1 < max(ob.dimensions) < 100,
    }
    for k, v in checks.items():
        print(f"[{'OK ' if v else 'НЕТ'}] {k}")
    return all(checks.values())

scan_checklist()
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| Перекрытие кадров | 60–80% | ниже 50% — дыры в геометрии |
| Reconstruction Decimation | 0.5–0.8 | 1.0 = максимум деталей и максимум шума |
| Texturing Mode | Consistent / Detail | Basic — только для проверки, не для продакшена |
| Texture Size | 4096 / 8192 | 8192 на 12 ГБ VRAM — предел для большинства карт |
| `remove_doubles` threshold | 0.001 м (1 мм) | для крупных объектов 0.005–0.01 |
| Decimate ratio | 0.2–0.4 | ретопология делается дальше, тут только чистка |
| Voxel size | 0.005–0.02 м | мельче → больше полигонов и меньше шума |
| Bake size | 2048 на остров | 4096, если сцена крупная и память позволяет |

### Про цвета и color management

Фототекстура — это sRGB-данные из JPEG. Если запечь её в линейное пространство или наоборот, получится «грязь». Отдельно: RealityCapture и Blender по-разному трактуют белый баланс, поэтому сцена почти всегда требует ручной правки через Hue/Saturation/Color Balance в композитной ноде.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| Align находит мало кадров | Мало перекрытия, нет текстуры, плохая освещённость | Добавь метки, сними с другим светом, уменьши шаг съёмки |
| Модель в «пузырях» | Слишком высокий decimation или шумная текстура | Decimation 0.6, текстурирование Consistent |
| Дыры в геометрии | Не хватило ракурсов с нижней стороны | Доснять низ и перевыровнять (Align Increment) |
| Текстура мыльная | Texturing Mode = Basic или слишком мало снимков | Consistent/Detail + пересчёт на полном наборе |
| Модель произвольного размера | Не задан Metric Scale | Задать в проекте RC и пересчитать, либо масштабировать в Blender |
| Blender зависает на импорте | 20 млн полигонов OBJ | Импортируй в фоне с прореживанием, либо экспортируй из RC сразу прорежённым |
| `remove_doubles` не помогает | Порог меньше реального расстояния между вершинами | Увеличь threshold до 0.005 и повтори |
| Запекание не стартует | Активен EEVEE или не выделен high-объект | Cycles + два объекта в выделении, active = low |
| Запечённая текстура в одном цвете | На high-объекте нет материала с текстурой | Проверь `high.data.materials` — там должен быть результат RC |
| После ретопологии форма «поплыла» | Ретопология построена не поверх скана | Surface Deform или Quad Remesher с целью = скан |
| Импорт OBJ вверх ногами | Не заданы оси | `forward_axis='NEGATIVE_Z', up_axis='Y'` |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #photogrammetry, #setup