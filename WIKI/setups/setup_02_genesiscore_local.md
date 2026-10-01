---
id: setup_02_genesiscore_local
lang: ru
category: setups
status: full
tags: [llm, mcp, setup]
---
# SETUP 02: GENESISCORE LOCAL (OLLAMA)

**ID:** SETUP-02 | **Type:** Local LLM Integration | **Difficulty:** ⭐⭐ | **Time:** 15-30 min

---

## 🎯 ЦЕЛЬ
Настроить GenesisCore для работы с локальными LLM через Ollama (приватность, бесплатно, офлайн)

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

| Компонент | Версия | Статус |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Обязательно |
| **Ollama** | latest | ✅ Обязательно |
| **RAM** | 16GB+ | 🟡 Рекомендуется |
| **VRAM** | 8GB+ | 🟡 Для 7B+ моделей |

---

## 🪟 WINDOWS УСТАНОВКА

### 1. Установка Ollama
```powershell
# Скачать и установить
winget install Ollama.Ollama

# Или с официального сайта
# https://ollama.com/download/windows

# Проверить
ollama --version
ollama list
```

### 2. Загрузка моделей для кодинга/блендера
```powershell
# Лучшие модели для Blender Python (по приоритету)
ollama pull codellama:13b        # Лучшая для кода, 7.3GB
ollama pull deepseek-coder:6.7b  # Отличная для Python, 3.8GB
ollama pull qwen2.5-coder:7b     # Новая, быстрая, 4.7GB
ollama pull llama3.2:3b          # Легкая, быстрая, 2.0GB

# Проверить
ollama list
```

### 3. Запуск Ollama сервера
```powershell
# Должен работать в фоне (автозапуск при установке)
# Проверить:
curl http://localhost:11434/api/tags

# Если не работает:
ollama serve
```

---

## 🔧 НАСТРОЙКА GENESISCORE

### 1. Установка аддона (если ещё не)
```bash
# В Blender: Edit → Preferences → Add-ons → Install from ZIP
# Выбрать: GenesisCore-main.zip
# Включить: GenesisCore
```

### 2. Настройка провайдера
```
N-Panel → GenesisCore вкладка:
1. Provider: ▼ Ollama
2. Base URL: http://localhost:11434/v1  (важно: /v1 на конце!)
3. API Key: (оставить пустым для Ollama)
4. Нажать "Fetch Models"
4. Выбрать модель: codellama:13b / deepseek-coder:6.7b / qwen2.5-coder:7b
5. Tool Modules: включить все (Shift+Click)
6. Save Config
7. Connect
```

### 3. Настройки модели (рекомендуемые)
```json
{
  "provider": "Ollama",
  "base_url": "http://localhost:11434/v1",
  "model": "codellama:13b",
  "temperature": 0.1,
  "top_p": 0.9,
  "max_tokens": 4096,
  "use_history": true
}
```

---

## 🔧 ОПТИМИЗАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ

### GPU Offloading (NVIDIA)
```powershell
# Ollama автоматически использует GPU если есть CUDA
# Проверить:
ollama run codellama:13b "test"
# Должно показать: "using GPU" в логах

# Принудительно включить GPU layers:
# В переменных окружения:
OLLAMA_NUM_GPU=999
OLLAMA_GPU_LAYERS=999
```

### Оптимизация памяти
```yaml
# В настройках GenesisCore:
use_history: false          # Отключить историю для экономии токенов
max_tokens: 2048            # Ограничить длину ответа
temperature: 0.1            # Детерминированные ответы
```

### Квантование (если мало VRAM)
```powershell
# Использовать квантованные версии:
ollama pull codellama:13b-q4_K_M   # 4-bit, 7.3GB → 4.7GB
ollama pull deepseek-coder:6.7b-q4_K_M  # 3.8GB → 2.5GB
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Быстрый тест в GenesisCore чате
```
"Создай куб 'TestCube' в позиции (1, 2, 3) с материалом красного цвета"
```

### Ожидаемый результат
1. Агент анализирует запрос
2. Вызывает `create_object` + `set_material`
3. В Blender появляется куб в (1, 2, 3) с красным материалом

---

## 🔧 УСТРАНЕНИЕ НЕИСПРАВНОСТЕЙ

| Проблема | Решение |
|----------|---------|
| `Connection refused` | Ollama не запущен → `ollama serve` |
| `Model not found` | `ollama pull <model_name>` |
| `Out of memory` | Использовать меньшую модель (3b/7b) или q4 квантование |
| `Slow response` | Включить GPU offloading, уменьшить `max_tokens` |
| `Base URL error` | Проверить `http://localhost:11434/v1` (с /v1!) |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [MCP ADVANCED: STREAMING & TOOL COMPOSITION](../mcp_advanced/streaming_tools.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md)
- **Теги:** #llm, #mcp, #setup

