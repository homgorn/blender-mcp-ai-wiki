---
id: case_02_game_props
lang: es
orig_lang: ru
category: cases
type: case
difficulty: 2
translation: template
---
# КЕЙС 02: JUEGO PROPS PIPELINE

> Objetivo: 

**ID:** case_02_game_props | **Lang:** es | **Orig:** ru | **Category:** cases | **Tags:** **, 8b7355

## Cómo usar
Esta es la versión en español de 'case_02_game_props'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
case_02_game_props / cases / **, 8b7355
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: case_02_game_props
lang: ru
orig_lang: ru
category: cases
type: case
difficulty: 2
---

# КЕЙС 02: GAME PROPS PIPELINE

> Цель: ## 🌍 MULTILANG

**ID:** case_02_game_props | **Lang:** ru | **Orig:** ru | **Category:** cases | **Tags:** 8b7355

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

- **Воркфлоу:** [WF 07: Game Asset Pipeline](../workflows/wf_07_game_asset_pipeline.md)
- **Сетяп:** [Setup 01: blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Кейсы:** [Case 05: Procedural City](../cases/case_05_procedural_city.md) — масштабирование
- **Следующий:** [Case 03: Product Viz](../cases/case_03_product_viz.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/cases/case_02_game_props.md` |
| Русский | `multilang/ru/cases/case_02_game_props.md` |