---
lang: en
tags: [animation, reference]
---
# ANIMATION WORKFLOWS

## Overview
Rigging, animation, and rendering pipelines for Blender.

---

## Rigging

### Rigify (Humanoid)
```
1. Import character mesh (T-pose or A-pose)
2. Add Armature → Human (Meta-Rig)
3. Scale/position meta-rig to match mesh
4. Generate Rig (Rigify buttons → Generate)
5. Parent: Mesh → Armature (Automatic Weights)
6. Weight paint cleanup if needed
```

### Auto-Rig Pro / Rigify Pro (Advanced)
- Better facial rigs
- IK/FK switching
- Custom bone shapes

### Simple Rig (Props/Mechanical)
```
1. Add bones for each moving part
2. Parent bones to mesh (Bone Heat / Envelope)
3. Add constraints: Copy Location/Rotation/Scale
4. Add drivers for mechanical relationships
```

---

## Keyframe Animation

### Basic Workflow
```
1. Set frame range: Scene → Frame Start/End
2. Pose at frame 1 → Insert keyframes (I → Location/Rotation/Scale)
3. Move to frame 50 → Pose → Insert keyframes
4. Graph Editor: Clean curves, set interpolation
5. Dope Sheet: Adjust timing
```

### Interpolation Types
| Type | Use Case |
|------|----------|
| Bezier | Smooth, natural motion (default) |
| Linear | Mechanical, constant speed |
| Constant | Hold pose (stepped) |
| Elastic/Bounce | Cartoon effects |

### Graph Editor Tips
```
- T: Interpolation menu
- V: Handle type (Auto, Vector, Aligned, Free)
- Shift+E: Auto-clamp handles
- Period (.) on numpad: Frame selected
- Ctrl+Click: Add keyframe at cursor
```

---

## NLA (Non-Linear Animation)

### Action Strips
```
1. Create actions: Walk, Run, Idle, Attack
2. NLA Editor → Push Down (stash) each action
3. Blend strips: Overlap for transitions
4. Extrapolation: Hold / Nothing / Repeat
5. Layer strips: Additive layers for details
```

### Workflow
```
Base Layer: Walk cycle (repeat)
Layer 1: Arm swing variation (additive)
Layer 2: Head turn (override)
Layer 3: Facial expression (override)
```

---

## Motion Capture / Retargeting

### Import BVH/FBX
```
1. File → Import → BVH / FBX
2. Creates armature with animation
3. Retarget to your rig:
   - Add constraints: Copy Rotation (target mocap bone)
   - Or use Retargeting addon (Rigify has built-in)
```

### Retargeting Workflow (Rigify)
```
1. Import mocap → creates "Mocap" armature
2. Select your Rigify rig
3. Bone Constraints → Copy Rotation → Target: Mocap bone
4. Bake Action (Pose → Animation → Bake Action)
5. Clean up: Remove constraints, simplify keys
```

---

## Procedural Animation

### Drivers
```python
# Driver: Gear rotation based on another gear
# Driver expression: -var * (teeth_a / teeth_b)

# Setup via Python
driver = gear_b.driver_add('rotation_euler', 2).driver
driver.type = 'SCRIPTED'
var = driver.variables.new()
var.name = 'gear_a_rot'
var.targets[0].id = gear_a
var.targets[0].data_path = 'rotation_euler[2]'
driver.expression = '-gear_a_rot * 0.5'  # 2:1 ratio
```

### Geometry Nodes Animation
```
1. Geometry Nodes → Object Info → Get animated object
2. Use frame number: #frame
3. Math nodes for procedural motion
4. Instance on points with animation offset
```

### Simulation (Physics)
```
- Rigid Body: Falling objects, destruction
- Cloth: Flags, capes, clothing
- Fluid: Water, smoke, fire
- Particles: Magic effects, debris, crowds
- Soft Body: Jelly, flesh deformation
```

---

## Camera Animation

### Dolly/Crane
```
1. Add Curve (Bezier) for path
2. Camera → Follow Path constraint
3. Target Empty → Track To constraint
4. Animate Curve Evaluation (0→1 over frames)
```

