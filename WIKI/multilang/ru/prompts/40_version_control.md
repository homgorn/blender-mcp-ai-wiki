---
id: 40_version_control
lang: ru
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P40: VERSION CONTROL & RENDER JOBS

> Цель: ---

**ID:** 40_version_control | **Lang:** ru | **Orig:** ru | **Category:** prompts | **Tags:** backup, ci, flamenco, git, lfs, versioning

## Как пользоваться
Это русская версия '40_version_control'. Кодовые блоки языконезависимы. Выполняйте шаги по порядку, проверяйте разделом Проверка.

## MCP-промпт (копипаст)
```
40_version_control / prompts / backup, ci, flamenco, git, lfs, versioning
```

> Замечание: код/пути оставлены на английском для совместимости Blender/Python.

---

# P40: VERSION CONTROL & RENDER JOBS

**ID:** P40 | **Кластер:** Pipeline | **Сложность:** ⭐⭐ | **Теги:** #git #lfs #versioning #flamenco #ci #backup

---

## 🎯 ЦЕЛЬ
Версионирование .blend (Git LFS + lock) и отправка рендер-джобов (Flamenco/CLI)

---

## 📝 ПРОМПТ (РУС)

```
Настрой версионирование: LFS track [маски], lock [мейн-сцены].
Отправь джобу: frames [A-B], samples [N], output [путь].
```

---

## 📝 ПРОМПТ (ENG)

```
Setup versioning: LFS track [masks], lock [main scenes].
Submit job: frames [A-B], samples [N], output [path].
```

---

## 🔧 КОМАНДЫ

```bash
# .gitattributes
# *.blend filter=lfs diff=lfs merge=lfs -text
# *.exr filter=lfs diff=lfs merge=lfs -text
# *.fbx filter=lfs diff=lfs merge=lfs -text
# *.png filter=lfs diff=lfs merge=lfs -text
```

```python
# save versioned copy
import bpy, datetime
v = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bpy.ops.wm.save_as_mainfile(filepath=f"//versions/scene_v{v}.blend")
```

```bash
# CLI render job
# blender -b scenes/main.blend -E CYCLES -o //renders/anim_#### -s 1 -e 250 -a
```

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 04](../setups/setup_04_headless_render.md), [Setup 05](../setups/setup_05_render_farm.md), [Setup 07](../setups/setup_07_ci_cd.md)
- **Воркфлоу:** [WF 08](../workflows/wf_08_batch_processing.md)
