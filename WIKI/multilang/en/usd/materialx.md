---
id: materialx
lang: en
orig_lang: en
category: usd
type: reference
difficulty: 0
translation: template
---
# USD / MATERIALX / OPENUSD PIPELINE

> Goal: ## 🌍 MULTILANG

**ID:** materialx | **Lang:** en | **Orig:** en | **Category:** usd | **Tags:** 

---

# USD / MATERIALX / OPENUSD PIPELINE

**OpenUSD pipeline for Blender → USD → Houdini/Maya/Katana → Render**

---

## 🎯 USD IN BLENDER

### Blender USD Support (4.0+)
```
Blender USD Features:
├── Export: Full scene, selection, collections
├── Import: Full scene, specific prims, variants
├── Materials: Principled BSDF → MaterialX / UsdPreviewSurface
├── Animation: Full animation, shape keys, constraints
├── Cameras: Full camera data, DOF, stereo
├── Lights: All light types, IES profiles
├── Volumes: VDB, OpenVDB, custom volumes
├── Instancing: Native USD instancing, point instancer
├── Variants: Variant sets, variant selection
├── Composition: References, payloads, sublayers
├── Custom Data: Custom properties, custom attributes
└── Hydra: Viewport rendering via Hydra delegates
```

---

## ⚙️ USD EXPORT

### Basic Export
```python
import bpy
from pathlib import Path

def export_usd(
    filepath: str,
    selection_only: bool = False,
    export_materials: bool = True,
    export_uvmaps: bool = True,
    export_animation: bool = True,
    export_frame_range: bool = True,
    export_frame_step: int = 1,
    export_uvmaps: bool = True,
    export_normals: bool = True,
    export_colors: bool = True,
    export_animation: bool = True,
    export_skinning: bool = True,
    export_uvmaps: bool = True,
    export_display_color: bool = True,
    export_instancing: bool = True,
    export_visibility: bool = True,
    export_custom_properties: bool = True,
    export_custom_attributes: bool = True,
    export_materials: bool = True,
    export_uvmaps: bool = True,
    export_animation: bool = True,
    export_frame_range: bool = True,
    export_frame_step: int = 1,
    # MaterialX
    material_x: bool = True,
    shading_mode: str = 'USE_MATERIAL_X',  # 'USE_MATERIAL_X', 'USE_PREVIEW', 'USE_LOOKDEV'
    # Purpose
    purpose: str = 'default',  # 'default', 'render', 'proxy', 'guide'
    # Instancing
    export_instancing: bool = True,
    # Visibility
    export_visibility: bool = True,
    # Custom Properties
    export_custom_properties: bool = True,
    export_custom_attributes: bool = True,
):
    """Export USD with full options"""
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    bpy.ops.wm.usd_export(
        filepath=filepath,
        selection_only=selection_only,
        export_materials=export_materials,
        export_uvmaps=export_uvmaps,
        export_animation=export_animation,
        export_frame_range=export_frame_range,
        export_frame_step=export_frame_step,
        export_uvmaps=export_uvmaps,
        export_normals=export_normals,
        export_colors=export_colors,
        export_animation=export_animation,
        export_skinning=True,
        export_uvmaps=True,
        export_display_color=True,
        export_instancing=export_instancing,
        export_visibility=export_visibility,
        export_custom_properties=export_custom_properties,
        export_custom_attributes=export_custom_attributes,
        export_materials=export_materials,
        export_uvmaps=export_uvmaps,
        export_animation=export_animation,
        export_frame_range=export_frame_range,
        export_frame_step=export_frame_step,
        # MaterialX
        material_x=material_x,
        shading_mode=shading_mode,
        # Purpose
        purpose=purpose,
        export_instancing=export_instancing,
        export_visibility=export_visibility,
        export_custom_properties=export_custom_properties,
        export_custom_attributes=export_custom_attributes,
    )

# Usage
export_usd("/project/assets/hero/hero_v001.usda", selection_only=True)
```

