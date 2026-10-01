---
lang: ru
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
- **Промпты:** [P11 Procedural](./11_procedural_textures.md), [P12 Texture Paint](./12_texture_painting.md)
- **Следующий:** [P38: Bake Pipeline](./38_bake_pipeline.md)
