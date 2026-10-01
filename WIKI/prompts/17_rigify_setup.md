---
lang: ru
tags: [prompt, rigging]
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

- **Прочие в категории «Промпты»:** [P44: MOCAP RETARGETING](44_mocap_retarget.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md), [P03: MODIFIERS STACK](03_modifiers_stack.md), [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P05: UV UNWRAPPING STRATEGIES](05_uv_unwrapping.md), [P06: RETOPOLOGY WORKFLOW](06_retopology_workflow.md)
- **Теги:** #armature, #humanoid, #prompt, #rigging, #rigify, #weights

