---
lang: en
tags: [blender, mcp, reference]
---
# MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER

## Overview
MCP (Model Context Protocol) is an open standard for connecting AI assistants to external tools and data. In Blender context, it enables LLMs to directly control Blender via structured tool calls.

---

## Protocol Specification

### Transport Options
| Transport | Use Case | Example |
|-----------|----------|---------|
| **stdio** | Local subprocess | `uvx blender-mcp` |
| **SSE** | HTTP long-polling | GenesisCore on :45677 |
| **WebSocket** | Bidirectional | Future |

### Message Format
```json
// Request (Client → Server)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_object",
    "arguments": {"entity_type": "CUBE", "name": "MyCube"}
  }
}

// Response (Server → Client)
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "name": "MyCube",
    "type": "MESH",
    "location": [0, 0, 0]
  }
}
```

---

## Blender MCP Implementations

### 1. blender-mcp (Reference Server)
- **Architecture:** External MCP server (uvx) + Blender addon (TCP :9876)
- **Transport:** stdio → TCP
- **Tools:** 28+ (scene, objects, materials, 5 asset sources, AI 3D gen)
- **Clients:** Any MCP-compatible (Claude, Cursor, Codex, OpenCode, etc.)

### 2. GenesisCore (All-in-One)
- **Architecture:** Blender addon with built-in MCP Client + Server
- **Transport:** Internal SSE (:45677) + External SSE for other clients
- **Providers:** OpenRouter, DeepSeek, OpenAI, Anthropic, Ollama, SiliconFlow
- **UI:** Native N-panel chat interface

### Comparison
| Aspect | blender-mcp | GenesisCore |
|--------|-------------|-------------|
| MCP Server | External process | Built-in (FastMCP) |
| MCP Client | External (any) | Built-in (multi-provider) |
| Transport | stdio → TCP :9876 | Internal SSE :45677 |
| LLM Providers | Any (via client) | 6 built-in |
| Asset Sources | 5 (PH, Sketchfab, PP, Rodin, Hunyuan) | 1 (Poly Haven) |
| UI | N-panel (server control) | N-panel (chat + config) |
| Code Execution | `execute_blender_code` | `execute_blender_code` |

---

## Tool Calling Flow

```
User Prompt
     │
     ▼
LLM analyzes → selects tool(s)
     │
     ▼
MCP Client formats tool call
     │
     ▼
┌─────────────────────────────┐
│      Transport Layer        │
│  stdio / SSE / WebSocket    │
└─────────────────────────────┘
     │
     ▼
MCP Server receives → validates
     │
     ▼
Tool handler executes
     │
     ├─ blender-mcp: TCP → Blender addon → bpy
     └─ GenesisCore: Direct bpy (same process)
     │
     ▼
Result → MCP response → LLM
     │
     ▼
LLM continues or responds to user
```

---

## Blender Addon Integration Patterns

### Pattern 1: Socket Server (blender-mcp)
```python
# addon.py - Socket server in background thread
class BlenderMCPServer:
    def __init__(self, host='localhost', port=9876):
        self.socket = socket.socket()
        self.command_queue = queue.Queue()
    
    def _server_loop(self):  # Thread
        while running:
            client, _ = self.socket.accept()
            threading.Thread(target=self._handle_client, args=(client,)).start()
    
    def _drain_command_queue(self):  # bpy.app.timer (main thread)
        while queue:
            cmd, client = queue.get()
            result = self.execute_command(cmd)
            client.send(json.dumps(result))

    def execute_command(self, cmd):
        handler = HANDLERS[cmd['type']]
        return handler(**cmd['params'])
```

### Pattern 2: Built-in MCP Server (GenesisCore)
```python
# src/server/server.py - FastMCP in Blender process
class BlenderMCPServer(FastMCP):
    def __init__(self):
        super().__init__(name="BlenderMCPServer", host="localhost", port=45677)
    
    @self.tool()
    def create_object(self, entity_type: str, ...) -> dict:
        # Direct bpy operations - no IPC needed
        bpy.ops.mesh.primitive_cube_add(...)
        return {"name": obj.name, ...}

# Runs in daemon thread
Server.run()  # Thread(target=Server.main).start()
```

