# BLENDER API DEEP: OPERATORS, PANELS & PROFILING

**Advanced Blender Python API patterns for production add-ons and automation**

---

## 🎯 OPERATORS (bpy.types.Operator)

### Complete Operator Template
```python
import bpy
from bpy.props import (
    FloatProperty, IntProperty, BoolProperty, 
    EnumProperty, StringProperty, PointerProperty,
    FloatVectorProperty, CollectionProperty
)
from bpy.types import Operator, Panel, PropertyGroup

class MY_OT_advanced_operator(bpy.types.Operator):
    """Advanced operator with full feature set"""
    bl_idname = "my.advanced_operator"
    bl_label = "Advanced Operator"
    bl_description = "Full-featured operator with undo, modal, invoke, draw"
    bl_options = {'REGISTER', 'UNDO', 'PRESET', 'BLOCKING'}
    
    # Properties
    intensity: FloatProperty(
        name="Intensity",
        description="Effect intensity",
        default=1.0, min=0.0, max=10.0,
        soft_min=0.0, soft_max=5.0,
        step=10, precision=3,
        unit='NONE', subtype='FACTOR'
    )
    
    count: IntProperty(
        name="Count",
        default=1, min=1, max=1000,
        step=1
    )
    
    use_advanced: BoolProperty(
        name="Advanced Mode",
        default=False,
        description="Enable advanced options"
    )
    
    mode: EnumProperty(
        name="Mode",
        items=[
            ('FAST', "Fast", "Quick processing"),
            ('QUALITY', "Quality", "High quality"),
            ('CUSTOM', "Custom", "Custom settings"),
        ],
        default='FAST'
    )
    
    target_object: PointerProperty(
        name="Target",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH'
    )
    
    # Advanced: CollectionProperty for lists
    items: CollectionProperty(type=bpy.types.PropertyGroup)
    
    # State for modal operators
    _timer = None
    _mouse_pos = (0, 0)
    _start_value = 0.0
    
    # ===== INVOKE (called on user action) =====
    def invoke(self, context, event):
        if self.use_advanced:
            return context.window_manager.invoke_props_dialog(self, width=400)
        return self.execute(context)
    
    # ===== DRAW (UI in dialog/popover) =====
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.prop(self, "intensity")
        layout.prop(self, "count")
        layout.prop(self, "mode")
        layout.prop(self, "target_object")
        layout.prop(self, "use_advanced")
        
        if self.use_advanced:
            box = layout.box()
            box.label(text="Advanced Options:")
            # Add advanced props here
    
    # ===== EXECUTE (Main logic) =====
    def execute(self, context):
        try:
            result = self.process(context)
            self.report({'INFO'}, f"Processed {self.count} objects")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
    
    def process(self, context):
        """Main processing logic"""
        objects = [self.target_object] if self.target_object else \
                  [o for o in context.selected_objects if o.type == 'MESH']
        
        for i, obj in enumerate(objects[:self.count]):
            # Process each object
            self.process_object(obj, i)
        
        return len(objects)
    
    def process_object(self, obj, index):
        # Your processing logic here
        pass
    
    # ===== MODAL (Long-running with UI updates) =====
    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.cancel(context)
            return {'CANCELLED'}
        
        if event.type == 'TIMER':
            # Update progress
            self.update_progress(context)
            return {'RUNNING_MODAL'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if self.use_advanced:
            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return self.execute(context)
    
    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
    
    def update_progress(self, context):
        # Update progress bar, viewport, etc.
        pass

# ===== REGISTRATION =====
classes = [MY_OT_advanced_operator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

---

## 🎨 PANELS & UI (bpy.types.Panel)

### Advanced Panel with Layout Tricks
```python
class MY_PT_advanced_panel(bpy.types.Panel):
    bl_label = "Advanced Tools"
    bl_idname = "MY_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Tools"
    bl_order = 10
    bl_parent_id = None  # Set to parent panel ID for sub-panels
    bl_options = {'DEFAULT_CLOSED', 'HEADER_LAYOUT_EXPAND'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='TOOL_SETTINGS')
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        # Header with icon
        row = layout.row()
        row.label(text=f"Active: {obj.name}", icon='OBJECT_DATA')
        
        # Box with custom styling
        box = layout.box()
        box.label(text="Quick Actions", icon='TOOL_SETTINGS')
        
        # Operator buttons with icons
        row = box.row(align=True)
        row.operator("object.shade_smooth", icon='MOD_SUBSURF', text="Smooth")
        row.operator("object.shade_flat", icon='MOD_SUBSURF', text="Flat")
        
        # Split layout
        split = layout.split(factor=0.6)
        col1 = split.column()
        col2 = split.column()
        
        col1.label(text="Settings:")
        col1.prop(context.scene, "my_custom_prop")
        
        col2.label(text="Actions:")
        col2.operator("my.custom_operator", icon='PLAY')
        
        # Expandable section
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_advanced", 
                 icon='TRIA_DOWN' if context.scene.show_advanced else 'TRIA_RIGHT',
                 icon_only=True, emboss=False)
        row.label(text="Advanced Options")
        
        if context.scene.show_advanced:
            box.prop(context.scene, "advanced_setting1")
            box.prop(context.scene, "advanced_setting2")
        
        # Dynamic list
        if hasattr(bpy.context.scene, 'my_list'):
            layout.template_list(
                "MY_UL_custom_list", "", 
                context.scene, "my_list",
                context.scene, "my_list_index",
                rows=3
            )
        
        # Progress bar
        if hasattr(context.scene, 'my_progress'):
            layout.progress(context.scene.my_progress, text="Processing...")
