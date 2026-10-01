---
id: 01_geometry_basics
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 1
translation: human
---
# P01: PRIMITIVEN ERSTELLEN — BASIS

**ID:** P01 | **Cluster:** Geometry Basics | **Schwierigkeit:** ⭐ | **Tags:** #geometry #primitives #basics #bpy.ops

---

## 🎯 ZIEL
Basis-Primitive über MCP mit präziser Parameterkontrolle erstellen

---

## 📝 PROMPT

```
Erstelle ein [TYPE]-Primitiv namens "[NAME]" an Position [X, Y, Z],
Skalierung [SX, SY, SZ], Rotation [RX, RY, RZ] (in Radiant).

Typen: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT

Beispiel: "Erstelle einen Würfel 'Box_01' bei (2, 0, 1) Skalierung (1, 2, 1) Rotation (0, 0, 0.785)"
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

## 📊 PARAMETER JE TYP

| Typ | Erforderlich | Optional |
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

## ⚠️ HÄUFIGE FEHLER

| Fehler | Ursache | Lösung |
|--------|---------|---------|
| `Object not found` | Name belegt | Eindeutige Namen nutzen oder `get_scene_info` prüfen |
| `Invalid rotation` | Grad statt Radiant | Umrechnen: `radians = degrees * π / 180` |
| `Primitive not created` | Kontext (EDIT mode) | Immer im OBJECT mode bleiben |

---

## 🔗 LINKS

- **Fälle:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Nächster:** [P02: Boolean Operations](./02_boolean_operations.md)
