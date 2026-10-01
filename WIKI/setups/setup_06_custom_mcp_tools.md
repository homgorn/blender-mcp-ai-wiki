---
id: setup_06_custom_mcp_tools
lang: ru
category: setups
status: full
---
# SETUP 06: CUSTOM MCP TOOLS

**ID:** SETUP-06 | **Type:** Extending Blender-MCP / GenesisCore | **Difficulty:** ⭐⭐⭐ | **Time:** 30-60 min

---

## 🎯 ЦЕЛЬ
Создать собственные MCP инструменты для специфических задач: кастомные примитивы, экспорт в форматы, интеграция с внешними API

---

## 📋 АРХИТЕКТУРА MCP TOOLS

### Blender-MCP (External Server)
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  MCP Client     │────▶│  MCP Server      │────▶│  Blender Addon  │
│  (OpenCode/     │     │  (Python/FastMCP)│     │  (TCP :9876)    │
│   Cursor/etc)   │     │  Custom Tools    │     │  bpy execution  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### GenesisCore (Built-in)
```
┌─────────────────┐     ┌──────────────────┐
│  GenesisCore    │────▶│  Blender Process │
│  (Built-in      │     │  Custom Tools    │
│   MCP Client)   │     │  Direct bpy      │
└─────────────────┘     └──────────────────┘
```

---

## 🔧 BLANDER-MCP: СОЗДАНИЕ CUSTOM TOOLS

### 1. Структура проекта
```
my_blender_mcp/
├── pyproject.toml
├── src/
│   └── my_blender_mcp/
│       ├── __init__.py
│       ├── server.py
│       └── tools/
│           ├── __init__.py
│           ├── export_tools.py
│           └── geometry_tools.py
└── tests/
```

### 2. pyproject.toml
```toml
[project]
name = "my-blender-mcp"
version = "0.1.0"
description = "Custom MCP tools for Blender"
requires-python = ">=3.10"
dependencies = [
    "blender-mcp>=1.6",
    "mcp>=1.0",
    "fastmcp>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.entry-points.mcp]
my_tools = "my_blender_mcp.server:register_tools"
```

### 3. Custom Tool: Export to glTF with Settings
```python
# src/my_blender_mcp/tools/export_tools.py
from mcp.server.fastmcp import FastMCP
from typing import Optional
import json

def register_export_tools(mcp: FastMCP):
    
    @mcp.tool()
    async def export_gltf_advanced(
        filepath: str,
        export_format: str = "GLB",
        export_animations: bool = True,
        export_materials: bool = True,
        export_tangents: bool = True,
        export_cameras: bool = False,
        export_lights: bool = False,
        apply_modifiers: bool = True,
        export_selected_only: bool = False,
    ) -> str:
        """
        Export scene to glTF/GLB with advanced options.
        
        Args:
            filepath: Output path (relative to .blend or absolute)
            export_format: "GLB" or "GLTF_EMBEDDED" or "GLTF_SEPARATE"
            export_animations: Include animations
            export_materials: Include PBR materials
            export_tangents: Include tangent space for normal maps
            export_cameras: Include cameras
            export_lights: Include lights
            apply_modifiers: Apply modifiers before export
            export_selected_only: Export only selected objects
        """
        # This will be executed in Blender via the addon
        return json.dumps({
            "type": "export_gltf_advanced",
            "params": {
                "filepath": filepath,
                "export_format": export_format,
                "export_animations": export_animations,
                "export_materials": export_materials,
                "export_tangents": export_tangents,
                "export_cameras": export_cameras,
                "export_lights": export_lights,
                "apply_modifiers": apply_modifiers,
                "export_selected_only": export_selected_only,
            }
        })

    @mcp.tool()
    async def export_fbx_game(
        filepath: str,
        apply_unit_scale: bool = True,
        bake_space_transform: bool = True,
        object_types: list = None,
        primary_bone_axis: str = "Y_FORWARD",
        secondary_bone_axis: str = "X_UP",
    ) -> str:
        """
        Export to FBX optimized for game engines (Unity/Unreal/Godot).
        """
        return json.dumps({
            "type": "export_fbx_game",
            "params": {
                "filepath": filepath,
                "apply_unit_scale": apply_unit_scale,
                "bake_space_transform": bake_space_transform,
                "object_types": object_types or ["ARMATURE", "MESH"],
                "primary_bone_axis": primary_bone_axis,
                "secondary_bone_axis": secondary_bone_axis,
            }
        })

    @mcp.tool()
    async def export_usd_pipeline(
        filepath: str,
        export_animation: bool = True,
        export_materials: bool = True,
        export_uv_maps: bool = True,
        purpose: str = "default",  # "default", "render", "proxy", "guide"
    ) -> str:
        """
        Export to USD for pipeline (Houdini, Maya, Katana, USDZ).
        """
        return json.dumps({
            "type": "export_usd_pipeline",
            "params": {
                "filepath": filepath,
                "export_animation": export_animation,
                "export_materials": export_materials,
                "export_uv_maps": export_uv_maps,
                "purpose": purpose,
            }
        })
```

