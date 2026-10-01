---
id: setup_08_asset_pipeline
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 08: ASSET PIPELINE

> Ziel: 

**ID:** setup_08_asset_pipeline | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **, list[str], none

## Verwendung
Dies ist die deutsche Version von 'setup_08_asset_pipeline'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_08_asset_pipeline / setups / **, list[str], none
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_08_asset_pipeline
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 3
---

# СЕТАП 08: ASSET PIPELINE

> Цель: ## 🌍 MULTILANG

**ID:** setup_08_asset_pipeline | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** list[str], none

---

# SETUP 08: ASSET PIPELINE

**ID:** SETUP-08 | **Type:** Asset Management & Pipeline | **Difficulty:** ⭐⭐⭐ | **Time:** 40-60 min

---

## 🎯 ЦЕЛЬ
Полный пайплайн управления ассетами: организация, версионирование, валидация, экспорт, деплой

---

## 📋 АРХИТЕКТУРА ПАЙПЛАЙНА

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CREATE    │───▶│  VALIDATE   │───▶│  VERSION    │───▶│  EXPORT     │
│  (Model/    │    │  (Auto QA)  │    │  (Git LFS)  │    │  (Multi-fmt)│
│   Texture)  │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                │                │                │
       ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ASSET REGISTRY (JSON/DB)                     │
│  Metadata  |  Dependencies  |  Tags  |  LODs  |  Preview       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOY TARGETS                               │
│  Game Engine  |  Web/Three.js  |  USD Pipeline  |  Render Farm  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 СТРУКТУРА АССЕТОВ

```
assets/
├── models/
│   ├── characters/
│   │   ├── hero/
│   │   │   ├── v001/
│   │   │   │   ├── hero_v001.blend
│   │   │   │   ├── hero_v001.fbx
│   │   │   │   ├── hero_v001.gltf
│   │   │   │   ├── hero_v001.usdz
│   │   │   │   ├── textures/
│   │   │   │   │   ├── hero_basecolor_2k.png
│   │   │   │   │   ├── hero_roughness_2k.png
│   │   │   │   │   ├── hero_normal_2k.exr
│   │   │   │   │   └── hero_metallic_2k.png
│   │   │   │   ├── lods/
│   │   │   │   │   ├── hero_LOD0.blend
│   │   │   │   │   ├── hero_LOD1.blend
│   │   │   │   │   └── hero_LOD2.blend
│   │   │   │   ├── metadata.json
│   │   │   │   └── preview.png
│   │   │   └── latest -> v001/
│   │   └── ...
│   ├── props/
│   ├── environment/
│   └── vehicles/
├── materials/
│   ├── library/
│   │   ├── metal/
│   │   ├── wood/
│   │   ├── fabric/
│   │   └── ...
│   └── substance/
├── textures/
│   ├── pbr/
│   ├── hdri/
│   └── masks/
├── hdri/
├── scripts/
│   ├── validators/
│   ├── exporters/
│   └── pipeline/
├── registry/
│   ├── assets.json          # Главный реестр
│   ├── index.db             # SQLite для поиска
│   └── tags.yaml            # Теговые категории
└── pipeline/
    ├── config.yaml
    ├── validators.yaml
    └── export_presets.yaml
```

---

## 📄 МЕТАДАННЫЕ АССЕТА (metadata.json)

