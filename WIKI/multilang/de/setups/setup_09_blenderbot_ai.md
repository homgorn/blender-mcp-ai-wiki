---
id: setup_09_blenderbot_ai
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 09: BLENDERBOT / AI CODING AGENT

> Ziel: 

**ID:** setup_09_blenderbot_ai | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_09_blenderbot_ai'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_09_blenderbot_ai / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_09_blenderbot_ai
lang: ru
orig_lang: en
category: setups
type: setup
difficulty: 2
---

# СЕТАП 09: BLENDERBOT / AI CODING AGENT

> Цель: ## 🌍 MULTILANG

**ID:** setup_09_blenderbot_ai | **Lang:** ru | **Orig:** en | **Category:** setups | **Tags:** 

---

# SETUP 09: BLENDERBOT / AI CODING AGENT

**ID:** SETUP-09 | **Type:** AI Coding Assistant for Blender | **Difficulty:** ⭐⭐ | **Time:** 20-30 min

---

## 🎯 ЦЕЛЬ
Настроить BlenderBot / AI Coding Agent для генерации Blender Python кода через LLM

---

## 📋 АРХИТЕКТУРА

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM (GPT-4/   │────▶│  BlenderBot     │────▶│   Blender       │
│   Claude/Codex) │     │  (MCP Server)   │     │   (bpy API)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 🛠️ УСТАНОВКА

### Вариант 1: BlenderGPT (Open Source)
```bash
# GitHub: https://github.com/BlenderGPT/BlenderGPT
git clone https://github.com/BlenderGPT/BlenderGPT
cd BlenderGPT
pip install -r requirements.txt

# Настройка API ключей
cp .env.example .env
# Редактируй .env с твоими API ключами
```

### Вариант 2: Blender-Copilot (VS Code Extension)
```bash
# Установка через VS Code Marketplace
# Поиск: "Blender Copilot" или "Blender Python"

# Или через pip
pip install blender-copilot
```

### Вариант 3: Custom MCP Agent (Рекомендуемый)
```python
# custom_blender_agent.py
import bpy
import bmesh
import mathutils
import json
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BlenderCodingAgent")

@mcp.tool()
async def generate_blender_script(
    task: str,
    context: str = "",
    style: str = "clean"  # "clean", "verbose", "minimal"
) -> str:
    """
    Генерация Blender Python скрипта по описанию задачи.
    
    Args:
        task: Описание задачи (например: "Создай процедурный дом")
        context: Дополнительный контекст (сцена, объекты, настройки)
        style: Стиль кода
    """
    
    system_prompt = f"""
    Ты — эксперт по Blender Python API (bpy).
    Стиль кода: {style}.
    
    Правила:
    1. Всегда используй bpy.data, bpy.ops, bpy.context, bmesh, mathutils
    2. Проверяй существование объектов перед обращением
    3. Используй context managers для режимов (EDIT/OBJECT)
    4. Добавляй комментарии на русском/английском
    5. Обрабатывай ошибки try/except
    6. Возвращай готовый к выполнению код
    
    Контекст: {context}
    """
    
    # Здесь был бы вызов LLM API
    # Возвращаем готовый скрипт
    return generate_code_via_llm(task, system_prompt)

@mcp.tool()
async def fix_blender_script(
    script: str,
    error: str,
    context: str = ""
) -> str:
    """Исправление Blender скрипта по ошибке"""
    return fix_code_via_llm(script, error, context)

@mcp.tool()
async def explain_blender_api(
    topic: str,
    depth: str = "medium"  # "basic", "medium", "deep"
) -> str:
    """Объяснение Blender API темы"""
    return explain_api_via_llm(topic, depth)

if __name__ == "__main__":
    mcp.run()
```

---

## 🔧 КОНФИГУРАЦИЯ MCP

### OpenCode Config
```json
{
  "mcp": {
    "blender-coding-agent": {
      "type": "local",
      "command": ["python", "-m", "custom_blender_agent"],
      "enabled": true,
      "environment": {
        "BLENDER_MCP_SAFE_MODE": "0",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "blender-coding-agent": {
      "command": "python",
      "args": ["-m", "custom_blender_agent"],
      "env": {
        "OPENAI_API_KEY": "your-key",
        "ANTHROPIC_API_KEY": "your-key"
      }
    }
  }
}
```

---

## 🎯 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Генерация процедурного здания
```
User: "Создай процедурный небоскреб 50 этажей с остеклением"
Agent генерирует:
- GN tree для небоскреба
- Параметры: этажи, оконные ряды, стиль
- Материалы: стекло, бетон, металл
- LODs для производительности
```

### Пример 2: Исправление ошибки
```
User: "Ошибка: 'bpy.data.objects' has no attribute 'my_obj'"
Agent: Исправляет на bpy.data.objects.get("my_obj") с проверкой None
```

### Пример 3: Объяснение API
```
User: "Объясни bpy.ops.mesh.boolean_modifier"
Agent: Дает подробное объяснение с примерами использования
```

---

## 🔧 РАСШИРЕНИЕ: CUSTOM TOOLS

### Дополнительные MCP Tools
```python
@mcp.tool()
async def analyze_blender_scene() -> dict:
    """Анализ текущей сцены для контекста"""
    return {
        "objects_count": len(bpy.data.objects),
        "materials_count": len(bpy.data.materials),
        "collections": [c.name for c in bpy.data.collections],
        "current_frame": bpy.context.scene.frame_current,
        "render_engine": bpy.context.scene.render.engine,
    }

@mcp.tool()
async def suggest_optimization(scene_data: dict) -> list:
    """Предложения по оптимизации сцены"""
    suggestions = []
    # Анализ и предложения
    return suggestions

@mcp.tool()
async def generate_boilerplate(template: str) -> str:
    """Генерация boilerplate кода"""
    templates = {
        "operator": OPERATOR_TEMPLATE,
        "panel": PANEL_TEMPLATE,
        "property_group": PROP_GROUP_TEMPLATE,
        "addon": ADDON_TEMPLATE,
    }
    return templates.get(template, "")
```

---

## 🔗 LINKS

- **BlenderGPT:** https://github.com/BlenderGPT/BlenderGPT
- **Blender Copilot:** https://github.com/blender-copilot
- **MCP Spec:** https://modelcontextprotocol.io/
- **FastMCP:** https://github.com/jlowin/fastmcp

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_09_blenderbot_ai.md` |
| Russian | `multilang/ru/setups/setup_09_blenderbot_ai.md` |