#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate full prompts P21-P30 (physics/GN/MCP/optimization)."""
import os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
W = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent) / "prompts"
F = {}

F["21_physics_simulation.md"] = """# P21: PHYSICS SIMULATION

**ID:** P21 | **Кластер:** Simulation | **Сложность:** ⭐⭐⭐ | **Теги:** #physics #rigid-body #cloth #fluid #collision #cache

---

## 🎯 ЦЕЛЬ
Симуляции Rigid Body / Cloth / Fluid: настройка, бейк кэша, экспорт Alembic

---

## 📝 ПРОМПТ (РУС)

```
Настрой симуляцию [TYPE: RIGID/CLOTH/FLUID] для "[OBJECT]":
Параметры: [mass/friction/damping/resolution]
Кэш: DISK CACHE [start-end], запеки
Экспорт: Alembic при нужде
```

---

## 📝 ПРОМПТ (ENG)

```
Setup [TYPE: RIGID/CLOTH/FLUID] simulation for "[OBJECT]":
Params: [mass/friction/damping/resolution]
Cache: DISK CACHE [start-end], bake it
Export: Alembic if needed
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def setup_rigid_body(obj_name, body_type='ACTIVE', mass=1.0, friction=0.5, restitution=0.2):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError(f"Object {obj_name} not found")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add(type=body_type)
    rb = obj.rigid_body
    rb.mass = mass
    rb.friction = friction
    rb.restitution = restitution
    rb.collision_shape = 'CONVEX_HULL'
    return {"rigid_body": obj_name, "type": body_type}

def setup_cloth(obj_name, pin_group=None, quality=5):
    obj = bpy.data.objects.get(obj_name)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Cloth", 'CLOTH')
    s = mod.settings
    s.quality = quality
    s.mass = 0.3
    s.air_damping = 1.0
    if pin_group:
        s.vertex_group_mass = pin_group
    # Collision
    mod.collision_settings.use_collision = True
    mod.collision_settings.thickness_outer = 0.01
    return {"cloth": obj_name}

def bake_cache(frame_start=1, frame_end=250, cache_type='ALL'):
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    bpy.ops.ptcache.bake_all(bake=True)
    return {"baked": f"{frame_start}-{frame_end}"}

def export_alembic(objects, filepath, start=1, end=250):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        bpy.data.objects.get(o).select_set(True)
    bpy.ops.wm.alembic_export(
        filepath=filepath, selected=True,
        start=start, end=end, flatten=True, subsamples=4)
    return {"alembic": filepath}

# setup_rigid_body("Crate", mass=2.0)
# setup_cloth("Flag", pin_group="Pin", quality=6)
# bake_cache(1, 120)
```

---

## 📊 ТИПЫ СИМУЛЯЦИЙ
| Тип | Модификатор | Кэш | Экспорт |
|-----|-------------|-----|---------|
| Rigid Body | RigidBody world | Point Cache | Alembic |
| Cloth | CLOTH | Point Cache | Alembic / MDD |
| Fluid (Mantaflow) | FLUID domain/flow | OpenVDB | VDB sequence |
| Particles | PARTICLE_SYSTEM | Point Cache | Alembic |
| Soft Body | SOFT_BODY | Point Cache | Alembic |

---

## ⚠️ ОШИБКИ
| Ошибка | Решение |
|--------|---------|
| Объекты проваливаются | Увеличь Substeps (Scene → Rigid Body World → Steps), проверь Scale applied |
| Cloth взрывается | Уменьши mass, увеличь quality, проверь self-collision distance |
| Кэш не бейкится | Cache Type = All, путь записи доступен, Disk Cache включён |

---

## 🔗 СВЯЗИ
- **Воркфлоу:** [WF 05](../workflows/wf_05_procedural_assets.md)
- **Следующий:** [P22: Particles](./22_particles.md)
"""

