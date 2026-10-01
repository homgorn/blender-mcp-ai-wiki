---
lang: ru
orig_lang: en
translation: ai
---
# АРХИТЕКТУРА MCP — ПРОТОКОЛ MODEL CONTEXT ДЛЯ BLENDER

## Обзор
MCP (Model Context Protocol) — открытый стандарт для подключения ИИ-ассистентов к внешним инструментам и данным. В контексте Blender он позволяет LLM напрямую управлять Blender через структурированные вызовы инструментов.

---

## Спецификация протокола

### Варианты транспорта
| Транспорт | Сценарий использования | Пример |
|-----------|------------------------|---------|
| **stdio** | Локальный подпроцесс | `uvx blender-mcp` |
| **SSE** | Долгий опрос по HTTP (long-polling) | GenesisCore на :45677 |
| **WebSocket** | Двунаправленный | В будущем |

### Формат сообщений
```json
// Запрос (клиент → сервер)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_object",
    "arguments": {"entity_type": "CUBE", "name": "MyCube"}
  }
}

// Ответ (сервер → клиент)
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

## Реализации MCP для Blender

### 1. blender-mcp (эталонный сервер)
- **Архитектура:** внешний MCP-сервер (uvx) + аддон Blender (TCP :9876)
- **Транспорт:** stdio → TCP
- **Инструменты:** 28+ (сцена, объекты, материалы, 5 источников ассетов, генерация 3D по ИИ)
- **Клиенты:** любой совместимый с MCP (Claude, Cursor, Codex, OpenCode и др.)

### 2. GenesisCore (всё в одном)
- **Архитектура:** аддон Blender со встроенными MCP-клиентом и MCP-сервером
- **Транспорт:** внутренний SSE (:45677) + внешний SSE для других клиентов
- **Провайдеры:** OpenRouter, DeepSeek, OpenAI, Anthropic, Ollama, SiliconFlow
- **UI:** встроенный чат в N-панели

### Сравнение
| Аспект | blender-mcp | GenesisCore |
|--------|-------------|-------------|
| MCP-сервер | Внешний процесс | Встроенный (FastMCP) |
| MCP-клиент | Внешний (любой) | Встроенный (несколько провайдеров) |
| Транспорт | stdio → TCP :9876 | Внутренний SSE :45677 |
| LLM-провайдеры | Любой (через клиент) | 6 встроенных |
| Источники ассетов | 5 (PH, Sketchfab, PP, Rodin, Hunyuan) | 1 (Poly Haven) |
| UI | N-панель (управление сервером) | N-панель (чат + конфигурация) |
| Выполнение кода | `execute_blender_code` | `execute_blender_code` |

---

## Схема вызова инструментов

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

## Паттерны интеграции аддона в Blender

### Паттерн 1: сокетный сервер (blender-mcp)
```python
# addon.py — сокетный сервер в фоновом потоке
class BlenderMCPServer:
    def __init__(self, host='localhost', port=9876):
        self.socket = socket.socket()
        self.command_queue = queue.Queue()
    
    def _server_loop(self):  # Поток
        while running:
            client, _ = self.socket.accept()
            threading.Thread(target=self._handle_client, args=(client,)).start()
    
    def _drain_command_queue(self):  # bpy.app.timer (главный поток)
        while queue:
            cmd, client = queue.get()
            result = self.execute_command(cmd)
            client.send(json.dumps(result))

    def execute_command(self, cmd):
        handler = HANDLERS[cmd['type']]
        return handler(**cmd['params'])
```

### Паттерн 2: встроенный MCP-сервер (GenesisCore)
```python
# src/server/server.py — FastMCP внутри процесса Blender
class BlenderMCPServer(FastMCP):
    def __init__(self):
        super().__init__(name="BlenderMCPServer", host="localhost", port=45677)
    
    @self.tool()
    def create_object(self, entity_type: str, ...) -> dict:
        # Прямые операции bpy — IPC не требуется
        bpy.ops.mesh.primitive_cube_add(...)
        return {"name": obj.name, ...}

# Выполняется в потоке-демоне
Server.run()  # Thread(target=Server.main).start()
```

### Паттерн 3: MCP-клиент внутри Blender (GenesisCore)
```python
# src/client/base.py — подключается к локальному MCP-серверу
class MCPClientBase:
    async def connect_to_server(self):
        async with sse_client(url="http://localhost:45677/sse") as (read, write):
            self.session = ClientSession(read, write)
            await self.session.initialize()
    
    async def call_tool(self, fn_name, arguments):
        return await self.session.call_tool(fn_name, arguments)
