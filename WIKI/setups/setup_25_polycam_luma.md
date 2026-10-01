---
id: setup_25_polycam_luma
lang: ru
category: setups
type: setup
status: full
tags: [photogrammetry, setup]
---
# SETUP 25: POLYCAM / LUMA / KIRI SCAN

**ID:** SETUP-25 | **Type:** Mobile Scan | **Difficulty:** ⭐ | **Time:** 30-60 min
**RU/EN Bilingual**

> Когда применять: когда нужно быстро «оцифровать» объект на телефоне: референс пропов, ас sets-скан, замер помещения, прототип. Скорость съёмки измеряется минутами, качество — заметно ниже, чем у десктопной фотограмметрии, и почти всегда требует чистки в Blender.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Polycam или Luma AI или KIRI 3D Scan | актуальная из App Store / Google Play | съёмка и обработка на телефоне |
| Телефон с LiDAR (iPhone Pro / iPad Pro) | — | качественно меняет результат: даёт глубину, а не только цвет |
| Blender | 4.2 LTS+ | импорт, чистка, ретопология |
| Quad Remesher / QuadriFlow | см. примечание | квадры для рендера |
| Приложение для конвертации splat → mesh, если нужен меш | см. примечание | для Gaussian splatting |

> [!NOTE]
> Экосистема мобильного сканирования меняется быстрее всего во всём пайплайне: приложения добавляют и убирают режимы (NeRF, Gaussian splatting, LiDAR-фото), а экспорт меняет набор поддерживаемых форматов. Прежде чем строить на чём-то пайплайн, **сделай один тестовый экспорт и посмотри, что реально предлагает твоя версия приложения** — это 10 минут и снимает половину вопросов.

## 🎯 ЦЕЛЬ
Получить из мобильного скана пригодный объект: разобраться в форматах экспорта (GLB, OBJ+текстуры, PLY, splat), понять, что Blender умеет импортировать, починить масштаб, убрать мусор и довести геометрию до состояния, в котором её можно ретополозировать и запечь.

## 🛠️ НАСТРОЙКА

### 1. Съёмка: правила, которые экономят пересъёмку

```text
• Двигайся вокруг объекта, не останавливаясь на 5 секунд —
  приложениям нужен поток кадров, а не одиночные снимки
• Сначала пройди на средней дистанции, потом вернись ближе
  для деталей: приложение само склеит два прохода
• Не закрывай объект рукой в кадре — получишь дыру
• Для помещений: сначала круг по периметру, потом по вертикали
• Для мелких объектов: рента с расстояния 30–60 см и высоким ISO
• Свет: равномерный. Жёсткая тень даёт «запечатанную» ошибку,
  которую склеить нельзя
```

### 2. Форматы экспорта и что с ними делать

| Формат | Что внутри | Blender | Когда выбирать |
|---------|-----------|---------|----------------|
| **GLB / glTF** | меш + встроенная текстура, PBR-материал | импортируется штатно | лучший выбор: один файл, всё внутри |
| **OBJ + PNG** | меш + карты, развёртка | импортируется штатно | если GLB не получается |
| **PLY** | облако точек (иногда с цветом) | импортируется в новых версиях | когда нужна геометрия без текстуры |
| **Gaussian splat** (`.splat`, `.ply`, `.spz`) | набор «брызг» с параметрами | **напрямую не меш** | только для рендера в specialized-плеерах |

> [!NOTE]
> **Gaussian splatting не является мешем.** В Blender его нельзя импортировать как геометрию штатными средствами — это другой тип данных (анизотропные эллипсоиды с коэффициентами). Варианты: конвертация в меш сторонними инструментами (с потерей качества и увеличением размера) либо рендер сплата в отдельном плеерере и композитинг. Прежде чем строить пайплайн, убедись, что экспорт splat вообще доступен в твоей версии приложения и понимай, куда ты его понесёшь.

### 3. Импорт GLB в Blender

```python
# mobile_import.py — Blender: Text Editor → Run Script
import bpy, os

def import_gltf(filepath=r"C:\scans\chair.glb"):
    if not os.path.exists(filepath):
        print("нет файла:", filepath); return
    before = set(bpy.data.objects)
    with bpy.context.temp_override():
        bpy.ops.import_scene.gltf(filepath=filepath)
    new = set(bpy.data.objects) - before
    print("импортировано:", len(new))
    for ob in sorted(new, key=lambda o: o.name):
        d = ob.dimensions
        print(f"  {ob.name:24s} v={len(ob.data.vertices):>7,}  "
              f"dims={d.x:.3f}×{d.y:.3f}×{d.z:.3f}")
    return new

objs = import_gltf()
```

