---
id: setup_36_vroid_studio
lang: ru
category: setups
type: setup
status: full
tags: [blender, character, setup]
---
# SETUP 36: VROID STUDIO → BLENDER

**ID:** SETUP-36 | **Type:** Anime | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

> Когда применять: делаешь аниме-аватара в VRoid Studio и нужно довести его до рендера или до VRM-сцены в Blender.

## 🎯 ЦЕЛЬ
Импортировать VRM 1.0 в Blender, разобраться, что делать с материалами MToon и пружинными костями волос, и честно оценить, что из правок Blender переживёт обратный экспорт в VRoid Studio. Последний пункт важнее остальных: формат VRM проектировался для «модель + риг + выражения лица», и любая ручная правка геометрии в Blender за пределами допустимого почти всегда ломает обратный путь.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| VRoid Studio | актуальная | создание модели и выгрузка VRM |
| VRM 1.0 | спецификация, `vrM.dev` | формат обмена |
| Blender | 4.x | импорт, рендер, доработка |
| VRM-аддон для Blender | входит в поставку Blender, включается в Preferences → Add-ons | импорт и экспорт VRM |

> [!NOTE]
> Аддон импорта VRM есть в поставке Blender, но в разных версиях он называется и лежит по-разному («VRM Add-on for Blender» / включён через Add-ons / вынесен в расширения). Плюс существует популярная одноимённая версия аддона от сообщества — с куда большим числом настроек. Проверь в `Preferences → Add-ons`, что именно у тебя включено, до того как писать пайплайн: у них разные возможности экспорта.

## 🛠️ НАСТРОЙКА

### 1. Подготовка модели в VRoid Studio
Модель настраивается до выгрузки: поза, материалы, набор выражений лица, шейдер. Важное правило — VRM хранит только то, что описано стандартом; всё остальное при обратном импорте теряется.

```text
1. VRoid Studio → собрать модель (тело, одежда, причёска)
2. Настроить материалы: MToon, параметры (outline, rim, matcap)
3. Задать набор выражений лица (A / I / U / E / O, blink и т.д.)
4. Pose → выбрать позу (обычно A-Pose) → File → Export → VRM 1.0
```

### 2. Импорт в Blender
```python
import bpy

print("blender:", bpy.app.version_string)
print("vrm-аддоны:", [k for k in bpy.context.preferences.addons.keys()
                       if "vrm" in k.lower()])

bpy.ops.import_scene.vrm(filepath=r"C:\work\vrm\avatar.vrm")
```
Оператор `import_scene.vrm` появляется только после включения аддона. Если его нет — версия аддона не совпадает с версией Blender.

```python
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        mats = [m.name for m in o.data.materials]
        print(f"{o.name}: tris={tris} mats={mats}")
    elif o.type == 'ARMATURE':
        print(f"{o.name}: костей={len(o.data.bones)}")
```

### 3. Материалы MToon
MToon — это toon-шейдер, заточенный под нелинейное освещение в VR-движках. В Blender его нет: аддон либо собирает node group по параметрам MToon, либо (в части версий аддона) умеет привести материал к стандартному Principled BSDF.

```python
# Посмотреть, что вообще собрал аддон
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    for m in o.data.materials:
        if not m or not m.use_nodes:
            continue
        kinds = sorted({n.type for n in m.node_tree.nodes})
        print(m.name, "->", kinds)
```

> [!NOTE]
> Пункт «конвертировать MToon в Principled» существует не во всех сборках аддона и называется по-разному. Если в твоей версии такого пункта нет — это не баг, а ограничение: придётся собирать шейдер вручную, и toon-look придётся воспроизводить освещением (Flat/Toon шейдер Cycles), а не материалом.

### 4. Пружинные кости
Волосы и некоторые элементы одежды анимируются spring bones — цепочка костей, колеблющихся от движения головы. В VRoid Studio это отдельная сущность; в Blender она либо приезжает как цепочка костей, либо теряется.

```python
# Найти цепочки: кости без родителя, но с потомками — кандидаты на пружины
arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
if arm:
    for b in arm.data.bones:
        if b.parent is None or not b.use_connect:
            kids = [c.name for c in b.children]
            if kids:
                print("корень цепочки:", b.name, "-> потомки:", kids[:4])
```