### Export with Variants
```python
def export_usd_with_variants(filepath, variant_sets=None):
    """
    variant_sets = {
        "modeling": ["high", "low", "proxy"],
        "material": ["clean", "damaged", "rusty"],
        "lod": ["LOD0", "LOD1", "LOD2", "LOD3"]
    }
    """
    # Create variant sets in USD
    # This requires USD Python API (pxr)
    from pxr import Usd, UsdGeom, Sdf
    
    stage = Usd.Stage.CreateNew(filepath)
    
    # Define variant sets
    if variant_sets:
        for set_name, variants in variant_sets.items():
            variant_set = stage.GetRootPrim().GetVariantSets().AddVariantSet(set_name)
            for variant in variants:
                variant_set.AddVariant(variant)
                variant_set.SetVariantSelection(variant)
                with variant_set.GetVariantEditContext():
                    # Add variant-specific content
                    pass
    
    stage.GetRootLayer().Save()

# Usage
export_usd_with_variants("/assets/hero/hero.usda", {
    "modeling": ["high", "low", "proxy"],
    "material": ["clean", "dirty", "wet"],
    "lod": ["LOD0", "LOD1", "LOD2", "LOD3"]
})
```

---

## 🎨 MATERIALX IN BLENDER

### MaterialX Export
```python
def export_materialx(material_name, filepath):
    """Export Blender material as MaterialX"""
    mat = bpy.data.materials[material_name]
    
    if not mat.use_nodes:
        raise ValueError("Material must use nodes")
    
    # Ensure MaterialX output
    mat.node_tree.nodes['Material Output'].target = 'MATERIALX'
    
    # Export via USD with MaterialX
    bpy.ops.wm.usd_export(
        filepath=f"{filepath}.usda",
        material_x=True,
        shading_mode='USE_MATERIAL_X',
        selection_only=True,
    )

# MaterialX Standard Surface
def create_materialx_standard_surface(mat_name):
    """Create MaterialX-compatible standard surface"""
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Standard Surface (MaterialX compatible)
    standard = nodes.new('ShaderNodeBsdfPrincipled')
    standard.location = (0, 0)
    
    # MaterialX outputs
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    output.target = 'MATERIALX'
    
    # Connect
    mat.node_tree.links.new(standard.outputs['BSDF'], output.inputs['Surface'])
    
    # MaterialX specific: Use standard surface parameters
    # base_color, specular_color, specular_roughness, metallic, etc.
    
    return mat
```

### MaterialX Node Reference
```python
# MaterialX Nodes in Blender (4.2+)
# -----------------------------------
# Standard Surface: mx_standard_surface
# Normal Map: mx_normal_map
# Displacement: mx_displacement
# Image: mx_image
# Color Correct: mx_color_correct
# Mix: mx_mix
# Switch: mx_switch
# Condition: mx_condition
# Transform: mx_transform
# Position: mx_position
# Normal: mx_normal
# Geometric Properties: mx_geometric_properties

# Example: MaterialX Network
def create_materialx_network():
    mat = bpy.data.materials.new("MX_Standard")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # MaterialX Standard Surface
    standard = nodes.new('ShaderNodeBsdfPrincipled')
    standard.location = (0, 0)
    # Note: Blender's Principled maps to MX standard_surface
    
    # Image Texture
    tex = nodes.new('ShaderNodeTexImage')
    tex.location = (-400, 0)
    
    # Color Correct
    cc = nodes.new('ShaderNodeColorBalance')
    cc.location = (-200, 0)
    cc.correction_method = 'LIFT_GAMMA_GAIN'
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)
    output.target = 'MATERIALX'
    
    # Links
    links.new(tex.outputs['Color'], cc.inputs['Color'])
    links.new(cc.outputs['Color'], standard.inputs['Base Color'])
    links.new(standard.outputs['BSDF'], output.inputs['Surface'])
    
    return mat
```

---

## 🏗️ USD PIPELINE

