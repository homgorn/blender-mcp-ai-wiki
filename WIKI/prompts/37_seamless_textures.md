---
lang: ru
tags: [prompt, texturing]
---
# P37: SEAMLESS TEXTURE WORKFLOW

**ID:** P37 | **Кластер:** Materials | **Сложность:** ⭐⭐ | **Теги:** #seamless #tiling #inpaint #dream-textures #uv

---

## 🎯 ЦЕЛЬ
Бесшовные тайлящиеся текстуры: генерация + проверка стыков + фикс inpaint

---

## 📝 ПРОМПТ (РУС)

```
Сгенерируй seamless "[материал]" [res], проверь стыки (offset 50%),
замаскируй швы → inpaint. Примени с repeat [N].
```

---

## 📝 ПРОМПТ (ENG)

```
Generate seamless "[material]" [res], check seams (offset 50%),
mask seams → inpaint. Apply with repeat [N].
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def tile_material(obj_name, scale=4.0):
    obj = bpy.data.objects.get(obj_name)
    mat = obj.active_material
    nodes = mat.node_tree.nodes
    mapping = next((n for n in nodes if n.type == 'MAPPING'), None)
    if not mapping:
        tex_coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        mat.node_tree.links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        for n in nodes:
            if n.type == 'TEX_IMAGE' and not n.inputs['Vector'].links:
                mat.node_tree.links.new(mapping.outputs['Vector'], n.inputs['Vector'])
    mapping.inputs['Scale'].default_value = (scale, scale, scale)
    return {"tiled": scale}
```

---

## 📊 ПРОВЕРКА ШВОВ
1. Image Editor → View → Repeat
2. Или UV offset 0.5 → швы в центре
3. Inpaint masked seams (Dream Textures / A1111)

---

## 🔗 СВЯЗИ

- **Прочие в категории «Промпты»:** [P05: UV UNWRAPPING STRATEGIES](05_uv_unwrapping.md), [P46: UDIM WORKFLOW](46_udim_workflow.md), [P12: TEXTURE PAINTING](12_texture_painting.md), [P19: NLA EDITOR WORKFLOW](19_nla_workflow.md), [P01: PRIMITIVE CREATION BASICS](01_geometry_basics.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [P02: BOOLEAN OPERATIONS](02_boolean_operations.md), [P03: MODIFIERS STACK](03_modifiers_stack.md)
- **Теги:** #dream, #dream-textures, #inpaint, #prompt, #seamless, #texturing, #tiling, #uv

