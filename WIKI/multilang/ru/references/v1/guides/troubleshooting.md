---
lang: ru
orig_lang: en
translation: ai
---
# ГАЙД ПО РЕШЕНИЮ ПРОБЛЕМ

## Проблемы с установкой Blender

### Сбой установки MSI (код возврата 1620)
```powershell
# Проверить лог установки
Get-Content C:\BLENDER ai\install.log -Tail 50

# Типичные причины:
# - Требуется перезагрузка
# - Уже запущен другой процесс установки MSI
# - Недостаточно прав (запускать от имени администратора)
# - Повреждённая загрузка

# Решение: скачать заново, запустить от имени администратора
Start-Process msiexec.exe -ArgumentList "/i C:\BLENDER ai\blender-4.2.3-windows-x64.msi /qb" -Verb RunAs -Wait
```

### Blender не найден после установки
```powershell
# Проверить типовые расположения
Test-Path "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
Test-Path "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
Get-ChildItem "$env:LOCALAPPDATA\Programs\Blender Foundation\" -Recurse -Filter blender.exe
Get-ChildItem "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\" -Recurse -Filter "*lender*"

# Используйте portable-версию
# Распакуйте ZIP в C:\BLENDER ai\Blender\ и запустите blender.exe напрямую
```

---

## Проблемы с uv / uvx

### `uvx` не найден / `spawn uvx ENOENT`
```powershell
# 1. Полностью перезапустите PowerShell/терминал
# 2. Проверьте PATH
$env:PATH -split ";" | Where-Object { $_ -like "*\.local\bin*" }

# 3. Добавьте вручную, если пути нет
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")

# 4. Укажите полный путь в конфиге MCP
where uvx
# → C:\Users\<USER>\.local\bin\uvx.exe
```

### Конфликты версий / проблемы с кэшем
```bash
uv cache clean blender-mcp
uv cache clean --all
uvx --refresh blender-mcp
```

### Проблемы с версией Python
```json
// В конфиге MCP зафиксируйте Python 3.11
{
  "args": ["--python", "3.11", "blender-mcp"],
  "env": { "UV_PYTHON_PREFERENCE": "only-managed" }
}
```

---

## Проблемы с подключением MCP

### "Connection Refused" / "Cannot Connect to Blender"
1. **Аддон в Blender не запущен:**
   - Откройте Blender → N-панель → **MCP for Blender** → нажмите **Start MCP Server**
   - Либо для GenesisCore: N-панель → **GenesisCore** → нажмите **Connect**

2. **Неверный порт:**
   - blender-mcp: порт 9876 (настраивается через `BLENDER_PORT`)
   - GenesisCore: порт 45677 (внутренний)

3. **Блокировка брандмауэром/антивирусом:**
   - Разрешите `python.exe` / `blender.exe` в брандмауэре Windows
   - Проверьте профиль частной сети

### Таймаут на командах
```bash
# Разбейте сложные запросы на меньшие шаги
# Вместо: "Build entire city with 50 buildings"
# Делайте: "Create one building template" → "Array it 10x" → "Add variations"

# При необходимости увеличьте таймаут в конфиге клиента
```

### Инструменты не появляются в AI-клиенте
```bash
# 1. Полностью перезапустите AI-клиент (не только окно)
#    - Windows: выход из системного трея
#    - macOS: Cmd+Q
# 2. Проверьте синтаксис конфига (валидные JSON/TOML)
# 3. Убедитесь, что uvx работает в терминале: uvx blender-mcp --help
```

---

## Специфика GenesisCore

### "Connecting..." зависает навсегда
```bash
# 1. Проверьте, что порт 45677 не занят
netstat -an | findstr 45677

# 2. Полностью перезапустите Blender
# 3. Загляните в System Console (Window → Toggle System Console) на предмет ошибок
# 4. Отключите другие аддоны, которые могут конфликтовать
```

### Список моделей пуст / "Failed to Fetch Models"
```bash
# 1. Убедитесь, что API-ключ верный
# 2. Проверьте интернет-соединение / прокси
# 3. Попробуйте другого провайдера (DeepSeek, OpenRouter, Ollama)
# 4. Для Ollama: убедитесь, что ollama serve запущен, а модель скачана (ollama pull deepseek-coder)
```

### Инструменты не выполняются
```bash
# 1. Включите модули инструментов в N-панели (Shift+клик для множественного выбора)
#    Обязательные: Common Tools, Object Tools, Material Tools
#    Опциональные: Polyhaven Tools, Asset Tools
# 2. Проверьте System Console на ошибки Python
# 3. Некоторым инструментам нужен определённый контекст (например, активный объект)
```

---

## Проблемы Dream Textures

### Не хватает VRAM / CUDA OOM
```bash
# Снизьте разрешение: максимум 512x512 для 4 ГБ VRAM
# Используйте fp16 (half precision) — значение по умолчанию
# Закройте другие программы, нагружающие GPU
# Включите Attention Slicing (Auto) в настройках
# Уменьшите число шагов: 20-30 вместо 50
```

