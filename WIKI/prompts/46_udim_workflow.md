---
lang: ru
---
# P46: UDIM WORKFLOW

**ID:** P46 | **Кластер:** Materials | **Сложность:** ⭐⭐ | **Теги:** #udim #uv-tiles #mari #texturing #baking

---

## 🎯 ЦЕЛЬ
UDIM-тайлы: раскладка 1001–10xx, нейминг, bake/export по тайлам

---

## 📝 ПРОМПТ (РУС)

```
Разложи UV "[OBJECT]" по UDIM: [назначение тайлов],
нейминг `{asset}_{map}_<UDIM>.png`. Проверь перекрытия.
```

---

## 📝 ПРОМПТ (ENG)

```
Lay out UV of "[OBJECT]" across UDIMs: [tile assignment],
naming `{asset}_{map}_<UDIM>.png`. Check overlaps.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def udim_report(obj_name):
    obj = bpy.data.objects.get(obj_name)
    mesh = obj.data
    tiles = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            uv = mesh.uv_layers.active.data[li].uv
            tile = 1001 + int(uv.x) + int(uv.y) * 10
            tiles.setdefault(tile, 0)
            tiles[tile] += 1
    return {"tiles": sorted(tiles), "loops": sum(tiles.values())}

def udim_fill_template(obj_name, tile=1001, color=(0.5, 0.5, 0.5, 1.0), res=2048):
    img = bpy.data.images.new(f"{obj_name}_{tile}", res, res, alpha=True)
    img.source = 'TILED'
    # tile_number: Blender API хранит номер тайла; создаём через оператор
    bpy.context.view_layer.objects.active = bpy.data.objects.get(obj_name)
    return {"tile_image": img.name}

# udim_report("Hero_Body")
```

---

## 📊 РАСКЛАДКА (пример персонаж)
| UDIM | Часть | Res |
|------|-------|-----|
| 1001 | Голова/шея | 4k |
| 1002 | Торс/руки | 2k |
| 1003 | Ноги | 2k |
| 1004 | Кисти/ступни/мелочи | 2k |

---

## 📊 НЕЙМИНГ
`{asset}_{map}_{udim}.{ext}` → `hero_basecolor_1001.png`. `<UDIM>` плейсхолдер понимают Substance/Mari/Blender.

---

## 🔗 СВЯЗИ
- **Промпты:** [P05 UV](./05_uv_unwrapping.md), [P38 Bake](./38_bake_pipeline.md)
- **Следующий:** [P47: Alembic Cache](./47_alembic_cache.md)
