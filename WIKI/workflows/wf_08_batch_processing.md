---
id: wf_08_batch_processing
lang: ru
category: workflows
status: full
---
# WF 08: BATCH PROCESSING

**ID:** WF-08 | **Type:** Automation / Pipeline | **Difficulty:** ⭐⭐ | **Time:** 15-60 min setup

---

## 🎯 ЦЕЛЬ
Автоматизация рутинных операций: батч-рендер, конвертация, валидация, экспорт, деплой

---

## 📋 ТИПЫ БАТЧ-ОПЕРАЦИЙ

| Категория | Операции | Типичное применение |
|-----------|----------|---------------------|
| **Rendering** | Frame range, Multi-camera, Multi-scene | Анимация, ArchViz, Product viz |
| **Conversion** | Format convert, LOD gen, UV unwrap | Asset pipeline, Game export |
| **Validation** | QA checks, Naming, Polycount | CI/CD, Asset library |
| **Export** | Multi-format, Multi-LOD, Multi-scene | Game engine, Web, Pipeline |
| **Asset Management** | Rename, Organize, Registry update | Library maintenance |
| **Scene Assembly** | Batch import, Scatter, Layout | Procedural, Large scenes |

---

## 🔧 MCP КОМАНДЫ ДЛЯ БАТЧА

### Batch Render (Multi-camera, Multi-frame)
```bash
"Батч-рендер всех камер в сцене:
1. Найди все камеры в коллекции 'Cameras_Render'
2. Для каждой камеры:
   - Set Active Camera
   - Set Output Path: //renders/{camera_name}_####.exr
   - Render Frame Range 1-250
   - Compositor: Auto-save passes
3. Generate MP4 preview для каждой камеры"

# Или через Python (см. скрипт ниже)
```

### Batch Convert (Format + LOD)
```bash
"Конвертация всех .blend в папке /assets/source/ в GLB + FBX + USDZ:
1. Найди все .blend файлы рекурсивно
2. Для каждого:
   - Открыть
   - Apply All Transforms
   - Generate LODs (Decimate 0.5, 0.25, 0.1)
   - Export GLB (Draco compression)
   - Export FBX (Game ready)
   - Export USDZ (AR/Web)
   - Save metadata JSON
3. Update Asset Registry"
```

### Batch Validate (QA)
```bash
"QA проверка всех ассетов в /assets/library/:
Для каждого ассета:
1. Geometry: Non-manifold, Loose verts, Zero-area faces
2. UV: Overlaps, Out of bounds, Missing UVs
3. Materials: Missing textures, Wrong color space, Naming
4. Naming Convention: {asset}_{type}_{variant}_LOD{num}
5. Polycount: Within target ±10%
6. Scale: Applied (1.0, 1.0, 1.0)
6. Pivot: At base or center
Generate QA Report: HTML + JSON"
```

### Batch Rename & Organize
```bash
"Реорганизация библиотеки /assets/:
1. Rename по конвенции: {category}_{name}_{variant}_v{ver}
2. Move to folders: /models/characters/, /models/props/, /models/env/
3. Update Asset Registry (JSON/SQLite)
4. Generate Thumbnails (256x256) для каждого ассета
5. Generate LOD Preview (Wireframe + Shaded)"
```

---

## 🐍 PYTHON СКРИПТЫ ДЛЯ БАТЧА

