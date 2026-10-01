---
id: 14_camera_composition
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P14: CÁMARA & COMPOSITION

> Objetivo: 

**ID:** 14_camera_composition | **Lang:** es | **Orig:** ru | **Category:** prompts | **Tags:** **, animation, camera, composition, dof, framing, render

## Cómo usar
Esta es la versión en español de '14_camera_composition'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
14_camera_composition / prompts / **, animation, camera, composition, dof, framing, render
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: 14_camera_composition
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 2
---

# P14: CAMERA & COMPOSITION

> Цель: ## 🌍 MULTILANG

**ID:** 14_camera_composition | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, animation, camera, composition, dof, framing, render

---

# P14: CAMERA & COMPOSITION

**ID:** P14 | **Cluster:** Lighting/Rendering | **Difficulty:** ⭐⭐ | **Tags:** #camera #composition #dof #framing #animation #render

---

## 🎯 GOAL
Setup professional cameras with proper framing, depth of field, and composition rules

---

## 📝 PROMPT (RUS)

```
Настрой камеру "[CAM_NAME]" для сцены:
Тип: PERSP / ORTHO / PANO
Позиция: [X, Y, Z] | Target: [объект/координаты]
Focal Length: [mm] | Sensor: [Full Frame / APS-C / MFT]
DOF: Focus Object / Distance | F-Stop: [1.4-16]
Composition: Rule of Thirds / Golden Ratio / Center / Symmetry
```

---

## 📝 PROMPT (ENG)

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
    """Создать камеру с целью"""
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    cam_obj.location = location
    cam_data.lens = lens
    cam_data.sensor_width = sensor_width
    cam_data.clip_start = clip_start
    cam_data.clip_end = clip_end
    
    # Track To constraint
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

# Активная камера
cam = create_camera("Cam_Main", (7, -7, 5), "Main_Subject", lens=50)
bpy.context.scene.camera = cam
```

### DEPTH OF FIELD (DOF)
```python
def setup_dof(camera_obj, focus_object=None, focus_distance=5.0, fstop=2.8, blades=8):
    """Настройка глубины резкости"""
    cam = camera_obj.data
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = fstop
    cam.dof.aperture_blades = blades
    cam.dof.aperture_ratio = 1.0
    
    if focus_object:
        cam.dof.focus_object = focus_object
    else:
        cam.dof.focus_distance = focus_distance
    
    # Viewport DOF preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.show_camera_dof = True

# Использование
cam = bpy.data.objects.get("Cam_Main")
subject = bpy.data.objects.get("Main_Subject")
setup_dof(cam, focus_object=subject, fstop=1.8)
```

### COMPOSITION GUIDES
```python
def setup_composition_guides(camera_obj, guide_type='THIRDS'):
    """Показать направляющие композиции в viewport"""
    cam = camera_obj.data
    
    # Включить сетку в камере
    cam.show_composition_guides = True
    
    # Типы направляющих (доступны в Blender 3.0+)
    guides = {
        'THIRDS': 'THIRDS',           # Rule of Thirds
        'GOLDEN': 'GOLDEN',           # Golden Ratio
        'QUARTERS': 'QUARTERS',       # Quarters
        'DIAGONAL': 'DIAGONAL',       # Diagonal
        'HARMONIC_TRIANGLES': 'HARMONIC_TRIANGLES_A', 'HARMONIC_TRIANGLES_B',
        'CROSSHAIR': 'CROSSHAIR',
    }
    
    if guide_type in guides:
        cam.composition_guide = guides[guide_type]

