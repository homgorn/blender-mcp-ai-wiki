---
id: profiling
lang: ru
orig_lang: en
category: performance
type: reference
difficulty: 0
translation: template
---
# PERFORMANCE: PROFILING, MEMORY, GPU OPTIMIZATION

> Цель: ## 🌍 MULTILANG

**ID:** profiling | **Lang:** ru | **Orig:** en | **Category:** performance | **Tags:** version

---

# PERFORMANCE: PROFILING, MEMORY, GPU OPTIMIZATION

**Production-grade performance optimization for Blender**

---

## 🎯 PERFORMANCE PYRAMID

```
                    ┌─────────────────┐
                    │   ALGORITHM     │  ← Biggest impact (10-100x)
                    │  (Data structs) │
├───────────────────┤                 ├────────────────────────────────────┤
│                   │   DATA LAYOUT   │  ← Memory access patterns (2-10x)  │
│   ARCHITECTURE    │  (SoA vs AoS)   │                                    │
├───────────────────┤                 ├────────────────────────────────────┤
│                   │  PARALLELISM    │  ← CPU/GPU utilization (2-100x)    │
│   EXECUTION       │  (SIMD/GPU)     │                                    │
├───────────────────┤                 ├────────────────────────────────────┤
│                   │  CACHING        │  ← Reuse computed results (2-10x)  │
│   OPTIMIZATION    │  (Memoize/LOD)  │                                    │
├───────────────────┤                 ├────────────────────────────────────┤
│                   │  MICRO-OPT      │  ← Instruction-level (1.1-2x)      │
│    MICRO          │  (SIMD/branch)  │                                    │
└───────────────────┘                 └──────────────────────────────────┘
```

---

## 🔬 PROFILING TOOLS

### Built-in Profiling
```python
import cProfile
import pstats
import io
from contextlib import contextmanager

@contextmanager
def profile_context(name="profile"):
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield profiler
    finally:
        profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats('cumulative')
        stats.print_stats(30)
        print(f"\n=== {name} Profile ===")
        print(stream.getvalue())

# Usage
with profile_context("Heavy Operation"):
    result = heavy_operation()
```

### Blender-Specific Profiling
```python
import bpy
import time
import bmesh

def time_operator(operator_id, *args, **kwargs):
    """Time a Blender operator"""
    start = time.perf_counter()
    result = getattr(bpy.ops, operator_id)(*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"{operator_id}: {elapsed:.4f}s")
    return result

def profile_mesh_ops(obj, operations):
    """Profile BMesh operations"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    for op_name, op_func in operations:
        start = time.perf_counter()
        op_func(bm)
        elapsed = time.perf_counter() - start
        print(f"BMesh {op_name}: {elapsed:.4f}s")
    
    bm.to_mesh(obj.data)
    bm.free()

# Profile viewport performance
def profile_viewport_redraw(iterations=100):
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    
    start = time.perf_counter()
    for _ in range(iterations):
        area.tag_redraw()
    elapsed = time.perf_counter() - start
    print(f"{iterations} redraws: {elapsed:.4f}s ({elapsed/iterations*1000:.2f}ms each)")
```

### Memory Profiling
```python
import sys
import gc
import psutil

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def profile_memory_growth(iterations=100):
    """Track memory growth over iterations"""
    gc.collect()
    initial = get_memory_usage()
    
    for i in range(iterations):
        # Your operation here
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.delete()
        
        if i % 10 == 0:
            gc.collect()
            current = get_memory_usage()
            print(f"Iteration {i}: {current - initial:.2f} MB growth")

def find_memory_leaks():
    """Find objects not being garbage collected"""
    import gc
    gc.collect()
    
    before = len(gc.get_objects())
    
    # Your operation
    for _ in range(100):
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.delete()
    
    gc.collect()
    after = len(gc.get_objects())
    
    print(f"Object count delta: {after - before}")
    if after - before > 100:
        print("⚠️ Possible memory leak!")
        
        # Find what's leaking
        types_count = {}
        for obj in gc.get_objects():
            t = type(obj).__name__
            types_count[t] = types_count.get(t, 0) + 1
        
        for t, count in sorted(types_count.items(), key=lambda x: -x[1])[:20]:
            print(f"  {t}: {count}")

# GPU Memory (NVIDIA)
def get_gpu_memory():
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return {
            'total': info.total / 1024**3,
            'used': info.used / 1024**3,
            'free': info.free / 1024**3,
        }
    except:
        return {'error': 'pynvml not available or no NVIDIA GPU'}
```