F["22_particles.md"] = """# P22: PARTICLE SYSTEMS

**ID:** P22 | **Кластер:** Simulation | **Сложность:** ⭐⭐ | **Теги:** #particles #hair #emitter #children #cache

---

## 🎯 ЦЕЛЬ
Системы частиц: emitter/hair, children, поля, кэш, рендер как объекты

---

## 📝 ПРОМПТ (РУС)

```
Создай particle system на "[EMITTER]": тип [EMITTER/HAIR],
count [N], lifetime [F], velocity [V], render as [OBJECT/COLLECTION]
```

---

## 📝 ПРОМПТ (ENG)

```
Create particle system on "[EMITTER]": type [EMITTER/HAIR],
count [N], lifetime [F], velocity [V], render as [OBJECT/COLLECTION]
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def create_emitter(obj_name, count=1000, lifetime=50, vel=2.0, render_obj=None):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError("Emitter not found")
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Particles", 'PARTICLE_SYSTEM')
    psys = mod.particle_system
    s = psys.settings
    s.type = 'EMITTER'
    s.count = count
    s.lifetime = lifetime
    s.frame_start = 1
    s.frame_end = 10
    s.emit_from = 'FACE'
    s.normal_factor = vel
    s.render_type = 'OBJECT' if render_obj else 'HALO'
    if render_obj:
        s.instance_object = bpy.data.objects.get(render_obj)
    return {"particles": count, "emitter": obj_name}

def create_hair(obj_name, count=500, length=0.3, children=10):
    obj = bpy.data.objects.get(obj_name)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Hair", 'PARTICLE_SYSTEM')
    s = mod.particle_system.settings
    s.type = 'HAIR'
    s.count = count
    s.hair_length = length
    s.child_nbr = children
    s.child_type = 'INTERPOLATED'
    return {"hair": count}

# create_emitter("Emitter", count=2000, lifetime=60, vel=3.0, render_obj="Debris")
# create_hair("Head", count=800, length=0.25)
```

---

## 🔗 СВЯЗИ
- **Промпты:** [P21 Physics](./21_physics_simulation.md)
- **Следующий:** [P23: Geometry Nodes Basics](./23_geometry_nodes_basics.md)
"""

F["23_geometry_nodes_basics.md"] = """# P23: GEOMETRY NODES BASICS

**ID:** P23 | **Кластер:** Geometry Nodes | **Сложность:** ⭐⭐ | **Теги:** #geometry-nodes #procedural #attributes #instances

---

## 🎯 ЦЕЛЬ
Базовый GN-сетап: Group Input/Output, distribute points, instance on points, realize

---

## 📝 ПРОМПТ (РУС)

```
Создай Geometry Nodes "[GROUP]" на "[OBJECT]":
Входы: [Count, Seed, Scale]
Логика: Distribute Points → Instance Collection → Random Transform
```

---

## 📝 ПРОМПТ (ENG)

```
Create Geometry Nodes "[GROUP]" on "[OBJECT]":
Inputs: [Count, Seed, Scale]
Logic: Distribute Points → Instance Collection → Random Transform
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def create_gn_scatter(obj_name, group_name="GN_Scatter", collection_name=None):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError("Object not found")
    ng = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    nodes, links = ng.nodes, ng.links
    nodes.clear()
    inp = nodes.new('NodeGroupInput')
    out = nodes.new('NodeGroupOutput')
    inp.location = (-400, 0); out.location = (400, 0)
    ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
    ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    dist = nodes.new('GeometryNodeDistributePointsOnFaces')
    dist.location = (-100, 0)
    dist.distribute_method = 'POISSON'
    inst = nodes.new('GeometryNodeInstanceOnPoints')
    inst.location = (100, 0)
    real = nodes.new('GeometryNodeRealizeInstances')
    real.location = (300, 0)
    links.new(inp.outputs[0], dist.inputs['Density'])
    links.new(dist.outputs['Points'], inst.inputs['Points'])
    links.new(inst.outputs['Instances'], real.inputs['Geometry'])
    links.new(real.outputs['Geometry'], out.inputs['Geometry'])
    mod = obj.modifiers.new("GN", 'NODES')
    mod.node_group = ng
    return {"group": group_name, "object": obj_name}

# create_gn_scatter("Ground", "GN_Trees")
```

---

## 📊 КЛЮЧЕВЫЕ НОДЫ
| Нода | Назначение |
|------|------------|
| Distribute Points on Faces | Точки по поверхности |
| Instance on Points | Инстансы коллекции |
| Realize Instances | Конвертация в геометрию |
| Random Value | Случайные scale/rotation |
| Store Named Attribute | Кастомные атрибуты |

---

## 🔗 СВЯЗИ
- **Промпты:** [P07 Instancing](./07_instancing_arrays.md), [P24 Scatter](./24_gn_scatter.md)
- **Следующий:** [P24: GN Scatter](./24_gn_scatter.md)
"""

F["24_gn_scatter.md"] = """# P24: GN SCATTER & DISTRIBUTION

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
"""

