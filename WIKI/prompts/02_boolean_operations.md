---
lang: ru
tags: [modeling, prompt]
---
# P02: BOOLEAN OPERATIONS

**ID:** P02 | **Кластер:** Geometry Basics | **Сложность:** ⭐⭐ | **Теги:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 ЦЕЛЬ
Выполнение булевых операций (Difference, Union, Intersect) между объектами через MCP

---

## 📝 ПРОМПТ (РУС)

```
Выполни булеву операцию [OPERATION] между "[OBJECT_A]" (базовый) и "[OBJECT_B]" (инструмент).
Операции: DIFFERENCE (вычитание), UNION (объединение), INTERSECT (пересечение).
Результат: объект A модифицируется, объект B может быть удалён.
```

---

## 📝 ПРОМПТ (ENG)

```
Perform boolean [OPERATION] between "[OBJECT_A]" (base) and "[OBJECT_B]" (tool).
Operations: DIFFERENCE (subtract), UNION (merge), INTERSECT (intersection).
Result: object A is modified, object B can be deleted.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# Настройка
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# Убедиться в OBJECT mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Выбрать объекты
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# Добавить модификатор Boolean
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 'FAST' для простых геометрий

# Применить
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# Удалить инструмент (опционально)
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 ОПЕРАЦИИ

| Операция | Визуальный результат | Use Case |
|----------|---------------------|----------|
| **DIFFERENCE** | A минус B | Окна, двери, отверстия, канавки |
| **UNION** | A плюс B | Объединение частей, слияние мешей |
| **INTERSECT** | Только пересечение | Маски, вырезание форм |

---

## 💡 ПРОДВИНУТЫЕ ПАТТЕРНЫ

### Множественные булевы (одновременно)
```python
# Несколько вычитаний за один проход
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# Применить все
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Очистка
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### Будьте аккуратны с нормалями
```python
# Проверить и исправить нормали перед булевым
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ ЧАСТЫЕ ПРОБЛЕМЫ

| Проблема | Причина | Решение |
|----------|---------|---------|
| Результат пустой | Нормали наружу/внутрь | `Mesh > Normals > Recalculate Outside` |
| Артефакты геометрии | Не-манифольд края | `Select > Select All by Trait > Non-Manifold` → исправить |
| Медленно на сложных мешах | Много полигонов | Используй `DECIMATE` перед булевым, или `FAST` solver |
| Объект исчезает | Пересечение пустое | Проверь расположение объектов |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P03: MODIFIERS STACK](03_modifiers_stack.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md), [P04: MESH EDITING (BMESH)](04_mesh_editing_bmesh.md), [P07: INSTANCING & ARRAYS](07_instancing_arrays.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md)
- **По темам:** [P19: NLA EDITOR WORKFLOW](19_nla_workflow.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P23: GEOMETRY NODES BASICS](23_geometry_nodes_basics.md)
- **Теги:** #boolean, #difference, #intersect, #modeling, #modifiers, #prompt, #union

