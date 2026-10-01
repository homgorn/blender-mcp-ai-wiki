---
lang: en
tags: [animation, modeling, prompt, texturing]
---
# P19: NLA EDITOR WORKFLOW

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

- **Прочие в категории «Промпты»:** [P12: TEXTURE PAINTING](12_texture_painting.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md), [P43: CAMERA SWITCHING & MARKERS](43_camera_switching.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md)
- **По темам:** [P03: MODIFIERS STACK](03_modifiers_stack.md), [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md), [P05: UV UNWRAPPING STRATEGIES](05_uv_unwrapping.md)
- **Теги:** #actions, #animation, #blending, #layers, #modeling, #nla, #nonlinear, #prompt, #texturing