```python
# Диагностика после импорта: масштаб, UV, материалы, версиии
import bpy

def scan_report():
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        d = ob.dimensions
        big = max(d)
        verdict = ("подозрительно мало" if big < 0.2 else
                   "подозрительно много" if big > 50 else "правдоподобно")
        print(f"{ob.name:22s} {big:8.3f} м — {verdict}")
        print(f"   UV: {[u.name for u in ob.data.uv_layers] or 'НЕТ'}")
        print(f"   материалы: {[m.name for m in ob.data.materials if m] or 'НЕТ'}")
    print("ориентиры: стул ~0.6, стол ~0.8, дверь 2.0, человек 1.75, авто 4.5")

scan_report()
```

### 4. Починка масштаба

Мобильные приложения часто нормализуют объект «в куб 1×1×1» или считают в сантиметрах. Два способа:

```python
# scale_fix.py — Blender: Text Editor → Run Script
import bpy

def fit_to_height(obj_name, target_m=0.45):
    """
    Подгоняет объект под известный размер.
    Примеры: стул по высоте спинки 0.9 м, дверь 2.0 м,
    кружка по высоте 0.09 м, человек 1.75 м.
    """
    ob = bpy.data.objects.get(obj_name)
    if not ob:
        print("нет объекта:", obj_name); return

    current = ob.dimensions.z          # работаем по Z: приложения обычно
                                       # ориентируют объект вертикально
    if current < 1e-6:
        print("нулевая высота — объект вырожден"); return

    factor = target_m / current
    ob.scale = (factor, factor, factor)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print(f"коэффициент {factor:.4f} → высота {ob.dimensions.z:.3f} м")

def fit_by_measured_dimension(obj_name, axis, measured_m):
    """
    axis: 0 = X (ширина), 1 = Y (глубина), 2 = Z (высота).
    measured_m — реальная замеренная величина.
    """
    ob = bpy.data.objects[obj_name]
    current = ob.dimensions[axis]
    factor = measured_m / max(current, 1e-6)
    ob.scale = (factor, factor, factor)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print(f"ось {axis}: {current:.4f} → {measured_m} м (×{factor:.4f})")

# Пример: стул, высота спинки 0.9 м
fit_to_height("Chair", 0.9)
# Пример: измеренная ширина стола 1.4 м
fit_by_measured_dimension("Table", 0, 1.4)
```

### 5. Чистка мусора

Типовой мусор мобильного скана: «пузыри» на фоне, «tentacles» от движения, дыры.

```python
# cleanup.py — Blender: Text Editor → Run Script
import bpy, bmesh
from mathutils import Vector

def cleanup_scan(obj_name="scan",
                merge_threshold=0.002,   # 2 мм — сливает двойные вершины
                outlier_scale=0.02,      # порог отбрасывания дальних точек
                smooth_iterations=2):
    ob = bpy.data.objects.get(obj_name)
    if not ob:
        print("нет объекта"); return

    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob

    # 1) Обрезка «пузырей» — геометрия, отстоящая дальше порога от центра
    bm = bmesh.new()
    bm.from_mesh(ob.data)

    coords = [v.co.copy() for v in bm.verts]
    cx = sum(c.x for c in coords) / len(coords)
    cy = sum(c.y for c in coords) / len(coords)
    cz = sum(c.z for c in coords) / len(coords)
    center = Vector((cx, cy, cz))
    diag = max(ob.dimensions)
    limit = outlier_scale * diag

    loose = [v for v in bm.verts if (v.co - center).length > limit]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(ob.data)
    bm.free()
    print("удалено далёких вершин:", len(loose))

    # 2) Слияние и удаление висячих вершин
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=merge_threshold)
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # 3) Сглаживание — убирает шум и ступеньки сканирования
    sm = ob.modifiers.new("Clean", 'SMOOTH')
    sm.factor = 0.5
    sm.iterations = smooth_iterations
    print(f"осталось {len(ob.data.vertices):,} вершин")
```

### 6. Текстура мобильного скана: чего ожидать

```text
Что обычно приезжает:
  • Одна текстура 1–2K на весь объект (атлас), иногда без нормалей
  • Нормали часто нет вообще — только цвет
  • Качество ниже, чем у десктопной фотограмметрии: шум, «замыленность»
  • Иногда цвет в вершинных атрибутах вместо UV-текстуры

Что с этим делать:
  1. Для рендера: ретопология → своя развёртка → запечь карты со скана
  2. Для быстрого превью: оставить как есть, но поднять разрешение
     текстуры или перевзвесить через шумоподавление в композитной ноде
  3. Если текстуры нет вообще: только форма, материалы придётся
     делать процедурно или красить заново
```

```python
# Восстановить цвет из вершинных атрибутов в текстуру, если приехало именно так
def vertex_color_to_attribute(ob):
    """Если цвет лежит в vertex colors — переносим в color attribute,
    из которого его читает нода Attribute в материале."""
    if "Col" in ob.data.vertex_colors:
        ob.data.vertex_colors.remove(ob.data.vertex_colors["Col"])
    ca = ob.data.color_attributes.new(name="Col", type='BYTE_COLOR', domain='POINT')
    src = ob.data.vertex_colors.active
    for li, loop in enumerate(ob.data.loops):
        ca.data[loop.vertex_index].color = src.data[li].color
    print("перенесено в color attribute 'Col':", len(ca.data), "значений")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверка содержимого GLB без Blender — быстрый взгляд на состав
python -c "import struct,sys;d=open(r'C:\scans\chair.glb','rb').read(); \
print('magic:',d[:4]); print('version:',struct.unpack('<I',d[4:8])[0]); \
print('size:',len(d),'bytes')"

# Распаковка GLB, если нужно достать текстуру отдельно
python -c "
import struct, json
d = open(r'C:\scans\chair.glb','rb').read()
ln = struct.unpack('<I', d[12:16])[0]
print(json.loads(d[20:20+ln]))
"
```

