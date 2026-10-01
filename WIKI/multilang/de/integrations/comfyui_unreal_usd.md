---
id: comfyui_unreal_usd
lang: de
orig_lang: ru
category: integrations
type: reference
difficulty: 0
translation: template
---
# INTEGRATIONS: COMFYUI, UNREAL, USD, TOUCHDESIGNER

> Ziel: 

**ID:** comfyui_unreal_usd | **Lang:** de | **Orig:** ru | **Category:** integrations | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'comfyui_unreal_usd'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
comfyui_unreal_usd / integrations / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: comfyui_unreal_usd
lang: ru
orig_lang: en
category: integrations
type: reference
difficulty: 0
---

# INTEGRATIONS: COMFYUI, UNREAL, USD, TOUCHDESIGNER

> Цель: ## 🌍 MULTILANG

**ID:** comfyui_unreal_usd | **Lang:** ru | **Orig:** en | **Category:** integrations | **Tags:** 

---

# INTEGRATIONS: COMFYUI, UNREAL, USD, TOUCHDESIGNER

**Blender ecosystem integrations for production pipelines**

---

## 🎨 COMFYUI + BLENDER

### ComfyUI → Blender Live Sync
```python
# blender_comfyui_sync.py
import asyncio
import aiohttp
import json
import bpy
from pathlib import Path

class ComfyUIBridge:
    def __init__(self, comfyui_url="http://127.0.0.1:8188"):
        self.base_url = comfyui_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def queue_prompt(self, workflow: dict):
        """Queue a prompt in ComfyUI"""
        async with self.session.post(
            f"{self.base_url}/prompt",
            json={"prompt": workflow, "client_id": "blender"}
        ) as resp:
            return await resp.json()
    
    async def get_images(self, prompt_id: str):
        """Get generated images"""
        async with self.session.get(
            f"{self.base_url}/history/{prompt_id}"
        ) as resp:
            history = await resp.json()
            return history.get(prompt_id, {}).get("outputs", {})
    
    async def download_image(self, filename: str, subfolder: str = "", type: str = "output"):
        """Download generated image"""
        params = {"filename": filename, "subfolder": subfolder, "type": type}
        async with self.session.get(
            f"{self.base_url}/view", params=params
        ) as resp:
            return await resp.read()

# Blender Integration
async def generate_textures_comfyui(prompt: str, output_dir: Path):
    """Generate PBR textures via ComfyUI"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": f"PBR texture, {prompt}, seamless, 8k, high quality", "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "blur, low quality, distorted, watermark, text", "clip": ["1", 1]}
        },
        "4": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42, "steps": 20, "cfg": 7, "sampler_name": "dpmpp_2m",
                "scheduler": "karras", "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                "latent_image": ["5", 0]
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["4", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "pbr_texture", "images": ["6", 0]}
        }
    }
    
    async with ComfyUIBridge() as bridge:
        result = await bridge.queue_prompt({"prompt": workflow})
        prompt_id = result["prompt_id"]
        
        # Wait for completion
        while True:
            await asyncio.sleep(2)
            history = await bridge.get_images(prompt_id)
            if prompt_id in history:
                break
        
        # Download and apply to Blender
        outputs = history[prompt_id]["outputs"]
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img_info in node_output["images"]:
                    img_data = await bridge.download_image(
                        img_info["filename"], 
                        img_info.get("subfolder", ""),
                        img_info.get("type", "output")
                    )
                    # Save and create material
                    filepath = Path("textures") / img_info["filename"]
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    Path(filepath).write_bytes(img_data)
                    create_pbr_material_from_image(filepath)
```

### ComfyUI Workflow Templates for PBR
```json
{
  "pbr_material_generation": {
    "base_color": {
      "prompt": "{material}, {style}, base color, albedo, flat lighting",
      "negative": "shadows, lighting, highlights, specular, glossy"
    },
    "roughness": {
      "prompt": "{material}, roughness map, grayscale, detailed surface imperfections",
      "negative": "color, shiny, glossy, smooth"
    },
    "normal": {
      "prompt": "{material}, normal map, OpenGL format, detailed surface details",
      "negative": "color, flat, smooth"
    },
    "normal_flip_y": true,
    "height": {
      "prompt": "{material}, height map, displacement, depth, grayscale",
      "negative": "flat, smooth"
    }
  }
}
```

---

## 🎮 UNREAL ENGINE LIVE LINK

