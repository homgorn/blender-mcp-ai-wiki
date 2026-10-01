---
lang: ru
orig_lang: en
translation: ai
---
# СПРАВОЧНИК ПО API МАТЕРИАЛОВ BLENDER

## Principled BSDF (стандартный PBR)

### Входные сокеты
```python
principled = nodes["Principled BSDF"]

# Базовый слой
principled.inputs['Base Color'].default_value        # RGBA (0-1)
principled.inputs['Subsurface'].default_value        # Float (0-1)
principled.inputs['Subsurface Radius'].default_value # RGB
principled.inputs['Subsurface Color'].default_value  # RGBA
principled.inputs['Subsurface IOR'].default_value    # Float
principled.inputs['Subsurface Anisotropy'].default_value # Float

# Металлик
principled.inputs['Metallic'].default_value          # Float (0-1)
principled.inputs['Specular'].default_value          # Float (0-1)
principled.inputs['Specular Tint'].default_value     # Float (0-1)

# Шероховатость
principled.inputs['Roughness'].default_value         # Float (0-1)
principled.inputs['Anisotropic'].default_value       # Float (0-1)
principled.inputs['Anisotropic Rotation'].default_value # Float (0-1)

# Transmission (стекло)
principled.inputs['Transmission'].default_value      # Float (0-1)
principled.inputs['Transmission Roughness'].default_value # Float

# Coat (лаковое покрытие)
principled.inputs['Coat Weight'].default_value       # Float (0-1)
principled.inputs['Coat Roughness'].default_value    # Float (0-1)

# Sheen (ткань)
principled.inputs['Sheen Weight'].default_value      # Float (0-1)
principled.inputs['Sheen Roughness'].default_value   # Float (0-1)
principled.inputs['Sheen Tint'].default_value        # Float (0-1)

# Излучение
principled.inputs['Emission Color'].default_value    # RGBA
principled.inputs['Emission Strength'].default_value # Float

# Alpha
principled.inputs['Alpha'].default_value             # Float (0-1)

# Normal
principled.inputs['Normal'].default_value            # Vector (из Normal Map)
principled.inputs['Clearcoat Normal'].default_value  # Vector

# Tangent
principled.inputs['Tangent'].default_value           # Vector (для Anisotropic)
```

### Выходные сокеты
```python
principled.outputs['BSDF']      # Shader (в Material Output)
principled.outputs['Alpha']     # Float (для прозрачности)
```

---

## Полная настройка PBR-материала

### По картам текстур
```python
def create_pbr_material(name, maps, obj=None):
    """maps: словарь с ключами: base_color, roughness, normal, metallic, height, ao, emission"""
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
    
    # Displacement output (для height)
    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (200, -200)
    links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
    mat.displacement_method = 'BOTH'
    
    # Texture Coordinate + Mapping (для всех текстур)
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    def add_texture(map_key, input_name, colorspace='sRGB', use_normal_map=False, use_disp=False):
        if map_key not in maps:
            return
        img = maps[map_key]
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = img
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
    add_texture('ao', 'Base Color', 'Non-Color')  # AO смешивается отдельно
    add_texture('emission', 'Emission Color', 'sRGB')
    
    # Смешивание AO (умножение с Base Color)
    if 'ao' in maps:
        ao_tex = nodes.new('ShaderNodeTexImage')
        ao_tex.image = maps['ao']
        ao_tex.image.colorspace_settings.name = 'Non-Color'
        ao_tex.location = (-200, 200)
        links.new(mapping.outputs['Vector'], ao_tex.inputs['Vector'])
        
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.location = (0, 100)
        links.new(principled.inputs['Base Color'].links[0].from_node.outputs['Color'], mix.inputs[1])
        links.new(ao_tex.outputs['Color'], mix.inputs[2])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    
    # Назначить объекту
    if obj:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    
    return mat
```

---

## Справочник типов нод

