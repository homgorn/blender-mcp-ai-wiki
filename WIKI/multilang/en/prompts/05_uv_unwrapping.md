---
id: 05_uv_unwrapping
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P05: UV UNWRAPPING STRATEGIES

> Goal: ## 🌍 MULTILANG

**ID:** 05_uv_unwrapping | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** **, procedural, texturing, unwrapping, uv

---

# P05: UV UNWRAPPING STRATEGIES

**ID:** P05 | **Кластер:** Geometry Basics | **Сложность:** ⭐⭐ | **Теги:** #uv #unwrapping #texturing #procedural

---

## 🎯 ЦЕЛЬ
Автоматические и полуавтоматические стратегии UV-развёртки для разных типов объектов

---

## 📝 ПРОМПТ (РУС)

```
Разверни UV для "[OBJECT_NAME]" методом [METHOD]:
- SMART_PROJECT: автоматический, угол [LIMIT]
- LIGHTMAP_PACK: для 베이ка, padding [PX]
- CUBE_PROJECTION: кубическая проекция
- SPHERE_PROJECTION: сферическая
- MANUAL_SEAMS: по швам (нужны预先 отмеченные seams)
```

---

## 📝 ПРОМПТ (ENG)

```
Unwrap UV for "[OBJECT_NAME]" using [METHOD]:
- SMART_PROJECT: automatic, angle [LIMIT]
- LIGHTMAP_PACK: for baking, padding [PX]
- CUBE_PROJECTION: cubic projection
- SPHERE_PROJECTION: spherical
- MANUAL_SEAMS: by seams (pre-marked seams required)
```

---

## 🔧 MCP: `execute_blender_code`

### SMART UV PROJECT (Универсальный)
```python
import bpy

obj = bpy.data.objects.get("Target")
if not obj or obj.type != 'MESH':
    raise ValueError("Mesh object required")

# Подготовка
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

# Smart UV Project
bpy.ops.uv.smart_project(
    angle_limit=1.0472,      # 66° - порог для нового острова
    island_margin=0.02,      # отступ между островами
    area_weight=0.0,         # вес площади (0-1)
    correct_aspect=True,     # учитывать соотношение сторон
    scale_to_bounds=False,   # масштабировать в границы
)

bpy.ops.object.mode_set(mode='OBJECT')
print(f"Smart UV Project done: {len(obj.data.uv_layers)} UV maps")
```

### LIGHTMAP PACK (Для бейка)
```python
bpy.ops.uv.lightmap_pack(
    PADDING=4,               # пикселей между островами
    Px_MARGIN=4,             # отступ в пикселях
    share_tex_space=False,   # делить пространство
)
```

### CUBE / SPHERE PROJECTION
```python
# Кубическая (для архитектуры, коробок)
bpy.ops.uv.cube_project(
    cube_size=1.0,
    clip_to_bounds=True,
    correct_aspect=True,
)

# Сферическая (для окружений, неба)
bpy.ops.uv.sphere_project(
    direction='Z',           # ось проекции
    align='POLAR',           # выравнивание
)
```

### ПО ШВАМ (Ручное управление)
```python
# 1. Отметить швы (в EDIT mode)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.edges.ensure_lookup_table()

# Авто-швы по острым рёбрам
for e in bm.edges:
    if e.calc_face_angle() > 1.0472:  # > 60°
        e.use_seam = True

bmesh.update_edit_mesh(obj.data)

# 2. Развернуть по швам
bpy.ops.uv.unwrap(
    method='ANGLE_BASED',    # 'CONFORMAL' для органики
    margin=0.001,
    fill_holes=True,
    correct_aspect=True,
)

bpy.ops.object.mode_set(mode='OBJECT')
```

---

## 📊 СРАВНЕНИЕ МЕТОДОВ

