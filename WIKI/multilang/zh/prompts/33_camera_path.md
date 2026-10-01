---
id: 33_camera_path
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P33: 相机 PATH ANIMATION

> 目标: ---

**ID:** 33_camera_path | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** camera, dof, follow, follow-path, rack, rack-focus, track, track-to

## 使用方法
这是 '33_camera_path' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
33_camera_path / prompts / camera, dof, follow, follow-path, rack, rack-focus, track, track-to
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

# P33: CAMERA PATH ANIMATION

**ID:** P33 | **Кластер:** Animation | **Сложность:** ⭐⭐ | **Теги:** #camera #follow-path #track-to #dof #rack-focus

---

## 🎯 ЦЕЛЬ
Камера по кривой + Track To на цель + анимация фокуса (rack focus)

---

## 📝 ПРОМПТ (РУС)

```
Анимируй камеру "[CAM]" по кривой "[CURVE]" за [N] кадров, цель "[TARGET]".
Rack focus: [OBJ_A] → [OBJ_B] на кадрах [F1-F2].
```

---

## 📝 ПРОМПТ (ENG)

```
Animate camera "[CAM]" along curve "[CURVE]" over [N] frames, target "[TARGET]".
Rack focus: [OBJ_A] → [OBJ_B] at frames [F1-F2].
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def camera_follow_path(cam_name, curve_name, frames=250, target_name=None):
    cam = bpy.data.objects.get(cam_name)
    curve = bpy.data.objects.get(curve_name)
    if not cam or not curve:
        raise ValueError("Camera or curve not found")
    c = cam.constraints.new('FOLLOW_PATH')
    c.target = curve
    c.use_curve_follow = True
    c.use_fixed_location = True
    curve.data.path_duration = frames
    curve.data.eval_time = 1
    curve.data.keyframe_insert("eval_time", frame=1)
    curve.data.eval_time = frames
    curve.data.keyframe_insert("eval_time", frame=frames)
    for fc in curve.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    if target_name:
        t = cam.constraints.new('TRACK_TO')
        t.target = bpy.data.objects.get(target_name)
        t.track_axis = 'TRACK_NEGATIVE_Z'
        t.up_axis = 'UP_Y'
    return {"camera": cam_name, "frames": frames}
```

---

## 🔗 СВЯЗИ
- **Промпты:** [P14 Camera](./14_camera_composition.md), [P16 Keyframes](./16_keyframe_animation.md)
- **Следующий:** [P34: Corrective Shapes](./34_corrective_shapes.md)
