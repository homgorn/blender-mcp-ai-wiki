# PROMPTING GUIDE - EFFECTIVE AI COMMANDS FOR BLENDER

## Core Principles

### 1. Be Specific About Geometry
```
❌ "Make a house"
✅ "Create a low-poly house: 6x8m base, 4m walls, gabled roof 3m high, 
     1x2m door centered front, two 1x1m windows on each side"
```

### 2. Reference Blender Concepts
```
✅ "Add a Subdivision Surface modifier (levels=2) to the cube"
✅ "Create a Principled BSDF material: Base Color #8B4513, Roughness 0.8"
✅ "Set object origin to geometry center (Right-click → Set Origin → Origin to Geometry)"
```

### 3. Break Complex Tasks Into Steps
```
Step 1: "Create the base geometry for a medieval tower"
Step 2: "Add window openings using boolean difference with cylinders"
Step 3: "Apply stone material with moss in crevices"
Step 4: "Add crenellations on top using array modifier"
Step 5: "Set up 3-point lighting for dramatic rendering"
```

---

## Prompt Templates by Task

### Object Creation
```
"Create a [PRIMITIVE] named [NAME] at location [X,Y,Z] with scale [X,Y,Z]
 rotation [X,Y,Z] (radians). 
 Primitives: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT"

Example:
"Create a CYLINDER named 'Column' at (0,0,0) scale (0.3,0.3,5) rotation (0,0,0)"
```

### Material Assignment
```
"Create a Principled BSDF material named [NAME] with:
 Base Color: [R,G,B] or hex #RRGGBB
 Roughness: [0-1]
 Metallic: [0-1]
 [Optional: Transmission, IOR, Clearcoat, Emission]
 Apply to object [OBJECT_NAME]"

Example:
"Create material 'Gold' with Base Color #FFD700, Roughness 0.1, Metallic 1.0, Apply to 'Ring'"
```

### Lighting Setups
```
"Create [LIGHT_TYPE] light named [NAME] at [LOCATION] with:
 Energy: [WATTS]
 Color: [R,G,B] or temperature [K]
 [For AREA: size, spread]
 [For SUN: angle]"

Common setups:
- "3-point studio lighting: Key (1000W, 5600K, 45°), Fill (300W, 6500K, -30°), Rim (500W, 5600K, 180°)"
- "HDRI lighting: Search Poly Haven for 'studio' HDRI, 2k resolution, set as world"
- "Volumetric fog: Add cube domain, Principled Volume density 0.1, Sun light through"
```

### Camera Setup
```
"Add CAMERA named [NAME] at [LOCATION] rotation [EULER]
 Set as active camera: bpy.context.scene.camera = bpy.data.objects['NAME']
 [Optional: Lens 50mm, Sensor 36mm, DOF focus on object]"
```

### Poly Haven Assets
```
"Search Poly Haven for [ASSET_TYPE: models/hdris/textures] with 
 [categories: ['category1', 'category2']] [tags: ['tag1']]
 Download [ASSET_ID] at [RESOLUTION: 1k/2k/4k/8k] 
 [For textures: apply to object [NAME]]"

Examples:
"Search Poly Haven models categories ['furniture', 'seating'] download 'ArmChair_01' at 2k"
"Search Poly Haven hdris categories ['indoor'] download 'abandoned_bakery' at 2k set as world"
"Search Poly Haven textures categories ['metal'] download 'RustedIron' at 2k apply to 'Pipe'"
```

### Poly Pizza (Low-Poly)
```
"Search Poly Pizza for [QUERY] category [CATEGORY_NAME] licence [CC0/CC-BY] 
 animated [true/false] limit [N]
 Download [MODEL_ID] normalize_size true target_size [METERS]"

Categories: Food & Drink, Clutter, Weapons, Transport, Furniture & Decor, 
Objects, Nature, Animals, Buildings, People & Characters, Scenes & Levels, Other
```

### Sketchfab (High-Quality)
```
"Search Sketchfab for [QUERY] categories [CATEGORY] count [N] downloadable true
 Get preview for [UID]
 Download [UID] target_size [METERS]"
```

### AI 3D Generation (Hyper3D/Hunyuan3D)
```
"Generate 3D model of [DESCRIPTION] using Hyper3D Rodin
 [or Hunyuan3D]
 Poll status until complete
 Import result"
```

### Scene Building
```
"Create a [SCENE_TYPE] scene:
- [LIST OF OBJECTS WITH SPECS]
- Lighting: [SETUP]
- Camera: [POSITION/TYPE]
- Render settings: Cycles/EEVEE, samples, resolution"
```

---

## Advanced Prompting Patterns

