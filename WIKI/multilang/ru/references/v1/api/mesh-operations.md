---
lang: ru
orig_lang: en
translation: ai
---
# СПРАВОЧНИК ПО API ОПЕРАЦИЙ С МЕШАМИ BLENDER

## Создание примитивов

### bpy.ops (зависит от контекста)
```python
# Требуется корректный контекст (view_layer, активный объект)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0), rotation=(0,0,0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=2)
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, vertices=32, cap_ends=True)
bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, vertices=32)
bpy.ops.mesh.primitive_torus_add(
    major_radius=1, minor_radius=0.3,
    major_segments=48, minor_segments=12
)
bpy.ops.mesh.primitive_plane_add(size=2)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=2)
bpy.ops.mesh.primitive_monkey_add(size=1)  # Suzanne
```

### Низкоуровневый способ (без контекста) — ПРЕДПОЧТИТЕЛЬНО
```python
import bpy
import bmesh
from mathutils import Vector

def create_cube(name="Cube", size=2, location=(0,0,0)):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_uv_sphere(name="Sphere", radius=1, segments=32, ring_count=16):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, radius=radius, u_segments=segments, v_segments=ring_count)
    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_cylinder(name="Cylinder", radius=1, depth=2, vertices=32):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, radius1=radius, radius2=radius, depth=depth, segments=vertices)
    bm.to_mesh(mesh)
    bm.free()
    return obj
```

---

## Операции BMesh (эквивалент режима редактирования)

### Подготовка
```python
import bmesh

# BMesh в режиме объекта (создаёт новый меш)
bm = bmesh.new()
# ... операции ...
bm.to_mesh(mesh)
bm.free()

# BMesh в режиме редактирования (изменяет существующий)
bm = bmesh.from_edit_mesh(obj.data)
# ... операции ...
bmesh.update_edit_mesh(obj.data)
```

### Операции с вершинами
```python
# Создать вершины
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((0, 1, 0))

# Выделить / снять выделение
v1.select = True
bm.verts.ensure_lookup_table()

# Трансформация
v1.co = (2, 0, 0)
v1.co += Vector((0.1, 0, 0))

# Удаление
bm.verts.remove(v1)
```

### Операции с рёбрами
```python
# Создать ребро
e = bm.edges.new((v1, v2))

# Циклы рёбер
bmesh.ops.edge_loops(bm, edges=[e])

# Разделить рёбра
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2)

# Скруглить рёбра
bmesh.ops.bevel(bm, geom=bm.edges, offset=0.1, segments=3, profile=0.5)

# Растворить рёбра
bmesh.ops.dissolve_edges(bm, edges=[e])
```

### Операции с гранями
```python
# Создать грань
f = bm.faces.new((v1, v2, v3))  # Треугольник
f = bm.faces.new((v1, v2, v3, v4))  # Четырёхугольник

# Свойства грани
f.select = True
f.material_index = 0
f.normal  # mathutils.Vector

# Экструзия
result = bmesh.ops.extrude_face_region(bm, geom=[f])
extruded_geom = result['geom']
# Переместить экструдированные грани
for elem in extruded_geom:
    if isinstance(elem, bmesh.types.BMFace):
        bmesh.ops.translate(bm, verts=elem.verts, vec=(0, 0, 1))

# Inset
bmesh.ops.inset_region(bm, faces=[f], thickness=0.1, depth=0.1)

# Poke (веер из треугольников)
bmesh.ops.poke(bm, faces=[f])

# Триангуляция
bmesh.ops.triangulate(bm, faces=bm.faces)

# Разделить грани
bmesh.ops.subdivide_edges(bm, edges=[e for f in bm.faces for e in f.edges], cuts=1)
```

### Выделение и запросы
```python
# Выделить всё
for v in bm.verts: v.select = True
for e in bm.edges: e.select = True
for f in bm.faces: f.select = True

# Получить выделенное
selected_verts = [v for v in bm.verts if v.select]
selected_edges = [e for e in bm.edges if e.select]
selected_faces = [f for f in bm.faces if f.select]

# По индексу
v = bm.verts[0]
e = bm.edges[0]
f = bm.faces[0]

# Таблицы поиска (обязательны после изменения топологии)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
```

### Модификаторы меша (BMesh)
```python
# Remesh (воксельный)
bmesh.ops.remesh(bm, voxel_size=0.1, adaptivity=0.0)

# Сглаживание
bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, iterations=10)

# Decimate
# Напрямую в bmesh нет — используйте модификатор или bpy.ops

# Удалить оторванные элементы
bmesh.ops.delete_loose(bm, dist=0.001)
```

---

## Доступ к данным меша (bpy.data.meshes)

