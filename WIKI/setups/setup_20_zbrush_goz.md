---
id: setup_20_zbrush_goz
lang: ru
category: setups
type: setup
status: full
tags: [sculpt, setup]
---
# SETUP 20: ZBRUSH GOZ BRIDGE

**ID:** SETUP-20 | **Type:** Sculpt | **Difficulty:** ⭐⭐ | **Time:** 30-50 min
**RU/EN Bilingual**

> Когда применять: когда детализация делается в ZBrush (поры, складки, разрушения), а сцена живёт в Blender. GoZ — это push-мост: ZBrush сам отправляет выбранный сабтул в активную программу, без ручного экспорта.

## 🎯 ЦЕЛЬ
Настроить двусторонний обмен между ZBrush и Blender через GoZ (GoZBrush), научиться передавать меш на нужном уровне subdivision, полипейнт как vertex color и карту смещения как displacement. На выходе — цикл «лепим в ZBrush → го в Blender → го обратно», в котором Blender остаётся источником формы, а ZBrush — источником деталей.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| ZBrush | 2022.0.5 и новее (ZBrush 2024 / 2025) | sculpt + отправитель GoZ |
| GoZ-плагин для Blender | версия, совместимая с твоим ZBrush и Blender | приёмник в Blender |
| ZBrushCentral / ZBrush 2024+ лицензия | — | сам ZBrush платный; **GoZ при этом бесплатен и open source** |
| Blender | 4.2 LTS+ | приём, vertex color, displacement |
| Карта смещения | 16- или 32-битная | true displacement |
| Одно из двух | Quad Remesher или ручная ретопология | игровая/рендерная топология |

> [!NOTE]
> GoZ — одна из немногих вещей в этом пайплайне, где не надо гадать: протокол и его реализации публичны (репозиторий GoZBrush), и в ZBrush он встроен. Проверь, что плагин Blender разрешает входящие подключения — иначе ZBrush будет писать в пустоту, молча.

## 🛠️ НАСТРОЙКА

### 1. Порядок запуска важен

```text
1. Blender  запустить ПЕРВЫМ и открыть нужную сцену
2. В ZBrush нажать GoZ (кнопка в панели Tool, справа внизу)
3. ZBrush подключится к Blender как к получателю
4. Дальше нажатие GoZ отправляет текущий сабтул в Blender
```

Если ZBrush запущен раньше Blender — подключения не будет, потому что ZBrush ищет получателя в момент нажатия GoZ, а не слушает постоянно.

### 2. Отправка меша и управление уровнем subdivision

```text
Уровни детализации в ZBrush настраиваются ДО нажатия GoZ:
  • В панели Tool справа внизу — 5 кнопок уровней SDiv (1–5)
  • Отмеченные уровни отправляются в Blender
  • Higher Resolution: если включить, ZBrush сама досчитает недостающие
    уровни перед отправкой (долго, зато не нужно ждать вручную)

Практика: отправлять на том уровне, где реально есть работа.
Уровень 5 на недовылепленном объекте — это миллионы пустых полигонов.
```

Что GoZ умеет передавать (перечень закрытый — что не входит, тем придётся обмениваться файлами):

| Что | Передаётся через GoZ | Файл вручную |
|-----|---------------------|--------------|
| Меш (выбранный уровень SDiv) | да | FBX / OBJ |
| Normals | да | — |
| UV | да (как есть в ZBrush) | FBX |
| Полипейнт → vertex color | да | OBJ/FBX + vertex color |
| Displacement (карта смещения) | да | TIFF/EXR |
| Mask | да | — |
| SubTools как отдельные объекты | зависит от настроек плагина | FBX |
| Материалы/шейдеры | нет | нет |

### 3. Polypaint → vertex color в Blender

```python
# goz_setup.py — Blender: Text Editor → Run Script
import bpy

def ensure_color_attribute(obj: bpy.types.Object, name="Col", domain='CORNER'):
    """
    GoZ обычно приносит vertex color под фиксированным именем.
    Создаём атрибут заранее, чтобы потом просто перезаполнять его.
    """
    if name in obj.data.color_attributes:
        return obj.data.color_attributes[name]
    return obj.data.color_attributes.new(name=name, type='BYTE_COLOR', domain=domain)

def setup_polypaint_material(obj: bpy.types.Object, mat_name="M_Polypaint"):
    """Vertex Color в Principled BSDF. В Blender 4.x нода Vertex Color
    ушла в Attribute (GEOMETRY) — имя атрибута задаётся вручную."""
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')

    attr = tree.nodes.new("ShaderNodeAttribute")
    attr.attribute_type = 'GEOMETRY'
    attr.attribute_name = "Col"
    attr.location = (-250, 100)

    tree.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    mat.use_fake_user = True
    return mat

def apply_polypaint(obj_name):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print("объект не найден:", obj_name); return
    ensure_color_attribute(obj)
    setup_polypaint_material(obj)
    # GoZ обновляет атрибут на месте; если переименовал — поправь в атрибуте
    print("vertex color подключён:", obj.name)

apply_polypaint("Cube")
```