### Текстурные ноды
```python
# Image Texture
tex = nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load("path.png")
tex.projection = 'FLAT'  # 'BOX', 'SPHERE', 'TUBE'
tex.interpolation = 'Linear'  # 'Closest', 'Cubic', 'Smart'

# Environment Texture (HDRI)
env = nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load("hdri.exr")
env.projection = 'EQUIRECTANGULAR'

# Процедурные текстуры
noise = nodes.new('ShaderNodeTexNoise')
noise.noise_dimensions = '4D'
noise.noise_type = 'FBM'

voronoi = nodes.new('ShaderNodeTexVoronoi')
voronoi.feature = 'SMOOTH_F1'  # 'F1', 'F2', 'SMOOTH_F1', 'DISTANCE_TO_EDGE'
voronoi.metric = 'MANHATTAN'  # 'EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI'

musgrave = nodes.new('ShaderNodeTexMusgrave')
musgrave.musgrave_dimensions = '3D'
musgrave.musgrave_type = 'MULTIFRACTAL'

magic = nodes.new('ShaderNodeTexMagic')
wave = nodes.new('ShaderNodeTexWave')
wave.wave_type = 'SINE'  # 'SAW', 'TRI'

brick = nodes.new('ShaderNodeTexBrick')
checker = nodes.new('ShaderNodeTexChecker')
gradient = nodes.new('ShaderNodeTexGradient')
gradient.gradient_type = 'LINEAR'  # 'QUADRATIC', 'EASING', 'DIAGONAL', 'RADIAL', 'QUADRATIC_SPHERE'
```

### Цветовые ноды
```python
# Mix RGB
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'  # 'MULTIPLY', 'SCREEN', 'OVERLAY', 'SOFT_LIGHT', 'HARD_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'HUE', 'SATURATION', 'VALUE', 'COLOR'

# Color Ramp
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.interpolation = 'LINEAR'  # 'CONSTANT', 'EASE', 'CARDINAL', 'B_SPLINE'
# ramp.color_ramp.elements[0].position = 0.0
# ramp.color_ramp.elements[0].color = (0,0,0,1)

# RGB Curves
curves = nodes.new('ShaderNodeRGBCurve')
curves.mapping.curves[0].points[0].location = (0, 0)
curves.mapping.curves[0].points[1].location = (1, 1)

# Hue/Saturation/Value
hsv = nodes.new('ShaderNodeHueSaturation')
hsv.hue = 0.5
hsv.saturation = 1.0
hsv.value = 1.0
hsv.fac = 1.0

# Gamma
gamma = nodes.new('ShaderNodeGamma')
gamma.gamma = 2.2

# Brightness/Contrast
bc = nodes.new('ShaderNodeBrightContrast')
bc.bright = 0.0
bc.contrast = 0.0

# Invert
invert = nodes.new('ShaderNodeInvert')
invert.fac = 1.0
```

### Векторные и математические ноды
```python
# Mapping
mapping = nodes.new('ShaderNodeMapping')
mapping.vector_type = 'POINT'  # 'TEXTURE', 'VECTOR', 'NORMAL'
# mapping.inputs['Location'].default_value = (0,0,0)
# mapping.inputs['Rotation'].default_value = (0,0,0)
# mapping.inputs['Scale'].default_value = (1,1,1)

# Texture Coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
# Выходы: Generated, Normal, UV, Object, Camera, Window, Reflection

# Vector Math
vmath = nodes.new('ShaderNodeVectorMath')
vmath.operation = 'ADD'  # 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH', 'SCALE', 'NORMALIZE', 'ABSOLUTE', 'FLOOR', 'CEIL', 'MODULO', 'FRACTION', 'MINIMUM', 'MAXIMUM', 'SNAP', 'WRAP', 'PINGPONG', 'SINE', 'COSINE', 'TANGENT'

# Math
math = nodes.new('ShaderNodeMath')
math.operation = 'ADD'  # 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'SINE', 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2', 'POWER', 'LOGARITHM', 'MINIMUM', 'MAXIMUM', 'ROUND', 'LESS_THAN', 'GREATER_THAN', 'MODULO', 'ABSOLUTE', 'EXPONENT', 'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND', 'TRUNC', 'FRACT', 'FLOOR', 'CEIL', 'FRACTION', 'PINGPONG', 'SNAP', 'WRAP'
math.use_clamp = False
```

### Шейдерные ноды
```python
# Glossy BSDF
glossy = nodes.new('ShaderNodeBsdfGlossy')
glossy.distribution = 'GGX'  # 'ASHIKHMIN', 'BECKMANN', 'MULTI_GGX'

# Glass BSDF
glass = nodes.new('ShaderNodeBsdfGlass')
glass.distribution = 'GGX'

# Transparent BSDF
transp = nodes.new('ShaderNodeBsdfTransparent')

# Излучение
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (1,1,1,1)
emission.inputs['Strength'].default_value = 1.0

# Объём
volume = nodes.new('ShaderNodeVolumePrincipled')
volume_abs = nodes.new('ShaderNodeVolumeAbsorption')
volume_scat = nodes.new('ShaderNodeVolumeScatter')

# Mix Shader
mix_shader = nodes.new('ShaderNodeMixShader')
# Factor 0-1, Shader1, Shader2

# Add Shader
add_shader = nodes.new('ShaderNodeAddShader')
```

