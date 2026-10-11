#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate full prompts P16-P20 (animation cluster)."""
import os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
W = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent) / "prompts"

P16 = """# P16: KEYFRAME ANIMATION BASICS

**ID:** P16 | **Кластер:** Animation | **Сложность:** ⭐ | **Теги:** #animation #keyframes #interpolation #graph-editor #dope-sheet

---

## 🎯 ЦЕЛЬ
Базовая анимация через ключевые кадры: location/rotation/scale, интерполяция, Graph Editor

---

## 📝 ПРОМПТ (РУС)

```
Анимируй "[OBJECT_NAME]" свойство [PROP: location/rotation_euler/scale]:
Кадры: {frame: value, ...}
Интерполяция: BEZIER / LINEAR / CONSTANT
Пример: "Анимируй Cube location {1: (0,0,0), 50: (5,0,0), 100: (5,5,2)} BEZIER"
```

---

## 📝 ПРОМПТ (ENG)

```
Animate "[OBJECT_NAME]" property [PROP]:
Keyframes: {frame: value, ...}
Interpolation: BEZIER / LINEAR / CONSTANT
Example: "Animate Cube location {1: (0,0,0), 50: (5,0,0), 100: (5,5,2)} BEZIER"
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def animate_property(obj_name, prop_path, keyframes, interpolation='BEZIER'):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError(f"Object {obj_name} not found")
    for frame, value in sorted(keyframes.items()):
        setattr(obj, prop_path, value)
        obj.keyframe_insert(data_path=prop_path, frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            if fc.data_path == prop_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = interpolation
    return {"animated": obj_name, "prop": prop_path, "keys": len(keyframes)}

# Пример: куб летит по дуге
animate_property("Cube", "location", {1: (0,0,0), 50: (5,0,3), 100: (10,0,0)}, 'BEZIER')
```

---

## 📊 ИНТЕРПОЛЯЦИЯ

| Тип | Эффект | Когда |
|-----|--------|-------|
| BEZIER | Плавно, ease in/out | 90% случаев |
| LINEAR | Равномерно | Механика |
| CONSTANT | Резко, без перехода | Hold-позы, стоп-моушн |

---

## 💡 СОВЕТЫ
- Frame 1 = Frame N+1 для лупа (см. Case 06)
- Graph Editor → Key → Simplify для чистки
- `fcurve.extrapolation = 'CYCLIC'` для бесконечного повтора

---

## ⚠️ ОШИБКИ
| Ошибка | Решение |
|--------|---------|
| Ключи не вставляются | Проверь режим OBJECT, объект выбран |
| Рывки | Смени BEZIER→LINEAR или почисти handles (V → Automatic) |

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 06: Animation Loop](../cases/case_06_animation_loop.md)
- **Воркфлоу:** [WF 04: Character Animation](../workflows/wf_04_character_animation.md)
- **Следующий:** [P17: Rigify Setup](./17_rigify_setup.md)
"""

P17 = """# P17: RIGIFY HUMANOID SETUP

**ID:** P17 | **Кластер:** Animation | **Сложность:** ⭐⭐ | **Теги:** #rigify #rigging #armature #weights #humanoid

---

## 🎯 ЦЕЛЬ
Rigify-риг для humanoid-персонажа: meta-rig → generate → weights → тест поз

---

## 📝 ПРОМПТ (РУС)

```
Зариггай "[MESH_NAME]" через Rigify:
Meta-rig: Human, масштаб под меш
Generate → Parent (Automatic Weights) → Weight Paint чистка
Тест: T-pose, A-pose, присед
```

---

## 📝 ПРОМПТ (ENG)

```
Rig "[MESH_NAME]" with Rigify:
Meta-rig: Human scaled to mesh
Generate → Parent (Automatic Weights) → Weight cleanup
Test: T-pose, A-pose, squat
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def rigify_setup(mesh_name):
    mesh = bpy.data.objects.get(mesh_name)
    if not mesh or mesh.type != 'MESH':
        raise ValueError("Mesh required")
    # Meta-rig
    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.active_object
    meta.name = "MetaRig"
    # Масштабировать под меш (вручную в UI или кодом)
    # Generate
    bpy.context.view_layer.objects.active = meta
    bpy.ops.object.armature_human_tweak_add()  # опционально
    bpy.ops.pose.rigify_generate()
    rig = bpy.data.objects.get("rig")
    # Parent
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True); rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    return {"rig": rig.name, "mesh": mesh.name}

# rigify_setup("Character_Body")
```

---

## 📊 ЧЕК-ЛИСТ РИГА
- [ ] Meta-rig кости внутри меша
- [ ] Generate без ошибок
- [ ] Веса: голова=skull, плечи=градиент, пальцы=по фалангам
- [ ] Экстремальные позы без разрывов

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 04: Character Rig](../cases/case_04_character_rig.md)
- **Промпты:** [P16 Keyframes](./16_keyframe_animation.md), [P18 Drivers](./18_drivers_constraints.md)
- **Следующий:** [P18: Drivers & Constraints](./18_drivers_constraints.md)
"""

