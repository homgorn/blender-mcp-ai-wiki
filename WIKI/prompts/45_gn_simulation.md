---
lang: en
tags: [geometry-nodes, modeling, prompt]
---
# P45: GEOMETRY NODES SIMULATION ZONES

**ID:** P45 | **Кластер:** Geometry Nodes | **Сложность:** ⭐⭐⭐ | **Теги:** #geometry-nodes #simulation #particles #physics #blender-4

---

## 🎯 ЦЕЛЬ
Симуляции внутри GN 4.x: Simulation Zone, delta time, state attributes, bake

---

## 📝 ПРОМПТ (РУС)

```
Создай GN-симуляцию "[NAME]": state [position/velocity/age],
forces [gravity/wind/turbulence], collision [цель], bake [N] кадров.
```

---

## 📝 ПРОМПТ (ENG)

```
Create GN simulation "[NAME]": state [position/velocity/age],
forces [gravity/wind/turbulence], collision [target], bake [N] frames.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def gn_simulation_shell(obj_name, group_name="GN_Sim"):
    """Каркас GN-дерева с Simulation Zone (ноду Simulation Input/Output добавляет Blender при создании зоны вручную).
    Скрипт создаёт группу и базу; зону дособрать в редакторе."""
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError("Object not found")
    ng = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    nodes, links = ng.nodes, ng.links
    nodes.clear()
    inp = nodes.new('NodeGroupInput')
    out = nodes.new('NodeGroupOutput')
    inp.location = (-600, 0)
    out.location = (600, 0)
    ng.interface.new_socket(name="Delta Time", in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    # Подсказка структуры зоны (текст в frame):
    frame = nodes.new('NodeFrame')
    frame.label = "SIM ZONE: Sim Input → Forces → Integrate → Sim Output"
    mod = obj.modifiers.new("GN_Sim", 'NODES')
    mod.node_group = ng
    # Bake settings
    mod.show_viewport = True
    return {"group": group_name, "next": "добавь Simulation Zone в редакторе, bake через modifier"}

def bake_simulation(obj_name, frame_start=1, frame_end=120):
    s = bpy.context.scene
    s.frame_start = frame_start
    s.frame_end = frame_end
    # GN bake: через point cache simulation zone (Blender 4.x — кнопка Bake в модификаторе вручную)
    return {"bake_range": f"{frame_start}-{frame_end}", "note": "нажми Bake в GN-модификаторе"}
```

---

## 📊 STATE ATTRIBUTES
| Атрибут | Тип | Смысл |
|---------|-----|-------|
| position | Vector | Текущая позиция |
| velocity | Vector | Скорость (интегрируется) |
| age | Float | Возраст частицы |
| lifetime | Float | Время жизни (kill при age > lifetime) |
| id | Integer | Стабильный ID между кадрами |

---

## ⚠️ ОШИБКИ
| Ошибка | Решение |
|--------|---------|
| Взрыв частиц | Delta Time слишком большой; уменьши forces ×10 |
| Дрожание | Substeps: уменьши dt, увеличь damping |
| Потеря id | Не пересоздавай точки каждый кадр, храни state |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P07: INSTANCING & ARRAYS](07_instancing_arrays.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P23: GEOMETRY NODES BASICS](23_geometry_nodes_basics.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P21: PHYSICS SIMULATION](21_physics_simulation.md)
- **По темам:** [P25: PROCEDURAL BUILDING GENERATOR](25_procedural_building.md), [SIMULATION & PHYSICS: GEOMETRY NODES 4.0+](../simulation/rigid_body_gn.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md)
- **Теги:** #blender, #blender-4, #geometry, #geometry-nodes, #modeling, #particles, #physics, #prompt, #simulation