### Unreal Live Link Plugin for Blender
```python
# unreal_livelink.py
import bpy
import socket
import json
import struct
from bpy.props import StringProperty, BoolProperty, IntProperty

class UnrealLiveLink:
    """Live Link connection to Unreal Engine"""
    
    def __init__(self, host="127.0.0.1", port=1986):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Connect to Unreal Live Link"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.connected = True
        print(f"Connected to Unreal at {self.host}:{self.port}")
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.connected = False
    
    def send_transform(self, object_name: str, location, rotation, scale):
        """Send object transform to Unreal"""
        if not self.connected:
            return
        
        data = {
            "subject_name": object_name,
            "transform": {
                "location": list(location),
                "rotation": list(rotation),  # Quaternion [x, y, z, w]
                "scale": list(scale)
            },
            "timestamp": bpy.context.scene.frame_current / bpy.context.scene.render.fps
        }
        
        message = json.dumps(data).encode('utf-8')
        # Length prefix (4 bytes)
        length = struct.pack('>I', len(message))
        self.socket.sendall(length + message)
    
    def send_mesh(self, object_name: str, mesh_data: dict):
        """Send mesh data to Unreal"""
        # Implementation for mesh streaming
        pass

# Blender Operator for Live Link
class OBJECT_OT_unreal_livelink_connect(bpy.types.Operator):
    bl_idname = "unreal.livelink_connect"
    bl_label = "Connect to Unreal Live Link"
    
    host: StringProperty(name="Host", default="127.0.0.1")
    port: IntProperty(name="Port", default=1986)
    
    def execute(self, context):
        global livelink
        livelink = UnrealLiveLink(self.host, self.port)
        livelink.connect()
        return {'FINISHED'}

class OBJECT_OT_unreal_livelink_sync(bpy.types.Operator):
    bl_idname = "unreal.livelink_sync"
    bl_label = "Sync Selection to Unreal"
    
    def execute(self, context):
        if not livelink or not livelink.connected:
            self.report({'ERROR'}, "Not connected to Unreal")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            livelink.send_transform(
                obj.name,
                obj.location,
                obj.rotation_quaternion,
                obj.scale
            )
        return {'FINISHED'}

# Panel
class VIEW3D_PT_unreal_livelink(bpy.types.Panel):
    bl_label = "Unreal Live Link"
    bl_idname = "VIEW3D_PT_unreal_livelink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Unreal'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("unreal.livelink_connect")
        layout.operator("unreal.livelink_sync")
        layout.prop(context.scene, "unreal_auto_sync")

# Auto-sync on frame change
def sync_on_frame_change(scene):
    if getattr(scene, "unreal_auto_sync", False) and livelink and livelink.connected:
        for obj in bpy.context.selected_objects:
            livelink.send_transform(
                obj.name, obj.location, obj.rotation_quaternion, obj.scale
            )

bpy.app.handlers.frame_change_post.append(sync_on_frame_change)
```

---

## 🎮 UNREAL ROUNDTRIP (Blender ↔ Unreal)

### Export Pipeline
```python
# unreal_export.py
import bpy
import os
from pathlib import Path

class UnrealExportSettings:
    """Unreal-optimized export settings"""
    
    @staticmethod
    def configure_fbx_export():
        return {
            "apply_unit_scale": True,
            "apply_scale_options": 'FBX_SCALE_ALL',
            "bake_space_transform": True,
            "object_types": {'ARMATURE', 'MESH'},
            "use_mesh_modifiers": True,
            "use_mesh_modifiers_render": True,
            "mesh_smooth_type": 'FACE',
            "use_subsurf": True,
            "add_leaf_bones": False,
            "primary_bone_axis": 'Y_FORWARD',
            "secondary_bone_axis": 'X_UP',
            "bake_anim": True,
            "bake_anim_use_all_bones": True,
            "bake_anim_use_nla_strips": True,
            "bake_anim_use_all_actions": False,
            "bake_anim_force_startend_keying": True,
            "bake_anim_step": 1.0,
            "bake_anim_simplify_factor": 1.0,
        }
    
    @staticmethod
    def configure_gltf_export():
        return {
            "export_format": 'GLB',
            "export_copyright": "MyStudio",
            "export_image_format": 'AUTO',
            "export_materials": 'EXPORT',
            "export_colors": True,
            "export_normals": True,
            "export_tangents": True,
            "export_animations": True,
            "export_frame_range": True,
            "export_frame_step": 1,
            "export_force_sampling": True,
            "export_skins": True,
            "export_morph": True,
            "export_lights": False,
            "export_cameras": False,
        }

def export_for_unreal(asset_name, output_dir, collection_name=None):
    """Export selected objects or collection for Unreal"""
    output_path = Path("exports") / "unreal" / asset_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Select objects
    if collection_name:
        coll = bpy.data.collections.get(collection_name)
        if coll:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in coll.objects:
                obj.select_set(True)
    else:
        # Use selected objects
        pass
    
    # Export FBX
    fbx_path = Path("exports") / "unreal" / f"{asset_name}.fbx"
    bpy.ops.export_scene.fbx(
        filepath=str(fbx_path),
        **UnrealExportSettings.configure_fbx_export()
    )
    
    # Also export GLB for web/preview
    glb_path = Path("exports") / "unreal" / f"{asset_name}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        **{
            "export_format": 'GLB',
            "use_selection": True,
            "export_apply": True,
            "export_tangents": True,
            "export_materials": 'EXPORT',
            "export_animations": True,
            "export_frame_range": True,
            "export_skins": True,
            "export_morph": True,
        }
    )
    
    print(f"Exported to {fbx_path} and {glb_path}")

# Unreal Import Helper (Python for Unreal)
unreal_import_helper = '''
import unreal

def import_fbx_asset(fbx_path, import_settings=None):
    """Import FBX into Unreal with optimal settings"""
    if import_settings is None:
        import_settings = unreal.FbxImportUI()
        import_settings.import_mesh = True
        import_settings.import_as_skeletal = False
        import_settings.import_rigid_animation = False
        import_settings.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        import_settings.static_mesh_import_data.combine_meshes = True
        import_settings.static_mesh_import_data.auto_generate_collision = True
        import_settings.static_mesh_import_data.collision_type = unreal.FBXCollisionType.FBXCTF_Box
        import_settings.material_import_method = unreal.FBXMaterialImportMethod.FBXMI_FIND_OR_CREATE
        import_settings.texture_import_data.material_search_path = "/Game/Materials"
    
    task = unreal.AssetImportTask()
    task.filename = fbx_path
    task.destination_path = "/Game/Assets/Imported"
    task.replace_existing = True
    task.automated = True
    task.save = True
    task.options = import_settings
    
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    print(f"Imported: {fbx_path}")
'''
```

