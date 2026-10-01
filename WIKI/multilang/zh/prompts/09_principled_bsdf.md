---
id: 09_principled_bsdf
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: human
---
# P09：PRINCIPLED BSDF 设置

**ID:** P09 | **类别:** Materials PBR | **提示词:** ⭐ | **Tags:** #materials #pbr #principled-bshf #shader-nodes

---

## 🎯 目标
创建并配置带完整 PBR 贴图集的 Principled BSDF 材质

---

## 📝 提示词

```
创建 "[MAT_NAME]" 材质，类型 Principled BSDF:
Base Color: [R, G, B] 或 hex #RRGGBB
Roughness: [0.0-1.0]
Metallic: [0.0-1.0]
[可选] Transmission, IOR, Clearcoat, Sheen, Emission
指定给对象 "[OBJECT_NAME]"
```

---

## 🔧 MCP: `set_material`（基础）

```json
{
  "type": "set_material",
  "params": {
    "object_name": "Cube",
    "material_name": "Mat_Red",
    "color": [1.0, 0.0, 0.0, 1.0]
  }
}
```

---

## 🔧 MCP: `execute_blender_code`（完整 PBR）

```python
import bpy
from pathlib import Path

def create_pbr_material(name, maps_dict, obj_name=None):
    """
    maps_dict keys: 'base_color', 'roughness', 'metallic', 'normal', 'height', 'ao', 'emission'
    values: 文件路径或颜色元组 (R,G,B,A)
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Principled BSDF
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)

    # Material Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    # Displacement
    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (200, -200)
    links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
    mat.displacement_method = 'BOTH'

    # Texture Coordinate + Mapping
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    def add_texture(key, input_name, colorspace='sRGB', use_normal_map=False, use_disp=False):
        if key not in maps_dict:
            return
        val = maps_dict[key]

        if isinstance(val, (tuple, list)):  # 颜色
            principled.inputs[input_name].default_value = val + (1.0,) if len(val)==3 else val
            return

        # 图像文件
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(val))
        tex.image.colorspace_settings.name = colorspace
        tex.location = (-200, 0)
        links.new(mapping.outputs['Vector'], tex.inputs['Vector'])

        if use_normal_map:
            nmap = nodes.new('ShaderNodeNormalMap')
            nmap.location = (0, -100)
            links.new(tex.outputs['Color'], nmap.inputs['Color'])
            links.new(nmap.outputs['Normal'], principled.inputs[input_name])
        elif use_disp:
            links.new(tex.outputs['Color'], disp.inputs['Height'])
        else:
            links.new(tex.outputs['Color'], principled.inputs[input_name])

    # 连接贴图
    add_texture('base_color', 'Base Color', 'sRGB')
    add_texture('roughness', 'Roughness', 'Non-Color')
    add_texture('metallic', 'Metallic', 'Non-Color')
    add_texture('normal', 'Normal', 'Non-Color', use_normal_map=True)
    add_texture('height', 'Height', 'Non-Color', use_disp=True)
    add_texture('emission', 'Emission Color', 'sRGB')

    # AO -> 与 Base Color 混合
    if 'ao' in maps_dict:
        ao_tex = nodes.new('ShaderNodeTexImage')
        ao_tex.image = bpy.data.images.load(str(maps_dict['ao']))
        ao_tex.image.colorspace_settings.name = 'Non-Color'
        ao_tex.location = (-200, 200)
        links.new(mapping.outputs['Vector'], ao_tex.inputs['Vector'])

        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.location = (0, 100)
        # 通过 Mix 重连 Base Color
        if principled.inputs['Base Color'].links:
            from_node = principled.inputs['Base Color'].links[0].from_node
            from_socket = principled.inputs['Base Color'].links[0].from_socket
            links.new(from_socket, mix.inputs[1])
        links.new(ao_tex.outputs['Color'], mix.inputs[2])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])

    # 指定给对象
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

    return mat

# === 使用示例 ===

# 1. 纯色
create_pbr_material("Mat_Red", {
    'base_color': (1.0, 0.2, 0.2, 1.0),
    'roughness': 0.5,
    'metallic': 0.0
}, "Cube")

# 2. 金色
create_pbr_material("Mat_Gold", {
    'base_color': (1.0, 0.843, 0.0, 1.0),
    'roughness': 0.1,
    'metallic': 1.0
}, "Ring")

# 3. 玻璃
create_pbr_material("Mat_Glass", {
    'base_color': (1.0, 1.0, 1.0, 1.0),
    'roughness': 0.0,
    'transmission': 1.0,  # 需要时加到函数中
    'ior': 1.45
}, "Glass_Obj")

# 4. 来自文件的完整 PBR
create_pbr_material("Mat_Brick", {
    'base_color': Path("//textures/brick_basecolor.png"),
    'roughness': Path("//textures/brick_roughness.png"),
    'normal': Path("//textures/brick_normal.png"),
    'height': Path("//textures/brick_height.png"),
    'ao': Path("//textures/brick_ao.png"),
}, "Wall")
```

