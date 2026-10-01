---
id: 06_retopology_workflow
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P06: RETOPOLOGY ВОРКФЛОУ

> 目标: 

**ID:** 06_retopology_workflow | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** **, game, game-ready, optimization, quads, retopo, retopology

## 使用方法
这是 '06_retopology_workflow' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
06_retopology_workflow / prompts / **, game, game-ready, optimization, quads, retopo, retopology
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: 06_retopology_workflow
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 3
---

# P06: RETOPOLOGY ВОРКФЛОУ

> Цель: ## 🌍 MULTILANG

**ID:** 06_retopology_workflow | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, game, game-ready, optimization, quads, retopo, retopology

---

# P06: RETOPOLOGY WORKFLOW

**ID:** P06 | **Cluster:** Geometry Basics | **Difficulty:** ⭐⭐⭐ | **Tags:** #retopology #retopo #game-ready #optimization #quads

---

## 🎯 GOAL
Create clean, animation-ready topology from high-poly source using manual and automated retopology

---

## 📝 PROMPT (RUS)

```
Выполни ретопологию "[HIGHPOLY_OBJECT]" → "[LOWPOLY_OBJECT]":
Метод: MANUAL (Snap to surface) / QUAD_REMESHER / INSTANT_MESHES
Target tris: [NUMBER]
Сохранить UV: YES/NO
Сохранить вертекс-группы: YES/NO
```

---

## 📝 PROMPT (ENG)

```
Retopologize "[HIGHPOLY_OBJECT]" → "[LOWPOLY_OBJECT]":
Method: MANUAL (Snap to surface) / QUAD_REMESHER / INSTANT_MESHES
Target tris: [NUMBER]
Preserve UV: YES/NO
Preserve vertex groups: YES/NO
```

---

## 🔧 MCP: `execute_blender_code`

### QUAD REMESHER (Авто, лучшее качество)
```python
import bpy

highpoly = bpy.data.objects.get("HighPoly_Sculpt")
if not highpoly:
    raise ValueError("Highpoly object not found")

# Дубликат для ретопологии
lowpoly = highpoly.copy()
lowpoly.data = highpoly.data.copy()
lowpoly.name = "LowPoly_Retopo"
bpy.context.collection.objects.link(lowpoly)

# Quad Remesher (требует аддон, встроен в Blender 3.5+)
bpy.context.view_layer.objects.active = lowpoly
bpy.ops.object.mode_set(mode='OBJECT')

# Встроенный Quadriflow (Blender 3.5+)
bpy.ops.object.quadriflow_remesh(
    quad_count=5000,           # Целевое кол-во квадов
    adaptivity=0.0,            # 0=равномерно, 1=адаптивно
    smoothness=1.0,            # Сглаживание
    seed=42                    # Для воспроизводимости
)

print(f"Retopo done: {len(lowpoly.data.polygons)} quads, {len(lowpoly.data.vertices)} verts")
```

### MANUAL RETOPO (Snap to Surface)
```python
import bpy
import bmesh

highpoly = bpy.data.objects.get("HighPoly")
lowpoly = bpy.data.objects.get("LowPoly_Base")

if not highpoly or not lowpoly:
    raise ValueError("Objects not found")

# Настроить Snap
bpy.context.scene.tool_settings.snap_elements = {'FACE'}
bpy.context.scene.tool_settings.use_snap = True
bpy.context.scene.tool_settings.use_snap_project = True
bpy.context.scene.tool_settings.snap_target = 'CLOSEST'

# В EDIT mode на lowpoly
bpy.context.view_layer.objects.active = lowpoly
bpy.ops.object.mode_set(mode='EDIT')

bm = bmesh.from_edit_mesh(lowpoly.data)
bm.verts.ensure_lookup_table()

# Переместить каждую вершину на поверхность highpoly
import bpy_extras.view3d_utils
import mathutils

for v in bm.verts:
    if v.select:  # Только выделенные
        world_co = lowpoly.matrix_world @ v.co
        # Raycast к highpoly
        result, location, normal, index = highpoly.ray_cast(
            highpoly.matrix_world.inverted() @ world_co,
            highpoly.matrix_world.inverted() @ (world_co + mathutils.Vector((0,0,-10)))
        )
        if result:
            v.co = lowpoly.matrix_world.inverted() @ location

bmesh.update_edit_mesh(lowpoly.data)
bpy.ops.object.mode_set(mode='OBJECT')
```

### INSTANT MESHES (Если установлен)
```bash
# Внешний инструмент: https://github.com/wjakob/instant-meshes
# CLI: instant-meshes -o output.obj input.obj -f 5000
# Потом импорт в Blender
```

---

## 📊 СРАВНЕНИЕ МЕТОДОВ

| Метод | Скорость | Качество | Контроль | Зависимости |
|-------|----------|----------|----------|-------------|
| **Quad Remesher** | ⚡⚡ | ⭐⭐⭐⭐ | Средний | Встроен (Blender 3.5+) |
| **Instant Meshes** | ⚡⚡⚡ | ⭐⭐⭐ | Высокий | Внешний бинарь |
| **Manual (Snap)** | ⚡ | ⭐⭐⭐⭐⭐ | Полный | Нет |
| **Quad Remesher (аддон)** | ⚡⚡ | ⭐⭐⭐⭐⭐ | Высокий | Платный аддон |

---

## 💡 ПОСЛЕ РЕТОПОЛОГИИ

```python
# 1. Проверить топологию
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.vert_connect_nonplanar()  # Найти не-плоские
bpy.ops.mesh.select_non_manifold()      # Non-manifold
bpy.ops.object.mode_set(mode='OBJECT')

# 2. Перенос UV (Data Transfer)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = highpoly
highpoly.select_set(True)
lowpoly.select_set(True)
bpy.ops.object.join_uvs()  # или Data Transfer modifier

# 3. Перенос Vertex Groups (Data Transfer)
dt = lowpoly.modifiers.new("DataTransfer", 'DATA_TRANSFER')
dt.object = highpoly
dt.use_vert_data = True
dt.data_types_verts = {'VGROUP_WEIGHTS'}
dt.vert_mapping = 'NEAREST_FACE_INTERPOLATED'
bpy.ops.object.modifier_apply(modifier="DataTransfer")

# 4. Bake Normal Map
# См. P05 (UV) + WF 03 (Texture Pipeline)
```

---

## ⚠️ ЧЕК-ЛИСТ ПЕРЕД ЭКСПОРТОМ

- [ ] Только квады (0 треугольников)
- [ ] Нет полюсов > 5 ребер
- [ ] Edge flow следует анатомии / форме
- [ ] UV развёрнуты без перекрытий
- [ ] Нормали направлены наружу
- [ ] Вертекс-группы перенесены
- [ ] Normal Map запечён (High → Low)

---

## 🔗 LINKS

- **Cases:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Workflows:** [WF 07: Game Asset Pipeline](../workflows/wf_07_game_asset_pipeline.md)
- **Prompts:** [P04 BMesh](./04_mesh_editing_bmesh.md), [P05 UV](./05_uv_unwrapping.md)
- **Next:** [P07: Instancing & Arrays](./07_instancing_arrays.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/06_retopology_workflow.md` |
| Russian | `multilang/ru/prompts/06_retopology_workflow.md` |