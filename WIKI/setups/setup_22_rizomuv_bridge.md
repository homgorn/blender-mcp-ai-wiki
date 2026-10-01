---
id: setup_22_rizomuv_bridge
lang: ru
category: setups
type: setup
status: full
tags: [setup, topology]
---
# SETUP 22: RIZOMUV BRIDGE

**ID:** SETUP-22 | **Type:** UV Pro | **Difficulty:** ⭐⭐ | **Time:** 30-60 min
**RU/EN Bilingual**

> Когда применять: когда развёртка сделана, но разложена плохо — острова разного размера, текстура растянута, швы не там. RizomUV даёт честный контроль над площадью островов и предсказуемые швы, чего не дают встроенные инструменты Blender.

## 🎯 ЦЕЛЬ
Настроить обмен UV между Blender и RizomUV так, чтобы развёртка приходила обратно в тот же объект, в правильном масштабе и с заданными швами. Научиться делать три вещи: авто-швы по углу, пакинг с контролем минимальной длины текстуры и раскладку по сетке UDIM для больших текстур.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Blender | 4.2 LTS+ | источник геометрии и приём UV |
| RizomUV Bridge / RizomUV | 2020.3+ | работа с UV |
| Лицензия RizomUV | на момент написания коммерческая, есть пробный период | сам инструмент |
| Модель с развёрткой либо без | — | если развёртки нет, её надо построить до обмена |

> [!NOTE]
> У RizomUV сложная история с лицензиями и режимами (Bridge / Islands / UV Pack), и состав функций менялся между крупными релизами. Проверь, что в твоей версии есть именно те инструменты, что описаны ниже (Auto Seams, Scaling, Layout), прежде чем строить пайплайн на них. Ничего из перечисленного ниже не является бесплатным и гарантированным — это коммерческий продукт.

## 🛠️ НАСТРОЙКА

### 1. Передать объект в RizomUV

```text
RizomUV → Preferences → Miscellaneous
  • Subdivision level: выбери уровень (обычно 1 — RizomUV не нужен full-res)
  • Risky mode / LOD: для больших мешей

Blender → File → Export → FBX (.fbx) с выбором только нужного объекта
  В настройках экспорта:
    ✓ Apply Modifiers — обязательно, иначе RizomUV увидит «голый» меш
    Path Mode: Copy
    Limit to: Selected Objects

Альтернатива без файла: буфер обмена
  RizomUV умеет читать геометрию из clipboard (формат OBJ).
  В Blender: выделить объект → Ctrl+C в контексте, где копируется
  выделение как OBJ (обычно Edit → Copy умеет), затем в RizomUV вставить.
  Формат обмена через clipboard менялся — проверь свою версию.
```

> [!NOTE]
> Простое и надёжное правило: **FBX через файл работает всегда**, clipboard — удобство, которое может не сработать. Для CI и повторяемых прогонов пиши только файловый путь.

### 2. Авто-швы по углу

```text
В RizomUV:
  Toolbars → UV Seams / Seams
    Auto Seams (по углу):
      • Enable Auto Seams — включить
      • Angle: значение в градусах

Как выбрать угол:
  • 30°  — много мелких деталей, ювелирка, заклёпки
  • 66°  — универсальное значение для большинства объектов
  • 80°  — только жёсткие рёбра (куб, панель)
  • 90°  — фактически отключает: рёбра под прямым углом не режутся
```

Ручной контроль поверх авто-швов:

```python
# Упрощённая эталонная развёртка в Blender — то, что RizomUV делает,
# но похуже. Полезно как запасной вариант и как проверка: если результат
# Blender приемлем, возможно RizomUV не нужен.
import bpy, math

def unwrap_angle_based(obj_name="Body", angle_deg=66.0, margin=0.02):
    """
    angle_based режет по рёбрам, острые нежели angle_limit.
    Углы задаются в радианах.
    """
    ob = bpy.data.objects.get(obj_name)
    if not ob:
        print("нет объекта:", obj_name); return

    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    # Гладкие полигоны НЕ должны резаться — иначе развёртка распадается
    if ob.data.use_auto_smooth if hasattr(ob.data, "use_auto_smooth") else False:
        for p in ob.data.polygons:
            p.use_smooth = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', angle_limit=math.radians(angle_deg))
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    print("unwrap:", ob.name, "| UV-слоёв:", len(ob.data.uv_layers))
```

