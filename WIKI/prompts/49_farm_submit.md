---
lang: ru
tags: [prompt, render, render-farm]
---
# P49: RENDER FARM SUBMIT

**ID:** P49 | **Кластер:** Pipeline | **Сложность:** ⭐⭐ | **Теги:** #render-farm #flamenco #jobs #chunks #monitor

---

## 🎯 ЦЕЛЬ
Отправка джобы на ферму: чанки кадров, приоритеты, мониторинг, ретрай упавших

---

## 📝 ПРОМПТ (РУС)

```
Отправь джобу "[SCENE]": кадры [A-B] чанками по [N],
samples [S], output [путь], приоритет [P]. Мониторь до конца.
```

---

## 📝 ПРОМПТ (ENG)

```
Submit job "[SCENE]": frames [A-B] in chunks of [N],
samples [S], output [path], priority [P]. Monitor to completion.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def prepare_farm_scene(samples=128, out="//renders/anim_####", fmt='OPEN_EXR_MULTILAYER'):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = True
    s.render.filepath = out
    s.render.image_settings.file_format = fmt
    s.render.image_settings.color_mode = 'RGBA'
    s.render.image_settings.color_depth = '16'
    # Все текстуры — packed или относительные пути
    for img in bpy.data.images:
        if img.source == 'FILE' and img.filepath.startswith('/'):
            img.filepath = '//textures/' + img.name
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_mainfile()
    return {"prepared": True, "samples": samples}

def chunk_frames(start, end, chunk=25):
    ranges = []
    f = start
    while f <= end:
        ranges.append((f, min(f + chunk - 1, end)))
        f += chunk
    return {"chunks": ranges}

# prepare_farm_scene(128)
# chunk_frames(1, 250, 25)
```

---

## 📊 ЧЕК-ЛИСТ ДЖОБЫ
- [ ] Текстуры packed / относительные пути
- [ ] Кэш симуляций запечён (не live)
- [ ] Output путь существует на всех воркерах
- [ ] Тестовый чанк 3 кадра прошёл
- [ ] Ретрай только упавших чанков

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P29: BATCH PROCESSING & CLI](29_batch_cli.md), [P40: VERSION CONTROL & RENDER JOBS](40_version_control.md), [P47: ALEMBIC CACHE PIPELINE](47_alembic_cache.md), [P14: CAMERA & COMPOSITION](14_camera_composition.md), [P22: PARTICLE SYSTEMS](22_particles.md)
- **По темам:** [P30: OPTIMIZATION (SCENE & RENDER)](30_optimization.md), [P31: RENDER PASSES & AOV](31_render_passes_aov.md), [P41: DISPLACEMENT & MICRO-DETAIL](41_displacement_micro.md)
- **Теги:** #chunks, #flamenco, #jobs, #monitor, #prompt, #render, #render-farm

