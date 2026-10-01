---
lang: ru
tags: [pipeline, prompt]
---
# P47: ALEMBIC CACHE PIPELINE

**ID:** P47 | **Кластер:** Pipeline | **Сложность:** ⭐⭐ | **Теги:** #alembic #cache #abc #simulation #render-farm #pipeline

---

## 🎯 ЦЕЛЬ
Кэширование анимации/симуляций в Alembic: экспорт, velocity blur, импорт на ферме

---

## 📝 ПРОМПТ (РУС)

```
Запеки Alembic "[OBJECTS]" кадры [A-B]: flatten, subsamples [N],
UV/normals ON. Проверь размер файла и motion blur.
```

---

## 📝 ПРОМПТ (ENG)

```
Bake Alembic "[OBJECTS]" frames [A-B]: flatten, subsamples [N],
UVs/normals ON. Verify file size and motion blur.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def export_alembic(objects, filepath, start=1, end=250, subsamples=4):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        bpy.data.objects.get(o).select_set(True)
    bpy.ops.wm.alembic_export(
        filepath=filepath, selected=True,
        start=start, end=end, flatten=True, subsamples=subsamples,
        write_uvs=True, write_normals=True, write_vertex_colors=True,
        export_subdivision=True)
    import os
    size_mb = os.path.getsize(filepath) / 1024 / 1024
    return {"alembic": filepath, "mb": round(size_mb, 1)}

def import_alembic(filepath, as_background_job=False):
    bpy.ops.wm.alembic_import(
        filepath=filepath, as_background_job=as_background_job)
    return {"imported": filepath}

# export_alembic(["Cloth_Shirt", "Hero_Body"], "//cache/shot_010.abc", 1, 120)
```

---

## 📊 ПАРАМЕТРЫ
| Параметр | Значение |
|----------|----------|
| Flatten | ON (чистая иерархия для фермы) |
| Subsamples | 4 (motion blur), 1 (статика) |
| UVs/Normals | ON (иначе shading сломан) |
| Velocities | ON для motion blur |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P22: PARTICLE SYSTEMS](22_particles.md), [P21: PHYSICS SIMULATION](21_physics_simulation.md), [P29: BATCH PROCESSING & CLI](29_batch_cli.md), [P49: RENDER FARM SUBMIT](49_farm_submit.md), [P14: CAMERA & COMPOSITION](14_camera_composition.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md)
- **Теги:** #alembic, #cache, #pipeline, #prompt, #render, #render-farm, #simulation

