---
lang: ru
tags: [prompt, render]
---
# P30: OPTIMIZATION (SCENE & RENDER)

**ID:** P30 | **Кластер:** Advanced | **Сложность:** ⭐⭐ | **Теги:** #optimization #decimate #lod #instances #samples #denoise

---

## 🎯 ЦЕЛЬ
Оптимизация сцены и рендера: полигоны, текстуры, сэмплы, инстансинг

---

## 📝 ПРОМПТ (РУС)

```
Оптимизируй сцену: decimate [ratio], LOD [уровни], текстуры [res],
сэмплы [N] + denoise. Цель: [FPS/VRAM/время кадра]
```

---

## 📝 ПРОМПТ (ENG)

```
Optimize scene: decimate [ratio], LOD [levels], textures [res],
samples [N] + denoise. Target: [FPS/VRAM/frame time]
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def optimize_scene(target_tris=500000, tex_res=2048, samples=128):
    # 1. Decimate heavy meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            tris = sum(len(p.vertices)-2 for p in obj.data.polygons)
            if tris > 50000:
                mod = obj.modifiers.new("Decimate_Opt", 'DECIMATE')
                mod.ratio = max(0.1, target_tris / max(tris, 1) / len(bpy.data.objects))
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=mod.name)
    # 2. Render settings
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.01
    return {"optimized": True, "samples": samples}

# optimize_scene()
```

---

## 📊 ЧЕК-ЛИСТ
- [ ] Применены scale, удалены doubles
- [ ] LOD0/1/2 для тяжёлых объектов
- [ ] Текстуры ≤2k для фона, 4k только hero
- [ ] Adaptive sampling + denoise
- [ ] Instancing вместо дубликатов

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P06: RETOPOLOGY WORKFLOW](06_retopology_workflow.md), [P07: INSTANCING & ARRAYS](07_instancing_arrays.md), [P14: CAMERA & COMPOSITION](14_camera_composition.md), [P22: PARTICLE SYSTEMS](22_particles.md), [P23: GEOMETRY NODES BASICS](23_geometry_nodes_basics.md)
- **По темам:** [P24: GN SCATTER & DISTRIBUTION](24_gn_scatter.md), [P29: BATCH PROCESSING & CLI](29_batch_cli.md), [P31: RENDER PASSES & AOV](31_render_passes_aov.md)
- **Теги:** #decimate, #denoise, #instances, #lod, #optimization, #prompt, #render, #samples

