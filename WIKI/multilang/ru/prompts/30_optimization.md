---
id: 30_optimization
lang: ru
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P30: OPTIMIZATION (SCENE & RENDER)

> Цель: ---

**ID:** 30_optimization | **Lang:** ru | **Orig:** ru | **Category:** prompts | **Tags:** decimate, denoise, instances, lod, optimization, samples

## Как пользоваться
Это русская версия '30_optimization'. Кодовые блоки языконезависимы. Выполняйте шаги по порядку, проверяйте разделом Проверка.

## MCP-промпт (копипаст)
```
30_optimization / prompts / decimate, denoise, instances, lod, optimization, samples
```

> Замечание: код/пути оставлены на английском для совместимости Blender/Python.

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
- **Кейсы:** [Case 02](../cases/case_02_game_props.md)
- **Воркфлоу:** [WF 07](../workflows/wf_07_game_asset_pipeline.md)
