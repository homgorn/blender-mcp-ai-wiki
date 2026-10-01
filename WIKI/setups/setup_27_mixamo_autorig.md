---
id: setup_27_mixamo_autorig
lang: ru
category: setups
type: setup
status: full
tags: [rigging, setup]
---
# SETUP 27: MIXAMO AUTO-RIG

**ID:** SETUP-27 | **Type:** Auto Rig | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

> Когда применять: нужен рабочий гуманоидный риг с библиотекой анимаций за один сеанс, без ручной сборки скелета.

## 🎯 ЦЕЛЬ
Провести персонажа из Blender через веб-авторинг Mixamo, получить скелет и анимации обратно в сцену и починить то, что ломается при импорте FBX. Отдельно разбираем главное ограничение Mixamo: в скелете нет костей пальцев — если пальцы нужны, риг собирается иначе.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | FBX-импорт, проверка скелета |
| Adobe Mixamo | актуальная версия, браузер | авторинг и библиотека motion capture |
| Аккаунт Adobe | бесплатного тарифа хватает | загрузка персонажа и скачивание клипов |
| FBX-экспорт из Blender | встроенный | только меш, без уже существующего рига |

## 🛠️ НАСТРОЙКА

### 1. Готовим персонажа к загрузке
Mixamo анализирует силуэт, поэтому сцена не должна быть заслонена. Проверь три вещи: ориентация (лицом по `+Y`, носом по `+Z`), отсутствие лишних частей (волосы, одежда мешают автоопределению суставов) и пропорции.

```python
import bpy

ob = bpy.context.view_layer.objects.active
ob.name = "CHAR"

# Единицы: метры, без применённого масштаба — FBX переносит масштаб как есть
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Сохраняем только видимую геометрию
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.context.view_layer.objects.active = ob
```

Позу перед загрузкой держи в **T-pose** или **A-pose** — руки вдоль тела либо строго в стороны. В T-pose плечи и локти определяются увереннее, в A-pose меньше риск, что авторинг притаит руки к торсу.

### 2. Экспорт в Mixamo
```python
bpy.ops.export_scene.fbx(
    filepath=r"C:\work\mixamo\char.fbx",
    use_selection=True,
    object_types={'MESH'},        # только меш: старый риг Mixamo перезапишет
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,          # висячие кости в игре ломают маппинг
    path_mode='AUTO',
)
```
На стороне сайта Mixamo: загрузи FBX, пройди три шага авторинга (постановка скелета → проверка → выбор модели), на этапе выбора модели подтверди, что поза соответствует указанной тобой. Скачай **with skin**, если нужен готовый персонаж, и **without skin**, если анимация нужна для твоего собственного рига.

### 3. Импорт обратно и разбор результата
```python
bpy.ops.import_scene.fbx(
    filepath=r"C:\work\mixamo\char_with_skin.fbx",
    automatic_bone_orientation=True,
    global_scale=1.0,
    use_anim=True,
)
```
После импорта в сцене два объекта: меш и арматура. Все кости называются с префиксом `mixamorig:` — это не баг, а способ Mixamo избежать конфликтов имён при объединении нескольких клипов.

```python
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = "mixamorig"

print("костей:", len(arm.data.bones))
print("есть ли пальцы:",
      any(b.name.startswith("mixamorig:LeftHandIndex") for b in arm.data.bones))
```

### 4. Приводим меш в порядок
Сглаживание нормалей ломается на стыках импортированного FBX. Пересчитываем по углу, иначе в движении появляются тёмные полосы на плечах и бёдрах.

```python
mesh_ob = next(o for o in bpy.data.objects if o.type == 'MESH')
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = mesh_ob
mesh_ob.select_set(True)

try:
    bpy.ops.object.shade_smooth_by_angle(angle=0.523599)  # 30°, Blender 4.1+
except RuntimeError:
    mesh_ob.data.use_auto_smooth = True                  # Blender 4.0 и раньше
    mesh_ob.data.auto_smooth_angle = 0.523599
```

> [!NOTE]
> Симметрию нормалей проверяй вручную: у FBX из Mixamo она обычно корректна, но после любых ручных правок — нет. Отдельный оператор `normals_make_consistent` (`bpy.ops.mesh.normals_make_consistent(inside=False)`) существует только в Edit Mode.

### 5. Снимаем локти и плечи
Классическая проблема: объём предплечья уезжает, плечо проваливается. Лечится не ригом, а весами и корректирующими формами.

