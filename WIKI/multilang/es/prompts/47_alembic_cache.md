---
id: 47_alembic_cache
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P47: ALEMBIC CACHE PIPELINE

> Objetivo: ---

**ID:** 47_alembic_cache | **Lang:** es | **Orig:** ru | **Category:** prompts | **Tags:** alembic, cache, pipeline, render, render-farm, simulation

## Cómo usar
Esta es la versión en español de '47_alembic_cache'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
47_alembic_cache / prompts / alembic, cache, pipeline, render, render-farm, simulation
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

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
- **Промпты:** [P21 Physics](./21_physics_simulation.md), [P40 Version Control](./40_version_control.md)
- **Сетяпы:** [Setup 05 Render Farm](../setups/setup_05_render_farm.md)
- **Следующий:** [P48: Eevee vs Cycles](./48_eevee_vs_cycles.md)