### Pattern 3: MCP Client in Blender (GenesisCore)
```python
# src/client/base.py - Connects to local MCP server
class MCPClientBase:
    async def connect_to_server(self):
        async with sse_client(url="http://localhost:45677/sse") as (read, write):
            self.session = ClientSession(read, write)
            await self.session.initialize()
    
    async def call_tool(self, fn_name, arguments):
        return await self.session.call_tool(fn_name, arguments)
```

---

## Security Considerations

### Safe Mode (blender-mcp)
```bash
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp
```
**Blocks:**
- `import os, subprocess, sys, socket, requests, urllib`
- `open()`, `eval()`, `exec()`, `compile()`
- `bpy.app.handlers`, `bpy.app.timers`, `bpy.app.driver_namespace`
- Class/property registration (`bpy.utils.register_class`)
- External file loading (`bpy.data.libraries.load`)

**Allows:**
- All `bpy.ops.*` (modeling, materials, rendering, save, import/export)
- `bpy.data.*` read/write (objects, meshes, materials, scenes)
- `mathutils`, `math`, `random`, `json`, `uuid` (stdlib)

### Code Execution Risk
Both implementations expose `execute_blender_code`:
```python
# DANGEROUS - full Python access
bpy.ops.wm.open_mainfile(filepath="/etc/passwd")  # Blocked in safe mode
os.system("rm -rf /")  # Blocked in safe mode

# SAFE - Blender operations only
bpy.ops.mesh.primitive_cube_add()
mat = bpy.data.materials.new("Red")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1,0,0,1)
```

**Best Practice:** Always use specific tools (`create_object`, `set_material`) instead of raw code execution.

---

## Environment Variables

### blender-mcp
| Variable | Default | Description |
|----------|---------|-------------|
| `BLENDER_HOST` | `localhost` | Blender addon host |
| `BLENDER_PORT` | `9876` | Blender addon port |
| `BLENDER_MCP_SAFE_MODE` | `0` | Enable safe mode |
| `DISABLE_TELEMETRY` | `false` | Disable telemetry |
| `UV_PYTHON_PREFERENCE` | - | `only-managed` to avoid conda/pyenv |

### GenesisCore
| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | - | API key for OpenRouter |
| `DEEPSEEK_API_KEY` | - | API key for DeepSeek |
| `OPENAI_API_KEY` | - | API key for OpenAI |
| `ANTHROPIC_API_KEY` | - | API key for Anthropic |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |

---

## Adding Custom Tools

### blender-mcp (Server-side)
```python
# src/blender_mcp/tools/my_tool.py
from mcp.server.fastmcp import FastMCP

@mcp.tool()
async def my_custom_tool(param: str) -> str:
    """Description for LLM"""
    blender = get_blender_connection()
    return blender.send_command("my_custom_command", {"param": param})
```

### GenesisCore (Addon-side)
```python
# src/tools/my_tools.py
from .common import ToolsPackageBase

class MyTools(ToolsPackageBase):
    def my_custom_tool(param: str) -> dict:
        """Description for LLM"""
        # Direct bpy access
        return {"result": "success"}

# src/tools/__init__.py
from .my_tools import MyTools  # Order affects UI display
```

### GenesisCore Custom Client
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

## Debugging

### Blender System Console
- **Windows:** Window → Toggle System Console
- **macOS:** `/Applications/Blender.app/Contents/MacOS/Blender` in Terminal
- **Linux:** Run Blender from terminal

### Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| "Connection refused" | Addon not running | N-panel → Start MCP Server |
| "Timeout" | Complex operation | Break into smaller steps |
| "Safe mode rejected" | Forbidden import | Rewrite without os/subprocess |
| Model list empty | API key invalid | Check key + network |
| Poly Pizza 403 | Cloudflare bot check | Residential IP or manual download |

---

## Version Compatibility

| Blender | blender-mcp | GenesisCore | MCP Spec |
|---------|-------------|-------------|----------|
| 3.0+ | ✅ | ❌ | 2024-11-05 |
| 4.0+ | ✅ | ✅ | 2024-11-05 |
| 4.2+ | ✅ | ✅ | 2025-06-18 |

---

## Resources
- [MCP Specification](https://modelcontextprotocol.io/)
- [blender-mcp Repo](https://github.com/ahujasid/blender-mcp)
- [GenesisCore Repo](https://github.com/AIGODLIKE/GenesisCore)
- [FastMCP Python SDK](https://github.com/jlowin/fastmcp)

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md)
- **Теги:** #blender, #mcp, #reference

---

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

