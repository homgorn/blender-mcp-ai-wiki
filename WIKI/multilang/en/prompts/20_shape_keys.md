---
id: 20_shape_keys
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P20: SHAPE KEYS & MORPHING

> Goal: ---

**ID:** 20_shape_keys | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** blendshapes, corrective, facial, morph, shape, shape-keys

## How to use
This page is the en version of '20_shape_keys'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.

## MCP Prompt (copy-paste)
```
20_shape_keys / prompts / blendshapes, corrective, facial, morph, shape, shape-keys
```

> Note: code/paths stay in English for Blender/Python compatibility.

---

# P20: SHAPE KEYS & MORPHING

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
