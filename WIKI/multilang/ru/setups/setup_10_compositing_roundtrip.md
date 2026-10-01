---
id: setup_10_compositing_roundtrip
lang: ru
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)

> Цель: ## 🌍 MULTILANG

**ID:** setup_10_compositing_roundtrip | **Lang:** ru | **Orig:** ru | **Category:** setups | **Tags:** 

---

# SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)

**ID:** SETUP-10 | **Type:** Compositing Pipeline | **Difficulty:** ⭐⭐⭐ | **Time:** 30-45 min

---

## 🎯 ЦЕЛЬ
Настроить полноценный пайплайн Blender ↔ Nuke / After Effects для профессионального композитинга

---

## 🎯 АРХИТЕКТУРА ПАЙПЛАЙНА

```
Blender (3D)          OpenEXR/ACES          Nuke / AE (Comp)
┌─────────────┐      Multi-layer          ┌─────────────┐
│  3D Scene   │ ──────────────────────▶  │  Compositing│
│  - Models   │  EXR Multi-layer          │  - Grade    │
│  - Lights   │  Cryptomatte              │  - Effects  │
│  - Cameras  │  Deep Data                │  - Track    │
└─────────────┘                          └─────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────────┐                    ┌─────────────┐
│   Deliverables  │                    │  Final Out  │
│  - EXR seq      │                    │  - ProRes   │
│  - LUTs/CDL     │                    │  - H264/HEVC│
│  - LUTs/3D LUT  │                    │  - DPX/EXR  │
└─────────────────┘                    └─────────────┘
```

---

## 📋 НАСТРОЙКА EXR MULTI-LAYER EXPORT

### Blender EXR Multi-layer Setup
```python
# exr_multilayer_setup.py
import bpy

def setup_exr_multilayer():
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    # Render Layers
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (-400, 0)
    rl.layer = "ViewLayer"
    
    # Enable all passes
    view_layer = bpy.context.view_layer
    view_layer.use_pass_combined = True
    view_layer.use_pass_z = True              # Depth
    view_layer.use_pass_normal = True         # Normal
    view_layer.use_pass_mist = True           # Mist
    view_layer.use_pass_ambient_occlusion = True  # AO
    view_layer.use_pass_emission = True       # Emission
    view_layer.use_pass_shadow = True         # Shadow
    view_layer.use_pass_diffuse_color = True  # DiffCol
    view_layer.use_pass_glossy_color = True   # GlossCol
    view_layer.use_pass_transmission_color = True  # TransCol
    view_layer.use_pass_subsurface_color = True    # SubsurfCol
    view_layer.use_pass_volume = True         # Volume
    
    # Cryptomatte
    view_layer.use_pass_cryptomatte = True
    view_layer.cryptomatte_use_object = True
    view_layer.cryptomatte_use_material = True
    view_layer.cryptomatte_use_asset = True
    
    # Freestyle
    bpy.context.scene.render.use_freestyle = True
    view_layer.use_freestyle = True
    
    # Cryptomatte node
    crypto = nodes.new('CompositorNodeCryptomatte')
    crypto.location = (0, -400)
    links.new(rl.outputs['Cryptomatte00'], crypto.inputs['Image'])
    
    # File Output - MultiLayer EXR
    file_out = nodes.new('CompositorNodeOutputFile')
    file_out.location = (800, 0)
    file_out.format.file_format = 'OPEN_EXR_MULTILAYER'
    file_out.format.color_mode = 'RGBA'
    file_out.format.color_depth = '32'
    file_out.format.exr_codec = 'ZIP'
    file_out.base_path = "//renders/exr/"
    
    # Connect all passes
    passes = [
        'Image', 'Depth', 'Normal', 'Mist', 'AO',
        'Emission', 'Shadow', 'DiffCol', 'GlossCol',
        'TransCol', 'SubsurfCol', 'Volume',
        'Cryptomatte00', 'Cryptomatte10', 'Cryptomatte20'
    ]
    
    for i, pass_name in enumerate(passes):
        if pass_name in rl.outputs:
            file_out.layer_slots.new(pass_name)
            links.new(rl.outputs[pass_name], file_out.inputs[i])
            file_out.layer_slots[i].path = pass_name
    
    # Composite output
    comp = nodes.new('CompositorNodeComposite')
    comp.location = (1000, 0)
    links.new(nodes['Render Layers'].outputs['Image'], comp.inputs['Image'])
    
    print("EXR Multi-layer setup complete!")

setup_exr_multilayer()
```