---

## 📊 PBR 参数速查

| 材质 | Base Color | Roughness | Metallic | Transmission | IOR | Clearcoat |
|----------|------------|-----------|----------|--------------|-----|-----------|
| **塑料** | 颜色 | 0.3-0.5 | 0.0 | 0.0 | 1.5 | 0.0 |
| **金属（抛光）** | 金属色 | 0.05-0.15 | 1.0 | 0.0 | — | 0.0 |
| **金属（锈蚀/哑光）** | 金属色 | 0.6-0.9 | 1.0 | 0.0 | — | 0.0 |
| **玻璃** | 白色 | 0.0 | 0.0 | 1.0 | 1.45-1.5 | 0.0 |
| **水** | 浅蓝 | 0.05 | 0.0 | 1.0 | 1.33 | 0.0 |
| **皮肤** | 肤色 | 0.6-0.8 | 0.0 | 0.0 | 1.5 | 0.1-0.3 |
| **布料** | 布色 | 0.8-1.0 | 0.0 | 0.0 | 1.5 | 0.0 |
| **陶瓷** | 颜色 | 0.1-0.3 | 0.0 | 0.0 | 1.5 | 0.2-0.5 |
| **石头/混凝土** | 灰/米 | 0.7-1.0 | 0.0 | 0.0 | 1.5 | 0.0 |
| **木材** | 木色 | 0.6-0.9 | 0.0 | 0.0 | 1.5 | 0.0 |

---

## 🎨 特殊效果

### Emission（发光）
```python
principled.inputs['Emission Color'].default_value = (1.0, 0.8, 0.2, 1.0)  # 暖光
principled.inputs['Emission Strength'].default_value = 5.0  # 强度
```

### Clearcoat（清漆/陶瓷）
```python
principled.inputs['Coat Weight'].default_value = 1.0
principled.inputs['Coat Roughness'].default_value = 0.03
```

### Sheen（布料/丝绒）
```python
principled.inputs['Sheen Weight'].default_value = 0.5
principled.inputs['Sheen Roughness'].default_value = 0.3
principled.inputs['Sheen Tint'].default_value = 0.5
```

### Subsurface（皮肤、蜡、大理石）
```python
principled.inputs['Subsurface Weight'].default_value = 0.3
principled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # RGB 穿透半径
principled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)
```

### Anisotropic（拉丝表面）
```python
principled.inputs['Anisotropic'].default_value = 0.8
principled.inputs['Anisotropic Rotation'].default_value = 0.25  # 90°
# 需要 Tangent 输入（UV 或 Geometry > Tangent）
```

---

## 🔗 СВЯЗИ

- **案例:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **工作流:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **提示词:** [P10 Node Groups](./10_node_groups.md), [P11 Procedural Textures](./11_procedural_textures.md)
- **MCP 工具:** `set_material`（基础），`execute_blender_code`（完整）
- **下一个:** [P10: Node Group Creation](./10_node_groups.md)
