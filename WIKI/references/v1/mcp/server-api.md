---
lang: en
tags: [api, mcp, reference]
---
# MCP SERVER API REFERENCE

## blender-mcp Tools (28+)

### Core Scene Tools

#### `get_scene_info`
```json
// Returns simplified scene data
{
  "name": "Scene",
  "object_count": 15,
  "objects": [
    {"name": "Cube", "type": "MESH", "location": [0,0,0]}
  ],
  "materials_count": 5
}
```

#### `get_object_info`
```json
// Parameters
{"name": "Cube"}

// Returns
{
  "name": "Cube",
  "type": "MESH",
  "location": [0,0,0],
  "rotation": [0,0,0],
  "scale": [1,1,1],
  "visible": true,
  "bound_box": [[...], ...],
  "materials": ["Material.001"],
  "mesh": {"vertices": 8, "edges": 12, "polygons": 6}
}
```

#### `get_world_state_snapshot`
```json
// Compact trajectory snapshot (4000 object cap)
{
  "name": "Scene",
  "object_count": 15,
  "objects_listed": 15,
  "objects_truncated": false,
  "selected": ["Cube"],
  "selected_count": 1,
  "frame_current": 1,
  "fps": 24,
  "objects": [...],
  "active_camera": "Camera",
  "camera": {...},
  "lights": [...],
  "materials_count": 5,
  "material_fps": {"Material": "a1b2c3d4"},
  "world_fp": "e5f6g7h8",
  "project_id": "abc123def456",
  "blender_version": "4.2.3",
  "snapshot_source": "native"
}
```

#### `get_viewport_screenshot`
```json
// Parameters
{"max_size": 800, "filepath": "/tmp/screenshot.png", "format": "png"}

// Returns: Image (MCP Image type)
```

#### `execute_blender_code`
```json
// Parameters
{"code": "import bpy\nbpy.ops.mesh.primitive_cube_add(location=(1,2,3))"}

// Returns
{"result": "Code executed successfully: ..."}
```

#### `get_addon_info`
```json
// Handshake info
{
  "name": "MCP for Blender",
  "addon_version": [1, 6],
  "protocol_version": 5,
  "capabilities": ["get_scene_info", "get_object_info", ...],
  "blender_version": "Blender 4.2.3"
}
```

### Material Tools

#### `set_texture`
```json
// Parameters
{"object_name": "Cube", "texture_id": "RustedIron"}

// Applies previously downloaded Poly Haven texture
```

### Poly Haven Tools (require enable in Blender)

#### `get_polyhaven_categories`
```json
// Parameters
{"asset_type": "hdris"}  // "hdris" | "textures" | "models" | "all"

// Returns formatted category list with counts
```

#### `search_polyhaven_assets`
```json
// Parameters
{"asset_type": "models", "categories": "architecture,buildings"}

// Returns
{
  "total_count": 45,
  "returned_count": 20,
  "assets": {...}
}
```

#### `download_polyhaven_asset`
```json
// Parameters
{"asset_id": "abandoned_bakery", "asset_type": "hdris", "resolution": "2k", "file_format": "exr"}
// asset_type: "hdris" | "textures" | "models"
// resolution: "1k" | "2k" | "4k" | "8k" | "16k"

// HDRI → sets as world environment
// Texture → creates PBR material
// Model → imports .blend to scene
```

#### `get_polyhaven_status`
```json
// Returns enabled status + message
```

### Poly Pizza Tools (require API key + enable)

#### `get_polypizza_status`
```json
// Returns enabled status
```

#### `search_polypizza_models`
```json
// Parameters
{"query": "chair", "category": "Furniture & Decor", "licence": "CC0", "animated": false, "limit": 20}

// Categories: Food & Drink, Clutter, Weapons, Transport, Furniture & Decor, 
// Objects, Nature, Animals, Buildings, People & Characters, Scenes & Levels, Other
// Licence: "CC0" (no credit) | "CC-BY" (credit required)

// Returns formatted list with licence + tri count
```