P18 = """# P18: DRIVERS & CONSTRAINTS

**ID:** P18 | **Кластер:** Animation | **Сложность:** ⭐⭐ | **Теги:** #drivers #constraints #procedural #rig #automation

---

## 🎯 ЦЕЛЬ
Процедурные связи: drivers (выражения) + constraints (Track To, Copy, Limit)

---

## 📝 ПРОМПТ (РУС)

```
Добавь драйвер: "[OBJ].[PROP]" ← "[TARGET].[PROP]" выражение "[EXPR]"
Или constraint: [TYPE] на "[OBJ]" с целью "[TARGET]"
Пример: "Гир B rotation.z = -gear_a_rot * 2"
```

---

## 📝 ПРОМПТ (ENG)

```
Add driver: "[OBJ].[PROP]" ← "[TARGET].[PROP]" expression "[EXPR]"
Or constraint: [TYPE] on "[OBJ]" targeting "[TARGET]"
Example: "Gear B rotation.z = -gear_a_rot * 2"
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def add_driver(obj_name, prop_path, target_name, target_prop, expr="var"):
    obj = bpy.data.objects.get(obj_name)
    tgt = bpy.data.objects.get(target_name)
    if not obj or not tgt:
        raise ValueError("Objects not found")
    drv = obj.driver_add(prop_path).driver
    drv.type = 'SCRIPTED'
    var = drv.variables.new()
    var.name = "var"
    var.targets[0].id = tgt
    var.targets[0].data_path = target_prop
    drv.expression = expr
    return {"driver": f"{obj_name}.{prop_path} = {expr}"}

def add_track_to(obj_name, target_name):
    obj = bpy.data.objects.get(obj_name)
    tgt = bpy.data.objects.get(target_name)
    c = obj.constraints.new('TRACK_TO')
    c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    return {"constraint": "TRACK_TO"}

# Примеры:
# add_driver("Gear_B", "rotation_euler[2]", "Gear_A", "rotation_euler[2]", "-var * 2")
# add_track_to("Camera", "Empty_Target")
```

---

## 📊 CONSTRAINTS ШПАРГАЛКА
| Тип | Назначение |
|-----|------------|
| TRACK_TO | Камера смотрит на цель |
| COPY LOCATION/ROTATION/SCALE | Повторение трансформа |
| LIMIT LOCATION/ROTATION | Ограничители (двери, суставы) |
| FOLLOW PATH | Движение по кривой |
| CHILD OF | Временное родительство (оружие в руке) |

---

## 🔗 СВЯЗИ
- **Промпты:** [P17 Rigify](./17_rigify_setup.md), [P19 NLA](./19_nla_workflow.md)
- **Следующий:** [P19: NLA Workflow](./19_nla_workflow.md)
"""