Проверка, что цвет реально пришёл (должно быть видно на модели, а не серое):

```python
# Диагностика: смотрим реальные значения в атрибуте
obj = bpy.data.objects.get("Cube")
if obj:
    ca = obj.data.color_attributes.get("Col")
    if ca:
        n = len(ca.data)
        nonzero = sum(1 for d in ca.data if d.color[0] + d.color[1] + d.color[2] > 0.01)
        print(f"{ca.name}: {n} значений, ненулевых {nonzero} ({100*nonzero/max(n,1):.1f}%)")
    else:
        print("атрибута Col нет — GoZ не прислал полипейнт")
```

### 4. Displacement: карта смещения как настоящее смещение

```python
# displacement_setup.py — Blender: Text Editor → Run Script
import bpy, os

DISP_DIR = r"C:\zb"          # куда ZBrush сохранил карту
NAME = "disp.tiff"           # или disp.exr — зависит от того, что ты экспортировал

def setup_true_displacement(obj_name, disp_filename=NAME, scale=1.0):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print("нет объекта:", obj_name); return

    path = os.path.join(DISP_DIR, disp_filename)
    if not os.path.exists(path):
        print("нет карты смещения:", path); return

    img = bpy.data.images.load(path, check_existing=False)
    # Карта смещения — данные, не цвет: Non-Color обязателен
    img.colorspace_settings.name = 'Non-Color'

    disp = obj.modifiers.new("ZBrush Displace", 'DISPLACE')
    disp.texture = img
    disp.texture_coords = 'LOCAL'      # LOCAL = по системе координат объекта
    disp.mid_level = 0.5               # соответствует нулевому смещению
    disp.direction = 'NORMAL'
    disp.strength = scale

    # Порядок модификаторов критичен: смещение должно идти ПЕРЕД сабдивом
    subsurf = next((m for m in obj.modifiers if m.type == 'SUBSURF'), None)
    if subsurf:
        while obj.modifiers.find(subsurf.name) < obj.modifiers.find(disp.name):
            bpy.ops.object.modifier_move_up(modifier=subsurf.name)
    return disp

# Проверить, что карта не пустая
img = bpy.data.images.get("disp.tiff")
if img:
    px = list(img.pixels[:4096])
    mn, mx = min(px), max(px)
    print(f"диапазон карты: {mn:.3f}..{mx:.3f}",
          "— карта пустая" if mx - mn < 0.01 else "— карта информативна")
```

> [!NOTE]
> Экспорт карты смещения из ZBrush: `Tool → Displacement → Displacement Maps → Create` (предпросмотр), затем `Export`. Формат выбирай **16-битный TIFF или 32-битный EXR**: 8-битных карт не хватает на больших смещениях, шаг квантования становится виден. Точные пункты меню проверь в своей версии ZBrush — интерфейс заметно менялся между 2020 и 2025.

### 5. Ретопология: high → low

Главная ошибка — приносить high-poly в Blender и там разбираться. Правильная схема:

```python
# retopo_plan.py — Blender: Text Editor → Run Script
import bpy

def setup_retopo_workflow(high_name, low_name="Cube_Low"):
    """
    Высокая детальность живёт на отдельном объекте, рядом с игровым.
    В сцене они должны занимать одно и то же место.
    """
    high = bpy.data.objects.get(high_name)
    low  = bpy.data.objects.get(low_name)
    if not high or not low:
        print("нужны оба объекта:", high_name, low_name); return

    # Временная папка для проекции
    for ob in (high, low):
        mod = ob.modifiers.new("ProjectFromSurface", 'SURFACE_DEFORM')
        try:
            mod.target = high
            mod.falloff = 4.0
        except Exception as e:
            print("Surface Deform:", e)
            return

    print("Surface Deform настроен. Запеки через Object → Apply, иначе привязка живёт только в текущей сессии.")
```

```text
Если в проекте доступен Quad Remesher (аддон от Blender Studio / отдельная лицензия):
  Blender → Quad Remesher → Target = High, Target Preset = Quad, выбрать Target Surface
  → получаешь quad-меш на месте высокого, готовый к UV и запеканию.
  Это на порядок быстрее ручной ретопологии на органике.
```