---

## 📦 USD / MATERIALX / OPENUSD

### USD Export with MaterialX
```python
# usd_export.py
import bpy
from pathlib import Path

def export_usd_materialx(
    filepath: str,
    export_materials: bool = True,
    export_uvmaps: bool = True,
    export_animation: bool = True,
    purpose: str = "default",  # "default", "render", "proxy", "guide"
    material_x: bool = True,
    shading_mode: str = 'USE_MATERIAL_X'  # 'USE_MATERIAL_X', 'USE_PREVIEW', 'USE_LOOKDEV'
):
    """Export USD with MaterialX support"""
    
    # Ensure output directory
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Export settings
    bpy.ops.wm.usd_export(
        filepath=filepath,
        export_materials=export_materials,
        export_uvmaps=export_uvmaps,
        export_animation=export_animation,
        export_frame_range=True,
        export_frame_step=1,
        export_uvmaps=True,
        export_normals=True,
        export_colors=True,
        export_animation=True,
        export_skinning=True,
        export_skinning=True,
        export_uvmaps=True,
        export_display_color=True,
        export_instancing=True,
        export_visibility=True,
        export_custom_properties=True,
        export_custom_attributes=True,
        export_materials=export_materials,
        export_uvmaps=export_uvmaps,
        export_animation=export_animation,
        export_frame_range=True,
        export_frame_step=1,
        # MaterialX specific
        material_x=material_x,
        shading_mode=shading_mode,
        # Purpose
        purpose=purpose,
    )

# MaterialX Shader Network in Blender
def create_materialx_shader(material_name: str):
    """Create MaterialX-compatible shader network"""
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Standard Surface (MaterialX compatible)
    standard = nodes.new('ShaderNodeBsdfPrincipled')
    standard.location = (0, 0)
    
    # MaterialX standard surface inputs
    # base_color, specular_color, specular_roughness, metallic, etc.
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    output.target = 'MATERIALX'  # MaterialX output
    
    # Connect
    mat.node_tree.links.new(standard.outputs['BSDF'], output.inputs['Surface'])
    
    # Add MaterialX specific nodes
    # MX_Standard_Surface, MX_Normal_Map, MX_Displacement, etc.
    
    return mat

# USD Scene Assembly
def assemble_usd_scene(shot_name: str, assets: list, output_path: str):
    """Assemble USD scene from multiple assets"""
    import pxr.Usd as Usd
    import pxr.UsdGeom as UsdGeom
    import pxr.Sdf as Sdf
    
    stage = Usd.Stage.CreateNew(str(Path("shots") / shot_name / f"{shot_name}.usda"))
    stage.SetDefaultPrim(stage.DefinePrim(f"/{shot_name}", "Scope"))
    
    # Set up default prim
    stage.SetDefaultPrim(stage.GetPrimAtPath(f"/{shot_name}"))
    
    # Add assets as references
    for i, asset in enumerate(assets):
        prim_path = f"/{shot_name}/assets/{asset['name']}_{i:03d}"
        prim = stage.DefinePrim(prim_path, "Xform")
        prim.GetReferences().AddReference(asset['usd_path'])
        
        # Set transform
        xform = UsdGeom.Xformable(prim)
        xform.AddTranslateOp().Set(asset.get('location', (0,0,0)))
        xform.AddRotateXYZOp().Set(asset.get('rotation', (0,0,0)))
        xform.AddScaleOp().Set(asset.get('scale', (1,1,1)))
    
    # Save
    stage.GetRootLayer().Save()
    print(f"USD scene assembled: {output_path}")
```

