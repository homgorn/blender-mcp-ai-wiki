#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Human translations chunk B: wf_02 + P09 -> es/de/zh. Code identical except translated comments."""
import os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
W = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent) / "multilang"

P09_CODE = {
"es": '''```python
import bpy
from pathlib import Path

def create_pbr_material(name, maps_dict, obj_name=None):
    """
    maps_dict keys: 'base_color', 'roughness', 'metallic', 'normal', 'height', 'ao', 'emission'
    values: filepath o tupla Color (R,G,B,A)
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

        # Archivo de imagen
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

    # Conectar mapas
    add_texture('base_color', 'Base Color', 'sRGB')
    add_texture('roughness', 'Roughness', 'Non-Color')
    add_texture('metallic', 'Metallic', 'Non-Color')
    add_texture('normal', 'Normal', 'Non-Color', use_normal_map=True)
    add_texture('height', 'Height', 'Non-Color', use_disp=True)
    add_texture('emission', 'Emission Color', 'sRGB')

    # AO -> Mix con Base Color
    if 'ao' in maps_dict:
        ao_tex = nodes.new('ShaderNodeTexImage')
        ao_tex.image = bpy.data.images.load(str(maps_dict['ao']))
        ao_tex.image.colorspace_settings.name = 'Non-Color'
        ao_tex.location = (-200, 200)
        links.new(mapping.outputs['Vector'], ao_tex.inputs['Vector'])

        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.location = (0, 100)
        # Reconectar Base Color vía Mix
        if principled.inputs['Base Color'].links:
            from_node = principled.inputs['Base Color'].links[0].from_node
            from_socket = principled.inputs['Base Color'].links[0].from_socket
            links.new(from_socket, mix.inputs[1])
        links.new(ao_tex.outputs['Color'], mix.inputs[2])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])

    # Asignar al objeto
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

    return mat

# === EJEMPLOS DE USO ===

# 1. Color simple
create_pbr_material("Mat_Red", {
    'base_color': (1.0, 0.2, 0.2, 1.0),
    'roughness': 0.5,
    'metallic': 0.0
}, "Cube")

# 2. Oro
create_pbr_material("Mat_Gold", {
    'base_color': (1.0, 0.843, 0.0, 1.0),
    'roughness': 0.1,
    'metallic': 1.0
}, "Ring")

# 3. Cristal
create_pbr_material("Mat_Glass", {
    'base_color': (1.0, 1.0, 1.0, 1.0),
    'roughness': 0.0,
    'transmission': 1.0,  # añadir a la función si se necesita
    'ior': 1.45
}, "Glass_Obj")

# 4. PBR completo desde archivos
create_pbr_material("Mat_Brick", {
    'base_color': Path("//textures/brick_basecolor.png"),
    'roughness': Path("//textures/brick_roughness.png"),
    'normal': Path("//textures/brick_normal.png"),
    'height': Path("//textures/brick_height.png"),
    'ao': Path("//textures/brick_ao.png"),
}, "Wall")
```''',
"de": '''```python
import bpy
from pathlib import Path

def create_pbr_material(name, maps_dict, obj_name=None):
    """
    maps_dict keys: 'base_color', 'roughness', 'metallic', 'normal', 'height', 'ao', 'emission'
    values: filepath oder Color-Tupel (R,G,B,A)
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

        if isinstance(val, (tuple, list)):  # Farbe
            principled.inputs[input_name].default_value = val + (1.0,) if len(val)==3 else val
            return

        # Bilddatei
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

    # Maps verbinden
    add_texture('base_color', 'Base Color', 'sRGB')
    add_texture('roughness', 'Roughness', 'Non-Color')
    add_texture('metallic', 'Metallic', 'Non-Color')
    add_texture('normal', 'Normal', 'Non-Color', use_normal_map=True)
    add_texture('height', 'Height', 'Non-Color', use_disp=True)
    add_texture('emission', 'Emission Color', 'sRGB')

    # AO -> Mix mit Base Color
    if 'ao' in maps_dict:
        ao_tex = nodes.new('ShaderNodeTexImage')
        ao_tex.image = bpy.data.images.load(str(maps_dict['ao']))
        ao_tex.image.colorspace_settings.name = 'Non-Color'
        ao_tex.location = (-200, 200)
        links.new(mapping.outputs['Vector'], ao_tex.inputs['Vector'])

        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.location = (0, 100)
        # Base Color via Mix neu verbinden
        if principled.inputs['Base Color'].links:
            from_node = principled.inputs['Base Color'].links[0].from_node
            from_socket = principled.inputs['Base Color'].links[0].from_socket
            links.new(from_socket, mix.inputs[1])
        links.new(ao_tex.outputs['Color'], mix.inputs[2])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])

    # Objekt zuweisen
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

    return mat

# === VERWENDUNGSBEISPIELE ===

# 1. Einfache Farbe
create_pbr_material("Mat_Red", {
    'base_color': (1.0, 0.2, 0.2, 1.0),
    'roughness': 0.5,
    'metallic': 0.0
}, "Cube")

# 2. Gold
create_pbr_material("Mat_Gold", {
    'base_color': (1.0, 0.843, 0.0, 1.0),
    'roughness': 0.1,
    'metallic': 1.0
}, "Ring")

# 3. Glas
create_pbr_material("Mat_Glass", {
    'base_color': (1.0, 1.0, 1.0, 1.0),
    'roughness': 0.0,
    'transmission': 1.0,  # bei Bedarf in Funktion ergänzen
    'ior': 1.45
}, "Glass_Obj")

# 4. Voll-PBR aus Dateien
create_pbr_material("Mat_Brick", {
    'base_color': Path("//textures/brick_basecolor.png"),
    'roughness': Path("//textures/brick_roughness.png"),
    'normal': Path("//textures/brick_normal.png"),
    'height': Path("//textures/brick_height.png"),
    'ao': Path("//textures/brick_ao.png"),
}, "Wall")
```''',
"zh": '''```python
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
```''',
}

