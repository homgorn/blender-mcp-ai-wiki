---
id: setup_12_unreal_livelink
lang: ru
category: setups
status: full
tags: [blender, setup, unreal]
---
# SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK

**ID:** SETUP-12 | **Type:** Game Engine Integration | **Difficulty:** ⭐⭐⭐ | **Time:** 30-60 min

---

## 🎯 ЦЕЛЬ
Настроить бесшовную интеграцию Blender ↔ Unreal Engine 5 через Live Link, Datasmith, USD

---

## 🎯 АРХИТЕКТУРА

```
Blender (Authoring)          Live Link / USD          Unreal Engine 5 (Runtime)
┌─────────────────┐         Live Link / USD          ┌─────────────────┐
│  Modeling       │ ──────────────────────────────▶  │  Level Design   │
│  Rigging/Anim   │  Datasmith / Live Link           │  Blueprint      │
│  Materials      │  Alembic / FBX / USD             │  Niagara FX     │
│  Cameras        │  Live Link Face/VCam             │  Sequencer      │
└─────────────────┘                                  └─────────────────┘
```

---

## 🔗 MЕТОДЫ ИНТЕГРАЦИИ

| Метод | Качество | Сложность | Use Case |
|-------|----------|-----------|----------|
| **Live Link** | Высокая | Средняя | Realtime камеры, 얼굴, камеры |
| **Datasmith** | Высокая | Низкая | Архитектура, статические сцены |
| **USD** | Максимальная | Высокая | Пайплайн, варианты, LOD |
| **Alembic** | Высокая | Низкая | Анимация, кэш |
| **FBX** | Средняя | Низкая | Быстрый экспорт/импорт |
| **Live Link Face/VCam** | Высокая | Низкая | Мокап, виртуальная камера |

---

## 🔴 LIVE LINK SETUP

### 1. Blender: Live Link Plugin
```python
# blender_livelink.py
# Требует: Unreal Live Link Plugin в Blender (Experimental)
# или аддон: https://github.com/EpicGames/UnrealEngine/tree/release/Engine/Plugins/Animation/LiveLink

import bpy
import asyncio
import websockets
import json

class BlenderLiveLink:
    def __init__(self, host="127.0.0.1", port=9876):
        self.uri = f"ws://{host}:{port}"
        self.websocket = None
        self.running = False
    
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        await self.register_subject()
    
    async def register_subject(self):
        """Регистрация субъекта в Unreal"""
        msg = {
            "MessageType": "SubjectRegistration",
            "SubjectName": "Blender_Camera",
            "SubjectType": "Camera"
        }
        await self.websocket.send(json.dumps(msg))
    
    async def send_camera_frame(self, camera_data):
        """Отправка данных камеры каждый кадр"""
        frame_data = {
            "MessageType": "FrameData",
            "SubjectName": "Blender_Camera",
            "FrameData": {
                "WorldTransform": {
                    "Translation": list(camera_data.location),
                    "Rotation": list(camera_data.rotation_quaternion),
                    "Scale": [1,1,1]
                },
                "FieldOfView": camera_data.fov,
                "AspectRatio": camera_data.aspect_ratio,
                "NearClip": camera_data.clip_start,
                "FarClip": camera_data.clip_end
            }
        }
        await self.websocket.send(json.dumps(frame_data))

# Авто-отправка каждый кадр
def setup_livelink_camera():
    bpy.app.handlers.frame_change_post.append(send_camera_data)

def send_camera_data(scene):
    cam = bpy.context.scene.camera
    if cam and livelink_client:
        asyncio.create_task(livelink_client.send_camera_frame(cam.data))
```

### Unreal Live Link Setup
```
1. Unreal: Edit → Plugins → Live Link → Enable
2. Window → Live Link → Add Source → "Blender" (WebSocket)
3. Source: ws://localhost:9876
4. Subject: "Blender_Camera" → Add to Level → CineCameraActor → Live Link Controller
```

---

## 📦 DATASMITH (Архитектура/Статика)