### 3. Пакинг: контроль минимальной длины текстуры

Главная метрика пакинга — **texel density** (пиксели на единицу поверхности). В RizomUV она выравнивается автоматически, и это то, ради чего инструмент и нужен.

```text
RizomUV → Toolbars → Layout / Scaling:
  • Normalize / Scale Island — выровнять размер островов
  • Scale — подвигать вручную отдельный остров
  • Target Texture Size (или Average Island Scale) — целевая плотность

Настройки пакинга, которые стоит зафиксировать:
  • Padding / Margin: 4–16 px (при 2K). 2 px — экономия памяти,
    но при бейкe видна «расфокусировка» на швах.
  • Rotate/Flip islands: включить, иначе упакует непредсказуемо
  • Метрика расстояния: Straightener Distance — лучше сохраняет форму
```

```python
# Измерение texel density в Blender — способ проверить, выровнял ли RizomUV
import bpy
from mathutils import Vector

def texel_density_report(obj_name="Body", texture_size=2048):
    ob = bpy.data.objects.get(obj_name)
    if not ob or not ob.data.uv_layers:
        print("нет UV"); return

    uv = ob.data.uv_layers.active.data
    u_extent = max(d.uv.x for d in uv) - min(d.uv.x for d in uv)

    # Средняя площадь островов в UV-пространстве
    tris = sum(1 for p in ob.data.polygons) * 2
    uv_area = sum(abs((d.uv[i].x - d.uv[j].x) * (d.uv[k].y - d.uv[j].y))
                  for poly in ob.data.polygons
                  for i, j, k in zip(poly.loop_indices,
                                     poly.loop_indices[1:] + poly.loop_indices[:1],
                                     poly.loop_indices[2:] + poly.loop_indices[:1]))
    if uv_area <= 0:
        print("нулевая UV-площадь — развёртка сломана"); return

    px_per_uv = texture_size / max(u_extent, 1e-6)
    print(f"объект: {ob.name}")
    print(f"UV-протяжённость: {u_extent:.3f}")
    print(f"треугольников: {tris:,}")
    print(f"пикселей на единицу UV: {px_per_uv:.0f}")
    print(f"средняя площадь острова: {uv_area/tris*1e4:.2f} (в 10⁻⁴ долях UV)")

texel_density_report()
```

### 4. UDIM: раскладка по сетке тайлов

```text
RizomUV:
  • Выделить все острова → Tools → Layout
  • В настройках раскладки выбрать UV Tile Grid (4×4, 8×8 …)
  • Острова разложатся по тайлам 1001, 1002, … с равномерной плотностью

В Blender:
  Image Editor → Image → Open → выбрать ВСЕ файлы 1001.png, 1002.png …
  Blender соберёт их в один датаблок с source='TILED'
  Нода Image Texture работает с ними как с одной текстурой
```

Проверка, что тайлы действительно собрались:

```python
import bpy
for img in bpy.data.images:
    if getattr(img, "source", None) == 'TILED':
        print(f"{img.name}: тайлов {len(img.tiles)}, "
              f"размер тайла {img.tiles[0].size[0]}×{img.tiles[0].size[1]}")
```

### 5. Вернуть UV в Blender

