---
id: 14_camera_composition
lang: en
category: prompts
type: prompt
difficulty: 2
translation: legacy
---

# P14: CAMERA & COMPOSITION

**ID:** P14 | **Cluster:** Lighting/Rendering | **Difficulty:** ⭐⭐ | **Tags:** #camera #composition #dof #framing #animation #render

---

## 🎯 GOAL
Setup professional cameras with proper framing, depth of field, and composition rules

---

## 📝 PROMPT

```
Setup camera "[CAM_NAME]" for scene:
Type: PERSP / ORTHO / PANO
Position: [X, Y, Z] | Target: [object/coordinates]
Focal Length: [mm] | Sensor: [Full Frame / APS-C / MFT]
DOF: Focus Object / Distance | F-Stop: [1.4-16]
Composition: Rule of Thirds / Golden Ratio / Center / Symmetry
```

---

## 🔧 MCP: `execute_blender_code`

### BASIC CAMERA SETUP
```python
import bpy
import math
from mathutils import Vector

def create_camera(name, location, target, lens=50, sensor_width=36, clip_start=0.1, clip_end=1000):
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    cam_obj.location = location
    cam_data.lens = lens
    cam_data.sensor_width = sensor_width
    cam_data.clip_start = clip_start
    cam_data.clip_end = clip_end
    
    if target:
        if isinstance(target, str):
            target_obj = bpy.data.objects.get(target)
        else:
            target_obj = target
        
        if target_obj:
            constraint = cam_obj.constraints.new('TRACK_TO')
            constraint.target = target_obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
    
    return cam_obj

cam = create_camera("Cam_Main", (7, -7, 5), "Main_Subject", lens=50)
bpy.context.scene.camera = cam
```

### DEPTH OF FIELD (DOF)
```python
def setup_dof(camera_obj, focus_object=None, focus_distance=5.0, fstop=2.8, blades=8):
    cam = camera_obj.data
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = fstop
    cam.dof.aperture_blades = blades
    cam.dof.aperture_ratio = 1.0
    
    if focus_object:
        cam.dof.focus_object = focus_object
    else:
        cam.dof.focus_distance = focus_distance
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.show_camera_dof = True

cam = bpy.data.objects.get("Cam_Main")
subject = bpy.data.objects.get("Main_Subject")
setup_dof(cam, focus_object=subject, fstop=1.8)
```

### COMPOSITION GUIDES
```python
def setup_composition_guides(camera_obj, guide_type='THIRDS'):
    cam = camera_obj.data
    cam.show_composition_guides = True
    
    guides = {
        'THIRDS': 'THIRDS',
        'GOLDEN': 'GOLDEN',
        'QUARTERS': 'QUARTERS',
        'DIAGONAL': 'DIAGONAL',
        'HARMONIC_TRIANGLES': 'HARMONIC_TRIANGLES_A',
        'CROSSHAIR': 'CROSSHAIR',
    }
    
    if guide_type in guides:
        cam.composition_guide = guides[guide_type]

setup_composition_guides(cam, 'THIRDS')
```

### CAMERA ANIMATION (Path Following)
```python
def animate_camera_path(camera_obj, curve_obj, frames=250, look_at_target=None):
    constraint = camera_obj.constraints.new('FOLLOW_PATH')
    constraint.target = curve_obj
    constraint.use_curve_follow = True
    constraint.use_fixed_location = True
    
    curve_obj.data.eval_time = 1
    curve_obj.data.path_duration = frames
    
    curve_obj.data.keyframe_insert("eval_time", frame=1)
    curve_obj.data.eval_time = frames
    curve_obj.data.keyframe_insert("eval_time", frame=frames)
    
    for fcurve in curve_obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'
    
    if look_at_target:
        track = camera_obj.constraints.new('TRACK_TO')
        track.target = look_at_target
        track.track_axis = 'TRACK_NEGATIVE_Z'
        track.up_axis = 'UP_Y'
        track.influence = 1.0

import math
curve_data = bpy.data.curves.new("Cam_Path", 'CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(3)

points = [(0, -10, 3), (5, -5, 4), (5, 5, 3), (0, 10, 2)]
for i, pt in enumerate(points):
    bp = spline.bezier_points[i]
    bp.co = pt
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'

curve_obj = bpy.data.objects.new("Cam_Path", curve_data)
bpy.context.collection.objects.link(curve_obj)

cam = bpy.data.objects.get("Cam_Main")
target = bpy.data.objects.get("Main_Subject")
animate_camera_path(cam, curve_obj, frames=250, look_at_target=target)
```

