---
id: setup_56_mocap_rokoko
lang: ru
category: setups
type: setup
status: full
tags: [mocap, setup]
---
# SETUP 56: MOCAP ROKOKO / MOVE AI

**ID:** SETUP-56 | **Type:** Mocap | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

> Когда применять: когда есть FBX с телом — запись смартфона, Rokoko Studio или
> Move AI — и его нужно перенести на свой риг и привести в порядок.

---

## 🎯 ЦЕЛЬ

Собрать повторяемый путь FBX → свой риг → запечённая анимация, с честным
разбором двух мест, где ломается всё: оси FBX и доступ к F-кривым.

Все вызовы API в статье проверены на Blender 5.2.1 LTS.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 5.x (проверено 5.2.1) | Импорт FBX, риг, запекание |
| Исходный FBX | экспорт из студии | Только FBX: `.fbx` встроенный, `io_fbx=True` |
| Целевой риг | Armature | Куда ретаргетить (в примере — человеческая цепь) |
| Текстовый редактор | любой | Держать таблицу соответствия костей |

---

## 🛠️ НАСТРОЙКА

### 1. Импортировать FBX с явными осями

Здесь ловушка, на которой спотыкается половина импортов: **в Blender 5.x
перечисления осей FBX — это `'X'`, `'Y'`, `'Z'`, `'-X'`, `'-Y'`, `'-Z'`**, а не
старые имена вида `Y_FORWARD`. Проверено на 5.2.1: попытка передать `Y_FORWARD`
падает с `enum "Y_FORWARD" not found`.

```python
# import_mocap.py
import bpy

AXES = {                      # проверенные значения enum в Blender 5.2
    'Y_FORWARD': '-Z',        # Blender Y-up -> FBX Y-up: вперёд = -Z в Blender
    'Z_FORWARD': '-Y',        # Blender Z-up -> FBX Z-up
}

axis_forward, axis_up = '-Z', 'Y'

bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.fbx(
    filepath="//mocap/take_01.fbx",
    use_anim=True,
    bake_anim=True,                     # кривые сразу в Action, без NLA-полос
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_bones=True,
    bake_anim_force_startend_keying=True,
    object_types={'ARMATURE', 'MESH'},  # проверенный набор в 5.2
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    axis_forward=axis_forward,
    axis_up=axis_up,
    use_custom_props=False,
)
```

`bake_anim_use_nla_strips=False` — принципиально: иначе каждая полоса NLA
станет отдельным источником, и дальнейшая чистка кривых превратится в
неразбираемую кашу.

### 2. Сверить масштаб и ориентацию до ретаргета

```python
def audit_rig(ob):
    """Напечатать то, из-за чего потом «плывут ноги»."""
    names = [b.name for b in ob.pose.bones]
    print("height_m:", max((ob.matrix_world @ b.tail).z for b in ob.pose.bones))
    print("bone_count:", len(names))
    return names

src_bones = audit_rig(bpy.data.objects["take_01_armature"])
dst_bones = audit_rig(bpy.data.objects["MY_RIG"])

# Масштаб сцены правится один раз, до ретаргета:
bpy.data.objects["take_01_armature"].scale = (0.01, 0.01, 0.01)  # FBX в сантиметрах
```

Проверка, которую стоит делать всегда: рост скелета в метрах. Если скелет выше
2.2 м — у вас сантиметры или неверный `axis_up`, и никакой ретаргет это не
починит.

### 3. Построить таблицу костей и проверить её

Имена костей в FBX задаёт экспортирующая сторона: они отличаются у Rokoko, Move
AI и любого другого инструмента. Поэтому маппинг — это **ваш файл**, а не
свойство формата, и его надо проверять на реальном файле, а не писать по памяти.