### Blender → Datasmith Export
```python
# blender_datasmith_export.py
import bpy
import os
from pathlib import Path

def export_datasmith(output_path, selection_only=True):
    """
    Экспорт через Datasmith (требует Blender Datasmith Exporter)
    """
    # В Blender 4.0+ есть встроенный экспорт Datasmith
    # File → Export → Datasmith (.udatasmith)
    
    # Настройки экспорта:
    export_settings = {
        "export_selected": True,
        "export_hierarchy": True,
        "export_materials": True,
        "export_textures": True,
        "export_lights": True,
        "export_cameras": True,
        "convert_units": True,  # Blender meters → Unreal cm
        "collision": "simple",  # none/simple/complex
        "generate_lightmap_uvs": True,
        "lightmap_resolution": 64,
    }
    
    # Экспорт через Python API (если доступно)
    # bpy.ops.export_scene.datasmith(filepath=output_path, **export_settings)
    
    print("Use File → Export → Datasmith (.udatasmith) for best results")

# Настройки материалов для Datasmith
def setup_datasmith_materials():
    """Подготовка материалов для Datasmith"""
    for mat in bpy.data.materials:
        if mat.use_nodes:
            # Найти Principled BSDF
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # Datasmith понимает стандартные PBR входы
                    # Base Color, Roughness, Metallic, Normal, Emission
                    # Дополнительные: Clearcoat, Anisotropy, Sheen, Transmission
                    pass

# Именование для Datasmith
def naming_convention():
    """
    Datasmith Naming Rules:
    - SM_StaticMeshName (Static Mesh)
    - SK_SkeletalMeshName (Skeletal Mesh)
    - M_MaterialName (Material)
    - T_TextureName_D (BaseColor)
    - T_TextureName_N (Normal)
    - T_TextureName_R (Roughness)
    - T_TextureName_M (Metallic)
    - T_TextureName_AO (Ambient Occlusion)
    - T_TextureName_H (Height)
    - MI_MaterialInstance (Material Instance)
    """
```

---

## 💎 USD PIPELINE (Продвинутый)

### USD Export для Unreal
```python
# usd_unreal_export.py
import bpy
from pathlib import Path

def export_usd_unreal(filepath, selection_only=True):
    """Экспорт USD оптимизированный для Unreal"""
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    bpy.ops.wm.usd_export(
        filepath=str(Path(filepath).absolute()),
        selection_only=selection_only,
        export_materials=True,
        export_uvmaps=True,
        export_animation=True,
        export_frame_range=True,
        export_frame_step=1,
        
        # MaterialX для Unreal
        material_x=True,
        shading_mode='USE_MATERIAL_X',
        
        # Purpose для Unreal
        purpose='default',  # default, render, proxy, guide
        
        # Instancing
        export_instancing=True,
        
        # Animation
        export_frame_range=True,
        export_frame_step=1,
        
        # Custom properties
        export_custom_properties=True,
        export_custom_attributes=True,
    )

# USD Variants для Unreal
def create_usd_variants(filepath, variants):
    """
    variants = {
        "modeling": ["high", "low", "proxy"],
        "material": ["clean", "damaged", "rusty"],
        "lod": ["LOD0", "LOD1", "LOD2", "LOD3"]
    }
    """
    from pxr import Usd, UsdGeom, Sdf
    
    stage = Usd.Stage.CreateNew(filepath)
    root = stage.GetRootPrim()
    
    for set_name, variants in variants.items():
        variant_set = root.GetVariantSets().AddVariantSet(set_name)
        for variant in variants:
            variant_set.AddVariant(variant)
            variant_set.SetVariantSelection(variant)
            with variant_set.GetVariantEditContext():
                # Добавить variant-specific контент
                pass
    
    stage.GetRootLayer().Save()

# LOD Variants
def create_lod_variants_usd(asset_name, lod_meshes):
    """
    lod_meshes = {
        "LOD0": mesh_obj_high,
        "LOD1": mesh_obj_med,
        "LOD2": mesh_obj_low,
        "LOD3": mesh_obj_imp
    }
    """
    from pxr import Usd, UsdGeom
    
    stage = Usd.Stage.CreateNew(f"{asset_name}_LODs.usda")
    root = stage.DefinePrim(f"/{asset_name}", "Xform")
    
    for lod_name, mesh_obj in lod_meshes.items():
        lod_prim = stage.DefinePrim(f"/{asset_name}/{lod_name}", "Xform")
        # Экспорт меша в USD prim
        # ... mesh export logic
    
    stage.GetRootLayer().Save()
```