### Asset Publishing
```python
# usd_pipeline.py
"""
USD Pipeline: Blender → USD → Houdini/Maya/Katana → Render
"""

class USDPipeline:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.usd_dir = self.project_root / "usd"
        self.usd_dir.mkdir(exist_ok=True)
    
    def publish_asset(self, asset_name: str, version: str, asset_type: str):
        """Publish asset as USD with versioning"""
        # Versioned path: /assets/props/crate/v003/crate_v003.usda
        version_dir = self.usd_dir / "assets" / asset_type / asset_name / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        usd_path = version_dir / f"{asset_name}_v{version}.usda"
        
        # Export current selection
        self.export_usd_with_materialx(str(version_dir / f"{asset_name}_v{version}.usda"))
        
        # Create symlink to latest
        latest_link = self.usd_dir / "assets" / asset_type / asset_name / "latest.usda"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(usd_path.relative_to(latest_link.parent))
        
        return str(usd_path)
    
    def assemble_shot(self, shot_name: str, layout_data: list):
        """Assemble shot from published assets"""
        shot_dir = self.usd_dir / "shots" / shot_name
        shot_dir.mkdir(parents=True, exist_ok=True)
        
        shot_usd = shot_dir / f"{shot_name}.usda"
        self.assemble_shot(shot_name, layout_data, str(shot_usd))
        
        return str(shot_usd)
    
    def assemble_shot(self, shot_name: str, layout_data: list, output_path: str):
        """Assemble shot from published assets"""
        import pxr.Usd as Usd
        import pxr.UsdGeom as UsdGeom
        import pxr.Sdf as Sdf
        
        stage = Usd.Stage.CreateNew(output_path)
        stage.SetDefaultPrim(stage.DefinePrim(f"/{shot_name}", "Scope"))
        stage.SetDefaultPrim(stage.GetPrimAtPath(f"/{shot_name}"))
        
        # Add assets as references
        for i, asset in enumerate(layout_data):
            prim_path = f"/{shot_name}/assets/{asset['name']}_{i:03d}"
            prim = stage.DefinePrim(prim_path, "Xform")
            prim.GetReferences().AddReference(asset['usd_path'])
            
            # Set transform
            import pxr.UsdGeom as UsdGeom
            xform = UsdGeom.Xformable(prim)
            xform.AddTranslateOp().Set(asset.get('location', (0,0,0)))
            xform.AddRotateXYZOp().Set(asset.get('rotation', (0,0,0)))
            xform.AddScaleOp().Set(asset.get('scale', (1,1,1)))
        
        stage.GetRootLayer().Save()
        print(f"USD scene assembled: {output_path}")

# Usage
pipeline = USDPipeline("/project")
pipeline.publish_asset("hero", "003", "characters")
pipeline.assemble_shot("sh0010", [
    {"name": "hero", "usd_path": "/project/usd/assets/characters/hero/v003/hero_v003.usda", 
     "location": (0, 0, 0), "rotation": (0, 0, 0), "scale": (1, 1, 1)},
    {"name": "environment", "usd_path": "/project/usd/assets/environments/city/v001/city_v001.usda",
     "location": (0, 0, 0), "rotation": (0, 0, 0), "scale": (1, 1, 1)},
])
```

---

## 🎨 MATERIALX WORKFLOWS

### MaterialX in Blender → Houdini
```python
# Blender → MaterialX → Houdini
"""
1. Blender: Create MaterialX-compatible shader
2. Export USD with material_x=True
3. Houdini: USD Import → MaterialX Shader Builder
4. Houdini: Assign to geometry
"""

# Houdini Python (for reference)
"""
# In Houdini Python Shell:
import hou

# Load USD
node = hou.node('/stage').createNode('usdimport', 'import_asset')
node.parm('filepath1').set('/assets/hero/hero_v003.usda')

# MaterialX will be imported as MaterialX Shader
# Can edit in MaterialX Shader Builder
"""
```

### MaterialX → Arnold / RenderMan / Karma
```python
# MaterialX → Arnold
"""
Arnold 7+ supports MaterialX natively:
1. Export .mtlx from Blender
2. Arnold: MaterialX Shader → Load .mtlx
4. Assign to geometry
"""

# MaterialX → RenderMan
"""
RenderMan 25+:
1. PxrMaterialX node
5. Load .mtlx file
6. Connect to PxrSurface
"""

# MaterialX → Karma (Houdini)
"""
Karma (Houdini's render engine):
1. Native MaterialX support
2. MaterialX Shader Builder
3. Live editing in viewport
"""
```

---

## 🎬 USD SCENE ASSEMBLY

