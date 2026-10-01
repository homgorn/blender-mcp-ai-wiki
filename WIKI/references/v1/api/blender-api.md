---
lang: en
tags: [api, blender, reference]
---
# BLENDER PYTHON API REFERENCE (4.x)

## Quick Reference

### Context & Data Access
```python
import bpy

# Context (read-only in background)
bpy.context.scene              # Current scene
bpy.context.view_layer         # Current view layer
bpy.context.active_object      # Active object (can be None)
bpy.context.selected_objects   # List of selected objects
bpy.context.object             # Same as active_object
bpy.context.mode               # Current mode ('OBJECT', 'EDIT', etc.)

# Data (always accessible)
bpy.data.objects               # All objects
bpy.data.meshes                # All meshes
bpy.data.materials             # All materials
bpy.data.collections           # All collections
bpy.data.scenes                # All scenes
bpy.data.images                # All images
bpy.data.node_groups           # All node groups
```

### Object Creation
```python
# Primitives (bpy.ops - requires context)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0), rotation=(0,0,0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, vertices=32)
bpy.ops.mesh.primitive_plane_add(size=2)
bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.3)

# Low-level (no context needed) - PREFERRED
mesh = bpy.data.meshes.new("MyMesh")
obj = bpy.data.objects.new("MyObject", mesh)
bpy.context.collection.objects.link(obj)

# Create mesh data
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesh)
# ... bmesh operations ...
bmesh.update_edit_mesh(mesh)
bpy.ops.object.mode_set(mode='OBJECT')
```

### Transform Operations
```python
obj = bpy.data.objects["Cube"]

# Location / Rotation / Scale
obj.location = (1.0, 2.0, 3.0)
obj.rotation_euler = (0, 0, 1.5708)  # Radians
obj.scale = (2.0, 2.0, 2.0)

# Matrix (world transform)
obj.matrix_world = mathutils.Matrix.Translation((1,2,3)) @ \
                   mathutils.Matrix.Rotation(1.57, 4, 'Z')

# Apply transforms (Ctrl+A)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Origin
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
```

### Mesh Editing (bmesh)
```python
import bmesh

# Edit mode bmesh
bm = bmesh.from_edit_mesh(obj.data)

# Create geometry
v1 = bm.verts.new((0,0,0))
v2 = bm.verts.new((1,0,0))
v3 = bm.verts.new((0,1,0))
bm.faces.new((v1, v2, v3))

# Modifiers on bmesh
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2)
bmesh.ops.bevel(bm, geom=bm.edges, offset=0.1, segments=3)
bmesh.ops.extrude_face_region(bm, geom=[f for f in bm.faces])

# Update
bmesh.update_edit_mesh(obj.data)

# Object mode bmesh (new mesh)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bm.to_mesh(mesh)
bm.free()
```

### Materials & Nodes
```python
# Create material
mat = bpy.data.materials.new("MyMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default
nodes.clear()

# Principled BSDF (standard)
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.location = (0, 0)
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Set properties
principled.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # RGBA
principled.inputs['Roughness'].default_value = 0.5
principled.inputs['Metallic'].default_value = 0.0
principled.inputs['Transmission'].default_value = 0.0
principled.inputs['Emission Strength'].default_value = 0.0

# Texture nodes
tex_image = nodes.new('ShaderNodeTexImage')
tex_image.image = bpy.data.images.load("path/to/texture.png")
tex_coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])

# Assign to object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```

### Modifiers
```python
mod = obj.modifiers.new("Subdivision", 'SUBSURF')
mod.levels = 2
mod.render_levels = 3

mod = obj.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.02
mod.segments = 3
mod.profile = 0.5

mod = obj.modifiers.new("Array", 'ARRAY')
mod.count = 5
mod.use_relative_offset = True
mod.relative_offset_displace = (1.5, 0, 0)

mod = obj.modifiers.new("Boolean", 'BOOLEAN')
mod.operation = 'DIFFERENCE'  # UNION, INTERSECT
mod.object = other_obj
mod.solver = 'EXACT'  # 'FAST' for simple

# Apply modifier
bpy.ops.object.modifier_apply(modifier="Subdivision")
```

### Collections & Hierarchy
```python
# Create collection
col = bpy.data.collections.new("MyCollection")
bpy.context.scene.collection.children.link(col)

# Move object to collection
col.objects.link(obj)
bpy.context.scene.collection.objects.unlink(obj)

# Parenting
child.parent = parent
child.parent_type = 'OBJECT'  # 'BONE', 'VERTEX'

# Collections for organization
bpy.context.view_layer.active_layer_collection = \
    bpy.context.view_layer.layer_collection.children["MyCollection"]
```

### Animation
```python
# Keyframes
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location", frame=1)
obj.location = (10, 0, 0)
obj.keyframe_insert(data_path="location", frame=250)

# Interpolation
for fcurve in obj.animation_data.action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'  # 'LINEAR', 'CONSTANT'

# Drivers
driver = obj.driver_add("location", 0).driver
driver.type = 'SCRIPTED'
var = driver.variables.new()
var.name = "target_x"
var.targets[0].id = target_obj
var.targets[0].data_path = "location[0]"
driver.expression = "target_x * 2"

# NLA
track = obj.animation_data.nla_tracks.new()
strip = track.strips.new("ActionName", 1, obj.animation_data.action)
strip.scale = 2.0  # Time scale
```

