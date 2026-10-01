---
id: 26_mcp_basics
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P26: MCP BASICS (BLENDER-MCP COMMANDS)

> Goal: ---

**ID:** 26_mcp_basics | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** blender, blender-mcp, commands, mcp, setup, tools

## How to use
This page is the en version of '26_mcp_basics'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.

## MCP Prompt (copy-paste)
```
26_mcp_basics / prompts / blender, blender-mcp, commands, mcp, setup, tools
```

> Note: code/paths stay in English for Blender/Python compatibility.

---

# P26: MCP BASICS (BLENDER-MCP COMMANDS)

**ID:** P26 | **Кластер:** MCP Integration | **Сложность:** ⭐ | **Теги:** #mcp #blender-mcp #tools #commands #setup

---

## 🎯 ЦЕЛЬ
Базовые MCP-команды: scene info, create/modify/delete, screenshot, code execution

---

## 📝 ПРОМПТ (РУС)

```
Через MCP: [действие]
Примеры: "Покажи сцену", "Создай сферу", "Скриншот viewport"
```

---

## 📝 ПРОМПТ (ENG)

```
Via MCP: [action]
Examples: "Show scene", "Create sphere", "Viewport screenshot"
```

---

## 🔧 MCP TOOLS

```json
// 1. Scene info
{"type": "get_scene_info", "params": {}}
// 2. Create
{"type": "create_object", "params": {"entity_type": "SPHERE", "name": "Ball", "location": [0,0,2]}}
// 3. Modify
{"type": "modify_object", "params": {"name": "Ball", "scale": [2,2,2]}}
// 4. Screenshot
{"type": "get_viewport_screenshot", "params": {"max_size": 800}}
// 5. Code
{"type": "execute_code", "params": {"code": "import bpy\nbpy.ops.mesh.primitive_cube_add()"}}
```

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 01](../setups/setup_01_blender_mcp_basic.md)
- **Следующий:** [P27: Poly Haven Pipeline](./27_polyhaven_pipeline.md)