```text
Вариант A (основной): FBX обратно
  RizomUV → File → Export FBX → в Blender File → Import → FBX (.fbx)
  В настройках импорта:
    ✓ UVs — обязательно
    ✓ Normals
    Осторожно: импорт FBX создаёт НОВЫЙ объект. Старый удали,
    иначе в сцене будет дубль.

Вариант B (точнее): только UV-карта
  RizomUV умеет экспортировать UV-карты отдельно (формат .uv / .json —
  зависит от версии). В Blender:
    Image Editor → выбрать объект → Image → Open → выбрать этот файл
    Он наложится на существующий UV-слой.

Вариант C (для CI): встроенный формат Blender
  Blender умеет читать и писать свой формат раскладки:
    bpy.ops.uv.export_layout(filepath="layout.uv")   # экспорт раскладки
    bpy.ops.uv.import_layout(filepath="layout.uv")   # импорт обратно
  Это НЕ совместимо с RizomUV — только для внутреннего обмена/бэкапа.
```

> [!NOTE]
> Набор операторов `uv.import_layout` / `uv.export_layout` и их аргументы менялись между версиями Blender. Проверь `bpy.ops.uv.export_layout.get_rna_type().properties.keys()` перед использованием. Формат `.uv` — внутренний формат Blender, RizomUV его не читает.

### 6. Ручные швы и проверка результата

Авто-швы — это отправная точка, а не ответ. Два места почти всегда требуют рук:

```text
• Сгибы, которые не должны разворачиваться (жёсткие рёбра мебели,
  складки, заклёпки) — им назначают UV Seam поверх грани
• Скрытые зоны (внутренняя сторона дна, зона под юбкой) — им назначают
  Project from View, чтобы упаковать туда мелкий островок,
  а не тратить на них пол-атласа
```

```python
# Ручные швы в Blender: маркировка рёбер и повторная проверка плотности
import bpy, math

def mark_seams_by_angle(obj_name="Body", angle_deg=66.0):
    """Отмечает швами рёбра, острее порога. Основа для ручной правки."""
    ob = bpy.data.objects[obj_name]
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob

    # Уже существующие швы снимаем, чтобы не копить мусор
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    print("швы с островов проставлены — дальше рисуй руками в UV-редакторе")

def pack_report(obj_name="Body", texture_size=2048):
    """Проверка после пакинга: сколько места занято и какая плотность."""
    ob = bpy.data.objects[obj_name]
    uv = ob.data.uv_layers.active.data
    xs = [d.uv.x for d in uv]; ys = [d.uv.y for d in uv]
    w = max(xs) - min(xs); h = max(ys) - min(ys)
    print(f"UV-протяжённость: {w:.3f} × {h:.3f}")
    print(f"пикселей по ширине: {texture_size * w:.0f} из {texture_size}")
    if w < 0.9 or h < 0.9:
        print("внимание: атлас занят слабо — есть смысл поднять разрешение тайла")
```

Признаки плохой развёртки, которые видно сразу:

| Симптом | Причина | Что делать |
|---------|---------|-----------|
| Светлая полоса поперёк текстуры | Перекрывающиеся острова | Проверить острова на перекрытие, распаковать заново |
| Артефакты бейка вокруг каждого острова | Padding мал для фильтра | Поднять padding, перезапечь |
| Одна часть текстуры резче другой | Texel density не выровнен | RizomUV: Normalize Island Scale; либо распаковать острова по площади |
| Полоса «размытия» на сгибе | Остров пересекает острый угол | Добавить шов на ребре |
| Текстура «едет» при анимации | Развёртка деформируется вместе с мешем | Проверить, что UV не лежит на перемещаемых вершинах |

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Диагностика развёртки в Blender: перекрытия, острова, плотность
import bpy

