---
id: setup_11_touchdesigner
lang: ru
category: setups
status: full
---
# SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS

**ID:** SETUP-11 | **Type:** Realtime Visuals / Interactive | **Difficulty:** ⭐⭐⭐ | **Time:** 30-60 min

---

## 🎯 ЦЕЛЬ
Настроить realtime связь Blender ↔ TouchDesigner для интерактивных визуалов, VJ, инсталляций

---

## 🎯 АРХИТЕКТУРА

```
Blender (Content)          OSC/NDI/Spout          TouchDesigner (Realtime)
┌─────────────────┐       OSC/UDP/TCP          ┌─────────────────┐
│  Models/Anim    │ ───────────────────────▶  │  Real-time    │
│  Cameras/Lights │  NDI/Spout (Video)        │  Render/Comp  │
│  Geometry Nodes │  Shared Memory            │  - VJ         │
│  Shaders        │  OSC (Params)             │  - Interactive│
└─────────────────┘                           └─────────────────┘
```

---

## 🔧 ОСНОВНЫЕ ПРОТОКОЛЫ

| Протокол | Задержка | Пропускная способность | Use Case |
|----------|----------|------------------------|----------|
| **OSC** | ~1-5ms | Низкая | Параметры, триггеры, синк |
| **NDI** | ~1-2 кадра | Высокая (4K60) | Видео поток |
| **Spout** | ~0-1 кадр | Высокая (GPU-direct) | Windows GPU sharing |
| **Shared Memory** | ~0ms | Очень высокая | Текстуры/геометрия |
| **WebSocket** | ~5-10ms | Средняя | Web/Remote |
| **ZeroMQ** | ~1-2ms | Высокая | Высоконагруженные |

---

## 🔧 ОСНОВНЫЕ МЕТОДЫ СВЯЗИ

### 1. OSC (Open Sound Control) - Основной
```python
# blender_osc_sender.py
import bpy
import socket
import json
from pythonosc import udp_client

class BlenderOSC:
    def __init__(self, ip="127.0.0.1", port=7000):
        self.client = udp_client.SimpleUDPClient(ip, port)
    
    def send_transform(self, obj_name, location, rotation, scale):
        """Отправить трансформ объекта"""
        self.client.send_message(f"/blender/object/{obj_name}/transform", [
            *location, *rotation, *scale
        ])
    
    def send_camera(self, cam_name, fov, aspect, clip_start, clip_end):
        """Отправить параметры камеры"""
        self.client.send_message(f"/blender/camera/{cam_name}", [
            fov, aspect, clip_start, clip_end
        ])
    
    def send_custom(self, address, *args):
        """Произвольное сообщение"""
        self.client.send_message(address, list(args))
    
    def send_frame_sync(self, frame, fps):
        """Синхронизация кадра"""
        self.client.send_message("/blender/sync", [frame, fps])

# Автоматическая отправка при изменении кадра
def setup_frame_sync():
    osc = BlenderOSC()
    
    def frame_change_handler(scene):
        osc.send_frame_sync(scene.frame_current, scene.render.fps)
    
    bpy.app.handlers.frame_change_post.append(frame_change_handler)

# Регистрация
bpy.app.handlers.load_post.append(lambda _: setup_frame_sync())
```

### TouchDesigner OSC In
```python
# TouchDesigner OSC In DAT / OSC In CHOP
# Network: 0.0.0.0:7000
# Callbacks:
def onOSCMessage(dat, rowIndex, message, address, args):
    if address == "/blender/object/*/transform":
        # Parse: /blender/object/Cube/transform [x, y, z, rx, ry, rz, sx, sy, sz]
        obj_name = address.split('/')[-2]
        vals = args
        # Apply to TouchDesigner COMP/Geo
        op(f'/scene/{obj_name}').par.tx = vals[0]
        op(f'/scene/{obj_name}').par.ty = vals[1]
        op(f'/scene/{obj_name}').par.tz = vals[2]
```

---

## 📹 NDI (Network Device Interface)

