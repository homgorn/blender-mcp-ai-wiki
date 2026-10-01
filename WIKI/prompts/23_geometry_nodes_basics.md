---
lang: en
tags: [geometry-nodes, modeling, prompt]
---
# P23: GEOMETRY NODES BASICS

**ID:** P23 | **Кластер:** Geometry Nodes | **Сложность:** ⭐⭐ | **Теги:** #geometry-nodes #procedural #attributes #instances

---

## 🎯 ЦЕЛЬ
Базовый GN-сетап: Group Input/Output, distribute points, instance on points, realize

---

## 📝 ПРОМПТ (РУС)

```
Создай Geometry Nodes "[GROUP]" на "[OBJECT]":
Входы: [Count, Seed, Scale]
Логика: Distribute Points → Instance Collection → Random Transform
```

---

## 📝 ПРОМПТ (ENG)

```
Create Geometry Nodes "[GROUP]" on "[OBJECT]":
Inputs: [Count, Seed, Scale]
Logic: Distribute Points → Instance Collection → Random Transform
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def create_gn_scatter(obj_name, group_name="GN_Scatter", collection_name=None):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError("Object not found")
    ng = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    nodes, links = ng.nodes, ng.links
    nodes.clear()
    inp = nodes.new('NodeGroupInput')
    out = nodes.new('NodeGroupOutput')
    inp.location = (-400, 0); out.location = (400, 0)
    ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
    ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    dist = nodes.new('GeometryNodeDistributePointsOnFaces')
    dist.location = (-100, 0)
    dist.distribute_method = 'POISSON'
    inst = nodes.new('GeometryNodeInstanceOnPoints')
    inst.location = (100, 0)
    real = nodes.new('GeometryNodeRealizeInstances')
    real.location = (300, 0)
    links.new(inp.outputs[0], dist.inputs['Density'])
    links.new(dist.outputs['Points'], inst.inputs['Points'])
    links.new(inst.outputs['Instances'], real.inputs['Geometry'])
    links.new(real.outputs['Geometry'], out.inputs['Geometry'])
    mod = obj.modifiers.new("GN", 'NODES')
    mod.node_group = ng
    return {"group": group_name, "object": obj_name}

# create_gn_scatter("Ground", "GN_Trees")
```

---

## 📊 КЛЮЧЕВЫЕ НОДЫ
| Нода | Назначение |
|------|------------|
| Distribute Points on Faces | Точки по поверхности |
| Instance on Points | Инстансы коллекции |
| Realize Instances | Конвертация в геометрию |
| Random Value | Случайные scale/rotation |
| Store Named Attribute | Кастомные атрибуты |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P07: INSTANCING & ARRAYS](07_instancing_arrays.md), [P25: PROCEDURAL BUILDING GENERATOR](25_procedural_building.md), [P45: GEOMETRY NODES SIMULATION ZONES](45_gn_simulation.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P03: MODIFIERS STACK](03_modifiers_stack.md)
- **По темам:** [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md), [P22: PARTICLE SYSTEMS](22_particles.md)
- **Теги:** #attributes, #geometry, #geometry-nodes, #instances, #modeling, #procedural, #prompt

