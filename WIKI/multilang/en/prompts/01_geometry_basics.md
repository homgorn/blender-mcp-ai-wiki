---
id: 01_geometry_basics
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: template
---
# P01: PRIMITIVE CREATION BASICS

> Goal: ## 🌍 MULTILANG

**ID:** 01_geometry_basics | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** **, basics, bpy, bpy.ops, geometry, primitives

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

- **Кейсы:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Воркфлоу:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Сетяпы:** [Setup 01: blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Следующий:** [P02: Boolean Operations](./02_boolean_operations.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/prompts/01_primitive_creation.md` |
| Русский | `multilang/ru/prompts/01_primitive_creation.md` |