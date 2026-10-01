---
id: 12_texture_painting
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P12: TEXTURE PAINTING

> Цель: ## 🌍 MULTILANG

**ID:** 12_texture_painting | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, baking, brushes, layers, pbr, texture, texture-paint

---

# P12: TEXTURE PAINTING

**ID:** P12 | **Cluster:** Materials PBR | **Difficulty:** ⭐⭐ | **Tags:** #texture-paint #layers #brushes #baking #pbr

---

## 🎯 GOAL
Hand-paint PBR textures directly on 3D models using Blender's Texture Paint mode with layer system

---

## 📝 PROMPT (RUS)

```
Настрой Texture Paint для "[OBJECT_NAME]":
Слои: BASE_COLOR, ROUGHNESS, METALLIC, NORMAL, HEIGHT
Кисти: DRAW, SOFTEN, SMEAR, CLONE, FILL, MASK
Маска: по вертекс-группам / по UV / по Cavity
Экспорт: все карты в папку //textures/
```

---

## 📝 PROMPT (ENG)

```
Setup Texture Paint for "[OBJECT_NAME]":
Layers: BASE_COLOR, ROUGHNESS, METALLIC, NORMAL, HEIGHT
Brushes: DRAW, SOFTEN, SMEAR, CLONE, FILL, MASK
Mask: by vertex groups / by UV / by Cavity
Export: all maps to //textures/ folder
```

---

## 🔧 MCP: `execute_blender_code`

### SETUP TEXTURE PAINT LAYERS
```python
import bpy

obj = bpy.data.objects.get("Target_Mesh")
if not obj or obj.type != 'MESH':
    raise ValueError("Mesh object required")

# Убедиться в UV
if not obj.data.uv_layers:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')

# Создать изображения для слоёв
def create_paint_image(name, width=2048, height=2048, color=(0,0,0,0), float_buffer=False):
    img = bpy.data.images.new(name, width, height, alpha=True, float_buffer=float_buffer)
    pixels = [color[0], color[1], color[2], color[3]] * (width * height)
    img.pixels = pixels
    return img

# Слои PBR
base_color_img = create_paint_image("Tex_BaseColor", color=(0.5, 0.5, 0.5, 1))
roughness_img = create_paint_image("Tex_Roughness", color=(0.5, 0.5, 0.5, 1), float_buffer=True)
metallic_img = create_paint_image("Tex_Metallic", color=(0.0, 0.0, 0.0, 1), float_buffer=True)
normal_img = create_paint_image("Tex_Normal", color=(0.5, 0.5, 1.0, 1))
height_img = create_paint_image("Tex_Height", color=(0.5, 0.5, 0.5, 1), float_buffer=True)

# Материал с Texture Paint слоями
mat = bpy.data.materials.new("Mat_Paint")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.location = (0, 0)
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Texture nodes для каждого слоя
def add_paint_texture(img, label, location):
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.label = label
    tex.location = location
    tex.interpolation = 'Linear'
    return tex

tex_base = add_paint_texture(base_color_img, "PAINT_BaseColor", (-400, 300))
tex_rough = add_paint_texture(roughness_img, "PAINT_Roughness", (-400, 100))
tex_metal = add_paint_texture(metallic_img, "PAINT_Metallic", (-400, -100))
tex_norm = add_paint_texture(normal_img, "PAINT_Normal", (-400, -300))

links.new(tex_base.outputs['Color'], principled.inputs['Base Color'])
links.new(tex_rough.outputs['Color'], principled.inputs['Roughness'])
links.new(tex_metal.outputs['Color'], principled.inputs['Metallic'])

# Normal Map
normal_map = nodes.new('ShaderNodeNormalMap')
normal_map.location = (200, -300)
links.new(tex_norm.outputs['Color'], normal_map.inputs['Color'])
links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])

# Назначить материал
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Переключить в Texture Paint mode
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='TEXTURE_PAINT')

# Настроить слои для рисования
tool_settings = bpy.context.scene.tool_settings
tool_settings.unified_paint_settings.use_unified_size = True
tool_settings.unified_paint_settings.size = 50
tool_settings.unified_paint_settings.use_unified_strength = True
tool_settings.unified_paint_settings.strength = 0.5

print("Texture Paint ready! Layers: BaseColor, Roughness, Metallic, Normal")
```

### BRUSH PRESETS
```python
import bpy

# Создать кисти для PBR
def create_brush(name, brush_type, strength=0.5, radius=50, blend='MIX', use_color=True):
    brush = bpy.data.brushes.new(name)
    brush.brush_type = brush_type
    brush.strength = strength
    brush.size = radius
    brush.blend = blend
    if use_color:
        brush.color = (0.8, 0.8, 0.8)
    return brush

# Base Color кисти
create_brush("Paint_Draw", 'DRAW', strength=0.5, radius=80)
create_brush("Paint_Soften", 'SOFTEN', strength=0.3, radius=100)
create_brush("Paint_Smear", 'SMEAR', strength=0.4, radius=80)
create_brush("Paint_Clone", 'CLONE', strength=1.0, radius=50)
create_brush("Paint_Fill", 'FILL', strength=1.0, radius=200)

# Mask кисти
create_brush("Mask_Draw", 'MASK', strength=1.0, radius=80, use_color=False)
create_brush("Mask_Blur", 'MASK', strength=0.3, radius=100, use_color=False)
```

### MASKING TECHNIQUES
```python
# Маска по Cavity (полости)
bpy.ops.paint.mask_cavity()

# Маска по вертекс-группам
obj.vertex_groups.new(name="Paint_Mask")
# Назначить веса в Weight Paint mode

# Маска по UV (Edge Mask)
bpy.ops.paint.mask_by_attribute(attribute_name="uv_edge")

# Инверсия маски
bpy.ops.paint.mask_invert()
```

### EXPORT ALL MAPS
```python
import os

export_dir = "//textures/"
os.makedirs(bpy.path.abspath(export_dir), exist_ok=True)

for img in [base_color_img, roughness_img, metallic_img, normal_img, height_img]:
    filepath = os.path.join(export_dir, img.name + ".png")
    img.filepath_raw = filepath
    img.file_format = 'PNG'
    img.save()

print("Exported to:", bpy.path.abspath(export_dir))
```

---

## 📊 LAYER WORKFLOW

| Слой | Image Format | Color Space | Paint Mode | Blend |
|------|--------------|-------------|------------|-------|
| Base Color | PNG 8-bit | sRGB | Color | MIX |
| Roughness | PNG 8-bit | Non-Color | Value | MIX |
| Metallic | PNG 8-bit | Non-Color | Value | MIX |
| Normal | PNG 8-bit | Non-Color | Color (RGB=Normal) | MIX |
| Height | PNG 16/32-bit | Non-Color | Value | MIX |

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| Используй `float_buffer=True` для Roughness/Metallic/Height | Точность значений 0-1 |
| Включи `Unified Paint Settings` | Единые размер/сила для всех кистей |
| Рисуй на Low-poly с Multires | Детали без лагов |
| Используй Stencil для текстур | Точное размещение деталей |
| Сохраняй каждые 5 мин | `Image > Save` или `Alt+S` |

---

## 🔗 LINKS

- **Prompts:** [P09 Principled BSDF](./09_principled_bsdf.md), [P11 Procedural Textures](./11_procedural_textures.md)
- **Workflows:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **Cases:** [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **Next:** [P13: Lighting & HDRI](./13_lighting_hdri.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/12_texture_painting.md` |
| Russian | `multilang/ru/prompts/12_texture_painting.md` |