---
lang: en
---
# PIPELINE & STUDIO: OPENPYPE / AYON

**Production pipeline management for Blender studios**

---

## 🎯 WHAT IS OPENPYPE / AYON?

| Feature | OpenPype | AYON |
|---------|----------|------|
| **Status** | Mature, stable | Active development (OpenPype successor) |
| **Architecture** | Python, MongoDB, Qt | Python, PostgreSQL, React/Qt |
| **DCC Support** | Blender, Maya, Houdini, Nuke, 3dsMax, etc. | Same + more |
| **Key Feature** | Project anatomy, publishing, versioning | Modern UI, better API, cloud-ready |
| **License** | LGPL | Apache 2.0 |

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                        SERVER                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │  Mongo  │  │  REST   │  │  Web UI │  │  Events │         │
│  │   DB    │  │   API   │  │         │  │  Bus    │         │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   BLENDER     │    │   HOUDINI     │    │    NUKE       │
│  (Addon)      │    │  (Package)    │    │  (Menu)       │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## 🚀 INSTALLATION

### Server (Docker)
```yaml
# docker-compose.yml
version: '3.8'
services:
  mongo:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  openpype:
    image: ynput/openpype:latest
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - OPENPYPE_MONGO_DATABASE=openpype
      - OPENPYPE_SECRET=your-secret-key
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    depends_on:
      - mongo

volumes:
  mongo_data:
```

### Client (Blender Addon)
```bash
# Install via OpenPype Launcher
# 1. Download OpenPype Launcher from GitHub Releases
# 2. Run launcher, login to server
# 3. Click "Install Blender Addon"
# 4. Select Blender executable
# 5. Restart Blender

# Or manual install:
# 1. Download OpenPype client zip
# 2. Extract to: ~/.config/blender/4.2/scripts/addons/openpype
# 3. Enable in Preferences → Add-ons
```

---

## ⚙️ CONFIGURATION

### Project Anatomy (Project Structure)
```yaml
# config/anatomy.yaml
project:
  name: "MyProject"
  code: "MPJ"
  
anatomy:
  roots:
    work: "/mnt/storage/projects/MyProject/work"
    publish: "/mnt/storage/projects/MyProject/publish"
    scratch: "/tmp/openpype_scratch"
  
  templates:
    # File naming
    work_file: "{root[work]}/{project[name]}/{asset[type]}/{asset[name]}/work/{task[name]}/v{version:03d}/{asset[name]}_{task[name]}_v{version:03d}.{ext}"
    publish_file: "{root[publish]}/{project[name]}/{asset[type]}/{asset[name]}/publish/{subset[name]}/v{version:03d}/{subset[name]}_v{version:03d}.{ext}"
    
    # Folder structure
    folder: "{root[work]}/{project[name]}/{asset[type]}/{asset[name]}/{task[name]}"
    
    # Naming conventions
    version_padding: 3
    frame_padding: 4

  # Asset types
  asset_types:
    - character
    - prop
    - environment
    - vehicle
    - fx
    - camera
    - rig
  
  # Tasks
  tasks:
    - modeling
    - rigging
    - surfacing
    - layout
    - animation
    - fx
    - lighting
    - compositing
  
  # Subsets (what gets published)
  subsets:
    modelMain:
      families: ["model"]
      tasks: ["modeling"]
      extensions: [".abc", ".usd", ".fbx", ".obj"]
    modelProxy:
      families: ["model"]
      tasks: ["modeling"]
      extensions: [".abc", ".usd"]
    lookDev:
      families: ["lookdev"]
      tasks: ["surfacing"]
      extensions: [".ma", ".usd", ".ass"]
    rigMain:
      families: ["rig"]
      tasks: ["rigging"]
      extensions: [".ma", ".usd"]
    animation:
      families: ["animation"]
      tasks: ["animation"]
      extensions: [".abc", ".usd"]
    layout:
      families: ["layout"]
      tasks: ["layout"]
      extensions: [".abc", ".usd"]
    fx:
      families: ["fx"]
      tasks: ["fx"]
      extensions: [".abc", ".vdb", ".bgeo.sc"]
    lighting:
      families: ["lighting"]
      tasks: ["lighting"]
      extensions: [".ma", ".usd"]
    comp:
      families: ["comp"]
      tasks: ["compositing"]
      extensions: [".nk", ".exr", ".mov"]
```

---

## 🔌 BLENDER ADDON SETUP

### Installation & Setup
```python
# In Blender after installing OpenPype addon:
# 1. Preferences → Add-ons → OpenPype → Configure
# 2. Set Server URL: http://localhost:8080
# 3. Login with credentials
# 4. Select Project
# 4. OpenPype menu appears in top bar

# Auto-setup on Blender start
import bpy

def setup_openpype():
    import openpype.hosts.blender.api as op_blender
    
    # Auto-connect to server
    op_blender.connect_to_server("http://localhost:8080")
    
    # Set project
    op_blender.set_current_project("MyProject")
    
    # Load tools
    op_blender.install_tools()

bpy.app.handlers.load_post.append(lambda _: setup_openpype())
```

---

## 📦 PUBLISHING WORKFLOW