### batch_render.py
```python
#!/usr/bin/env python3
"""Batch Render Script для Blender CLI"""
import bpy
import os
import sys
import argparse
from pathlib import Path

def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Batch Render")
    parser.add_argument("--scene", required=True, help="Path to .blend file")
    parser.add_argument("--output", default="//renders/", help="Output directory")
    parser.add_argument("--cameras", nargs="+", help="Camera names (default: all in 'Cameras_Render')")
    parser.add_argument("--frame-start", type=int, default=1)
    parser.add_argument("--frame-end", type=int, default=250)
    parser.add_argument("--resolution", nargs=2, type=int, default=[1920, 1080])
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--format", choices=["PNG", "EXR", "JPEG"], default="EXR")
    parser.add_argument("--engine", choices=["CYCLES", "EEVEE"], default="CYCLES")
    parser.add_argument("--denoise", action="store_true")
    parser.add_argument("--compositor", action="store_true")
    return parser.parse_args(argv)

def setup_scene(args):
    scene = bpy.context.scene
    scene.render.engine = args.engine
    scene.render.resolution_x = args.resolution[0]
    scene.render.resolution_y = args.resolution[1]
    scene.render.resolution_percentage = 100
    scene.frame_start = args.frame_start
    scene.frame_end = args.frame_end
    
    if args.engine == 'CYCLES':
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = args.denoise
        if args.denoise:
            scene.cycles.denoiser = 'OPTIX'
            scene.cycles.denoising_prefilter = 'ACCURATE'
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
    
    # Output
    scene.render.filepath = args.output
    scene.render.image_settings.file_format = args.format
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '32' if args.format == 'EXR' else '16'
    if args.format == 'EXR':
        scene.render.image_settings.exr_codec = 'ZIP'
        scene.render.image_settings.use_preview = True
    
    # Compositor
    if args.compositor:
        setup_compositor()

def setup_compositor():
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (-400, 0)
    
    # Basic color correction
    cc = nodes.new('CompositorNodeColorBalance')
    cc.location = (0, 200)
    cc.correction_method = 'LIFT_GAMMA_GAIN'
    cc.lift = (1.02, 1.0, 0.98)
    cc.gamma = (1.0, 1.0, 1.0)
    cc.gain = (0.98, 1.0, 1.02)
    
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (200, 0)
    glare.glare_type = 'FOG_GLOW'
    glare.mix = 0.2
    glare.threshold = 0.8
    
    comp = nodes.new('CompositorNodeComposite')
    comp.location = (400, 0)
    viewer = nodes.new('CompositorNodeViewer')
    viewer.location = (400, -200)
    
    links = tree.links
    links.new(nodes['Render Layers'].outputs['Image'], cc.inputs['Image'])
    links.new(cc.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], comp.inputs['Image'])
    links.new(glare.outputs['Image'], viewer.inputs['Image'])

def get_cameras(args):
    if args.cameras:
        return [bpy.data.objects.get(name) for name in args.cameras if bpy.data.objects.get(name)]
    # Auto-detect: cameras in 'Cameras_Render' collection
    coll = bpy.data.collections.get('Cameras_Render')
    if coll:
        return [obj for obj in coll.objects if obj.type == 'CAMERA']
    # Fallback: all cameras
    return [obj for obj in bpy.data.objects if obj.type == 'CAMERA']

def render_camera(cam, args, cam_index):
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.filepath = os.path.join(args.output, f"{cam.name}_####")
    
    # Render animation
    bpy.ops.render.render(animation=True, write_still=False)
    print(f"✅ Rendered camera: {cam.name}")

def main():
    args = parse_args()
    
    # Load scene
    bpy.ops.wm.open_mainfile(filepath=args.scene)
    
    # Setup
    setup_scene(args)
    
    # Get cameras
    cameras = get_cameras(args)
    if not cameras:
        print("❌ No cameras found!")
        return
    
    print(f"🎬 Rendering {len(cameras)} cameras, frames {args.frame_start}-{args.frame_end}")
    
    # Render each camera
    for i, cam in enumerate(cameras):
        if cam:
            render_camera(cam, args, i)
    
    print("✅ Batch render complete!")

if __name__ == "__main__":
    main()
```