### Выходные ноды
```python
# Material Output
output = nodes.new('ShaderNodeOutputMaterial')
# Входы: Surface, Volume, Displacement, Thickness

# World Output
world_out = nodes.new('ShaderNodeOutputWorld')
# Входы: Surface, Volume
```

---

## Вспомогательные функции

### Поиск и создание нод
```python
def get_or_create_node(nodes, type_name, name=None):
    """Найти существующую ноду или создать новую"""
    for node in nodes:
        if node.bl_idname == type_name:
            return node
    node = nodes.new(type_name)
    if name:
        node.name = name
    return node

def clear_node_tree(node_tree):
    """Удалить все ноды"""
    for node in list(node_tree.nodes):
        node_tree.nodes.remove(node)
```

### Автоматическая раскладка
```python
def auto_layout_nodes(nodes, start_x=-600, y_step=200):
    """Простая горизонтальная раскладка"""
    x = start_x
    for i, node in enumerate(nodes):
        node.location.x = x
        node.location.y = i * y_step
        x += 300
```

### Запекание карт текстур
```python
def bake_texture(obj, map_type, output_image, margin=16):
    """Запечь map_type в output_image"""
    # map_type: 'DIFFUSE', 'NORMAL', 'ROUGHNESS', 'EMIT', 'AO', 'COMBINED'
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Создать bake-ноду
    mat = obj.active_material
    nodes = mat.node_tree.nodes
    bake_node = nodes.new('ShaderNodeTexImage')
    bake_node.image = output_image
    bake_node.select = True
    nodes.active = bake_node
    
    # Запечь
    bpy.ops.object.bake(
        type=map_type,
        use_selected_to_active=False,
        margin=margin
    )
    
    nodes.remove(bake_node)
    output_image.save()
```

---

## Типовые пресеты материалов

### Металл (золото)
```python
principled.inputs['Base Color'].default_value = (1.0, 0.843, 0.0, 1.0)  # Золото
principled.inputs['Metallic'].default_value = 1.0
principled.inputs['Roughness'].default_value = 0.1
```

### Металл (хром)
```python
principled.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
principled.inputs['Metallic'].default_value = 1.0
principled.inputs['Roughness'].default_value = 0.0
```

### Стекло
```python
principled.inputs['Transmission'].default_value = 1.0
principled.inputs['Roughness'].default_value = 0.0
principled.inputs['IOR'].default_value = 1.45
```

### Излучение (неон)
```python
principled.inputs['Emission Color'].default_value = (0.0, 1.0, 1.0, 1.0)  # Циан
principled.inputs['Emission Strength'].default_value = 10.0
```

### Подповерхностное рассеяние (кожа/воск)
```python
principled.inputs['Subsurface'].default_value = 0.5
principled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)
principled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)
```

### Ткань (Sheen)
```python
principled.inputs['Sheen Weight'].default_value = 0.5
principled.inputs['Sheen Roughness'].default_value = 0.3
principled.inputs['Sheen Tint'].default_value = 0.5
```

### Автоэмаль (Coat)
```python
principled.inputs['Base Color'].default_value = (0.8, 0.0, 0.0, 1.0)
principled.inputs['Metallic'].default_value = 0.8
principled.inputs['Roughness'].default_value = 0.2
principled.inputs['Coat Weight'].default_value = 1.0
principled.inputs['Coat Roughness'].default_value = 0.03
```

---

## Утилиты для материалов

### Копирование материала
```python
new_mat = mat.copy()
new_mat.name = "NewMaterial"
```

### Link и Append
```python
# Link (ссылка на оригинал)
with bpy.data.libraries.load("file.blend", link=True) as (data_from, data_to):
    data_to.materials = ["MaterialName"]

# Append (копия внутрь blend)
with bpy.data.libraries.load("file.blend", link=False) as (data_from, data_to):
    data_to.materials = ["MaterialName"]
```

### Удаление неиспользуемых
```python
# Удалить неиспользуемые материалы
for mat in list(bpy.data.materials):
    if mat.users == 0:
        bpy.data.materials.remove(mat)

# Или: File → Clean Up → Unused Data Blocks
```

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MESH OPERATIONS API REFERENCE](mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](scripting-patterns.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md)
- **По темам:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [MCP SERVER API REFERENCE](../mcp/server-api.md)
- **Теги:** #api, #blender, #reference, #shading
