---
id: 25_procedural_building
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P25: PROCEDURAL BUILDING GENERATOR

> Objetivo: ---

**ID:** 25_procedural_building | **Lang:** es | **Orig:** ru | **Category:** prompts | **Tags:** architecture, array, building, procedural

## Cómo usar
Esta es la versión en español de '25_procedural_building'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
25_procedural_building / prompts / architecture, array, building, procedural
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

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
- **Кейсы:** [Case 05](../cases/case_05_procedural_city.md)
- **Воркфлоу:** [WF 05](../workflows/wf_05_procedural_assets.md)
- **Следующий:** [P26: MCP Basics](./26_mcp_basics.md)
