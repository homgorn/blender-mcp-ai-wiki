---
lang: ru
orig_lang: en
translation: ai
---
# АДДОН BLENDER-MCP — ПОДРОБНЫЙ РАЗБОР

## Обзор
**Репозиторий:** https://github.com/ahujasid/blender-mcp
**Версия:** Latest | **Blender:** 3.0+ | **Лицензия:** MIT
**Звёзды:** 28.3k | **PyPI:** `blender-mcp`

blender-mcp — это **референсная реализация MCP-сервера** для Blender. Он работает как отдельный Python-процесс (через `uvx`) и подключается к лёгкому аддону Blender через TCP-сокет (порт 9876).

---

## Архитектура

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

## Ключевые отличия от GenesisCore

| Аспект | GenesisCore | blender-mcp |
|--------|-------------|-------------|
| **MCP-клиент** | Встроенный (несколько провайдеров) | Внешний (любой MCP-клиент) |
| **MCP-сервер** | Встроенный (FastMCP на :45677) | Внешний процесс (uvx) |
| **Транспорт** | SSE (внутренний) | stdio → TCP :9876 |
| **Источники ассетов** | Только Poly Haven | Poly Haven + Poly Pizza + Sketchfab + Hyper3D + Hunyuan3D |
| **Установка** | ZIP/Git в Blender | `uvx blender-mcp install-addon` |
| **Конфигурация** | N-панель Blender | Конфиг MCP-клиента + настройки аддона Blender |

---

## Установка

### Предварительные требования
```powershell
# Установить uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Добавить в PATH (после этого перезапустить оболочку)
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

### Быстрая установка
```powershell
# 1. Установить аддон Blender
uvx blender-mcp install-addon

# 2. Настроить MCP-клиент (см. ниже)

# 3. В Blender: N-панель → MCP for Blender → Start MCP Server
```

### Настройка MCP-клиента

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

## Доступные инструменты (v2026)

### Базовые инструменты сцены
| Инструмент | Описание |
|------|-------------|
| `get_scene_info` | Полная иерархия сцены |
| `get_object_info` | Подробные данные объекта |
| `create_object` | Примитивы: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT |
| `modify_object` | Трансформация + видимость |
| `delete_object` | Удаление по имени |
| `execute_blender_code` | **Выполнение произвольного Python-кода** |

### Инструменты материалов
| Инструмент | Описание |
|------|-------------|
| `set_material` | Создание/применение Principled BSDF с цветом |

### Инструменты ассетов (нужны API-ключи)
| Источник | Инструменты | Настройка |
|--------|-------|-------|
| **Poly Haven** | `search_polyhaven_assets`, `download_polyhaven_asset` | Бесплатно, без ключа |
| **Poly Pizza** | `search_polypizza_models`, `download_polypizza_model` | Бесплатный API-ключ |
| **Sketchfab** | `search_sketchfab_models`, `download_sketchfab_model` | API-ключ |
| **Hyper3D Rodin** | `generate_rodin_model`, `get_rodin_generation_status` | API-ключ |
| **Hunyuan3D** | `generate_hunyuan3d_model`, `get_hunyuan3d_status` | SecretId/SecretKey |

---

## Интеграция с Poly Pizza (уникально для blender-mcp)

```python
# 1. Получить бесплатный API-ключ: https://poly.pizza/settings/api
# 2. В Blender: N-панель → MCP for Blender → отметить "Use Poly Pizza" → вставить ключ
# 3. Либо задать переменную окружения: BLENDERMCP_POLYPIZZA_API_KEY

# Пример запроса к ИИ:
# "Search Poly Pizza for a low-poly chair under CC0 license and import at 1 meter tall"
```

**Лицензирование:** ~69% CC-BY (требует атрибуции); фильтруйте через `licence="CC0"`, если атрибуция не нужна.

---

## Генерация 3D через ИИ (уникально для blender-mcp)

### Hyper3D Rodin
```python
# Требуется API-ключ с https://hyper3d.ai/
# Переменная окружения: BLENDERMCP_HYPER3D_API_KEY
# Запрос к ИИ: "Generate a 3D model of a garden gnome through Hyper3D"
```

### Hunyuan3D (Tencent)
```python
# Требуется SecretId/SecretKey с https://3d.hunyuan.tencent.com/
# Переменные окружения: BLENDERMCP_HUNYUAN3D_SECRET_ID / SECRET_KEY / API_URL
# Запрос к ИИ: "Create a 3D model of a futuristic car using Hunyuan3D"
```

---

## Безопасный режим

```bash
# Включить безопасный режим (блокирует ввод-вывод файлов, сеть, подпроцессы, постоянный код)
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp
```

Или в конфиге MCP:
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

## Развёртывание в Docker

```bash
# Сборка
docker build -t blender-mcp .

# Запуск (macOS/Windows с Docker Desktop)
docker run -i --rm blender-mcp

# Запуск (Linux — сеть хоста)
docker run -i --rm --network=host -e BLENDER_HOST=localhost blender-mcp
```

Конфиг MCP:
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
| `spawn uvx ENOENT` | Укажите полный путь к uvx: `which uvx` / `where uvx` |
| Отказано в соединении | Аддон Blender не запущен; нажмите "Start MCP Server" |
| Poly Pizza Cloudflare | Скачайте .glb вручную → File → Import → glTF |
| Таймаут | Разбейте сложные запросы на шаги |
| Конфликт версий | `uv cache clean blender-mcp && uvx --refresh blender-mcp` |

---

## Расположение файлов

| Файл | Путь |
|------|------|
| Аддон (установлен) | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\blender_mcp.py` |
| Аддон (исходники) | `addon.py` в репозитории |
| MCP-сервер | `uvx blender-mcp` (запускается из кэша) |
| Конфиг (настройки Blender) | Edit → Preferences → Add-ons → MCP for Blender |
| Логи | Системная консоль Blender |

---

## Связанные страницы вики
- [Архитектура MCP](../mcp/architecture.md)
- [Сравнение с GenesisCore](genesiscore.md)
- [Настройка MCP-клиента](../mcp/clients.md)
- [Гайд по промптам](../guides/prompting.md)

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md), [BLENDER-MCP - FULL DOCUMENTATION](blender-mcp-full.md), [GENESISCORE ADDON - DEEP DIVE](genesiscore.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md)
- **По темам:** [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md)
- **Теги:** #addon, #blender, #mcp, #reference

