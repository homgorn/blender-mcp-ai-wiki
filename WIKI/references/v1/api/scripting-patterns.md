---
lang: en
tags: [blender, reference]
---
# BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE

## Core Principles

### 1. Always Check Existence
```python
# BAD
obj = bpy.data.objects["Cube"]
obj.location.x = 1

# GOOD
obj = bpy.data.objects.get("Cube")
if obj:
    obj.location.x = 1
else:
    print("Object not found")
```

### 2. Explicit Context Over Implicit
```python
# BAD (relies on bpy.context.active_object)
bpy.ops.object.shade_smooth()

# GOOD (explicit)
obj = bpy.data.objects["Cube"]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()
```

### 3. Mode Awareness
```python
# Ensure correct mode before operations
def ensure_mode(mode='OBJECT'):
    if bpy.context.mode != mode:
        bpy.ops.object.mode_set(mode=mode)

# Usage
ensure_mode('OBJECT')
# ... object operations ...

ensure_mode('EDIT')
bm = bmesh.from_edit_mesh(obj.data)
# ... bmesh operations ...
bmesh.update_edit_mesh(obj.data)

ensure_mode('OBJECT')
```

---

## Safe Execution Template

### For MCP `execute_blender_code`
```python
def safe_execute(operation_name, func):
    """
    Wrapper for safe code execution in MCP.
    Returns dict with success/error info.
    """
    try:
        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        result = func()
        
        # Force update
        bpy.context.view_layer.update()
        
        return {
            "success": True,
            "result": result,
            "operation": operation_name
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "operation": operation_name,
            "traceback": traceback.format_exc()
        }

# Usage
def create_scene():
    # ... your code ...
    return {"created": ["Cube", "Light", "Camera"]}

result = safe_execute("create_scene", create_scene)
```

---

## Common Patterns

### Pattern 1: Create Object with Material
```python
def create_object_with_material(name, primitive_type, location, material_name, color):
    """Create primitive, add material, assign"""
    # Create mesh
    if primitive_type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(location=location)
    elif primitive_type == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    # ... other types
    
    obj = bpy.context.active_object
    obj.name = name
    
    # Create material
    mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    principled.inputs['Base Color'].default_value = color + (1.0,) if len(color) == 3 else color
    principled.inputs['Roughness'].default_value = 0.5
    principled.inputs['Metallic'].default_value = 0.0
    
    # Assign
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return obj
```

### Pattern 2: Batch Create with Variations
```python
def create_variations(base_name, count, position_func, variation_func):
    """Create multiple objects with variations"""
    objects = []
    for i in range(count):
        loc = position_func(i)
        obj = create_object_with_material(
            f"{base_name}_{i:03d}",
            'CUBE',
            loc,
            f"Mat_{base_name}_{i:03d}",
            variation_func(i)
        )
        objects.append(obj)
    return objects

# Usage
def grid_position(i, cols=5):
    row = i // cols
    col = i % cols
    return (col * 3, row * 3, 0)

def color_variation(i):
    import colorsys
    hue = (i * 0.618) % 1.0  # Golden ratio distribution
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
    return (r, g, b)

objs = create_variations("Brick", 20, grid_position, color_variation)
```

### Pattern 3: Hierarchical Scene Setup
```python
def setup_scene_hierarchy():
    """Create organized collection hierarchy"""
    # Root collection
    root = bpy.data.collections.new("Scene_Root")
    bpy.context.scene.collection.children.link(root)
    
    # Sub-collections
    collections = {}
    for name in ["Geometry", "Lights", "Cameras", "FX", "References"]:
        col = bpy.data.collections.new(name)
        root.children.link(col)
        collections[name] = col
    
    return collections

def move_to_collection(obj, collection_name, collections):
    """Move object to named collection"""
    # Unlink from all
    for col in obj.users_collection:
        col.objects.unlink(obj)
    # Link to target
    collections[collection_name].objects.link(obj)
```

### Pattern 4: Animation Keyframing
```python
def animate_property(obj, prop_path, keyframes, interpolation='BEZIER'):
    """
    keyframes: {frame: value, ...}
    prop_path: e.g., "location", "rotation_euler", "scale"
    """
    for frame, value in keyframes.items():
        setattr(obj, prop_path, value)
        obj.keyframe_insert(data_path=prop_path, frame=frame)
    
    # Set interpolation
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve.data_path == prop_path:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = interpolation

# Usage
animate_property(obj, "location", {
    1: (0, 0, 0),
    50: (10, 0, 0),
    100: (10, 10, 0),
    150: (0, 10, 0),
    200: (0, 0, 0)
})
```

