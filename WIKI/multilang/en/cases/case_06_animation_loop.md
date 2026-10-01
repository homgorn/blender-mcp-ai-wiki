---
id: case_06_animation_loop
lang: en
orig_lang: en
category: cases
type: case
difficulty: 2
translation: template
---
# CASE 06: ANIMATION LOOP

> Goal: ## 🌍 MULTILANG

**ID:** case_06_animation_loop | **Lang:** en | **Orig:** en | **Category:** cases | **Tags:** 

---

# CASE 06: ANIMATION LOOP

**ID:** CASE-06 | **Type:** Motion Design / Looping Animation | **Difficulty:** ⭐⭐ | **Time:** 1-3 hours

---

## 🎯 GOAL
Create seamless looping animation: abstract, mechanical, character, or environmental

---

## 📋 LOOP TYPES & PIPELINES

| Type | Frames | Key Technique | Use Case |
|------|--------|---------------|----------|
| **Perfect Loop** | 60-240 | Frame 1 = Frame N+1 | Instagram, UI, Web |
| **Ping-Pong** | 30-120 | Forward + Reverse | UI, Loading |
| **Procedural** | ∞ | Math (sin/cos/noise) | Shaders, Backgrounds |
| **Physics Loop** | 120-500 | Cache → Loop Point | Cloth, Fluid, Particles |
| **Character Cycle** | 24-48 | Walk/Run/Idle | Games, Cinematics |

---

## 🔧 MCP COMMANDS BY TYPE

### TYPE A: PERFECT GEOMETRIC LOOP (Abstract)
```bash
# Concept: Rotating/Morphing geometry, perfect frame match

# Geometry Nodes Loop
"GN: Grid 10x10 → Extrude by Noise(Frame) → Scale by Sin(Frame)
Frame 1 = Frame 241 (240 frames @ 30fps = 8 сек)
Noise Seed = Frame → Детерминированный лоб"

# Shader Loop (Material)
"Principled BSDF:
Color = HSV(Hue=Frame/240, Sat=0.8, Val=1.0)
Emission = Sin(Frame/30) * 5.0
Displacement = Noise(UV + Frame/60) * 0.1"
```

### TYPE B: MECHANICAL LOOP (Gears, Machines)
```bash
# Gear System
"Driver Setup:
Gear_A (Driver) → Rotation Z = Frame * 6° (60 RPM @ 30fps)
Gear_B (Driven) → Ratio -1:2 (Driver * -2)
Gear_C (Driven) → Ratio 1:3 (Driver * -3)

# Piston Animation
Crank (Driver) → Rotation Z = Frame * 12°
Connecting Rod → Copy Rotation + Limit Distance
Piston → Locked Track + Limit Location Z

# Loop: Frame 1 = Frame 361 (6 оборотов = 12 сек @ 30fps)"
```

### TYPE C: CHARACTER WALK CYCLE
```bash
# Rigify Rig Setup
"Meta-Rig → Generate Rig
Walk Cycle (24 frames @ 24fps = 1 сек):

Frame 1:  Contact R (Right heel, Left toe)
Frame 7:  Down    (Right foot flat, Left passing)
Frame 13: Contact L (Left heel, Right toe)
Frame 19: Down    (Left foot flat, Right passing)
Frame 25: = Frame 1 (Loop)

# Graph Editor: All curves Bezier, Cyclic Extrapolation
# NLA: Walk Action → Push Down → Repeat"
```

### TYPE D: PHYSICS LOOP (Cloth/Particles)
```bash
# Cloth Flag Loop
"Plane 2x1м, Subdivide 50x25
Cloth Physics: Vertex Group 'Pin' (левый край)
Wind: Force Field → Noise Texture(Frame) → Strength 5-10
Cache: 240 фреймов → Найти Loop Point (похожее состояние)
Trim: Start=45, End=285 (240 фреймов плавный лоб)"

# Particle Loop
"Emitter: Circle 1м, Particles 1000
Velocity: Normal 2м/с + Random 0.5
Force: Vortex (Z) + Noise(Frame)
Lifetime: 120 фреймов
Loop: Emitter Rate = Frame % 120 → Бесшовный поток"
```

### TYPE E: SHADER/COMPOSITING LOOP (Post)
```bash
# Compositor Loop (Background)
"Render Layers → Glare(Frame%60) → Hue Rotate(Frame/120)
Output: 60 фреймов = 2 сек @ 30fps → Perfect Loop

# Background Plate для UI
"Resolution: 1920x1080, 60 фреймов
Export: WebM VP9 (loop) + GIF fallback"
```

