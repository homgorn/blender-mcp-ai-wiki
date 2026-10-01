---
id: setup_21_marvelous_clo3d
lang: ru
category: setups
type: setup
status: full
tags: [clothing, setup]
---
# SETUP 21: MARVELOUS / CLO3D CLOTH

**ID:** SETUP-21 | **Type:** Cloth | **Difficulty:** ⭐⭐⭐ | **Time:** 60-120 min
**RU/EN Bilingual**

> Когда применять: когда одежду нельзя сделать в Blender. Marvelous Designer / CLO 3D дают симуляцию ткани с настоящей вышивкой, швами и заломами, которые руками в нодах не воспроизвести. Blender принимает результат и отвечает за материал, рендер и общее оформление.

## 🎯 ЦЕЛЬ
Прогнать цикл «аватар → гардероб → симуляция → экспорт → Blender», где симуляция ткани считается в Marvelous/CLO, а геометрия приезжает в Blender кэшем Alembic. Дополнительно настроить толщину (Solidify), коллизию с телом и запекание нормалей, чтобы одежда корректно выглядела в рендере.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Marvelous Designer | 12/13 (или новее) | моделирование и симуляция одежды |
| CLO 3D | 7/8 (альтернатива, не оба сразу) | то же самое плюс симуляция тела |
| Blender | 4.2 LTS+ | приём Alembic, материал, рендер |
| Alembic (.abc) | любой | основной формат обмена |
| Collada / FBX / OBJ | как запасной путь | если Alembic несёт слишком тяжёлую геометрию |
| Avatar в A-pose или T-pose | — | поза, из которой симуляция стартует |

> [!NOTE]
> Главная техническая оговорка: **прямой живой линк между Marvelous/CLO и Blender отсутствует** как штатная функция. CLO продвигает свою экосистему (CLO LiveSync идёт в сторону Unity/Unreal и в сторону Blender отдельными аддонами сторонних авторов). Статья ниже описывает схему, которая работает всегда: симуляция в Marvelous → Alembic/OBJ в Blender. Если нужен именно live-линк, ищи сторонний аддон и проверяй его дату поддержки версий.

## 🛠️ НАСТРОЙКА

### 1. Позы и единицы — проверь до всего остального

```text
Marvelous Designer / CLO:
  • Аватар должен быть в A-pose (руки вниз под ~45°) или T-pose
  • Обе программы считают в сантиметрах по умолчанию
  • Blender — в метрах по умолчанию

Это главный источник ошибки «плащ размером с комнату».
Решение: при импорте в Blender выставить масштаб 0.01 (см / м),
или заранее сменить единицы в настройках сцены.
```

### 2. Экспорт из Marvelous Designer

```text
File → Export → Object
  Формат: Alembic (.abc)  ← основной выбор
  Что включить:
    ✓ Geometry / Mesh
    ✓ UV
    ✓ Normals (Smooth shading)
    ✓ Material (если есть .mtl — но текстуры всё равно придётся пересобирать)

  Отдельно, если нужен кэш по кадрам:
    File → Export → Simulation Cache  → папка с .obj по кадрам

Варианты форматов и когда что:
  .abc  — сохраняет UV и деформацию по кадрам в одном файле. Основной выбор.
  .fbx  — сохраняет скелет, но UV и швы теряются частично.
  .obj  — простой, надёжный, но без анимации: только статичный кадр.
```

> [!NOTE]
> Опции экспорта и их названия в меню менялись между мажорными версиями Marvelous Designer и CLO 3D (в частности, набор галочек в Object Export). Сверяйся с диалогом экспорта в своей версии, а не с этим списком: выбор здесь буквально «потерять UV» или «не потерять».

### 3. Импорт Alembic в Blender

