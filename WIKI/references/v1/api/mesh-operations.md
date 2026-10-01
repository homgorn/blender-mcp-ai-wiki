# BLENDER MESH OPERATIONS API REFERENCE

## Primitive Creation

### bpy.ops (Context-dependent)
```python
# Requires proper context (view_layer, active object)
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

### Low-Level (No Context) - PREFERRED
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

## BMesh Operations (Edit Mode Equivalent)

### Setup
```python
import bmesh

# Object mode BMesh (creates new mesh)
bm = bmesh.new()
# ... operations ...
bm.to_mesh(mesh)
bm.free()

# Edit mode BMesh (modifies existing)
bm = bmesh.from_edit_mesh(obj.data)
# ... operations ...
bmesh.update_edit_mesh(obj.data)
```

### Vertex Operations
```python
# Create vertices
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((0, 1, 0))

# Select/deselect
v1.select = True
bm.verts.ensure_lookup_table()

# Transform
v1.co = (2, 0, 0)
v1.co += Vector((0.1, 0, 0))

# Delete
bm.verts.remove(v1)
```

### Edge Operations
```python
# Create edge
e = bm.edges.new((v1, v2))

# Edge loops
bmesh.ops.edge_loops(bm, edges=[e])

# Subdivide edges
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2)

# Bevel edges
bmesh.ops.bevel(bm, geom=bm.edges, offset=0.1, segments=3, profile=0.5)

# Dissolve edges
bmesh.ops.dissolve_edges(bm, edges=[e])
```

### Face Operations
```python
# Create face
f = bm.faces.new((v1, v2, v3))  # Triangle
f = bm.faces.new((v1, v2, v3, v4))  # Quad

# Face properties
f.select = True
f.material_index = 0
f.normal  # mathutils.Vector

# Extrude
result = bmesh.ops.extrude_face_region(bm, geom=[f])
extruded_geom = result['geom']
# Move extruded faces
for elem in extruded_geom:
    if isinstance(elem, bmesh.types.BMFace):
        bmesh.ops.translate(bm, verts=elem.verts, vec=(0, 0, 1))

# Inset
bmesh.ops.inset_region(bm, faces=[f], thickness=0.1, depth=0.1)

# Poke (triangle fan)
bmesh.ops.poke(bm, faces=[f])

# Triangulate
bmesh.ops.triangulate(bm, faces=bm.faces)

# Subdivide faces
bmesh.ops.subdivide_edges(bm, edges=[e for f in bm.faces for e in f.edges], cuts=1)
```

### Selection & Queries
```python
# Select all
for v in bm.verts: v.select = True
for e in bm.edges: e.select = True
for f in bm.faces: f.select = True

# Get selected
selected_verts = [v for v in bm.verts if v.select]
selected_edges = [e for e in bm.edges if e.select]
selected_faces = [f for f in bm.faces if f.select]

# By index
v = bm.verts[0]
e = bm.edges[0]
f = bm.faces[0]

# Lookup tables (required after topology changes)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
```

### Mesh Modifiers (BMesh)
```python
# Remesh (voxel)
bmesh.ops.remesh(bm, voxel_size=0.1, adaptivity=0.0)

# Smooth
bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, iterations=10)

# Decimate
# Not directly in bmesh - use modifier or bpy.ops

# Delete loose
bmesh.ops.delete_loose(bm, dist=0.001)
```

---

## Mesh Data Access (bpy.data.meshes)

### Read Mesh Data
```python
mesh = obj.data

# Vertices
for v in mesh.vertices:
    v.co           # local coordinates
    v.normal       # vertex normal
    v.groups       # vertex groups
    v.index        # index

# Edges
for e in mesh.edges:
    e.vertices     # (v1_idx, v2_idx)
    e.use_seam     # UV seam
    e.use_sharp    # Sharp edge
    e.bevel_weight # Bevel weight

# Polygons (faces)
for poly in mesh.polygons:
    poly.vertices        # vertex indices
    poly.loop_indices    # loop indices
    poly.normal          # face normal
    poly.center          # face center
    poly.area            # face area
    poly.material_index  # material slot index

# Loops (per-vertex-per-face data)
for loop in mesh.loops:
    loop.vertex_index   # vertex index
    loop.normal         # loop normal (for smooth shading)

# UV Layers
for uv_layer in mesh.uv_layers:
    for uv in uv_layer.data:
        uv.uv           # Vector (u, v)

# Vertex Colors
for vc_layer in mesh.vertex_colors:
    for vc in vc_layer.data:
        vc.color        # RGBA (0-1)

# Shape Keys
if mesh.shape_keys:
    for key in mesh.shape_keys.key_blocks:
        key.value = 0.5
```

---

## Modifiers (via API)

### Add Modifier
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
mod.angle_limit = 1.0472  # 60 degrees

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
mod.offset = 0  # -1 to 1
mod.use_even_offset = True

mod = obj.modifiers.new("Decimate", 'DECIMATE')
mod.ratio = 0.5  # 0.0-1.0
mod.decimate_type = 'COLLAPSE'  # 'UNSUBDIV', 'PLANNAR'

mod = obj.modifiers.new("Remesh", 'REMESH')
mod.mode = 'VOXEL'  # 'SMOOTH', 'SHARP'
mod.voxel_size = 0.1
mod.adaptivity = 0.0
```

### Apply Modifier
```python
# Single
bpy.ops.object.modifier_apply(modifier="Subdivision")

# All
for mod in list(obj.modifiers):
    bpy.ops.object.modifier_apply(modifier=mod.name)

# Via Python (no context)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.modifier_apply(modifier=mod.name)
```