| Метод | Скорость | Качество | Лучше для | Авто-швы |
|-------|----------|----------|-----------|----------|
| **Smart Project** | ⚡⚡⚡ | ⭐⭐ | Хард-сёрфейс, пропсы | Да |
| **Lightmap Pack** | ⚡⚡ | ⭐⭐ | Бейкинг, игры | Да |
| **Cube Project** | ⚡⚡⚡ | ⭐ | Архитектура, примитивы | Да |
| **Sphere Project** | ⚡⚡⚡ | ⭐ | Сферы, небо | Да |
| **Unwrap (Seams)** | ⚡ | ⭐⭐⭐ | Органика, персонажи | Нет (ручной) |
| **Follow Active Quads** | ⚡ | ⭐⭐ | Прямоугольные полосы | Частично |

---

## 💡 СТРАТЕГИИ ПО ТИПАМ ОБЪЕКТОВ

### Архитектура (стены, пол, потолок)
```python
# 1. Smart Project с большим margin
bpy.ops.uv.smart_project(angle_limit=1.2, island_margin=0.05)

# 2. Выровнять острова (опционально)
bpy.ops.uv.align_rotation(method='AXIS_X')
bpy.ops.uv.align_rotation(method='AXIS_Y')
```

### Персонажи / Органика
```python
# 1. Ручные швы по anatomiи
# 2. Unwrap с CONFORMAL
bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.005)

# 3. Pack islands
bpy.ops.uv.pack_islands(margin=0.01)
```

### Гейм-пропсы (Low-poly)
```python
# 1. Smart Project агрессивно
bpy.ops.uv.smart_project(angle_limit=1.5, island_margin=0.01)

# 2. Упаковать максимально плотно
bpy.ops.uv.pack_islands(margin=0.002, rotate=True)
```

### Текстуры для бейка (Normal, AO, Curvature)
```python
# Lightmap Pack с ненулевым padding
bpy.ops.uv.lightmap_pack(PADDING=8, Px_MARGIN=8)
```

---

## 🔧 ПРО: UV УТИЛИТЫ

### Проверить перекрытия
```python
# В EDIT mode
bpy.ops.uv.select_all(action='DESELECT')
bpy.ops.uv.select_overlap()
# Выделены перекрывающиеся острова
```

### Выровнять тексель (Texas Density)
```python
# Установить плотность текселей (пикселей на метр)
bpy.ops.uv.texel_density_set(target=512)  # 512 px/m
```

### Копировать UV между объектами
```python
src = bpy.data.objects["Source"]
dst = bpy.data.objects["Target"]

# Передать активный UV слой
for i, (sf, df) in enumerate(zip(src.data.polygons, dst.data.polygons)):
    for sl, dl in zip(sf.loop_indices, df.loop_indices):
        dst.data.uv_layers.active.data[dl].uv = src.data.uv_layers.active.data[sl].uv
```

---

## ⚠️ ЧАСТЫЕ ПРОБЛЕМЫ

| Проблема | Причина | Решение |
|----------|---------|---------|
| Растянутые текстуры | Неправильный aspect | `correct_aspect=True` |
| Перекрытия островов | Мало margin | Увеличь `island_margin` / `PADDING` |
| Видимые швы | Нет швов / плохие | Отметь `use_seam` на острых рёбрах |
| Неравномерная плотность | Разный масштаб | `Object > Apply > Scale` перед unwrap |
| Инверсия UV | Отрицательный масштаб | Проверь `scale.x * scale.y * scale.z > 0` |

---

## 🔗 СВЯЗИ

- **Кейсы:** [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **Воркфлоу:** [WF 03: Texture Pipeline](../workflows/wf_03_texture_pipeline.md)
- **Промпты:** [P04 BMesh](./04_mesh_editing_bmesh.md), [P11 Procedural Textures](./11_procedural_textures.md)
- **Следующий:** [P06: Retopology Workflow](./06_retopology_workflow.md)

---

## 🌍 MULTILANG

| Язык | Файл |
|------|------|
| English | `multilang/en/prompts/05_uv_unwrapping.md` |
| Русский | `multilang/ru/prompts/05_uv_unwrapping.md` |