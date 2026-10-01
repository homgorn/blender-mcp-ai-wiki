---
lang: en
tags: [ai-3d, animation, assets, automation, blender, geometry-nodes, mcp, modeling]
---
# WORKFLOWS - PRODUCTION PIPELINES

## Workflow 1: Text-to-3D Scene Generation

### Using GenesisCore (In-Blender Chat)
```
1. Open Blender → N-panel → GenesisCore
2. Configure OpenRouter + Model (DeepSeek/Qwen)
3. Enable tools: Common, Object, Material, Polyhaven
4. Prompt sequence:
   
   "Create a cyberpunk alley scene:
   - Wet pavement plane 20x20m
   - Neon signs using emission materials (cyan, magenta, yellow)
   - Steam particles from grates
   - Hovering vehicle (simple primitive shapes)
   - Search Poly Haven for 'urban' HDRI at 2k, set as world
   - Camera: low angle looking down alley, 35mm lens"
```

### Using blender-mcp (External AI)
```
OpenCode/Claude prompt:
"Build a cyberpunk alley scene in Blender:
1. Create 20x20m plane for wet pavement at z=0
2. Add emission materials for neon signs (cyan, magenta, yellow) on cubes
3. Create particle system for steam on plane areas
4. Build simple hovering vehicle from primitives
5. Search Poly Haven for 'urban' HDRI, download 2k, set as world
6. Add camera at (-5, -10, 3) looking at (0,0,1), 35mm lens
7. Set render to Cycles, 256 samples, denoising on"
```

---

## Workflow 2: Texture Generation Pipeline

### GenesisCore + Dream Textures Combo
```
Phase 1 - Geometry (GenesisCore):
"Create a medieval castle wall section: 
- 10x5m stone wall with crenellations
- Wooden door with iron hinges
- Arrow slits as boolean cutouts
- Stone floor tiles"

Phase 2 - Materials (Dream Textures):
1. Select wall object → N-panel → Dream Textures
2. Generate: "weathered medieval stone wall, moss in cracks, seamless" 
   → Check Seamless → Generate → Apply
3. Select door → "aged oak wood, iron studs, seamless" → Apply
4. Select floor → "cobblestone pathway, worn, seamless" → Apply

Phase 3 - Polish (GenesisCore):
"Add vertex paint for moss variation on wall
Add geometry nodes for procedural ivy on top edges
Set up 3-point lighting for texture showcase"
```

### Pure Dream Textures (Texture Projection)
```
1. Model base geometry (wall, floor, props)
2. Select all faces to texture
3. Enter Local View (/)
4. Dream Textures → Project Dream Texture
5. Prompt: "ancient dungeon corridor, stone bricks, torch lighting, moss"
6. Model: stabilityai/stable-diffusion-2-depth
7. Click Project Dream Texture
8. Adjusts UVs automatically
```

---

## Workflow 3: Asset-Driven Scene Assembly

### Poly Haven + Poly Pizza + Sketchfab
```
"Create a cozy library scene using free assets:

1. Poly Haven:
   - Search models: 'bookshelf', 'wooden chair', 'desk lamp'
   - Search HDRI: 'library', 'indoor', 2k
   - Download all at 2k

2. Poly Pizza (low-poly fill):
   - Search: 'book', 'scroll', 'candle', 'potion bottle'
   - Licence: CC0 (no attribution)
   - Download, normalize_size=1.0, target_size=0.15

3. Sketchfab (hero pieces):
   - Search: 'ornate desk', 'grandfather clock'
   - Get preview, download at target_size=1.5m

4. Assembly:
   - Position bookshelves along walls
   - Scatter Poly Pizza books on shelves (random rotation)
   - Place hero desk center, chair beside
   - Add HDRI as world environment
   - Add area lights for desk lamp, candle glow
   - Camera: wide angle from doorway"
```

---

## Workflow 4: AI 3D Generation + Cleanup

### Hyper3D Rodin / Hunyuan3D
```
"Generate a fantasy creature concept:
1. Create Hyper3D job: 'dragon whelp, cute, stylized, low poly'
2. Poll status every 30s until complete
3. Import result
4. Cleanup:
   - Decimate modifier (ratio 0.3) for game-ready
   - Separate loose parts (P → By Loose Parts)
   - Create materials for each part (scales, eyes, horns)
   - UV unwrap (Smart UV Project)
   - Bake normal map from high-poly (if needed)
5. Rig: Add armature, auto-weight, basic pose"
```

---

## Workflow 5: Procedural Generation with Geometry Nodes

### City Block Generator
```
"Create Geometry Nodes setup for procedural city block:

1. Base grid: 10x10, 20m spacing
2. Building height: random 10-50m (seed controlled)
3. Building shape: extruded random polygons
4. Windows: array on faces, random offset
5. Roofs: flat/hipped/gabled (weighted random)
6. Street level: sidewalk, road markings, lamps
7. Variations: 
   - Park lots (empty with trees)
   - Plaza (fountain + benches)
   - Alleyways (dumpsters, fire escapes)

Controls exposed in modifier panel:
- Seed, Block Size, Density, Height Range, Style Mix"
```

### Blender Python for Geo Nodes
```python
# Execute via execute_blender_code
import bpy

ng = bpy.data.node_groups.new("CityBlock", 'GeometryNodeTree')
# ... build node tree programmatically ...
# See api/blender-api.md for Geometry Nodes API
```

