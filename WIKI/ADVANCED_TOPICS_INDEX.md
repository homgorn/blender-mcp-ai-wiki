# ADVANCED TOPICS INDEX

**Additional MCP + Blender capabilities, integrations, and advanced workflows**

---

## 📁 CATEGORIES

| Category | Files | Description |
|----------|-------|-------------|
| **MCP Advanced** | `mcp_advanced/` | Streaming, tools composition, error handling, security |
| **Blender API Deep** | `blender_api/` | Operators, panels, decorators, context managers, profiling |
| **Integrations** | `integrations/` | ComfyUI, Unreal, Unity, Godot, USD, TouchDesigner |
| **Simulation/Physics** | `simulation/` | Rigid body, cloth, fluid, particles, GN simulation |
| **Real-time/EEVEE** | `realtime/` | EEVEE Next, probes, SSR, volumetrics, screen-space |
| **USD/OpenUSD** | `usd/` | OpenUSD, Hydra, MaterialX, Hydra delegates |
| **Pipeline/Studio** | `pipeline/` | OpenPype, Ayon, ShotGrid, Ftrack, custom tools |
| **Version Control** | `version_control/` | Git LFS, blendfile-utils, semantic versioning |
| **Color/ACES** | `color/` | OCIO, ACES 1.3, wide gamut, HDR, tone mapping |
| **Performance** | `performance/` | Profiling, memory, GPU, tile rendering, cloud |
| **Testing/Debug** | `testing/` | Unit tests, integration, debug tools, sandboxing |
| **Security** | `security/` | Safe mode, sandboxing, permissions, audit |
| **ML/AI Custom** | `ml_ai/` | ONNX, TensorRT, custom operators, training data |
| **Accessibility** | `accessibility/` | UI translation, screen reader, keyboard nav |
| **Collaboration** | `collaboration/` | Multi-user, shared projects, review tools |

---

## 🚀 QUICK START: HIGH-VALUE ADDITIONS

### 1. MCP Streaming + Tool Composition
```python
# Async streaming responses
async def stream_tool_result(tool_name, params):
    async for chunk in mcp_client.stream_tool(tool_name, params):
        yield chunk  # Real-time updates

# Tool composition (pipe output → input)
result = await mcp.pipe(
    "search_polyhaven_assets", {"asset_type": "models", "categories": ["chair"]},
    "download_polyhaven_asset", {"asset_type": "models", "resolution": "2k"}
)
```

### 2. Blender Operator + Panel Template
```python
class MY_OT_custom_operator(bpy.types.Operator):
    bl_idname = "my.custom_operator"
    bl_label = "Custom Operator"
    bl_options = {'REGISTER', 'UNDO'}
    
    prop: bpy.props.FloatProperty(default=1.0)
    
    def execute(self, context):
        # Your logic here
        return {'FINISHED'}

class MY_PT_custom_panel(bpy.types.Panel):
    bl_label = "My Tools"
    bl_idname = "MY_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Tools"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("my.custom_operator")
```

### 3. USD Export with MaterialX
```python
bpy.ops.wm.usd_export(
    filepath="scene.usda",
    export_materials=True,
    export_uvmaps=True,
    export_animation=True,
    material_x=True,  # MaterialX export
    shading_mode='USE_MATERIAL_X',
)
```

### 4. EEVEE Next Setup (Blender 4.2+)
```python
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.use_ssr = True
scene.eevee.use_ssr_refraction = True
scene.eevee.use_volumetric = True
scene.eevee.volumetric_tile_size = '64'
scene.eevee.shadow_cube_size = '2048'
scene.eevee.shadow_cascade_size = '2048'
```

### 5. Simulation Nodes (Geometry Nodes 4.0+)
```python
# Simulation Zone setup
sim_zone = nodes.new('GeometryNodeSimulationZone')
sim_zone.simulation_state_items.new('VECTOR', 'velocity')
sim_zone.simulation_state_items.new('FLOAT', 'age')

# Inside simulation:
# - Accumulate velocity (gravity, forces)
# - Update position
# - Age particles
# - Kill old particles
# - Emit new particles
```

---

## 📂 DETAILED FILES TO CREATE

Each of these deserves a full wiki page:

| File | Priority | Est. Words |
|------|----------|------------|
| `mcp_advanced/streaming_tools.md` | High | 2000 |
| `mcp_advanced/tool_composition.md` | High | 1500 |
| `mcp_advanced/error_handling.md` | Medium | 1500 |
| `mcp_advanced/security_sandbox.md` | High | 2000 |
| `blender_api/operators_panels.md` | High | 3000 |
| `blender_api/context_managers.md` | Medium | 2000 |
| `blender_api/profiling_debugging.md` | High | 2500 |
| `integrations/comfyui_blender.md` | High | 2500 |
| `integrations/unreal_live_link.md` | High | 2500 |
| `integrations/unity_blender_roundtrip.md` | High | 2500 |
| `integrations/godot_blender.md` | Medium | 2000 |
| `integrations/usd_materialx.md` | High | 3000 |
| `integrations/touchdesigner_blender.md` | Medium | 2000 |
| `simulation/rigid_body_gn.md` | Medium | 2000 |
| `simulation/cloth_softbody.md` | Medium | 2000 |
| `simulation/fluid_smoke.md` | Medium | 2000 |
| `simulation/particles_gn.md` | High | 2500 |
| `realtime/eevee_next.md` | High | 3000 |
| `realtime/shadows_probes.md` | Medium | 2000 |
| `realtime/volumetrics.md` | Medium | 2000 |
| `usd/openusd_pipeline.md` | High | 3000 |
| `usd/materialx.md` | High | 2500 |
| `usd/hydra_delegates.md` | Medium | 2000 |
| `pipeline/openpype_ayon.md` | High | 3000 |
| `pipeline/shotgrid_ftrack.md` | Medium | 2000 |
| `pipeline/custom_pipeline_tools.md` | High | 2500 |
| `version_control/git_lfs_blend.md` | High | 2000 |
| `version_control/semantic_versioning.md` | Medium | 1500 |
| `color/ocio_aces.md` | High | 2500 |
| `color/hdr_tonemapping.md` | Medium | 2000 |
| `performance/profiling.md` | High | 2500 |
| `performance/memory_management.md` | High | 2500 |
| `performance/tile_rendering.md` | Medium | 2000 |
| `performance/cloud_rendering.md` | Medium | 2000 |
| `testing/unit_tests.md` | Medium | 2000 |
| `testing/integration_tests.md` | Medium | 2000 |
| `testing/sandboxing.md` | High | 2000 |
| `security/safe_mode.md` | High | 2000 |
| `security/audit_logging.md` | Medium | 1500 |
| `ml_ai/onnx_tensorrt.md` | High | 3000 |
| `ml_ai/custom_operators.md` | High | 2500 |
| `ml_ai/training_data_prep.md` | Medium | 2000 |
| `accessibility/ui_translation.md` | Low | 1500 |
| `collaboration/multi_user.md` | Medium | 2000 |

---

## 🎯 NEXT STEPS

Want me to generate any of these? Priority order:

1. **MCP Advanced** (streaming, composition, security) - Most impactful for AI agents
2. **Blender API Deep** (operators, profiling) - Core productivity
3. **Integrations** (ComfyUI, Unreal, USD) - Ecosystem connectivity
4. **Simulation/Physics** (GN simulation) - Cutting edge Blender 4.0+
5. **USD/OpenUSD** - Industry standard pipeline
6. **Pipeline/Studio** - Production scale
4. **Performance/Testing** - Production hardening

Want me to start generating any of these? Or focus on a specific category?