### Iterative Refinement
```
1. "Create a basic chair shape with primitives"
2. "Add subdivision surface and bevel to smooth edges"
3. "Create fabric material for seat, wood for legs"
4. "Add stitching detail using geometry nodes or displacement"
5. "Set up turntable animation 360° over 120 frames"
```

### Conditional Logic
```
"If the object 'Wall' exists, add a window opening at height 1.2m.
 Otherwise, create a wall first then add window."
```

### Batch Operations
```
"For each selected object: 
 1. Apply scale (Ctrl+A → Scale)
 2. Add bevel modifier (width=0.02, segments=3)
 3. Shade smooth
 4. Create unique material with random hue"
```

### Code Execution (When Tools Aren't Enough)
```
"Execute this Blender Python code:
```
import bpy
for obj in bpy.context.selected_objects:
    obj.modifiers.new('Bevel', 'BEVEL')
    obj.modifiers['Bevel'].width = 0.02
    obj.modifiers['Bevel'].segments = 3
    bpy.ops.object.shade_smooth()
```"
```

---

## Provider-Specific Tips

### OpenRouter (GenesisCore)
- **Best for coding:** `deepseek/deepseek-chat`, `qwen/qwen-2.5-coder-32b`
- **Best for reasoning:** `anthropic/claude-3.5-sonnet`
- **Cheapest:** `meta-llama/llama-3.1-8b-instruct` (simple tasks)
- Always specify model in GenesisCore settings

### blender-mcp (Any Client)
- Works with any MCP client (Claude, Cursor, Codex, OpenCode)
- Tools are self-documenting - LLM knows parameters
- Use `execute_blender_code` for custom operations

---

## Common Patterns Cheat Sheet

| Task | Prompt Pattern |
|------|----------------|
| **Primitive** | "Create [TYPE] named [NAME] at [LOC] scale [SCALE]" |
| **Material** | "Create Principled BSDF [NAME]: color [RGB], roughness [0-1], metallic [0-1] apply to [OBJ]" |
| **Modifier** | "Add [MODIFIER_TYPE] to [OBJ] with [PARAMS]" |
| **Bool** | "Boolean [UNION/DIFFERENCE/INTERSECT] [OBJ_A] with [OBJ_B]" |
| **Array** | "Add Array modifier to [OBJ]: count [N], offset [X,Y,Z]" |
| **Curve** | "Create Bezier curve through points [LIST], bevel depth [RADIUS]" |
| **Particles** | "Add Particle System to [OBJ]: type HAIR, count [N], length [L]" |
| **Rigid Body** | "Add Rigid Body to [OBJ]: type ACTIVE/PASSIVE, mass [KG]" |
| **Animation** | "Animate [OBJ] location from [START] to [END] over [FRAMES] frames" |
| **Driver** | "Add driver to [OBJ].[PROP] driven by [TARGET].[PROP] with expression [EXPR]" |
| **Geo Nodes** | "Create Geometry Nodes tree on [OBJ]: [NODE DESCRIPTION]" |

---

## Error Recovery

### When AI Gets Stuck
```
"Reset: Delete all objects created in this session. Start fresh with:
[CLEAR SPECIFICATION]"
```

### When Tool Fails
```
"The previous command failed with [ERROR]. 
Try alternative approach: [SUGGESTION]"
```

### When Result Is Wrong
```
"Undo the last operation. The issue is [DESCRIPTION].
Instead: [CORRECTED INSTRUCTION]"
```

---

## Token Optimization

### Use History Wisely
- **GenesisCore:** Toggle "Use History" off for independent commands
- **blender-mcp:** Each tool call is independent; no context needed

### Concise Prompts
```
❌ "I would like you to please create a cube that is red in color and put it at the origin"
✅ "Create CUBE named 'RedCube' at (0,0,0) material red"
```

### Batch Related Operations
```
✅ Single prompt: "Create 5 cubes in a row at x=-2,-1,0,1,2 with materials red,blue,green,yellow,purple"
```

---

## Debugging Prompts

### Inspect Scene
```
"Get full scene info including all objects, materials, lights, camera"
"Get object info for [NAME] - show vertices, faces, materials, modifiers"
"Take viewport screenshot"
```

### Check Addon Status
```
"Get addon info - show version, capabilities, protocol version"
"Check Poly Haven status"
"Check Poly Pizza status"
```

---

## Model-Specific Prompting

### DeepSeek / Qwen (Code-heavy)
```
"Write Blender Python code to: [ALGORITHMIC DESCRIPTION]
Use bpy.data, bpy.ops, mathutils. No external imports."
```

### Claude (Reasoning-heavy)
```
"Plan the steps to create [COMPLEX SCENE], then execute step by step.
Explain each step before executing."
```

### GPT-4o (Balanced)
```
"Create [SCENE] following best practices for [STYLE/TECHNIQUE].
Optimize for render time / poly count / editability."
```