---

## Workflow 6: Animation & Rigging

### Character Animation Pipeline
```
1. Import/Generate character (Mixamo, Hyper3D, manual)
2. Rigify:
   - Add Rigify meta-rig (Human)
   - Align bones to mesh
   - Generate rig
   - Parent with automatic weights
3. Animation:
   - Import motion capture (BVH/FBX)
   - Retarget to Rigify
   - Clean up: NLA strips, action layers
4. Export:
   - FBX for game engines
   - GLTF for web
   - Alembic for simulation cache
```

### Camera Animation
```
"Create cinematic camera path:
1. Add Bezier curve for dolly path
2. Add camera, Follow Path constraint
3. Add Empty for target, Track To constraint
4. Animate curve evaluation (0-1 over frames)
5. Add DOF: focus on target Empty, f-stop 1.8
6. Motion blur: Cycles → 0.5 shutter, 16 samples"
```

---

## Workflow 7: Optimization for Real-Time

### Game-Ready Asset Pipeline
```
Input: High-poly model (Sketchfab/Hyper3D/manual)

1. Retopology:
   - Instant Meshes / Quad Remesher
   - Target: 1-5k tris (props), 10-30k (characters)

2. UV Unwrap:
   - Seams on hard edges
   - Pack islands (margin 0.005)
   - UDIM if >4k textures

3. Baking (Cycles):
   - Normal (Tangent Space, 4k)
   - AO (16 samples, 4k)
   - Curvature (4k)
   - Position (for masking)
   - Material ID

4. Texturing (Substance/Blender):
   - PBR metal/rough workflow
   - Smart materials + custom details

5. Export:
   - GLTF: separate textures, Draco compression
   - Validate: gltf-transform inspect
   - LODs: 100%, 50%, 25%, 10% poly count
```

---

## Workflow 8: Batch Processing / Automation

### Render Farm Setup
```
# Blender CLI rendering
blender -b scene.blend -E CYCLES -o //render/frame_#### -f 1..250

# Distributed (using Flamenco or custom)
# 1. Split frames across machines
# 2. Sync assets via shared storage
# 3. Collect output
```

### Python Batch Script Template
```python
# Run: blender -b -P batch_script.py

import bpy
import sys

def process_scene(scene_path, output_dir):
    bpy.ops.wm.open_mainfile(filepath=scene_path)
    
    scene = bpy.context.scene
    scene.render.filepath = output_dir
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    
    bpy.ops.render.render(animation=True, write_still=False)
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    # Args after --
    argv = sys.argv[sys.argv.index("--")+1:]
    process_scene(argv[0], argv[1])
```

---

## Workflow 9: Version Control for .blend

### Git LFS Setup
```bash
# .gitattributes
*.blend filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.hdr filter=lfs diff=lfs merge=lfs -text
*.exr filter=lfs diff=lfs merge=lfs -text
*.glb filter=lfs diff=lfs merge=lfs -text
*.gltf filter=lfs diff=lfs merge=lfs -text

# Initialize
git lfs install
git lfs track "*.blend" "*.png" "*.hdr" "*.exr" "*.glb"
git add .gitattributes
```

### Blend File Diff
```bash
# Use blendfile-utils or custom script
# For meaningful diffs, export to interchange format:
blender -b scene.blend -P export_gltf.py
# Then diff .gltf (JSON)
```

---

## Decision Matrix: Which Tool When?

| Task | Primary Tool | Fallback |
|------|--------------|----------|
| Quick geometry | GenesisCore chat | blender-mcp |
| Complex scene logic | blender-mcp + Codex/Claude | GenesisCore |
| Texture generation | Dream Textures | Poly Haven textures |
| Hero assets | Sketchfab / Hyper3D | Manual modeling |
| Background props | Poly Pizza | Poly Haven models |
| HDRI lighting | Poly Haven (both) | Poly Haven |
| Code automation | execute_blender_code | Geometry Nodes |
| Game assets | Dream Textures + Retopo | Substance Painter |
| Animation | Rigify + NLA | Manual keyframes |
| Batch render | CLI + Flamenco | Manual |

---

## Tips for Reliable Automation

1. **Always verify before acting:** `get_scene_info` → plan → execute
2. **Use named objects:** Explicit names > "the cube I just made"
3. **Check mode:** Ensure `OBJECT` mode before transforms
4. **Apply scale:** `Ctrl+A → Scale` before bevel/array/modifiers
5. **Unique data:** `.copy()` meshes when duplicating
6. **Save incrementally:** `bpy.ops.wm.save_as_mainfile(filepath="scene_v001.blend")`
7. **Use collections:** Organize by type (Geometry, Lights, Cameras, FX)

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [TEXT-TO-3D WORKFLOWS](text-to-3d.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md)
- **По темам:** [P18: DRIVERS & CONSTRAINTS](../../../prompts/18_drivers_constraints.md), [P45: GEOMETRY NODES SIMULATION ZONES](../../../prompts/45_gn_simulation.md), [SETUP 35: READY PLAYER ME AVATARS](../../../setups/setup_35_readyplayerme.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](../../../setups/setup_45_hunyuan3d_21.md)
- **Теги:** #ai-3d, #animation, #assets, #automation, #blender, #geometry-nodes, #mcp, #modeling

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

