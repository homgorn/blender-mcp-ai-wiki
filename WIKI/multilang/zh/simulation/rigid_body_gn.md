---
id: rigid_body_gn
lang: zh
orig_lang: ru
category: simulation
type: reference
difficulty: 0
translation: template
---
# SIMULATION & PHYSICS: GEOMETRY NODES 4.0+

> 目标: 

**ID:** rigid_body_gn | **Lang:** zh | **Orig:** ru | **Category:** simulation | **Tags:** **

## 使用方法
这是 'rigid_body_gn' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
rigid_body_gn / simulation / **
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: rigid_body_gn
lang: ru
orig_lang: en
category: simulation
type: reference
difficulty: 0
---

# SIMULATION & PHYSICS: GEOMETRY NODES 4.0+

> Цель: ## 🌍 MULTILANG

**ID:** rigid_body_gn | **Lang:** ru | **Orig:** en | **Category:** simulation | **Tags:** 

---

# SIMULATION & PHYSICS: GEOMETRY NODES 4.0+

**Advanced simulation workflows in Blender 4.0+ Geometry Nodes**

---

## 🎯 SIMULATION ZONE (Blender 4.0+)

### Core Concepts
```
┌─────────────────────────────────────────────────────────────┐
│                    SIMULATION ZONE                          │
├─────────────────────────────────────────────────────────────┤
│  Inputs (from outside)          State (persisted per frame) │
│  ┌─────────────────┐            ┌─────────────────────────┐ │
│  │ Geometry Input  │            │ position (Vector)       │ │
│  │ Parameters      │            │ velocity (Vector)       │ │
│  │ Time/Frame      │            │ age (Float)             │ │
│  └─────────────────┘            │ custom attributes...    │ │
│                                 └─────────────────────────┘ │
│                        ┌─────────────────────┐              │
│                        │   Simulation Body   │              │
│                        │  (runs per frame)   │              │
│                        │                     │              │
│                        │ 1. Read State       │              │
│                        │ 2. Compute Forces   │              │
│                        │ 3. Update Velocity  │              │
│                        │ 4. Update Position  │              │
│                        │ 5. Handle Collisions│              │
│                        │ 6. Write State      │              │
│                        └─────────────────────┘              │
│                                 │                           │
│                                 ▼                           │
│                        ┌─────────────────────┐              │
│                        │   Output Geometry   │              │
│                        │   (next frame)      │              │
│                        └─────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 SIMULATION NODES REFERENCE

### Simulation Zone Setup
```python
# In Geometry Nodes Editor:
# 1. Add "Simulation Zone" node (Shift+A → Simulation → Simulation Zone)
# 2. Connect input geometry to "Geometry" input
# 3. Inside zone: Build simulation logic
# 4. Connect output geometry to "Geometry" output
```

### State Attributes (Auto-created)
```python
# Built-in state attributes (auto-managed):
# - position (Vector) - particle/object position
# - velocity (Vector) - current velocity
# - angular_velocity (Vector) - rotation speed
# - age (Float) - simulation age in frames
# - lifetime (Float) - when to die (0 = infinite)
# - id (Integer) - unique particle ID
# - mass (Float) - for physics calculations
# - drag (Float) - air resistance factor
```

### Simulation Nodes Reference
```python
# === INPUT NODES ===
# Simulation Input: Access external geometry/parameters
# Simulation Output: Write results back
# Frame: Current frame number
# Delta Time: Time per frame (1/FPS)

# === STATE NODES ===
# Store Named Attribute: Create/update state
# Named Attribute: Read state
# Remove Named Attribute: Cleanup

# === PHYSICS NODES ===
# Accumulate Field: Add forces (gravity, wind, noise)
# Drag: Velocity damping
# Gravity: Constant acceleration
# Wind: Directional force with noise

# === COLLISION NODES ===
# Collision: Detect collisions with geometry
# Response: Bounce, slide, stick, die
# Proximity: Distance-based interactions

# === PARTICLE NODES ===
# Emit Particles: Spawn new particles
# Kill Particles: Remove by condition
# Resample Particles: Maintain count

# === UTILITY NODES ===
# Index Switch: Branch by index
# Menu Switch: Branch by enum
# Compare: Logic operations
# Math/Vector Math: Calculations
# Random Value: Noise/randomness
# Attribute Statistic: Min/Max/Mean
```

---

## 🌊 PARTICLE SYSTEMS

### Basic Particle System
```python
# GN Tree: Basic_Particles
# 1. Input: Emitter geometry (plane, sphere, etc.)
# 2. Simulation Zone:
#    a. Emit Particles: Rate=100, Velocity=(0,0,5), Spread=0.5
#    b. Accumulate Field: Gravity (0,0,-9.8)
#    c. Drag: Factor=0.01
#    d. Kill Particles: Age > 100
#    e. Output: Instance on Points → Collection "Particle_Prefabs"
# 3. Output Geometry

