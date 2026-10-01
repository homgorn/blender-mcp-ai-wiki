---
id: 16_keyframe_animation
lang: ru
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P16: KEYFRAME ANIMATION BASICS

> Цель: ---

**ID:** 16_keyframe_animation | **Lang:** ru | **Orig:** ru | **Category:** prompts | **Tags:** animation, dope, dope-sheet, graph, graph-editor, interpolation, keyframes

## Как пользоваться
Это русская версия '16_keyframe_animation'. Кодовые блоки языконезависимы. Выполняйте шаги по порядку, проверяйте разделом Проверка.

## MCP-промпт (копипаст)
```
16_keyframe_animation / prompts / animation, dope, dope-sheet, graph, graph-editor, interpolation, keyframes
```

> Замечание: код/пути оставлены на английском для совместимости Blender/Python.

---

# P16: KEYFRAME ANIMATION BASICS

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