---

## Boolean Operations

### Using Modifier (Recommended)
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

## UV Unwrapping

### Basic Unwrap
```python
# Smart UV Project (best for hard surface)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.0472, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# Lightmap Pack (for baking)
bpy.ops.uv.lightmap_pack(PADDING=4, Px_MARGIN=4)

# Cube Projection
bpy.ops.uv.cube_project()

# Sphere Projection
bpy.ops.uv.sphere_project()
```

### Seam-Based Unwrap
```python
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')

# Mark seams
for e in bmesh.from_edit_mesh(obj.data).edges:
    if e.calc_face_angle() > 1.0472:  # 60 degrees
        e.use_seam = True

bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
bpy.ops.object.mode_set(mode='OBJECT')
```

### UV Manipulation
```python
# Scale UVs
uv_layer = mesh.uv_layers.active
for uv in uv_layer.data:
    uv.uv *= 2.0

# Translate UVs
for uv in uv_layer.data:
    uv.uv += (0.5, 0.5)

# Rotate UVs
import math
angle = math.pi / 4
for uv in uv_layer.data:
    u, v = uv.uv
    uv.uv = (u * math.cos(angle) - v * math.sin(angle),
             u * math.sin(angle) + v * math.cos(angle))
```

---

## Vertex Groups / Weights

### Create & Assign
```python
vg = obj.vertex_groups.new(name="GroupName")

# Assign vertices with weight
vg.add([0, 1, 2, 3], 1.0, 'REPLACE')  # vertex indices, weight, type

# Get weight
weight = vg.weight(vertex_index)

# Remove
vg.remove([0, 1, 2])
```

### Vertex Group Operations
```python
# Normalize all groups for vertex
vg.normalize()

# Clean (remove zero weights)
vg.clean(0.001, 0.0, 0.0)

# Mirror (for symmetrical rigs)
vg.mirror("GroupName.R", "GroupName.L", True)

# Copy
new_vg = obj.vertex_groups.new(name="Copy")
for v in obj.data.vertices:
    try:
        w = vg.weight(v.index)
        new_vg.add([v.index], w, 'REPLACE')
    except RuntimeError:
        pass  # Vertex not in group
```

---

## Normals & Shading

### Auto Smooth
```python
obj.data.use_auto_smooth = True
obj.data.auto_smooth_angle = 1.0472  # 60 degrees
```

### Custom Normals
```python
# Set custom normals
mesh = obj.data
mesh.use_auto_smooth = True
normals = []
for poly in mesh.polygons:
    for loop_idx in poly.loop_indices:
        normals.append(poly.normal)
mesh.normals_split_custom_set(normals)
mesh.use_auto_smooth = True

# Or from faces
mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
```

### Sharp Edges
```python
# Mark sharp
for e in mesh.edges:
    e.use_sharp = True  # For auto smooth

# Bevel weight
for e in mesh.edges:
    e.bevel_weight = 1.0
```

---

## Vertex Colors

### Paint via Python
```python
# Create layer
vc_layer = mesh.vertex_colors.new(name="Paint")

# Paint by face
for poly in mesh.polygons:
    for loop_idx in poly.loop_indices:
        loop = mesh.loops[loop_idx]
        vc_layer.data[loop_idx].color = (1.0, 0.0, 0.0, 1.0)  # Red

# Gradient by height
for poly in mesh.polygons:
    for loop_idx in poly.loop_indices:
        v = mesh.vertices[mesh.loops[loop_idx].vertex_index]
        h = (v.co.z - min_z) / (max_z - min_z)
        vc_layer.data[loop_idx].color = (h, h, h, 1.0)
```

---

## Performance Tips

### Batch Operations
```python
# Use foreach for bulk attribute access
co_list = [0.0] * (len(mesh.vertices) * 3)
mesh.vertices.foreach_get("co", co_list)

# Modify
for i in range(0, len(co_list), 3):
    co_list[i+2] += 0.1  # Raise Z

# Set back
mesh.vertices.foreach_set("co", co_list)
mesh.update()
```

### Efficient Selection
```python
# Instead of loop:
# for v in bm.verts: v.select = True

# Use:
bm.verts.ensure_lookup_table()
for v in bm.verts:
    v.select_set(True)  # or v.select = True
```

### Avoid bpy.ops in Loops
```python
# BAD
for obj in objects:
    bpy.ops.object.modifier_apply(modifier="Subdivision")

# GOOD - Single context override
with bpy.context.temp_override(selected_objects=objects):
    bpy.ops.object.modifier_apply(modifier="Subdivision")
```

---

## Common Patterns

### Create Mesh from Coordinates
```python
def create_mesh_from_vertices(name, vertices, faces):
    """vertices: [(x,y,z), ...], faces: [(v1,v2,v3), ...]"""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# Usage
verts = [(0,0,0), (1,0,0), (0,1,0), (1,1,0)]
faces = [(0,1,3,2)]  # Quad
obj = create_mesh_from_vertices("Quad", verts, faces)
```

### Duplicate & Separate
```python
# Duplicate object + mesh
new_obj = obj.copy()
new_obj.data = obj.data.copy()
bpy.context.collection.objects.link(new_obj)

# Separate loose parts (Edit mode)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
```

### Convert to Mesh
```python
# Convert curve/text/meta to mesh
bpy.context.view_layer.objects.active = obj
bpy.ops.object.convert(target='MESH')
```