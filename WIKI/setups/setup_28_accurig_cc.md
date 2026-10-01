---
id: setup_28_accurig_cc
lang: ru
category: setups
type: setup
status: full
tags: [rigging, setup]
---
# SETUP 28: ACCURIG / ACTORCORE RIG

**ID:** SETUP-28 | **Type:** Auto Rig | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

> Когда применять: нужен риг на персонаже, для которого Reallusion-сообщество уже насделало качественные анимации — то есть важна совместимость скелета, а не скорость авторинга.

## 🎯 ЦЕЛЬ
Собрать в Blender риг, совместимый с анимациями ActorCore от Reallusion, и убедиться, что веса и оси костей не разъедутся. Разбираем путь через браузерный AccuRig (генерация скелета по фото-проекциям), установку плагина ActorCore в Blender и честное ограничение: универсального авто-ретаргета в Blender нет, поэтому скелепы приводятся к единому виду вручную или констрейнтами.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | целевая сцена |
| AccuRig (браузер) | актуальная, `accurig.com` | генерация скелета и автовеса |
| ActorCore Plugin for Blender | версия под свою Blender | импорт анимаций, конвертация скелета |
| Исходный меш | гуманоид, T-pose или A-pose | вход для AccuRig |

> [!NOTE]
> Точные пункты меню и название плагина менялись вместе с переездом Reallusion на новый сайт. Ориентируйся на поиск в самом Blender: `Preferences → Add-ons → Install`, архив плагина берётся с официальной страницы Reallusion. Не качай плагин со сторонних зеркал — они регулярно ломаются после обновлений.

## 🛠️ НАСТРОЙКА

### 1. Подготовка меша
AccuRig определяет суставы по силуэту, поэтому лишняя геометрия (волосы, рюкзак, массивная одежда) резко ухудшает результат. Импортируй тело без головы и без волос — голову добавишь отдельно.

```python
import bpy

ob = bpy.context.view_layer.objects.active
ob.name = "BODY"

# Размер в метрах, масштаб применён: AccuRig работает с абсолютными пропорциями
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Проверить, что меш реально в позе, а не в A-stand с руками вдоль тела
print("рост по Z:", max(v.co.z for v in ob.data.vertices) -
      min(v.co.z for v in ob.data.vertices))
```

### 2. Генерация скелета в AccuRig
Браузерный шаг: загрузи FBX → расставь ключевые точки суставов (таз, плечи, локти, запястья, бёдра, колени, стопы) → подтверди, что скелеп в нужной позе → скачай экспорт.

```python
# Экспорт входного FBX: без скелета, только меш
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.context.view_layer.objects.active = ob

bpy.ops.export_scene.fbx(
    filepath=r"C:\work\accurig\body.fbx",
    use_selection=True,
    object_types={'MESH'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    path_mode='AUTO',
)
```

Что выбрать в самом AccuRig при экспорте, зависит от цели:

| Вариант экспорта в AccuRig | Что получается | Когда брать |
|---|---|---|
| Только скелет (skeleton) | чистая костная структура | свой риг на своём меше |
| Скелет + автовеса | FBX с готовыми весами | быстрый старт без ручного веса |
| С ActorCore-совместимой структурой | имена костей под анимации Reallusion | нужна библиотека ActorCore |

### 3. Импорт и привязка в Blender
```python
bpy.ops.import_scene.fbx(
    filepath=r"C:\work\accurig\body_skeleton.fbx",
    automatic_bone_orientation=True,
    global_scale=1.0,
)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.name = "AccuRig"

# Классическая автопривязка: распределяет веса по прогреву костей
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
```
Типы у оператора реально такие: `ARMATURE_AUTO`, `ARMATURE_NAME`, `ARMATURE_ENVELOPE`, `ARMATURE_WITH_EMPTY_GROUP`.

### 4. Оси костей
AccuRig и ActorCore используют Y как костную ось и X как ось наклона. Blender по умолчанию Y-up в костях, поэтому при первой генерации рига оси надо задать явно — иначе анимации будут вставать «на бок».

```python
# Пересчитать ролл костей под свои оси (Edit Mode, выделенные кости).
# Доступные значения type: POSITIVE_X / NEGATIVE_X / POSITIVE_Z / NEGATIVE_Z
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.armature.calculate_roll(type='POSITIVE_X')
bpy.ops.object.mode_set(mode='OBJECT')

# Прочитать, что получилось, и сверить с ожидаемым:
# у всех костей, кроме корневой, Y должен смотреть вдоль кости
for b in arm.pose.bones[:5]:
    print(b.name, "→ head", tuple(round(c, 3) for c in b.head),
          "tail", tuple(round(c, 3) for c in b.tail))
```

> [!NOTE]
> Автонаправление костей (`Bone envelopes`, `Inverse matrices`, `Automatic align rolls`) в Rigify и в авто-ригах задаётся по-разному. Универсального способа «выровнять всё» в bpy нет — у каждого рига своя процедура. Сверяйся с документацией конкретного аддона, а не с общим описанием Blender.