### batch_convert.py
```python
#!/usr/bin/env python3
"""Batch Convert .blend → GLB/FBX/USDZ with LODs"""
import bpy
import os
import sys
import json
import argparse
from pathlib import Path

def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Source directory with .blend files")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--formats", nargs="+", default=["GLTF", "FBX", "USDZ"])
    parser.add_argument("--lod-levels", type=int, default=3)
    parser.add_argument("--decimate-ratios", nargs="+", type=float, default=[1.0, 0.5, 0.25, 0.1])
    parser.add_argument("--draco", action="store_true")
    parser.add_argument("--registry", default="assets_registry.json")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

def create_lods(obj, ratios):
    """Create LOD meshes via Decimate modifier"""
    lods = [obj]
    for i, ratio in enumerate(ratios[1:], 1):
        lod = obj.copy()
        lod.data = obj.data.copy()
        lod.name = f"{obj.name}_LOD{i}"
        bpy.context.collection.objects.link(lod)
        
        mod = lod.modifiers.new(f"Decimate_LOD{i}", 'DECIMATE')
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        
        bpy.context.view_layer.objects.active = lod
        bpy.ops.object.modifier_apply(modifier=mod.name)
        lods.append(lod)
    return lods

def export_gltf(objects, filepath, draco=False):
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_tangents=True,
        export_materials='EXPORT',
        export_animations=True,
        export_draco_mesh_compression_enable=draco,
        export_draco_mesh_compression_level=6,
    )

def export_fbx(objects, filepath):
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=True,
        object_types={'ARMATURE', 'MESH'},
        use_armature_deform_only=True,
        add_leaf_bones=False,
        primary_bone_axis='Y_FORWARD',
        secondary_bone_axis='X_UP',
    )

def export_usdz(objects, filepath):
    bpy.ops.wm.usd_export(
        filepath=filepath,
        export_selected=True,
        export_animation=True,
        export_materials=True,
    )

def process_blend(blend_path, args):
    # Load
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    
    # Select exportable objects
    objects = [obj for obj in bpy.data.objects if obj.get("export", True) and obj.type == 'MESH']
    if not objects:
        print(f"⚠️  No exportable objects in {blend_path.name}")
        return
    
    # Create LODs
    all_objects = []
    for obj in objects:
        lods = create_lods(obj, args.decimate_ratios)
        all_objects.extend(lods)
    
    # Output dir
    asset_name = blend_path.stem
    out_dir = Path(args.output_dir) / asset_name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {"asset": asset_name, "version": "1.0", "exports": {}}
    
    # Export each format
    if "GLTF" in args.formats:
        gltf_dir = out_dir / "gltf"
        gltf_dir.mkdir(exist_ok=True)
        for obj in all_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            filepath = gltf_dir / f"{obj.name}.glb"
            export_gltf([obj], str(filepath), args.draco)
            metadata["exports"][f"gltf_{obj.name}"] = str(filepath)
    
    if "FBX" in args.formats:
        fbx_dir = out_dir / "fbx"
        fbx_dir.mkdir(exist_ok=True)
        for obj in all_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            filepath = fbx_dir / f"{obj.name}.fbx"
            export_fbx([obj], str(filepath))
            metadata["exports"][f"fbx_{obj.name}"] = str(filepath)
    
    if "USDZ" in args.formats:
        usdz_dir = out_dir / "usdz"
        usdz_dir.mkdir(exist_ok=True)
        for obj in all_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            filepath = usdz_dir / f"{obj.name}.usdz"
            export_usdz([obj], str(filepath))
            metadata["exports"][f"usdz_{obj.name}"] = str(filepath)
    
    # Save metadata
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"✅ Processed: {asset_name}")

def main():
    args = parse_args()
    
    input_dir = Path(args.input_dir)
    blend_files = list(input_dir.rglob("*.blend"))
    
    print(f"🔍 Found {len(blend_files)} .blend files")
    
    for blend_file in blend_files:
        try:
            process_blend(blend_file, args)
        except Exception as e:
            print(f"❌ Error processing {blend_file}: {e}")

if __name__ == "__main__":
    main()
```

### batch_validate.py
```python
#!/usr/bin/env python3
"""Batch QA Validation для библиотеки ассетов"""
import bpy
import os
import sys
import json
import argparse
from pathlib import Path

def validate_object(obj):
    errors = []
    warnings = []
    
    # Geometry checks
    if obj.type == 'MESH':
        mesh = obj.data
        # Non-manifold
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        non_manifold = [e for e in bm.edges if not e.is_manifold]
        if non_manifold:
            errors.append(f"{obj.name}: {len(non_manifold)} non-manifold edges")
        bm.free()
        
        # UV checks
        if not mesh.uv_layers:
            warnings.append(f"{obj.name}: No UV maps")
        else:
            # Check overlaps (simplified)
            uv_layer = mesh.uv_layers.active
            if uv_layer:
                uvs = [loop[uv_layer].uv for poly in mesh.polygons for loop in poly.loop_indices]
                if len(uvs) != len(set((round(u.x,4), round(u.y,4)) for u in uvs)):
                    warnings.append(f"{obj.name}: Possible UV overlaps")
        
        # Scale
        if any(abs(s - 1.0) > 0.001 for s in obj.scale):
            warnings.append(f"{obj.name}: Scale not applied {obj.scale}")
        
        # Naming convention
        import re
        pattern = r'^[a-z]+_[a-z0-9_]+(_v\d+)?(_LOD\d+)?$'
        if not re.match(pattern, obj.name):
            warnings.append(f"{obj.name}: Naming convention mismatch")
    
    # Materials
    for mat_slot in obj.material_slots:
        if mat_slot.material:
            mat = mat_slot.material
            if mat.use_nodes:
                # Check for missing textures
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and not node.image:
                        warnings.append(f"{obj.name}: Material '{mat.name}' has empty Image Texture node '{node.name}'")
    
    return {"errors": errors, "warnings": warnings}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-dir", required=True)
    parser.add_argument("--output", default="qa_report.json")
    parser.add_argument("--naming-pattern", default=r'^[a-z]+_[a-z0-9_]+(_v\d+)?(_LOD\d+)?$')
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    
    assets_dir = Path(args.assets_dir)
    blend_files = list(assets_dir.rglob("*.blend"))
    
    report = {"summary": {"total": 0, "passed": 0, "failed": 0}, "assets": {}}
    
    for blend_file in blend_files:
        print(f"🔍 Validating: {blend_file}")
        bpy.ops.wm.open_mainfile(filepath=str(blend_file))
        
        asset_name = blend_file.stem
        asset_report = {"file": str(blend_file), "objects": {}, "passed": True}
        
        for obj in bpy.data.objects:
            if obj.type in {'MESH', 'ARMATURE', 'CAMERA', 'LIGHT'}:
                result = validate_object(obj)
                asset_report["objects"][obj.name] = result
                if result["errors"]:
                    asset_report["passed"] = False
        
        if asset_report["passed"]:
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1
        report["summary"]["total"] += 1
        report["assets"][asset_name] = asset_report
    
    # Save report
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n📊 QA Report: {report['summary']['passed']}/{report['summary']['total']} passed")
    print(f"Report saved to: {args.output}")

if __name__ == "__main__":
    main()
```