---

## 🧠 MEMORY MANAGEMENT

### Blender Memory Patterns
```python
# ✅ GOOD: Reuse data structures
def good_pattern():
    bm = bmesh.new()
    for i in range(1000):
        bmesh.ops.create_cube(bm, size=1.0)
        bm.clear()  # Reuse!
    bm.free()

# ❌ BAD: Create/destroy in loop
def bad_pattern():
    for i in range(1000):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.free()  # Alloc/free overhead

# ✅ GOOD: Batch operations
def batch_create_cubes(count):
    bm = bmesh.new()
    verts = []
    for i in range(count):
        # Add vertices directly
        pass
    bm.to_mesh(mesh)
    bm.free()

# ❌ BAD: Individual operators
def slow_create_cubes(count):
    for i in range(count):
        bpy.ops.mesh.primitive_cube_add()  # Slow!

# ✅ GOOD: Apply scale once
def apply_transforms_once(objects):
    with bpy.context.temp_override(selected_objects=objects):
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# ❌ BAD: Individual apply
def slow_apply(objects):
    for obj in objects:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(scale=True)
```

### Data Structure Optimization
```python
# ✅ Structure of Arrays (SoA) - Cache friendly
class ParticleSystem_SOA:
    def __init__(self, count):
        self.positions = [0.0] * (count * 3)  # [x0,y0,z0, x1,y1,z1, ...]
        self.velocities = [0.0] * (count * 3)
        self.masses = [1.0] * count
    
    def update(self, dt):
        for i in range(len(self.masses)):
            i3 = i * 3
            self.positions[i3]   += self.velocities[i3]   * dt
            self.positions[i3+1] += self.velocities[i3+1] * dt
            self.positions[i3+2] += self.velocities[i3+2] * dt

# ❌ Array of Structures (AoS) - Cache misses
class ParticleSystem_AOS:
    def __init__(self, count):
        self.particles = [
            {'pos': [0,0,0], 'vel': [0,0,0], 'mass': 1.0}
            for _ in range(count)
        ]

# NumPy for heavy math
import numpy as np

def numpy_particle_update(positions, velocities, dt):
    """Vectorized particle update"""
    positions += velocities * dt  # Vectorized!

# Blender + NumPy bridge
def bmesh_to_numpy(bm):
    """Convert BMesh to NumPy arrays"""
    verts = np.empty((len(bm.verts), 3), dtype=np.float32)
    for i, v in enumerate(bm.verts):
        verts[i] = v.co
    return verts

def numpy_to_bmesh(verts, bm):
    """Update BMesh from NumPy"""
    for i, v in enumerate(bm.verts):
        v.co = verts[i]
    bmesh.update_edit_mesh(bm.id_data)
```

---

## ⚡ PARALLELISM & GPU

### Python Multiprocessing
```python
from multiprocessing import Pool, cpu_count
import bpy

def process_object(obj_name):
    """Process single object in worker"""
    import bpy
    obj = bpy.data.objects[obj_name]
    # Process...
    return obj_name, result

def parallel_process(objects, worker_func, workers=None):
    workers = workers or cpu_count()
    with Pool(workers) as pool:
        results = pool.map(worker_func, [o.name for o in objects])
    return dict(results)

# For Blender: Use separate processes (not threads due to GIL)
def batch_render_scenes(scenes, workers=4):
    import subprocess
    
    def render_scene(scene_file):
        result = subprocess.run([
            'blender', '-b', scene_file, '-P', 'render_script.py'
        ], capture_output=True, text=True)
        return result.returncode == 0
    
    with Pool(workers) as pool:
        results = pool.map(render_scene, scenes)
    return all(results)
```