#### `download_polypizza_model`
```json
// Parameters
{"model_id": "chair_01", "normalize_size": true, "target_size": 1.0}
// target_size in meters
```

### Sketchfab Tools (require API key + enable)

#### `get_sketchfab_status`
#### `search_sketchfab_models`
```json
// Parameters
{"query": "car", "categories": "vehicles", "count": 20, "downloadable": true}
```

#### `get_sketchfab_model_preview`
```json
// Parameters
{"uid": "abc123"}
// Returns: Image (thumbnail)
```

#### `download_sketchfab_model`
```json
// Parameters
{"uid": "abc123", "target_size": 4.5}
// target_size REQUIRED (meters, largest dimension)
// normalize_size always true
```

### Hyper3D Rodin Tools (require API key + enable)

#### `get_hyper3d_status`
#### `create_rodin_job`
```json
// Parameters
{"prompt": "garden gnome", "seed": 12345}
// Returns job_id
```

#### `poll_rodin_job_status`
```json
// Parameters
{"job_id": "job_abc123"}
// Returns status, progress, result_url
```

#### `import_generated_asset`
```json
// Parameters
{"job_id": "job_abc123", "result_url": "https://..."}
// Imports to scene
```

### Hunyuan3D Tools (require SecretId/SecretKey + enable)

#### `get_hunyuan3d_status`
#### `create_hunyuan_job`
#### `poll_hunyuan_job_status`
#### `import_generated_asset_hunyuan`

### Telemetry Tools

#### `get_telemetry_consent`
```json
// Returns {"consent": true|false|null}
```

#### `set_telemetry_consent`
```json
// Parameters
{"consent": false}
// Turns OFF data collection (cannot turn ON via tool)
```

#### `drain_human_activity`
```json
// Returns buffered undo/redo/operator events
{"events": [{"kind": "operator", "bl_idname": "mesh.primitive_cube_add", ...}]}
```

---

## GenesisCore Tools (Internal)

GenesisCore uses same tool definitions but executes directly in Blender process (no TCP).

### Tool Modules (src/tools/)

#### `CommonTools`
- `get_simple_info()` → basic scene stats
- `get_scene_info()` → full scene
- `execute_blender_code(code)` → arbitrary Python

#### `ObjectTools`
- `create_object(entity_type, name, location, rotation, scale, ...)` → CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT
- `modify_object(name, location, rotation, scale, visible)`
- `delete_object(object_name)`
- `get_object_info(object_name)`

#### `MaterialTools`
- `set_material(object_name, material_name, color)` → Principled BSDF

#### `PolyhavenTools`
- `polyhaven_search_models(names, tags, categories)`
- `polyhaven_fetch_model_info(asset_id)`
- `polyhaven_use_model_asset(asset_id, expected_resolution)`
- `polyhaven_search_hdris(names, tags, categories)`
- `polyhaven_fetch_hdri_info(asset_id)`
- `polyhaven_use_hdri(asset_id, expected_resolution)`

---

## JSON-RPC Protocol (Reference)

### Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {...}
  }
}
```

### Success Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {...}
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error: ..."
  }
}
```

---

## Adding Custom Tools

### blender-mcp (Server-side)
```python
# src/blender_mcp/tools/custom.py
from mcp.server.fastmcp import FastMCP

@mcp.tool()
async def my_tool(param: str) -> str:
    """Description for LLM"""
    blender = get_blender_connection()
    return blender.send_command("my_command", {"param": param})
```

### GenesisCore (Addon-side)
```python
# src/tools/my_tools.py
from .common import ToolsPackageBase

class MyTools(ToolsPackageBase):
    def my_tool(param: str) -> dict:
        """Description for LLM"""
        # Direct bpy access
        return {"result": "success"}

# src/tools/__init__.py
from .my_tools import MyTools  # Order = UI display order
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md)
- **По темам:** [GENESISCORE ADDON - DEEP DIVE](../addons/genesiscore.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](architecture.md)
- **Теги:** #api, #mcp, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

GenesisCore uses same tool definitions but executes directly in Blender process (no TCP).