```python
# Проверяем, что каждая кость реально управляет чем-то:
# пустая группа = веса не перенеслись, меш не привязан
def weights_for(arm, mesh, bone_name):
    vg = arm.vertex_groups.get(bone_name) or arm.vertex_groups.get(
        "mixamorig:" + bone_name)
    if vg is None:
        return "нет группы"
    n = sum(1 for v in mesh.data.vertices
            for g in v.groups if g.group == vg.index)
    return f"{n} вершин"

for bn in ("Hips", "Spine", "LeftArm", "RightArm"):
    print(bn, "->", weights_for(arm, mesh_ob, bn))
```

> [!NOTE]
> У Mesh-объекта группы весов лежат в `mesh.vertices[i].groups` (записи с полями `group` и `weight`), а список самых групп — в `armature.vertex_groups`. Имя группы у Mixamo совпадает с полным именем кости, то есть с префиксом. Путаница между этими двумя списками — самая частая причина «весов нет нигде».

### 6. Склейка клипов на одном риге
Скачанные клипы приходят отдельными файлами с копиями арматуры. Дальше их нужно свести к одному скелету: иначе в сцене будет пять одинаковых персонажей.

```python
import os

# 1. Импортировать клип как Action в существующую арматуру.
# Оператор bpy.ops.nla.* работает по выделенному объекту, поэтому
# сначала делаем активной именно ту арматуру, к которой хотим привязать клип.
rig = bpy.data.objects["mixamorig"]
bpy.context.view_layer.objects.active = rig
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)

clip = r"C:\work\mixamo\clips\walk.fbx"
bpy.ops.import_scene.fbx(filepath=clip, use_anim=True)

# 2. В NLA-редакторе (Animation workspace → NLA Editor) действие
#    появится как новый Action; перетащи его на канал сдвига.
#    Проверить, что он действительно появился:
for act in bpy.data.actions:
    print(act.name, "→", len(act.fcurves), "кривых")
```

> [!NOTE]
> Массовое заполнение NLA через bpy возможно, но оно же и хрупко: нужно вручную выставлять диапазон strip'а и слои. Для пяти клипов быстрее сделать это мышью, чем писать код. Если клипов больше тридцати — тогда пиши скрипт.

### 7. Массовая выгрузка клипов
```python
import os
OUT = r"C:\work\mixamo\clips"
os.makedirs(OUT, exist_ok=True)

CLIPS = ["idle", "walk", "run", "jump", "wave"]
for name in CLIPS:
    bpy.ops.import_scene.fbx(
        filepath=os.path.join(OUT, f"{name}.fbx"),
        automatic_bone_orientation=True,
        use_anim=True,
    )
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Как выглядит результат: сколько костей, какие action'ы, сколько ключей
for act in bpy.data.actions:
    print(act.name, "→", len(act.fcurves), "кривых")
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `object_types` | `{'MESH'}` | `{'ARMATURE','MESH'}` — если везёшь свой риг в Mixamo |
| `add_leaf_bones` | `False` | `True` — если движок требует хвосты у листьев |
| `automatic_bone_orientation` | `True` | `False` — если скелет ложится боком |
| `mesh_smooth_type` | `FACE` | `EDGE` — когда нужны хард-нормали на рёбрах |
| поза перед загрузкой | T-pose / A-pose | менять под конкретный меш, авторинг не всегда угадывает |
| `use_anim` при импорте | `True` | `False` — когда нужна только геометрия |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Авторинг «зацепил» кисти за торс | поза не T/A или пальцы прижаты | Повторить в чистой T-pose, без одежды и волос |
| Кости называются `mixamorig:Hips` | это штатное имя из FBX | Не переименовывать: клипы привязаны к этим именам |
| Нет костей пальцев | в риге Mixamo их нет в принципе | Добавить вручную либо собрать риг через Rigify/ARP |
| Рука проходит сквозь бедро | веса не перенеслись, меш не привязан | Проверить модификатор Armature и его цель |
| Тёмные полосы на сгибах | нормали не пересчитаны после импорта | `shade_smooth_by_angle` |
| Анимация проиграется рывками | снят `use_anim` или клип без ключей | Импортировать с `use_anim=True` |
| Персонаж после импорта лежит | `automatic_bone_orientation` справился не со всеми костями | Ручная ориентация в Pose Mode → `R` / выравнивание по костям |

## 🖥 MCP-ПРОМПТ

```text
RU: "Экспортируй CHAR в FBX только мешем, без leaf bones, для Mixamo" /
EN: "Export CHAR to FBX, mesh only, no leaf bones, for Mixamo"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 28: ACCURIG / ACTORCORE RIG](setup_28_accurig_cc.md), [SETUP 29: AUTO-RIG PRO](setup_29_autorignpro.md), [SETUP 30: RIGIFY ADVANCED + FACE](setup_30_rigify_advanced.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P17: RIGIFY HUMANOID SETUP](../prompts/17_rigify_setup.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #rigging, #setup