---

## 🔧 UNIVERSAL LOOP SETUP (MCP)

### FRAME RANGE & RENDER SETTINGS
```python
import bpy

def setup_perfect_loop(total_frames=240, fps=30):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.fps = fps
    scene.render.fps_base = 1
    
    # Cyclic extrapolation для всех fcurves
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                fcurve.extrapolation = 'CYCLIC'
    
    # NLA Tracks → Cyclic
    for track in obj.animation_data.nla_tracks:
        for strip in track.strips:
            strip.repeat = total_frames // int(strip.action_frame_end)
            strip.use_repeat = True
    
    print(f"Loop setup: {total_frames} frames @ {fps}fps = {total_frames/fps:.1f}s")

setup_perfect_loop(240, 30)
```

### RENDER OUTPUT FOR LOOP
```python
def setup_loop_output(format='FFMPEG', codec='H264', filepath="//renders/loop_"):
    scene = bpy.context.scene
    scene.render.filepath = filepath
    scene.render.image_settings.file_format = format
    
    if format == 'FFMPEG':
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = codec
        scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
        scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        scene.render.ffmpeg.gopsize = scene.frame_end  # Keyframe каждые N кадров
    
    # Для WebM (прозрачность)
    # scene.render.ffmpeg.format = 'WEBM'
    # scene.render.ffmpeg.codec = 'VP9'
```

### LOOP VALIDATION
```python
def validate_loop(obj_name, tolerance=0.001):
    """Проверить что Frame 1 == Frame N+1"""
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return False
    
    scene = bpy.context.scene
    start_frame = scene.frame_start
    end_frame = scene.frame_end
    
    # Сохранить текущий фрейм
    current = scene.frame_current
    
    scene.frame_set(start_frame)
    loc1, rot1, scale1 = obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()
    
    scene.frame_set(end_frame)
    loc2, rot2, scale2 = obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()
    
    scene.frame_set(current)
    
    diff_loc = (loc1 - loc2).length
    diff_rot = sum(abs(a - b) for a, b in zip(rot1, rot2))
    diff_scale = (scale1 - scale2).length
    
    is_loop = diff_loc < tolerance and diff_rot < tolerance and diff_scale < tolerance
    
    print(f"Loop validation for {obj_name}: {'✅ PASS' if is_loop else '❌ FAIL'}")
    print(f"  Loc diff: {diff_loc:.6f}, Rot diff: {diff_rot:.6f}, Scale diff: {diff_scale:.6f}")
    
    return is_loop

# Проверить все анимированные объекты
for obj in bpy.data.objects:
    if obj.animation_data:
        validate_loop(obj.name)
```

---

## 📊 LOOP SPECS BY PLATFORM

| Platform | Format | Duration | Resolution | Loop Type |
|----------|--------|----------|------------|-----------|
| **Instagram Reels** | MP4 H.264 | 3-15s | 1080x1920 | Perfect |
| **TikTok** | MP4 H.264 | 5-60s | 1080x1920 | Perfect |
| **Web (Hero)** | WebM VP9 | ∞ | 1920x1080 | Seamless |
| **UI Loader** | Lottie JSON | 1-3s | 200x200 | Ping-Pong |
| **Game Engine** | FBX/Alembic | 1-4s | Any | Cyclic |
| **LED Wall** | ProRes/EXR | 10-60s | 4K-8K | Perfect |

---

## 🔗 LINKS

- **Prompts:** P01, P07, P22, P24, P25, P26, P27, P28, P29, P30
- **Workflows:** [WF 04: Character Animation](../workflows/wf_04_character_animation.md), [WF 08: Batch](../workflows/wf_08_batch_processing.md)
- **Prompts Used:** P01, P07, P22-P30

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| `fcurve.extrapolation = 'CYCLIC'` | Автоматический лоб для всех кривых |
| NLA Repeat вместо копирования | Экономия памяти, легкость редактирования |
| Frame 1 = Frame N+1 (не N) | Правильный лоб при рендере |
| Gopsize = Frame Count | Один ключевой кадр на весь лоб = меньше артефактов |
| Validate Loop перед рендером | Экономит часы переработки |

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/cases/case_06_animation_loop.md` |
| Russian | `multilang/ru/cases/case_06_animation_loop.md` |