### USD Pipeline Integration
```python
# usd_pipeline.py
"""
USD Pipeline for Blender → USD → Houdini/Maya/Katana → Render
"""

class USDPipeline:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.usd_dir = self.project_root / "usd"
        self.usd_dir.mkdir(exist_ok=True)
    
    def publish_asset(self, asset_name: str, version: str, asset_type: str):
        """Publish asset as USD with versioning"""
        # Versioned path: /assets/props/crate/v003/crate_v003.usda
        version_dir = self.usd_dir / "assets" / "props" / asset_name / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        usd_path = version_dir / f"{asset_name}_v{version}.usda"
        
        # Export current selection
        self.export_usd_with_materialx(str(version_dir / f"{asset_name}_v{version}.usda"))
        
        # Create symlink to latest
        latest_link = self.usd_dir / "assets" / "props" / asset_name / "latest.usda"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(usd_path.relative_to(latest_link.parent))
        
        return str(usd_path)
    
    def assemble_shot(self, shot_name: str, layout_data: list):
        """Assemble shot from published assets"""
        shot_dir = self.usd_dir / "shots" / shot_name
        shot_dir.mkdir(parents=True, exist_ok=True)
        
        shot_usd = shot_dir / f"{shot_name}.usda"
        self.assemble_shot(shot_name, layout_data, str(shot_usd))
        
        return str(shot_usd)
```

---

## 🎛 TOUCHDESIGNER ↔ BLENDER

### TouchDesigner ↔ Blender OSC Bridge
```python
# touchdesigner_bridge.py
import bpy
import socket
import json
import threading
import time

class TouchDesignerBridge:
    def __init__(self, td_host="127.0.0.1", td_port=7000, blender_port=7001):
        self.td_addr = (td_host, td_port)
        self.blender_port = blender_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", blender_port))
        self.running = False
        self.callbacks = {}
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
    
    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(65536)
                msg = json.loads(data.decode())
                self.handle_message(msg)
            except Exception as e:
                print(f"TD Bridge error: {e}")
    
    def handle_message(self, msg):
        msg_type = msg.get("type")
        if msg_type in self.callbacks:
            self.callbacks[msg_type](msg.get("data", {}))
    
    def register_callback(self, msg_type, callback):
        self.callbacks[msg_type] = callback
    
    def send_to_td(self, msg_type: str, data: dict):
        msg = {"type": msg_type, "data": data, "timestamp": time.time()}
        self.socket.sendto(json.dumps(msg).encode(), self.td_addr)

# Blender → TouchDesigner
def setup_td_bridge():
    bridge = TouchDesignerBridge()
    
    # Register callbacks
    def on_td_camera(data):
        cam = bpy.data.objects.get("TD_Camera")
        if cam:
            cam.location = data.get("location", cam.location)
            cam.rotation_euler = data.get("rotation", cam.rotation_euler)
            cam.data.lens = data.get("lens", cam.data.lens)
    
    def on_td_lights(data):
        for light_data in data.get("lights", []):
            light = bpy.data.objects.get(light_data["name"])
            if light:
                light.location = light_data.get("location", light.location)
                light.data.energy = light_data.get("energy", light.data.energy)
    
    bridge = TouchDesignerBridge()
    bridge.register_callback("camera", on_td_camera)
    bridge.register_callback("lights", on_td_lights)
    bridge.start()
    
    # Send Blender scene info to TD
    def send_scene_info():
        data = {
            "objects": [
                {"name": obj.name, "location": list(obj.location), 
                 "rotation": list(obj.rotation_euler)}
                for obj in bpy.data.objects if obj.type in {'MESH', 'LIGHT', 'CAMERA'}
            ],
            "frame": bpy.context.scene.frame_current,
            "fps": bpy.context.scene.render.fps
        }
        bridge.send_to_td("scene_update", data)
    
    bpy.app.handlers.frame_change_post.append(lambda s: send_scene_info())
    
    return bridge
```

---

## 🔗 LINKS

- **ComfyUI:** https://github.com/comfyanonymous/ComfyUI
- **Unreal Live Link:** https://docs.unrealengine.com/5.3/en-US/live-link-in-unreal-engine/
- **USD Docs:** https://openusd.org/
- **MaterialX:** https://www.materialx.org/
- **TouchDesigner:** https://derivative.ca/
- **OpenPype/Ayon:** https://openpype.io/ / https://ayon.ynput.cloud/

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/integrations/comfyui_blender.md` |
| Russian | `multilang/ru/integrations/comfyui_blender.md` |