---

## 🐚 BASH WRAPPERS ДЛЯ CI/CD

### render.sh
```bash
#!/bin/bash
# Usage: ./render.sh scene.blend [camera1 camera2...]

SCENE=$1
shift
CAMERAS=$@

blender -b "$SCENE" -P batch_render.py -- \
  --cameras $CAMERAS \
  --frame-start 1 --frame-end 250 \
  --resolution 3840 2160 \
  --samples 256 \
  --format EXR \
  --engine CYCLES \
  --denoise \
  --compositor \
  --output //renders/
```

### convert.sh
```bash
#!/bin/bash
# Usage: ./convert.sh /path/to/assets /path/to/output

blender -b -P batch_convert.py -- \
  --input-dir "$1" \
  --output-dir "$2" \
  --formats GLTF FBX USDZ \
  --lod-levels 3 \
  --decimate-ratios 1.0 0.5 0.25 0.1 \
  --draco
```

### validate.sh
```bash
#!/bin/bash
# Usage: ./validate.sh /path/to/assets

blender -b -P batch_validate.py -- \
  --assets-dir "$1" \
  --output qa_report.json
```

---

## 🔄 CI/CD INTEGRATION (GitHub Actions)

### .github/workflows/batch.yml
```yaml
name: Batch Processing

on:
  schedule:
    - cron: '0 3 * * *'  # Nightly
  workflow_dispatch:
    inputs:
      operation:
        type: choice
        options: [render, convert, validate, all]
        default: all

jobs:
  batch:
    runs-on: ubuntu-latest
    container:
      image: nvidia/cuda:12.1-devel-ubuntu22.04
      options: --gpus all
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Blender
        run: |
          apt-get update && apt-get install -y blender xvfb
      
      - name: Run Batch Operations
        run: |
          if [[ "${{ github.event.inputs.operation }}" == "render" || "${{ github.event.inputs.operation }}" == "all" ]]; then
            xvfb-run -a ./render.sh scenes/main.blend Cam_Main Cam_Wide Cam_Detail
          fi
          
          if [[ "${{ github.event.inputs.operation }}" == "convert" || "${{ github.event.inputs.operation }}" == "all" ]]; then
            ./convert.sh assets/source assets/exports
          fi
          
          if [[ "${{ github.event.inputs.operation }}" == "validate" || "${{ github.event.inputs.operation }}" == "all" ]]; then
            ./validate.sh assets/library
          fi
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: batch-results
          path: |
            renders/
            exports/
            qa_report.json
          retention-days: 7
```

---

## 📊 MONITORING & LOGGING

### Structured Logging
```python
import logging
import json
from datetime import datetime

class BatchLogger:
    def __init__(self, log_file="batch.log"):
        self.logger = logging.getLogger("batch")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(handler)
    
    def log_start(self, operation, target, params):
        self.logger.info(json.dumps({
            "event": "start",
            "operation": operation,
            "target": target,
            "params": params,
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_end(self, operation, target, result, duration):
        self.logger.info(json.dumps({
            "event": "end",
            "operation": operation,
            "target": target,
            "result": result,
            "duration_sec": duration,
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_error(self, operation, target, error):
        self.logger.error(json.dumps({
            "event": "error",
            "operation": operation,
            "target": target,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }))
```

---

## 🔗 LINKS

- **Blender CLI:** https://docs.blender.org/manual/en/latest/advanced/command_line/
- **Blender Python API:** https://docs.blender.org/api/current/
- **Setup 04:** [Headless Render](../setups/setup_04_headless_render.md)
- **Setup 05:** [Render Farm](../setups/setup_05_render_farm.md)
- **Setup 07:** [CI/CD](../setups/setup_07_ci_cd.md)
- **Setup 08:** [Asset Pipeline](../setups/setup_08_asset_pipeline.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/workflows/wf_08_batch_processing.md` |
| Russian | `multilang/ru/workflows/wf_08_batch_processing.md` |

---

## FULL ADDENDUM: logging

- Structured logging каждого батча (JSON): operation/target/duration.
- Ретрай только упавших чанков, таймаут на кадр.

