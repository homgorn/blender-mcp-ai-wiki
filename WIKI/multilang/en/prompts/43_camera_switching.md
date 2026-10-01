---
id: 43_camera_switching
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P43: CAMERA SWITCHING & MARKERS

> Goal: ---

**ID:** 43_camera_switching | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** bindings, camera, markers, multi, multi-cam, sequencer

## How to use
This page is the en version of '43_camera_switching'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.

## MCP Prompt (copy-paste)
```
43_camera_switching / prompts / bindings, camera, markers, multi, multi-cam, sequencer
```

> Note: code/paths stay in English for Blender/Python compatibility.

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
- **Промпты:** [P14 Camera](./14_camera_composition.md), [P33 Camera Path](./33_camera_path.md)
- **Следующий:** [P44: Mocap Retarget](./44_mocap_retarget.md)
