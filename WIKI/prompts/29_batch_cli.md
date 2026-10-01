---
lang: ru
tags: [automation, prompt]
---
# P29: BATCH PROCESSING & CLI

**ID:** P29 | **Кластер:** Advanced | **Сложность:** ⭐⭐ | **Теги:** #batch #cli #headless #automation #render-farm

---

## 🎯 ЦЕЛЬ
Пакетная обработка: `blender -b -P script.py`, батч-рендер, конвертация

---

## 📝 ПРОМПТ (РУС)

```
Запусти батч: blender -b [SCENE] -P [SCRIPT] -- [ARGS]
Пример: "Отрендери 1-250 во всех .blend из папки"
```

---

## 📝 ПРОМПТ (ENG)

```
Run batch: blender -b [SCENE] -P [SCRIPT] -- [ARGS]
Example: "Render 1-250 for all .blend in folder"
```

---

## 🔧 КОМАНДЫ

```bash
# Один кадр
blender -b scene.blend -E CYCLES -o //out/frame_#### -f 1
# Анимация
blender -b scene.blend -E CYCLES -o //out/anim_#### -s 1 -e 250 -a
# Скрипт
blender -b scene.blend -P setup_render.py -o //out/ -f 1
# Пакет по папке
for f in scenes/*.blend; do blender -b "$f" -P batch.py -- --out renders/; done
```

```python
# batch.py шаблон
import bpy, sys
argv = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=argv[0])
bpy.context.scene.render.filepath = argv[1]
bpy.ops.render.render(animation=True)
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P47: ALEMBIC CACHE PIPELINE](47_alembic_cache.md), [P49: RENDER FARM SUBMIT](49_farm_submit.md), [P14: CAMERA & COMPOSITION](14_camera_composition.md), [P18: DRIVERS & CONSTRAINTS](18_drivers_constraints.md), [P22: PARTICLE SYSTEMS](22_particles.md)
- **По темам:** [P30: OPTIMIZATION (SCENE & RENDER)](30_optimization.md), [P31: RENDER PASSES & AOV](31_render_passes_aov.md), [P40: VERSION CONTROL & RENDER JOBS](40_version_control.md)
- **Теги:** #automation, #batch, #cli, #headless, #prompt, #render, #render-farm