### Handheld Shake
```
1. Camera → Add Noise modifier (Graph Editor)
2. Scale: 0.01-0.05, Strength: 0.1-0.5
3. Or: Python script for procedural shake
```

### DOF (Depth of Field)
```
1. Camera → Depth of Field → Focus Object: Target Empty
2. F-Stop: 1.4-2.8 (shallow) / 8-16 (deep)
3. Animate Focus Distance for rack focus
```

---

## Rendering Animation

### Settings
```python
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 250
scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Output
scene.render.filepath = "//renders/anim_####.png"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 15
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.5
scene.render.motion_blur_samples = 16
```

### Motion Blur
```
Cycles:
- Render → Motion Blur → Position: Center/Start/End
- Shutter: 0.5 (180° shutter)
- Samples: 16+ for quality

EEVEE:
- Render → Motion Blur → Enable
- Steps: 8-16
```

### Frame Sequencing
```bash
# Render frames
blender -b scene.blend -E CYCLES -o //renders/frame_#### -f 1..250

# Encode to video (ffmpeg)
ffmpeg -framerate 24 -i //renders/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Or in Blender: Video Sequencer → Add → Image Sequence → Export FFmpeg
```

---

## Alembic Cache (Pipeline)

### Export
```python
bpy.ops.wm.alembic_export(
    filepath="animation.abc",
    start=1, end=250,
    selected=True,
    flatten=True,
    subsamples=4
)
```

### Import
```python
bpy.ops.wm.alembic_import(
    filepath="animation.abc",
    as_background_job=False
)
```

---

## Crowd Animation

### Particle Instancing
```
1. Emitter plane → Particle System (Hair)
2. Render → Object → Collection (pick character collection)
3. Advanced → Rotation: Velocity/Random
4. Scale: Random 0.9-1.1
5. Use Collection instances for variation
```

### Geometry Nodes Crowd
```
1. Grid of points
2. Random select character from collection
3. Instance with random animation offset
4. Look-at target for direction
```

---

## Lip Sync

### Papagayo / Rhubarb
```
1. Audio → Rhubarb Lip Sync → .json/.tsv
2. Import to Blender (Papagayo addon or custom script)
3. Map phonemes to shape keys
4. Bake to shape key animation
```

### Shape Keys Setup
```
1. Create basis + phoneme shapes (A, E, I, O, U, M, etc.)
2. Driver each shape key from phoneme track
3. Smooth with Graph Editor
```

---

## Export for Game Engines

### Unity/Unreal (FBX)
```python
bpy.ops.export_scene.fbx(
    filepath="character.fbx",
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL',
    bake_space_transform=True,
    object_types={'ARMATURE', 'MESH'},
    use_armature_deform_only=True,
    add_leaf_bones=False,
    primary_bone_axis='Y_FORWARD',
    secondary_bone_axis='X_UP'
)
```

### Web (GLTF)
```python
bpy.ops.export_scene.gltf(
    filepath="character.glb",
    export_format='GLB',
    use_selection=True,
    export_animations=True,
    export_frame_range=True,
    export_frame_step=1,
    export_force_sampling=True,
    export_skins=True,
    export_morph=True
)
```

---

## Performance Tips

### Animation Optimization
```
- Reduce keyframes: Simplify curves (Graph Editor → Key → Simplify)
- Use actions for reusable cycles
- Bake physics to keyframes for render farm
- Proxy/low-res meshes for viewport animation
- Hide heavy collections while animating
```

### Render Farm
```
1. Split frames across machines
2. Use Flamenco (Blender's render farm) or Deadline
3. Shared storage for assets
4. Alembic caches for sim data
5. Collect → Encode → Review
```

---

## AI-Assisted Animation (via MCP)

### Prompt Examples
```
"Animate camera: 360° orbit around object over 120 frames, ease in/out"
"Create walk cycle for rigged character: 24 frames, loop seamlessly"
"Add noise modifier to camera rotation for handheld feel"
"Set up DOF rack focus from object A to B over 60 frames"
"Create particle explosion at frame 50, 200 particles, 2 second life"
"Bake rigid body simulation for 100 falling boxes to keyframes"
```