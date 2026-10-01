---
id: 01_geometry_basics
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: human
---
# P01: CREACIÓN DE PRIMITIVAS — BASE

**ID:** P01 | **Clúster:** Geometry Basics | **Dificultad:** ⭐ | **Tags:** #geometry #primitives #basics #bpy.ops

---

## 🎯 OBJETIVO
Crear primitivas básicas vía MCP con control preciso de parámetros

---

## 📝 PROMPT

```
Crea una primitiva [TYPE] llamada "[NAME]" en posición [X, Y, Z],
escala [SX, SY, SZ], rotación [RX, RY, RZ] (en radianes).

Tipos: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT

Ejemplo: "Crea un cubo 'Box_01' en (2, 0, 1) escala (1, 2, 1) rotación (0, 0, 0.785)"
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

## 📊 PARÁMETROS POR TIPO

| Tipo | Obligatorios | Opcionales |
|-----|--------------|--------------|
| CUBE | size | location, rotation, scale |
| SPHERE | radius | segments, ring_count, location, rotation, scale |
| CYLINDER | radius, depth | vertices, cap_ends, location, rotation, scale |
| PLANE | size | location, rotation, scale |
| CONE | radius1, radius2, depth | vertices, location, rotation, scale |
| TORUS | major_radius, minor_radius | major_segments, minor_segments, location, rotation, scale |
| EMPTY | — | location, rotation, scale, type |
| CAMERA | — | location, rotation, lens, sensor_width |
| LIGHT | — | location, rotation, type, energy, color |

---

## ⚠️ ERRORES FRECUENTES

| Error | Causa | Solución |
|--------|---------|---------|
| `Object not found` | Nombre ocupado | Usa nombres únicos o verifica `get_scene_info` |
| `Invalid rotation` | Grados en vez de radianes | Convierte: `radians = degrees * π / 180` |
| `Primitive not created` | Contexto (EDIT mode) | Quédate siempre en OBJECT mode |

---

## 🔗 ENLACES

- **Casos:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Flujos:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Siguiente:** [P02: Boolean Operations](./02_boolean_operations.md)
