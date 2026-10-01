---
id: 19_nla_workflow
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P19: NLA EDITOR WORKFLOW

> Ziel: ---

**ID:** 19_nla_workflow | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** actions, blending, layers, nla, nonlinear

## Verwendung
Dies ist die deutsche Version von '19_nla_workflow'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
19_nla_workflow / prompts / actions, blending, layers, nla, nonlinear
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

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
- **Кейсы:** [Case 04](../cases/case_04_character_rig.md), [Case 06](../cases/case_06_animation_loop.md)
- **Промпты:** [P18 Drivers](./18_drivers_constraints.md), [P20 Shape Keys](./20_shape_keys.md)
- **Следующий:** [P20: Shape Keys](./20_shape_keys.md)