### Geometry Nodes
```python
# Create node group
ng = bpy.data.node_groups.new("MyGeoNodes", 'GeometryNodeTree')
nodes = ng.nodes
links = ng.links

# Input/Output
input_node = nodes.new('NodeGroupInput')
output_node = nodes.new('NodeGroupOutput')

# Add sockets
ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Nodes
mesh_line = nodes.new('GeometryNodeMeshLine')
mesh_line.location = (-200, 0)
mesh_line.mode = 'POINTS'
links.new(input_node.outputs['Count'], mesh_line.inputs['Count'])

instance = nodes.new('GeometryNodeInstanceOnPoints')
instance.location = (200, 0)
links.new(mesh_line.outputs['Mesh'], instance.inputs['Points'])
links.new(input_node.outputs['Geometry'], instance.inputs['Instance'])

links.new(instance.outputs['Instances'], output_node.inputs['Geometry'])

# Apply to object
mod = obj.modifiers.new("GeoNodes", 'NODES')
mod.node_group = ng
```

### Rendering
```python
scene = bpy.context.scene

# Engine
scene.render.engine = 'CYCLES'  # 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'

# Cycles settings
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.cycles.device = 'GPU'  # 'CPU', 'GPU'

# EEVEE settings
scene.eevee.taa_render_samples = 64
scene.eevee.use_bloom = True
scene.eevee.use_ssr = True
scene.eevee.use_ssr_refraction = True

# Output
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.filepath = "//render_"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True

# Render
bpy.ops.render.render(write_still=True)
bpy.ops.render.render(animation=True)
```

### Import/Export
```python
# Import
bpy.ops.import_scene.gltf(filepath="model.glb")
bpy.ops.import_scene.fbx(filepath="model.fbx")
bpy.ops.import_mesh.stl(filepath="model.stl")
bpy.ops.wm.obj_import(filepath="model.obj")
bpy.ops.wm.ply_import(filepath="model.ply")

# Export
bpy.ops.export_scene.gltf(filepath="model.glb", export_format='GLB')
bpy.ops.export_scene.fbx(filepath="model.fbx")
bpy.ops.export_mesh.stl(filepath="model.stl")
bpy.ops.wm.obj_export(filepath="model.obj")
bpy.ops.wm.ply_export(filepath="model.ply")
```

### Utilities
```python
# Selection
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Mode switching
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='SCULPT')

# Delete
bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.meshes.remove(mesh, do_unlink=True)

# Duplicate
new_obj = obj.copy()
new_obj.data = obj.data.copy()  # Unique mesh
bpy.context.collection.objects.link(new_obj)

# Convert to mesh
bpy.ops.object.convert(target='MESH')

# Shade
bpy.ops.object.shade_smooth()
bpy.ops.object.shade_flat()
bpy.ops.object.shade_auto()

# Units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
```

### Performance Tips
```python
# Batch operations
with bpy.context.temp_override(selected_objects=objects):
    bpy.ops.object.shade_smooth()

# Disable updates during batch
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()

# Use foreach for bulk property setting
mesh.vertices.foreach_set("co", flat_coordinate_list)

# Profile
import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
# ... code ...
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20)
```

---

## Common Patterns for AI Automation

### Safe Object Access
```python
# ALWAYS check existence
obj = bpy.data.objects.get("Name")
if obj is None:
    raise ValueError("Object not found")

# ALWAYS use explicit references
obj = bpy.data.objects["Name"]  # Raises KeyError if missing
```

### Thread-Safe Execution (for MCP)
```python
# In blender-mcp addon: commands run on main thread via timer
# In GenesisCore: direct bpy access (same process)

# For background scripts:
def run_in_main_thread(func):
    def wrapper():
        return func()
    bpy.app.timers.register(wrapper, first_interval=0.01)
```

### Error Handling Template
```python
def safe_execute(code_func):
    try:
        result = code_func()
        return {"success": True, "result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Usage
result = safe_execute(lambda: create_complex_scene())
```

### Version Compatibility
```python
# Blender version check
if bpy.app.version >= (4, 0, 0):
    # New API
    bpy.ops.mesh.primitive_cube_add(size=2)
else:
    # Old API
    bpy.ops.mesh.primitive_cube_add(radius=1)

# Feature detection
has_asset_browser = hasattr(bpy.ops, 'asset')
```

---

## Reference Links
- [Blender Python API Docs](https://docs.blender.org/api/current/)
- [bpy.types Documentation](https://docs.blender.org/api/current/bpy.types.html)
- [bmesh Documentation](https://docs.blender.org/api/current/bmesh.html)
- [mathutils Documentation](https://docs.blender.org/api/current/mathutils.html)

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