```json
{
  "asset": {
    "id": "hero_main",
    "name": "Hero Character",
    "type": "character",
    "category": "characters",
    "version": "v001",
    "status": "approved",  // "wip", "review", "approved", "deprecated"
    "created": "2026-01-15T10:30:00Z",
    "updated": "2026-01-15T14:22:00Z",
    "author": "artist_name",
    "tags": ["hero", "human", "rigged", "game-ready", "lod"],
    "description": "Main protagonist character with full rig"
  },
  "technical": {
    "blender_version": "4.2.3",
    "triangles": 24500,
    "vertices": 12800,
    "uv_tiles": 2,
    "materials_count": 4,
    "bones_count": 150,
    "shape_keys": 28,
    "uv_maps": ["UVMap", "Lightmap"],
    "vertex_groups": 45
  },
  "lod": {
    "levels": 3,
    "LOD0": {"tris": 24500, "distance": 0, "file": "hero_LOD0.blend"},
    "LOD1": {"tris": 8200, "distance": 15, "file": "hero_LOD1.blend"},
    "LOD2": {"tris": 2100, "distance": 50, "file": "hero_LOD2.blend"}
  },
  "materials": [
    {"name": "Mat_Skin", "type": "skin", "textures": ["basecolor", "roughness", "normal", "subsurface"]},
    {"name": "Mat_Hair", "type": "hair", "textures": ["basecolor", "roughness", "normal", "alpha"]},
    {"name": "Mat_Clothing", "type": "fabric", "textures": ["basecolor", "roughness", "normal", "height"]},
    {"name": "Mat_Eyes", "type": "eye", "textures": ["basecolor", "normal", "emission"]}
  ],
  "rig": {
    "type": "rigify",
    "bones": 150,
    "face_bones": 52,
    "ik_fk": true,
    "twist_bones": true,
    "corrective_shapes": 24
  },
  "exports": {
    "gltf": {"file": "hero_v001.gltf", "size_mb": 12.4, "version": "2.0"},
    "fbx": {"file": "hero_v001.fbx", "size_mb": 15.2, "version": "7.4"},
    "usdz": {"file": "hero_v001.usdz", "size_mb": 18.7, "version": "1.0"},
    "usd": {"file": "hero_v001.usd", "size_mb": 22.1, "purpose": "default"}
  },
  "preview": {
    "thumbnail": "preview.png",
    "turntable": "turntable.mp4",
    "wireframe": "wireframe.png"
  },
  "dependencies": [
    "assets/materials/library/skin_base.mat",
    "assets/materials/library/hair_shader.mat"
  ],
  "pipeline": {
    "validated": true,
    "validator_version": "1.2.0",
    "last_validation": "2026-01-15T14:22:00Z",
    "warnings": [],
    "errors": []
  }
}
```

---

## ✅ АВТОВАЛИДАЦИЯ (QA)

### validators/geometry_validator.py
```python
import bpy
import bmesh
from typing import List, Dict, Any

class GeometryValidator:
    """Валидация геометрии ассета"""
    
    def __init__(self, obj: bpy.types.Object):
        self.obj = obj
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_all(self) -> Dict[str, Any]:
        self.check_non_manifold()
        self.check_loose_geometry()
        self.check_uv_overlaps()
        self.check_vertex_groups()
        self.check_face_orientation()
        self.check_sharp_edges()
        self.check_triangulation()
        self.check_scale()
        
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "stats": self.get_stats()
        }
    
    def check_non_manifold(self):
        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        non_manifold = [e for e in bm.edges if not e.is_manifold]
        if non_manifold:
            self.errors.append(f"Non-manifold edges: {len(non_manifold)}")
        bm.free()
    
    def check_uv_overlaps(self):
        if not self.obj.data.uv_layers:
            self.warnings.append("No UV maps found")
            return
        
        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        uv_layer = bm.loops.layers.uv.active
        
        # Упрощенная проверка
        uv_coords = []
        for face in bm.faces:
            for loop in face.loops:
                uv = loop[uv_layer].uv
                uv_coords.append((round(uv.x, 4), round(uv.y, 4)))
        
        if len(uv_coords) != len(set(uv_coords)):
            self.warnings.append("Possible UV overlaps detected")
        bm.free()
    
    def check_scale(self):
        scale = self.obj.scale
        if any(abs(s - 1.0) > 0.001 for s in scale):
            self.warnings.append(f"Object scale not applied: {scale}")
    
    def get_stats(self) -> Dict:
        mesh = self.obj.data
        return {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": sum(len(p.vertices) - 2 for p in mesh.polygons),
            "materials": len(mesh.materials),
            "uv_maps": len(mesh.uv_layers),
            "vertex_groups": len(self.obj.vertex_groups),
            "shape_keys": len(self.obj.data.shape_keys.key_blocks) if self.obj.data.shape_keys else 0,
        }

# CLI usage
def validate_asset(blend_path: str) -> Dict:
    import bpy
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    
    results = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            validator = GeometryValidator(obj)
            results[obj.name] = validator.validate_all()
    
    return results
```

