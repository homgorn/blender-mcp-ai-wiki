---
id: 48_eevee_vs_cycles
lang: en
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P48: EEVEE VS CYCLES DECISION

> Goal: ---

**ID:** 48_eevee_vs_cycles | **Lang:** en | **Orig:** ru | **Category:** prompts | **Tags:** cycles, decision, eevee, performance, presets, render, render-engine

## How to use
This page is the en version of '48_eevee_vs_cycles'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.

## MCP Prompt (copy-paste)
```
48_eevee_vs_cycles / prompts / cycles, decision, eevee, performance, presets, render, render-engine
```

> Note: code/paths stay in English for Blender/Python compatibility.

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
- **Промпты:** [P13 Lighting](./13_lighting_hdri.md), [P48→P30 Optimization](./30_optimization.md)
- **Следующий:** [P49: Farm Submit](./49_farm_submit.md)
