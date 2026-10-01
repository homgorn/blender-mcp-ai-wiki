---
lang: ru
orig_lang: en
translation: ai
---
# BLENDER-MCP — ПОЛНАЯ ДОКУМЕНТАЦИЯ

## Обзор
**Репозиторий:** https://github.com/ahujasid/blender-mcp
**Сайт:** https://mcp-for-blender.com/
**Версия:** 1.6+ | **Blender:** 3.0+ | **Лицензия:** MIT
**PyPI:** `blender-mcp` | **Discord:** https://discord.gg/SNqPn4TcKQ

---

## Архитектура

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

## Установка

### Предварительные требования
- Blender 3.0+
- Python 3.10+
- Пакетный менеджер **uv** (обязателен)

### Установка uv
```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Добавить в PATH (после этого перезапустить оболочку)
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

### Быстрая установка
```bash
# 1. Установить аддон Blender
uvx blender-mcp install-addon

# 2. Настроить MCP-клиент (см. ниже)

# 3. В Blender: N-панель → MCP for Blender → Start MCP Server
```

---

## Настройка MCP-клиента

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
Конфиг: `claude_desktop_config.json` (Settings → Developer → Edit Config)

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
Settings → MCP → Add Server (Windows: используйте `"command": "cmd", "args": ["/c", "uvx", "blender-mcp"]`)

### Codex
```bash
codex mcp add blender -- uvx blender-mcp
```
Или `~/.codex/config.toml`:
```toml
[mcp_servers.blender]
command = "uvx"
args = ["blender-mcp"]
env = { BLENDER_HOST = "localhost", BLENDER_PORT = "9876" }
```

---

## Доступные инструменты (28+)

### Базовые инструменты сцены
| Инструмент | Описание |
|------|-------------|
| `get_scene_info` | Полная иерархия сцены (ограничено 10 объектами) |
| `get_object_info` | Подробные данные объекта (трансформация, меш, материалы) |
| `get_world_state_snapshot` | Компактный снимок для траектории (потолок 4000 объектов) |
| `get_viewport_screenshot` | GPU-рендер offscreen → Image |
| `execute_blender_code` | **Выполнение произвольного Python-кода** (пошагово!) |
| `get_addon_info` | Рукопожатие версии/возможностей |

### Инструменты материалов
| Инструмент | Описание |
|------|-------------|
| `set_texture` | Применение загруженной текстуры Poly Haven к объекту |

### Poly Haven (бесплатно, без ключа)
| Инструмент | Описание |
|------|-------------|
| `get_polyhaven_categories` | Список категорий для hdris/textures/models |
| `search_polyhaven_assets` | Поиск с фильтрами по типу и категории |
| `download_polyhaven_asset` | Скачивание + импорт (HDRI→world, Texture→material, Model→scene) |
| `get_polyhaven_status` | Проверка, включён ли в Blender |

### Poly Pizza (бесплатный API-ключ)
| Инструмент | Описание |
|------|-------------|
| `get_polypizza_status` | Проверка, включён ли |
| `search_polypizza_models` | Запрос, категория (0-11), лицензия (0=CC-BY,1=CC0), animated, limit |
| `download_polypizza_model` | Импорт GLB, normalize_size, target_size (метры) |

**Категории:** 0=Food&Drink, 1=Clutter, 2=Weapons, 3=Transport, 4=Furniture&Decor, 5=Objects, 6=Nature, 7=Animals, 8=Buildings, 9=People&Characters, 10=Scenes&Levels, 11=Other

**Лицензия:** 0=CC-BY (нужен кредит), 1=CC0 (кредит не нужен)

### Sketchfab (API-ключ)
| Инструмент | Описание |
|------|-------------|
| `get_sketchfab_status` | Проверка, включён ли |
| `search_sketchfab_models` | Запрос, категории, количество, downloadable |
| `get_sketchfab_model_preview` | Миниатюра Image для визуальной проверки |
| `download_sketchfab_model` | Импорт, normalize_size, **target_size обязателен** (метры) |

### Hyper3D Rodin (API-ключ)
| Инструмент | Описание |
|------|-------------|
| `get_hyper3d_status` | Проверка, включён ли |
| `create_rodin_job` | Отправка задания генерации |
| `poll_rodin_job_status` | Проверка статуса задания |
| `import_generated_asset` | Импорт готовой модели |

### Hunyuan3D (SecretId/SecretKey)
| Инструмент | Описание |
|------|-------------|
| `get_hunyuan3d_status` | Проверка, включён ли |
| `create_hunyuan_job` | Отправка задания генерации |
| `poll_hunyuan_job_status` | Проверка статуса задания |
| `import_generated_asset_hunyuan` | Импорт готовой модели |

---

## Постоянные учётные данные API

### Настройки Blender (переживают перезапуск)
Edit → Preferences → Add-ons → MCP for Blender:
- Sketchfab API Key
- Poly Pizza API Key
- Hyper3D API Key
- Hunyuan3D SecretId / SecretKey / API URL

### Переменные окружения (headless/CI)
```bash
BLENDERMCP_SKETCHFAB_API_KEY
BLENDERMCP_POLYPIZZA_API_KEY
BLENDERMCP_HYPER3D_API_KEY
BLENDERMCP_HUNYUAN3D_SECRET_ID
BLENDERMCP_HUNYUAN3D_SECRET_KEY
BLENDERMCP_HUNYUAN3D_API_URL
```

---

## Безопасный режим

Блокирует рискованные операции в `execute_blender_code`:
- Ввод-вывод файлов, сеть, подпроцессы
- Хендлеры/таймеры/драйверы
- Регистрация классов/свойств
- Загрузка внешних .blend

**Включение:**
```bash
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp
```
Или в конфиге MCP:
```json
{ "mcpServers": { "blender": { "command": "uvx", "args": ["blender-mcp"], "env": { "BLENDER_MCP_SAFE_MODE": "1" } } } }
```

**Разрешено:** операторы Blender (моделирование, материалы, рендер, сохранение, импорт/экспорт)

---

## Развёртывание в Docker

```bash
# Сборка
docker build -t blender-mcp .