### Blender NDI Output
```python
# blender_ndi_sender.py
# Требует: pip install ndi-python (или Blender NDI Addon)

import bpy
import NDIlib as ndi

class BlenderNDI:
    def __init__(self, source_name="Blender_Output"):
        # Инициализация NDI
        if not ndi.initialize():
            raise RuntimeError("NDI init failed")
        
        create_desc = ndi.SendCreate()
        create_desc.ndi_name = source_name
        create_desc.clock_video = True
        create_desc.clock_audio = False
        
        self.sender = ndi.send_create(create_desc)
        if not self.sender:
            raise RuntimeError("NDI sender creation failed")
    
    def send_frame(self, image_data, width, height, frame_rate=30):
        """Отправить кадр (numpy array RGBA)"""
        video_frame = ndi.VideoFrameV2()
        video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_RGBA
        video_frame.xres = width
        video_frame.yres = height
        video_frame.frame_rate_N = frame_rate
        video_frame.frame_rate_D = 1
        video_frame.p_data = image_data.ctypes.data
        video_frame.line_stride_in_bytes = width * 4
        
        ndi.send_send_video_v2(self.sender, video_frame)
    
    def send_from_viewport(self, viewport_name="Viewport"):
        """Захват viewport и отправка"""
        # Используем bpy.ops.render.opengl для захвата
        pass

# Аддон для Blender (UI)
class NDI_PT_panel(bpy.types.Panel):
    bl_label = "NDI Output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NDI'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "ndi_source_name")
        layout.operator("ndi.start_stream")
        layout.operator("ndi.stop_stream")

class NDI_OT_start(bpy.types.Operator):
    bl_idname = "ndi.start_stream"
    bl_label = "Start NDI Stream"
    
    def execute(self, context):
        global ndi_sender
        ndi_sender = BlenderNDI(context.scene.ndi_source_name)
        self.report({'INFO'}, "NDI Stream Started")
        return {'FINISHED'}

class NDI_OT_stop(bpy.types.Operator):
    bl_idname = "ndi.stop_stream"
    bl_label = "Stop NDI Stream"
    
    def execute(self, context):
        global ndi_sender
        if ndi_sender:
            ndi_sender.destroy()
        return {'FINISHED'}
```

### TouchDesigner NDI In
```python
# TouchDesigner: NDI In TOP
# Network: Auto-detect или ручной IP
# Format: Auto / RGBA / RGB / Alpha
# Frame Rate: Match Source / Force 60/30
# Deinterlace: Off / On
```

---

## 🖥️ SPOUT (Windows Only - GPU Direct)

### Blender Spout Sender
```python
# blender_spout_sender.py
# Требует: Spout SDK + pySpout (pip install pySpout)

import SpoutSDK
import bpy
import numpy as np

class SpoutSender:
    def __init__(self, sender_name="Blender_Output", width=1920, height=1080):
        self.width = width
        self.height = height
        self.sender = SpoutSDK.SpoutSender()
        self.sender.CreateSender(sender_name, width, height, SpoutSDK.SPOUT_RGBA)
    
    def send_texture(self, texture_id):
        """Отправить OpenGL текстуру (GPU-to-GPU)"""
        # Прямая передача текстуры через общую память GPU
        pass
    
    def send_viewport(self, viewport_name="Viewport"):
        # Захват viewport как текстура и отправка
        pass
```

### TouchDesigner Spout In
```python
# TouchDesigner: Spout In TOP
# Sender Name: Blender_Output
# Format: RGBA / RGB
# Auto Detect Size: On
```

---

## 🔄 SHARED MEMORY (Fastest)

### Python Shared Memory
```python
# shared_memory_bridge.py
import mmap
import struct
import numpy as np
from multiprocessing import shared_memory

class SharedMemoryBridge:
    def __init__(self, name="blender_td_bridge", size=1920*1080*4*2):  # RGBA 1920x1080 x2 buffers
        self.shm = shared_memory.SharedMemory(
            create=True, size=size, name=name
        )
        self.buffer = np.ndarray(
            (1080, 1920, 4), dtype=np.uint8, buffer=self.shm.buf
        )
        self.frame_lock = False
    
    def write_frame(self, frame_data):
        """Запись кадра (numpy array RGBA)"""
        if not self.frame_lock:
            self.frame_lock = True
            self.buffer[:] = frame_data[:]
            self.frame_lock = False
    
    def read_frame(self):
        """Чтение кадра (non-blocking)"""
        if not self.frame_lock:
            return self.buffer.copy()
        return None
    
    def cleanup(self):
        self.shm.close()
        self.shm.unlink()

# Blender side
def write_to_shared_memory(image_data):
    shm = shared_memory.SharedMemory(name="blender_td_bridge")
    buffer = np.ndarray((1080, 1920, 4), dtype=np.uint8, buffer=shm.buf)
    buffer[:] = image_data[:]
    shm.close()

# TouchDesigner side (Python in TOP)
"""
import numpy as np
from multiprocessing import shared_memory

shm = shared_memory.SharedMemory(name="blender_td_bridge")
buffer = np.ndarray((1080, 1920, 4), dtype=np.uint8, buffer=shm.buf)
# Use buffer as TOP texture
"""
```

---

## 🎮 WEBSOCKET (Remote/Network)