### Pattern 5: Driver Setup
```python
def add_driver(obj, prop_path, target_obj, target_prop, expression="var"):
    """Add driver to obj.prop_path driven by target_obj.target_prop"""
    driver = obj.driver_add(prop_path).driver
    driver.type = 'SCRIPTED'
    
    var = driver.variables.new()
    var.name = "var"
    var.targets[0].id = target_obj
    var.targets[0].data_path = target_prop
    
    driver.expression = expression
    return driver

# Usage
# Rotate gear_b based on gear_a rotation (2:1 ratio)
add_driver(gear_b, "rotation_euler[2]", gear_a, "rotation_euler[2]", "-var * 2")
```

---

## Error Handling Patterns

### Context Manager for Mode Changes
```python
from contextlib import contextmanager

@contextmanager
def temp_mode(mode='OBJECT'):
    """Temporarily switch mode, restore after"""
    original_mode = bpy.context.mode
    if original_mode != mode:
        bpy.ops.object.mode_set(mode=mode)
    try:
        yield
    finally:
        if original_mode != mode:
            bpy.ops.object.mode_set(mode=original_mode)

# Usage
with temp_mode('EDIT'):
    bm = bmesh.from_edit_mesh(obj.data)
    # ... operations ...
    bmesh.update_edit_mesh(obj.data)
# Automatically back to original mode
```

### Context Manager for Selection
```python
@contextmanager
def temp_selection(objects, active=None):
    """Temporarily select objects, restore selection after"""
    # Save current
    prev_active = bpy.context.view_layer.objects.active
    prev_selected = bpy.context.selected_objects[:]
    
    # Set new
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    if active:
        bpy.context.view_layer.objects.active = active
    elif objects:
        bpy.context.view_layer.objects.active = objects[0]
    
    try:
        yield
    finally:
        # Restore
        bpy.ops.object.select_all(action='DESELECT')
        for obj in prev_selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = prev_active

# Usage
with temp_selection([obj1, obj2, obj3], active=obj1):
    bpy.ops.object.join()
```

### Undo Group
```python
def with_undo_step(name, func):
    """Wrap operation in undo step"""
    bpy.ops.ed.undo_push(message=name)
    try:
        return func()
    except Exception:
        bpy.ops.ed.undo()
        raise

# Usage
with_undo_step("Create Building", lambda: create_building())
```

---

## Performance Patterns

### Batch Processing
```python
def process_objects_batch(objects, process_func, batch_size=100):
    """Process objects in batches to avoid memory issues"""
    results = []
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i+batch_size]
        with bpy.context.temp_override(selected_objects=batch):
            batch_results = [process_func(obj) for obj in batch]
            results.extend(batch_results)
        # Optional: force garbage collection
        import gc
        gc.collect()
    return results
```

### Defer Expensive Operations
```python
def defer_to_next_frame(func):
    """Run function on next frame (useful for UI updates)"""
    def wrapper():
        func()
        return None  # Don't repeat
    bpy.app.timers.register(wrapper, first_interval=0.01)

# Usage
defer_to_next_frame(lambda: heavy_computation())
```

---

## Debugging Helpers

### Print Scene Summary
```python
def print_scene_summary():
    scene = bpy.context.scene
    print(f"Scene: {scene.name}")
    print(f"Objects: {len(scene.objects)}")
    print(f"Materials: {len(bpy.data.materials)}")
    print(f"Meshes: {len(bpy.data.meshes)}")
    print(f"Collections: {len(bpy.data.collections)}")
    for obj in scene.objects:
        print(f"  {obj.name} ({obj.type}) - {len(obj.data.vertices) if obj.type=='MESH' else 'N/A'} verts")

# Quick call
print_scene_summary()
```

### Find Issues
```python
def find_mesh_issues():
    """Check for common mesh problems"""
    issues = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        
        # Non-manifold edges
        bm = bmesh.new()
        bm.from_mesh(mesh)
        non_manifold = [e for e in bm.edges if not e.is_manifold]
        if non_manifold:
            issues.append(f"{obj.name}: {len(non_manifold)} non-manifold edges")
        
        # Zero-area faces
        zero_area = [f for f in bm.faces if f.calc_area() < 0.0001]
        if zero_area:
            issues.append(f"{obj.name}: {len(zero_area)} zero-area faces")
        
        # Duplicate vertices
        coords = [v.co for v in bm.verts]
        if len(coords) != len(set(str(c) for c in coords)):
            issues.append(f"{obj.name}: duplicate vertices")
        
        bm.free()
    
    return issues

# Run
for issue in find_mesh_issues():
    print(f"ISSUE: {issue}")
```

---

## Safe Mode Compliance (for blender-mcp)