### 4. Custom Tool: Geometry Generation
```python
# src/my_blender_mcp/tools/geometry_tools.py
import json
from mcp.server.fastmcp import FastMCP
from typing import List, Optional

def register_geometry_tools(mcp: FastMCP):
    
    @mcp.tool()
    async def create_procedural_building(
        name: str,
        width: float = 10.0,
        depth: float = 10.0,
        height: float = 30.0,
        floors: int = 10,
        window_density: float = 0.7,
        style: str = "modern",  # "modern", "classical", "industrial"
        location: List[float] = None,
    ) -> str:
        """
        Generate a procedural building with floors, windows, roof.
        """
        return json.dumps({
            "type": "create_procedural_building",
            "params": {
                "name": name,
                "width": width,
                "depth": depth,
                "height": height,
                "floors": floors,
                "window_density": window_density,
                "style": style,
                "location": location or [0, 0, 0],
            }
        })

    @mcp.tool()
    async def create_road_network(
        name: str,
        curves: List[dict],  # [{points: [[x,y,z],...], width: 8, type: "main"}]
        sidewalk_width: float = 2.0,
        curb_height: float = 0.15,
        markings: bool = True,
        streetlights: bool = True,
        light_spacing: float = 20.0,
    ) -> str:
        """
        Generate road network with sidewalks, curbs, markings, streetlights.
        """
        return json.dumps({
            "type": "create_road_network",
            "params": {
                "name": name,
                "curves": curves,
                "sidewalk_width": sidewalk_width,
                "curb_height": curb_height,
                "markings": markings,
                "streetlights": streetlights,
                "light_spacing": light_spacing,
            }
        })

    @mcp.tool()
    async def scatter_on_surface(
        target_object: str,
        source_collection: str,
        density: float = 0.1,
        scale_min: float = 0.8,
        scale_max: float = 1.2,
        rotation_random: bool = True,
        align_to_normal: bool = True,
        seed: int = 42,
    ) -> str:
        """
        Scatter objects from collection on target surface (Geometry Nodes style).
        """
        return json.dumps({
            "type": "scatter_on_surface",
            "params": {
                "target_object": target_object,
                "source_collection": source_collection,
                "density": density,
                "scale_min": scale_min,
                "scale_max": scale_max,
                "rotation_random": rotation_random,
                "align_to_normal": align_to_normal,
                "seed": seed,
            }
        })
```

### 5. Регистрация в Server
```python
# src/my_blender_mcp/server.py
from mcp.server.fastmcp import FastMCP
from .tools.export_tools import register_export_tools
from .tools.geometry_tools import register_geometry_tools

mcp = FastMCP("MyBlenderMCP")

# Регистрировать все кастомные инструменты
register_export_tools(mcp)
register_geometry_tools(mcp)

def register_tools():
    """Entry point для pyproject.toml"""
    return mcp
```

---

## 🔧 GENESISCORE: CUSTOM TOOLS (Built-in)

### 1. Структура в аддоне
```
GenesisCore/
├── src/
│   └── tools/
│       ├── __init__.py
│       ├── my_custom_tools.py
│       └── ...
```