### Blender WebSocket Server
```python
# blender_ws_server.py
import asyncio
import websockets
import json
import bpy
import asyncio

class BlenderWSServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
    
    async def handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data, websocket)
        finally:
            self.clients.remove(websocket)
    
    async def handle_message(self, data, ws):
        msg_type = data.get("type")
        
        if msg_type == "get_scene":
            await self.send_scene_info(ws)
        elif msg_type == "set_transform":
            self.set_object_transform(data)
        elif msg_type == "set_camera":
            self.set_camera(data)
        elif msg_type == "render":
            await self.render_frame(ws, data)
    
    async def send_scene_info(self, ws):
        objects = [
            {"name": o.name, "type": o.type, "location": list(o.location)}
            for o in bpy.data.objects
        ]
        await ws.send(json.dumps({"type": "scene_info", "objects": objects}))
    
    async def broadcast(self, message):
        if self.clients:
            await asyncio.gather(*[c.send(json.dumps(message)) for c in self.clients])

# TouchDesigner WebSocket Client
"""
// TouchDesigner WebSocket Client (WebSocket DAT)
var ws = new WebSocket("ws://localhost:8765");
ws.onmessage = function(event) {
    var data = JSON.parse(event.data);
    if (data.type == "scene_info") {
        updateScene(data.objects);
    }
});
"""
```

---

## 🎯 SYNC STRATEGIES

| Метод | Синхронизация | Латентность | Надежность |
|-------|---------------|-------------|------------|
| **Frame Counter** | Frame Number | Низкая | Высокая |
| **Timecode (SMPTE)** | Timecode | Средняя | Высокая |
| **Genlock/Blackburst** | Hardware Sync | Нулевая | Максимальная |
| **NTP/PTP** | Network Time | ~1ms | Высокая |
| **Frame Counter + Drift Correction** | Frame + Drift | Низкая | Высокая |

### Frame Sync Implementation
```python
# blender_frame_sync.py
import bpy
import time

class FrameSync:
    def __init__(self):
        self.frame_offset = 0
        self.last_frame = 0
        self.drift_threshold = 2  # frames
    
    def sync_frame(self, external_frame):
        """Синхронизация с внешним источником"""
        current = bpy.context.scene.frame_current
        drift = external_frame - current
        
        if abs(drift) > self.drift_threshold:
            # Hard sync
            bpy.context.scene.frame_set(external_frame)
            self.frame_offset = 0
        else:
            # Soft sync (drift correction)
            self.frame_offset = drift
    
    def get_synced_frame(self):
        return bpy.context.scene.frame_current + self.frame_offset

# Auto-sync on frame change
def frame_change_handler(scene):
    global frame_sync
    if hasattr(frame_sync, 'external_frame'):
        frame_sync.sync_frame(frame_sync.external_frame)

bpy.app.handlers.frame_change_post.append(frame_change_handler)
```

---

## 📊 PERFORMANCE COMPARISON

| Method | Latency | Throughput | Setup | Platform |
|--------|---------|------------|-------|----------|
| **Shared Memory** | ~0ms | ~8 GB/s | Complex | Linux/Win |
| **Spout** | 0-1 frame | ~6 GB/s | Medium | Windows |
| **NDI** | 1-2 frames | ~3 GB/s | Easy | All |
| **OSC** | 1-5ms | ~1 MB/s | Easy | All |
| **WebSocket** | 5-10ms | ~100 MB/s | Easy | All |
| **Shared Memory + GPU** | ~0ms | ~16 GB/s | Complex | Linux/Win |

---

## 🔗 LINKS

- **NDI SDK:** https://ndi.video/for-developers/
- **Spout SDK:** https://spout.zeal.co/
- **TouchDesigner Python:** https://docs.derivative.ca/Python
- **python-osc:** https://pypi.org/project/python-osc/
- **NDI Python:** https://github.com/Palakis/pyNDI

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_11_touchdesigner.md` |
| Russian | `multilang/ru/setups/setup_11_touchdesigner.md` |

---

## FULL GUIDE

### Протоколы
| Протокол | Задержка | Назначение |
|----------|----------|------------|
| OSC | 1–5ms | Параметры, триггеры |
| NDI | 1–2 кадра | Видео поток |
| Spout | 0–1 кадр | GPU-текстуры (Windows) |
| Shared Memory | ~0 | Текстуры/геометрия |

### Шаги
1. Blender: OSC-аддон, порт 7000, отправка трансформов выбранных объектов.
2. TouchDesigner: OSC In CHOP → связать с параметрами COMP.
3. Видео: NDI Out (Blender) → NDI In (TD) или Spout пара.
4. Синхронизация кадров: frame counter + drift correction (порог 2 кадра).

### Проверка
- [ ] Параметры двигаются без залипаний
- [ ] Видео без тиринга, задержка измерена