```python
# import_cloth.py — Blender: Text Editor → Run Script
import bpy, os

ABC = r"C:\clo\jacket.abc"          # путь к кэшу из Marvelous
SCALE = 0.01                        # сантиметры → метры

def import_garment(filepath=ABC, scale=SCALE, start=1, end=250):
    if not os.path.exists(filepath):
        print("нет файла:", filepath); return None

    before = set(bpy.data.objects)

    # ВАЖНО: оператор создаёт объект по контексту. Из Text Editor он
    # работает, но в background-режиме нужно переключить контекст.
    with bpy.context.temp_override():
        bpy.ops.wm.alembic_import(
            filepath=filepath,
            scale=scale,
            start=start,
            end=end,
            validate_meshes=True,
            is_shadow=False,
        )

    new = set(bpy.data.objects) - before
    print("импортировано объектов:", len(new))
    for ob in sorted(new, key=lambda o: o.name):
        print(f"  {ob.name:30s} v={len(ob.data.vertices):>9,}  "
              f"frames={getattr(ob.data, 'use_shape_key_edit_mode', 'n/a')}")
    return new

objs = import_garment()
```

> [!NOTE]
> Набор аргументов оператора `bpy.ops.wm.alembic_import` менялся между версиями Blender (часть флагов переименовывалась, часть добавлялась). Перед использованием вызови в консоли Blender `bpy.ops.wm.alembic_import.get_rna_type().properties.keys()` и собери вызов по фактическим именам — это надёжнее, чем доверять любому списку из интернета, включая этот.

### 4. Alembic без анимации: кэш OBJ по кадрам

Если Alembic весит сотни мегабайт, а нужна статика — импортируй кадр как OBJ:

```python
import bpy, os, glob

CACHE_DIR = r"C:\clo\cache"     # папка с jacket_0001.obj, jacket_0002.obj, ...

def import_single_frame(cache_dir=CACHE_DIR, frame=1):
    files = sorted(glob.glob(os.path.join(cache_dir, "*.obj")))
    if not files:
        print("кэш пуст:", cache_dir); return
    idx = min(max(frame - 1, 0), len(files) - 1)
    print("берём:", files[idx])

    # Импортируем один кадр — это просто OBJ
    with bpy.context.temp_override():
        bpy.ops.wm.obj_import(
            filepath=files[idx],
            forward_axis='NEGATIVE_Z', up_axis='Y',     # оси Marvelous → Blender
            global_scale=0.01,
        )
```

### 5. Толщина: Solidify

```python
# thickness.py — Blender: Text Editor → Run Script
import bpy

def add_thickness(obj_name, thickness_m=0.002, material_offset=0):
    """
    0.002 м = 2 мм. Реальные значения:
      джинса/кожа          1.5–3 мм
      хлопковая рубашка    0.3–0.6 мм
      тонкий шёлк           0.1–0.2 мм
      куртка-пуховик       8–20 мм (тут Solidify уже не подходит)
    """
    ob = bpy.data.objects.get(obj_name)
    if not ob:
        print("нет объекта:", obj_name); return

    sol = ob.modifiers.new("Thickness", 'SOLIDIFY')
    sol.thickness = thickness_m
    sol.offset = 0.0            # 0 = растёт наружу и внутрь; -1 = только внутрь
    sol.use_even_offset = True
    sol.use_quality_normals = True
    sol.material_offset = material_offset     # материал для внутренней стороны
    sol.material_offset_rim = material_offset # материал для кромки

    # Порядок: сначала толщина, потом сглаживание
    sm = ob.modifiers.new("Smooth", 'SMOOTH')
    sm.factor = 0.5
    sm.iterations = 2
    return sol

add_thickness("jacket", 0.002)
```

> [!NOTE]
> Solidify с невысокой плотностью сетки даёт «жестяной» вид на сгибах: вершины раздвигаются неравномерно. Если количество полигонов невелико, добавь Subdivision **перед** Solidify в порядке модификаторов, либо разбей ретопологию на сегменты по 2–3 см.

### 6. Коллизия и сшивка с телом

