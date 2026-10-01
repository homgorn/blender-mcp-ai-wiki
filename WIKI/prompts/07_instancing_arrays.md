---
lang: en
tags: [geometry-nodes, modeling, prompt]
---
# P07: INSTANCING & ARRAYS

**ID:** P07 | **Cluster:** Geometry Basics | **Difficulty:** ⭐⭐ | **Tags:** #instances #array #collection #geometry-nodes #procedural

---

## 🎯 GOAL
Efficient duplication and distribution of objects using Array modifier, Collection instances, and Geometry Nodes

---

## 📝 PROMPT (RUS)

```
Создай массив/распределение "[OBJECT_NAME]":
Метод: ARRAY_MODIFIER / COLLECTION_INSTANCE / GEOMETRY_NODES
Параметры: count, offset, randomize, scale, rotation
```

---

## 📝 PROMPT (ENG)

```
Create array/distribution of "[OBJECT_NAME]":
Method: ARRAY_MODIFIER / COLLECTION_INSTANCE / GEOMETRY_NODES
Parameters: count, offset, randomize, scale, rotation
```

---

## 🔧 MCP: `execute_blender_code`

### ARRAY MODIFIER (Простой линейный)
```python
import bpy

obj = bpy.data.objects.get("Source_Obj")
if not obj:
    raise ValueError("Object not found")

# Array Modifier
array = obj.modifiers.new("Array_Linear", 'ARRAY')
array.count = 10
array.use_relative_offset = True
array.relative_offset_displace = (2.0, 0, 0)  # 2м между экземплярами

# Array по кривой
curve = bpy.data.curves.new("Path", 'CURVE')
curve.dimensions = '3D'
spline = curve.splines.new('BEZIER')
spline.bezier_points.add(3)
# ... настроить точки кривой

curve_obj = bpy.data.objects.new("Path", curve)
bpy.context.collection.objects.link(curve_obj)

array2 = obj.modifiers.new("Array_Curve", 'ARRAY')
array2.fit_type = 'FIT_CURVE'
array2.curve = curve_obj
array2.use_relative_offset = True
array2.relative_offset_displace = (0, 0, 1.0)
```

### COLLECTION INSTANCES (Лёгкие, для сцены)
```python
import bpy

# Создать коллекцию с вариациями
col = bpy.data.collections.new("Props_Variants")
for i in range(5):
    var = bpy.data.objects.get(f"Prop_Var_{i}")
    if var:
        col.objects.link(var)

# Инстанс коллекции
instance = bpy.data.objects.new("Instancer", None)
instance.instance_type = 'COLLECTION'
instance.instance_collection = col
bpy.context.collection.objects.link(instance)

# Настроить распределение (Geometry Nodes лучше)
```

### GEOMETRY NODES (Полный контроль)
```python
import bpy

# Создать GN дерево
gn = bpy.data.node_groups.new("Scatter_Props", 'GeometryNodeTree')
nodes = gn.nodes
links = gn.links
nodes.clear()

# Input/Output
inp = nodes.new('NodeGroupInput')
out = nodes.new('NodeGroupOutput')
gn.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
gn.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
gn.interface.new_socket(name="Source", in_out='INPUT', socket_type='NodeSocketObject')

inp.location = (-400, 0)
out.location = (400, 0)

# Nodes
distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
distribute.location = (0, 0)
distribute.distribute_method = 'POISSON'

instance = nodes.new('GeometryNodeInstanceOnPoints')
instance.location = (200, 0)
instance.inputs['Scale'].default_value = (1, 1, 1)

realize = nodes.new('GeometryNodeRealizeInstances')
realize.location = (400, 0)

# Links
links.new(inp.outputs['Source'], distribute.inputs['Mesh'])
links.new(inp.outputs['Count'], distribute.inputs['Density'])
links.new(distribute.outputs['Points'], instance.inputs['Points'])
links.new(inp.outputs['Source'], instance.inputs['Instance'])
links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
links.new(realize.outputs['Geometry'], out.inputs['Geometry'])

# Применить к объекту-эмиттеру
emitter = bpy.data.objects.get("Ground")
mod = emitter.modifiers.new("GN_Scatter", 'NODES')
mod.node_group = gn
mod["Input_1"] = 1000  # Count
mod["Input_2"] = bpy.data.objects.get("Prop_Source")  # Source
```

---

## 📊 СРАВНЕНИЕ МЕТОДОВ

| Метод | Память | Гибкость | Анимация | Сложность |
|-------|--------|----------|----------|-----------|
| **Array Modifier** | Низкая | Низкая | Да | ⭐ |
| **Collection Instance** | Очень низкая | Средняя | Ограничено | ⭐⭐ |
| **Geometry Nodes** | Низкая | Максимальная | Да | ⭐⭐⭐ |

---

## 💡 ПРО ТИПЫ

### Случайные вариации (GN)
```python
# Random Scale
rand_scale = nodes.new('GeometryNodeRandomValue')
rand_scale.data_type = 'FLOAT_VECTOR'
rand_scale.outputs[0].default_value = (0.8, 0.8, 0.8)
rand_scale.outputs[1].default_value = (1.2, 1.2, 1.2)
links.new(rand_scale.outputs['Value'], instance.inputs['Scale'])

# Random Rotation
rand_rot = nodes.new('GeometryNodeRandomValue')
rand_rot.data_type = 'FLOAT_VECTOR'
rand_rot.outputs[0].default_value = (0, 0, 0)
rand_rot.outputs[1].default_value = (0, 0, 6.28)
links.new(rand_rot.outputs['Value'], instance.inputs['Rotation'])
```

### Weight Paint для плотности
```python
# Vertex Group "Density" на эмиттере
distribute.inputs['Density Attribute'].default_value = "Density"
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P23: GEOMETRY NODES BASICS](23_geometry_nodes_basics.md), [P25: PROCEDURAL BUILDING GENERATOR](25_procedural_building.md), [P45: GEOMETRY NODES SIMULATION ZONES](45_gn_simulation.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P03: MODIFIERS STACK](03_modifiers_stack.md)
- **По темам:** [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md), [P22: PARTICLE SYSTEMS](22_particles.md)
- **Теги:** #array, #collection, #geometry, #geometry-nodes, #instances, #modeling, #procedural, #prompt

