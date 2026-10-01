---
id: 42_portals_caustics
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P42: LIGHT PORTALS & CAUSTICS

> 目标: ---

**ID:** 42_portals_caustics | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** caustics, cycles, daylight, glass, interior, portals

## 使用方法
这是 '42_portals_caustics' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
42_portals_caustics / prompts / caustics, cycles, daylight, glass, interior, portals
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

# P42: LIGHT PORTALS & CAUSTICS

**ID:** P42 | **Кластер:** Lighting | **Сложность:** ⭐⭐⭐ | **Теги:** #portals #caustics #interior #daylight #cycles #glass

---

## 🎯 ЦЕЛЬ
Дневной интерьер без шума: порталы на окнах + каустика для стекла/воды

---

## 📝 ПРОМПТ (РУС)

```
Поставь порталы на все окна "[ROOM]", включи каустику
(reflective/refractive), samples [N]. Проверь шум в углах.
```

---

## 📝 ПРОМПТ (ENG)

```
Place portals on all windows of "[ROOM]", enable caustics
(reflective/refractive), samples [N]. Check noise in corners.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def add_portals(window_objs, portal_size_pad=0.1):
    made = []
    for wname in window_objs:
        w = bpy.data.objects.get(wname)
        if not w:
            continue
        dims = w.dimensions
        bpy.ops.mesh.primitive_plane_add(size=1)
        p = bpy.context.active_object
        p.name = f"Portal_{wname}"
        p.dimensions = (dims.x + portal_size_pad, dims.y + portal_size_pad, 0.01)
        p.location = w.location
        p.rotation_euler = w.rotation_euler
        # Портал — это Area light с portal enabled
        ld = bpy.data.lights.new(f"Portal_{wname}", 'AREA')
        p.data = ld
        ld.use_portal = True
        ld.energy = 0.0
        made.append(p.name)
    return {"portals": made}

def enable_caustics(samples=256):
    s = bpy.context.scene
    s.cycles.caustics_reflective = True
    s.cycles.caustics_refractive = True
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.glossy_bounces = max(s.cycles.glossy_bounces, 8)
    s.cycles.transmission_bounces = max(s.cycles.transmission_bounces, 12)
    return {"caustics": True, "samples": samples}

# add_portals(["Window_01", "Window_02"])
# enable_caustics(256)
```

---

## 📊 КОГДА НУЖНО
| Кейс | Порталы | Каустика |
|------|---------|----------|
| Дневной интерьер | Да (3–5x меньше шума) | Нет |
| Бассейн/ванна | Нет | Да (refractive) |
| Хром/зеркала | Нет | Да (reflective) |
| Ночь/студия | Нет | Нет |

---

## 🔗 СВЯЗИ
- **Промпты:** [P13 Lighting](./13_lighting_hdri.md), [P09 Principled](./09_principled_bsdf.md)
- **Следующий:** [P43: Camera Switching](./43_camera_switching.md)
