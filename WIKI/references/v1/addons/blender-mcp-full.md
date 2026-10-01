---
lang: en
tags: [blender, mcp, reference]
---
# BLENDER-MCP - FULL DOCUMENTATION

## Overview
**Repo:** https://github.com/ahujasid/blender-mcp
**Website:** https://mcp-for-blender.com/
**Version:** 1.6+ | **Blender:** 3.0+ | **License:** MIT
**PyPI:** `blender-mcp` | **Discord:** https://discord.gg/SNqPn4TcKQ

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP CLIENTS                                   │
│  Claude Desktop │ Cursor │ VS Code │ Codex │ OpenCode │ ...    │
└─────────────────────────────────────────────────────────────────┘
                              │ stdio (uvx blender-mcp)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCP SERVER (src/blender_mcp/server.py)             │
│  • FastMCP server with stdio transport                          │
│  • Tool definitions (28+ tools)                                 │
│  • Telemetry, trajectory capture, safe mode                    │
│  • Persistent TCP connection to Blender addon (port 9876)       │
└─────────────────────────────────────────────────────────────────┘
                              │ TCP :9876 (JSON protocol)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              BLENDER ADDON (addon.py)                            │
│  • Socket server on :9876                                        │
│  • Command queue → main thread execution (bpy.app.timers)       │
│  • Handlers for all 28+ command types                           │
│  • Poly Haven, Sketchfab, Poly Pizza, Hyper3D, Hunyuan3D       │
│  • Manual edit capture (undo/redo/operators)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BLENDER 3.0+                              │
│  • bpy.data / bpy.ops / bpy.context                             │
│  • GPU offscreen rendering for screenshots                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites
- Blender 3.0+
- Python 3.10+
- **uv** package manager (required)

### Install uv
```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add to PATH (restart shell after)
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

### Quick Install
```bash
# 1. Install Blender addon
uvx blender-mcp install-addon

# 2. Configure MCP client (see below)

# 3. In Blender: N-panel → MCP for Blender → Start MCP Server
```

---

## MCP Client Configuration

### OpenCode
```json
{
  "mcp": {
    "blender-mcp": {
      "type": "local",
      "command": ["uvx", "blender-mcp"],
      "enabled": true,
      "environment": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

### Claude Desktop
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```
Config: `claude_desktop_config.json` (Settings → Developer → Edit Config)

### Cursor
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```
Settings → MCP → Add Server (Windows: use `"command": "cmd", "args": ["/c", "uvx", "blender-mcp"]`)

### Codex
```bash
codex mcp add blender -- uvx blender-mcp
```
Or `~/.codex/config.toml`:
```toml
[mcp_servers.blender]
command = "uvx"
args = ["blender-mcp"]
env = { BLENDER_HOST = "localhost", BLENDER_PORT = "9876" }
```

---

## Available Tools (28+)

### Core Scene Tools
| Tool | Description |
|------|-------------|
| `get_scene_info` | Full scene hierarchy (limited to 10 objects) |
| `get_object_info` | Detailed object data (transform, mesh, materials) |
| `get_world_state_snapshot` | Compact snapshot for trajectory (4000 obj cap) |
| `get_viewport_screenshot` | GPU offscreen render → Image |
| `execute_blender_code` | **Arbitrary Python execution** (step-by-step!) |
| `get_addon_info` | Version/capability handshake |

### Material Tools
| Tool | Description |
|------|-------------|
| `set_texture` | Apply downloaded Poly Haven texture to object |

### Poly Haven (Free, no key)
| Tool | Description |
|------|-------------|
| `get_polyhaven_categories` | List categories for hdris/textures/models |
| `search_polyhaven_assets` | Search with type + category filters |
| `download_polyhaven_asset` | Download + import (HDRI→world, Texture→material, Model→scene) |
| `get_polyhaven_status` | Check if enabled in Blender |

### Poly Pizza (Free API key)
| Tool | Description |
|------|-------------|
| `get_polypizza_status` | Check if enabled |
| `search_polypizza_models` | Query, category (0-11), licence (0=CC-BY,1=CC0), animated, limit |
| `download_polypizza_model` | Import GLB, normalize_size, target_size (meters) |

**Categories:** 0=Food&Drink, 1=Clutter, 2=Weapons, 3=Transport, 4=Furniture&Decor, 5=Objects, 6=Nature, 7=Animals, 8=Buildings, 9=People&Characters, 10=Scenes&Levels, 11=Other

**License:** 0=CC-BY (credit required), 1=CC0 (no credit)

### Sketchfab (API key)
| Tool | Description |
|------|-------------|
| `get_sketchfab_status` | Check if enabled |
| `search_sketchfab_models` | Query, categories, count, downloadable |
| `get_sketchfab_model_preview` | Thumbnail Image for visual confirmation |
| `download_sketchfab_model` | Import, normalize_size, **target_size REQUIRED** (meters) |

### Hyper3D Rodin (API key)
| Tool | Description |
|------|-------------|
| `get_hyper3d_status` | Check if enabled |
| `create_rodin_job` | Submit generation job |
| `poll_rodin_job_status` | Check job status |
| `import_generated_asset` | Import completed model |

### Hunyuan3D (SecretId/SecretKey)
| Tool | Description |
|------|-------------|
| `get_hunyuan3d_status` | Check if enabled |
| `create_hunyuan_job` | Submit generation job |
| `poll_hunyuan_job_status` | Check job status |
| `import_generated_asset_hunyuan` | Import completed model |

---

## Persistent API Credentials

### Blender Preferences (survives restart)
Edit → Preferences → Add-ons → MCP for Blender:
- Sketchfab API Key
- Poly Pizza API Key
- Hyper3D API Key
- Hunyuan3D SecretId / SecretKey / API URL

### Environment Variables (headless/CI)
```bash
BLENDERMCP_SKETCHFAB_API_KEY
BLENDERMCP_POLYPIZZA_API_KEY
BLENDERMCP_HYPER3D_API_KEY
BLENDERMCP_HUNYUAN3D_SECRET_ID
BLENDERMCP_HUNYUAN3D_SECRET_KEY
BLENDERMCP_HUNYUAN3D_API_URL
```

---

## Safe Mode

Blocks risky operations in `execute_blender_code`:
- File I/O, network, subprocess
- Handlers/timers/drivers
- Class/property registration
- External .blend loading

**Enable:**
```bash
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp
```
Or MCP config:
```json
{ "mcpServers": { "blender": { "command": "uvx", "args": ["blender-mcp"], "env": { "BLENDER_MCP_SAFE_MODE": "1" } } } }
```

**Allowed:** Blender operators (modeling, materials, rendering, save, import/export)

---

## Docker Deployment

```bash
# Build
docker build -t blender-mcp .

# macOS/Windows (Docker Desktop)
docker run -i --rm blender-mcp

# Linux (host network)
docker run -i --rm --network=host -e BLENDER_HOST=localhost blender-mcp
```

MCP config:
```json
{ "mcpServers": { "blender": { "command": "docker", "args": ["run", "-i", "--rm", "blender-mcp"] } } }
```

---

## Python Version Pinning
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["--python", "3.11", "blender-mcp"],
      "env": { "UV_PYTHON_PREFERENCE": "only-managed" }
    }
  }
}
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `spawn uvx ENOENT` | Use full path: `which uvx` / `where uvx` |
| Connection refused | Blender addon not running; click "Start MCP Server" |
| Poly Pizza Cloudflare 403 | Download .glb manually → File → Import → glTF |
| Timeout | Break complex requests into steps |
| Version conflict | `uv cache clean blender-mcp && uvx --refresh blender-mcp` |
| Headless Blender (`-b`) | Commands never execute; use GUI or `xvfb-run -a blender` |