# Advanced: Particle Attributes
"""
Attribute: age (Float) - frame age
Attribute: lifetime (Float) - max frames
Attribute: size (Float) - per-particle scale
Attribute: color (Color) - per-particle color
Attribute: rotation (Euler/Quat) - orientation
Attribute: velocity (Vector) - for motion blur
"""
```

### Particle Forces
```python
# Gravity + Wind + Turbulence
"""
Accumulate Field (Gravity):
  Strength: -9.8
  Direction: (0, 0, -1)

Accumulate Field (Wind):
  Strength: 5.0
  Direction: (1, 0, 0)
  Noise: 0.5

Accumulate Field (Turbulence):
  Strength: 2.0
  Noise Scale: 5.0
  Noise Detail: 4

# Combine forces
Vector Math: Add (Gravity + Wind + Turbulence) → Total Force
Vector Math: Multiply (Force × Delta Time) → Velocity Change
Vector Math: Add (Velocity + Velocity Change) → New Velocity
"""

# Force Fields from Objects
"""
Object Info (Force Field Object) → Position
Vector Math: Subtract (Particle Pos - Field Pos) → Direction
Math: Power (1/Distance²) → Falloff
Vector Math: Scale (Direction × Falloff × Strength) → Force
"""
```

### Particle Collision
```python
# Collision with Geometry
"""
Collision Node:
  Target: Collision Geometry
  Mode: "Outside" / "Inside" / "Both"
  
Response Options:
  - Die: Kill particle
  - Bounce: Reflect velocity × restitution
  - Slide: Project velocity to surface tangent
  - Stick: Velocity = 0, parent to surface
  
Advanced:
  - Friction: Reduce tangential velocity
  - Restitution: Bounciness (0-1)
  - Thickness: Offset collision surface
"""
```

---

## 🧱 RIGID BODY SIMULATION (GN)

### Rigid Body in GN (Blender 4.0+)
```python
# Rigid Body Simulation via GN
"""
1. Input: Collection of rigid bodies (convex hulls)
2. Simulation Zone:
   a. Broad Phase: BVH broadphase collision detection
   b. Narrow Phase: GJK/EPA collision detection
   c. Constraint Solver: Sequential impulse solver
   d. Integration: Semi-implicit Euler
3. Output: Transformed instances

Nodes Used:
- Simulation Input (rigid body collection)
- Rigid Body Properties (mass, inertia, friction, restitution)
- Rigid Body Constraints (hinge, slider, fixed, spring)
- Collision Detection (broad + narrow phase)
- Constraint Solver (iterations=10, tolerance=0.001)
- Integration (velocity + position update)
"""

# Rigid Body Properties Node
"""
Properties per body:
- Mass (0 = static/infinite)
- Inertia Tensor (3x3 matrix, auto from mesh)
- Friction (0-1)
- Restitution/Bounciness (0-1)
- Linear Damping (air resistance)
- Angular Damping (air resistance)
- Sleep Threshold (auto-sleep when slow)
- Collision Shape: Convex Hull / Mesh / Box / Sphere / Capsule
"""
```

### Constraint System
```python
# Constraint Types
"""
Fixed: Weld two bodies together
Hinge: Rotation around single axis
Slider: Translation along single axis
Cone Twist: Limited rotation (ragdoll joints)
Spring: Soft constraint with stiffness/damping
Motor: Drive to target velocity/position
"""
```

---

## 🧵 CLOTH & SOFT BODY (GN)

### Cloth Simulation
```python
# Cloth Simulation in GN
"""
Cloth Properties:
- Bending Stiffness: Resistance to bending
- Stretch Stiffness: Resistance to stretching
- Shear Stiffness: Resistance to shearing
- Damping: Velocity damping
- Pressure: Volume preservation (for balloons)
- Self Collision: Check against self
- Vertex Groups: Pinning, stiffness maps

Solver: Projective Dynamics (XPBD)
- Iterations: 4-8 (more = stiffer)
- Time Step: Fixed substeps for stability
"""

# Cloth Pinning
"""
Vertex Group "Pin": Weight 1.0 = fully pinned
Vertex Group "Stiffness": Per-vertex stiffness multiplier
"""

### Soft Body
```python
# Soft Body (Tetrahedral)
"""
Tetrahedralize input mesh → Tetrahedra
Properties:
- Young's Modulus: Stiffness
- Poisson Ratio: Volume preservation
- Damping: Velocity decay
- Plasticity: Permanent deformation threshold
- Fracture: Break threshold

Solver: FEM (Finite Element Method) or XPBD
"""
```

---

## 💧 FLUID & SMOKE (GN + Native)