### 2. Custom Tool для GenesisCore
```python
# src/tools/my_custom_tools.py
from .common import ToolsPackageBase
import bpy

class MyCustomTools(ToolsPackageBase):
    """
    Custom tools for specific workflows.
    """
    
    def create_shot_sequence(
        shot_name: str,
        camera_name: str,
        start_frame: int,
        end_frame: int,
        resolution: list = None,
    ) -> dict:
        """
        Create a complete shot setup: camera, frames, render settings.
        """
        resolution = resolution or [1920, 1080]
        
        cam = bpy.data.objects.get(camera_name)
        if not cam:
            raise ValueError(f"Camera {camera_name} not found")
        
        scene = bpy.context.scene
        scene.frame_start = start_frame
        scene.frame_end = end_frame
        scene.render.resolution_x = resolution[0]
        scene.render.resolution_y = resolution[1]
        scene.camera = cam
        
        # Create marker
        marker = scene.timeline_markers.new(shot_name, frame=start_frame)
        marker.camera = cam
        
        return {
            "shot": shot_name,
            "camera": camera_name,
            "frames": f"{start_frame}-{end_frame}",
            "resolution": resolution,
        }
    
    def batch_rename_objects(
        pattern: str,
        replacement: str,
        selection_only: bool = True,
    ) -> dict:
        """
        Batch rename objects using regex pattern.
        """
        import re
        objects = bpy.context.selected_objects if selection_only else bpy.data.objects
        renamed = 0
        
        for obj in objects:
            new_name = re.sub(pattern, replacement, obj.name)
            if new_name != obj.name:
                obj.name = new_name
                renamed += 1
        
        return {"renamed": renamed, "total": len(objects)}
    
    def create_lod_hierarchy(
        base_object: str,
        lod_levels: int = 3,
        decimate_ratios: list = None,
    ) -> dict:
        """
        Create LOD hierarchy for game export.
        """
        decimate_ratios = decimate_ratios or [0.5, 0.25, 0.1]
        base = bpy.data.objects.get(base_object)
        if not base:
            raise ValueError(f"Object {base_object} not found")
        
        lod_objects = [base]
        for i, ratio in enumerate(decimate_ratios):
            lod = base.copy()
            lod.data = base.data.copy()
            lod.name = f"{base_object}_LOD{i+1}"
            bpy.context.collection.objects.link(lod)
            
            mod = lod.modifiers.new(f"Decimate_LOD{i+1}", 'DECIMATE')
            mod.ratio = ratio
            bpy.context.view_layer.objects.active = lod
            bpy.ops.object.modifier_apply(modifier=mod.name)
            
            lod_objects.append(lod)
        
        return {"base": base_object, "lods": [o.name for o in lod_objects[1:]]}

def register():
    from .common import ToolsPackageBase
    ToolsPackageBase.register_tool_package(MyCustomTools)

def unregister():
    from .common import ToolsPackageBase
    ToolsPackageBase.unregister_tool_package(MyCustomTools)
```

### 3. Регистрация в GenesisCore
```python
# src/tools/__init__.py
from .common import ToolsPackageBase
from .common_tools import CommonTools
from .object_tools import ObjectTools
from .material_tools import MaterialTools
from .polyhaven_tools import PolyhavenTools
from .asset_tools import AssetTools
# Добавьте свои:
from .my_custom_tools import MyCustomTools

def register():
    ToolsPackageBase.register()

def unregister():
    ToolsPackageBase.unregister()
```

---

## 📦 УПАКОВКА И УСТАНОВКА

### Blender-MCP Package
```bash
# Сборка
pip install build
python -m build

# Установка в development mode
pip install -e .

# Тест
uvx my-blender-mcp --help
```

### GenesisCore (просто перезапуск Blender)
```bash
# После добавления файлов в src/tools/
# Перезапустить Blender
# GenesisCore автоматически загрузит новые инструменты
```

---

## 🔗 РЕГИСТРАЦИЯ В MCP CLIENTS

### OpenCode (my-blender-mcp)
```json
{
  "mcp": {
    "my-blender-mcp": {
      "type": "local",
      "command": ["uvx", "my-blender-mcp"],
      "enabled": true
    }
  }
}
```

### GenesisCore (встроено)
```
# Никакой дополнительной настройки - инструменты доступны сразу в чате
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Blender-MCP Test
```bash
# В терминале с запущенным blender-mcp
echo '{"type":"create_procedural_building","params":{"name":"TestTower","width":10,"height":50,"floors":10}}' | nc localhost 9876
```

### GenesisCore Test
```
# В чате GenesisCore:
"Создай процедурную башню 'TestTower' шириной 10м, высотой 50м, 10 этажей"
```

---

## 🔗 LINKS

- **Blender-MCP Repo:** https://github.com/ahujasid/blender-mcp
- **GenesisCore Repo:** https://github.com/AIGODLIKE/GenesisCore
- **FastMCP Docs:** https://github.com/jlowin/fastmcp
- **Setup 05:** [Render Farm](../setups/setup_05_render_farm.md)
- **Next:** [Setup 07: CI/CD Integration](../setups/setup_07_ci_cd.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_06_custom_mcp_tools.md` |
| Russian | `multilang/ru/setups/setup_06_custom_mcp_tools.md` |