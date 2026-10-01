---
lang: ru
---
# P21: PHYSICS SIMULATION

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