F["25_procedural_building.md"] = """# P25: PROCEDURAL BUILDING GENERATOR

**ID:** P25 | **Кластер:** Geometry Nodes | **Сложность:** ⭐⭐⭐ | **Теги:** #procedural #architecture #building #array #facade

---

## 🎯 ЦЕЛЬ
Параметрическое здание: этажи, фасад с окнами, крыша, LOD

---

## 📝 ПРОМПТ (РУС)

```
Сгенерируй здание "[NAME]": W×D×H [w,d,h], этажей [N],
оконная сетка [cols×rows], стиль [modern/classical], крыша [flat/pitched]
```

---

## 📝 ПРОМПТ (ENG)

```
Generate building "[NAME]": W×D×H [w,d,h], floors [N],
window grid [cols×rows], style [modern/classical], roof [flat/pitched]
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def procedural_building(name, w=10, d=10, h=30, floors=10, win_cols=5, win_rows=8):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    import bmesh
    bm = bmesh.new()
    # Корпус
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w / 2
        v.co.y *= d / 2
        v.co.z *= h / 2
        v.co.z += h / 2  # base at z=0
    bm.to_mesh(mesh)
    bm.free()
    # Этажи через Array
    arr = obj.modifiers.new("Floors", 'ARRAY')
    arr.count = 1  # корпус уже полный; окна отдельно
    # Окна: отдельные плоскости через массив
    bpy.ops.mesh.primitive_plane_add(size=1)
    win = bpy.context.active_object
    win.name = f"{name}_Windows"
    win.scale = (1.2, 0.05, 1.5)
    ax = win.modifiers.new("WinX", 'ARRAY')
    ax.count = win_cols
    ax.relative_offset_displace = (2.0, 0, 0)
    az = win.modifiers.new("WinZ", 'ARRAY')
    az.count = win_rows
    az.relative_offset_displace = (0, 0, 2.2)
    return {"building": name, "windows": win.name}

# procedural_building("Tower_A", w=12, d=12, h=45, floors=12, win_cols=6, win_rows=10)
```

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 05](../cases/case_05_procedural_city.md)
- **Воркфлоу:** [WF 05](../workflows/wf_05_procedural_assets.md)
- **Следующий:** [P26: MCP Basics](./26_mcp_basics.md)
"""

F["26_mcp_basics.md"] = """# P26: MCP BASICS (BLENDER-MCP COMMANDS)

**ID:** P26 | **Кластер:** MCP Integration | **Сложность:** ⭐ | **Теги:** #mcp #blender-mcp #tools #commands #setup

---

## 🎯 ЦЕЛЬ
Базовые MCP-команды: scene info, create/modify/delete, screenshot, code execution

---

## 📝 ПРОМПТ (РУС)

```
Через MCP: [действие]
Примеры: "Покажи сцену", "Создай сферу", "Скриншот viewport"
```

---

## 📝 ПРОМПТ (ENG)

```
Via MCP: [action]
Examples: "Show scene", "Create sphere", "Viewport screenshot"
```

---

## 🔧 MCP TOOLS

```json
// 1. Scene info
{"type": "get_scene_info", "params": {}}
// 2. Create
{"type": "create_object", "params": {"entity_type": "SPHERE", "name": "Ball", "location": [0,0,2]}}
// 3. Modify
{"type": "modify_object", "params": {"name": "Ball", "scale": [2,2,2]}}
// 4. Screenshot
{"type": "get_viewport_screenshot", "params": {"max_size": 800}}
// 5. Code
{"type": "execute_code", "params": {"code": "import bpy\\nbpy.ops.mesh.primitive_cube_add()"}}
```

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 01](../setups/setup_01_blender_mcp_basic.md)
- **Следующий:** [P27: Poly Haven Pipeline](./27_polyhaven_pipeline.md)
"""

F["27_polyhaven_pipeline.md"] = """# P27: POLY HAVEN ASSET PIPELINE

**ID:** P27 | **Кластер:** MCP Integration | **Сложность:** ⭐ | **Теги:** #polyhaven #assets #hdri #textures #models #mcp

---

## 🎯 ЦЕЛЬ
Поиск → скачивание → применение Poly Haven ассетов через MCP

---

## 📝 ПРОМПТ (РУС)

```
Найди на Poly Haven [тип: models/hdris/textures] "[запрос]",
скачай [ID] [resolution] и [примени/поставь world]
```

---

## 📝 ПРОМПТ (ENG)

```
Find on Poly Haven [type] "[query]", download [ID] [resolution] and [apply/set world]
```

---

## 🔧 MCP TOOLS

```json
// Поиск
{"type": "search_polyhaven_assets", "params": {"asset_type": "hdris", "categories": "studio"}}
// Скачивание HDRI
{"type": "download_polyhaven_asset", "params": {"asset_id": "studio_small_01", "asset_type": "hdris", "resolution": "2k"}}
// Скачивание текстуры + применение
{"type": "download_polyhaven_asset", "params": {"asset_id": "brick_wall_01", "asset_type": "textures", "resolution": "2k"}}
{"type": "set_texture", "params": {"object_name": "Wall", "texture_id": "brick_wall_01"}}
```

---

## 🔗 СВЯЗИ
- **Промпты:** [P13 Lighting](./13_lighting_hdri.md)
- **Следующий:** [P28: Custom MCP Tools](./28_custom_mcp_tools.md)
"""