```

### Custom List Template
```python
class MY_UL_custom_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon='OBJECT_DATA')
            row.prop(item, "enabled", text="", icon='CHECKBOX_HLT' if item.enabled else 'CHECKBOX_DEHLT')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='OBJECT_DATA')

class MyListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    enabled: bpy.props.BoolProperty(default=True)
    value: bpy.props.FloatProperty(default=1.0)

# Register
bpy.utils.register_class(MyListItem)
bpy.types.Scene.my_list = bpy.props.CollectionProperty(type=MyListItem)
bpy.types.Scene.my_list_index = bpy.props.IntProperty()
```

---

## ⚡ PROFILING & PERFORMANCE

### Built-in Profiling
```python
import cProfile
import pstats
import io
from contextlib import contextmanager

@contextmanager
def profile_context(name="profile"):
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield profiler
    finally:
        profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats('cumulative')
        stats.print_stats(20)
        print(f"\n=== {name} Profile ===")
        print(stream.getvalue())

# Usage
with profile_context("Heavy Operation"):
    result = heavy_operation()
```

### Blender-Specific Profiling
```python
import bpy
import time

def time_operator(operator_id, *args, **kwargs):
    """Time a Blender operator"""
    start = time.perf_counter()
    result = bpy.ops.__dict__[operator_id](*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"{operator_id}: {elapsed:.4f}s")
    return result

# Profile mesh operations
def profile_mesh_ops(obj, operations):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    for op_name, op_func in operations:
        start = time.perf_counter()
        op_func(bm)
        elapsed = time.perf_counter() - start
        print(f"BMesh {op_name}: {elapsed:.4f}s")
    
    bm.to_mesh(obj.data)
    bm.free()

# Profile viewport performance
def profile_viewport_redraw(iterations=100):
    import time
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    
    start = time.perf_counter()
    for _ in range(iterations):
        area.tag_redraw()
        bpy.context.window_manager.event_timer_add(0.001, window=bpy.context.window)
    elapsed = time.perf_counter() - start
    print(f"{iterations} redraws: {elapsed:.4f}s ({elapsed/iterations*1000:.2f}ms each)")
```

### Memory Profiling
```python
import sys
import gc

