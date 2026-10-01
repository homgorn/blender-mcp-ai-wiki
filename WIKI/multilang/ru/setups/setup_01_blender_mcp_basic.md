---
id: setup_01_blender_mcp_basic
lang: ru
orig_lang: ru
category: setups
type: setup
difficulty: 1
translation: template
---
# СЕТАП 01: BLENDER-MCP BASIC

> Цель: ## 🌍 MULTILANG

**ID:** setup_01_blender_mcp_basic | **Lang:** ru | **Orig:** ru | **Category:** setups | **Tags:** 

---

# SETUP 01: BLENDER-MCP BASIC

**ID:** SETUP-01 | **Тип:** Core Infrastructure | **Сложность:** ⭐ | **Время:** 10-15 мин

---

## 🎯 ЦЕЛЬ
Установка и настройка blender-mcp для работы с IDE агентами (OpenCode, Cursor, VS Code, Codex, Claude Desktop)

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

| Компонент | Версия | Статус |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Обязательно |
| **Python** | 3.10+ | ✅ Встроен в Blender |
| **uv** | latest | ✅ Обязательно |
| **Git** | latest | ⚠️ Опционально |

---

## 🪟 WINDOWS УСТАНОВКА (ПОШАГОВО)

### 1. Установка uv
```powershell
# PowerShell от администратора
irm https://astral.sh/uv/install.ps1 | iex

# Перезапустить терминал
# Проверить
uv --version
uvx --version
```

### 2. Установка blender-mcp аддона
```powershell
# Автоматическая установка в Blender
uvx blender-mcp install-addon

# Проверить путь
uvx blender-mcp addon-paths
# Должен показать: C:\Users\<USER>\AppData\Roaming\Blender Foundation\Blender\4.x\scripts\addons\blender_mcp.py
```

### 3. Настройка PATH (если uvx не найден)
```powershell
# Найти uvx
where uvx
# Обычно: C:\Users\<USER>\.local\bin\uvx.exe

# Добавить в User PATH
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
# Перезапустить терминал/IDE
```

---

## 🔧 BLENDER НАСТРОЙКА

### 1. Включить аддон
```
Edit → Preferences → Add-ons
Search: "MCP for Blender"
☑ Interface: MCP for Blender
```

### 2. Запустить MCP Server
```
N-Panel (клавиша N) → вкладка "MCP for Blender"
☑ Poly Haven
☑ Poly Pizza (вставить API ключ)
☐ Sketchfab (опционально)
☐ Hyper3D / Hunyuan3D (опционально)
🟢 Кнопка: "Start MCP Server"
```

### 3. Проверить в System Console
```
Window → Toggle System Console
Должно появиться:
"BlenderMCP server started on localhost:9876"
```

---

## 🤖 IDE АГЕНТЫ КОНФИГУРАЦИЯ

### OpenCode (`~/.config/opencode/opencode.jsonc`)
```jsonc
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

### Cursor (Settings → MCP → Add Server)
```json
{
  "mcpServers": {
    "blender": {
      "command": "cmd",
      "args": ["/c", "uvx", "blender-mcp"]
    }
  }
}
```

### VS Code (MCP Extension)
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

### Codex
```bash
codex mcp add blender -- uvx blender-mcp
```

### Claude Desktop (`claude_desktop_config.json`)
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

## ✅ ТЕСТ ПОДКЛЮЧЕНИЯ

### В OpenCode / терминале:
```bash
# Простой тест
"Получи информацию о текущей сцене"
```

### Ожидаемый ответ:
```json
{
  "name": "Scene",
  "object_count": 2,
  "objects": [
    {"name": "Cube", "type": "MESH", "location": [0, 0, 0]},
    {"name": "Light", "type": "LIGHT", "location": [0, 0, 5]}
  ],
  "materials_count": 1
}
```

### Тест создания объекта:
```bash
"Создай куб 'TestCube' в позиции (2, 0, 0) с масштабом (1, 2, 1)"
```

---

## 🔑 API КЛЮЧИ (ОПЦИОНАЛЬНО)

| Сервис | Где получить | Куда вставить |
|--------|--------------|---------------|
| **Poly Pizza** | https://poly.pizza/settings/api | Blender Preferences → Add-ons → MCP for Blender → Poly Pizza API Key |
| **Sketchfab** | https://sketchfab.com/developers/api | Blender Preferences → Add-ons → MCP for Blender → Sketchfab API Key |
| **Hyper3D** | https://hyper3d.ai/ | Blender Preferences → Add-ons → MCP for Blender → Hyper3D API Key |
| **Hunyuan3D** | https://3d.hunyuan.tencent.com/ | Blender Preferences → Add-ons → MCP for Blender → SecretId/SecretKey |

---

## ⚠️ ЧАСТЫЕ ПРОБЛЕМЫ

| Проблема | Решение |
|----------|---------|
| `spawn uvx ENOENT` | Добавить `~/.local/bin` в PATH, перезапустить IDE |
| `Connection refused` | Blender не запущен или MCP Server не стартовал (N-panel → Start) |
| `Timeout` | Слишком сложный запрос → разбить на шаги |
| `Poly Pizza 403` | Cloudflare блок → скачать .glb вручную → File → Import → glTF |
| `ModuleNotFoundError: mcp` | Запустить Blender от админа один раз для автоустановки deps |

---

## 🔗 СВЯЗИ

- **Промпты:** [P01-P05](../prompts/) — базовые команды
- **Кейсы:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Воркфлоу:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **MCP Docs:** [MCP Tools Reference](../references/v1/mcp/server-api.md)
- **Следующий:** [Setup 02: GenesisCore Local](../setups/setup_02_genesiscore_local.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/setups/setup_01_blender_mcp_basic.md` |
| Русский | `multilang/ru/setups/setup_01_blender_mcp_basic.md` |