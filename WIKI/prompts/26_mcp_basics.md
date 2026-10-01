---
lang: en
tags: [blender, mcp, prompt]
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

- **Прочие в категории «Промпты»:** [P27: POLY HAVEN ASSET PIPELINE](27_polyhaven_pipeline.md), [P28: CUSTOM MCP TOOLS DEVELOPMENT](28_custom_mcp_tools.md), [P35: MCP ERROR RECOVERY](35_mcp_error_recovery.md), [P45: GEOMETRY NODES SIMULATION ZONES](45_gn_simulation.md), [P46: UDIM WORKFLOW](46_udim_workflow.md)
- **По темам:** [SETUP 01: BLENDER-MCP BASIC](../setups/setup_01_blender_mcp_basic.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](../setups/setup_09_blenderbot_ai.md), [SETUP 35: READY PLAYER ME AVATARS](../setups/setup_35_readyplayerme.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](../setups/setup_45_hunyuan3d_21.md)
- **Теги:** #blender, #blender-mcp, #commands, #mcp, #prompt, #setup, #tools

