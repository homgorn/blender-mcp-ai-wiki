---
lang: ru
orig_lang: en
translation: ai
---
# СПРАВОЧНИК ПО API MCP-СЕРВЕРА

## Инструменты blender-mcp (28+)

### Базовые инструменты работы со сценой

#### `get_scene_info`
```json
// Возвращает упрощённые данные сцены
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
// Параметры
{"name": "Cube"}

// Возвращает
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
// Компактный снимок траектории (лимит — 4000 объектов)
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
// Параметры
{"max_size": 800, "filepath": "/tmp/screenshot.png", "format": "png"}

// Возвращает: Image (тип Image в MCP)
```

#### `execute_blender_code`
```json
// Параметры
{"code": "import bpy\nbpy.ops.mesh.primitive_cube_add(location=(1,2,3))"}

// Возвращает
{"result": "Code executed successfully: ..."}
```

#### `get_addon_info`
```json
// Данные рукопожатия
{
  "name": "MCP for Blender",
  "addon_version": [1, 6],
  "protocol_version": 5,
  "capabilities": ["get_scene_info", "get_object_info", ...],
  "blender_version": "Blender 4.2.3"
}
```

### Инструменты материалов

#### `set_texture`
```json
// Параметры
{"object_name": "Cube", "texture_id": "RustedIron"}

// Применяет ранее скачанную текстуру Poly Haven
```

### Инструменты Poly Haven (требуют включения в Blender)

#### `get_polyhaven_categories`
```json
// Параметры
{"asset_type": "hdris"}  // "hdris" | "textures" | "models" | "all"

// Возвращает отформатированный список категорий с количеством элементов
```

#### `search_polyhaven_assets`
```json
// Параметры
{"asset_type": "models", "categories": "architecture,buildings"}

// Возвращает
{
  "total_count": 45,
  "returned_count": 20,
  "assets": {...}
}
```

#### `download_polyhaven_asset`
```json
// Параметры
{"asset_id": "abandoned_bakery", "asset_type": "hdris", "resolution": "2k", "file_format": "exr"}
// asset_type: "hdris" | "textures" | "models"
// resolution: "1k" | "2k" | "4k" | "8k" | "16k"

// HDRI → становится окружением мира
// Texture → создаёт PBR-материал
// Model → импортирует .blend в сцену
```

#### `get_polyhaven_status`
```json
// Возвращает статус включения и сообщение
```

### Инструменты Poly Pizza (требуют API-ключ и включения)

#### `get_polypizza_status`
```json
// Возвращает статус включения
```

#### `search_polypizza_models`
```json
// Параметры
{"query": "chair", "category": "Furniture & Decor", "licence": "CC0", "animated": false, "limit": 20}

// Categories: Food & Drink, Clutter, Weapons, Transport, Furniture & Decor, 
// Objects, Nature, Animals, Buildings, People & Characters, Scenes & Levels, Other
// Licence: "CC0" (без указания авторства) | "CC-BY" (атрибуция обязательна)

// Возвращает отформатированный список с лицензией и числом треугольников
```

#### `download_polypizza_model`
```json
// Параметры
{"model_id": "chair_01", "normalize_size": true, "target_size": 1.0}
// target_size в метрах
```

### Инструменты Sketchfab (требуют API-ключ и включения)

#### `get_sketchfab_status`
#### `search_sketchfab_models`
```json
// Параметры
{"query": "car", "categories": "vehicles", "count": 20, "downloadable": true}
```

#### `get_sketchfab_model_preview`
```json
// Параметры
{"uid": "abc123"}
// Возвращает: Image (миниатюра)
```

#### `download_sketchfab_model`
```json
// Параметры
{"uid": "abc123", "target_size": 4.5}
// target_size ОБЯЗАТЕЛЬНЫЙ (метры, наибольшая сторона)
// normalize_size всегда true
```

### Инструменты Hyper3D Rodin (требуют API-ключ и включения)

#### `get_hyper3d_status`
#### `create_rodin_job`
```json
// Параметры
{"prompt": "garden gnome", "seed": 12345}
// Возвращает job_id
```

#### `poll_rodin_job_status`
```json
// Параметры
{"job_id": "job_abc123"}
// Возвращает status, progress, result_url
```

#### `import_generated_asset`
```json
// Параметры
{"job_id": "job_abc123", "result_url": "https://..."}
// Импортирует в сцену
```

### Инструменты Hunyuan3D (требуют SecretId/SecretKey и включения)

#### `get_hunyuan3d_status`
#### `create_hunyuan_job`
#### `poll_hunyuan_job_status`
#### `import_generated_asset_hunyuan`

### Инструменты телеметрии

#### `get_telemetry_consent`
```json
// Возвращает {"consent": true|false|null}
```

#### `set_telemetry_consent`
```json
// Параметры
{"consent": false}
// Выключает сбор данных (через инструмент включить обратно нельзя)
```

#### `drain_human_activity`
```json
// Возвращает буферизованные события отмены/повтора/операторов
{"events": [{"kind": "operator", "bl_idname": "mesh.primitive_cube_add", ...}]}
```

---

## Инструменты GenesisCore (внутренние)

GenesisCore использует те же определения инструментов, но выполняет их напрямую в процессе Blender (без TCP).

### Модули инструментов (src/tools/)

#### `CommonTools`
- `get_simple_info()` → базовая статистика сцены
- `get_scene_info()` → полная сцена
- `execute_blender_code(code)` → произвольный Python

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

## Протокол JSON-RPC (справочно)

### Запрос
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

### Успешный ответ
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {...}
}
```

### Ответ с ошибкой
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

## Добавление своих инструментов

### blender-mcp (на стороне сервера)
```python
# src/blender_mcp/tools/custom.py
from mcp.server.fastmcp import FastMCP

@mcp.tool()
async def my_tool(param: str) -> str:
    """Description for LLM"""
    blender = get_blender_connection()
    return blender.send_command("my_command", {"param": param})
```

### GenesisCore (на стороне аддона)
```python
# src/tools/my_tools.py
from .common import ToolsPackageBase

class MyTools(ToolsPackageBase):
    def my_tool(param: str) -> dict:
        """Description for LLM"""
        # Прямой доступ к bpy
        return {"result": "success"}

# src/tools/__init__.py
from .my_tools import MyTools  # Порядок = порядок отображения в UI
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md)
- **По темам:** [GENESISCORE ADDON - DEEP DIVE](../addons/genesiscore.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](architecture.md)
- **Теги:** #api, #mcp, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.
