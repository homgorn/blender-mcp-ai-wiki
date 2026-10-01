---
lang: en
tags: [mcp, reference]
---
# MCP CLIENT CONFIGURATIONS

## OpenCode
**Config:** `~/.config/opencode/opencode.json`
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

## Claude Desktop
**Config:** `claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/`
- Windows: `%APPDATA%\Claude\`
- Linux: `~/.config/claude/`

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

**Claude Code CLI:**
```bash
claude mcp add blender uvx blender-mcp
```

## Cursor
**Settings → MCP → Add Server**
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
**Windows:** Use `"command": "cmd", "args": ["/c", "uvx", "blender-mcp"]`

## VS Code (with MCP extension)
**Settings → Extensions → MCP → Add Server**
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

## Codex
**CLI:**
```bash
codex mcp add blender -- uvx blender-mcp
```
**Config:** `~/.codex/config.toml`
```toml
[mcp_servers.blender]
command = "uvx"
args = ["blender-mcp"]
env = { BLENDER_HOST = "localhost", BLENDER_PORT = "9876" }
```

**Desktop App:** Settings → MCP Servers → Add Server → name: `blender`, STDIO, command: `uvx blender-mcp`

## Antigravity
```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Docker (Alternative)
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
**Linux:** Add `"--network=host", "-e", "BLENDER_HOST=localhost"`

## Environment Variables (All Clients)
```json
"environment": {
  "BLENDER_HOST": "localhost",
  "BLENDER_PORT": "9876",
  "BLENDER_MCP_SAFE_MODE": "0",
  "DISABLE_TELEMETRY": "false",
  "UV_PYTHON_PREFERENCE": "only-managed"
}
```

## Python Version Pinning (Recommended)
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

## Troubleshooting Client Connections

| Issue | Fix |
|-------|-----|
| `spawn uvx ENOENT` | Use full path: `which uvx` / `where uvx` → put in `command` |
| Connection refused | Blender addon not running; click "Start MCP Server" |
| Tools not appearing | Restart client after config change (full quit) |
| Timeout on first call | Normal; retry once |

## GenesisCore (Built-in Client)
No external MCP client needed. Configure in Blender N-panel:
1. Provider: OpenRouter / DeepSeek / OpenAI / Anthropic / Ollama / SiliconFlow
2. API Key
3. Model selection
4. Tool modules (Common, Object, Material, Polyhaven, Asset)
5. Connect (uses internal SSE on :45677)

**External clients can connect to GenesisCore:**
```json
{
  "mcpServers": {
    "BlenderGenesis": {
      "url": "http://localhost:45677"
    }
  }
}
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [GENESISCORE ADDON - DEEP DIVE](../addons/genesiscore.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](architecture.md)
- **По темам:** [MCP SERVER API REFERENCE](server-api.md), [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **Теги:** #mcp, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