### validators/material_validator.py
```python
class MaterialValidator:
    """Валидация PBR материалов"""
    
    REQUIRED_PBR_MAPS = ["base_color", "roughness", "normal", "metallic"]
    OPTIONAL_MAPS = ["height", "ao", "emission", "subsurface"]
    
    def validate_material(self, mat: bpy.types.Material) -> Dict:
        errors = []
        warnings = []
        
        if not mat.use_nodes:
            errors.append("Material doesn't use nodes")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        nodes = mat.node_tree.nodes
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if not principled:
            errors.append("No Principled BSDF found")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Проверка текстур
        for map_name in self.REQUIRED_PBR_MAPS:
            input_socket = principled.inputs.get(map_name.title().replace('_', ' '))
            if input_socket and not input_socket.links:
                warnings.append(f"Missing {map_name} texture")
        
        # Проверка цветовых пространств
        for node in nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                if node.image.colorspace_settings.name == 'sRGB' and 'roughness' in node.label.lower():
                    warnings.append(f"Roughness map '{node.image.name}' uses sRGB instead of Non-Color")
                if node.image.colorspace_settings.name == 'sRGB' and 'normal' in node.label.lower():
                    warnings.append(f"Normal map '{node.image.name}' uses sRGB instead of Non-Color")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
```

---

## 📦 ЭКСПОРТЕРЫ (МУЛЬТИ-ФОРМАТ)

### exporters/multi_exporter.py
```python
import bpy
import os
import json
from pathlib import Path
from typing import List, Dict

class MultiExporter:
    """Экспорт в все необходимые форматы"""
    
    def __init__(self, output_dir: str, asset_id: str, version: str):
        self.output_dir = Path(output_dir)
        self.asset_id = asset_id
        self.version = version
        self.results = {}
    
    def export_all(self, objects: List[bpy.types.Object], formats: List[str] = None) -> Dict:
        formats = formats or ["GLTF", "FBX", "USDZ", "USD"]
        
        for fmt in formats:
            if fmt == "GLTF":
                self.results["gltf"] = self.export_gltf(objects)
            elif fmt == "FBX":
                self.results["fbx"] = self.export_fbx(objects)
            elif fmt == "USDZ":
                self.results["usdz"] = self.export_usdz(objects)
            elif fmt == "USD":
                self.results["usd"] = self.export_usd(objects)
        
        return self.results
    
    def export_gltf(self, objects) -> Dict:
        self.output_dir.joinpath("gltf").mkdir(parents=True, exist_ok=True)
        results = {}
        
        for obj in objects:
            filepath = self.output_dir / "gltf" / f"{obj.name}.glb"
            
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            bpy.ops.export_scene.gltf(
                filepath=str(filepath),
                export_format='GLB',
                use_selection=True,
                export_apply=True,
                export_tangents=True,
                export_materials='EXPORT',
                export_colors=True,
                export_animations=True,
                export_morph=True,
                export_skins=True,
                export_extras=True,
            )
            
            size = filepath.stat().st_size
            results[obj.name] = {"file": str(filepath), "size_mb": round(size/1024/1024, 2)}
        
        return results
    
    def export_fbx(self, objects) -> Dict:
        self.output_dir.joinpath("fbx").mkdir(parents=True, exist_ok=True)
        results = {}
        
        for obj in objects:
            filepath = self.output_dir / "fbx" / f"{obj.name}.fbx"
            
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            bpy.ops.export_scene.fbx(
                filepath=str(filepath),
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
            
            size = filepath.stat().st_size
            results[obj.name] = {"file": str(filepath), "size_mb": round(size/1024/1024, 2)}
        
        return results
    
    def export_usdz(self, objects) -> Dict:
        self.output_dir.joinpath("usdz").mkdir(parents=True, exist_ok=True)
        results = {}
        
        for obj in objects:
            filepath = self.output_dir / "usdz" / f"{obj.name}.usdz"
            
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            bpy.ops.wm.usd_export(
                filepath=str(filepath),
                export_selected=True,
                export_animation=True,
                export_materials=True,
            )
            
            size = filepath.stat().st_size
            results[obj.name] = {"file": str(filepath), "size_mb": round(size/1024/1024, 2)}
        
        return results
    
    def export_usd(self, objects) -> Dict:
        self.output_dir.joinpath("usd").mkdir(parents=True, exist_ok=True)
        results = {}
        
        filepath = self.output_dir / "usd" / f"{self.asset_id}.usd"
        
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        
        bpy.ops.wm.usd_export(
            filepath=str(filepath),
            export_selected=True,
            export_animation=True,
            export_materials=True,
            export_uvmaps=True,
        )
        
        size = filepath.stat().st_size
        return {"file": str(filepath), "size_mb": round(size/1024/1024, 2)}
```

