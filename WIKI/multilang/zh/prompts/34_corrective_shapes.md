---
id: 34_corrective_shapes
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P34: CORRECTIVE SHAPE KEYS

> 目标: ---

**ID:** 34_corrective_shapes | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** corrective, deform, drivers, rig, shape, shape-keys

## 使用方法
这是 '34_corrective_shapes' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
34_corrective_shapes / prompts / corrective, deform, drivers, rig, shape, shape-keys
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

# P34: CORRECTIVE SHAPE KEYS

**ID:** P34 | **Кластер:** Animation | **Сложность:** ⭐⭐⭐ | **Теги:** #corrective #shape-keys #drivers #rig #deform

---

## 🎯 ЦЕЛЬ
Коррективы деформаций: shape key + driver от кости (локти, колени, плечи)

---

## 📝 ПРОМПТ (РУС)

```
Создай corrective "[KEY]" на "[MESH]" для кости "[BONE]".
Драйвер: rotation → value 0..1 с плавным переходом.
```

---

## 📝 ПРОМПТ (ENG)

```
Create corrective "[KEY]" on "[MESH]" for bone "[BONE]".
Driver: rotation → value 0..1 with smooth mapping.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def corrective_key(mesh_name, key_name, rig_name, bone_name, lo=0.5, hi=1.2):
    mesh = bpy.data.objects.get(mesh_name)
    if not mesh.data.shape_keys:
        mesh.shape_key_add(name="Basis", from_mix=False)
    key = mesh.shape_key_add(name=key_name, from_mix=False)
    key.slider_min = 0.0
    key.slider_max = 1.0
    drv = key.driver_add("value").driver
    drv.type = 'SCRIPTED'
    var = drv.variables.new()
    var.name = "r"
    var.type = 'TRANSFORMS'
    var.targets[0].id = bpy.data.objects.get(rig_name)
    var.targets[0].bone_target = bone_name
    var.targets[0].transform_type = 'ROT_X'
    var.targets[0].transform_space = 'LOCAL_SPACE'
    drv.expression = f"min(max((r-({lo}))/(({hi})-({lo})),0),1)"
    return {"corrective": key_name}
```

---

## 🔗 СВЯЗИ
- **Промпты:** [P20 Shape Keys](./20_shape_keys.md), [P17 Rigify](./17_rigify_setup.md)
- **Следующий:** [P35: MCP Error Recovery](./35_mcp_error_recovery.md)