---

## 🎬 ANIMATION PIPELINE

### Alembic Export/Import
```python
# alembic_pipeline.py
import bpy

def export_alembic_animation(filepath, objects, start_frame, end_frame):
    """Экспорт анимации в Alembic для Unreal"""
    bpy.ops.wm.alembic_export(
        filepath=str(Path(filepath).absolute()),
        selected=True,
        selected_objects=[o.name for o in objects],
        start=start_frame,
        end=end_frame,
        step=1.0,
        flatten=True,
        subdiv_schema=True,
        write_uvs=True,
        write_normals=True,
        write_vertex_colors=True,
        export_subdivision=True,
        subdiv_schema=True,
    )

# Unreal Alembic Import
"""
Unreal: File → Import → Alembic Cache (.abc)
Settings:
- Import Type: Skeletal / Geometry Cache
- Import Type: Skeletal (для скелетной анимации)
- Create Skeleton: Yes
- Import Materials: True
- Create Physics Asset: No
"""

# Geometry Cache (для сложной анимации)
def export_geometry_cache(objects, output_dir):
    """
    Geometry Cache (.abc) для сложных деформаций
    Unreal: Geometry Cache Component
    """
    for obj in objects:
        bpy.ops.wm.alembic_export(
            filepath=f"{output_dir}/{obj.name}.abc",
            selected=True,
            start=bpy.context.scene.frame_start,
            end=bpy.context.scene.frame_end,
        )
```

---

## 🎥 LIVE LINK FACE / VCAM

### Live Link Face (iOS)
```python
# blender_livelink_face.py
"""
Live Link Face (iOS) → Blender → Unreal
1. iPhone: Live Link Face app → IP Blender/Unreal
2. Blender: Прием morph targets
3. Unreal: Live Link Face → MetaHuman
"""

# Blender: Прием ARKit blendshapes
class LiveLinkFaceReceiver:
    def __init__(self, port=11111):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', port))
    
    def receive_blendshapes(self):
        data, addr = self.sock.recvfrom(65536)
        # ARKit blendshapes: 52 blendshapes
        # Применить к Shape Keys меша
        data = json.loads(data)
        for name, value in data['blendshapes'].items():
            if name in bpy.context.object.data.shape_keys.key_blocks:
                bpy.context.object.data.shape_keys.key_blocks[name].value = value

# Unreal Live Link Face Setup:
"""
1. Unreal: Window → Live Link → Add Source → Live Link Face
2. iPhone: Live Link Face App → Connect to Unreal IP
3. Blueprint: Live Link Controller → Set Subject → Face
3. MetaHuman: Assign to Face Mesh
"""
```

### Virtual Camera (VCam)
```python
# blender_virtual_camera.py
"""
Virtual Camera: Blender Camera → Unreal VCam
1. Blender: Camera + Live Link
2. Unreal: VCam Plugin → Live Link Controller
3. iPad/iPhone: Unreal VCam App → Control Camera
"""

# Blender: Virtual Camera Setup
def setup_virtual_camera():
    cam = bpy.data.objects.new("VCam", bpy.data.cameras.new("VCam"))
    bpy.context.collection.objects.link(cam)
    
    # Live Link properties
    cam["LiveLinkSubject"] = "VCam"
    cam["LiveLinkSource"] = "Blender"
    
    # Constraints для smooth movement
    constraint = cam.constraints.new('COPY_TRANSFORMS')
    constraint.target = bpy.data.objects.get("VCam_Controller")
    
    return cam
```

