---
id: 26_mcp_basics
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P26: MCP BASICS (Blender-MCP COMMANDS)

> 目标: ---

**ID:** 26_mcp_basics | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** blender, blender-mcp, commands, mcp, setup, tools

## 使用方法
这是 '26_mcp_basics' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
26_mcp_basics / prompts / blender, blender-mcp, commands, mcp, setup, tools
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

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
