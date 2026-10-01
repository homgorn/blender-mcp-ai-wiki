---
id: 28_custom_mcp_tools
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P28: CUSTOM MCP TOOLS DEVELOPMENT

> Objetivo: ---

**ID:** 28_custom_mcp_tools | **Lang:** es | **Orig:** ru | **Category:** prompts | **Tags:** addon, custom, custom-tools, fastmcp, mcp, python

## Cómo usar
Esta es la versión en español de '28_custom_mcp_tools'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
28_custom_mcp_tools / prompts / addon, custom, custom-tools, fastmcp, mcp, python
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

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
- **Сетяпы:** [Setup 06](../setups/setup_06_custom_mcp_tools.md)
- **Следующий:** [P29: Batch & CLI](./29_batch_cli.md)
