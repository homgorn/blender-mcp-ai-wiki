---
id: 04_mesh_editing_bmesh
lang: ru
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P04: MESH EDITING (BMESH)

> Цель: ## 🌍 MULTILANG

**ID:** 04_mesh_editing_bmesh | **Lang:** ru | **Orig:** ru | **Category:** prompts | **Tags:** **, bmesh, edit, edit-mode, low, low-level, mesh, mesh-manipulation, procedural

---

# P04: MESH EDITING (BMESH)

**ID:** P04 | **Кластер:** Geometry Basics | **Сложность:** ⭐⭐⭐ | **Теги:** #bmesh #edit-mode #mesh-manipulation #procedural #low-level

---

## 🎯 ЦЕЛЬ
Низкоуровневое редактирование меша через BMesh API для процедурной генерации

---

## 📝 ПРОМПТ (РУС)

```
Используй BMesh для создания/модификации меша "[OBJECT_NAME]":
- Режим: CREATE_NEW / EDIT_EXISTING
- Операции: [список операций с параметрами]
- Финализировать: UPDATE_MESH / TO_OBJECT
```

---

## 📝 ПРОМПТ (ENG)

```
Use BMesh to create/modify mesh "[OBJECT_NAME]":
- Mode: CREATE_NEW / EDIT_EXISTING
- Operations: [list of operations with params]
- Finalize: UPDATE_MESH / TO_OBJECT
```

---

## 🔧 MCP: `execute_blender_code`

### СОЗДАНИЕ НОВОГО МЕША
```python
import bpy
import bmesh
from mathutils import Vector

def create_custom_mesh(name, vertices, faces):
    """vertices: [(x,y,z), ...], faces: [(v1,v2,v3), ...]"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # Создать вершины
    bm_verts = [bm.verts.new(Vector(v)) for v in vertices]
    bm.verts.ensure_lookup_table()
    
    # Создать грани
    for face_indices in faces:
        try:
            bm.faces.new([bm_verts[i] for i in face_indices])
        except ValueError as e:
            print(f"Skipping invalid face {face_indices}: {e}")
    
    bm.to_mesh(mesh)
    bm.free()
    return obj

# Пример: Пирамида
pyramid_verts = [
    (0, 0, 2),      # apex
    (-1, -1, 0),    # base corners
    (1, -1, 0),
    (1, 1, 0),
    (-1, 1, 0),
]
pyramid_faces = [
    (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),  # sides
    (1, 2, 3, 4)  # base
]

obj = create_custom_mesh("Pyramid", pyramid_verts, pyramid_faces)
print(f"Created: {obj.name}")
```

---

### РЕДАКТИРОВАНИЕ СУЩЕСТВУЮЩЕГО (EDIT MODE)
```python
import bpy
import bmesh

obj = bpy.data.objects.get("Target_Mesh")
if not obj or obj.type != 'MESH':
    raise ValueError("Mesh object required")

# Перейти в EDIT mode для BMesh
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')

bm = bmesh.from_edit_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# === ОПЕРАЦИИ ===

# 1. SUBDIVIDE - подразделение рёбер
edges_to_subdivide = [e for e in bm.edges if e.calc_length() > 0.5]
bmesh.ops.subdivide_edges(bm, edges=edges_to_subdivide, cuts=2)

# 2. BEVEL - фаска на рёбрах
sharp_edges = [e for e in bm.edges if e.calc_face_angle() > 1.0]
bmesh.ops.bevel(bm, geom=sharp_edges, offset=0.05, segments=3, profile=0.5)

# 3. EXTRUDE - выдавливание граней
top_faces = [f for f in bm.faces if f.normal.z > 0.9]
extrude_result = bmesh.ops.extrude_face_region(bm, geom=top_faces)
extruded_geom = extrude_result['geom']
# Переместить выдавленное
new_faces = [g for g in extruded_geom if isinstance(g, bmesh.types.BMFace)]
bmesh.ops.translate(bm, verts=[v for f in new_faces for v in f.verts], vec=(0, 0, 1.0))

# 4. INSET - врезание
bmesh.ops.inset_region(bm, faces=list(bm.faces), thickness=0.1, depth=0.05)

# 5. POKE - триангуляция через центр
bmesh.ops.poke(bm, faces=list(bm.faces))

# 6. SMOOTH - сглаживание вершин
bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.3, iterations=5)

# Применить изменения
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

print(f"Edited: {obj.name}, verts={len(obj.data.vertices)}, faces={len(obj.data.polygons)}")
```

