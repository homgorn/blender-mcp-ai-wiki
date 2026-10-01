---
lang: ru
tags: [cycles, eevee, prompt]
---
# P48: EEVEE VS CYCLES DECISION

**ID:** P48 | **Кластер:** Rendering | **Сложность:** ⭐⭐ | **Теги:** #eevee #cycles #render-engine #decision #presets #performance

---

## 🎯 ЦЕЛЬ
Выбрать движок под задачу: матрица решений + готовые пресеты настроек

---

## 📝 ПРОМПТ (РУС)

```
Выбери движок для "[задача]": [archviz/product/animation/stylized/vr].
Примени пресет, объясни 3 причины выбора.
```

---

## 📝 ПРОМПТ (ENG)

```
Pick engine for "[task]": [archviz/product/animation/stylized/vr].
Apply preset, give 3 reasons.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def apply_engine_preset(preset='cycles_preview'):
    s = bpy.context.scene
    if preset == 'cycles_preview':
        s.render.engine = 'CYCLES'
        s.cycles.samples = 64
        s.cycles.use_denoising = True
        s.cycles.use_adaptive_sampling = True
    elif preset == 'cycles_final':
        s.render.engine = 'CYCLES'
        s.cycles.samples = 256
        s.cycles.use_denoising = True
        s.cycles.denoiser = 'OPTIX'
        s.cycles.use_adaptive_sampling = True
        s.cycles.adaptive_threshold = 0.01
    elif preset == 'eevee_preview':
        s.render.engine = 'BLENDER_EEVEE_NEXT'
        s.eevee.taa_render_samples = 16
    elif preset == 'eevee_final':
        s.render.engine = 'BLENDER_EEVEE_NEXT'
        s.eevee.taa_render_samples = 64
        s.eevee.use_bloom = True
        s.eevee.use_ssr = True
        s.eevee.use_ssr_refraction = True
    return {"preset": preset, "engine": s.render.engine}

# apply_engine_preset('cycles_final')
```

---

## 📊 МАТРИЦА
| Задача | Движок | Почему |
|--------|--------|--------|
| ArchViz фотореализм | Cycles | GI, каустика, дисплейсмент |
| Product hero | Cycles | Точные отражения/преломления |
| Анимация сериал | EEVEE Next | Скорость, стабильный вид |
| Стилизация/NPR | EEVEE Next | Shader to RGB, lineart |
| VR превью | EEVEE Next | FPS |
| Текстуры bake | Cycles | Корректный бейк |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P32: LIGHT LINKING & SHADOWS](32_light_linking.md), [P41: DISPLACEMENT & MICRO-DETAIL](41_displacement_micro.md), [P14: CAMERA & COMPOSITION](14_camera_composition.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P29: BATCH PROCESSING & CLI](29_batch_cli.md)
- **По темам:** [P30: OPTIMIZATION (SCENE & RENDER)](30_optimization.md), [P31: RENDER PASSES & AOV](31_render_passes_aov.md), [P40: VERSION CONTROL & RENDER JOBS](40_version_control.md)
- **Теги:** #cycles, #decision, #eevee, #performance, #presets, #prompt, #render, #render-engine