```python
# collision.py — Blender: Text Editor → Run Script
import bpy

def setup_collision(body_name="Body", garment_name="jacket"):
    body = bpy.data.objects.get(body_name)
    garment = bpy.data.objects.get(garment_name)
    if not body or not garment:
        print("нужны оба объекта"); return

    # На ТЕЛЕ — Collision: тело становится препятствием
    if not any(m.type == 'COLLISION' for m in body.modifiers):
        col = body.modifiers.new("Collision", 'COLLISION')
        # Плоский коллайдер (convex hull) работает стабильнее, чем mesh
        col.collision_shape = 'CONVEX_HULL'
        body.collision.thickness_outer = 0.01
        body.collision.damping = 0.3
        body.collision.friction_factor = 0.5

    # На ОДЕЖДЕ — Shrinkwrap, если она сидит слишком свободно
    sw = garment.modifiers.new("Wrap to body", 'SHRINKWRAP')
    sw.wrap_method = 'NEAREST_SURFACEPOINT'
    sw.target = body
    sw.offset = 0.01
    # Порядок: Shrinkwrap ДО Solidify, иначе толщина ляжет на уже сжатую форму

setup_collision()
```

Если в Blender нужна **собственная** симуляция одежды (а не кэш из Marvelous), цепочка такая:

```python
# Настоящая cloth-симуляция в Blender — только для простых случаев.
# Струна/лента/юбка получаются хорошо, куртка с капюшоном — нет.
def setup_cloth(body_name="Body", garment_name="jacket", quality=5):
    body  = bpy.data.objects[body_name]
    cloth = bpy.data.objects[garment_name]

    if not any(m.type == 'COLLISION' for m in body.modifiers):
        body.modifiers.new("Collision", 'COLLISION')

    m = cloth.modifiers.new("Cloth", 'CLOTH')
    s = m.settings
    s.quality = quality          # 5 достаточно; выше 10 — минуты на кадр
    s.mass = 0.3                 # kg/vertex; меньше → легче, «шёлковая» ткань
    s.tension_stiffness = 15
    s.compression_stiffness = 15
    s.shear_stiffness = 5
    s.bending_stiffness = 0.5
    s.air_damping = 1.0

    # Pin-группа: зафиксировать верх (плечи, талия) иначе одежда улетает
    if not cloth.modifiers.get("Pin"):
        pin = cloth.vertex_groups.new(name="Pin")
        top = max((v.co.z for v in cloth.data.vertices), default=0.0)
        ids = [v.index for v in cloth.data.vertices if v.co.z > top * 0.9]
        pin.add(ids, 1.0, 'REPLACE')
        m.settings.vertex_group_mass = "Pin"
    return m
```

### 7. Запекание нормалей на одежду

```text
Только в Cycles (EEVEE запекание не поддерживает):
  1. Выделить одежду, сделать активной
  2. Добавить в материал Image Texture с ACTIVE UV (имя слоя = имя UV-карты)
  3. Object Data → UV → выбрать развёртку одежды как активную
  4. Baking → Type: Normal → Save As: C:\clo\jacket_normal.exr

Важно: перед запеканием разверни одежду (UV → Smart UV Project),
иначе запечётся каша из перекрывающихся островов.
```

```python
# Проверка готовности к запеканию
import bpy

def check_bake_ready(obj_name="jacket"):
    ob = bpy.data.objects.get(obj_name)
    if not ob:
        print("нет объекта"); return
    uv_layers = [uv.name for uv in ob.data.uv_layers]
    print("UV-слои:", uv_layers or "НЕТ — запекание невозможно")
    print("активный движок:", bpy.context.scene.render.engine)
    mats = [m.name for m in ob.data.materials if m and m.use_nodes]
    for m in mats:
        imgs = [n.image.name for n in bpy.data.materials[m].node_tree.nodes if n.type == 'TEX_IMAGE']
        print(f"  {m}: текстуры {imgs or 'НЕТ'}")
    if bpy.context.scene.render.engine != 'CYCLES':
        print("внимание: EEVEE не умеет запекать. Переключись на Cycles.")

check_bake_ready()
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Запекание симуляции одежды не требует GUI при экспорте кэша:
# в Marvelous Designer File → Export → Simulation Cache выбираешь
# папку, диапазон кадров и формат (obj/abc). Дальше — обычная папка с файлами.

# Импорт кэша в Blender в batch-режиме (CI, без открытой сцены):
blender --background --python import_cloth.py -- /c/clo/cache /c/clo/out.blend
```

