---
id: 03_modifiers_stack
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P03: MODIFIERS STACK

> Ziel: 

**ID:** 03_modifiers_stack | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** **, modifiers, non, non-destructive, procedural, stack

## Verwendung
Dies ist die deutsche Version von '03_modifiers_stack'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
03_modifiers_stack / prompts / **, modifiers, non, non-destructive, procedural, stack
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: 03_modifiers_stack
lang: ru
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
---

# P03: MODIFIERS STACK

> Цель: ## 🌍 MULTILANG

**ID:** 03_modifiers_stack | **Lang:** ru | **Orig:** ru | **Category:** prompts | **Tags:** **, modifiers, non, non-destructive, procedural, stack

---

# P03: MODIFIERS STACK

**ID:** P03 | **Кластер:** Geometry Basics | **Сложность:** ⭐⭐ | **Теги:** #modifiers #non-destructive #stack #procedural

---

## 🎯 ЦЕЛЬ
Построение не-деструктивного стека модификаторов для процедурного моделирования

---

## 📝 ПРОМПТ (РУС)

```
Добавь к "[OBJECT_NAME]" стек модификаторов в порядке:
1. [MOD_1] с параметрами {...}
2. [MOD_2] с параметрами {...}
...
Порядок важен: модификаторы применяются сверху вниз.
```

---

## 📝 ПРОМПТ (ENG)

```
Add modifier stack to "[OBJECT_NAME]" in order:
1. [MOD_1] with params {...}
2. [MOD_2] with params {...}
...
Order matters: modifiers apply top-to-bottom.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

obj = bpy.data.objects.get("Base_Mesh")
if not obj:
    raise ValueError("Object not found")

# Очистить существующие (опционально)
# obj.modifiers.clear()

# === ПРИМЕР СТЕКА: Procedural Building ===

# 1. BEVEL - сглаживание краёв
bevel = obj.modifiers.new("Bevel_Edges", 'BEVEL')
bevel.width = 0.02
bevel.segments = 3
bevel.profile = 0.5
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 1.0472  # 60°

# 2. SUBSURF - подделение для гладкости
subsurf = obj.modifiers.new("Subdiv_Smooth", 'SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3
subsurf.subdivision_type = 'CATMULL_CLARK'

# 3. ARRAY - повторение по оси
array = obj.modifiers.new("Array_Floors", 'ARRAY')
array.count = 10
array.use_relative_offset = True
array.relative_offset_displace = (0, 0, 3.5)  # высота этажа

# 4. MIRROR - симметрия
mirror = obj.modifiers.new("Mirror_X", 'MIRROR')
mirror.use_axis = (True, False, False)
mirror.use_bisect_axis = (True, False, False)

# 5. DECIMATE - оптимизация для игры
decimate = obj.modifiers.new("Decimate_LOD", 'DECIMATE')
decimate.ratio = 0.3
decimate.decimate_type = 'COLLAPSE'

# 6. BEVEL (второй) - на рёбрах после array
bevel2 = obj.modifiers.new("Bevel_Final", 'BEVEL')
bevel2.width = 0.01
bevel2.segments = 2

print(f"Stack built: {len(obj.modifiers)} modifiers on {obj.name}")
```

---

## 📊 ПОПУЛЯРНЫЕ СТЕКИ

### Архитектура: Здание
```
1. BEVEL (sharp edges) → 2. ARRAY (floors) → 3. MIRROR (symmetry) → 4. SUBSURF (smooth)
```

### Гейм-ассет: Prop
```
1. BEVEL → 2. WEIGHTED NORMAL (shading) → 3. DECIMATE (LOD) → 4. UV PROJECT (optional)
```

### Персонаж: Cloth
```
1. SUBSURF → 2. CLOTH SIM → 3. SHRINKWRAP (to body) → 4. SOLIDIFY (thickness)
```

### Хард-сёрфейс: Механизм
```
1. BEVEL (weight-based) → 2. BOOLEAN (details) → 3. EDGE SPLIT (sharp) → 4. WEIGHTED NORMAL
```

---

## ⚙️ КЛЮЧЕВЫЕ МОДИФИКАТОРЫ И ПАРАМЕТРЫ

| Модификатор | Главные параметры | Когда использовать |
|-------------|-------------------|-------------------|
| **BEVEL** | width, segments, profile, limit_method | Всегда для реализма |
| **SUBSURF** | levels, render_levels, subdivision_type | Органика, плавные формы |
| **ARRAY** | count, offset (relative/constant/object) | Повторяющиеся элементы |
| **MIRROR** | axis, bisect, mirror_object | Симметрия |
| **BOOLEAN** | operation, object, solver | Вычитание/объединение |
| **DECIMATE** | ratio, type (COLLAPSE/UNSUBDIV/PLANAR) | Оптимизация, LOD |
| **SOLIDIFY** | thickness, offset, even_thickness | Толщина, ткань |
| **SHRINKWRAP** | target, wrap_mode, offset | Надевание, проекция |
| **DISPLACE** | texture, strength, direction | Детализация, ландшафт |
| **GEOMETRY_NODES** | node_group | Полный процедурализм |

---

## 💡 ПРО ТИПЫ

### Vertex Groups для контроля
```python
# Ограничить BEVEL только острыми рёбрами
bevel.limit_method = 'WEIGHT'
bevel.vertex_group = "Bevel_Weight"

# Создать группу и назначить веса
vg = obj.vertex_groups.new(name="Bevel_Weight")
# Назначь веса через bmesh или vertex paint
```

### Драйверы на модификаторах
```python
# Анимировать count массива
driver = array.driver_add('count').driver
driver.type = 'SCRIPTED'
var = driver.variables.new()
var.name = "frame"
var.targets[0].id = bpy.data.scenes["Scene"]
var.targets[0].data_path = "frame_current"
driver.expression = "1 + frame / 10"
```

### Применение по необходимости
```python
# Применить только некоторые (для экспорта)
for mod in list(obj.modifiers):
    if mod.name.startswith("Decimate") or mod.name.startswith("Bevel_Final"):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
```

---

## ⚠️ ПРАВИЛА ПОРЯДКА

| Порядок | Эффект |
|---------|--------|
| BEVEL → SUBSURF | Фаска поделится, мягкие края |
| SUBSURF → BEVEL | Фаска на уже гладком меше, острее |
| ARRAY → MIRROR | Зеркалится уже массив |
| MIRROR → ARRAY | Массив зеркалится целиком |
| BOOLEAN → SUBSURF | Гладкое результат булева |
| SUBSURF → BOOLEAN | Булев на высокополигональном (медленно) |

---

## 🔗 СВЯЗИ

- **Кейсы:** [Case 05: Procedural City](../cases/case_05_procedural_city.md)
- **Воркфлоу:** [WF 05: Procedural Assets](../workflows/wf_05_procedural_assets.md)
- **Промпты:** [P01 Primitives](./01_geometry_basics.md), [P02 Boolean](./02_boolean_operations.md)
- **Следующий:** [P04: Mesh Editing (BMesh)](./04_mesh_editing_bmesh.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/prompts/03_modifiers_stack.md` |
| Русский | `multilang/ru/prompts/03_modifiers_stack.md` |