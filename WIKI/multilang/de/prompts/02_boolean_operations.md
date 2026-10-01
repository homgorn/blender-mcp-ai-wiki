---
id: 02_boolean_operations
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human
---
# P02: BOOLESCHE OPERATIONEN

**ID:** P02 | **Cluster:** Geometry Basics | **Schwierigkeit:** ⭐⭐ | **Tags:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 ZIEL
Boolesche Operationen (Difference, Union, Intersect) zwischen Objekten via MCP

---

## 📝 PROMPT

```
Führe boolesche Operation [OPERATION] zwischen "[OBJECT_A]" (Basis) und "[OBJECT_B]" (Werkzeug) aus.
Operationen: DIFFERENCE (subtrahieren), UNION (vereinigen), INTERSECT (Schnittmenge).
Ergebnis: Objekt A wird modifiziert, Objekt B kann gelöscht werden.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# Setup
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# OBJECT mode sicherstellen
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Objekte wählen
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# Boolean-Modifier hinzufügen
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 'FAST' für einfache Geometrien

# Anwenden
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# Werkzeug löschen (optional)
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 OPERATIONEN

| Operation | Visuelles Ergebnis | Use Case |
|----------|---------------------|----------|
| **DIFFERENCE** | A minus B | Fenster, Türen, Öffnungen, Nuten |
| **UNION** | A plus B | Teile vereinen, Meshes fusionieren |
| **INTERSECT** | Nur Schnittmenge | Masken, Formen ausschneiden |

---

## 💡 FORTGESCHRITTENE MUSTER

### Mehrere Booleans (gleichzeitig)
```python
# Mehrere Subtraktionen in einem Durchgang
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# Alle anwenden
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Aufräumen
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### Vorsicht mit Normalen
```python
# Normalen vor Boolean prüfen und korrigieren
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ HÄUFIGE PROBLEME

| Problem | Ursache | Lösung |
|--------|---------|---------|
| Leeres Ergebnis | Normalen innen/außen | `Mesh > Normals > Recalculate Outside` |
| Geometrie-Artefakte | Non-manifold Kanten | `Select > Select All by Trait > Non-Manifold` → fixen |
| Langsam bei komplexen Meshes | Viele Polygone | `DECIMATE` vorher nutzen, oder `FAST`-Solver |
| Objekt verschwindet | Leere Schnittmenge | Positionen der Objekte prüfen |

---

## 🔗 LINKS

- **Fälle:** [Case 01: ArchViz Interior](../cases/case_01_archviz_interior.md) — Fenster/Türen in Wänden
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Verwandte Prompts:** [P01 Primitives](./01_geometry_basics.md), [P03 Modifiers Stack](./03_modifiers_stack.md)
- **Nächster:** [P03: Modifiers Stack](./03_modifiers_stack.md)