---

## 📊 BMesh ОПЕРАЦИЙ ЧЕТ-ЛИСТ

| Операция | Функция | Параметры | Use Case |
|----------|---------|-----------|----------|
| **Create Vert** | `bm.verts.new(Vector)` | coordinates | Базовая геометрия |
| **Create Edge** | `bm.edges.new((v1, v2))` | two verts | Каркас |
| **Create Face** | `bm.faces.new([v1,v2,v3...])` | vert list (3+) | Полигоны |
| **Subdivide** | `bmesh.ops.subdivide_edges` | edges, cuts | Детализация |
| **Bevel** | `bmesh.ops.bevel` | geom, offset, segments | Фаски |
| **Extrude** | `bmesh.ops.extrude_face_region` | geom (faces) | Выдавливание |
| **Inset** | `bmesh.ops.inset_region` | faces, thickness, depth | Врезки |
| **Poke** | `bmesh.ops.poke` | faces | Триангуляция |
| **Translate** | `bmesh.ops.translate` | verts, vec | Перемещение |
| **Scale** | `bmesh.ops.scale` | verts, vec | Масштаб |
| **Rotate** | `bmesh.ops.rotate` | verts, cent, matrix | Вращение |
| **Smooth** | `bmesh.ops.smooth_vert` | verts, factor, iter | Релаксация |
| **Remove Doubles** | `bmesh.ops.remove_doubles` | verts, dist | Очистка |
| **Triangulate** | `bmesh.ops.triangulate` | faces | Триангуляция |
| **Solidify** | `bmesh.ops.solidify` | faces, thickness | Толщина |

---

## 💡 ПРО ПАТТЕРНЫ

### Процедурный дом ( 바닥 + стены + крыша)
```python
def create_house_bmesh(width=6, depth=8, height=4, wall_thick=0.2):
    bm = bmesh.new()
    
    # Пол (плоскость)
    floor = bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1)
    # Масштабировать
    for v in floor['verts']:
        v.co.x *= width/2
        v.co.y *= depth/2
        v.co.z = 0
    
    # Стены - экструдировать вверх
    wall_faces = [f for f in bm.faces if f.normal.z < 0.1]  # не пол
    extrude = bmesh.ops.extrude_face_region(bm, geom=wall_faces)
    walls = [g for g in extrude['geom'] if isinstance(g, bmesh.types.BMFace)]
    bmesh.ops.translate(bm, verts=[v for f in walls for v in f.verts], vec=(0, 0, height))
    
    # Толщина стен (Solidify)
    bmesh.ops.solidify(bm, geom=walls, thickness=wall_thick)
    
    # Крыша - пирамида на верху
    # ... roof logic
    
    mesh = bpy.data.meshes.new("House")
    bm.to_mesh(mesh)
    bm.free()
    return mesh
```

### Модификация UV через BMesh
```python
bm = bmesh.from_edit_mesh(obj.data)
uv_layer = bm.loops.layers uv.verify()  # или .new("UVMap")

for face in bm.faces:
    for loop in face.loops:
        uv = loop[uv_layer]
        # Плановая проекция
        uv.uv = (loop.vert.co.x, loop.vert.co.y)

bmesh.update_edit_mesh(obj.data)
```

---

## ⚠️ ВАЖНЫЕ ПРАВИЛА

| Правило | Почему |
|---------|--------|
| `bm.verts.ensure_lookup_table()` после изменений | Индексы сбиваются |
| `bmesh.update_edit_mesh(obj.data)` перед выходом | Записать в меш |
| `bpy.ops.object.mode_set(mode='OBJECT')` после | Вернуться в объектный режим |
| `bm.free()` для новых BMesh | Утечка памяти |
| Проверяй `if isinstance(g, BMFace)` после extrude | Результат смешанный |

---

## 🔗 СВЯЗИ

- **Кейсы:** [Case 05: Procedural City](../cases/case_05_procedural_city.md)
- **Воркфлоу:** [WF 05: Procedural Assets](../workflows/wf_05_procedural_assets.md)
- **Промпты:** [P03 Modifiers](./03_modifiers_stack.md), [P05: UV Unwrapping](./05_uv_unwrapping.md)
- **Следующий:** [P05: UV Unwrapping Strategies](./05_uv_unwrapping.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/prompts/04_mesh_editing_bmesh.md` |
| Русский | `multilang/ru/prompts/04_mesh_editing_bmesh.md` |