### Сбой скачивания модели
```bash
# 1. Проверьте интернет
# 2. Для моделей с ограниченным доступом: задайте HF_TOKEN в настройках
# 3. Попробуйте другую модель: stabilityai/stable-diffusion-2-1-base
# 4. Ручная загрузка: huggingface.co → download → Import Checkpoint
```

### Карантин macOS (не Windows)
```bash
xattr -r -d com.apple.quarantine ~/Library/Application\ Support/Blender/3.3/scripts/addons/dream_textures/.python_dependencies
```

### Медленная генерация
```bash
# Используйте меньше шагов (20-30)
# Меньшее разрешение (512x512)
# Scheduler: DPM++ 2M Karras (быстрее)
# Включите Speed Optimizations: Half Precision
```

---

## Специфика blender-mcp

### Сбой загрузки Poly Pizza (Cloudflare 403)
```
Error: "Poly Pizza's CDN returned a Cloudflare bot-protection challenge"

Исправление:
1. Скачайте .glb вручную с https://poly.pizza
2. File → Import → glTF 2.0
3. Либо используйте домашний IP (не VPN и не адрес дата-центра)
```

### Команды не выполняются в headless Blender (`blender -b`)
```
blender-mcp требует GUI Blender для выполнения команд.
Используйте: blender (с GUI) или xvfb-run -a blender (headless в Linux)
```

### Safe Mode блокирует скрипт
```
Error: "Rejected by safe mode - ..."

Исправление:
1. Перепишите без: os, subprocess, open(), eval(), exec()
2. Используйте только: bpy, bmesh, mathutils, math, random, json, uuid
3. Либо отключите: BLENDER_MCP_SAFE_MODE=0 (по умолчанию)
```

---

## Проблемы интеграции ассетов

### Ассеты Poly Haven не появляются
```bash
# 1. Включите "Use Poly Haven" в N-панели Blender → MCP for Blender
# 2. Проверьте кэш: %TEMP%\polyhaven_models\ / polyhaven_hdris\
# 3. Очистите кэш и повторите
```

### Sketchfab требует API-ключа
```bash
# 1. Получите ключ: https://sketchfab.com/developers/api
# 2. Blender Preferences → Add-ons → MCP for Blender → Sketchfab API Key
# 3. Или через env: BLENDERMCP_SKETCHFAB_API_KEY
```

### Hyper3D / Hunyuan3D не работают
```bash
# 1. Включите в N-панели
# 2. Добавьте API-ключи в Preferences
# 3. Проверьте баланс/квоту в панели провайдера
# 4. На бесплатном тарифе могут быть ограничения
```

---

## Проблемы с производительностью

### Blender зависает / не отвечает
```bash
# 1. Ищите бесконечные циклы в System Console
# 2. Сократите количество объектов в сцене
# 3. Отключите тяжёлые модификаторы (Subsurf с высоким числом уровней)
# 4. Используйте более простую геометрию для ИИ-генерации
```

### Большие .blend-файлы
```bash
# File → Clean Up → Unused Data Blocks
# File → External Data → Automatically Pack Resources (или распаковать)
# Удалите неиспользуемые материалы, текстуры, меши
# Используйте Linked libraries для повторяющихся ассетов
```

---

## Отладочные инструменты

### Системная консоль Blender
```
Windows: Window → Toggle System Console
macOS: /Applications/Blender.app/Contents/MacOS/Blender (в терминале)
Linux: запустите blender из терминала
```

### Логи MCP-сервера
```bash
# blender-mcp: работает в том терминале, где вы запустили uvx
# GenesisCore: смотрите в системную консоль Blender
```

### Включите подробное логирование
```python
# В консоли Python в Blender:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Типовые сообщения об ошибках

| Ошибка | Причина | Исправление |
|-------|-------|-------|
| `KeyError: 'object_name'` | Объект не существует | Проверьте написание, используйте `bpy.data.objects.get()` |
| `AttributeError: 'NoneType'` | Контекст равен None (background mode) | Запустите Blender с GUI |
| `RuntimeError: Operator not available` | Неверный режим (EDIT вместо OBJECT) | `bpy.ops.object.mode_set(mode='OBJECT')` |
| `MemoryError` | Не хватает RAM/VRAM | Снизьте разрешение, закройте приложения |
| `ModuleNotFoundError` | Отсутствует Python-пакет | Зависимости подтягивает uvx; проверьте .python_dependencies |

---

## Где искать помощь

1. **Системная консоль Blender** — первое, куда стоит заглянуть
2. **GitHub Issues:**
   - GenesisCore: https://github.com/AIGODLIKE/GenesisCore/issues
   - blender-mcp: https://github.com/ahujasid/blender-mcp/issues
   - Dream Textures: https://github.com/carson-katri/dream-textures/issues
3. **Discord:**
   - blender-mcp: https://discord.gg/SNqPn4TcKQ
   - Dream Textures: https://discord.gg/EmDJ8CaWZ7
4. **Документация:** эта вики + официальные руководства

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](installation.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [GENESISCORE ADDON - DEEP DIVE](../addons/genesiscore.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md)
- **По темам:** [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md)
- **Теги:** #addon, #blender, #mcp, #reference