---

## 📦 UNREAL IMPORT SETTINGS

### FBX Import Settings
```python
# unreal_fbx_import.py (Unreal Python)
import unreal

def import_fbx_optimized(fbx_path, destination_path="/Game/Assets/"):
    """Оптимизированный импорт FBX в Unreal"""
    
    import_options = unreal.FbxImportUI()
    import_options.import_mesh = True
    import_options.import_as_skeletal = False
    import_options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    
    # Static Mesh Settings
    import_options.static_mesh_import_data.combine_meshes = True
    import_options.static_mesh_import_data.auto_generate_collision = True
    import_options.static_mesh_import_data.collision_type = unreal.FBXCollisionType.FBXCTF_Box
    import_options.static_mesh_import_data.auto_compute_lod_distances = True
    import_options.static_mesh_import_data.lod_count = 4
    import_options.static_mesh_import_data.lod_distance_ratios = [0.0, 0.3, 0.6, 0.9]
    
    # Materials
    import_options.material_import_method = unreal.FBXMaterialImportMethod.FBXMI_FIND_OR_CREATE
    import_options.texture_import_data.material_search_path = "/Game/Materials"
    
    # Import
    task = unreal.AssetImportTask()
    task.filename = fbx_path
    task.destination_path = destination_path
    task.replace_existing = True
    task.automated = True
    task.save = True
    task.options = import_options
    
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
```

### Geometry Cache Import
```python
# Geometry Cache для сложных деформаций
def import_geometry_cache(abc_path, destination="/Game/Animations/"):
    import_options = unreal.GeometryCacheImportOptions()
    import_options.import_type = unreal.GeometryCacheImportType.ALEMBIC
    import_options.flip_u = False
    import_options.flip_v = False
    
    task = unreal.AssetImportTask()
    task.filename = abc_path
    task.destination_path = destination
    task.options = import_options
    task.automated = True
    task.replace_existing = True
    
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
```

---

## 🎮 VIRTUAL CAMERA (VCAM)

### Blender → Unreal VCam
```python
# blender_virtual_camera.py
"""
Blender Camera → Unreal Virtual Camera
1. Blender: Camera + Live Link
2. Unreal: VCam Plugin → Live Link Controller
3. iPad/iPhone: Unreal VCam App
"""

class VirtualCameraSetup:
    def __init__(self):
        self.vcam = None
    
    def setup_vcam(self, camera_name="VCam"):
        # Создать камеру
        cam_data = bpy.data.cameras.new("VCam")
        cam_obj = bpy.data.objects.new("VCam", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        
        # Настройки для VCam
        cam_data.lens = 35  # mm
        cam_data.sensor_width = 36
        cam_data.sensor_height = 24
        
        # Live Link properties
        bpy.context.object["LiveLinkSubject"] = "VCam"
        bpy.context.object["LiveLinkRole"] = "VirtualCamera"
        
        # Constraints для VCam controller
        self.setup_vcam_constraints()
    
    def setup_vcam_constraints(self):
        # VCam Controller Empty
        controller = bpy.data.objects.new("VCam_Controller", None)
        bpy.context.collection.objects.link(controller)
        controller.empty_display_type = 'ARROWS'
        controller.empty_display_size = 0.5
        
        # Camera follows controller
        cam = bpy.data.objects["VCam"]
        constraint = cam.constraints.new('COPY_TRANSFORMS')
        constraint.target = bpy.data.objects["VCam_Controller"]
        constraint.influence = 1.0
        
        # VCam specific properties
        controller["VCam_Speed"] = 10.0
        controller["VCam_Sensitivity"] = 1.0
```