### Shot Assembly
```python
def assemble_shot_usd(shot_name, layout_data, output_path):
    """Assemble shot from asset references"""
    from pxr import Usd, UsdGeom, Sdf, Gf
    
    stage = Usd.Stage.CreateNew(output_path)
    stage.SetDefaultPrim(stage.DefinePrim(f"/{shot_name}", "Scope"))
    stage.SetDefaultPrim(stage.GetPrimAtPath(f"/{shot_name}"))
    
    # Add assets as references
    for i, asset in enumerate(layout_data):
        prim_path = f"/{shot_name}/assets/{asset['name']}_{i:03d}"
        prim = stage.DefinePrim(prim_path, "Xform")
        prim.GetReferences().AddReference(asset['usd_path'])
        
        # Set transform
        xform = UsdGeom.Xformable(prim)
        xform.AddTranslateOp().Set(Gf.Vec3d(*asset.get('location', (0,0,0))))
        xform.AddRotateXYZOp().Set(Gf.Vec3f(*asset.get('rotation', (0,0,0))))
        xform.AddScaleOp().Set(Gf.Vec3f(*asset.get('scale', (1,1,1))))
    
    # Add lights
    for light_data in layout_data.get('lights', []):
        light_path = f"/{shot_name}/lights/{light_data['name']}"
        light_prim = stage.DefinePrim(light_path, "RectLight")
        light_prim.GetAttribute("intensity").Set(light_data['intensity'])
        light_prim.GetAttribute("color").Set(Gf.Vec3f(*light_data['color']))
        light_prim.GetAttribute("width").Set(light_data.get('width', 1.0))
        light_prim.GetAttribute("height").Set(light_data.get('height', 1.0))
    
    # Add camera
    cam_data = layout_data.get('camera', {})
    if cam_data:
        cam_path = f"/{shot_name}/camera"
        cam_prim = stage.DefinePrim(cam_path, "Camera")
        cam_prim.GetAttribute("focalLength").Set(cam_data.get('focal_length', 50))
        cam_prim.GetAttribute("horizontalAperture").Set(cam_data.get('aperture', 36))
        cam_prim.GetAttribute('focusDistance').Set(cam_data.get('focus_distance', 10))
        cam_prim.GetAttribute('fStop').Set(cam_data.get('fstop', 2.8))
    
    # Save
    stage.GetRootLayer().Save()
    print(f"Shot USD assembled: {output_path}")

# Usage
assemble_shot_usd("sh0010", {
    "assets": [
        {"name": "hero", "usd_path": "/assets/hero/hero_v003.usda", 
         "location": (0, 0, 0), "rotation": (0, 0, 0), "scale": (1, 1, 1)},
        {"name": "environment", "usd_path": "/assets/env/city_v001.usda",
         "location": (0, 0, 0), "rotation": (0, 0, 0), "scale": (1, 1, 1)},
    ],
    "lights": [
        {"name": "key_light", "intensity": 5000, "color": (1.0, 0.95, 0.9), "width": 2, "height": 2},
        {"name": "fill_light", "intensity": 1500, "color": (0.9, 0.95, 1.0), "width": 4, "height": 4},
    ],
    "camera": {"focal_length": 35, "aperture": 36, "focus_distance": 5, "fstop": 2.8}
}, "/project/shots/sh0010/sh0010.usda")
```

---

## 🔧 USD PYTHON API (PXR)

### Common Operations
```python
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt

# Open Stage
stage = Usd.Stage.Open("/path/to/scene.usda")

# Traverse
for prim in stage.Traverse():
    print(prim.GetPath(), prim.GetTypeName())

# Find Prims
prim = stage.GetPrimAtPath("/path/to/prim")

# Attributes
attr = prim.GetAttribute("attr_name")
value = attr.Get()
attr.Set(new_value)

# Relationships
rel = prim.GetRelationship("rel_name")
targets = rel.GetTargets()
rel.SetTargets([Sdf.Path("/new/target")])

# Variants
variant_set = prim.GetVariantSets().AddVariantSet("modeling")
variant_set.AddVariant("high")
variant_set.SetVariantSelection("high")
with variant_set.GetVariantEditContext():
    # Edit high-res variant
    pass

# Composition
stage.GetRootLayer().subLayerPaths.append("./layer.usda")

# Save
stage.GetRootLayer().Save()
```

---

## 🔗 LINKS

- **OpenUSD:** https://openusd.org/
- **MaterialX:** https://www.materialx.org/
- **USD Python API:** https://openusd.org/release/api.html
- **USD in Blender:** https://docs.blender.org/manual/en/latest/addons/import_export/scene_usd.html
- **Hydra Delegates:** https://github.com/Kitware/hydra

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/usd/materialx.md` |
| Russian | `multilang/ru/usd/materialx.md` |