### Чтение данных меша
```python
mesh = obj.data

# Вершины
for v in mesh.vertices:
    v.co           # локальные координаты
    v.normal       # нормаль вершины
    v.groups       # группы вершин
    v.index        # индекс

# Рёбра
for e in mesh.edges:
    e.vertices     # (v1_idx, v2_idx)
    e.use_seam     # шов UV
    e.use_sharp    # острое ребро
    e.bevel_weight # вес Bevel

# Полигоны (грани)
for poly in mesh.polygons:
    poly.vertices        # индексы вершин
    poly.loop_indices    # индексы лупов
    poly.normal          # нормаль грани
    poly.center          # центр грани
    poly.area            # площадь грани
    poly.material_index  # индекс слота материала

# Лупы (данные на каждую пару «вершина-грань»)
for loop in mesh.loops:
    loop.vertex_index   # индекс вершины
    loop.normal         # нормаль лупа (для гладкого затенения)

# Слои UV
for uv_layer in mesh.uv_layers:
    for uv in uv_layer.data:
        uv.uv           # Vector (u, v)

# Цвета вершин
for vc_layer in mesh.vertex_colors:
    for vc in vc_layer.data:
        vc.color        # RGBA (0-1)

# Shape Keys
if mesh.shape_keys:
    for key in mesh.shape_keys.key_blocks:
        key.value = 0.5
```

---

## Модификаторы (через API)

### Добавление модификатора
```python
mod = obj.modifiers.new("Subdivision", 'SUBSURF')
mod.levels = 2
mod.render_levels = 3
mod.subdivision_type = 'CATMULL_CLARK'  # 'SIMPLE'

mod = obj.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.02
mod.segments = 3
mod.profile = 0.5
mod.limit_method = 'ANGLE'  # 'WEIGHT', 'VGROUP', 'NONE'
mod.angle_limit = 1.0472  # 60 градусов

mod = obj.modifiers.new("Array", 'ARRAY')
mod.count = 5
mod.use_relative_offset = True
mod.relative_offset_displace = (1.5, 0, 0)

mod = obj.modifiers.new("Mirror", 'MIRROR')
mod.use_axis = (True, False, False)
mod.use_bisect_axis = (True, False, False)

mod = obj.modifiers.new("Boolean", 'BOOLEAN')
mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
mod.object = other_obj
mod.solver = 'EXACT'  # 'FAST'

mod = obj.modifiers.new("Solidify", 'SOLIDIFY')
mod.thickness = 0.1
mod.offset = 0  # от -1 до 1
mod.use_even_offset = True

mod = obj.modifiers.new("Decimate", 'DECIMATE')
mod.ratio = 0.5  # 0.0-1.0
mod.decimate_type = 'COLLAPSE'  # 'UNSUBDIV', 'PLANNAR'

mod = obj.modifiers.new("Remesh", 'REMESH')
mod.mode = 'VOXEL'  # 'SMOOTH', 'SHARP'
mod.voxel_size = 0.1
mod.adaptivity = 0.0
```

### Применение модификатора
```python
# Один
bpy.ops.object.modifier_apply(modifier="Subdivision")

# Все
for mod in list(obj.modifiers):
    bpy.ops.object.modifier_apply(modifier=mod.name)

# Через Python (без контекста)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.modifier_apply(modifier=mod.name)
```

---

## Булевы операции

### Через модификатор (рекомендуется)
```python
def boolean_union(obj_a, obj_b):
    mod = obj_a.modifiers.new("Bool", 'BOOLEAN')
    mod.operation = 'UNION'
    mod.object = obj_b
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.object.modifier_apply(modifier="Bool")
    bpy.data.objects.remove(obj_b, do_unlink=True)
    return obj_a

def boolean_difference(obj_a, obj_b):
    mod = obj_a.modifiers.new("Bool", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = obj_b
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.object.modifier_apply(modifier="Bool")
    bpy.data.objects.remove(obj_b, do_unlink=True)
    return obj_a

def boolean_intersect(obj_a, obj_b):
    mod = obj_a.modifiers.new("Bool", 'BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.object = obj_b
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.object.modifier_apply(modifier="Bool")
    bpy.data.objects.remove(obj_b, do_unlink=True)
    return obj_a
```

---

## Развёртка UV

### Базовая развёртка
```python
# Smart UV Project (лучше для hard surface)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.0472, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# Lightmap Pack (для запекания)
bpy.ops.uv.lightmap_pack(PADDING=4, Px_MARGIN=4)

# Cube Projection
bpy.ops.uv.cube_project()

# Sphere Projection
bpy.ops.uv.sphere_project()
```

### Развёртка по швам
```python
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')

# Пометить швы
for e in bmesh.from_edit_mesh(obj.data).edges:
    if e.calc_face_angle() > 1.0472:  # 60 градусов
        e.use_seam = True

bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
bpy.ops.object.mode_set(mode='OBJECT')
```

