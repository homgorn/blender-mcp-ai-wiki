---
id: 49_farm_submit
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P49: RENDER FARM SUBMIT

> Ziel: ---

**ID:** 49_farm_submit | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** chunks, flamenco, jobs, monitor, render, render-farm

## Verwendung
Dies ist die deutsche Version von '49_farm_submit'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
49_farm_submit / prompts / chunks, flamenco, jobs, monitor, render, render-farm
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P49: RENDER FARM SUBMIT

**ID:** P49 | **Кластер:** Pipeline | **Сложность:** ⭐⭐ | **Теги:** #render-farm #flamenco #jobs #chunks #monitor

---

## 🎯 ЦЕЛЬ
Отправка джобы на ферму: чанки кадров, приоритеты, мониторинг, ретрай упавших

---

## 📝 ПРОМПТ (РУС)

```
Отправь джобу "[SCENE]": кадры [A-B] чанками по [N],
samples [S], output [путь], приоритет [P]. Мониторь до конца.
```

---

## 📝 ПРОМПТ (ENG)

```
Submit job "[SCENE]": frames [A-B] in chunks of [N],
samples [S], output [path], priority [P]. Monitor to completion.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def prepare_farm_scene(samples=128, out="//renders/anim_####", fmt='OPEN_EXR_MULTILAYER'):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = True
    s.render.filepath = out
    s.render.image_settings.file_format = fmt
    s.render.image_settings.color_mode = 'RGBA'
    s.render.image_settings.color_depth = '16'
    # Все текстуры — packed или относительные пути
    for img in bpy.data.images:
        if img.source == 'FILE' and img.filepath.startswith('/'):
            img.filepath = '//textures/' + img.name
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_mainfile()
    return {"prepared": True, "samples": samples}

def chunk_frames(start, end, chunk=25):
    ranges = []
    f = start
    while f <= end:
        ranges.append((f, min(f + chunk - 1, end)))
        f += chunk
    return {"chunks": ranges}

# prepare_farm_scene(128)
# chunk_frames(1, 250, 25)
```

---

## 📊 ЧЕК-ЛИСТ ДЖОБЫ
- [ ] Текстуры packed / относительные пути
- [ ] Кэш симуляций запечён (не live)
- [ ] Output путь существует на всех воркерах
- [ ] Тестовый чанк 3 кадра прошёл
- [ ] Ретрай только упавших чанков

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 05 Render Farm](../setups/setup_05_render_farm.md), [Setup 04 Headless](../setups/setup_04_headless_render.md)
- **Следующий:** [P50: Turntable QA](./50_turntable_qa.md)
