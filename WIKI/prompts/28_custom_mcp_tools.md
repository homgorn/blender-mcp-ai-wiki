---
lang: ru
tags: [mcp, prompt]
---
# P28: CUSTOM MCP TOOLS DEVELOPMENT

**ID:** P28 | **Кластер:** MCP Integration | **Сложность:** ⭐⭐⭐ | **Теги:** #mcp #custom-tools #python #fastmcp #addon

---

## 🎯 ЦЕЛЬ
Свои MCP-инструменты: серверная сторона (FastMCP) + Blender addon handler

---

## 📝 ПРОМПТ (РУС)

```
Создай MCP tool "[NAME]": параметры {...}, выполняет [действие bpy],
возвращает {...}. Зарегистрируй в сервере и аддоне.
```

---

## 📝 ПРОМПТ (ENG)

```
Create MCP tool "[NAME]": params {...}, runs [bpy action], returns {...}. Register in server and addon.
```

---

## 🔧 ШАБЛОН

```python
# Server (src/blender_mcp/tools/custom.py)
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Custom")

@mcp.tool()
async def my_tool(param: str) -> str:
    '''Description for LLM'''
    blender = get_blender_connection()
    return blender.send_command("my_command", {"param": param})

# Addon (addon.py) — в execute_command handlers:
# def my_command_handler(self, param): ...
```

```python
# GenesisCore style (встроенный):
# src/tools/my_tools.py
from .common import ToolsPackageBase
class MyTools(ToolsPackageBase):
    def my_tool(param: str) -> dict:
        '''Description for LLM'''
        import bpy
        return {"result": "success"}
# + import в src/tools/__init__.py
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](26_mcp_basics.md), [P27: POLY HAVEN ASSET PIPELINE](27_polyhaven_pipeline.md), [P35: MCP ERROR RECOVERY](35_mcp_error_recovery.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md)
- **По темам:** [MCP ADVANCED: STREAMING & TOOL COMPOSITION](../mcp_advanced/streaming_tools.md), [P03: MODIFIERS STACK](03_modifiers_stack.md), [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md)
- **Теги:** #addon, #custom, #custom-tools, #fastmcp, #mcp, #prompt, #python

