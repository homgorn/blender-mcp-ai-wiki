---
id: 29_batch_cli
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P29: BATCH PROCESSING & CLI

> Ziel: ---

**ID:** 29_batch_cli | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** automation, batch, cli, headless, render, render-farm

## Verwendung
Dies ist die deutsche Version von '29_batch_cli'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
29_batch_cli / prompts / automation, batch, cli, headless, render, render-farm
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P29: BATCH PROCESSING & CLI

**ID:** P29 | **Кластер:** Advanced | **Сложность:** ⭐⭐ | **Теги:** #batch #cli #headless #automation #render-farm

---

## 🎯 ЦЕЛЬ
Пакетная обработка: `blender -b -P script.py`, батч-рендер, конвертация

---

## 📝 ПРОМПТ (РУС)

```
Запусти батч: blender -b [SCENE] -P [SCRIPT] -- [ARGS]
Пример: "Отрендери 1-250 во всех .blend из папки"
```

---

## 📝 ПРОМПТ (ENG)

```
Run batch: blender -b [SCENE] -P [SCRIPT] -- [ARGS]
Example: "Render 1-250 for all .blend in folder"
```

---

## 🔧 КОМАНДЫ

```bash
# Один кадр
blender -b scene.blend -E CYCLES -o //out/frame_#### -f 1
# Анимация
blender -b scene.blend -E CYCLES -o //out/anim_#### -s 1 -e 250 -a
# Скрипт
blender -b scene.blend -P setup_render.py -o //out/ -f 1
# Пакет по папке
for f in scenes/*.blend; do blender -b "$f" -P batch.py -- --out renders/; done
```

```python
# batch.py шаблон
import bpy, sys
argv = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=argv[0])
bpy.context.scene.render.filepath = argv[1]
bpy.ops.render.render(animation=True)
```

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 04](../setups/setup_04_headless_render.md), [Setup 05](../setups/setup_05_render_farm.md)
- **Воркфлоу:** [WF 08](../workflows/wf_08_batch_processing.md)
- **Следующий:** [P30: Optimization](./30_optimization.md)
