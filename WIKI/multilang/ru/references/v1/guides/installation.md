---
lang: ru
orig_lang: en
translation: ai
---
# РУКОВОДСТВО ПО УСТАНОВКЕ — ПОЛНАЯ НАСТРОЙКА

## Предварительные требования
- Windows 10/11 (это руководство)
- Blender 4.2+
- Python 3.10+ (входит в поставку Blender)
- Интернет-соединение для скачивания моделей

---

## Шаг 1: Установка uv (обязательно)

```powershell
# Установить uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Добавить в PATH (ОБЯЗАТЕЛЬНО — после этого перезапустите PowerShell)
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")

# Проверка
uv --version
uvx --version
```

---

## Шаг 2: Установка Blender

### Вариант A: MSI-установщик (рекомендуется)
```powershell
# Файл уже скачан: C:\BLENDER ai\blender-4.2.3-windows-x64.msi
msiexec /i "C:\BLENDER ai\blender-4.2.3-windows-x64.msi" /quiet /norestart
```

### Вариант B: Portable ZIP
```powershell
# Распаковать в C:\BLENDER ai\Blender
# Запустить: C:\BLENDER ai\Blender\blender.exe
```

### Проверка
```powershell
# Найти путь к Blender
where blender
# Или проверьте: C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
```

---

## Шаг 3: Установка blender-mcp (MCP-сервер + аддон)

```powershell
# Установить аддон в Blender
uvx blender-mcp install-addon

# Проверить путь к аддону
uvx blender-mcp addon-paths
```

---

## Шаг 4: Установка аддона GenesisCore

```powershell
# Уже скачан: C:\BLENDER ai\addons\GenesisCore-main.zip
# В Blender:
# 1. Edit → Preferences → Add-ons → Install from ZIP
# 2. Выбрать: C:\BLENDER ai\addons\GenesisCore-main.zip
# 3. Включить: Search "GenesisCore" → Check box
```

---

## Шаг 5: Установка аддона Dream Textures

```powershell
# Скачать свежий релиз:
# https://github.com/carson-katri/dream-textures/releases/latest
# Скачать: dream_textures-<version>.zip

# В Blender:
# 1. Edit → Preferences → Add-ons → Install from ZIP
# 2. Выбрать скачанный ZIP
# 3. Включить: Dream Textures

# Первый запуск: скачивает PyTorch + diffusers (~2-4 ГБ)
# Preferences → Dream Textures → Download model: stabilityai/stable-diffusion-2-1-base
```

---

## Шаг 6: Настройка OpenCode MCP

Создайте/откройте: `C:\Users\<USERNAME>\.config\opencode\opencode.json`

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

---

## Шаг 7: Настройка GenesisCore (OpenRouter)

1. Получите API-ключ: https://openrouter.ai/keys
2. В Blender: нажмите `N` → вкладка **GenesisCore**
3. **Provider:** OpenRouter
4. **API Key:** вставьте ключ
5. **Fetch Models** → выберите: `deepseek/deepseek-chat` или `qwen/qwen-2.5-coder-32b`
6. **Tool Modules:** включите все (Shift+клик для множественного выбора)
7. **Save Config**

---

## Шаг 8: Запуск серверов

### blender-mcp (для OpenCode/Claude/Cursor)
```powershell
# Терминал 1: запустить MCP-сервер
uvx blender-mcp
# Держать процесс запущенным
```

### В Blender (для обоих)
1. Нажмите `N` → вкладка **MCP for Blender**
2. Отметьте: Poly Haven, Poly Pizza, Sketchfab и т. д.
3. Введите API-ключи в Preferences → Add-ons → MCP for Blender
4. Нажмите **Start MCP Server**

### GenesisCore (для чата внутри Blender)
1. Нажмите `N` → вкладка **GenesisCore**
2. Нажмите **Connect** (подключается к внутреннему серверу на :45677)
3. Общайтесь с ИИ прямо в Blender

---

## Шаг 9: Проверка всего

