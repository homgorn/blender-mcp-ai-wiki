---
lang: ru
---
# P18: DRIVERS & CONSTRAINTS

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
