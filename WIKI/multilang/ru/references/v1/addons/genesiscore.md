---
lang: ru
orig_lang: en
translation: ai
---
# АДДОН GENESISCORE — ПОДРОБНЫЙ РАЗБОР

## Обзор
**Репозиторий:** https://github.com/AIGODLIKE/GenesisCore
**Версия:** 0.0.1 | **Blender:** 4.0+ | **Лицензия:** Open Source
**Звёзды:** 134 | **Язык:** Python

GenesisCore — это **полноценный MCP-клиент + сервер**, встроенный прямо в Blender. В отличие от blender-mcp (только сервер), GenesisCore включает и LLM-клиент, поэтому вы общаетесь с ИИ *внутри Blender* через N-панель.

---

## Архитектура

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

## Ключевые возможности

### 1. Встроенный MCP-клиент (внешний хост не нужен)
```python
# В base.py — подключается к локальному MCP-серверу на порту 45677
async def connect_to_server(self):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    stdio_transport = await self.exit_stack.enter_async_context(
        sse_client(url="http://localhost:45677/sse", headers=headers)
    )
```

### 2. Поддержка нескольких провайдеров
| Провайдер | Base URL | Модель по умолчанию |
|----------|----------|---------------|
| **OpenRouter** | `https://openrouter.ai/api` | `anthropic/claude-3.5-haiku` |
| **DeepSeek** | `https://api.deepseek.com` | `deepseek-chat` |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o` |
| **Anthropic** | `https://api.anthropic.com` | `claude-3-5-sonnet` |
| **Ollama** | `http://localhost:11434/v1` | `llama3.2` |
| **SiliconFlow** | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-Coder-32B` |

### 3. Модули инструментов (расширяемые)
Каждый модуль регистрирует инструменты в MCP-сервере:

```python
# common_tools.py — самый мощный инструмент
def execute_blender_code(code: str) -> dict:
    """Выполнить произвольный код Blender Python API"""
    namespace = {"bpy": bpy}
    exec(code, namespace)
    return {"executed": True}
```

**Доступные инструменты:**
| Модуль | Инструменты |
|--------|-------|
| `common_tools` | `get_scene_info`, `get_simple_info`, `execute_blender_code` |
| `object_tools` | `create_object`, `modify_object`, `delete_object`, `get_object_info` |
| `material_tools` | `set_material` (Principled BSDF) |
| `polyhaven_tools` | `search_models`, `fetch_model_info`, `use_model_asset`, `search_hdris`, `use_hdri` |

### 4. Интеграция с Poly Haven
- Кэширует в `%TEMP%\polyhaven_{models|hdris}`
- Автоматически подгружает закэшированные ассеты
- Поддерживает разрешения 1k/2k/4k/8k/16k

### 5. Подключение внешнего MCP-хоста
```json
{
  "mcpServers": {
    "BlenderGenesis": {
      "url": "http://localhost:45677"
    }
  }
}
```
Это позволяет Claude Desktop / Cursor / Codex подключаться к серверу GenesisCore.

---

## Установка

### Способ 1: установка из ZIP (рекомендуется)
1. Скачать: https://github.com/AIGODLIKE/GenesisCore/archive/refs/heads/main.zip
2. Blender → Edit → Preferences → Add-ons → **Install from ZIP**
3. Выбрать ZIP-файл
4. Включить **GenesisCore** (искать "GenesisCore" или "AI")

### Способ 2: git clone (с автообновлениями)
```powershell
cd %APPDATA%\Blender Foundation\Blender\4.2\scripts\addons
git clone https://github.com/AIGODLIKE/GenesisCore.git
```
Затем включить в настройках.

---

## Конфигурация

### Настройка OpenRouter (рекомендуется)
1. Получить API-ключ: https://openrouter.ai/keys
2. В N-панели Blender (нажать `N`) → вкладка **GenesisCore**
3. **Provider:** OpenRouter
4. **API Key:** вставить свой ключ
5. **Fetch Models** → выбрать: `deepseek/deepseek-chat` или `qwen/qwen-2.5-coder-32b`
6. **Tool Modules:** включить все (Shift для множественного выбора)
7. **Save Config**

### Рекомендации по моделям (2026)
| Задача | Модель | Стоимость |
|------|-------|------|
| **Сложные рассуждения** | `anthropic/claude-3.5-sonnet` | $$$ |
| **Код / Blender API** | `deepseek/deepseek-chat` | $ |
| **Быстро и дёшево** | `qwen/qwen-2.5-coder-32b` | $ |
| **Локально (бесплатно)** | `ollama:codellama:13b` | Бесплатно |

---

## Рабочий процесс

```
1. Откройте N-панель (N) → GenesisCore
2. Выберите провайдера и модель
3. Включите модули инструментов (Common, Object, Material, Polyhaven)
4. Введите промпт в поле чата
5. Нажмите Enter / Execute
6. ИИ строит план → вызывает инструменты → выполняет в Blender
7. Результат появляется в чате, вьюпорт обновляется
```

---

## Примеры промптов

### Базовая геометрия
```
"Create a low-poly castle with 4 towers, a central keep, and a moat. Use simple primitives."
```

### Материалы и свет
```
"Create a studio lighting setup: 3-point lighting with key, fill, and rim lights. Make a chrome sphere in center."
```

### Ассеты Poly Haven
```
"Search Poly Haven for a Victorian chair and an HDRI for indoor lighting. Import both and set up the scene."
```

### Сложная сцена
```
"Build a cyberpunk alley scene: wet pavement (use HDRI), neon signs (emission materials), 
steam particles, and a hovering vehicle. Use Poly Haven assets where possible."
```

### Прямое выполнение кода
```
"Execute this code to create a procedural city grid with random building heights"
```
→ ИИ вызывает `execute_blender_code` с полным bpy-скриптом

---

## Продвинутое: разработка своих инструментов

### 1. Создание модуля инструментов
```python
# src/tools/my_tools.py
from .common import ToolsPackageBase