### Allowed Imports Only
```python
# ✅ ALLOWED
import bpy
import bmesh
import math
import mathutils
import random
import json
import uuid
import itertools
import collections
import functools
import fractions
import decimal
import statistics
import typing
import dataclasses
import enum
import hashlib
import base64
import datetime
import time
import re
import string
import textwrap
import copy
import pprint
import numbers
import fractions
import pathlib
import os.path
import sys

# ❌ BLOCKED (safe mode)
import os          # file I/O
import subprocess  # process execution
import sys         # system access
import socket      # network
import requests    # HTTP
import urllib      # URL handling
import threading   # threading
import multiprocessing
import asyncio
import importlib   # dynamic imports
import pkgutil
import inspect
```

### Safe Code Template
```python
# This template passes safe mode validation
import bpy
import bmesh
import math
import mathutils
import random
import json

def main():
    # Your Blender operations here
    # Only use: bpy.data, bpy.ops, bmesh, mathutils, math, random, json
    
    # Example: Create procedural building
    for i in range(5):
        bpy.ops.mesh.primitive_cube_add(
            location=(i * 3, 0, 0),
            scale=(1, 1, random.uniform(2, 5))
        )
        obj = bpy.context.active_object
        obj.name = f"Building_{i}"
    
    return {"created": 5}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
```

---

## Version Compatibility

### Version Checks
```python
# Blender version
if bpy.app.version >= (4, 0, 0):
    # New API
    bpy.ops.mesh.primitive_cube_add(size=2)
else:
    # Old API
    bpy.ops.mesh.primitive_cube_add(radius=1)

# Feature detection
has_asset_browser = hasattr(bpy.ops, 'asset')
has_geometry_nodes = 'GeometryNodeTree' in dir(bpy.types)

# Property existence
if hasattr(bpy.types.Object, "new_property"):
    obj.new_property = value
```

---

## Testing Patterns

### Unit Test Template
```python
import unittest
import bpy
import bmesh

class TestMeshOperations(unittest.TestCase):
    def setUp(self):
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
    
    def test_create_cube(self):
        obj = create_object_with_material("TestCube", 'CUBE', (0,0,0), "TestMat", (1,0,0))
        self.assertEqual(obj.name, "TestCube")
        self.assertEqual(obj.type, 'MESH')
        self.assertEqual(len(obj.data.materials), 1)
    
    def test_boolean_difference(self):
        cube = create_object_with_material("Cube", 'CUBE', (0,0,0), "Mat", (1,0,0))
        sphere = create_object_with_material("Sphere", 'SPHERE', (0.5,0,0), "Mat", (0,1,0))
        
        result = boolean_difference(cube, sphere)
        self.assertEqual(result.name, "Cube")
        # Sphere should be deleted
        self.assertNotIn("Sphere", bpy.data.objects)

if __name__ == '__main__':
    unittest.main()
```

---

## MCP Integration Best Practices

### Step-by-Step for Complex Tasks
```python
# Instead of one massive operation, break into steps:

# Step 1: Setup
result = execute("Create collections for organization")

# Step 2: Base geometry
result = execute("Create floor plane 20x20m at origin")

# Step 3: Walls
result = execute("Create 4 walls around floor perimeter, 3m high")

# Step 4: Openings
result = execute("Boolean subtract door opening 1x2m in front wall")

# Step 5: Roof
result = execute("Create gabled roof over walls")

# Step 6: Materials
result = execute("Apply stone material to walls, wood to floor, tile to roof")

# Step 7: Lighting
result = execute("Add 3-point lighting: key, fill, rim")

# Step 8: Camera
result = execute("Add camera at (-10, -15, 5) looking at center, 35mm")

# Step 9: Render settings
result = execute("Set Cycles, 128 samples, 1920x1080, output to //renders/")
```

### Validation After Each Step
```python
def verify_step(step_name, verification_func):
    """Execute step and verify result"""
    result = execute(step_name)
    if not result.get("success"):
        return {"success": False, "error": f"{step_name} failed: {result.get('error')}"}
    
    # Verify
    try:
        verification_func()
        return {"success": True, "result": result}
    except AssertionError as e:
        return {"success": False, "error": f"{step_name} verification failed: {e}"}

# Usage
def verify_floor_exists():
    obj = bpy.data.objects.get("Floor")
    assert obj and obj.type == 'MESH'
    assert abs(obj.dimensions.x - 20) < 0.01
    assert abs(obj.dimensions.y - 20) < 0.01

result = verify_step("Create floor", verify_floor_exists)
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MATERIALS API REFERENCE](materials.md), [BLENDER MESH OPERATIONS API REFERENCE](mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](blender-api.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md)
- **По темам:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [PROMPTING GUIDE - EFFECTIVE AI COMMANDS FOR BLENDER](../guides/prompting.md)
- **Теги:** #blender, #reference

---

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