F["28_custom_mcp_tools.md"] = """# P28: CUSTOM MCP TOOLS DEVELOPMENT

**ID:** P28 | **Кластер:** MCP Integration | **Сложность:** ⭐⭐⭐ | **Теги:** #mcp #custom-tools #python #fastmcp #addon

---

## 🎯 ЦЕЛЬ
Свои MCP-инструменты: серверная сторона (FastMCP) + Blender addon handler

---

## 📝 ПРОМПТ (РУС)

```
Создай MCP tool "[NAME]": параметры {...}, выполняет [действие bpy],
возвращает {...}. Зарегистрируй в сервере и аддоне.
```

---

## 📝 ПРОМПТ (ENG)

```
Create MCP tool "[NAME]": params {...}, runs [bpy action], returns {...}. Register in server and addon.
```

---

## 🔧 ШАБЛОН

```python
# Server (src/blender_mcp/tools/custom.py)
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Custom")

@mcp.tool()
async def my_tool(param: str) -> str:
    '''Description for LLM'''
    blender = get_blender_connection()
    return blender.send_command("my_command", {"param": param})

# Addon (addon.py) — в execute_command handlers:
# def my_command_handler(self, param): ...
```

```python
# GenesisCore style (встроенный):
# src/tools/my_tools.py
from .common import ToolsPackageBase
class MyTools(ToolsPackageBase):
    def my_tool(param: str) -> dict:
        '''Description for LLM'''
        import bpy
        return {"result": "success"}
# + import в src/tools/__init__.py
```

---

## 🔗 СВЯЗИ
- **Сетяпы:** [Setup 06](../setups/setup_06_custom_mcp_tools.md)
- **Следующий:** [P29: Batch & CLI](./29_batch_cli.md)
"""

F["29_batch_cli.md"] = """# P29: BATCH PROCESSING & CLI

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
"""

F["30_optimization.md"] = """# P30: OPTIMIZATION (SCENE & RENDER)

**ID:** P30 | **Кластер:** Advanced | **Сложность:** ⭐⭐ | **Теги:** #optimization #decimate #lod #instances #samples #denoise

---

## 🎯 ЦЕЛЬ
Оптимизация сцены и рендера: полигоны, текстуры, сэмплы, инстансинг

---

## 📝 ПРОМПТ (РУС)

```
Оптимизируй сцену: decimate [ratio], LOD [уровни], текстуры [res],
сэмплы [N] + denoise. Цель: [FPS/VRAM/время кадра]
```

---

## 📝 ПРОМПТ (ENG)

```
Optimize scene: decimate [ratio], LOD [levels], textures [res],
samples [N] + denoise. Target: [FPS/VRAM/frame time]
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

def optimize_scene(target_tris=500000, tex_res=2048, samples=128):
    # 1. Decimate heavy meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            tris = sum(len(p.vertices)-2 for p in obj.data.polygons)
            if tris > 50000:
                mod = obj.modifiers.new("Decimate_Opt", 'DECIMATE')
                mod.ratio = max(0.1, target_tris / max(tris, 1) / len(bpy.data.objects))
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=mod.name)
    # 2. Render settings
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.01
    return {"optimized": True, "samples": samples}

# optimize_scene()
```

---

## 📊 ЧЕК-ЛИСТ
- [ ] Применены scale, удалены doubles
- [ ] LOD0/1/2 для тяжёлых объектов
- [ ] Текстуры ≤2k для фона, 4k только hero
- [ ] Adaptive sampling + denoise
- [ ] Instancing вместо дубликатов

---

## 🔗 СВЯЗИ
- **Кейсы:** [Case 02](../cases/case_02_game_props.md)
- **Воркфлоу:** [WF 07](../workflows/wf_07_game_asset_pipeline.md)
"""

for name, content in F.items():
    (W / name).write_text(content, encoding="utf-8")
print(f"OK P21-P30: {len(F)} files")
