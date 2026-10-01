---
id: 22_particles
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: template
---
# P22: PARTICLE SYSTEMS

> Ziel: ---

**ID:** 22_particles | **Lang:** de | **Orig:** ru | **Category:** prompts | **Tags:** cache, children, emitter, hair, particles

## Verwendung
Dies ist die deutsche Version von '22_particles'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
22_particles / prompts / cache, children, emitter, hair, particles
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

# P22: PARTICLE SYSTEMS

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