### GPU Compute (Experimental)
```python
# Blender 4.2+ Compute Shaders
# Requires: Blender 4.2+, Vulkan/Metal/OpenCL

# Example: Particle simulation on GPU
compute_shader = """
#version 450
layout(local_size_x = 256) in;

layout(std430, binding = 0) buffer Particles {
    vec4 position[];
    vec4 velocity[];
};

layout(push_constant) uniform PushConstants {
    float dt;
    vec3 gravity;
} pc;

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= particle_count) return;
    
    velocity[i] += pc.gravity * pc.dt;
    position[i] += velocity[i] * pc.dt;
}
"""

# Python side
def dispatch_compute_shader(shader, particle_count, dt, gravity):
    import gpu
    shader = gpu.shader.from_spirv(compute_shader)
    # ... dispatch logic
```

### NumPy/SciPy for Heavy Math
```python
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

# Fast nearest neighbor
def find_neighbors(points, query_points, k=10):
    tree = cKDTree(points)
    distances, indices = tree.query(query_points, k=k)
    return distances, indices

# Fast rotation
def rotate_points(points, axis, angle):
    rot = Rotation.from_rotvec(axis * angle)
    return rot.apply(points)

# Fast mesh operations
def mesh_boolean_union(mesh1, mesh2):
    # Use OpenVDB or CGAL via Python bindings
    import pyopenvdb as vdb
    # ... boolean operations
```

---

## 📊 RENDER PERFORMANCE

### Cycles Optimization
```python
def optimize_cycles(scene):
    s = scene.cycles
    
    # Adaptive Sampling (huge speedup)
    s.use_adaptive_sampling = True
    s.adaptive_threshold = 0.01
    s.adaptive_min_samples = 32
    
    # Denoising
    s.use_denoising = True
    s.denoiser = 'OPTIX'  # 'OPENIMAGEDENOISE' / 'OPTIX'
    s.denoising_prefilter = 'ACCURATE'
    
    # Light Paths (reduce for speed)
    s.max_bounces = 8
    s.diffuse_bounces = 3
    s.glossy_bounces = 3
    s.transmission_bounces = 8
    s.volume_bounces = 2
    
    # Caustics (expensive)
    s.caustics_reflective = False
    s.caustics_refractive = False
    
    # Light Sampling
    s.use_light_tree = True
    s.sample_light_direct = True

# Motion Blur
scene.render.use_motion_blur = True
scene.cycles.motion_blur_shutter = 0.5
scene.cycles.motion_blur_samples = 8
```

### EEVEE Next Optimization
```python
def optimize_eevee_next(scene):
    s = scene.eevee
    
    # Shadows
    s.shadow_cube_size = '1024'  # 512, 1024, 2048, 4096
    s.shadow_cascade_size = '1024'
    s.shadow_clip_start = 0.1
    s.shadow_clip_end = 100.0
    
    # GI
    s.gi_cubemap_resolution = '512'
    s.gi_cache_resolution = '256'
    s.gi_diffuse_bounces = 1
    
    # Volumetrics
    s.volumetric_tile_size = '64'
    s.volumetric_samples = 16
    
    # SSR
    s.use_ssr = True
    s.use_ssr_refraction = True
    s.ssr_quality = 0.5
    s.ssr_thickness = 0.01
```

---

## 📦 ASSET OPTIMIZATION