P09_PROSE = {
"es": {
 "title": "P09: CONFIGURACIÓN PRINCIPLED BSDF",
 "cluster": "Materials PBR", "diff": "⭐", "tags": "#materials #pbr #principled-bshf #shader-nodes",
 "goal": "Crear y configurar un material Principled BSDF con el set PBR completo",
 "prompt": 'Crea el material "[MAT_NAME]" tipo Principled BSDF:\nBase Color: [R, G, B] o hex #RRGGBB\nRoughness: [0.0-1.0]\nMetallic: [0.0-1.0]\n[Opcional] Transmission, IOR, Clearcoat, Sheen, Emission\nAsígnaselo al objeto "[OBJECT_NAME]"',
 "cheat": "CHULETA DE PARÁMETROS PBR",
 "h": ["Material", "Base Color", "Roughness", "Metallic", "Transmission", "IOR", "Clearcoat"],
 "rows": [
  ["**Plástico**", "Color", "0.3-0.5", "0.0", "0.0", "1.5", "0.0"],
  ["**Metal (pulido)**", "Color del metal", "0.05-0.15", "1.0", "0.0", "—", "0.0"],
  ["**Metal (oxidado/mate)**", "Color del metal", "0.6-0.9", "1.0", "0.0", "—", "0.0"],
  ["**Cristal**", "Blanco", "0.0", "0.0", "1.0", "1.45-1.5", "0.0"],
  ["**Agua**", "Azul claro", "0.05", "0.0", "1.0", "1.33", "0.0"],
  ["**Piel**", "Color piel", "0.6-0.8", "0.0", "0.0", "1.5", "0.1-0.3"],
  ["**Tela**", "Color tela", "0.8-1.0", "0.0", "0.0", "1.5", "0.0"],
  ["**Cerámica**", "Color", "0.1-0.3", "0.0", "0.0", "1.5", "0.2-0.5"],
  ["**Piedra/Hormigón**", "Gris/beige", "0.7-1.0", "0.0", "0.0", "1.5", "0.0"],
  ["**Madera**", "Madera", "0.6-0.9", "0.0", "0.0", "1.5", "0.0"],
 ],
 "fx": "EFECTOS ESPECIALES",
 "fxb": [("Emission (Brillo)", "principled.inputs['Emission Color'].default_value = (1.0, 0.8, 0.2, 1.0)  # Luz cálida\nprincipled.inputs['Emission Strength'].default_value = 5.0  # Intensidad"),
 ("Clearcoat (Barniz/Cerámica)", "principled.inputs['Coat Weight'].default_value = 1.0\nprincipled.inputs['Coat Roughness'].default_value = 0.03"),
 ("Sheen (Tela/Terciopelo)", "principled.inputs['Sheen Weight'].default_value = 0.5\nprincipled.inputs['Sheen Roughness'].default_value = 0.3\nprincipled.inputs['Sheen Tint'].default_value = 0.5"),
 ("Subsurface (Piel, cera, mármol)", "principled.inputs['Subsurface Weight'].default_value = 0.3\nprincipled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # Radio RGB de penetración\nprincipled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)"),
 ("Anisotropic (Superficies estriadas)", "principled.inputs['Anisotropic'].default_value = 0.8\nprincipled.inputs['Anisotropic Rotation'].default_value = 0.25  # 90°\n# Se necesita entrada Tangent (UV o Geometry > Tangent)")],
 "links": "- **Casos:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 03: Product Viz](../cases/case_03_product_viz.md)\n- **Flujos:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)\n- **Prompts:** [P10 Node Groups](./10_node_groups.md), [P11 Procedural Textures](./11_procedural_textures.md)\n- **MCP Tool:** `set_material` (básico), `execute_blender_code` (completo)\n- **Siguiente:** [P10: Node Group Creation](./10_node_groups.md)",
},
"de": {
 "title": "P09: PRINCIPLED BSDF SETUP",
 "cluster": "Materials PBR", "diff": "⭐", "tags": "#materials #pbr #principled-bshf #shader-nodes",
 "goal": "Principled BSDF Material mit komplettem PBR-Mapset erstellen und einrichten",
 "prompt": 'Erstelle Material "[MAT_NAME]" vom Typ Principled BSDF:\nBase Color: [R, G, B] oder hex #RRGGBB\nRoughness: [0.0-1.0]\nMetallic: [0.0-1.0]\n[Optional] Transmission, IOR, Clearcoat, Sheen, Emission\nWeise es dem Objekt "[OBJECT_NAME]" zu',
 "cheat": "PBR-PARAMETER-SPICKZETTEL",
 "h": ["Material", "Base Color", "Roughness", "Metallic", "Transmission", "IOR", "Clearcoat"],
 "rows": [
  ["**Plastik**", "Farbe", "0.3-0.5", "0.0", "0.0", "1.5", "0.0"],
  ["**Metall (poliert)**", "Metallfarbe", "0.05-0.15", "1.0", "0.0", "—", "0.0"],
  ["**Metall (rostig/matt)**", "Metallfarbe", "0.6-0.9", "1.0", "0.0", "—", "0.0"],
  ["**Glas**", "Weiß", "0.0", "0.0", "1.0", "1.45-1.5", "0.0"],
  ["**Wasser**", "Hellblau", "0.05", "0.0", "1.0", "1.33", "0.0"],
  ["**Haut**", "Hautfarbe", "0.6-0.8", "0.0", "0.0", "1.5", "0.1-0.3"],
  ["**Stoff**", "Stofffarbe", "0.8-1.0", "0.0", "0.0", "1.5", "0.0"],
  ["**Keramik**", "Farbe", "0.1-0.3", "0.0", "0.0", "1.5", "0.2-0.5"],
  ["**Stein/Beton**", "Grau/beige", "0.7-1.0", "0.0", "0.0", "1.5", "0.0"],
  ["**Holz**", "Holzton", "0.6-0.9", "0.0", "0.0", "1.5", "0.0"],
 ],
 "fx": "SPEZIALEFFEKTE",
 "fxb": [("Emission (Glühen)", "principled.inputs['Emission Color'].default_value = (1.0, 0.8, 0.2, 1.0)  # Warmes Licht\nprincipled.inputs['Emission Strength'].default_value = 5.0  # Stärke"),
 ("Clearcoat (Lack/Keramik)", "principled.inputs['Coat Weight'].default_value = 1.0\nprincipled.inputs['Coat Roughness'].default_value = 0.03"),
 ("Sheen (Stoff/Samt)", "principled.inputs['Sheen Weight'].default_value = 0.5\nprincipled.inputs['Sheen Roughness'].default_value = 0.3\nprincipled.inputs['Sheen Tint'].default_value = 0.5"),
 ("Subsurface (Haut, Wachs, Marmor)", "principled.inputs['Subsurface Weight'].default_value = 0.3\nprincipled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # RGB-Eindringradius\nprincipled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)"),
 ("Anisotropic (gerillte Oberflächen)", "principled.inputs['Anisotropic'].default_value = 0.8\nprincipled.inputs['Anisotropic Rotation'].default_value = 0.25  # 90°\n# Tangent-Eingang nötig (UV oder Geometry > Tangent)")],
 "links": "- **Fälle:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 03: Product Viz](../cases/case_03_product_viz.md)\n- **Workflows:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)\n- **Prompts:** [P10 Node Groups](./10_node_groups.md), [P11 Procedural Textures](./11_procedural_textures.md)\n- **MCP Tool:** `set_material` (Basis), `execute_blender_code` (voll)\n- **Nächster:** [P10: Node Group Creation](./10_node_groups.md)",
},
"zh": {
 "title": "P09：PRINCIPLED BSDF 设置",
 "cluster": "Materials PBR", "diff": "⭐", "tags": "#materials #pbr #principled-bshf #shader-nodes",
 "goal": "创建并配置带完整 PBR 贴图集的 Principled BSDF 材质",
 "prompt": '创建 "[MAT_NAME]" 材质，类型 Principled BSDF:\nBase Color: [R, G, B] 或 hex #RRGGBB\nRoughness: [0.0-1.0]\nMetallic: [0.0-1.0]\n[可选] Transmission, IOR, Clearcoat, Sheen, Emission\n指定给对象 "[OBJECT_NAME]"',
 "cheat": "PBR 参数速查",
 "h": ["材质", "Base Color", "Roughness", "Metallic", "Transmission", "IOR", "Clearcoat"],
 "rows": [
  ["**塑料**", "颜色", "0.3-0.5", "0.0", "0.0", "1.5", "0.0"],
  ["**金属（抛光）**", "金属色", "0.05-0.15", "1.0", "0.0", "—", "0.0"],
  ["**金属（锈蚀/哑光）**", "金属色", "0.6-0.9", "1.0", "0.0", "—", "0.0"],
  ["**玻璃**", "白色", "0.0", "0.0", "1.0", "1.45-1.5", "0.0"],
  ["**水**", "浅蓝", "0.05", "0.0", "1.0", "1.33", "0.0"],
  ["**皮肤**", "肤色", "0.6-0.8", "0.0", "0.0", "1.5", "0.1-0.3"],
  ["**布料**", "布色", "0.8-1.0", "0.0", "0.0", "1.5", "0.0"],
  ["**陶瓷**", "颜色", "0.1-0.3", "0.0", "0.0", "1.5", "0.2-0.5"],
  ["**石头/混凝土**", "灰/米", "0.7-1.0", "0.0", "0.0", "1.5", "0.0"],
  ["**木材**", "木色", "0.6-0.9", "0.0", "0.0", "1.5", "0.0"],
 ],
 "fx": "特殊效果",
 "fxb": [("Emission（发光）", "principled.inputs['Emission Color'].default_value = (1.0, 0.8, 0.2, 1.0)  # 暖光\nprincipled.inputs['Emission Strength'].default_value = 5.0  # 强度"),
 ("Clearcoat（清漆/陶瓷）", "principled.inputs['Coat Weight'].default_value = 1.0\nprincipled.inputs['Coat Roughness'].default_value = 0.03"),
 ("Sheen（布料/丝绒）", "principled.inputs['Sheen Weight'].default_value = 0.5\nprincipled.inputs['Sheen Roughness'].default_value = 0.3\nprincipled.inputs['Sheen Tint'].default_value = 0.5"),
 ("Subsurface（皮肤、蜡、大理石）", "principled.inputs['Subsurface Weight'].default_value = 0.3\nprincipled.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # RGB 穿透半径\nprincipled.inputs['Subsurface Color'].default_value = (1.0, 0.3, 0.1, 1.0)"),
 ("Anisotropic（拉丝表面）", "principled.inputs['Anisotropic'].default_value = 0.8\nprincipled.inputs['Anisotropic Rotation'].default_value = 0.25  # 90°\n# 需要 Tangent 输入（UV 或 Geometry > Tangent）")],
 "links": "- **案例:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 03: Product Viz](../cases/case_03_product_viz.md)\n- **工作流:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)\n- **提示词:** [P10 Node Groups](./10_node_groups.md), [P11 Procedural Textures](./11_procedural_textures.md)\n- **MCP 工具:** `set_material`（基础），`execute_blender_code`（完整）\n- **下一个:** [P10: Node Group Creation](./10_node_groups.md)",
},
}

