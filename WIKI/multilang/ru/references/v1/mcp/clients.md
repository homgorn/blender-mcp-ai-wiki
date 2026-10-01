---
lang: ru
orig_lang: en
translation: ai
---
# КОНФИГУРАЦИИ MCP-КЛИЕНТОВ

## OpenCode
**Конфиг:** `~/.config/opencode/opencode.json`
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
**Конфиг:** `claude_desktop_config.json`
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
**Windows:** используйте `"command": "cmd", "args": ["/c", "uvx", "blender-mcp"]`

## VS Code (с MCP-расширением)
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
**Конфиг:** `~/.codex/config.toml`
```toml
[mcp_servers.blender]
command = "uvx"
args = ["blender-mcp"]
env = { BLENDER_HOST = "localhost", BLENDER_PORT = "9876" }
```

**Десктопное приложение:** Settings → MCP Servers → Add Server → name: `blender`, STDIO, command: `uvx blender-mcp`

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

## Docker (альтернатива)
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
**Linux:** добавьте `"--network=host", "-e", "BLENDER_HOST=localhost"`

## Переменные окружения (все клиенты)
```json
"environment": {
  "BLENDER_HOST": "localhost",
  "BLENDER_PORT": "9876",
  "BLENDER_MCP_SAFE_MODE": "0",
  "DISABLE_TELEMETRY": "false",
  "UV_PYTHON_PREFERENCE": "only-managed"
}
```

## Фиксация версии Python (рекомендуется)
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

## Диагностика подключений клиентов

| Проблема | Решение |
|-------|-----|
| `spawn uvx ENOENT` | Укажите полный путь: `which uvx` / `where uvx` → впишите в `command` |
| Connection refused | Аддон Blender не запущен; нажмите "Start MCP Server" |
| Инструменты не появляются | Перезапустите клиент после правки конфига (полный выход) |
| Таймаут при первом вызове | Это нормально; повторите один раз |

## GenesisCore (встроенный клиент)
Внешний MCP-клиент не нужен. Настройте в N-панели Blender:
1. Провайдер: OpenRouter / DeepSeek / OpenAI / Anthropic / Ollama / SiliconFlow
2. API-ключ
3. Выбор модели
4. Модули инструментов (Common, Object, Material, Polyhaven, Asset)
5. Подключение (использует внутренний SSE на :45677)

**Внешние клиенты могут подключаться к GenesisCore:**
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