### Unreal VCam Setup
```python
# Unreal Python (в Unreal Editor)
import unreal

def setup_unreal_vcam():
    # Enable VCam Plugin
    # Edit → Plugins → Virtual Camera → Enable → Restart
    
    # Create VCam Component
    vcam = unreal.VirtualCameraComponent()
    vcam.set_editor_property("LiveLinkSubject", "VCam")
    
    # VCam Settings
    vcam.set_editor_property("FieldOfView", 90.0)
    vcam.set_editor_property("AspectRatio", 16.0/9.0)
    
    # Input Settings
    input_settings = unreal.get_default_object(unreal.InputSettings)
    input_settings.add_axis_mapping(unreal.InputAxisKeyMapping(
        axis_name="VCam_MoveForward",
        key=unreal.Key("W"),
        scale=1.0
    ))
    # ... другие маппинги
```

---

## 📦 PIPELINE AUTOMATION

### Automated Export/Import
```python
# pipeline_automation.py
import bpy
import subprocess
from pathlib import Path

class PipelineAutomation:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.exports_dir = self.project_root / "exports"
        self.imports_dir = self.project_root / "imports"
    
    def export_all_for_unreal(self):
        """Экспорт всех ассетов для Unreal"""
        collections = {
            "Characters": "Characters",
            "Props": "Props", 
            "Environment": "Environment",
            "Vehicles": "Vehicles"
        }
        
        for coll_name, export_subdir in collections.items():
            coll = bpy.data.collections.get(coll_name)
            if coll:
                self.export_collection(coll, export_subdir)
    
    def export_collection(self, collection, subdir):
        """Экспорт коллекции как отдельные FBX/USD"""
        output_dir = self.exports_dir / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for obj in collection.all_objects:
            if obj.type == 'MESH':
                # FBX Export
                fbx_path = output_dir / f"{obj.name}.fbx"
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.export_scene.fbx(
                    filepath=str(fbx_path),
                    use_selection=True,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    bake_space_transform=True,
                    object_types={'MESH', 'ARMATURE'},
                    use_armature_deform_only=True,
                    add_leaf_bones=False,
                    primary_bone_axis='Y_FORWARD',
                    secondary_bone_axis='X_UP'
                )
                
                # USD Export
                usd_path = output_dir / f"{obj.name}.usda"
                bpy.ops.wm.usd_export(
                    filepath=str(output_dir / f"{obj.name}.usda"),
                    selected_objects_only=True,
                    export_materials=True,
                    material_x=True,
                    export_animation=False
                )

# Usage
auto = PipelineAutomation("/project")
auto.export_all_for_unreal()
```

---

## 🎯 UNREAL BLUEPRINT INTEGRATION

### Live Link Blueprint
```cpp
// Unreal C++ / Blueprint
// LiveLinkController Component

UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()
    
    UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "LiveLink")
    ULiveLinkControllerComponent* LiveLinkController;
    
    UFUNCTION(BlueprintCallable)
    void SetLiveLinkSubject(FName SubjectName)
    {
        if (LiveLinkController)
        {
            LiveLinkController->SetSubject(SubjectName);
        }
    }
    
    UFUNCTION(BlueprintCallable)
    void SetLiveLinkRetargetAsset(ULiveLinkRetargetAsset* Asset)
    {
        if (LiveLinkController)
        {
            LiveLinkController->SetRetargetAsset(Asset);
        }
    }
};

// Blueprint Usage:
// 1. Add LiveLinkController Component to Character
// 2. Set Subject Name: "Blender_Camera" или "VCam"
// 3. Set Retarget Asset: ваш Retarget Asset
// 4. В Tick: Get Live Link Pose → Apply to Mesh
```

---

## 📊 PERFORMANCE TIPS

| Optimization | Impact |
|--------------|--------|
| **Reduce Update Rate** | Live Link: 30Hz вместо 60Hz для далеко объектов |
| **Compress Transforms** | Отправлять только измененные кости |
| **Batch Updates** | Группировать обновления в один пакет |
| **LOD для Live Link** | Упрощенные скелеты для дальних объектов |
| **Async Updates** | Не блокировать Game Thread |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 13: BLENDER + UNITY ROUNDTRIP](setup_13_unity_roundtrip.md)
- **Теги:** #blender, #setup, #unreal

