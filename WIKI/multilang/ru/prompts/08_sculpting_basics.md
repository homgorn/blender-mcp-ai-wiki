---
id: 08_sculpting_basics
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P08: SCULPTING BASICS

> Цель: ## 🌍 MULTILANG

**ID:** 08_sculpting_basics | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, brushes, dyntopo, highpoly, multires, sculpting

---

# P08: SCULPTING BASICS

**ID:** P08 | **Cluster:** Geometry Basics | **Difficulty:** ⭐⭐ | **Tags:** #sculpting #dyntopo #brushes #multires #highpoly

---

## 🎯 GOAL
Create organic high-poly models using Blender's sculpting tools with Dyntopo and Multires

---

## 📝 PROMPT (RUS)

```
Создай высокополигональный скulpt "[OBJECT_NAME]" из "[BASE_MESH]":
Режим: DYNTOPO (динамическая топология) / MULTIRES (подделение)
Кисти: DRAW, CLAY, SMOOTH, GRAB, INFLATE, CREASE, LAYER
Детализация: [DETAIL_LEVEL]
```

---

## 📝 PROMPT (ENG)

```
Sculpt high-poly "[OBJECT_NAME]" from "[BASE_MESH]":
Mode: DYNTOPO (dynamic topology) / MULTIRES (subdivision)
Brushes: DRAW, CLAY, SMOOTH, GRAB, INFLATE, CREASE, LAYER
Detail level: [DETAIL_LEVEL]
```

---

## 🔧 MCP: `execute_blender_code`

### DYNTOPO SETUP
```python
import bpy

obj = bpy.data.objects.get("Base_Mesh")
if not obj:
    raise ValueError("Base mesh not found")

# Подготовка
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='SCULPT')

# Включить Dyntopo
bpy.context.scene.tool_settings.sculpt.dyntopo = True
bpy.context.scene.tool_settings.sculpt.detail_type = 'CONSTANT'
bpy.context.scene.tool_settings.sculpt.constant_detail = 12  # Размер детали
bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE_EDGES'
bpy.context.scene.tool_settings.sculpt.detail_size = 0.01  # Relative

# Симметрия
bpy.context.scene.tool_settings.sculpt.use_symmetry_x = True
bpy.context.scene.tool_settings.sculpt.use_symmetry_y = False
bpy.context.scene.tool_settings.sculpt.use_symmetry_z = False

print("Dyntopo enabled. Enter Sculpt mode manually.")
```

### MULTIRES SETUP (Для анимации)
```python
obj = bpy.data.objects.get("Base_Mesh")

# Добавить Multires
multires = obj.modifiers.new("Multires", 'MULTIRES')
bpy.ops.object.mode_set(mode='SCULPT')

# Подразделить
for i in range(4):
    bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')

# Уровень скulpting
obj.modifiers["Multires"].sculpt_level = 3

print(f"Multires levels: {len(obj.modifiers['Multires'].levels)}")
```

### КЛЮЧЕВЫЕ КИСТИ И НАСТРОЙКИ
```python
import bpy

tool_settings = bpy.context.scene.tool_settings
brush = tool_settings.sculpt.brush

# Настроить кисть программно
def set_brush(name, strength=0.5, radius=50, autosmooth=0.0):
    brush = bpy.data.brushes.get(name)
    if brush:
        tool_settings.sculpt.brush = brush
        brush.strength = strength
        brush.size = radius
        brush.use_autosmooth = autosmooth > 0
        brush.autosmooth_factor = autosmooth

# Основные кисти
BRUSHES = {
    'DRAW': {'strength': 0.3, 'radius': 80},      # Базовая отрисовка
    'CLAY': {'strength': 0.4, 'radius': 100},     # Добавление объёма
    'CLAY_STRIPS': {'strength': 0.35, 'radius': 80}, # Полоски глины
    'SMOOTH': {'strength': 0.5, 'radius': 100},   # Сглаживание (Shift)
    'GRAB': {'strength': 0.5, 'radius': 120},     # Перетаскивание (G)
    'INFLATE': {'strength': 0.3, 'radius': 80},   # Надувание
    'CREASE': {'strength': 0.4, 'radius': 40},    # Уточнение краёв
    'LAYER': {'strength': 0.3, 'radius': 60},     # Слои (высота)
    'SCRAPE': {'strength': 0.3, 'radius': 60},    # Скребливание
    'PINCH': {'strength': 0.4, 'radius': 40},     # Сжатие краёв
}

for bname, params in BRUSHES.items():
    set_brush(bname, **params)
```

### MASKING И HIDING
```python
# Маска (Ctrl+I инверсия)
bpy.ops.sculpt.mask_clear()
# Нарисовать маску кистью MASK
# Скрыть маскированное: H
# Показать всё: Alt+H

# Face Sets (Blender 3.0+)
bpy.ops.sculpt.face_set_init()
# Разные цвета для разных частей
```

---

## 📊 DYNTOPO vs MULTIRES

| Характеристика | DYNTOPO | MULTIRES |
|----------------|---------|----------|
| **Топология** | Динамическая, меняется | Фиксированная, поделена |
| **Анимация** | Нет (нужен ретопо) | Да (базовая топология сохранена) |
| **Память** | Эффективна | Выше (все уровни в RAM) |
| **Детализация** | Любая, локально | Ограничена уровнем подделения |
| **Симметрия** | Полная | Полная |
| **Export** | Нужен ретопо | Можно экспортировать уровень |

---

## 💡 ПРО ТИПЫ

### Matcap для удобства
```python
# В Viewport Shading → Matcap
# Рекомендуемые: clay, clay_brown, skin
```

### Lazy Stroke для плавных линий
```python
brush = bpy.data.brushes['DRAW']
brush.use_lazy_stroke = True
brush.lazy_radius = 20
```

### Face Sets для изоляции
```python
# Создать Face Set
bpy.ops.sculpt.face_set_create(name="Eyes")
# Изолировать: Select Face Set → H
```

---

## ⚠️ ЧАСТЫЕ ПРОБЛЕМЫ

| Проблема | Решение |
|----------|---------|
| Лаги при Dyntopo | Увеличь `detail_size`, уменьши `constant_detail` |
| Артефакты симметрии | Проверь центр объекта, примени `Object > Set Origin > Center of Mass` |
| Потеря деталей при Multires | Не скачивай уровни выше `sculpt_level` |
| Дырки в меше | `Mesh > Clean Up > Fill Holes` или `Make Manifold` |

---

## 🔗 LINKS

- **Cases:** [Case 04: Character Rig](../cases/case_04_character_rig.md)
- **Workflows:** [WF 04: Character Animation](../workflows/wf_04_character_animation.md)
- **Prompts:** [P06 Retopology](./06_retopology_workflow.md), [P04 BMesh](./04_mesh_editing_bmesh.md)
- **Next:** [P10: Node Group Creation](./10_node_groups.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/08_sculpting_basics.md` |
| Russian | `multilang/ru/prompts/08_sculpting_basics.md` |