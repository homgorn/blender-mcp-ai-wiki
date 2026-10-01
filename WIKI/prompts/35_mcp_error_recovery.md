---
lang: ru
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
- **Сетяпы:** [Setup 01](../setups/setup_01_blender_mcp_basic.md)
- **Следующий:** [P36: Asset Licensing](./36_asset_licensing.md)
