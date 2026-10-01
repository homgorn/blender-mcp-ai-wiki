---
id: 09_principled_bsdf
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P09: PRINCIPLED BSDF SETUP

> Goal: ## 🌍 MULTILANG

**ID:** 09_principled_bsdf | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** **, materials, pbr, principled, principled-bshf, rrggbb, shader, shader-nodes

---

# P09: PRINCIPLED BSDF SETUP

**ID:** P09 | **Кластер:** Materials PBR | **Сложность:** ⭐ | **Теги:** #materials #pbr #principled-bshf #shader-nodes

---

## 🎯 ЦЕЛЬ
Создание и настройка Principled BSDF материала с полным набором PBR карт

---

## 📝 ПРОМПТ (РУС)

```
Создай материал "[MAT_NAME]" типа Principled BSDF:
Base Color: [R, G, B] или hex #RRGGBB
Roughness: [0.0-1.0]
Metallic: [0.0-1.0]
[Optional] Transmission, IOR, Clearcoat, Sheen, Emission
Присвой к объекту "[OBJECT_NAME]"
```

---

## 📝 ПРОМПТ (ENG)

```
Create material "[MAT_NAME]" with Principled BSDF:
Base Color: [R, G, B] or hex #RRGGBB
Roughness: [0.0-1.0]
Metallic: [0.0-1.0]
[Optional] Transmission, IOR, Clearcoat, Sheen, Emission
Assign to object "[OBJECT_NAME]"
```

---

## 🔧 MCP: `set_material` (базовый)

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

## 🔧 MCP: `execute_blender_code` (полный PBR)

```python
import bpy
from pathlib import Path

def create_pbr_material(name, maps_dict, obj_name=None):
    """
    maps_dict keys: 'base_color', 'roughness', 'metallic', 'normal', 'height', 'ao', 'emission'
    values: filepath или Color tuple (R,G,B,A)
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
        
        if isinstance(val, (tuple, list)):  # Color
            principled.inputs[input_name].default_value = val + (1.0,) if len(val)==3 else val
            return
        
        # Image file
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
    
    # Подключить карты
    add_texture('base_color', 'Base Color', 'sRGB')
    add_texture('roughness', 'Roughness', 'Non-Color')
    add_texture('metallic', 'Metallic', 'Non-Color')
    add_texture('normal', 'Normal', 'Non-Color', use_normal_map=True)
    add_texture('height', 'Height', 'Non-Color', use_disp=True)
    add_texture('emission', 'Emission Color', 'sRGB')
    
    # AO -> Mix с Base Color
    if 'ao' in maps_dict:
        ao_tex = nodes.new('ShaderNodeTexImage')
        ao_tex.image = bpy.data.images.load(str(maps_dict['ao']))
        ao_tex.image.colorspace_settings.name = 'Non-Color'
        ao_tex.location = (-200, 200)
        links.new(mapping.outputs['Vector'], ao_tex.inputs['Vector'])
        
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.location = (0, 100)
        # Переподключить Base Color через Mix
        if principled.inputs['Base Color'].links:
            from_node = principled.inputs['Base Color'].links[0].from_node
            from_socket = principled.inputs['Base Color'].links[0].from_socket
            links.new(from_socket, mix.inputs[1])
        links.new(ao_tex.outputs['Color'], mix.inputs[2])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    
    # Назначить объекту
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
    
    return mat

# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

# 1. Простой цвет
create_pbr_material("Mat_Red", {
    'base_color': (1.0, 0.2, 0.2, 1.0),
    'roughness': 0.5,
    'metallic': 0.0
}, "Cube")

# 2. Золото
create_pbr_material("Mat_Gold", {
    'base_color': (1.0, 0.843, 0.0, 1.0),
    'roughness': 0.1,
    'metallic': 1.0
}, "Ring")

# 3. Стекло
create_pbr_material("Mat_Glass", {
    'base_color': (1.0, 1.0, 1.0, 1.0),
    'roughness': 0.0,
    'transmission': 1.0,  # нужно добавить в функцию
    'ior': 1.45
}, "Glass_Obj")

# 4. Полный PBR из файлов
create_pbr_material("Mat_Brick", {
    'base_color': Path("//textures/brick_basecolor.png"),
    'roughness': Path("//textures/brick_roughness.png"),
    'normal': Path("//textures/brick_normal.png"),
    'height': Path("//textures/brick_height.png"),
    'ao': Path("//textures/brick_ao.png"),
}, "Wall")
```

---

## 📊 PBR ПАРАМЕТРЫ ШПАРГАЛКА

| Материал | Base Color | Roughness | Metallic | Transmission | IOR | Clearcoat |
|----------|------------|-----------|----------|--------------|-----|-----------|
| **Пластик** | Цвет | 0.3-0.5 | 0.0 | 0.0 | 1.5 | 0.0 |
| **Металл (полированный)** | Цвет металла | 0.05-0.15 | 1.0 | 0.0 | — | 0.0 |
| **Металл (ржавый/матовый)** | Цвет металла | 0.6-0.9 | 1.0 | 0.0 | — | 0.0 |
| **Стекло** | Белый | 0.0 | 0.0 | 1.0 | 1.45-1.5 | 0.0 |
| **Вода** | Голубой | 0.05 | 0.0 | 1.0 | 1.33 | 0.0 |
| **Кожа** | Кожаный цвет | 0.6-0.8 | 0.0 | 0.0 | 1.5 | 0.1-0.3 |
| **Ткань** | Цвет ткани | 0.8-1.0 | 0.0 | 0.0 | 1.5 | 0.0 |
| **Керамика** | Цвет | 0.1-0.3 | 0.0 | 0.0 | 1.5 | 0.2-0.5 |
| **Камень/Бетон** | Серый/бежевый | 0.7-1.0 | 0.0 | 0.0 | 1.5 | 0.0 |
| **Дерево** | Деревянный | 0.6-0.9 | 0.0 | 0.0 | 1.5 | 0.0 |

---

## 🎨 СПЕЦИАЛЬНЫЕ ЭФФЕКТЫ

### Emission (Свечение)
```python
principled.inputs['Emission Color'].default_value = (1.0, 0.8, 0.2, 1.0)  # Тёплый свет
principled.inputs['Emission Strength'].default_value = 5.0  # Сила
```

### Clearcoat (Лак/Керамика)
```python
principled.inputs['Coat Weight'].default_value = 1.0
principled.inputs['Coat Roughness'].default_value = 0.03
```

### Sheen (Ткань/Велюр)
```python
principled.inputs['Sheen Weight'].default_value = 0.5
principled.inputs['Sheen Roughness'].default_value = 0.3
principled.inputs['Sheen Tint'].default_value = 0.5
```

### Subsurface (Кожа, воск, мрамор)
```python
principled.inputs['Subsurface Weight'].default_value = 0.3
principled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # RGB радиус проникновения
principled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)
```

### Anisotropic (Поверхности с насечкой)
```python
principled.inputs['Anisotropic'].default_value = 0.8
principled.inputs['Anisotropic Rotation'].default_value = 0.25  # 90°
# Нужен Tangent вход (UV или Geometry > Tangent)
```

---

## 🔗 СВЯЗИ

- **Кейсы:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **Воркфлоу:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **Промпты:** [P10 Node Groups](./10_node_groups.md), [P11 Procedural Textures](./11_procedural_textures.md)
- **MCP Tool:** `set_material` (базовый), `execute_blender_code` (полный)
- **Следующий:** [P10: Node Group Creation](./10_node_groups.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/prompts/09_principled_bsdf.md` |
| Русский | `multilang/ru/prompts/09_principled_bsdf.md` |