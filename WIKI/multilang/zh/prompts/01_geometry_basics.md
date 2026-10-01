---
id: 01_geometry_basics
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: human
---
# P01：基础体素创建

**ID:** P01 | **类别:** Geometry Basics | **难度:** ⭐ | **标签:** #geometry #primitives #basics #bpy.ops

---

## 🎯 目标
通过 MCP 创建基础体素，精确控制参数

---

## 📝 提示词

```
创建名为 "[NAME]" 的 [TYPE] 体素，位置 [X, Y, Z]，
缩放 [SX, SY, SZ]，旋转 [RX, RY, RZ]（弧度）。

类型: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT

示例: "在 (2, 0, 1) 创建立方体 'Box_01'，缩放 (1, 2, 1)，旋转 (0, 0, 0.785)"
```

---

## 🔧 MCP 工具: `create_object`

```json
{
  "type": "create_object",
  "params": {
    "entity_type": "CUBE",
    "name": "Box_01",
    "location": [2.0, 0.0, 1.0],
    "rotation": [0.0, 0.0, 0.785],
    "scale": [1.0, 2.0, 1.0]
  }
}
```

---

## 📊 各类型参数

| 类型 | 必需 | 可选 |
|------|------|------|
| CUBE | size | location, rotation, scale |
| SPHERE | radius | segments, ring_count, location, rotation, scale |
| CYLINDER | radius, depth | vertices, cap_ends, location, rotation, scale |
| PLANE | size | location, rotation, scale |
| CONE | radius1, radius2, depth | vertices, location, rotation, scale |
| TORUS | major_radius, minor_radius | major_segments, minor_segments, location, rotation, scale |
| EMPTY | — | location, rotation, scale, type |
| CAMERA | — | location, rotation, lens, sensor_width |
| LIGHT | — | location, rotation, type, energy, color |

---

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `Object not found` | 名称被占用 | 用唯一名称或检查 `get_scene_info` |
| `Invalid rotation` | 用了角度而非弧度 | 换算: `radians = degrees * π / 180` |
| `Primitive not created` | 上下文是 EDIT 模式 | 始终保持 OBJECT 模式 |

---

## 🔗 相关链接

- **案例:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **工作流:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **下一个:** [P02: Boolean Operations](./02_boolean_operations.md)