Что делать, если пружины не приехали: пересобрать волосы как цепочку костей вручную и анимировать через drivers либо через `Hook`/constraints. Это отдельная работа на несколько часов, и обратно в VRoid Studio она не экспортируется.

### 5. Обратный экспорт — что теряется
```python
# Перед экспортом: что вообще можно выгрузить обратно в VRM
print("mesh objects:", sum(1 for o in bpy.data.objects if o.type == 'MESH'))
print("shape keys:",
      sum(len(o.data.shape_keys.key_blocks)
          for o in bpy.data.objects
          if o.type == 'MESH' and o.data.shape_keys))

# Экспорт через аддон VRM
bpy.ops.export_scene.vrm(filepath=r"C:\work\vrm\avatar_out.vrm")
```
Реалистичный список потерь: любые нестандартные модификаторы, добавленные тобой меши, новые кости без привязки к стандартным именам VRM, изменения UV, материалы, которые не являются MToon.

| Что делал в Blender | Вернётся ли в VRoid Studio |
|---|---|
| Подвинул вершины | нет |
| Добавил shape keys | нет |
| Новый материал | нет |
| Удалил кость стандарта VRM | нет, файл может стать невалидным |
| Переименовал кость | нет, сломает стандарт |
| Ничего не менял | да, round-trip безопасен |

### 6. Для VRM-движка — не трогай Blender
Если конечная цель — VRM-сцена в Unity или WebXR, правильный путь — экспортировать из VRoid Studio напрямую и не редактировать в Blender. Blender полезен, когда цель — рендер картинок или видео, а не интерактив.

```python
# Проверка перед рендером: нормали, материалы, объём геометрии
for o in bpy.data.objects:
    if o.type == 'MESH':
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        has_mat = any(m and m.use_nodes for m in o.data.materials)
        print(f"{o.name}: tris={tris} материалы={'да' if has_mat else 'НЕТ'}")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Сводка по модели: вершины, кости, ключи формы
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
print("вершин:", len(mesh.data.vertices))
print("shape keys:", len(mesh.data.shape_keys.key_blocks)
      if mesh.data.shape_keys else 0)
print("UV-карт:", len(mesh.data.uv_layers))
```

| Параметр | Значение | Когда менять |
|---|---|---|
| формат VRM | `1.0` | `0.x` — только если приёмник старый |
| поза в VRoid Studio | A-Pose | T-Pose — если планируется риг в Blender |
| материал в Blender | MToon node group | Principled — если рендеришь в Cycles/EEVEE, а не в VR |
| шейдер Cycles для toon | `Flat` | `Toon` — когда нужен жёсткий контур |
| `export_scene.vrm` | только из исходной модели | после любых правок результат гарантированно теряется |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `import_scene.vrm` не найден | аддон не включён или несовместимая версия | Проверить `Preferences → Add-ons`, при необходимости поставить версию аддона от сообщества |
| Материал выглядит как обычный пластик | MToon не переведён в поддерживаемый шейдер | Либо конвертировать в Principled, либо собрать toon-освещение в Cycles |
| Пружинные волосы не двигаются | цепочки не импортировались или потеряли коллайдеры | Пересобрать вручную цепочку костей + drivers |
| После экспорта в VRM Studio модель не открывается | нарушен стандарт VRM | Откатиться к исходному VRM и экспортировать без ручных правок |
| Материалы потеряли цвет | texture slots переставлены | Не редактировать UV/slots, если нужен обратный путь |
| Лицо без выражений | набор expressions не передан | Экспортировать с включёнными expressions из VRoid Studio |
| Модель в 10 раз меньше | нормализация роста в формате | Масштабировать вручную; единицы Blender при этом ни при чём |

## 🖥 MCP-ПРОМПТ

```text
RU: "Импортируй avatar.vrm, выведи по объектам треугольники, материалы и их
     типы нод, найди цепочки костей волос, проверь наличие shape keys" /
EN: "Import avatar.vrm, print per-object triangles, materials and their
     node types, find hair bone chains, check for shape keys"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 32: DAZ → BLENDER (DIFFEOMORPHIC)](setup_32_daz_diffeomorphic.md), [SETUP 34: METAHUMAN → BLENDER](setup_34_metahuman_blender.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #blender, #character, #setup