---
id: 02_boolean_operations
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human
---
# P02: OPERACIONES BOOLEANAS

**ID:** P02 | **Clúster:** Geometry Basics | **Dificultad:** ⭐⭐ | **Tags:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 OBJETIVO
Operaciones booleanas (Difference, Union, Intersect) entre objetos vía MCP

---

## 📝 PROMPT

```
Ejecuta la operación booleana [OPERATION] entre "[OBJECT_A]" (base) y "[OBJECT_B]" (herramienta).
Operaciones: DIFFERENCE (restar), UNION (unir), INTERSECT (intersección).
Resultado: el objeto A se modifica, el objeto B puede eliminarse.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# Configuración
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# Asegurar OBJECT mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Seleccionar objetos
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# Añadir modificador Boolean
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 'FAST' para geometrías simples

# Aplicar
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# Eliminar herramienta (opcional)
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 OPERACIONES

| Operación | Resultado visual | Caso de uso |
|----------|---------------------|----------|
| **DIFFERENCE** | A menos B | Ventanas, puertas, agujeros, ranuras |
| **UNION** | A más B | Unir piezas, fusionar mallas |
| **INTERSECT** | Solo intersección | Máscaras, recorte de formas |

---

## 💡 PATRONES AVANZADOS

### Booleanos múltiples (a la vez)
```python
# Varias restas en una pasada
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# Aplicar todos
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Limpieza
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### Cuidado con las normales
```python
# Verificar y corregir normales antes del booleano
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ PROBLEMAS FRECUENTES

| Problema | Causa | Solución |
|--------|---------|---------|
| Resultado vacío | Normales dentro/fuera | `Mesh > Normals > Recalculate Outside` |
| Artefactos | Aristas no-manifold | `Select > Select All by Trait > Non-Manifold` → corregir |
| Lento en mallas complejas | Muchos polígonos | Usa `DECIMATE` antes, o solver `FAST` |
| El objeto desaparece | Intersección vacía | Verifica la posición de los objetos |

---

## 🔗 ENLACES

- **Casos:** [Case 01: ArchViz Interior](../cases/case_01_archviz_interior.md) — ventanas/puertas en paredes
- **Flujos:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Prompts relacionados:** [P01 Primitives](./01_geometry_basics.md), [P03 Modifiers Stack](./03_modifiers_stack.md)
- **Siguiente:** [P03: Modifiers Stack](./03_modifiers_stack.md)