P19 = """# P19: NLA EDITOR WORKFLOW

**ID:** P19 | **Кластер:** Animation | **Сложность:** ⭐⭐ | **Теги:** #nla #actions #layers #blending #nonlinear

---

## 🎯 ЦЕЛЬ
Нелинейная анимация: actions → strips → слои (Replace/Add) → блендинг

---

## 📝 ПРОМПТ (РУС)

```
Собери NLA для "[RIG]":
Track 0: [ACTION_BASE] (Replace, Cyclic)
Track 1: [ACTION_ADD] (Add, Influence 0.5)
Переходы: Crossfade [N] кадров
```

---

## 📝 ПРОМПТ (ENG)

```
Build NLA for "[RIG]":
Track 0: [ACTION_BASE] (Replace, Cyclic)
Track 1: [ACTION_ADD] (Add, Influence 0.5)
Transitions: Crossfade [N] frames
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def push_to_nla(obj_name, action_name, track_name="Track", blend='REPLACE', repeat=True):
    obj = bpy.data.objects.get(obj_name)
    if not obj or not obj.animation_data:
        raise ValueError("No animation data")
    ad = obj.animation_data
    if not ad.nla_tracks:
        track = ad.nla_tracks.new()
        track.name = track_name
    else:
        track = ad.nla_tracks[0]
    action = bpy.data.actions.get(action_name)
    strip = track.strips.new(action.name, 1, action)
    strip.blend_type = blend  # REPLACE / ADD / COMBINE / MULTIPLY
    strip.extrapolation = 'HOLD' if not repeat else 'NOTHING'
    strip.use_auto_blend = True
    strip.blend_in = 5
    strip.blend_out = 5
    return {"strip": strip.name, "track": track.name}

# push_to_nla("Rig", "Walk", "Base", 'REPLACE')
# push_to_nla("Rig", "ArmSwing", "Additive", 'ADD')
```

---

## 📊 BLEND MODES
| Mode | Эффект |
|------|--------|
| REPLACE | Заменяет нижние слои |
| ADD | Добавляет (аддитивные слои: дыхание, жесты) |
| COMBINE | Комбинирует по каналам |
| MULTIPLY | Умножает (редко) |

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 04](../cases/case_04_character_rig.md), [Case 06](../cases/case_06_animation_loop.md)
- **Промпты:** [P18 Drivers](./18_drivers_constraints.md), [P20 Shape Keys](./20_shape_keys.md)
- **Следующий:** [P20: Shape Keys](./20_shape_keys.md)
"""

P20 = """# P20: SHAPE KEYS & MORPHING

**ID:** P20 | **Кластер:** Animation | **Сложность:** ⭐⭐ | **Теги:** #shape-keys #morph #facial #corrective #blendshapes

---

## 🎯 ЦЕЛЬ
Shape keys для лица/коррективов: basis → keys → drivers → экспорт

---

## 📝 ПРОМПТ (РУС)

```
Создай shape keys для "[MESH]": [список: smile, blink_L, jaw_open...]
Basis = нейтральное лицо. Значения 0..1. Драйверы от костей при нужде.
```

---

## 📝 ПРОМПТ (ENG)

```
Create shape keys for "[MESH]": [list: smile, blink_L, jaw_open...]
Basis = neutral. Range 0..1. Drive from bones if needed.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def add_shape_key(obj_name, key_name, from_mix=False):
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != 'MESH':
        raise ValueError("Mesh required")
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    key = obj.shape_key_add(name=key_name, from_mix=from_mix)
    key.slider_min = 0.0
    key.slider_max = 1.0
    key.value = 0.0
    return {"key": key.name}

def drive_shape_from_bone(obj_name, key_name, rig_name, bone_name, axis='LOC_Z', scale=0.1):
    obj = bpy.data.objects.get(obj_name)
    key = obj.data.shape_keys.key_blocks.get(key_name)
    drv = key.driver_add("value").driver
    drv.type = 'SCRIPTED'
    var = drv.variables.new()
    var.name = "v"
    var.type = 'TRANSFORMS'
    var.targets[0].id = bpy.data.objects.get(rig_name)
    var.targets[0].bone_target = bone_name
    var.targets[0].transform_type = axis
    var.targets[0].transform_space = 'LOCAL_SPACE'
    drv.expression = f"v * {scale}"
    return {"driven": key_name}

# add_shape_key("Head", "smile")
# add_shape_key("Head", "blink_L")
# drive_shape_from_bone("Head", "jaw_open", "Rig", "jaw", 'LOC_Z', 0.05)
```

---

## 📊 ЛИЦЕВЫЕ НАБОРЫ
| Набор | Ключи |
|-------|-------|
| Базовый (6) | smile, frown, blink_L/R, jaw_open, brow_up |
| FACS-мини (15) | + lip_pucker, cheek_raise, nose_wrinkle, eye_squint... |
| ARKit (52) | Полный набор для мокапа |

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 04](../cases/case_04_character_rig.md)
- **Промпты:** [P19 NLA](./19_nla_workflow.md)
- **Следующий:** P21 (Physics, чанк B)
"""

for name, content in [
    ("16_keyframe_animation.md", P16),
    ("17_rigify_setup.md", P17),
    ("18_drivers_constraints.md", P18),
    ("19_nla_workflow.md", P19),
    ("20_shape_keys.md", P20),
]:
    (W/name).write_text(content, encoding="utf-8")
print("OK P16-P20")