### FLIP Fluid (Geometry Nodes)
```python
# FLIP Fluid in GN (Experimental)
"""
Grid-Based FLIP:
1. Particles carry velocity/mass
2. Transfer to grid (PIC/FLIP blend)
3. Pressure projection (Poisson solve)
4. Velocity extrapolation
4. Transfer back to particles
5. Surface reconstruction (Marching Cubes)

Nodes:
- Particle to Grid (PIC/FLIP ratio)
- Grid Operations (Diffusion, Advection, Pressure)
- Pressure Solve (Multigrid/Conjugate Gradient)
- Grid to Particle
- Surface Reconstruction (Dual Contouring)
"""

# Quick Fluid (Native Blender)
"""
Quick Fluid Setup:
1. Domain: Cube → Quick Fluid → Domain
2. Flow: Object → Quick Fluid → Flow
3. Effector: Object → Quick Fluid → Effector
4. Cache: Bake to disk
"""
```

### Smoke/Fire (Native + GN)
```python
# Smoke Simulation
"""
Smoke Domain Settings:
- Resolution: 64-256 (powers of 2)
- Time Scale: 1.0
- Vorticity: 2.0 (turbulence)
- Dissolve: 0.01 (smoke decay)

Flow Settings:
- Type: Smoke / Fire / Fire+Smoke
- Fuel: 1.0
- Temperature: 1.0 (fire) / 0.0 (smoke)
- Density: 1.0

GN Integration:
- Cache smoke to VDB/VDB sequence
- GN: Volume to Mesh (Marching Cubes)
- GN: Instance on Volume Points
"""
```

---

## 🌊 ADVANCED TECHNIQUES

### Substeps & Stability
```python
# Fixed Substeps for Stability
"""
Substeps: 4-8 per frame (more = stable, slower)
Time Step: 1/FPS / Substeps

Adaptive Substepping:
- Check max velocity
- If velocity × dt > cell_size: increase substeps
- Max substeps: 16
"""

### Collision Optimization
```python
# Broad Phase
"""
BVH Tree: Build once per frame
AABB Test: Fast rejection
Pairs: Only test overlapping AABBs

# Narrow Phase
GJK: Distance between convex shapes
EPA: Penetration depth/direction
Contact Generation: Manifold (up to 4 contacts)
"""

### GPU Acceleration (Future/Experimental)
```python
# Compute Shaders for Physics
"""
Blender 4.2+ Compute Shader Support:
- Particle systems on GPU
- Cloth/Soft body on GPU
- Fluid pressure solve on GPU
- Broad phase on GPU

Requirements:
- Blender 4.2+
- Vulkan/Metal/OpenCL support
- Experimental features enabled
"""
```

---

## 🎨 CREATIVE EXAMPLES

### Rain Simulation
```python
# Rain with Splash
"""
1. Emitter: Plane above scene
2. Particles: Rain drops (stretched spheres)
3. Forces: Gravity + Wind + Turbulence
4. Collision: Ground plane → Splash particles
5. Splash: Secondary emitter at collision points
5. Render: Motion blur + Depth of Field
"""
```

### Destruction (Fracture + RBD)
```python
# Procedural Fracture + RBD
"""
1. Input Mesh → Voronoi Fracture (GN) → Fractured Pieces
2. Assign Rigid Body Properties (mass from volume)
3. Impulse Force at Impact Point
4. RBD Simulation
5. Dust/Debris Particles from fracture edges
5. Fracture Sound (by impact energy)
"""
```

### Cloth on Character
```python
# Cloth on Rigged Character
"""
1. Character Mesh → Vertex Groups for pinning
2. Cloth Mesh (shirt/pants) → Shrinkwrap to body (bind)
3. Cloth Sim: Pin groups (shoulders, waist, collar)
4. Collision: Body mesh (thickened)
5. Wind/Turbulence for movement
6. Cache → Alembic → Engine
"""
```

---

## 🔧 PERFORMANCE TIPS

| Technique | Speedup | Trade-off |
|-----------|---------|-----------|
| **Instance on Points** | 100x vs objects | All instances identical |
| **Point Cache (Alembic/USD)** | Playback only | No runtime sim |
| **Decimate LOD** | 10x viewport | Lower detail far |
| **Billboard Impostors** | 100x far | No 3D rotation |
| **GPU Compute** | 10-50x | Experimental |
| **Fixed Substeps** | Stable | Predictable cost |

---

## 🔗 LINKS

- **GN Simulation Docs:** https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/simulation/
- **XPBD Paper:** https://matthias-research.github.io/pages/publications/XPBD.pdf
- **Blender Physics:** https://docs.blender.org/manual/en/latest/physics/
- **XPBD in GN:** https://developer.blender.org/T112345

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/simulation/rigid_body_gn.md` |
| Russian | `multilang/ru/simulation/rigid_body_gn.md` |