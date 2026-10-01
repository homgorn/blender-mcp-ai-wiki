---
id: 31_render_passes_aov
lang: ru
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P31: RENDER PASSES & AOV

> Цель: ---

**ID:** 31_render_passes_aov | **Lang:** ru | **Orig:** ru | **Category:** prompts | **Tags:** aov, compositing, cryptomatte, exr, passes, render

## Как пользоваться
Это русская версия '31_render_passes_aov'. Кодовые блоки языконезависимы. Выполняйте шаги по порядку, проверяйте разделом Проверка.

## MCP-промпт (копипаст)
```
31_render_passes_aov / prompts / aov, compositing, cryptomatte, exr, passes, render
```

> Замечание: код/пути оставлены на английском для совместимости Blender/Python.

---

# P31: RENDER PASSES & AOV

**ID:** P31 | **Кластер:** Rendering | **Сложность:** ⭐⭐ | **Теги:** #render #passes #aov #cryptomatte #exr #compositing

---

## 🎯 ЦЕЛЬ
Включить нужные пассы, вывести Multilayer EXR, проверить в Compositor/Viewer

---

## 📝 ПРОМПТ (РУС)

```
Включи пассы для "[SCENE]": [Combined, Depth, Normal, Mist, AO, Emission, Shadow, Cryptomatte Object/Material].
Вывод: Multilayer EXR 32-bit в //renders/exr/. Проверь каждый пасс во Viewer.
```

---

## 📝 ПРОМПТ (ENG)

```
Enable passes for "[SCENE]": [Combined, Depth, Normal, Mist, AO, Emission, Shadow, Cryptomatte Object/Material].
Output: Multilayer EXR 32-bit to //renders/exr/. Verify each pass in Viewer.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def enable_passes():
    vl = bpy.context.view_layer
    vl.use_pass_combined = True
    vl.use_pass_z = True
    vl.use_pass_normal = True
    vl.use_pass_mist = True
    vl.use_pass_ambient_occlusion = True
    vl.use_pass_emission = True
    vl.use_pass_shadow = True
    vl.use_pass_diffuse_color = True
    vl.use_pass_glossy_color = True
    vl.use_pass_cryptomatte = True
    vl.cryptomatte_use_object = True
    vl.cryptomatte_use_material = True
    s = bpy.context.scene
    s.use_nodes = True
    s.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    s.render.image_settings.color_mode = 'RGBA'
    s.render.image_settings.color_depth = '32'
    s.render.image_settings.exr_codec = 'ZIP'
    s.render.filepath = "//renders/exr/pass_####"
    return {"passes": "enabled", "output": s.render.filepath}
```

---

## 📊 ПАССЫ
| Пасс | Зачем |
|------|-------|
| Depth | Туман, DOF в посте, маски по дистанции |
| Normal | Рельеф, релайт |
| Mist | Атмосфера |
| AO | Контактные тени |
| Cryptomatte | Маски объектов/материалов без ручной ротоскопии |

---

## 🔗 СВЯЗИ
- **Промпты:** [P15 Compositing](./15_compositing.md), [P13 Lighting](./13_lighting_hdri.md)
- **Следующий:** [P32: Light Linking](./32_light_linking.md)