class MyTools(ToolsPackageBase):
    def my_custom_tool(param: str) -> dict:
        """Описание для LLM"""
        # здесь операции bpy
        return {"result": "success"}
```

### 2. Регистрация в `__init__.py`
```python
# src/tools/__init__.py
from .my_tools import MyTools
# Порядок важен для отображения в интерфейсе
```

### 3. Собственный LLM-клиент
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

## Решение проблем

| Проблема | Решение |
|-------|-----|
| **"Connecting..." зависает** | Проверьте, что порт 45677 не заблокирован; перезапустите Blender |
| **Список моделей пуст** | Проверьте API-ключ; проверьте сеть/прокси |
| **Инструменты не появляются** | Включите модули в N-панели (Shift+клик для множественного выбора) |
| **Poly Haven не работает** | Проверьте интернет; кэш лежит в `%TEMP%\polyhaven_*` |
| **Ошибки выполнения кода** | Откройте системную консоль (Window → Toggle System Console) |

---

## Расположение файлов

| Файл | Путь |
|------|------|
| Корень аддона | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\GenesisCore\` |
| Конфиг | `%APPDATA%\Blender Foundation\Blender\4.2\config\genesiscore_config.json` |
| Кэш Poly Haven | `%TEMP%\polyhaven_models\` / `polyhaven_hdris\` |
| Логи | Системная консоль Blender |

---

## Связанные страницы вики
- [Архитектура MCP](../mcp/architecture.md)
- [Паттерны работы с API Blender](../api/scripting-patterns.md)
- [Гайд по промптам](../guides/prompting.md)
- [Сравнение с blender-mcp](blender-mcp.md)

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP ADDON - DEEP DIVE](blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md), [BLENDER-MCP - FULL DOCUMENTATION](blender-mcp-full.md), [DREAM TEXTURES ADDON - DEEP DIVE](dream-textures.md)
- **По темам:** [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [MCP CLIENT CONFIGURATIONS](../mcp/clients.md), [MCP SERVER API REFERENCE](../mcp/server-api.md)
- **Теги:** #addon, #mcp, #reference