```python
# Инвентаризация скана: что вообще приехало — решает, есть ли смысл продолжать
import bpy

def inventory():
    total_v = total_f = 0
    has_uv = has_tex = has_normal = False
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        total_v += len(ob.data.vertices); total_f += len(ob.data.polygons)
        has_uv |= bool(ob.data.uv_layers)
        for m in ob.data.materials:
            if not m or not m.use_nodes:
                continue
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image:
                    has_tex = True
                    if n.label.lower().find("norm") >= 0 or "nrm" in n.image.name.lower():
                        has_normal = True
    print(f"вершин {total_v:,} | полигонов {total_f:,}")
    print(f"UV: {'есть' if has_uv else 'НЕТ'} | текстура: {'есть' if has_tex else 'НЕТ'} "
          f"| карта нормалей: {'есть' if has_normal else 'НЕТ'}")
    print("нет UV или текстуры → ретопология обязательна, "
          "запекать будет нечего")

inventory()
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| Формат экспорта | GLB | GLB несёт PBR внутри и импортируется без настроек |
| `merge_threshold` | 0.001–0.005 м | 5 мм для крупных объектов, 1 мм для мелких |
| `outlier_scale` | 0.02 от диагонали | ниже 0.01 — срежет края; выше 0.05 — мусор останется |
| Smooth iterations | 2–4 | больше 4 — теряются мелкие детали |
| Известный размер | всегда задавать | без него сцена «повисает» на неизвестном масштабе |
| Текстура скана | 1–2K атлас | для рендера лучше перевзвесить на своей развёртке |
| ЛиDAR vs фото-режим | LiDAR лучше по форме | фото-режим лучше по цвету |

### Про NeRF и Gaussian splatting: когда это полезно

```text
Скан-тип            Что это                  Когда брать вместо меша
─────────────────   ──────────────────────   ─────────────────────────────
Фотограмметрия      сетка + текстура         финальная геометрия для рендера
LiDAR-фото          сетка + цвет             точная форма, средний цвет
NeRF (нейронное)    объёмное представление   просмотр, прототип; не для экспорта
Gaussian splatting  «брызги» с параметрами  фотореалистичный просмотр с любого
                                              ракурса; тяжёлые файлы
```

Практическое правило: если результат пойдёт дальше в рендер или в экспорт — бери сетку (фотограмметрия или LiDAR-фото). NeRF и splatting хороши как быстрый просмотр идеи, но из них не получится ни ретопология, ни запекание, ни физика.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| Модель размером 1×1×1 | Приложение нормализовало геометрию | `fit_to_height` или `fit_by_measured_dimension` |
| Модель размером 0.01 м | Приложение считает в сантиметрах | Та же функция, подставить реальные метры |
| Объект перевёрнут | Разные соглашения по Y-up/Z-up | Ручной поворот на 180° вокруг X; при экспорте через glTF Blender обычно справляется сам |
| Импорт GLB не дал текстуры | Текстура внутри отдельного буфера, версия glTF-экспортёра старая | Проверь содержимое файла (блок выше); попроси экспорт в OBJ + PNG |
| Сплошной цвет без деталей | Нормалей нет, освещение плоское | Перевзвесить карты скана на своей развёртке — запечь AO/curvature с ретопологии |
| «Пузыри» и «щупальца» | Мусор в облаке точек, движение при съёмке | `cleanup_scan` с outlier-отсечением; при сильном мусоре — переснять |
| Дыры на скан | Закрытые поверхности (низ, ручки) | Обойти объект снизу; заполнить дыры в Blender (`Mesh → Fill Holes`) |
| Splat не открывается в Blender | Splat — не меш | Конвертировать в меш сторонним инструментом или рендерить в отдельном плеерере |
| Экспорт недоступен в приложении | Формат заблокирован за подпиской / не поддерживается | Проверь тариф и список форматов; для GLB обычно нет ограничений |
| Blender зависает на импорте | 2–5 млн полигонов PLY | Импортируй фоновым режимом и прореживай сразу |
| Текстура «мылится» после рендера | Разрешение атласа ниже, чем нужно для кадра | Ретопология + своя развёртка + запекание 2K на остров |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 23: REALITYCAPTURE SCAN TO BLENDER](setup_23_realitycapture_scan.md), [SETUP 24: AGISOFT METASHAPE](setup_24_metashape_scan.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **Теги:** #photogrammetry, #setup