### 5. Сохранение объёма при деформации
Тонкие участки — запястья, шея, щиколотка — «схлопываются» при линейных весах. Двойные кватернионы это чинят.

```python
for pb in arm.pose.bones:
    pb.use_deform_preserve_volume = True   # Soft/dual-quaternion skinning
```
Если этого мало, помогает классическая связка: автоматические веса + контрольный меш (в ARP это Clean Plate, в других ригах — дубликат поверхности).

### 6. Импорт анимаций ActorCore
Открываешь `.fbx` или `.actor` из библиотеки ActorCore через плагин. Главный нюанс: имена костей должны совпасть с уже привязанным ригом. Если AccuRig дал другие имена — скелет надо переименовать или привести к общему виду до импорта.

```python
# Сверка имён: что пришло из рига и что ожидает библиотека
arm_bones = {b.name for b in arm.data.bones}
print(sorted(arm_bones))
```

### 7. Ретаргет, если скелеты не совпадают
Универсального авто-ретаргета в Blender нет — это факт, а не недоработка: встроенный стек работает с BVH и с одинаковыми именами костей. Когда источник и приёмник ригов различаются, рабочий путь — констрейнты на уровне костей.

```python
# Ретаргет через констрейнт: копия поворота с кости-источника на кость-приёмник
src_arm = bpy.data.objects["ImportedAnimation"]   # арматура-источник
dst = arm.pose.bones["upperarm.R"]                # имя кости уточни в своём риге
src = src_arm.pose.bones["RightArm"]              # кость-источник

con = dst.constraints.new('COPY_ROTATION')
con.target = src_arm
con.subtarget = src.name
con.target_space = 'WORLD'
con.owner_space = 'WORLD'
con.mix_mode = 'BEFORE'
con.influence = 1.0

# Прогнать кадр, чтобы констрейнты пересчитались
bpy.context.scene.frame_set(bpy.context.scene.frame_current)
```

> [!NOTE]
> Констрейнт «копия поворота» не учитывает разницу в длине костей и в оценочной позе, поэтому для серьёзного продакшна ретаргет дописывают руками. Для быстрой проверки «анимация вообще похожа» — способ рабочий.

### 8. Диагностика перед сдачей
```python
# Свести всё в одну таблицу: что приехало и в каком состоянии
for o in bpy.data.objects:
    if o.type == 'MESH':
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        print(f"{o.name}: tris={tris} mods={[m.type for m in o.modifiers]}")
    elif o.type == 'ARMATURE':
        print(f"{o.name}: костей={len(o.data.bones)} "
              f"групп={len(o.vertex_groups)}")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Применить позу как новую оценочную — после импорта анимации
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.armature_apply()
bpy.ops.object.mode_set(mode='OBJECT')
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `parent_set(type=)` | `ARMATURE_AUTO` | `ARMATURE_WITH_EMPTY_GROUP` — когда автовес даёт мусор |
| `pb.use_deform_preserve_volume` | `True` | `False` — если анимации сжимают суставы сильнее, чем «линейно» |
| `automatic_bone_orientation` | `True` | `False` — когда импорт кладёт кости боком |
| `global_scale` | `1.0` | подбирается под размер персонажа; FBX хранит его в самом файле |
| `mesh_smooth_type` | `FACE` | `EDGE` — для хард-нормалей на рёбрах |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| AccuRig ставит суставы в сторону | на меш попали волосы, одежда или дубликат | Экспортировать голое тело, повторить |
| Автовеса не распределились | пересекающиеся кости, невыпуклая топология | Переделать сетку в районе таза/плеч, весать вручную |
| Анимация из ActorCore не цепляется | имена костей не совпадают | Сверить `arm.data.bones` с именами в библиотеке |
| Кости повёрнуты на 90° | не задан bone orientation при импорте | Переимпортировать с `automatic_bone_orientation=True` |
| Локти и колени «схлопываются» | линейные веса | Включить `use_deform_preserve_volume` |
| Плагин не появился в списке аддонов | несовместимая версия Blender | Проверить требования плагина к версии Blender |
| Персонаж сместился после Apply | Apply Pose с неприменённым масштабом | Заранее `transform_apply` |

## 🖥 MCP-ПРОМПТ

```text
RU: "AccuRig: экспорт скелета тела, импорт FBX, parent_set ARMATURE_AUTO,
     preserve volume на всех костях, сверка имён с библиотекой ActorCore" /
EN: "AccuRig: export body skeleton, import FBX, ARMATURE_AUTO parenting,
     preserve volume on all bones, compare names with ActorCore library"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 27: MIXAMO AUTO-RIG](setup_27_mixamo_autorig.md), [SETUP 29: AUTO-RIG PRO](setup_29_autorignpro.md), [SETUP 30: RIGIFY ADVANCED + FACE](setup_30_rigify_advanced.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P17: RIGIFY HUMANOID SETUP](../prompts/17_rigify_setup.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #rigging, #setup