### Тест blender-mcp (через OpenCode)
```bash
# В чате OpenCode:
"Get the current Blender scene info"
"Create a cube at location (1, 2, 3)"
"Search Poly Haven for a concrete texture and apply to cube"
```

### Тест GenesisCore (в N-панели Blender)
```
Prompt: "Create a low-poly house with a roof, door, and windows"
Prompt: "Add studio lighting: key, fill, rim lights"
Prompt: "Search Poly Haven for an HDRI and set as world environment"
```

### Тест Dream Textures
1. Выберите куб → N-панель → **Dream Textures**
2. Prompt: "weathered brick wall, seamless"
3. Отметьте **Seamless** → Generate
4. Примените к материалу

---

## Необходимые API-ключи

| Сервис | Ключ | Где получить | Где ввести |
|---------|-----|--------------|----------------|
| **OpenRouter** | Обязательно | https://openrouter.ai/keys | N-панель GenesisCore |
| **Poly Pizza** | Бесплатный | https://poly.pizza/settings/api | Blender Preferences → MCP for Blender |
| **Sketchfab** | Обязательно | https://sketchfab.com/developers/api | Blender Preferences → MCP for Blender |
| **Hyper3D** | Обязательно | https://hyper3d.ai/ | Blender Preferences → MCP for Blender |
| **Hunyuan3D** | SecretId/Key | https://3d.hunyuan.tencent.com/ | Blender Preferences → MCP for Blender |
| **DreamStudio** | Опционально | https://beta.dreamstudio.ai/ | Blender Preferences → Dream Textures |

---

## Итоговая структура каталогов

```
C:\BLENDER ai\
├── blender-4.2.3-windows-x64.msi
├── blender-4.2.3-windows-x64.zip
├── CHANGELOG.md
├── INDEX.md
├── addons\
│   ├── GenesisCore-main.zip
│   ├── blender-mcp-full.md
│   ├── blender-mcp.md
│   ├── dream-textures-full.md
│   ├── dream-textures.md
│   └── genesiscore.md
├── mcp\
│   ├── architecture.md
│   ├── clients.md
│   ├── server-api.md
│   └── setup-guide.md
├── guides\
│   ├── installation.md
│   ├── prompting.md
│   ├── troubleshooting.md
│   └── workflows.md
├── api\
│   ├── blender-api.md
│   ├── materials.md
│   ├── mesh-operations.md
│   └── scripting-patterns.md
├── workflows\
│   ├── animation.md
│   ├── scene-building.md
│   ├── text-to-3d.md
│   └── texture-generation.md
└── references\
    └── (additional docs)
```

---

## Краткая сводка по решению проблем

| Проблема | Решение |
|---------|----------|
| `uvx` не найден | Перезапустите PowerShell; проверьте PATH |
| Blender не найден | Выполните `uvx blender-mcp addon-paths` |
| Аддон не отображается | Перезапустите Blender; проверьте папку нужной версии |
| GenesisCore «Connecting...» | Порт 45677 заблокирован; перезапустите Blender |
| Dream Textures OOM | Снизьте разрешение; используйте fp16 |
| Poly Pizza 403 | Ручная загрузка + File → Import → glTF |

---

## Следующие шаги
1. Прочитайте [Гайд по промптам](../guides/prompting.md)
2. Прочитайте [Воркфлоу](../workflows/scene-building.md)
3. Изучите [Паттерны работы с API Blender](../api/scripting-patterns.md)
4. Проверьте [Архитектуру MCP](../mcp/architecture.md)

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [TROUBLESHOOTING GUIDE](troubleshooting.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [DREAM TEXTURES ADDON - DEEP DIVE](../addons/dream-textures.md), [GENESISCORE ADDON - DEEP DIVE](../addons/genesiscore.md)
- **По темам:** [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [SETUP 35: READY PLAYER ME AVATARS](../../../setups/setup_35_readyplayerme.md), [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md)
- **Теги:** #addon, #blender, #mcp, #reference, #stable-diffusion