> [!NOTE]
> Quad Remesher распространяется как отдельный аддон (Extension) с собственной лицензией и подпиской, и доступность/условия менялись. Проверь актуальный статус в списке Extensions в своей версии Blender, прежде чем строить на нём пайплайн. Альтернативы: Remesh → QuadriFlow (встроен в новые версии Blender как отдельный аддон), либо ручная ретопология.

### 6. Проверка сквозного цикла

```text
1. Запустить Blender, затем ZBrush
2. ZBrush → GoZ  (подключение)
3. Выбрать Tool → нажать GoZ  → в Blender появляется/обновляется объект
4. Перерисовать Polypaint в ZBrush → GoZ → vertex color в Blender обновился
5. Экспортировать displacement → подключить Displace в Blender
6. Surface Deform для проекции деталей на ретопологию
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Полная диагностика GoZ-сцены: что пришло, с чем, и где проблема
import bpy

def goz_report():
    print("=" * 50)
    print("Blender:", bpy.app.version_string)

    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    print(f"мешей в сцене: {len(meshes)}")

    for ob in meshes:
        attrs = [a.name for a in ob.data.color_attributes]
        mods = [f"{m.type}" for m in ob.modifiers]
        print(f"  {ob.name:20s} v={len(ob.data.vertices):>9,}  "
              f"color={attrs or '—'}  mods={mods or '—'}")

    # Проверка карт смещения
    for img in bpy.data.images:
        if img.source == 'FILE' and img.name.lower().startswith(("disp", "normal")):
            print(f"  {img.name}: {img.size[0]}×{img.size[1]}, "
                  f"colorspace={img.colorspace_settings.name}, depth={img.depth}")
    print("=" * 50)

goz_report()
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| Уровень SDiv на GoZ | 1–5, активный обычно 3–5 | 5 на грубом объекте = миллионы ненужных полигонов |
| Higher Resolution | вкл/выкл | включай, когда не хочешь ждать досчёта вручную |
| `mid_level` (Displace) | 0.5 | всегда 0.5, если ZBrush карта нормализована в 0..1 |
| `texture_coords` (Displace) | `LOCAL` | `GLOBAL` — если объект двигается в мире и смещение «поехало» |
| `strength` (Displace) | 0.01–0.05 м | слишком большое значение рвёт низкополигональную сетку |
| Формат карты смещения | 16-bit TIFF / 32-bit EXR | 8 бит = видимые ступеньки на больших смещениях |
| Attribute name (vertex color) | `Col` | имя задаёт плагин; если не совпадает — поправь в ноде Attribute |
| `BYTE_COLOR` vs `FLOAT_COLOR` | BYTE_COLOR | точность 8 бит на канал хватает для полипейнта |
| Subdivision после Displace | 1–2 уровня | смещение требует плотности; считай полигоны |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| ZBrush не видит Blender | ZBrush запущен раньше Blender | Перезапусти: сначала Blender, потом ZBrush, потом GoZ |
| Нажал GoZ, в Blender ничего | Плагин GoZ выключен или не установлен | `Edit → Preferences → Add-ons`, найти GoZ и включить |
| Пришёл объект с 20 млн полигонов | Отправлен SDiv 5 без Higher Resolution | Отправляй на том уровне, где есть работа; проверь на скриншоте |
| Vertex color в Blender серый | Атрибут называется не `Col`, либо перезаписался при GoZ | Назови в ноде Attribute точное имя атрибута из Mesh Properties → Color Attributes |
| Polypaint цвета «уехали» | Полипейнт в ZBrush в линейном пространстве, а в Blender интерпретируется как sRGB | Держи одинаковый colorspace в ZBrush и в Blender; проверь на градиенте |
| Displacement рвёт меш | Не хватает плотности сетки или `strength` слишком большой | Добавь Subdivision до Displace в порядке модификаторов, уменьши strength |
| Displacement смещается при движении объекта | `texture_coords='GLOBAL'` | Поставь `LOCAL` |
| Поверхность «плывёт» после запекания Surface Deform | Модификатор не применён | `Object → Apply`, иначе привязка не переживёт перезагрузку файла |
| Материал из ZBrush не пришёл | GoZ не передаёт материалы | Собирай материал в Blender вручную: это 6 нод, а не проблема пайплайна |
| Экспорт карты смещения даёт серое | Включён Grayscale/Monochrome, карта без данных | В ZBrush сначала `Create`, потом `Export`; проверь диапазон пикселей скриптом выше |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P08: SCULPTING BASICS](../prompts/08_sculpting_basics.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #sculpt, #setup