```python
# bone_map.py — маппинг хранится в файле, а не в коде скрипта
BONE_MAP = {
    "Hips":      "pelvis",
    "Spine":     "spine_fk",
    "Chest":     "spine_ik",
    "Neck":      "neck",
    "Head":      "head",
    "LeftUpLeg": "thigh_fk.L",   "LeftLeg":   "shin_fk.L",
    "LeftFoot":  "foot_fk.L",    "LeftToe":   "ball_fk.L",
    "RightUpLeg":"thigh_fk.R",   "RightLeg":  "shin_fk.R",
    "RightFoot": "foot_fk.R",    "RightToe":  "ball_fk.R",
    "LeftArm":   "upper_arm_fk.L",  "LeftForeArm": "forearm_fk.L",
    "RightArm":  "upper_arm_fk.R",  "RightForeArm":"forearm_fk.R",
}

def verify_map(src_bones, dst_bones, mapping):
    missing_dst = sorted(set(mapping.values()) - set(dst_bones))
    missing_src = sorted(set(mapping) - set(src_bones))
    if missing_dst:
        print("НЕТ В ЦЕЛЕВОМ РИГЕ:", missing_dst)
    if missing_src:
        print("НЕТ В ИСХОДНОМ FBX:", missing_src)
    return len(mapping) - len(missing_src)

print("mapped:", verify_map(src_bones, dst_bones, BONE_MAP))
```

### 4. Ретаргетить констрейнтами

Классический способ: копировать **мировую** ориентацию костей, а не локальную.
Локальное копирование ломается, когда у источника и цели разные длины костей.

```python
def retarget(dst, src, mapping):
    bpy.ops.object.select_all(action='DESELECT')
    dst.select_set(True)
    bpy.context.view_layer.objects.active = dst
    bpy.ops.object.mode_set(mode='POSE')
    added = 0
    for sbone, dbone in mapping.items():
        if sbone not in src.pose.bones or dbone not in dst.pose.bones:
            continue
        c = dst.pose.bones[dbone].constraints.new('COPY_ROTATION')
        c.target, c.subtarget = src, sbone
        c.target_space = 'WORLD'      # читать в мире...
        c.owner_space  = 'WORLD'      # ...и писать в мире
        added += 1
    bpy.ops.object.mode_set(mode='OBJECT')
    return added

print("constraints:", retarget(bpy.data.objects["MY_RIG"],
                               bpy.data.objects["take_01_armature"],
                               BONE_MAP))
```

### 5. Запечь и снять констрейнты

```python
# Запекание в NLA с визуальным ключированием: контроллеры IK/FK
# пересчитываются «как видит глаз», а не как считает формула.
bpy.ops.object.select_all(action='DESELECT')
dst = bpy.data.objects["MY_RIG"]
dst.select_set(True)
bpy.context.view_layer.objects.active = dst

bpy.ops.nla.bake(
    frame_start=1, frame_end=int(dst.animation_data.action.frame_range[1]),
    step=1,
    only_selected=False,
    visual_keying=True,
    clear_constraints=True,       # констрейнты уходят сразу после запекания
    clear_parents=False,
    clean_curves=False,           # чистим сами, следующим шагом
    use_current_action=True,
)
```

### 6. Почистить кривые

В Blender 5.x F-кривые больше **не** лежат в `action.fcurves` — свойства нет,
`AttributeError`. Правильный путь: `action.layers[0].strips[0].channelbags[0]`.
Проверено на 5.2.1.

```python
def action_fcurves(action):
    """Достать F-кривые из slotted Action в Blender 4.4+/5.x.
    Старый action.fcurves в 5.x удалён."""
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                yield from cb.fcurves

def clean(action):
    """Ровняем хэндлы: AUTO_CLAMPED не даёт кривой уйти в сторону
    между соседними ключами — это и есть главный источник одиночных
    «дёрганий» на коже."""
    n = 0
    for fc in action_fcurves(action):
        for kp in fc.keyframe_points:
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()
        n += 1
    return n

print("curves cleaned:", clean(dst.animation_data.action))
```

Дополнительно стоит прогнать `bpy.ops.graph.smooth(type='SMOOTH')` с выделенными
ключами — но порог подбирают вручную: у таза и у стопы он разный, и одна цифра
для всей анимации либо съест движение, либо ничего не уберёт.