### DOF ANIMATION (Rack Focus)
```python
def animate_rack_focus(camera_obj, start_obj, end_obj, start_frame=1, end_frame=100):
    cam = camera_obj.data
    cam.dof.use_dof = True
    
    cam.dof.focus_object = start_obj
    cam.keyframe_insert('dof.focus_object', frame=start_frame)
    
    cam.dof.focus_object = end_obj
    cam.keyframe_insert('dof.focus_object', frame=end_frame)
    
    if camera_obj.animation_data and camera_obj.animation_data.action:
        for fcurve in camera_obj.animation_data.action.fcurves:
            if 'focus_object' in fcurve.data_path:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'

animate_rack_focus(cam, subject1, subject2, 1, 120)
```

### MULTI-CAMERA SETUP
```python
def setup_multi_camera(names_positions, target, lens=50):
    cams = []
    for i, (name, pos) in enumerate(names_positions):
        cam = create_camera(name, pos, target, lens=lens)
        cams.append(cam)
        
        marker = bpy.context.scene.timeline_markers.new(f"Cam_{name}", frame=i*50+1)
        marker.camera = cam
    
    return cams

cams = setup_multi_camera([
    ("Cam_Wide", (-10, -10, 5)),
    ("Cam_Medium", (-5, -5, 3)),
    ("Cam_Close", (-2, -2, 2)),
    ("Cam_Detail", (-1, -1, 1.5)),
], "Main_Subject", lens=35)
```

### CAMERA PRESETS
```python
CAMERA_PRESETS = {
    'PRODUCT': {'lens': 50, 'sensor': 36, 'fstop': 8, 'dist': 2},
    'PORTRAIT': {'lens': 85, 'sensor': 36, 'fstop': 1.8, 'dist': 1.5},
    'ARCHITECTURE': {'lens': 24, 'sensor': 36, 'fstop': 11, 'dist': 10},
    'LANDSCAPE': {'lens': 16, 'sensor': 36, 'fstop': 16, 'dist': 50},
    'MACRO': {'lens': 100, 'sensor': 36, 'fstop': 5.6, 'dist': 0.3},
    'DRONE': {'lens': 20, 'sensor': 36, 'fstop': 8, 'dist': 100},
    'INTERIOR': {'lens': 35, 'sensor': 36, 'fstop': 4, 'dist': 5},
}

def apply_camera_preset(camera_obj, preset_name, target):
    preset = CAMERA_PRESETS[preset_name]
    cam = camera_obj.data
    cam.lens = preset['lens']
    cam.sensor_width = preset['sensor']
    setup_dof(camera_obj, target, fstop=preset['fstop'])
```

---

## 📊 COMPOSITION RULES

| Rule | Description | Camera | Use Case |
|------|-------------|--------|----------|
| Rule of Thirds | 3x3 grid, object at intersection | THIRDS | Universal |
| Golden Ratio | Fibonacci spiral | GOLDEN | Nature, portrait |
| Center | Object in center | CROSSHAIR | Symmetry, product |
| Symmetry | Mirror reflection | CENTER | Architecture, auto |
| Leading Lines | Lines lead to object | DIAGONAL | Roads, perspective |
| Frame in Frame | Frame within frame | CUSTOM | Arches, windows |
| Negative Space | Empty space | CUSTOM | Minimalism |

---

## 🔗 LINKS

- **Prompts:** [P13 Lighting](./13_lighting_hdri.md), [P15 Compositing](./15_compositing.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **MCP Tools:** `execute_blender_code`, `get_viewport_screenshot`
- **Next:** [P15: Compositing](./15_compositing.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/14_camera_composition.md` |
| Russian | `multilang/ru/prompts/14_camera_composition.md` |