```

---

## Вопросы безопасности

### Безопасный режим (blender-mcp)
```bash
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp
```
**Блокирует:**
- `import os, subprocess, sys, socket, requests, urllib`
- `open()`, `eval()`, `exec()`, `compile()`
- `bpy.app.handlers`, `bpy.app.timers`, `bpy.app.driver_namespace`
- Регистрацию классов/свойств (`bpy.utils.register_class`)
- Загрузку внешних файлов (`bpy.data.libraries.load`)

**Разрешает:**
- Все `bpy.ops.*` (моделирование, материалы, рендер, сохранение, импорт/экспорт)
- Чтение/запись `bpy.data.*` (объекты, меши, материалы, сцены)
- `mathutils`, `math`, `random`, `json`, `uuid` (stdlib)

### Риск выполнения кода
Обе реализации предоставляют `execute_blender_code`:
```python
# ОПАСНО — полный доступ к Python
bpy.ops.wm.open_mainfile(filepath="/etc/passwd")  # Блокируется в безопасном режиме
os.system("rm -rf /")  # Блокируется в безопасном режиме

# БЕЗОПАСНО — только операции Blender
bpy.ops.mesh.primitive_cube_add()
mat = bpy.data.materials.new("Red")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1,0,0,1)
```

**Лучшая практика:** всегда используйте конкретные инструменты (`create_object`, `set_material`) вместо прямого выполнения кода.

---

## Переменные окружения

### blender-mcp
| Переменная | По умолчанию | Описание |
|------------|---------------|----------|
| `BLENDER_HOST` | `localhost` | Хост аддона Blender |
| `BLENDER_PORT` | `9876` | Порт аддона Blender |
| `BLENDER_MCP_SAFE_MODE` | `0` | Включить безопасный режим |
| `DISABLE_TELEMETRY` | `false` | Отключить телеметрию |
| `UV_PYTHON_PREFERENCE` | - | `only-managed`, чтобы избежать conda/pyenv |

### GenesisCore
| Переменная | По умолчанию | Описание |
|------------|---------------|----------|
| `OPENROUTER_API_KEY` | - | API-ключ OpenRouter |
| `DEEPSEEK_API_KEY` | - | API-ключ DeepSeek |
| `OPENAI_API_KEY` | - | API-ключ OpenAI |
| `ANTHROPIC_API_KEY` | - | API-ключ Anthropic |
| `OLLAMA_HOST` | `http://localhost:11434` | Эндпоинт Ollama |

---

## Добавление своих инструментов

### blender-mcp (на стороне сервера)
```python
# src/blender_mcp/tools/my_tool.py
from mcp.server.fastmcp import FastMCP

@mcp.tool()
async def my_custom_tool(param: str) -> str:
    """Description for LLM"""
    blender = get_blender_connection()
    return blender.send_command("my_custom_command", {"param": param})
```

### GenesisCore (на стороне аддона)
```python
# src/tools/my_tools.py
from .common import ToolsPackageBase

class MyTools(ToolsPackageBase):
    def my_custom_tool(param: str) -> dict:
        """Description for LLM"""
        # Прямой доступ к bpy
        return {"result": "success"}

# src/tools/__init__.py
from .my_tools import MyTools  # Порядок влияет на отображение в UI
```

### GenesisCore: собственный клиент
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

## Отладка

### Системная консоль Blender
- **Windows:** Window → Toggle System Console
- **macOS:** `/Applications/Blender.app/Contents/MacOS/Blender` в терминале
- **Linux:** запустите Blender из терминала

### Типичные проблемы
| Симптом | Причина | Решение |
|---------|---------|---------|
| "Connection refused" | Аддон не запущен | N-панель → Start MCP Server |
| "Timeout" | Сложная операция | Разбить на более мелкие шаги |
| "Safe mode rejected" | Запрещённый импорт | Переписать без os/subprocess |
| Список моделей пуст | Неверный API-ключ | Проверить ключ и сеть |
| Poly Pizza 403 | Проверка Cloudflare на бота | Домашний IP или ручная загрузка |

---

## Совместимость версий

| Blender | blender-mcp | GenesisCore | Спецификация MCP |
|---------|-------------|-------------|----------|
| 3.0+ | ✅ | ❌ | 2024-11-05 |
| 4.0+ | ✅ | ✅ | 2024-11-05 |
| 4.2+ | ✅ | ✅ | 2025-06-18 |

---

## Ресурсы
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

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