P09_META = {
 "es": ("PROMPT", "MCP: `set_material` (básico)", "MCP: `execute_blender_code` (PBR completo)", "OBJETIVO", "Clúster"),
 "de": ("PROMPT", "MCP: `set_material` (Basis)", "MCP: `execute_blender_code` (volles PBR)", "ZIEL", "Cluster"),
 "zh": ("提示词", "MCP: `set_material`（基础）", "MCP: `execute_blender_code`（完整 PBR）", "目标", "类别"),
}

for lang, d in P09_PROSE.items():
    ph, basic, full, goalw, clusterw = P09_META[lang]
    rows = "\n".join("| " + " | ".join(r) + " |" for r in d["rows"])
    fx = "\n\n".join(f"### {t}\n```python\n{c}\n```" for t, c in d["fxb"])
    text = f"""---
id: 09_principled_bsdf
lang: {lang}
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: human
---
# {d['title']}

**ID:** P09 | **{clusterw}:** {d['cluster']} | **{ph}:** {d['diff']} | **Tags:** {d['tags']}

---

## 🎯 {goalw}
{d['goal']}

---

## 📝 {ph}

```
{d['prompt']}
```

---

## 🔧 {basic}

```json
{{
  "type": "set_material",
  "params": {{
    "object_name": "Cube",
    "material_name": "Mat_Red",
    "color": [1.0, 0.0, 0.0, 1.0]
  }}
}}
```

---

## 🔧 {full}

{P09_CODE[lang]}

---

## 📊 {d['cheat']}

| {' | '.join(d['h'])} |
|----------|------------|-----------|----------|--------------|-----|-----------|
{rows}

---

## 🎨 {d['fx']}

{fx}

---

## 🔗 СВЯЗИ

{d['links']}
"""
    (W / lang / "prompts" / "09_principled_bsdf.md").write_text(text, encoding="utf-8")
print("OK chunk B: wf_02/P09 x3 (P09 done)")