---

## 🏷️ АССЕТ РЕЕСТР (REGISTRY)

### registry/assets.json
```json
{
  "version": "1.0",
  "updated": "2026-01-15T15:00:00Z",
  "assets": {
    "hero_main": {
      "path": "assets/models/characters/hero/latest/",
      "version": "v001",
      "status": "approved",
      "tags": ["character", "hero", "rigged", "lod"],
      "dependencies": ["skin_material", "hair_shader"],
      "exports": ["gltf", "fbx", "usdz", "usd"],
      "lod": true,
      "rigged": true
    },
    "prop_crate_wooden": {
      "path": "assets/models/props/crate_wooden/latest/",
      "version": "v003",
      "status": "approved",
      "tags": ["prop", "crate", "wood", "game-ready"],
      "exports": ["gltf", "fbx"],
      "lod": true,
      "rigged": false
    }
  },
  "tags": {
    "character": ["hero_main", "npc_villager"],
    "prop": ["prop_crate_wooden", "prop_barrel"],
    "environment": ["building_house_01", "tree_oak"],
    "vehicle": ["car_sedan", "truck"],
    "game-ready": ["hero_main", "prop_crate_wooden"],
    "rigged": ["hero_main"],
    "lod": ["hero_main", "prop_crate_wooden"]
  }
}
```

### registry/search.py
```python
import json
from pathlib import Path
from typing import List, Dict, Optional

class AssetRegistry:
    def __init__(self, registry_path: str):
        self.path = Path(registry_path)
        self.data = self.load()
    
    def load(self) -> Dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"version": "1.0", "assets": {}, "tags": {}}
    
    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))
    
    def register_asset(self, asset_id: str, metadata: Dict):
        self.data["assets"][asset_id] = metadata
        # Обновить теги
        for tag in metadata.get("tags", []):
            if tag not in self.data["tags"]:
                self.data["tags"][tag] = []
            if asset_id not in self.data["tags"][tag]:
                self.data["tags"][tag].append(asset_id)
        self.save()
    
    def search(self, query: str = None, tags: List[str] = None, 
               type_filter: str = None, status: str = None) -> List[Dict]:
        results = []
        for asset_id, asset in self.data["assets"].items():
            if query and query.lower() not in asset_id.lower():
                continue
            if tags and not all(t in asset.get("tags", []) for t in tags):
                continue
            if type_filter and asset.get("type") != type_filter:
                continue
            if status and asset.get("status") != status:
                continue
            results.append({"id": asset_id, **asset})
        return results
    
    def get_dependencies(self, asset_id: str) -> List[str]:
        return self.data["assets"].get(asset_id, {}).get("dependencies", [])
    
    def get_dependents(self, asset_id: str) -> List[str]:
        dependents = []
        for aid, asset in self.data["assets"].items():
            if asset_id in asset.get("dependencies", []):
                dependents.append(aid)
        return dependents
```

---

## 🔄 CI/CD ИНТЕГРАЦИЯ

