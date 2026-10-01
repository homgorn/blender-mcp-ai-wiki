---
id: 24_gn_scatter
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P24: GN SCATTER & DISTRIBUTION

> 目标: ---

**ID:** 24_gn_scatter | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** density, lod, poisson, poisson-disk, scatter, weight, weight-paint

## 使用方法
这是 '24_gn_scatter' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
24_gn_scatter / prompts / density, lod, poisson, poisson-disk, scatter, weight, weight-paint
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

# P24: GN SCATTER & DISTRIBUTION

**ID:** P24 | **Кластер:** Geometry Nodes | **Сложность:** ⭐⭐ | **Теги:** #scatter #poisson-disk #density #weight-paint #lod

---

## 🎯 ЦЕЛЬ
Продвинутое рассеивание: density attribute, weight paint, random pick, LOD по дистанции

---

## 📝 ПРОМПТ (РУС)

```
Рассей коллекцию "[COLL]" по "[TARGET]":
Density: [attribute/значение], Count [N], Scale [min-max], Seed [S]
```

---

## 📝 ПРОМПТ (ENG)

```
Scatter collection "[COLL]" on "[TARGET]":
Density: [attribute/value], Count [N], Scale [min-max], Seed [S]
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def gn_scatter_advanced(target, collection, density_attr="", count=1000, smin=0.8, smax=1.2, seed=42):
    obj = bpy.data.objects.get(target)
    coll = bpy.data.collections.get(collection)
    if not obj or not coll:
        raise ValueError("Target or collection not found")
    ng = bpy.data.node_groups.new("GN_ScatterAdv", 'GeometryNodeTree')
    nodes, links = ng.nodes, ng.links
    nodes.clear()
    inp = nodes.new('NodeGroupInput'); out = nodes.new('NodeGroupOutput')
    inp.location = (-500, 0); out.location = (500, 0)
    ng.interface.new_socket(name="Density", in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    dist = nodes.new('GeometryNodeDistributePointsOnFaces')
    dist.location = (-200, 0)
    dist.distribute_method = 'POISSON'
    if density_attr:
        dist.inputs['Density Attribute'].default_value = density_attr
    inst = nodes.new('GeometryNodeInstanceOnPoints')
    inst.location = (0, 0)
    rnd_scale = nodes.new('GeometryNodeRandomValue')
    rnd_scale.data_type = 'FLOAT_VECTOR'
    rnd_scale.location = (-200, -200)
    rnd_scale.outputs[0].default_value = (smin, smin, smin)
    rnd_scale.outputs[1].default_value = (smax, smax, smax)
    links.new(rnd_scale.outputs['Value'], inst.inputs['Scale'])
    real = nodes.new('GeometryNodeRealizeInstances')
    real.location = (300, 0)
    links.new(dist.outputs['Points'], inst.inputs['Points'])
    links.new(inst.outputs['Instances'], real.inputs['Geometry'])
    links.new(real.outputs['Geometry'], out.inputs['Geometry'])
    mod = obj.modifiers.new("GN_Scatter", 'NODES')
    mod.node_group = ng
    mod["Input_1"] = count
    mod["Input_2"] = seed
    return {"scatter": collection, "target": target}

# gn_scatter_advanced("Ground", "Trees", density_attr="Density", count=2000)
```

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 05](../cases/case_05_procedural_city.md)
- **Следующий:** [P25: Procedural Building](./25_procedural_building.md)