def uv_health(obj_name="Body", texture_size=2048):
    ob = bpy.data.objects.get(obj_name)
    if not ob or not ob.data.uv_layers:
        print("нет UV-слоя"); return

    uv = ob.data.uv_layers.active.data
    uv_data = [d.uv.copy() for d in uv]

    # Острова по связанности рёбер
    mesh = ob.data
    edge_faces = {}
    for poly in mesh.polygons:
        ls = list(poly.loop_indices)
        for a, b in zip(ls, ls[1:] + ls[:1]):
            key = tuple(sorted((a, b)))
            edge_faces.setdefault(key, []).append(poly.index)

    seen, islands = set(), 0
    for start in range(len(mesh.loops)):
        if start in seen:
            continue
        islands += 1
        seen.add(start)
        stack = [start]
        while stack:
            cur = stack.pop()
            for a, b in ((cur, (cur + 1) % len(mesh.loops)), ((cur - 1) % len(mesh.loops), cur)):
                for f in edge_faces.get(tuple(sorted((a, b))), []):
                    for li in mesh.polygons[f].loop_indices:
                        if li not in seen:
                            seen.add(li); stack.append(li)

    xs = [v.x for v in uv_data]; ys = [v.y for v in uv_data]
    print(f"объект      : {ob.name}")
    print(f"островов    : {islands}")
    print(f"диапазон UV : X {min(xs):.3f}..{max(xs):.3f}  Y {min(ys):.3f}..{max(ys):.3f}")
    print(f"покрытие    : {texture_size * (max(xs)-min(xs)):.0f} px по ширине")
    print("вне 0..1?  :", "ДА — развёртка вылезла за тайл" if max(xs) > 1.01 or min(xs) < -0.01 or max(ys) > 1.01 else "нет")

uv_health()
```

```python
# Раскладка по сетке тайлов средствами Blender — запасной путь, если
# RizomUV под рукой нет
import bpy

def tile_uv(obj_name="Body", grid=4):
    ob = bpy.data.objects[obj_name]
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='CONFORMAL')      # минимизирует искажения формы
    bpy.ops.uv.pack_islands(margin=0.005)
    bpy.ops.object.mode_set(mode='OBJECT')

    print("раскладка готова. Оператор раскладки по сетке тайлов —")
    print("UV → Image → New Image (или Image Editor → Image), выбери UV Tile Grid.")
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| Auto Seams angle | 66° | 30° для мелочи, 80° для кубических форм |
| FBX `Apply Modifiers` | включён | выключи, если рисуешь уже с применённым сабдивом |
| RizomUV Subdivision Level | 1 | 2 для мелких деталей, выше 3 — уже тяжело |
| Padding/Margin | 4–16 px @ 2K | 2 px при 8K экономит память, но ореол на швах |
| Rotate islands | включён | без него пакинг неоптимален по форме |
| UDIM grid | 4×4 для одной 2K-«страницы» | 8×8 при текстуре 16K |
| `angle_limit` для `ANGLE_BASED` | 66° = 1.15 рад | значение по умолчанию в Blender — 66°, совпадает с привычкой |
| `pack_islands(margin=)` | 0.005–0.02 | для текстуры с бейком ставь больше, чем для цветной |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| RizomUV открыл объект без детализации | FBX без `Apply Modifiers` | Переэкспортируй с галочкой Apply Modifiers |
| В сцене два одинаковых объекта | Импорт FBX создал новый объект | Удали старый, переименуй импортированный |
| Импорт FBX потерял UV | В настройках импорта снята галочка UVs | Импортируй заново с UVs |
| Острова в Blender «поплыли» после обратного импорта | Разный масштаб UV между программами | Проверь диапазон UV: должен лежать в 0..1 (или в сетке тайлов) |
| Текстура «мылится» в одном месте | Texel density не выровнен | RizomUV → Normalize Island Scale; либо в Blender распаковать острова по площади |
| Бейк даёт чёрные швы | Padding меньше ширины фильтра бейка | Увеличь padding до 8–16 px и перезапеки |
| UDIM-текстура не занимает весь меш | В Blender выбран один тайл вместо всех | Открой все файлы 1001… разом через Image Editor → Open |
| Развёртка в одном месте вырождена (нулевая площадь) | Вырожденные UV из-за вырожденных фейсов | Удали дублирующиеся вершины: Mesh → Merge by Distance |
| `TypeError` на `bpy.ops.uv.import_layout` | Аргументы оператора изменились | `get_rna_type().properties.keys()` |
| Швы в RizomUV не совпадают с тем, что в Blender | Разная интерпретация flip островов | После импорта проверь острова на перевёрнутость: выдели остров и посмотри на нормали |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 26: TOPOGUN / QUAD DRAW RETOPO](setup_26_topogun_quad.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #topology