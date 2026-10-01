---
lang: en
---
# P10: NODE GROUP CREATION

**ID:** P10 | **Cluster:** Materials PBR | **Difficulty:** ⭐⭐ | **Tags:** #node-groups #reuse #shader-library #procedural

---

## 🎯 GOAL
Create reusable shader node groups for consistent material library and procedural effects

---

## 📝 PROMPT (RUS)

```
Создай Node Group "[GROUP_NAME]" с входами/выходами:
Inputs: [список: имя, тип, дефолт, min, max]
Outputs: [список: имя, тип]
Внутренняя логика: [описание нод]
Использование: в материалах через Group Node
```

---

## 📝 PROMPT (ENG)

```
Create Node Group "[GROUP_NAME]" with inputs/outputs:
Inputs: [list: name, type, default, min, max]
Outputs: [list: name, type]
Internal logic: [node description]
Usage: in materials via Group Node
```

---

## 🔧 MCP: `execute_blender_code`

### БАЗОВЫЙ ШАБЛОН
```python
import bpy

def create_node_group(name, inputs_def, outputs_def, build_func):
    """
    inputs_def: [("Name", "NodeSocketFloat", default, min, max), ...]
    outputs_def: [("Name", "NodeSocketFloat"), ...]
    build_func: function(nodes, links, input_node, output_node)
    """
    # Удалить старую если есть
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    
    ng = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    nodes = ng.nodes
    links = ng.links
    nodes.clear()
    
    # Input/Output ноды
    inp = nodes.new('NodeGroupInput')
    inp.location = (-400, 0)
    out = nodes.new('NodeGroupOutput')
    out.location = (400, 0)
    
    # Создать сокеты
    for sock_def in inputs_def:
        sock_name, sock_type, default, min_val, max_val = sock_def
        sock = ng.interface.new_socket(name=sock_name, in_out='INPUT', socket_type=sock_type)
        sock.default_value = default
        sock.min_value = min_val
        sock.max_value = max_val
    
    for sock_def in outputs_def:
        sock_name, sock_type = sock_def
        ng.interface.new_socket(name=sock_name, in_out='OUTPUT', socket_type=sock_type)
    
    # Построить логику
    build_func(nodes, links, inp, out)
    
    return ng

# === ПРИМЕРЫ ===

# 1. PBR UTILITY GROUP (Универсальный PBR)
def build_pbr_utility(nodes, links, inp, out):
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    links.new(inp.outputs['Base Color'], principled.inputs['Base Color'])
    links.new(inp.outputs['Roughness'], principled.inputs['Roughness'])
    links.new(inp.outputs['Metallic'], principled.inputs['Metallic'])
    links.new(inp.outputs['Normal'], principled.inputs['Normal'])
    links.new(inp.outputs['Height'], principled.inputs['Displacement'])
    links.new(principled.outputs['BSDF'], out.inputs['BSDF'])
    links.new(principled.outputs['Alpha'], out.inputs['Alpha'])

pbr_inputs = [
    ("Base Color", "NodeSocketColor", (0.8, 0.8, 0.8, 1.0), 0, 1),
    ("Roughness", "NodeSocketFloat", 0.5, 0, 1),
    ("Metallic", "NodeSocketFloat", 0.0, 0, 1),
    ("Normal", "NodeSocketVector", (0, 0, 1), -1, 1),
    ("Height", "NodeSocketFloat", 0, -1, 1),
]
pbr_outputs = [("BSDF", "NodeSocketShader"), ("Alpha", "NodeSocketFloat")]

create_node_group("PBR_Utility", pbr_inputs, pbr_outputs, build_pbr_utility)

# 2. EDGE WEAR GROUP (Потертости по краям)
def build_edge_wear(nodes, links, inp, out):
    # Geometry > Pointiness
    geom = nodes.new('ShaderNodeNewGeometry')
    geom.location = (-200, 200)
    
    # Color Ramp для контроля
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 200)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)  # Чёрный в углублениях
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)  # Белый на краях
    
    links.new(geom.outputs['Pointiness'], ramp.inputs['Fac'])
    
    # Mix с Base Color
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.location = (200, 0)
    links.new(ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(inp.outputs['Base Color'], mix.inputs[1])
    links.new(inp.outputs['Edge Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], out.inputs['Color'])

edge_inputs = [
    ("Base Color", "NodeSocketColor", (0.8, 0.8, 0.8, 1), 0, 1),
    ("Edge Color", "NodeSocketColor", (0.1, 0.1, 0.1, 1), 0, 1),
]
edge_outputs = [("Color", "NodeSocketColor")]

create_node_group("Edge_Wear", edge_inputs, edge_outputs, build_edge_wear)

# 3. PROCEDURAL RUST/LEAKS
def build_rust_leaks(nodes, links, inp, out):
    # Noise Texture для ржавчины
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-200, 200)
    noise.noise_dimensions = '3D'
    noise.scale = 50
    noise.detail = 8
    
    # Color Ramp для распределения
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 200)
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0, 0, 0, 0)  # Прозрачный
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.6, 0.2, 0.05, 1)  # Ржавый
    
    # Mix с Base Color
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MIX'
    mix.location = (200, 0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(inp.outputs['Base Color'], mix.inputs[1])
    links.new(inp.outputs['Rust Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], out.inputs['Color'])

rust_inputs = [
    ("Base Color", "NodeSocketColor", (0.8, 0.8, 0.8, 1), 0, 1),
    ("Rust Color", "NodeSocketColor", (0.6, 0.2, 0.05, 1), 0, 1),
    ("Scale", "NodeSocketFloat", 50, 1, 500),
]
rust_outputs = [("Color", "NodeSocketColor")]

create_node_group("Procedural_Rust", rust_inputs, rust_outputs, build_rust_leaks)

# 4. PARALLAX / INTERIOR MAPPING
def build_parallax(nodes, links, inp, out):
    # UV Offset на основе View Direction
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)
    
    # Vector Math для параллакса
    view_dir = nodes.new('ShaderNodeNewGeometry')
    view_dir.location = (-400, -200)
    
    # Сложная логика здесь...
    # См. полные примеры в библиотеках
    pass

print("Node groups created!")
```

---

## 📊 ТИПЫ СОКЕТОВ

| Тип | Socket Type | Пример |
|-----|-------------|--------|
| Float | `NodeSocketFloat` | Roughness, Scale |
| Color | `NodeSocketColor` | Base Color, Emission |
| Vector | `NodeSocketVector` | Normal, Tangent |
| Shader | `NodeSocketShader` | BSDF Output |
| Boolean | `NodeSocketBool` | Toggle |
| Integer | `NodeSocketInt` | Count, Seed |

---

## 💡 BEST PRACTICES

| Практика | Почему |
|----------|--------|
| Группировать по функциям | Переиспользование |
| Документировать сокеты | Навигация в узлах |
| Версионировать (`Name_v001`) | Совместимость |
| Тестировать в изоляции | Отладка |
| Публиковать в Asset Browser | Доступ в любой сцене |

---

## 🔗 LINKS

- **Prompts:** [P09 Principled BSDF](./09_principled_bsdf.md), [P11 Procedural Textures](./11_procedural_textures.md)
- **Workflows:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **Cases:** [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **Next:** [P11: Procedural Textures](./11_procedural_textures.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/materials/10_node_groups.md` |
| Russian | `multilang/ru/materials/10_node_groups.md` |