def get_memory_usage():
    """Get current memory usage in MB"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def profile_memory_growth(iterations=100):
    """Track memory growth over iterations"""
    gc.collect()
    initial = get_memory_usage()
    
    for i in range(iterations):
        # Your operation here
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.delete()
        
        if i % 10 == 0:
            gc.collect()
            current = get_memory_usage()
            print(f"Iteration {i}: {current - initial:.2f} MB growth")

def find_memory_leaks():
    """Find objects not being garbage collected"""
    import gc
    gc.collect()
    
    before = len(gc.get_objects())
    
    # Your operation
    for _ in range(100):
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.delete()
    
    gc.collect()
    after = len(gc.get_objects())
    
    print(f"Object count delta: {after - before}")
    if after - before > 100:
        print("⚠️ Possible memory leak!")
        
        # Find what's leaking
        types_count = {}
        for obj in gc.get_objects():
            t = type(obj).__name__
            types_count[t] = types_count.get(t, 0) + 1
        
        for t, count in sorted(types_count.items(), key=lambda x: -x[1])[:20]:
            print(f"  {t}: {count}")
```

---

## 🐛 DEBUGGING TECHNIQUES

### Remote Debugging (VS Code / PyCharm)
```python
# In Blender Python Console:
import debugpy
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()
print("Debugger attached!")

# Then in launch.json:
# {
#   "name": "Blender Debug",
#   "type": "python",
#   "request": "attach",
#   "connect": {"host": "localhost", "port": 5678},
#   "pathMappings": [{"localRoot": "${workspaceFolder}", "remoteRoot": "/"}]
# }
```

### Debugging with Breakpoints
```python
# Programmatic breakpoint
import sys
def debug_break():
    import pdb; pdb.set_trace()  # or breakpoint() in Python 3.7+

# Conditional breakpoint
def debug_if(condition, msg="Debug break"):
    if condition:
        print(f"DEBUG: {msg}")
        breakpoint()

# In operator:
def execute(self, context):
    if context.object.name == "DebugMe":
        breakpoint()  # Stops here when object named "DebugMe"
    return {'FINISHED'}
```

### Logging Best Practices
```python
import logging
import sys

# Setup once per session
def setup_logging(level=logging.DEBUG):
    logger = logging.getLogger("my_addon")
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console)
    
    # File handler
    file_handler = logging.FileHandler("my_addon.log")
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    ))
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

# Usage in operator
class MY_OT_example(bpy.types.Operator):
    def execute(self, context):
        logger.info(f"Processing {len(context.selected_objects)} objects")
        try:
            # ... work ...
            logger.info("Completed successfully")
        except Exception as e:
            logger.exception(f"Failed: {e}")
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}
```

### Blender System Console Access
```python
# Show/hide system console (Windows)
import ctypes
def toggle_console():
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    console = kernel32.GetConsoleWindow()
    if console:
        user32.ShowWindow(console, 0 if ctypes.windll.user32.IsWindowVisible(console) else 1)

# Write to console directly
def console_print(*args, **kwargs):
    import sys
    print(*args, **kwargs, file=sys.__stdout__, flush=True)

# Redirect print to Blender's report system
class ReportCapture:
    def __init__(self, operator):
        self.op = operator
        self.messages = []
    
    def write(self, msg):
        if msg.strip():
            self.messages.append(msg.strip())
            self.op.report({'INFO'}, msg.strip())
    
    def flush(self):
        pass

# Usage
def execute(self, context):
    old_stdout = sys.stdout
    sys.stdout = ReportCapture(self)
    try:
        print("This goes to Blender reports!")
        # ... work ...
    finally:
        sys.stdout = old_stdout
    return {'FINISHED'}
```

---

## 🔧 CONTEXT MANAGERS & UTILITIES

### Safe Context Managers
```python
from contextlib import contextmanager

@contextmanager
def mode_context(mode='OBJECT'):
    """Temporarily switch mode, restore on exit"""
    original_mode = bpy.context.mode
    if original_mode != mode:
        bpy.ops.object.mode_set(mode=mode)
    try:
        yield
    finally:
        if bpy.context.mode != original_mode:
            bpy.ops.object.mode_set(mode=original_mode)

@contextmanager
def selection_context(objects):
    """Temporarily select objects, restore selection"""
    prev_active = bpy.context.view_layer.objects.active
    prev_selected = bpy.context.selected_objects[:]
    
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]
    
    try:
        yield
    finally:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in prev_selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = prev_active

@contextmanager
def temp_override(**kwargs):
    """Temporarily override context"""
    with bpy.context.temp_override(**kwargs):
        yield

# Usage
with mode_context('EDIT'):
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()

with selection_context([obj1, obj2]):
    bpy.ops.object.join()

with temp_override(area=area, region=region):
    bpy.ops.screen.region_quadview()
```

---

## 🧪 TESTING PATTERNS

### Unit Tests for Operators
```python
import unittest
import bpy
import bmesh

class TestMyOperator(unittest.TestCase):
    def setUp(self):
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
    
    def test_operator_creates_cube(self):
        bpy.ops.mesh.primitive_cube_add(location=(1, 2, 3))
        obj = bpy.context.active_object
        self.assertEqual(obj.name, "Cube")
        self.assertEqual(obj.location.x, 1.0)
    
    def test_bmesh_operations(self):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        mesh = bpy.data.meshes.new("Test")
        bm.to_mesh(mesh)
        bm.free()
        
        self.assertEqual(len(mesh.vertices), 8)
        self.assertEqual(len(mesh.polygons), 6)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests with pytest
```python
# tests/test_operators.py
import pytest
import bpy

@pytest.fixture(autouse=True)
def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    yield
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def test_operator_registration():
    assert "MY_OT_advanced_operator" in dir(bpy.types)

@pytest.mark.parametrize("mode,expected", [
    ('FAST', {'time': 0.1}),
    ('QUALITY', {'time': 1.0}),
])
def test_operator_modes(mode, expected):
    bpy.ops.my.advanced_operator(mode=mode)
    # Verify result matches expected
```

---

## 🔗 LINKS

- **Blender Python API:** https://docs.blender.org/api/current/
- **bpy.types.Operator:** https://docs.blender.org/api/current/bpy.types.Operator.html
- **bpy.types.Panel:** https://docs.blender.org/api/current/bpy.types.Panel.html
- **bpy.props:** https://docs.blender.org/api/current/bpy.props.html
- **bmesh:** https://docs.blender.org/api/current/bmesh.html
- **Blender Dev Wiki:** https://wiki.blender.org/wiki/Process/Addons

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/blender_api/operators_panels.md` |
| Russian | `multilang/ru/blender_api/operators_panels.md` |