```python
# Сводка по всей одежде: толщина, коллизия, порядок модификаторов
import bpy
for ob in bpy.context.scene.objects:
    if ob.type != 'MESH':
        continue
    if not ob.modifiers:
        continue
    chain = " → ".join(m.type for m in ob.modifiers)
    sol = next((m for m in ob.modifiers if m.type == 'SOLIDIFY'), None)
    thick = f"{sol.thickness*1000:.1f} мм" if sol else "—"
    print(f"{ob.name:22s} {len(ob.data.vertices):>8,} v  {thick:>8s}  {chain}")
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| `scale` при Alembic-импорте | 0.01 | если импортируешь FBX/OBJ и он уже в метрах — 1.0 |
| `solidify.thickness` | 0.0002–0.003 м | 0.002 м (2 мм) — универсальное значение для ткани |
| `solidify.offset` | 0.0 или -1.0 | 0 — наружу и внутрь, -1 — только внутрь (для облегающего) |
| `use_even_offset` | `True` | без него толщина густеет на острых углах |
| `collision.collision_shape` | `CONVEX_HULL` | `MESH` точнее, но в разы медленнее и капризнее |
| `cloth.quality` | 5 | выше 8 — минуты вместо секунд, без заметного выигрыша |
| `cloth.mass` | 0.3 kg/vertex | меньше → ткань «летит», больше → «ватная» |
| `shrinkwrap.offset` | 0.005–0.01 м | меньше значения → z-fighting с телом |
| Bump/AO на одежде | запекать в 2K | мелкий шов виден только вблизи — нужен большой бюджет карт |

### Порядок модификаторов (то, что ломается чаще всего)

```text
Правильно:
  Shrinkwrap / Surface Deform  →  Solidify  →  Subdivision  →  Smooth  →  Weighted Normal

Неправильно:
  Solidify  →  Shrinkwrap      # толщина уже запечатана, потом её мнёт
  Solidify  →  Subdivision      # сабдив сгладит кромку, край станет скруглённым
```

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| Одежда в 100 раз больше тела | Сантиметры против метров | `scale=0.01` при импорте, либо сменить единицы сцены |
| Меш вверх ногами / повёрнут | Несовпадение осей OBJ | Для OBJ задай `forward_axis='NEGATIVE_Z', up_axis='Y'` |
| Импорт Alembic падает с `TypeError` | Список аргументов оператора изменился | `bpy.ops.wm.alembic_import.get_rna_type().properties.keys()` |
| Одежда «протекает» сквозь тело при рендере | Нет Collision на теле | Добавить Collision на тело, проверить `thickness_outer` |
| Ткань выглядит как картон | Толщина слишком большая или нечётная сетка | Уменьши thickness, включи `use_even_offset`, добавь Subdivision перед Solidify |
| Швы и строчки потерялись | Экспорт без UV | Включи UV в экспорте; проверь наличие UV-слоя после импорта |
| Нормали запечёлись кашей | Развёртка не сделана или острова перекрыты | Smart UV Project с margin 0.02, залей до запекания |
| Запекание не запускается | Активен EEVEE | Только Cycles |
| Alembic весит 400 МБ и едет | Полная симуляция по кадрам | Экспортируй кэш только на нужный диапазон кадров либо один статичный кадр |
| В Blender нет нормалей на одежде | Импорт без smooth normals | Включи Normals при экспорте; проверь `obj.data.shade_smooth()` |
| Zipper/пуговицы смещаются при анимации тела | Alembic не несёт привязки к скелету | Для анимации используй Cloth (в Blender) или привяжи через Surface Deform к деформированной сетке |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P03: MODIFIERS STACK](../prompts/03_modifiers_stack.md), [P21: PHYSICS SIMULATION](../prompts/21_physics_simulation.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #clothing, #setup