---

## 🎬 NUKE ROUNDTRIP

### Nuke Import Script
```python
# nuke_import.py (запускать в Nuke Script Editor)
import nuke
import os

def import_blender_exr(exr_path):
    """Импорт Blender EXR в Nuke"""
    read = nuke.createNode('Read')
    read['file'].setValue(exr_path)
    read['colorspace'].setValue('linear')
    return read

def setup_cryptomatte(read_node):
    """Настройка Cryptomatte"""
    crypto = nuke.createNode('Cryptomatte')
    crypto.setInput(0, read_node)
    crypto['cryptoLayer'].setValue('crypto_object')  # или crypto_material
    return crypto

def setup_deep_compositing(read_node):
    """Deep compositing setup"""
    deep = nuke.createNode('DeepRead')
    deep['file'].setValue(read_node['file'].value())
    return deep

# Пример полного пайплайна
def setup_blender_shot(shot_name, exr_path):
    read = import_blender_exr(exr_path)
    crypto = setup_cryptomatte(read)
    
    # Color correction
    grade = nuke.createNode('Grade')
    grade.setInput(0, crypto)
    
    # Output
    write = nuke.createNode('Write')
    write['file'].setValue(f'/renders/final/{shot_name}_v001.%04d.exr')
    write['file_type'].setValue('exr')
    write['colorspace'].setValue('linear')
    write.setInput(0, grade)
    
    return write
```

---

## 🎨 AFTER EFFECTS ROUNDTRIP

### AE Import Script (JSX)
```javascript
// ae_import_blender.jsx (запуск в After Effects)
var exrPath = "/path/to/renders/shot001/beauty.####.exr";
var compName = "Blender_Shot_001";

// Создание компа
var comp = app.project.items.addComp(
    "Blender_Shot_001", 1920, 1080, 1, 250, 24
);

// Импорт EXR последовательности
var importOptions = new ImportOptions(File(exrPath));
importOptions.sequence = true;
importOptions.forceAlphabetical = true;
var footage = app.project.importFile(importOptions);

// Добавление в комп
var layer = comp.layers.add(footage);
layer.adjustmentLayer = false;

// Cryptomatte эффект
var crypto = layer.Effects.addProperty("Cryptomatte");
crypto.property("Crypto Layer").setValue("crypto_object");

// Color Correction
var cc = layer.Effects.addProperty("Color Correction");
cc.property("Master Saturation").setValue(110);

// Export
var renderQueue = app.project.renderQueue;
var rqItem = renderQueue.items.add(comp);
rqItem.outputModule(1).file = new File("/renders/final/shot001_final.mov");
rqItem.outputModule(1).applyTemplate("Lossless with Alpha");
```

### OpenColorIO в AE
```javascript
// OCIO Setup для ACES в AE
app.project.colorSettings.colorManagementEnabled = true;
app.project.colorSettings.workingSpace = "ACEScg";
app.project.colorSettings.displayColorSpace = "sRGB";
app.project.colorSettings.viewTransform = "ACES 1.0 SDR-video";
```

---

## 🔄 ROUNDTRIP WORKFLOW

