# BLENDER-MCP ADDON - DEEP DIVE

## Overview
**Repo:** https://github.com/ahujasid/blender-mcp
**Version:** Latest | **Blender:** 3.0+ | **License:** MIT
**Stars:** 28.3k | **PyPI:** `blender-mcp`

blender-mcp is the **reference MCP server implementation** for Blender. It runs as a separate Python process (via `uvx`) and connects to a lightweight Blender addon via TCP socket (port 9876).

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    MCP CLIENT (Claude/Cursor/Codex)         │
│  uvx blender-mcp                                            │
├────────────────────────────────────────────────────────────┤
│  src/blender_mcp/                                           │
│  ├── server.py       # FastMCP server (stdio transport)    │
│  ├── socket_server.py# TCP server on :9876                 │
│  └── tools/          # Tool definitions                     │
└────────────────────────────────────────────────────────────┘
                              │ TCP :9876
                              ▼
┌────────────────────────────────────────────────────────────┐
│              BLENDER ADDON (addon.py)                       │
│  • Socket client connecting to :9876                        │
│  • BlenderExecutor: Thread-safe command queue              │
│  • Command handlers for each tool                          │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                        BLENDER                              │
└────────────────────────────────────────────────────────────┘
```

---

## Key Differences from GenesisCore

| Aspect | GenesisCore | blender-mcp |
|--------|-------------|-------------|
| **MCP Client** | Built-in (multiple providers) | External (any MCP client) |
| **MCP Server** | Built-in (FastMCP on :45677) | External process (uvx) |
| **Transport** | SSE (internal) | stdio → TCP :9876 |
| **Asset Sources** | Poly Haven only | Poly Haven + Poly Pizza + Sketchfab + Hyper3D + Hunyuan3D |
| **Installation** | ZIP/Git in Blender | `uvx blender-mcp install-addon` |
| **Configuration** | Blender N-panel | MCP client config + Blender addon prefs |

---

## Installation

### Prerequisites
```powershell
# Install uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add to PATH (restart shell after)
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

### Quick Install
```powershell
# 1. Install Blender addon
uvx blender-mcp install-addon

# 2. Configure MCP client (see below)

# 3. In Blender: N-panel → MCP for Blender → Start MCP Server
```

### MCP Client Configuration

#### OpenCode
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

#### Claude Desktop
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

#### Cursor
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

---

## Available Tools (v2026)

### Core Scene Tools
| Tool | Description |
|------|-------------|
| `get_scene_info` | Full scene hierarchy |
| `get_object_info` | Detailed object data |
| `create_object` | Primitives: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT |
| `modify_object` | Transform + visibility |
| `delete_object` | Remove by name |
| `execute_blender_code` | **Arbitrary Python execution** |

### Material Tools
| Tool | Description |
|------|-------------|
| `set_material` | Create/apply Principled BSDF with color |

### Asset Tools (Require API Keys)
| Source | Tools | Setup |
|--------|-------|-------|
| **Poly Haven** | `search_polyhaven_assets`, `download_polyhaven_asset` | Free, no key |
| **Poly Pizza** | `search_polypizza_models`, `download_polypizza_model` | Free API key |
| **Sketchfab** | `search_sketchfab_models`, `download_sketchfab_model` | API key |
| **Hyper3D Rodin** | `generate_rodin_model`, `get_rodin_generation_status` | API key |
| **Hunyuan3D** | `generate_hunyuan3d_model`, `get_hunyuan3d_status` | SecretId/SecretKey |

---

## Poly Pizza Integration (Unique to blender-mcp)

```python
# 1. Get free API key: https://poly.pizza/settings/api
# 2. In Blender N-panel → MCP for Blender → tick "Use Poly Pizza" → paste key
# 3. Or set env: BLENDERMCP_POLYPIZZA_API_KEY

# Usage via AI:
# "Search Poly Pizza for a low-poly chair under CC0 license and import at 1 meter tall"
```

**Licensing:** ~69% CC-BY (requires attribution), filter with `licence="CC0"` for no attribution.

---

## AI 3D Generation (Unique to blender-mcp)

### Hyper3D Rodin
```python
# Requires API key from https://hyper3d.ai/
# Env: BLENDERMCP_HYPER3D_API_KEY
# AI: "Generate a 3D model of a garden gnome through Hyper3D"
```

### Hunyuan3D (Tencent)
```python
# Requires SecretId/SecretKey from https://3d.hunyuan.tencent.com/
# Env: BLENDERMCP_HUNYUAN3D_SECRET_ID / SECRET_KEY / API_URL
# AI: "Create a 3D model of a futuristic car using Hunyuan3D"
```

---

## Safe Mode

```bash
# Enable safe mode (blocks file I/O, network, subprocess, persistent code)
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp
```

Or in MCP config:
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": { "BLENDER_MCP_SAFE_MODE": "1" }
    }
  }
}
```

---

## Docker Deployment

```bash
# Build
docker build -t blender-mcp .

# Run (macOS/Windows with Docker Desktop)
docker run -i --rm blender-mcp

# Run (Linux - host network)
docker run -i --rm --network=host -e BLENDER_HOST=localhost blender-mcp
```

MCP config:
```json
{
  "mcpServers": {
    "blender": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "blender-mcp"]
    }
  }
}
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
| `spawn uvx ENOENT` | Use full path to uvx: `which uvx` / `where uvx` |
| Connection refused | Blender addon not running; click "Start MCP Server" |
| Poly Pizza Cloudflare | Download .glb manually → File → Import → glTF |
| Timeout | Break complex requests into steps |
| Version conflict | `uv cache clean blender-mcp && uvx --refresh blender-mcp` |

---

## File Locations

| File | Path |
|------|------|
| Addon (installed) | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\blender_mcp.py` |
| Addon (source) | `addon.py` in repo |
| MCP Server | `uvx blender-mcp` (runs from cache) |
| Config (Blender prefs) | Edit → Preferences → Add-ons → MCP for Blender |
| Logs | Blender System Console |

---

## Related Wiki Pages
- [MCP Architecture](../mcp/architecture.md)
- [GenesisCore Comparison](genesiscore.md)
- [MCP Client Setup](../mcp/clients.md)
- [Prompting Guide](../guides/prompting.md)