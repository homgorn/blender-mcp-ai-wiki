---
id: case_02_game_props
lang: ru
category: cases
status: full
tags: [case, game-assets, pipeline]
---
# CASE 02: GAME PROPS PIPELINE

**ID:** CASE-02 | **Тип:** Game Asset Production | **Сложность:** ⭐⭐ | **Время:** 30-60 мин

---

## 🎯 ЦЕЛЬ
Полный пайплайн создания гейм-готовых пропсов: от примитивов → оптимизация → UV → PBR материалы → экспорт

---

## 📋 ПЛАН РАБОТЫ (6 ШАГОВ)

### ШАГ 1: Блокаут (Primitives + Boolean)
**Промпты:** P01, P02
**Время:** 5-10 мин

```python
# Базовая форма
create_object("CUBE", "Prop_Base", [0,0,0], [1,1,1])
create_object("CYLINDER", "Prop_Detail", [0,0,1], [0.3,0.3,0.5])

# Булев для деталей
boolean_difference("Prop_Base", "Prop_Detail")
```

### ШАГ 2: Детализация (Bevel + Modifiers)
**Промпты:** P03
**Время:** 5 мин

```python
modifiers_stack = [
    ("BEVEL", {"width": 0.02, "segments": 3, "profile": 0.5}),
    ("WEIGHTED_NORMAL", {"weight": 100, "face_weight": 0.5}),
]
```

### ШАГ 3: Оптимизация (Decimate / Retopo)
**Промпты:** P06
**Время:** 5 мин

```python
# Target: 500-2000 tris для пропса
decimate_ratio = target_tris / current_tris
```

### ШАГ 4: UV Развёртка
**Промпты:** P05
**Время:** 5 мин

```python
# Smart Project для пропсов
bpy.ops.uv.smart_project(angle_limit=1.2, island_margin=0.005)
bpy.ops.uv.pack_islands(margin=0.002, rotate=True)
```

### ШАГ 5: PBR Материалы
**Промпты:** P09, P10
**Время:** 5-10 мин

```python
# Principled BSDF с текстурами
maps = {
    'base_color': 'prop_basecolor.png',
    'roughness': 'prop_roughness.png',
    'normal': 'prop_normal.png',
    'metallic': 'prop_metallic.png',
}
```

### ШАГ 6: Экспорт (GLTF/GLB)
**Время:** 2 мин

```python
bpy.ops.export_scene.gltf(
    filepath="prop.glb",
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_tangents=True,
)
```

---

## 🔧 MCP КОМАНДЫ ПОШАГОВО

### 1. Сцена
```bash
OpenCode: "Очисти сцену, создай новый проп: куб 1x1x1м с цилиндрическим вырезом в центре"
```

### 2. Модификаторы
```bash
OpenCode: "Добавь Bevel 0.02м 3 сегмента и Weighted Normal к пропсу"
```

### 3. UV
```bash
OpenCode: "Разверни UV Smart Project с margin 0.005, упакуй острова"
```

### 4. Материал
```bash
OpenCode: "Создай PBR материал: BaseColor #8B7355, Roughness 0.7, Metallic 0.0, присвой к пропсу"
```

### 5. Проверка
```bash
OpenCode: "Покажи статистику: трисы, вершины, UV острова, материалы"
```

### 6. Экспорт
```bash
OpenCode: "Экспорт пропса в GLB с тангентами, применить модификаторы"
```

---

## 📊 МЕТРИКИ КАЧЕСТВА

| Метрика | Target | Critical |
|---------|--------|----------|
| **Triangles** | 500-2000 | < 5000 |
| **UV Islands** | 1-8 | < 15 |
| **Texel Density** | 512 px/m | > 256 |
| **Overlapping UVs** | 0 | 0 |
| **Non-manifold edges** | 0 | 0 |
| **Material Slots** | 1-2 | < 4 |
| **File Size (GLB)** | < 500 KB | < 2 MB |

---

## 🎨 ВАРИАНТЫ ПРОПСОВ

| Тип | Tris | Особенности |
|-----|------|-------------|
| **Crate/Box** | 300-500 | Простой куб + bevel + детали |
| **Barrel** | 400-800 | Цилиндр + ребра + крышка |
| **Weapon** | 800-2000 | Boolean детали, острые края |
| **Furniture** | 1000-3000 | Модульные части, зеркалирование |
| **Vegetation** | 200-600 | Плоские полигоны + alpha |

---

## 🔗 ИСПОЛЬЗУЕМЫЕ ПРОМПТЫ

| Промпт | Роль |
|--------|------|
| [P01](../prompts/01_geometry_basics.md) | Базовая геометрия |
| [P02](../prompts/02_boolean_operations.md) | Булевы вычитания |
| [P03](../prompts/03_modifiers_stack.md) | Стек модификаторов |
| [P05](../prompts/05_uv_unwrapping.md) | UV развёртка |
| [P09](../prompts/09_principled_bsdf.md) | PBR материал |
| [P10](../prompts/10_node_groups.md) | Библиотека материалов |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 16: DUNGEON TILESET](case_16_dungeon_tileset.md)
- **По темам:** [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md), [CASE 06: ANIMATION LOOP](case_06_animation_loop.md)
- **Теги:** #case, #game-assets, #pipeline