### Blender → Nuke → Blender
```python
# blender_nuke_roundtrip.py
import bpy
import subprocess
from pathlib import Path

def blender_to_nuke_to_blender(shot_name):
    """
    Полный цикл: Blender → Nuke → Blender
    """
    # 1. Blender: Render EXR Multi-layer
    exr_path = f"//renders/{shot_name}/beauty.####.exr"
    bpy.context.scene.render.filepath = exr_path
    bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.image_settings.color_depth = '32'
    bpy.context.scene.render.image_settings.exr_codec = 'ZIP'
    bpy.ops.render.render(animation=True, write_still=False)
    
    # 2. Nuke Processing (внешний скрипт)
    nuke_script = f"""
    import nuke
    read = nuke.createNode('Read')
    read['file'].setValue('{exr_path}')
    # ... compositing ...
    write = nuke.createNode('Write')
    write['file'].setValue('//renders/{shot_name}_comp.####.exr')
    write['file_type'].setValue('exr')
    nuke.execute(write, 1, 250)
    """
    
    # Запуск Nuke
    subprocess.run(['nuke', '-t', '-x', nuke_script], check=True)
    
    # 3. Blender: Импорт результата
    comp_path = f"//renders/{shot_name}_comp.####.exr"
    # Импорт как Image Sequence или Movie Clip
    bpy.ops.clip.open(filepath=comp_path)
    
    return "Roundtrip complete"
```

---

## 🎯 COLOR MANAGEMENT (ACES/OCIO)

### Unified OCIO Config
```yaml
# config.ocio (общий для Blender/Nuke/AE)
ocio_profile_version: 2

color_spaces:
  - !<ColorSpace>
    name: ACEScg
    bit_depth: 32f
    is_data: false
    to_reference: !<GroupTransform>
      children:
        - !<MatrixTransform> {matrix: [0.662454, 0.134004, 0.156187, 0, 0.272228, 0.674081, 0.053691, 0, -0.005574, -0.004058, 1.009632, 0, 0, 0, 0, 1]}

  - name: sRGB
    bit_depth: 8ui
    to_reference: !<ColorSpaceTransform> {src: sRGB, dst: ACEScg}

viewing_rules:
  - !<ViewingRule> {name: "sRGB", colorspace: "sRGB", encodings: ["sRGB"]}

views:
  - !<View> {name: "ACES 1.3 SDR-video", colorspace: "sRGB", looks: ["ACES_sRGB"]}

looks:
  - !<Look> {name: "ACES_sRGB", process_space: "ACEScg", transform: !<GroupTransform> {children: [{!<ColorSpaceTransform> {src: ACEScg, dst: sRGB}}]}}
```

### Nuke OCIO Setup
```python
# nuke_ocio_setup.py
nuke.root()['colorManagement'].setValue('OCIO')
nuke.root()['OCIO_config'].setValue('custom')
nuke.root()['OCIO_config_file'].setValue('/path/to/config.ocio')
nuke.root()['colorManagement'].setValue('OCIO')
nuke.root()['OCIO_viewTransform'].setValue('ACES 1.3 SDR-video')
```

---

## 📦 DELIVERY SPECS

| Deliverable | Format | Color Space | Bit Depth | Use Case |
|-------------|--------|-------------|-----------|----------|
| **Master** | EXR MultiLayer | ACEScg | 32-bit float | Archive |
| **Comp Source** | EXR MultiLayer | ACEScg | 32-bit float | Nuke/AE |
| **Review** | MP4/H.264 | sRGB | 8-bit | Client Review |
| **Broadcast** | ProRes 422 HQ | Rec.709 | 10-bit | TV Delivery |
| **DCI-P3** | ProRes 4444 | P3-D65 | 12-bit | Cinema DCP |
| **HDR (PQ)** | ProRes 4444 | Rec.2020 ST2084 | 16-bit | HDR Delivery |
| **HDR (HLG)** | ProRes 4444 | Rec.2020 HLG | 10-bit | Broadcast HDR |
| **Web/Streaming** | H.265/HEVC | sRGB/P3 | 10-bit | YouTube/Vimeo |

---

## 🔗 LINKS

- **OpenEXR Spec:** https://www.openexr.com/
- **Nuke Python API:** https://docs.foundry.com/nuke/13.0/pythondevguide/
- **AE Scripting:** https://extendscript.docsforadobe.dev/
- **OCIO Configs:** https://github.com/AcademySoftwareFoundation/OpenColorIO-Configs
- **ACES Central:** https://acescentral.com/

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_10_compositing_roundtrip.md` |
| Russian | `multilang/ru/setups/setup_10_compositing_roundtrip.md` |