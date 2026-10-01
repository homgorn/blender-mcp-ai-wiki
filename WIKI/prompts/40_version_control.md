---
lang: ru
tags: [prompt, render]
---
# P40: VERSION CONTROL & RENDER JOBS

**ID:** P40 | **Кластер:** Pipeline | **Сложность:** ⭐⭐ | **Теги:** #git #lfs #versioning #flamenco #ci #backup

---

## 🎯 ЦЕЛЬ
Версионирование .blend (Git LFS + lock) и отправка рендер-джобов (Flamenco/CLI)

---

## 📝 ПРОМПТ (РУС)

```
Настрой версионирование: LFS track [маски], lock [мейн-сцены].
Отправь джобу: frames [A-B], samples [N], output [путь].
```

---

## 📝 ПРОМПТ (ENG)

```
Setup versioning: LFS track [masks], lock [main scenes].
Submit job: frames [A-B], samples [N], output [path].
```

---

## 🔧 КОМАНДЫ

```bash
# .gitattributes
# *.blend filter=lfs diff=lfs merge=lfs -text
# *.exr filter=lfs diff=lfs merge=lfs -text
# *.fbx filter=lfs diff=lfs merge=lfs -text
# *.png filter=lfs diff=lfs merge=lfs -text
```

```python
# save versioned copy
import bpy, datetime
v = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bpy.ops.wm.save_as_mainfile(filepath=f"//versions/scene_v{v}.blend")
```

```bash
# CLI render job
# blender -b scenes/main.blend -E CYCLES -o //renders/anim_#### -s 1 -e 250 -a
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P49: RENDER FARM SUBMIT](49_farm_submit.md), [P14: CAMERA & COMPOSITION](14_camera_composition.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P29: BATCH PROCESSING & CLI](29_batch_cli.md), [P30: OPTIMIZATION (SCENE & RENDER)](30_optimization.md)
- **По темам:** [P31: RENDER PASSES & AOV](31_render_passes_aov.md), [P41: DISPLACEMENT & MICRO-DETAIL](41_displacement_micro.md), [P43: CAMERA SWITCHING & MARKERS](43_camera_switching.md)
- **Теги:** #backup, #ci, #flamenco, #git, #lfs, #prompt, #render, #versioning