---

## File Locations

| File | Path |
|------|------|
| Addon (installed) | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\blender_mcp.py` |
| Addon (source) | `addon.py` in repo |
| MCP Server | `uvx blender-mcp` (from cache) |
| Config (Blender prefs) | Edit → Preferences → Add-ons → MCP for Blender |
| Logs | Blender System Console (Window → Toggle System Console) |

---

## Telemetry
- **Default:** ON (anonymous usage data)
- **Disable in Blender:** Preferences → Add-ons → MCP for Blender → uncheck telemetry
- **Disable via env:** `DISABLE_TELEMETRY=true uvx blender-mcp`
- **Data:** Tool name, success, duration, prompts, code, screenshots, scene data
- **Terms:** See `TERMS_AND_CONDITIONS.md` in repo

---

## Blender Addon Source (addon.py) - Key Classes

### BlenderMCPServer
```python
class BlenderMCPServer:
    def __init__(self, host='localhost', port=9876)
    def start()          # Binds socket, starts thread, registers timer
    def stop()           # Closes socket, unregisters timer, cleans up
    def _server_loop()   # Accepts connections in daemon thread
    def _drain_command_queue()  # Timer callback (0.05s) - executes on main thread
    def _handle_client() # Per-client handler thread
    def execute_command() # Dispatches to handlers
```

### Key Handlers
- `get_scene_info()` - Simplified scene data
- `get_world_state_snapshot()` - Compact trajectory snapshot
- `get_object_info(name)` - Full object details
- `get_viewport_screenshot()` - GPU offscreen render
- `execute_code(code)` - **Arbitrary Python** (with safe mode check)
- `drain_human_activity()` - Undo/redo/operator capture
- Poly Haven / Sketchfab / Poly Pizza / Hyper3D / Hunyuan3D handlers

### Manual Edit Capture
- Records human operators (non-ignored) during MCP session
- `undo_post` / `redo_post` / `depsgraph_update_post` handlers
- Only active with telemetry consent + server running
- Drained via `drain_human_activity()` tool

---

## Protocol
- **Transport:** TCP socket (JSON over raw socket)
- **Port:** 9876 (configurable via `BLENDER_PORT`)
- **Command:** `{"type": "cmd_name", "params": {...}}`
- **Response:** `{"status": "success|error", "result": {...}}` or `{"status": "error", "message": "..."}`
- **Locking:** Single-threaded command queue on Blender main thread

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP ADDON - DEEP DIVE](blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md)
- **Теги:** #blender, #mcp, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

