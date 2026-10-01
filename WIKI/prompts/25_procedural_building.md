---
lang: ru
tags: [geometry-nodes, modeling, prompt]
---
# P25: PROCEDURAL BUILDING GENERATOR

**ID:** P25 | **Кластер:** Geometry Nodes | **Сложность:** ⭐⭐⭐ | **Теги:** #procedural #architecture #building #array #facade

---

## 🎯 ЦЕЛЬ
Параметрическое здание: этажи, фасад с окнами, крыша, LOD

---

## 📝 ПРОМПТ (РУС)

```
Сгенерируй здание "[NAME]": W×D×H [w,d,h], этажей [N],
оконная сетка [cols×rows], стиль [modern/classical], крыша [flat/pitched]
```

---

## 📝 ПРОМПТ (ENG)

```
Generate building "[NAME]": W×D×H [w,d,h], floors [N],
window grid [cols×rows], style [modern/classical], roof [flat/pitched]
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def procedural_building(name, w=10, d=10, h=30, floors=10, win_cols=5, win_rows=8):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    import bmesh
    bm = bmesh.new()
    # Корпус
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w / 2
        v.co.y *= d / 2
        v.co.z *= h / 2
        v.co.z += h / 2  # base at z=0
    bm.to_mesh(mesh)
    bm.free()
    # Этажи через Array
    arr = obj.modifiers.new("Floors", 'ARRAY')
    arr.count = 1  # корпус уже полный; окна отдельно
    # Окна: отдельные плоскости через массив
    bpy.ops.mesh.primitive_plane_add(size=1)
    win = bpy.context.active_object
    win.name = f"{name}_Windows"
    win.scale = (1.2, 0.05, 1.5)
    ax = win.modifiers.new("WinX", 'ARRAY')
    ax.count = win_cols
    ax.relative_offset_displace = (2.0, 0, 0)
    az = win.modifiers.new("WinZ", 'ARRAY')
    az.count = win_rows
    az.relative_offset_displace = (0, 0, 2.2)
    return {"building": name, "windows": win.name}

# procedural_building("Tower_A", w=12, d=12, h=45, floors=12, win_cols=6, win_rows=10)
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P07: INSTANCING & ARRAYS](07_instancing_arrays.md), [P23: GEOMETRY NODES BASICS](23_geometry_nodes_basics.md), [P03: MODIFIERS STACK](03_modifiers_stack.md), [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md)
- **По темам:** [P22: PARTICLE SYSTEMS](22_particles.md), [P45: GEOMETRY NODES SIMULATION ZONES](45_gn_simulation.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md)
- **Теги:** #architecture, #array, #building, #geometry-nodes, #modeling, #procedural, #prompt

