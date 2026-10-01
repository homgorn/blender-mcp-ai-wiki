---
id: 02_boolean_operations
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human
---
# P02：布尔运算

**ID:** P02 | **类别:** Geometry Basics | **难度:** ⭐⭐ | **标签:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 目标
通过 MCP 在对象间执行布尔运算（Difference、Union、Intersect）

---

## 📝 提示词

```
在 "[OBJECT_A]"（基础）和 "[OBJECT_B]"（工具）之间执行布尔运算 [OPERATION]。
运算：DIFFERENCE（相减）、UNION（合并）、INTERSECT（相交）。
结果：对象 A 被修改，对象 B 可以删除。
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# 设置
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# 确保 OBJECT 模式
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# 选择对象
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# 添加布尔修改器
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 简单几何用 'FAST'

# 应用
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# 删除工具对象（可选）
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 运算类型

| 运算 | 可视结果 | 用例 |
|------|----------|------|
| **DIFFERENCE** | A 减 B | 门窗、开孔、凹槽 |
| **UNION** | A 加 B | 合并部件、融合网格 |
| **INTERSECT** | 仅相交部分 | 遮罩、形状裁剪 |

---

## 💡 高级模式

### 多个布尔（一次完成）
```python
# 一次多个相减
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# 全部应用
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# 清理
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### 注意法线
```python
# 布尔运算前检查并修复法线
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 结果为空 | 法线内外反了 | `Mesh > Normals > Recalculate Outside` |
| 几何伪影 | 非流形边 | `Select > Select All by Trait > Non-Manifold` → 修复 |
| 复杂网格很慢 | 面数太多 | 先用 `DECIMATE`，或用 `FAST` solver |
| 对象消失 | 相交为空 | 检查对象位置 |

---

## 🔗 相关链接

- **案例:** [Case 01: ArchViz Interior](../cases/case_01_archviz_interior.md) — 墙体门窗
- **工作流:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **相关提示词:** [P01 Primitives](./01_geometry_basics.md), [P03 Modifiers Stack](./03_modifiers_stack.md)
- **下一个:** [P03: Modifiers Stack](./03_modifiers_stack.md)