### LOD System
```python
def create_lod_system(base_obj, lod_ratios=[1.0, 0.5, 0.25, 0.1]):
    """Create LOD hierarchy"""
    lods = [base_obj]
    
    for i, ratio in enumerate(lod_ratios[1:], 1):
        lod = base_obj.copy()
        lod.data = base_obj.data.copy()
        lod.name = f"{base_obj.name}_LOD{i}"
        bpy.context.collection.objects.link(lod)
        
        # Decimate
        mod = lod.modifiers.new(f"Decimate_LOD{i}", 'DECIMATE')
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        
        bpy.context.view_layer.objects.active = lod
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        lods.append(lod)
    
    return lods

# Distance-based LOD switching (Geometry Nodes)
"""
GN Tree: LOD Switch
Input: Distance to Camera
Logic:
  Distance < 50m:    LOD0 (100%)
  50-200m:          LOD1 (50%)
  200-500m:         LOD2 (25%)
  500m+:            LOD3 (10% or Billboard)
"""
```

### Billboard Impostors
```python
def create_impostor(obj, angles=8, resolution=2048):
    """Create billboard impostor for distant LOD"""
    import math
    
    # Render from multiple angles
    renders = []
    for i in range(angles):
        angle = (i / angles) * 2 * math.pi
        # Render from angle
        # Save as sprite sheet
    
    # Create sprite sheet
    # Shader: Billboard + View Angle → Sprite Index
```

---

## 📈 MONITORING & BENCHMARKING

### Automated Benchmarking
```python
import json
from datetime import datetime

class BenchmarkSuite:
    def __init__(self):
        self.results = []
    
    def benchmark(self, name, func, *args, **kwargs):
        import time
        gc.collect()
        
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - elapsed
        
        self.results.append({
            'name': name,
            'time': elapsed,
            'timestamp': datetime.now().isoformat(),
            'blender_version': bpy.app.version_string,
        })
        return result
    
    def save(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

# Benchmark Suite
suite = BenchmarkSuite()

# Mesh operations
suite.benchmark("create_cube_1000", lambda: [bpy.ops.mesh.primitive_cube_add() for _ in range(1000)])
suite.benchmark("boolean_union_100", lambda: [boolean_union(c1, c2) for _ in range(100)])
suite.benchmark("subdivision_100", lambda: [subdivide(obj, 2) for _ in range(100)])

# Render
suite.benchmark("render_1080p_128spp", lambda: render_frame(1920, 1080, 128))
suite.benchmark("render_4k_256spp", lambda: render_frame(3840, 2160, 256))

# Save
suite.save("benchmark_results.json")
```

### Continuous Benchmarking (CI/CD)
```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmark
on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    container:
      image: nvidia/cuda:12.1-devel-ubuntu22.04
      options: --gpus all
    steps:
      - uses: actions/checkout@v4
      - name: Install Blender
        run: |
          apt-get update && apt-get install -y blender
      - name: Run Benchmarks
        run: python scripts/run_benchmarks.py
      - name: Compare with baseline
        run: python scripts/compare_benchmarks.py
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            // Post benchmark results as PR comment
```

---

## 🔗 LINKS

- **Blender Performance:** https://docs.blender.org/manual/en/latest/advanced/performance/
- **Python Profiling:** https://docs.python.org/3/library/profile.html
- **NumPy Performance:** https://numpy.org/doc/stable/user/basics.performance.html
- **Vulkan Compute (архив):** https://github.com/GPUOpen-LibrariesAndSDKs/VulkanSamples
- **Blender Benchmark:** https://opendata.blender.org/

> [!NOTE]
> - Blender Performance Handbook переехал в официальную документацию: https://docs.blender.org/manual/en/latest/advanced/performance/
> - Репозиторий GPUOpen VulkanSamples архивирован; актуальные примеры Vulkan: https://github.com/khronosgroup/vulkan-samples
> - NumPy Performance Guide обновлён: https://numpy.org/doc/stable/user/basics.performance.html

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/performance/profiling.md` |
| Russian | `multilang/ru/performance/profiling.md` |