### 7. Зациклить

```python
def make_loop(action, frame_start, frame_end):
    """Cycles-модификатор повторяет диапазон бесконечно.
    Проверенный набор типов в 5.2: NULL, GENERATOR, FNGENERATOR, ENVELOPE,
    CYCLES, NOISE, LIMITS, STEPPED, SMOOTH."""
    frames = 0
    for fc in action_fcurves(action):
        fc.modifiers.new('CYCLES')
        frames += 1
    return frames

print("looped:", make_loop(dst.animation_data.action, 1, 120))
```

Вместо модификатора можно продублировать полосу в NLA — но тогда появятся
швы на стыке, и их придётся править вручную.

### 8. Foot lock на кадрах контакта

```python
# Простой, честный foot lock без плагинов: на кадрах контакта (их вы
# определяете сами по детекции скорости стопы) ключи IK-контроллеров
# фиксируются, а между ними интерполируются.
import bpy

ik = bpy.data.objects["MY_RIG"].pose.bones["foot_fk.L"]
ik.lock_location = (True, True, True)     # блокируем цель на кадрах контакта
ik.lock_rotation = (True, True, True)
# Затем вручную проставить ключи на кадрах контакта — либо снять блокировку
# на кадрах переноса. Полностью автоматический foot lock требует плагина.
```

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `axis_forward` / `axis_up` | `'-Z'` / `'Y'` | Другой источник — подбирается по одному кадру, а не «на глаз» |
| `primary/secondary_bone_axis` | `'Y'` / `'X'` | Если кости цели лежат |
| `bake_anim_use_nla_strips` | `False` | Всегда: NLA-полосы мешают чистке |
| `bake_anim_force_startend_keying` | `True` | Нужны точные первый и последний кадры |
| `target_space` / `owner_space` | `'WORLD'` / `'WORLD'` | Иначе длина костей влияет на результат |
| `nla.bake(visual_keying=)` | `True` | IK/FK-риги: «как видит глаз» |
| `clear_constraints` | `True` | Сразу после запекания — констрейнты мешают правке кривых |

> [!NOTE]
> Набор имён костей в FBX, пресеты экспорта в Rokoko Studio и Move AI и
> формат их облачных выгрузок менялись. Таблицу `BONE_MAP` нужно печатать из
> реально импортированного арматура (шаг 2) и править по факту, а не по
> памяти. Метки на теле в облачном сервисе именуются по их собственному
> словарю.

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `enum "Y_FORWARD" not found` | Устаревшее имя оси в скрипте | В Blender 5.x передавать `'Y'`/`'-Z'` и т.п. |
| Ноги «плывут», рост скелета 180 ед. | FBX в сантиметрах, сцена в метрах | Масштаб исходному объекту `0.01` **до** ретаргета |
| `AttributeError: 'Action' object has no attribute 'fcurves'` | Blender 5.x: slotted Actions | Идти через `action.layers[0].strips[0].channelbags[0].fcurves` |
| Один кадр из 1000 «дёргается» | Одиночный ключ, до него кривая уходила в сторону | `AUTO_CLAMPED` на хэндлах всех ключей |
| Персонаж идёт боком / вверх ногами | Перепутаны `axis_forward` и `axis_up` | Проверить на первом кадре; смотреть на позу, а не на оси |
| `enum "LIMIT_LOCATION" not found` у модификатора кривой | В 5.2 этот тип называется `LIMITS` | Перебор: `NULL, GENERATOR, FNGENERATOR, ENVELOPE, CYCLES, NOISE, LIMITS, STEPPED, SMOOTH` |
| После запекания констрейнты остались | Не пересоздали риг / запекали не тот объект | Проверить `pose.bones[...].constraints` после `nla.bake` |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 57: FACE MOCAP ARKIT](setup_57_face_mocap_arkit.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P44: MOCAP RETARGETING](../prompts/44_mocap_retarget.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **Теги:** #mocap, #setup