### Publisher UI (Blender)
```python
# Publisher is built into OpenPype Blender addon
# Access via: OpenPype → Publisher

# Publish Steps:
# 1. Select instances to publish
# 2. Validate (auto-runs validators)
# 4. Review validation results
# 5. Click "Publish"
# 6. Check progress in UI
# 7. Verify in OpenPype Web UI

# Custom Validators
class ValidateMeshNonManifold(pyblish.api.InstancePlugin):
    """Check for non-manifold geometry"""
    order = pyblish.api.ValidatorOrder
    families = ["model"]
    
    def process(self, instance):
        import bpy
        import bmesh
        
        obj = instance.data["object"]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        
        non_manifold = [e for e in bm.edges if not e.is_manifold]
        bm.free()
        
        if non_manifold:
            raise ValueError(f"Non-manifold edges found: {len(non_manifold)}")

# Custom Extractors
class ExtractAlembic(pyblish.api.Extractor):
    """Export Alembic cache"""
    order = pyblish.api.ExtractorOrder
    families = ["animation", "fx"]
    
    def extract(self, instance):
        import bpy
        from pathlib import Path
        
        staging_dir = Path(self.staging_dir(instance))
        filepath = staging_dir / f"{instance.name}.abc"
        
        # Select objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in instance.data["objects"]:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = instance.data["objects"][0]
        
        # Export Alembic
        bpy.ops.wm.alembic_export(
            filepath=str(filepath),
            selected=True,
            start=instance.context.data["frameStart"],
            end=instance.context.data["frameEnd"],
            selected=True,
            flatten=True,
            subsamples=4,
        )
        
        # Add to representations
        if "representations" not in instance.data:
            instance.data["representations"] = []
        
        instance.data["representations"].append({
            "name": "abc",
            "ext": "abc",
            "files": filepath.name,
            "stagingDir": str(staging_dir),
        )
```

---

## 🎯 WORKFLOW EXAMPLES

### Character Pipeline
```python
# Character Publishing Pipeline
"""
1. Modeling → Publish "modelMain" (Alembic/USD)
   ↓
2. Rigging → Reference modelMain → Publish "rigMain" (Maya/USD)
   ↓
3. Surfacing → Reference modelMain → Publish "lookDev" (Materials + Textures)
   ↓
4. Animation → Reference rigMain → Publish "animation" (Alembic/USD)
   ↓
5. Lighting → Reference animation + lookDev → Publish "lighting" (USD)
   ↓
6. Compositing → Publish "comp" (EXR + NK)
"""

# Publish Template
class PublishCharacter(pyblish.api.ContextPlugin):
    order = pyblish.api.ContextPluginOrder
    
    def process(self, context):
        # Define what to publish for a character
        instances = [
            {
                "name": "hero_modelMain",
                "family": "model",
                "subset": "modelMain",
                "objects": ["hero_geo"],
            },
            {
                "name": "hero_rigMain",
                "family": "rig",
                "subset": "rigMain",
                "objects": ["hero_rig"],
            },
            {
                "name": "hero_lookDev",
                "family": "lookdev",
                "subset": "lookDev",
                "objects": ["hero_geo"],
            },
        ]
        
        for inst_data in instances:
            instance = context.create_instance(inst_data["name"])
            instance.data.update({
                "family": inst_data["family"],
                "subset": inst_data["subset"],
                "objects": inst_data["objects"],
            })
```

---

## 🔧 AYON SPECIFICS (Next Gen)

### AYON Advantages
```yaml
# AYON improvements over OpenPype:
- Modern React-based Web UI
- GraphQL API instead of REST
- PostgreSQL instead of MongoDB
- Better multi-site support
- Built-in review tools (ftrack-style)
- Improved artist UI in DCCs
- Better plugin system
- Cloud-ready (Kubernetes)
```

### AYON Blender Addon
```python
# AYON Blender addon (similar to OpenPype but improved)
# Installation: Same process via AYON Launcher

# Key differences:
# - Uses GraphQL API
# - Better settings management
# - Improved publisher UI
- Better dependency tracking
- Integrated review tools
```

---

## 📊 PROJECT MANAGEMENT

### Shot Management
```python
# Shot Pipeline
class ShotManager:
    def __init__(self, project_name):
        self.project = project_name
    
    def create_shot(self, sequence, shot_number, description=""):
        """Create shot entity in OpenPype/AYON"""
        shot_name = f"{sequence}{shot_number:03d}"
        
        # Create folder structure
        shot_path = Path(f"shots/{sequence}/{shot_name}")
        shot_path.mkdir(parents=True, exist_ok=True)
        
        # Create entity in OpenPype
        # (via API)
        return shot_name
    
    def assign_tasks(self, shot_name, tasks):
        """Assign tasks to artists"""
        for task_name, artist in tasks.items():
            # Create task entity
            # Assign to artist
            pass
    
    def get_shot_status(self, shot_name):
        """Get shot progress"""
        # Query OpenPype for task statuses
        pass
```

---

## 🚀 DEPLOYMENT

### Production Deployment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ayon
      POSTGRES_USER: ayon
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 2G

  ayon-server:
    image: ynput/ayon-server:latest
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=ayon
      - POSTGRES_USER=ayon
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - AYON_SECRET=${AYON_SECRET}
      - AYON_ADMIN_EMAIL=${ADMIN_EMAIL}
      - AYON_ADMIN_PASSWORD=${ADMIN_PASSWORD}
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  ayon-frontend:
    image: ynput/ayon-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - ayon-server

volumes:
  postgres_data:
```

---

## 🔗 LINKS

- **OpenPype:** https://openpype.io/
- **AYON:** https://ayon.ynput.cloud/
- **OpenPype Docs:** https://openpype.io/docs/
- **AYON Docs:** https://docs.ayon.ynput.cloud/
- **GitHub:** https://github.com/ynput/openpype / https://github.com/ynput/ayon
- **Discord:** https://discord.gg/openpype

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/pipeline/openpype_ayon.md` |
| Russian | `multilang/ru/pipeline/openpype_ayon.md` |