---
lang: ru
tags: [mcp, prompt]
---
# P35: MCP ERROR RECOVERY

**ID:** P35 | **Кластер:** MCP Integration | **Сложность:** ⭐⭐ | **Теги:** #mcp #errors #retry #validation #scene-check

---

## 🎯 ЦЕЛЬ
Стандартный протокол восстановления: проверить сцену → упростить → повторить → откатить

---

## 📝 ПРОМПТ (РУС)

```
Команда упала с "[ERROR]". Выполни recovery:
1) get_scene_info, 2) упрости запрос, 3) повтори, 4) при повторе — undo и доложи.
```

---

## 📝 ПРОМПТ (ENG)

```
Command failed with "[ERROR]". Run recovery:
1) get_scene_info, 2) simplify, 3) retry, 4) on repeat failure — undo and report.
```

---

## 🔧 MCP ПОСЛЕДОВАТЕЛЬНОСТЬ

```json
{"type": "get_scene_info", "params": {}}
{"type": "get_viewport_screenshot", "params": {"max_size": 800}}
```

```python
import bpy

def safe_run(label, func):
    bpy.ops.ed.undo_push(message=label)
    try:
        out = func()
        bpy.context.view_layer.update()
        return {"success": True, "result": out}
    except Exception as e:
        bpy.ops.ed.undo()
        return {"success": False, "error": str(e)}
```

---

## 📊 ТАБЛИЦА ОШИБОК
| Ошибка | Действие |
|--------|----------|
| Timeout | Разбить на шаги по 1 объекту |
| Connection refused | Проверить Start MCP Server |
| Object not found | get_scene_info → точное имя |
| Non-manifold после boolean | Recalculate normals → повторить |
| OOM рендера | Samples/2, resolution/2, retry |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](26_mcp_basics.md), [P27: POLY HAVEN ASSET PIPELINE](27_polyhaven_pipeline.md), [P28: CUSTOM MCP TOOLS DEVELOPMENT](28_custom_mcp_tools.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md)
- **По темам:** [MCP ADVANCED: STREAMING & TOOL COMPOSITION](../mcp_advanced/streaming_tools.md), [P03: MODIFIERS STACK](03_modifiers_stack.md), [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md)
- **Теги:** #errors, #mcp, #prompt, #retry, #scene, #scene-check, #validation

