---
lang: ru
---
# P17: RIGIFY HUMANOID SETUP

**ID:** P17 | **Кластер:** Animation | **Сложность:** ⭐⭐ | **Теги:** #rigify #rigging #armature #weights #humanoid

---

## 🎯 ЦЕЛЬ
Rigify-риг для humanoid-персонажа: meta-rig → generate → weights → тест поз

---

## 📝 ПРОМПТ (РУС)

```
Зариггай "[MESH_NAME]" через Rigify:
Meta-rig: Human, масштаб под меш
Generate → Parent (Automatic Weights) → Weight Paint чистка
Тест: T-pose, A-pose, присед
```

---

## 📝 ПРОМПТ (ENG)

```
Rig "[MESH_NAME]" with Rigify:
Meta-rig: Human scaled to mesh
Generate → Parent (Automatic Weights) → Weight cleanup
Test: T-pose, A-pose, squat
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def rigify_setup(mesh_name):
    mesh = bpy.data.objects.get(mesh_name)
    if not mesh or mesh.type != 'MESH':
        raise ValueError("Mesh required")
    # Meta-rig
    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.active_object
    meta.name = "MetaRig"
    # Масштабировать под меш (вручную в UI или кодом)
    # Generate
    bpy.context.view_layer.objects.active = meta
    bpy.ops.object.armature_human_tweak_add()  # опционально
    bpy.ops.pose.rigify_generate()
    rig = bpy.data.objects.get("rig")
    # Parent
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True); rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    return {"rig": rig.name, "mesh": mesh.name}

# rigify_setup("Character_Body")
```

---

## 📊 ЧЕК-ЛИСТ РИГА
- [ ] Meta-rig кости внутри меша
- [ ] Generate без ошибок
- [ ] Веса: голова=skull, плечи=градиент, пальцы=по фалангам
- [ ] Экстремальные позы без разрывов

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 04: Character Rig](../cases/case_04_character_rig.md)
- **Промпты:** [P16 Keyframes](./16_keyframe_animation.md), [P18 Drivers](./18_drivers_constraints.md)
- **Следующий:** [P18: Drivers & Constraints](./18_drivers_constraints.md)