# Использование
setup_composition_guides(cam, 'THIRDS')  # или 'GOLDEN'
```

### CAMERA ANIMATION (Path Following)
```python
def animate_camera_path(camera_obj, curve_obj, frames=250, look_at_target=None):
    """Анимировать камеру по кривой"""
    # Follow Path constraint
    constraint = camera_obj.constraints.new('FOLLOW_PATH')
    constraint.target = curve_obj
    constraint.use_curve_follow = True
    constraint.use_fixed_location = True
    
    # Анимировать offset (0.0 -> 1.0)
    curve_obj.data.eval_time = 1
    curve_obj.data.path_duration = frames
    
    # Анимация eval_time
    curve_obj.data.keyframe_insert("eval_time", frame=1)
    curve_obj.data.eval_time = frames
    curve_obj.data.keyframe_insert("eval_time", frame=frames)
    
    # Interpolation LINEAR для равномерного движения
    for fcurve in curve_obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'
    
    # Track To target
    if look_at_target:
        track = camera_obj.constraints.new('TRACK_TO')
        track.target = look_at_target
        track.track_axis = 'TRACK_NEGATIVE_Z'
        track.up_axis = 'UP_Y'
        track.influence = 1.0

# Создать путь
import math
curve_data = bpy.data.curves.new("Cam_Path", 'CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(3)

# Настроить точки пути
points = [
    (0, -10, 3),   # Start
    (5, -5, 4),    # Point 1
    (5, 5, 3),     # Point 2
    (0, 10, 2),    # End
]
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
    """Анимация переключения фокуса (Rack Focus)"""
    cam = camera_obj.data
    cam.dof.use_dof = True
    
    # Ключевые кадры focus_object
    cam.dof.focus_object = start_obj
    cam.keyframe_insert('dof.focus_object', frame=start_frame)
    
    cam.dof.focus_object = end_obj
    cam.keyframe_insert('dof.focus_object', frame=end_frame)
    
    # Плавность перехода
    if camera_obj.animation_data and camera_obj.animation_data.action:
        for fcurve in camera_obj.animation_data.action.fcurves:
            if 'focus_object' in fcurve.data_path:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'

# Использование
animate_rack_focus(cam, subject1, subject2, 1, 120)
```

### MULTI-CAMERA SETUP (Для редактирования)
```python
def setup_multi_camera(names_positions, target, lens=50):
    """Создать несколько камер для разных ракурсов"""
    cams = []
    for i, (name, pos) in enumerate(names_positions):
        cam = create_camera(name, pos, target, lens=lens)
        cams.append(cam)
        
        # Marker для переключения в Sequencer
        marker = bpy.context.scene.timeline_markers.new(f"Cam_{name}", frame=i*50+1)
        marker.camera = cam
    
    return cams

# Использование
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
    # Позиция на расстоянии preset['dist'] от цели
    # ... расчёт позиции
```

### RENDER SETTINGS PER CAMERA
```python
def set_render_for_camera(camera_obj, resolution_x=1920, resolution_y=1080, samples=128):
    """Настроить рендер для конкретной камеры"""
    scene = bpy.context.scene
    scene.camera = camera_obj
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.filepath = f"//renders/{camera_obj.name}_"
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
```

---

## 📊 COMPOSITION RULES REFERENCE

| Правило | Описание | Камера | Использование |
|---------|----------|--------|---------------|
| **Rule of Thirds** | Сетка 3x3, объект на пересечении | THIRDS | Универсально |
| **Golden Ratio** | Спираль Фибоначчи | GOLDEN | Природа, портрет |
| **Center** | Объект в центре | CROSSHAIR | Симметрия, продукт |
| **Symmetry** | Зеркальное отражение | CENTER | Архитектура, авто |
| **Leading Lines** | Линии ведут к объекту | DIAGONAL | Дороги, перспектива |
| **Frame in Frame** | Рамка в рамке | CUSTOM | Арки, окна |
| **Negative Space** | Пустое пространство | CUSTOM | Минимализм |

---

## 🔗 LINKS

- **Prompts:** [P13 Lighting](./13_lighting_hdri.md), [P15 Compositing](./15_compositing.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md), [WF 04: Animation](../workflows/wf_04_character_animation.md)
- **MCP Tools:** `execute_blender_code`, `get_viewport_screenshot`
- **Next:** [P15: Compositing](./15_compositing.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/14_camera_composition.md` |
| Russian | `multilang/ru/prompts/14_camera_composition.md` |