### pipeline/validate_and_export.py
```python
#!/usr/bin/env python3
"""
Полный пайплайн: Валидация -> Экспорт -> Реестр -> Деплой
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scripts.validators.geometry_validator import GeometryValidator
from scripts.validators.material_validator import MaterialValidator
from scripts.exporters.multi_exporter import MultiExporter
from scripts.registry.search import AssetRegistry

def main():
    parser = argparse.ArgumentParser(description="Asset Pipeline")
    parser.add_argument("asset_path", help="Path to .blend file")
    parser.add_argument("--asset-id", required=True, help="Asset ID")
    parser.add_argument("--version", required=True, help="Version (e.g., v001)")
    parser.add_argument("--output", default="exports/", help="Output directory")
    parser.add_argument("--formats", nargs="+", default=["GLTF", "FBX", "USDZ"])
    parser.add_argument("--registry", default="registry/assets.json")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args()
    
    # 1. Load Blender file
    import bpy
    bpy.ops.wm.open_mainfile(filepath=args.asset_path)
    
    # 2. Validation
    if not args.skip_validation:
        print("🔍 Validating geometry...")
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                validator = GeometryValidator(obj)
                result = validator.validate_all()
                if not result["valid"]:
                    print(f"❌ Validation failed for {obj.name}: {result['errors']}")
                    sys.exit(1)
                if result["warnings"]:
                    print(f"⚠️  Warnings for {obj.name}: {result['warnings']}")
        
        print("🔍 Validating materials...")
        for mat in bpy.data.materials:
            validator = MaterialValidator()
            result = validator.validate_material(mat)
            if not result["valid"]:
                print(f"❌ Material validation failed: {result['errors']}")
                sys.exit(1)
            if result["warnings"]:
                print(f"⚠️  Material warnings: {result['warnings']}")
        
        print("✅ Validation passed")
    
    # 3. Export
    print("📦 Exporting...")
    exporter = MultiExporter(args.output, args.asset_id, args.version)
    objects = [obj for obj in bpy.data.objects if obj.get("export", True)]
    results = exporter.export_all(objects, args.formats)
    
    print(f"✅ Exported: {json.dumps(results, indent=2)}")
    
    # 4. Update Registry
    registry = AssetRegistry(args.registry)
    # ... обновить реестр с новой версией
    
    # 5. Deploy (если указано)
    if args.deploy:
        print("🚀 Deploying...")
        # aws s3 sync / rsync / etc.

if __name__ == "__main__":
    main()
```

---

## 📦 ДЕПЛОЙ ТАРГЕТЫ

### deploy/targets.yaml
```yaml
targets:
  unreal_engine:
    path: "../UE_Project/Content/Assets/"
    formats: ["FBX", "USD"]
    naming: "{asset_id}_v{version}"
    post_process:
      - "python scripts/ue_import_helper.py"
  
  unity:
    path: "../Unity_Project/Assets/Imported/"
    formats: ["FBX", "GLTF"]
    naming: "{asset_id}"
    import_settings:
      scale_factor: 1.0
      generate_colliders: true
  
  godot:
    path: "../Godot_Project/assets/models/"
    formats: ["GLTF", "GLB"]
    naming: "{asset_id}.glb"
  
  threejs_web:
    path: "../Web_Project/public/assets/models/"
    formats: ["GLTF", "GLB"]
    compression: "draco"
    texture_compression: "basis"
  
  usd_pipeline:
    path: "../USD_Pipeline/assets/"
    formats: ["USD", "USDA"]
    purpose: "default"
    layering: true
  
  render_farm:
    path: "/mnt/flamenco-storage/assets/"
    formats: ["BLEND", "USD"]
    include_lods: true
  
  cdn:
    bucket: "s3://my-game-assets/"
    formats: ["GLTF", "GLB"]
    cdn_url: "https://cdn.mygame.com/assets/"
    cache_control: "max-age=31536000"
```

---

## 🔗 LINKS

- **Git LFS:** https://git-lfs.github.com/
- **USD Docs:** https://openusd.org/
- **glTF Spec:** https://github.com/KhronosGroup/gltf
- **Setup 07:** [CI/CD Integration](../setups/setup_07_ci_cd.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_08_asset_pipeline.md` |
| Russian | `multilang/ru/setups/setup_08_asset_pipeline.md` |