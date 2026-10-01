# GENESISCORE ADDON - DEEP DIVE

## Overview
**Repo:** https://github.com/AIGODLIKE/GenesisCore
**Version:** 0.0.1 | **Blender:** 4.0+ | **License:** Open Source
**Stars:** 134 | **Language:** Python

GenesisCore is a **full MCP Client + Server** built directly into Blender. Unlike blender-mcp (server only), GenesisCore includes the LLM client, so you chat with AI *inside Blender* via N-panel.

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    GENESISCORE ADDON                        │
├────────────────────────────────────────────────────────────┤
│  src/                                                       │
│  ├── client/           # MCP Clients (LLM providers)       │
│  │   ├── base.py       # MCPClientBase - core logic        │
│  │   ├── openai.py     # OpenAI compatible                │
│  │   ├── openrouter.py # OpenRouter (extends OpenAI)      │
│  │   ├── deepseek.py   # DeepSeek API                     │
│  │   ├── claude.py     # Anthropic Claude                 │
│  │   ├── ollama.py     # Local Ollama                     │
│  │   └── siliconflow.py# SiliconFlow                      │
│  ├── server/           # MCP Server (FastMCP)              │
│  │   ├── server.py     # BlenderMCPServer on :45677       │
│  │   └── tools/        # Tool modules                      │
│  │       ├── common_tools.py    # Scene info, code exec    │
│  │       ├── object_tools.py    # Create/modify/delete     │
│  │       ├── material_tools.py  # PBR materials            │
│  │       ├── polyhaven_tools.py # Poly Haven assets         │
│  │       └── asset_tools.py     # Local assets             │
│  ├── preference.py     # Settings UI + config persistence  │
│  ├── ui.py             # N-panel interface                  │
│  ├── executor.py       # Thread-safe bpy execution         │
│  └── logger.py         # Logging                           │
└────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Built-in MCP Client (No External Host Needed)
```python
# In base.py - connects to local MCP server on port 45677
async def connect_to_server(self):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    stdio_transport = await self.exit_stack.enter_async_context(
        sse_client(url="http://localhost:45677/sse", headers=headers)
    )
```

### 2. Multi-Provider Support
| Provider | Base URL | Default Model |
|----------|----------|---------------|
| **OpenRouter** | `https://openrouter.ai/api` | `anthropic/claude-3.5-haiku` |
| **DeepSeek** | `https://api.deepseek.com` | `deepseek-chat` |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o` |
| **Anthropic** | `https://api.anthropic.com` | `claude-3-5-sonnet` |
| **Ollama** | `http://localhost:11434/v1` | `llama3.2` |
| **SiliconFlow** | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-Coder-32B` |

### 3. Tool Modules (Extensible)
Each module registers tools with the MCP server:

```python
# common_tools.py - Most powerful tool
def execute_blender_code(code: str) -> dict:
    """Execute arbitrary Blender Python API code"""
    namespace = {"bpy": bpy}
    exec(code, namespace)
    return {"executed": True}
