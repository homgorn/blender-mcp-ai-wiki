---
lang: ru
---
# P44: MOCAP RETARGETING

**ID:** P44 | **Кластер:** Animation | **Сложность:** ⭐⭐⭐ | **Теги:** #mocap #retarget #rokoko #fbx #rigify #curves

---

## 🎯 ЦЕЛЬ
Перенести мокап (Rokoko/MoveAI FBX) на Rigify-риг: ретаргет, foot lock, чистка кривых, луп

---

## 📝 ПРОМПТ (РУС)

```
Ретаргеть мокап "[MOCAP_FBX]" на риг "[RIG]":
маппинг костей, foot lock, despike, bake в action "[NAME]".
```

---

## 📝 ПРОМПТ (ENG)

```
Retarget mocap "[MOCAP_FBX]" onto rig "[RIG]":
bone mapping, foot lock, despike, bake to action "[NAME]".
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

BONE_MAP = {
    "Hips": "torso", "Spine": "spine_fk",
    "LeftUpLeg": "thigh_fk.L", "LeftLeg": "shin_fk.L", "LeftFoot": "foot_fk.L",
    "RightUpLeg": "thigh_fk.R", "RightLeg": "shin_fk.R", "RightFoot": "foot_fk.R",
    "LeftArm": "upper_arm_fk.L", "LeftForeArm": "forearm_fk.L", "LeftHand": "hand_fk.L",
    "RightArm": "upper_arm_fk.R", "RightForeArm": "forearm_fk.R", "RightHand": "hand_fk.R",
    "Head": "head",
}

def retarget_action(mocap_rig, target_rig, action_name="Mocap_Retarget"):
    src = bpy.data.objects.get(mocap_rig)
    dst = bpy.data.objects.get(target_rig)
    if not src or not dst:
        raise ValueError("Rigs not found")
    # Копируем world-матрицы костей покадрово через constraints (bake позже)
    bpy.ops.object.select_all(action='DESELECT')
    dst.select_set(True)
    bpy.context.view_layer.objects.active = dst
    bpy.ops.object.mode_set(mode='POSE')
    for sbone, dbone in BONE_MAP.items():
        if sbone not in src.pose.bones or dbone not in dst.pose.bones:
            continue
        c = dst.pose.bones[dbone].constraints.new('COPY_ROTATION')
        c.target = src
        c.subtarget = sbone
        c.target_space = 'WORLD'
        c.owner_space = 'WORLD'
    bpy.ops.object.mode_set(mode='OBJECT')
    return {"mapped": len(BONE_MAP), "next": "bake action, удали constraints"}

def despike_action(action_name, threshold=0.5):
    act = bpy.data.actions.get(action_name)
    if not act:
        raise ValueError("Action not found")
    cleaned = 0
    for fc in act.fcurves:
        pts = fc.keyframe_points
        for i in range(1, len(pts) - 1):
            v0, v1, v2 = pts[i-1].co.y, pts[i].co.y, pts[i+1].co.y
            if abs(v1 - (v0 + v2) / 2) > threshold:
                pts[i].co.y = (v0 + v2) / 2
                cleaned += 1
    return {"despiked": cleaned}
```

---

## 📊 ЧЕК-ЛИСТ
- [ ] Масштаб мокапа = масштаб рига (иначе ноги «плывут»)
- [ ] Foot lock: IK-контроллеры стоп на контактных кадрах
- [ ] Despike перед bake
- [ ] Loop: первый кадр = последний +1

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 56 Mocap](../setups/setup_56_mocap_rokoko.md)
- **Промпты:** [P17 Rigify](./17_rigify_setup.md), [P19 NLA](./19_nla_workflow.md)
- **Следующий:** [P45: GN Simulation](./45_gn_simulation.md)
