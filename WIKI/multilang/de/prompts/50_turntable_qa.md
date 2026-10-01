---
id: 50_turntable_qa
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P50: PORTFOLIO TURNTABLE & QA

> Ziel: ---

**ID:** 50_turntable_qa | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** checklist, portfolio, presentation, qa, turntable

## Verwendung
Dies ist die deutsche Version von '50_turntable_qa'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
50_turntable_qa / prompts / checklist, portfolio, presentation, qa, turntable
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P50: PORTFOLIO TURNTABLE & QA

**ID:** P50 | **Кластер:** Pipeline/Presentation | **Сложность:** ⭐ | **Теги:** #turntable #portfolio #qa #checklist #presentation

---

## 🎯 ЦЕЛЬ
Финальная подача ассета: тёрнтейбл-риг, lighting ladder, QA-чеклист, экспорт превью

---

## 📝 ПРОМПТ (РУС)

```
Собери тёрнтейбл для "[ASSET]": 120 кадров, 3 ракурса света,
wireframe+shaded+clay пассы. Прогони QA-чеклист, экспортируй MP4+PNG.
```

---

## 📝 ПРОМПТ (ENG)

```
Build turntable for "[ASSET]": 120 frames, 3 light angles,
wireframe+shaded+clay passes. Run QA checklist, export MP4+PNG.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy
import math

def turntable_rig(target_name, radius=3.0, height=1.2, frames=120, lens=85):
    tgt = bpy.data.objects.get(target_name)
    if not tgt:
        raise ValueError("Target not found")
    # Пустышка-центр на объекте
    bpy.ops.object.empty_add(location=tgt.location)
    pivot = bpy.context.active_object
    pivot.name = f"Turntable_{target_name}"
    # Камера
    bpy.ops.object.camera_add(location=(radius, 0, height))
    cam = bpy.context.active_object
    cam.name = f"Cam_Turntable_{target_name}"
    cam.data.lens = lens
    t = cam.constraints.new('TRACK_TO')
    t.target = pivot
    t.track_axis = 'TRACK_NEGATIVE_Z'
    t.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    # Вращение пивота 360° за frames
    pivot.rotation_euler = (0, 0, 0)
    pivot.keyframe_insert("rotation_euler", frame=1)
    pivot.rotation_euler = (0, 0, math.radians(360))
    pivot.keyframe_insert("rotation_euler", frame=frames)
    for fc in pivot.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    s = bpy.context.scene
    s.frame_start = 1
    s.frame_end = frames
    return {"turntable": pivot.name, "camera": cam.name, "frames": frames}

# turntable_rig("Hero", radius=2.5, frames=120)
```

---

## 📊 QA-ЧЕКЛИСТ (финальный)
- [ ] Scale applied, origin внизу/центре, имя по конвенции
- [ ] Non-manifold = 0, UV без перекрытий, нормали наружу
- [ ] Текстуры: BaseColor sRGB, остальные Non-Color, именование `{asset}_{map}_{res}`
- [ ] LOD0/1/2 на месте, трисы в бюджете
- [ ] Тёрнтейбл: shaded + clay + wireframe, 120f, MP4
- [ ] GLB/FBX открываются в чистом Blender

---

## 🔗 СВЯЗИ
- **Промпты:** [P14 Camera](./14_camera_composition.md), [P39 Export](./39_export_presets.md)
- **Кейсы:** [Case 03 Product Viz](../cases/case_03_product_viz.md)
