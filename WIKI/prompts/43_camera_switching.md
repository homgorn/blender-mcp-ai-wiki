---
lang: ru
tags: [animation, modeling, prompt, render]
---
# P43: CAMERA SWITCHING & MARKERS

**ID:** P43 | **Кластер:** Animation/Render | **Сложность:** ⭐⭐ | **Теги:** #camera #markers #bindings #sequencer #multi-cam

---

## 🎯 ЦЕЛЬ
Несколько камер в одной сцене: маркеры, привязки, переключение для монтажа

---

## 📝 ПРОМПТ (РУС)

```
Настрой [N] камер: [имена] на кадрах [F1, F2...].
Привяжи маркеры (Ctrl+B), проверь переключение в viewport.
```

---

## 📝 ПРОМПТ (ENG)

```
Setup [N] cameras: [names] at frames [F1, F2...].
Bind markers (Ctrl+B), verify switching in viewport.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def bind_cameras(bindings):
    """bindings: {frame: camera_name}"""
    s = bpy.context.scene
    for frame, cam_name in sorted(bindings.items()):
        cam = bpy.data.objects.get(cam_name)
        if not cam or cam.type != 'CAMERA':
            raise ValueError(f"Camera {cam_name} not found")
        marker = s.timeline_markers.new(f"Cam_{cam_name}", frame=frame)
        marker.camera_data = cam.data
    s.frame_start = min(bindings)
    return {"bound": len(bindings)}

def camera_from_view(cam_name):
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = cam_name
    bpy.context.scene.camera = cam
    bpy.ops.view3d.camera_to_view()
    return {"camera": cam_name}

# bind_cameras({1: "Cam_Wide", 60: "Cam_Medium", 120: "Cam_Close"})
```

---

## 📊 ПРИЁМЫ
| Приём | Как |
|-------|-----|
| Жёсткая склейка | Маркеры на соседних кадрах |
| Перебивка | Отдельная камера деталей на 10–15 кадров |
| Облёт + склейка | Path-камера (см. P33), склейки маркерами |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P14: CAMERA & COMPOSITION](14_camera_composition.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md), [P19: NLA EDITOR WORKFLOW](19_nla_workflow.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P33: CAMERA PATH ANIMATION](33_camera_path.md)
- **По темам:** [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 13: HARD-SURFACE SCI-FI GUN](../cases/case_13_hard_surface_gun.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md)
- **Теги:** #animation, #bindings, #camera, #markers, #modeling, #multi, #multi-cam, #prompt, #render, #sequencer