# macOS/Windows (Docker Desktop)
docker run -i --rm blender-mcp

# Linux (сеть хоста)
docker run -i --rm --network=host -e BLENDER_HOST=localhost blender-mcp
```

Конфиг MCP:
```json
{ "mcpServers": { "blender": { "command": "docker", "args": ["run", "-i", "--rm", "blender-mcp"] } } }
```

---

## Фиксация версии Python

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

## Решение проблем

| Проблема | Решение |
|-------|-----|
| `spawn uvx ENOENT` | Укажите полный путь: `which uvx` / `where uvx` |
| Отказано в соединении | Аддон Blender не запущен; нажмите "Start MCP Server" |
| Poly Pizza Cloudflare 403 | Скачайте .glb вручную → File → Import → glTF |
| Таймаут | Разбейте сложные запросы на шаги |
| Конфликт версий | `uv cache clean blender-mcp && uvx --refresh blender-mcp` |
| Headless Blender (`-b`) | Команды не выполняются; используйте GUI или `xvfb-run -a blender` |

---

## Расположение файлов

| Файл | Путь |
|------|------|
| Аддон (установлен) | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\blender_mcp.py` |
| Аддон (исходники) | `addon.py` в репозитории |
| MCP-сервер | `uvx blender-mcp` (из кэша) |
| Конфиг (настройки Blender) | Edit → Preferences → Add-ons → MCP for Blender |
| Логи | Системная консоль Blender (Window → Toggle System Console) |

---

## Телеметрия
- **По умолчанию:** ВКЛ (анонимные данные об использовании)
- **Отключение в Blender:** Preferences → Add-ons → MCP for Blender → снять галку с телеметрии
- **Отключение через env:** `DISABLE_TELEMETRY=true uvx blender-mcp`
- **Данные:** имя инструмента, успех, длительность, промпты, код, скриншоты, данные сцены
- **Условия:** см. `TERMS_AND_CONDITIONS.md` в репозитории

---

## Исходный код аддона (addon.py) — ключевые классы

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

### Ключевые обработчики
- `get_scene_info()` — Упрощённые данные сцены
- `get_world_state_snapshot()` — Компактный снимок траектории
- `get_object_info(name)` — Полные детали объекта
- `get_viewport_screenshot()` — GPU-рендер offscreen
- `execute_code(code)` — **Произвольный Python** (с проверкой безопасного режима)
- `drain_human_activity()` — Захват undo/redo/операторов
- Обработчики Poly Haven / Sketchfab / Poly Pizza / Hyper3D / Hunyuan3D

### Захват ручных правок
- Записывает операторы пользователя (кроме игнорируемых) во время MCP-сессии
- Хендлеры `undo_post` / `redo_post` / `depsgraph_update_post`
- Работает только при согласии на телеметрию и запущенном сервере
- Сбрасывается инструментом `drain_human_activity()`

---

## Протокол
- **Транспорт:** TCP-сокет (JSON поверх raw-сокета)
- **Порт:** 9876 (настраивается через `BLENDER_PORT`)
- **Команда:** `{"type": "cmd_name", "params": {...}}`
- **Ответ:** `{"status": "success|error", "result": {...}}` или `{"status": "error", "message": "..."}`
- **Блокировки:** однопоточная очередь команд в главном потоке Blender

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP ADDON - DEEP DIVE](blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md)
- **Теги:** #blender, #mcp, #reference

