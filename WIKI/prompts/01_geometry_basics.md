---
lang: ru
tags: [modeling, prompt]
---
# P01: PRIMITIVE CREATION BASICS

**ID:** P01 | **Кластер:** Geometry Basics | **Сложность:** ⭐ | **Теги:** #geometry #primitives #basics #bpy.ops

---

## 🎯 ЦЕЛЬ
Создание базовых примитивов через MCP с точным контролем параметров

---

## 📝 ПРОМПТ (РУС)

```
Создай примитив [TYPE] с именем "[NAME]" в позиции [X, Y, Z], 
масштаб [SX, SY, SZ], поворот [RX, RY, RZ] (в радианах).

Доступные типы: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT

Пример: "Создай куб 'Box_01' в (2, 0, 1) масштаб (1, 2, 1) поворот (0, 0, 0.785)"
```

---

## 📝 ПРОМПТ (ENG)

```
Create a [TYPE] primitive named "[NAME]" at location [X, Y, Z], 
scale [SX, SY, SZ], rotation [RX, RY, RZ] (radians).

Available types: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT

Example: "Create cube 'Box_01' at (2, 0, 1) scale (1, 2, 1) rotation (0, 0, 0.785)"
```

---

## 🔧 MCP TOOL: `create_object`

```json
{
  "type": "create_object",
  "params": {
    "entity_type": "CUBE",
    "name": "Box_01",
    "location": [2.0, 0.0, 1.0],
    "rotation": [0.0, 0.0, 0.785],
    "scale": [1.0, 2.0, 1.0]
  }
}
```

---

## 📊 ПАРАМЕТРЫ ПО ТИПАМ

| Тип | Обязательные | Опциональные |
|-----|--------------|--------------|
| CUBE | size | location, rotation, scale |
| SPHERE | radius | segments, ring_count, location, rotation, scale |
| CYLINDER | radius, depth | vertices, cap_ends, location, rotation, scale |
| PLANE | size | location, rotation, scale |
| CONE | radius1, radius2, depth | vertices, location, rotation, scale |
| TORUS | major_radius, minor_radius | major_segments, minor_segments, location, rotation, scale |
| EMPTY | — | location, rotation, scale, type (PLAIN_AXES, ARROWS, etc.) |
| CAMERA | — | location, rotation, lens, sensor_width |
| LIGHT | — | location, rotation, type (POINT, SUN, SPOT, AREA), energy, color |

---

## 💡 ВАРИАНТЫ ИСПОЛЬЗОВАНИЯ

### Базовый куб
```json
{"entity_type": "CUBE", "name": "Cube_Base", "location": [0, 0, 0]}
```

### Сфера с детализацией
```json
{"entity_type": "SPHERE", "name": "Sphere_HighPoly", "location": [0, 0, 2], "radius": 1.5, "segments": 64, "ring_count": 32}
```

### Камера для рендера
```json
{"entity_type": "CAMERA", "name": "Cam_Main", "location": [7, -7, 5], "rotation": [0.9, 0, 0.785]}
```

### Студийный свет
```json
{"entity_type": "LIGHT", "name": "Key_Light", "location": [4, 4, 6], "rotation": [-0.7, 0, 0.785], "type": "AREA", "energy": 1000, "size": 2}
```

---

## ⚠️ ЧАСТЫЕ ОШИБКИ

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Object not found` | Имя занято | Используй уникальные имена или проверяй `get_scene_info` |
| `Invalid rotation` | Градусы вместо радиан | Конвертируй: `radians = degrees * π / 180` |
| `Primitive not created` | Контекст (EDIT mode) | Всегда будь в OBJECT mode |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P07: INSTANCING & ARRAYS](07_instancing_arrays.md), [P23: GEOMETRY NODES BASICS](23_geometry_nodes_basics.md), [P45: GEOMETRY NODES SIMULATION ZONES](45_gn_simulation.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md), [P03: MODIFIERS STACK](03_modifiers_stack.md)
- **По темам:** [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md), [P19: NLA EDITOR WORKFLOW](19_nla_workflow.md)
- **Теги:** #basics, #bpy, #bpy.ops, #geometry, #modeling, #primitives, #prompt