```

**Available Tools:**
| Module | Tools |
|--------|-------|
| `common_tools` | `get_scene_info`, `get_simple_info`, `execute_blender_code` |
| `object_tools` | `create_object`, `modify_object`, `delete_object`, `get_object_info` |
| `material_tools` | `set_material` (Principled BSDF) |
| `polyhaven_tools` | `search_models`, `fetch_model_info`, `use_model_asset`, `search_hdris`, `use_hdri` |

### 4. Poly Haven Integration
- Caches to `%TEMP%\polyhaven_{models|hdris}`
- Auto-loads cached assets
- Supports 1k/2k/4k/8k/16k resolutions

### 5. External MCP Host Connection
```json
{
  "mcpServers": {
    "BlenderGenesis": {
      "url": "http://localhost:45677"
    }
  }
}
```
Allows Claude Desktop / Cursor / Codex to connect to GenesisCore's server.

---

## Installation

### Method 1: ZIP Install (Recommended)
1. Download: https://github.com/AIGODLIKE/GenesisCore/archive/refs/heads/main.zip
2. Blender → Edit → Preferences → Add-ons → **Install from ZIP**
3. Select the ZIP file
4. Enable **GenesisCore** (search "GenesisCore" or "AI")

### Method 2: Git Clone (Auto-updates)
```powershell
cd %APPDATA%\Blender Foundation\Blender\4.2\scripts\addons
git clone https://github.com/AIGODLIKE/GenesisCore.git
```
Then enable in Preferences.

---

## Configuration

### OpenRouter Setup (Recommended)
1. Get API key: https://openrouter.ai/keys
2. In Blender N-panel (press `N`) → **GenesisCore** tab
3. **Provider:** OpenRouter
4. **API Key:** Paste your key
5. **Fetch Models** → Select: `deepseek/deepseek-chat` or `qwen/qwen-2.5-coder-32b`
6. **Tool Modules:** Enable all (hold Shift to multi-select)
7. **Save Config**

### Model Recommendations (2026)
| Task | Model | Cost |
|------|-------|------|
| **Complex reasoning** | `anthropic/claude-3.5-sonnet` | $$$ |
| **Coding/Blender API** | `deepseek/deepseek-chat` | $ |
| **Fast/cheap** | `qwen/qwen-2.5-coder-32b` | $ |
| **Local (free)** | `ollama:codellama:13b` | Free |

---

## Usage Workflow

```
1. Open N-panel (N) → GenesisCore
2. Select Provider + Model
3. Enable Tool Modules (Common, Object, Material, Polyhaven)
4. Type prompt in chat box
5. Press Enter / Click Execute
6. AI plans → calls tools → executes in Blender
7. Result appears in chat + viewport updates
```

---

## Example Prompts

### Basic Geometry
```
"Create a low-poly castle with 4 towers, a central keep, and a moat. Use simple primitives."
```

### Material + Lighting
```
"Create a studio lighting setup: 3-point lighting with key, fill, and rim lights. Make a chrome sphere in center."
```

### Poly Haven Assets
```
"Search Poly Haven for a Victorian chair and an HDRI for indoor lighting. Import both and set up the scene."
```

### Complex Scene
```
"Build a cyberpunk alley scene: wet pavement (use HDRI), neon signs (emission materials), 
steam particles, and a hovering vehicle. Use Poly Haven assets where possible."
```

### Code Execution (Direct)
```
"Execute this code to create a procedural city grid with random building heights"
```
→ AI calls `execute_blender_code` with full bpy script

---

## Advanced: Custom Tool Development

### 1. Create Tool Module
```python
# src/tools/my_tools.py
from .common import ToolsPackageBase

class MyTools(ToolsPackageBase):
    def my_custom_tool(param: str) -> dict:
        """Description for LLM"""
        # bpy operations here
        return {"result": "success"}
```

### 2. Register in `__init__.py`
```python
# src/tools/__init__.py
from .my_tools import MyTools
# Order matters for UI display
```

### 3. Custom LLM Client
```python
# src/client/custom.py
from .base import MCPClientBase

class MCPClientCustom(MCPClientBase):
    @classmethod
    def info(cls):
        return {"name": "Custom", "description": "My Provider", "version": "0.1"}
    
    @classmethod
    def default_config(cls):
        return {"base_url": "https://api.custom.com", "model": "default"}
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **"Connecting..." hangs** | Check port 45677 not blocked; restart Blender |
| **Model list empty** | Verify API key; check network/proxy |
| **Tools not showing** | Enable modules in N-panel (Shift+click for multiple) |
| **Poly Haven fails** | Check internet; cache in `%TEMP%\polyhaven_*` |
| **Code execution errors** | Open System Console (Window → Toggle System Console) |

---

## File Locations

| File | Path |
|------|------|
| Addon root | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\GenesisCore\` |
| Config | `%APPDATA%\Blender Foundation\Blender\4.2\config\genesiscore_config.json` |
| Poly Haven cache | `%TEMP%\polyhaven_models\` / `polyhaven_hdris\` |
| Logs | Blender System Console |

---

## Related Wiki Pages
- [MCP Architecture](../mcp/architecture.md)
- [Blender API Patterns](../api/scripting-patterns.md)
- [Prompting Guide](../guides/prompting.md)
- [blender-mcp Comparison](blender-mcp.md)