### Манипуляция с UV
```python
# Масштабировать UV
uv_layer = mesh.uv_layers.active
for uv in uv_layer.data:
    uv.uv *= 2.0

# Сдвинуть UV
for uv in uv_layer.data:
    uv.uv += (0.5, 0.5)

# Повернуть UV
import math
angle = math.pi / 4
for uv in uv_layer.data:
    u, v = uv.uv
    uv.uv = (u * math.cos(angle) - v * math.sin(angle),
             u * math.sin(angle) + v * math.cos(angle))
```

---

## Группы вершин и веса

### Создание и назначение
```python
vg = obj.vertex_groups.new(name="GroupName")

# Назначить вершины с весом
vg.add([0, 1, 2, 3], 1.0, 'REPLACE')  # индексы вершин, вес, тип

# Получить вес
weight = vg.weight(vertex_index)

# Удалить
vg.remove([0, 1, 2])
```

### Операции с группами вершин
```python
# Нормализовать все группы для вершины
vg.normalize()

# Очистить (убрать нулевые веса)
vg.clean(0.001, 0.0, 0.0)

# Зеркалить (для симметричных ригов)
vg.mirror("GroupName.R", "GroupName.L", True)

# Копировать
new_vg = obj.vertex_groups.new(name="Copy")
for v in obj.data.vertices:
    try:
        w = vg.weight(v.index)
        new_vg.add([v.index], w, 'REPLACE')
    except RuntimeError:
        pass  # Вершина не входит в группу
```

---

## Нормали и затенение

### Автосглаживание
```python
obj.data.use_auto_smooth = True
obj.data.auto_smooth_angle = 1.0472  # 60 градусов
```

### Пользовательские нормали
```python
# Задать пользовательские нормали
mesh = obj.data
mesh.use_auto_smooth = True
normals = []
for poly in mesh.polygons:
    for loop_idx in poly.loop_indices:
        normals.append(poly.normal)
mesh.normals_split_custom_set(normals)
mesh.use_auto_smooth = True

# Или по вершинам
mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
```

### Острые рёбра
```python
# Пометить острыми
for e in mesh.edges:
    e.use_sharp = True  # Для автосглаживания

# Вес Bevel
for e in mesh.edges:
    e.bevel_weight = 1.0
```

---

## Цвета вершин

### Рисование через Python
```python
# Создать слой
vc_layer = mesh.vertex_colors.new(name="Paint")

# Красить по граням
for poly in mesh.polygons:
    for loop_idx in poly.loop_indices:
        loop = mesh.loops[loop_idx]
        vc_layer.data[loop_idx].color = (1.0, 0.0, 0.0, 1.0)  # Красный

# Градиент по высоте
for poly in mesh.polygons:
    for loop_idx in poly.loop_indices:
        v = mesh.vertices[mesh.loops[loop_idx].vertex_index]
        h = (v.co.z - min_z) / (max_z - min_z)
        vc_layer.data[loop_idx].color = (h, h, h, 1.0)
```

---

## Советы по производительности

### Пакетные операции
```python
# Использовать foreach для массового доступа к атрибутам
co_list = [0.0] * (len(mesh.vertices) * 3)
mesh.vertices.foreach_get("co", co_list)

# Изменить
for i in range(0, len(co_list), 3):
    co_list[i+2] += 0.1  # Поднять Z

# Записать обратно
mesh.vertices.foreach_set("co", co_list)
mesh.update()
```

### Эффективное выделение
```python
# Вместо цикла:
# for v in bm.verts: v.select = True

# Использовать:
bm.verts.ensure_lookup_table()
for v in bm.verts:
    v.select_set(True)  # или v.select = True
```

### Избегайте bpy.ops в циклах
```python
# ПЛОХО
for obj in objects:
    bpy.ops.object.modifier_apply(modifier="Subdivision")

# ХОРОШО — один override контекста
with bpy.context.temp_override(selected_objects=objects):
    bpy.ops.object.modifier_apply(modifier="Subdivision")
```

---

## Общие паттерны

### Создание меша по координатам
```python
def create_mesh_from_vertices(name, vertices, faces):
    """vertices: [(x,y,z), ...], faces: [(v1,v2,v3), ...]"""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# Использование
verts = [(0,0,0), (1,0,0), (0,1,0), (1,1,0)]
faces = [(0,1,3,2)]  # Четырёхугольник
obj = create_mesh_from_vertices("Quad", verts, faces)
```

### Дублирование и разделение
```python
# Дублировать объект + меш
new_obj = obj.copy()
new_obj.data = obj.data.copy()
bpy.context.collection.objects.link(new_obj)

# Отделить оторванные части (режим редактирования)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
```

### Преобразование в меш
```python
# Преобразовать кривую/текст/мета-объект в меш
bpy.context.view_layer.objects.active = obj
bpy.ops.object.convert(target='MESH')
```

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MATERIALS API REFERENCE](materials.md), [BLENDER PYTHON API REFERENCE (4.x)](blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](scripting-patterns.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md)
- **По темам:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [MCP SERVER API REFERENCE](../mcp/server-api.md)
- **Теги:** #api, #blender, #modeling, #reference
