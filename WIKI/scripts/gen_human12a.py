#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Human translations chunk A: setup_02 + P02 -> es/de/zh. Code blocks identical, prose translated."""
from pathlib import Path
W = Path(r"C:\BLENDER ai\WIKI") / "multilang"

SETUP02 = {
"es": """---
id: setup_02_genesiscore_local
lang: es
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: human
---
# CONFIGURACIÓN 02: GENESISCORE LOCAL (OLLAMA)

**ID:** SETUP-02 | **Tipo:** Integración LLM local | **Dificultad:** ⭐⭐ | **Tiempo:** 15-30 min

---

## 🎯 OBJETIVO
Configurar GenesisCore para trabajar con LLM locales vía Ollama (privacidad, gratis, sin conexión)

---

## 📋 REQUISITOS PREVIOS

| Componente | Versión | Estado |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Obligatorio |
| **Ollama** | latest | ✅ Obligatorio |
| **RAM** | 16GB+ | 🟡 Recomendado |
| **VRAM** | 8GB+ | 🟡 Para modelos 7B+ |

---

## 🪟 INSTALACIÓN EN WINDOWS

### 1. Instalar Ollama
```powershell
# Descargar e instalar
winget install Ollama.Ollama

# O desde el sitio oficial
# https://ollama.com/download/windows

# Comprobar
ollama --version
ollama list
```

### 2. Descargar modelos para coding/Blender
```powershell
# Mejores modelos para Blender Python (por prioridad)
ollama pull codellama:13b        # El mejor para código, 7.3GB
ollama pull deepseek-coder:6.7b  # Excelente para Python, 3.8GB
ollama pull qwen2.5-coder:7b     # Nuevo, rápido, 4.7GB
ollama pull llama3.2:3b          # Ligero, rápido, 2.0GB

# Comprobar
ollama list
```

### 3. Iniciar el servidor Ollama
```powershell
# Debe ejecutarse en segundo plano (autostart al instalar)
# Comprobar:
curl http://localhost:11434/api/tags

# Si no funciona:
ollama serve
```

---

## 🔧 CONFIGURACIÓN DE GENESISCORE

### 1. Instalar el addon (si aún no)
```bash
# En Blender: Edit → Preferences → Add-ons → Install from ZIP
# Elegir: GenesisCore-main.zip
# Activar: GenesisCore
```

### 2. Configurar el proveedor
```
N-Panel → pestaña GenesisCore:
1. Provider: ▼ Ollama
2. Base URL: http://localhost:11434/v1  (¡importante: /v1 al final!)
3. API Key: (dejar vacío para Ollama)
4. Pulsar "Fetch Models"
4. Elegir modelo: codellama:13b / deepseek-coder:6.7b / qwen2.5-coder:7b
5. Tool Modules: activar todos (Shift+Click)
6. Save Config
7. Connect
```

### 3. Ajustes del modelo (recomendados)
```json
{
  "provider": "Ollama",
  "base_url": "http://localhost:11434/v1",
  "model": "codellama:13b",
  "temperature": 0.1,
  "top_p": 0.9,
  "max_tokens": 4096,
  "use_history": true
}
```

---

## 🔧 OPTIMIZACIÓN DEL RENDIMIENTO

### GPU Offloading (NVIDIA)
```powershell
# Ollama usa la GPU automáticamente si hay CUDA
# Comprobar:
ollama run codellama:13b "test"
# Debe mostrar: "using GPU" en los logs

# Forzar GPU layers:
# En variables de entorno:
OLLAMA_NUM_GPU=999
OLLAMA_GPU_LAYERS=999
```

### Optimización de memoria
```yaml
# En ajustes de GenesisCore:
use_history: false          # Desactivar historial para ahorrar tokens
max_tokens: 2048            # Limitar la longitud de respuesta
temperature: 0.1            # Respuestas deterministas
```

### Cuantización (si hay poca VRAM)
```powershell
# Usar versiones cuantizadas:
ollama pull codellama:13b-q4_K_M   # 4-bit, 7.3GB → 4.7GB
ollama pull deepseek-coder:6.7b-q4_K_M  # 3.8GB → 2.5GB
```

---

## 🧪 PRUEBAS

### Prueba rápida en el chat de GenesisCore
```
"Crea un cubo 'TestCube' en la posición (1, 2, 3) con material rojo"
```

### Resultado esperado
1. El agente analiza la petición
2. Llama a `create_object` + `set_material`
3. En Blender aparece un cubo en (1, 2, 3) con material rojo

---

## 🔧 SOLUCIÓN DE PROBLEMAS

| Problema | Solución |
|----------|---------|
| `Connection refused` | Ollama no está en marcha → `ollama serve` |
| `Model not found` | `ollama pull <model_name>` |
| `Out of memory` | Usar un modelo menor (3b/7b) o cuantización q4 |
| `Slow response` | Activar GPU offloading, reducir `max_tokens` |
| `Base URL error` | Verificar `http://localhost:11434/v1` (¡con /v1!) |

---

## 🔗 ENLACES

- **Modelos Ollama:** https://ollama.com/library
- **Repo GenesisCore:** https://github.com/AIGODLIKE/GenesisCore
- **Setup 01:** [blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Siguiente:** [Setup 03: Dream Textures](../setups/setup_03_dream_textures.md)
""",
"de": """---
id: setup_02_genesiscore_local
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: human
---
# SETUP 02: GENESISCORE LOKAL (OLLAMA)

**ID:** SETUP-02 | **Typ:** Lokale LLM-Integration | **Schwierigkeit:** ⭐⭐ | **Zeit:** 15-30 Min

---

## 🎯 ZIEL
GenesisCore für lokale LLMs via Ollama einrichten (Privatsphäre, kostenlos, offline)

---

## 📋 VORAUSSETZUNGEN

| Komponente | Version | Status |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Erforderlich |
| **Ollama** | latest | ✅ Erforderlich |
| **RAM** | 16GB+ | 🟡 Empfohlen |
| **VRAM** | 8GB+ | 🟡 Für 7B+ Modelle |

---

## 🪟 WINDOWS-INSTALLATION

### 1. Ollama installieren
```powershell
# Herunterladen und installieren
winget install Ollama.Ollama

# Oder von der offiziellen Website
# https://ollama.com/download/windows

# Prüfen
ollama --version
ollama list
```

### 2. Modelle für Coding/Blender laden
```powershell
# Beste Modelle für Blender Python (nach Priorität)
ollama pull codellama:13b        # Bestes für Code, 7.3GB
ollama pull deepseek-coder:6.7b  # Exzellent für Python, 3.8GB
ollama pull qwen2.5-coder:7b     # Neu, schnell, 4.7GB
ollama pull llama3.2:3b          # Leicht, schnell, 2.0GB

# Prüfen
ollama list
```

### 3. Ollama-Server starten
```powershell
# Sollte im Hintergrund laufen (Autostart bei Installation)
# Prüfen:
curl http://localhost:11434/api/tags

# Falls nicht:
ollama serve
```

---

## 🔧 GENESISCORE-EINRICHTUNG

### 1. Addon installieren (falls noch nicht)
```bash
# In Blender: Edit → Preferences → Add-ons → Install from ZIP
# Wählen: GenesisCore-main.zip
# Aktivieren: GenesisCore
```

### 2. Provider einrichten
```
N-Panel → Reiter GenesisCore:
1. Provider: ▼ Ollama
2. Base URL: http://localhost:11434/v1  (wichtig: /v1 am Ende!)
3. API Key: (leer lassen für Ollama)
4. "Fetch Models" klicken
4. Modell wählen: codellama:13b / deepseek-coder:6.7b / qwen2.5-coder:7b
5. Tool Modules: alle aktivieren (Shift+Click)
6. Save Config
7. Connect
```

### 3. Modell-Einstellungen (empfohlen)
```json
{
  "provider": "Ollama",
  "base_url": "http://localhost:11434/v1",
  "model": "codellama:13b",
  "temperature": 0.1,
  "top_p": 0.9,
  "max_tokens": 4096,
  "use_history": true
}
```

---

## 🔧 LEISTUNGSOPTIMIERUNG

### GPU Offloading (NVIDIA)
```powershell
# Ollama nutzt die GPU automatisch bei CUDA
# Prüfen:
ollama run codellama:13b "test"
# Sollte zeigen: "using GPU" in den Logs

# GPU-Layer erzwingen:
# In Umgebungsvariablen:
OLLAMA_NUM_GPU=999
OLLAMA_GPU_LAYERS=999
```

### Speicheroptimierung
```yaml
# In GenesisCore-Einstellungen:
use_history: false          # Verlauf deaktivieren um Tokens zu sparen
max_tokens: 2048            # Antwortlänge begrenzen
temperature: 0.1            # Deterministische Antworten
```

### Quantisierung (bei wenig VRAM)
```powershell
# Quantisierte Versionen nutzen:
ollama pull codellama:13b-q4_K_M   # 4-bit, 7.3GB → 4.7GB
ollama pull deepseek-coder:6.7b-q4_K_M  # 3.8GB → 2.5GB
```

---

## 🧪 TESTS

### Schnelltest im GenesisCore-Chat
```
"Erstelle einen Würfel 'TestCube' an Position (1, 2, 3) mit rotem Material"
```

### Erwartetes Ergebnis
1. Der Agent analysiert die Anfrage
2. Ruft `create_object` + `set_material` auf
3. In Blender erscheint ein Würfel bei (1, 2, 3) mit rotem Material

---

## 🔧 FEHLERBEHEBUNG

| Problem | Lösung |
|----------|---------|
| `Connection refused` | Ollama läuft nicht → `ollama serve` |
| `Model not found` | `ollama pull <model_name>` |
| `Out of memory` | Kleineres Modell nutzen (3b/7b) oder q4-Quantisierung |
| `Slow response` | GPU-Offloading aktivieren, `max_tokens` senken |
| `Base URL error` | Prüfen: `http://localhost:11434/v1` (mit /v1!) |

---

## 🔗 LINKS

- **Ollama-Modelle:** https://ollama.com/library
- **GenesisCore-Repo:** https://github.com/AIGODLIKE/GenesisCore
- **Setup 01:** [blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Nächster:** [Setup 03: Dream Textures](../setups/setup_03_dream_textures.md)
""",
"zh": """---
id: setup_02_genesiscore_local
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: human
---
# 配置 02：本地 GENESISCORE (OLLAMA)

**ID:** SETUP-02 | **类型:** 本地 LLM 集成 | **难度:** ⭐⭐ | **用时:** 15-30 分钟

---

## 🎯 目标
配置 GenesisCore 使用本地 LLM（Ollama）：隐私、免费、离线

---

## 📋 前置要求

| 组件 | 版本 | 状态 |
|------|------|------|
| **Blender** | 4.0+ | ✅ 必需 |
| **Ollama** | latest | ✅ 必需 |
| **RAM** | 16GB+ | 🟡 推荐 |
| **VRAM** | 8GB+ | 🟡 7B+ 模型需要 |

---

## 🪟 WINDOWS 安装

### 1. 安装 Ollama
```powershell
# 下载并安装
winget install Ollama.Ollama

# 或从官网下载
# https://ollama.com/download/windows

# 检查
ollama --version
ollama list
```

### 2. 下载代码/Blender 模型
```powershell
# 最适合 Blender Python 的模型（按优先级）
ollama pull codellama:13b        # 最适合代码，7.3GB
ollama pull deepseek-coder:6.7b  # Python 极佳，3.8GB
ollama pull qwen2.5-coder:7b     # 新，速度快，4.7GB
ollama pull llama3.2:3b          # 轻量，速度快，2.0GB

# 检查
ollama list
```

### 3. 启动 Ollama 服务
```powershell
# 应以后台运行（安装时自动启动）
# 检查：
curl http://localhost:11434/api/tags

# 如果不行：
ollama serve
```

---

## 🔧 GENESISCORE 设置

### 1. 安装插件（如尚未安装）
```bash
# 在 Blender: Edit → Preferences → Add-ons → Install from ZIP
# 选择: GenesisCore-main.zip
# 启用: GenesisCore
```

### 2. 配置服务商
```
N 面板 → GenesisCore 选项卡：
1. Provider: ▼ Ollama
2. Base URL: http://localhost:11434/v1  （重要：末尾要有 /v1！）
3. API Key: （Ollama 留空）
4. 点击 "Fetch Models"
4. 选择模型: codellama:13b / deepseek-coder:6.7b / qwen2.5-coder:7b
5. Tool Modules: 全部启用（Shift+Click）
6. Save Config
7. Connect
```

### 3. 模型设置（推荐）
```json
{
  "provider": "Ollama",
  "base_url": "http://localhost:11434/v1",
  "model": "codellama:13b",
  "temperature": 0.1,
  "top_p": 0.9,
  "max_tokens": 4096,
  "use_history": true
}
```

---

## 🔧 性能优化

### GPU Offloading (NVIDIA)
```powershell
# 有 CUDA 时 Ollama 自动使用 GPU
# 检查：
ollama run codellama:13b "test"
# 日志中应显示 "using GPU"

# 强制启用 GPU layers:
# 在环境变量中：
OLLAMA_NUM_GPU=999
OLLAMA_GPU_LAYERS=999
```

### 内存优化
```yaml
# 在 GenesisCore 设置中：
use_history: false          # 关闭历史以节省 token
max_tokens: 2048            # 限制回答长度
temperature: 0.1            # 确定性回答
```

### 量化（显存不足时）
```powershell
# 使用量化版本：
ollama pull codellama:13b-q4_K_M   # 4-bit，7.3GB → 4.7GB
ollama pull deepseek-coder:6.7b-q4_K_M  # 3.8GB → 2.5GB
```

---

## 🧪 测试

### 在 GenesisCore 聊天中快速测试
```
"在位置 (1, 2, 3) 创建立方体 'TestCube'，红色材质"
```

### 预期结果
1. 智能体分析请求
2. 调用 `create_object` + `set_material`
3. Blender 中在 (1, 2, 3) 出现红色立方体

---

## 🔧 故障排除

| 问题 | 解决方法 |
|------|----------|
| `Connection refused` | Ollama 未运行 → `ollama serve` |
| `Model not found` | `ollama pull <model_name>` |
| `Out of memory` | 用更小的模型 (3b/7b) 或 q4 量化 |
| `Slow response` | 启用 GPU offloading，减小 `max_tokens` |
| `Base URL error` | 检查 `http://localhost:11434/v1`（要有 /v1！） |

---

## 🔗 相关链接

- **Ollama 模型:** https://ollama.com/library
- **GenesisCore 仓库:** https://github.com/AIGODLIKE/GenesisCore
- **配置 01:** [blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **下一个:** [Setup 03: Dream Textures](../setups/setup_03_dream_textures.md)
""",
}

P02 = {
"es": """---
id: 02_boolean_operations
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human
---
# P02: OPERACIONES BOOLEANAS

**ID:** P02 | **Clúster:** Geometry Basics | **Dificultad:** ⭐⭐ | **Tags:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 OBJETIVO
Operaciones booleanas (Difference, Union, Intersect) entre objetos vía MCP

---

## 📝 PROMPT

```
Ejecuta la operación booleana [OPERATION] entre "[OBJECT_A]" (base) y "[OBJECT_B]" (herramienta).
Operaciones: DIFFERENCE (restar), UNION (unir), INTERSECT (intersección).
Resultado: el objeto A se modifica, el objeto B puede eliminarse.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# Configuración
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# Asegurar OBJECT mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Seleccionar objetos
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# Añadir modificador Boolean
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 'FAST' para geometrías simples

# Aplicar
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# Eliminar herramienta (opcional)
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 OPERACIONES

| Operación | Resultado visual | Caso de uso |
|----------|---------------------|----------|
| **DIFFERENCE** | A menos B | Ventanas, puertas, agujeros, ranuras |
| **UNION** | A más B | Unir piezas, fusionar mallas |
| **INTERSECT** | Solo intersección | Máscaras, recorte de formas |

---

## 💡 PATRONES AVANZADOS

### Booleanos múltiples (a la vez)
```python
# Varias restas en una pasada
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# Aplicar todos
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Limpieza
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### Cuidado con las normales
```python
# Verificar y corregir normales antes del booleano
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ PROBLEMAS FRECUENTES

| Problema | Causa | Solución |
|--------|---------|---------|
| Resultado vacío | Normales dentro/fuera | `Mesh > Normals > Recalculate Outside` |
| Artefactos | Aristas no-manifold | `Select > Select All by Trait > Non-Manifold` → corregir |
| Lento en mallas complejas | Muchos polígonos | Usa `DECIMATE` antes, o solver `FAST` |
| El objeto desaparece | Intersección vacía | Verifica la posición de los objetos |

---

## 🔗 ENLACES

- **Casos:** [Case 01: ArchViz Interior](../cases/case_01_archviz_interior.md) — ventanas/puertas en paredes
- **Flujos:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Prompts relacionados:** [P01 Primitives](./01_geometry_basics.md), [P03 Modifiers Stack](./03_modifiers_stack.md)
- **Siguiente:** [P03: Modifiers Stack](./03_modifiers_stack.md)
""",
"de": """---
id: 02_boolean_operations
lang: de
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human
---
# P02: BOOLESCHE OPERATIONEN

**ID:** P02 | **Cluster:** Geometry Basics | **Schwierigkeit:** ⭐⭐ | **Tags:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 ZIEL
Boolesche Operationen (Difference, Union, Intersect) zwischen Objekten via MCP

---

## 📝 PROMPT

```
Führe boolesche Operation [OPERATION] zwischen "[OBJECT_A]" (Basis) und "[OBJECT_B]" (Werkzeug) aus.
Operationen: DIFFERENCE (subtrahieren), UNION (vereinigen), INTERSECT (Schnittmenge).
Ergebnis: Objekt A wird modifiziert, Objekt B kann gelöscht werden.
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# Setup
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# OBJECT mode sicherstellen
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Objekte wählen
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# Boolean-Modifier hinzufügen
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 'FAST' für einfache Geometrien

# Anwenden
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# Werkzeug löschen (optional)
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 OPERATIONEN

| Operation | Visuelles Ergebnis | Use Case |
|----------|---------------------|----------|
| **DIFFERENCE** | A minus B | Fenster, Türen, Öffnungen, Nuten |
| **UNION** | A plus B | Teile vereinen, Meshes fusionieren |
| **INTERSECT** | Nur Schnittmenge | Masken, Formen ausschneiden |

---

## 💡 FORTGESCHRITTENE MUSTER

### Mehrere Booleans (gleichzeitig)
```python
# Mehrere Subtraktionen in einem Durchgang
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# Alle anwenden
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Aufräumen
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### Vorsicht mit Normalen
```python
# Normalen vor Boolean prüfen und korrigieren
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ HÄUFIGE PROBLEME

| Problem | Ursache | Lösung |
|--------|---------|---------|
| Leeres Ergebnis | Normalen innen/außen | `Mesh > Normals > Recalculate Outside` |
| Geometrie-Artefakte | Non-manifold Kanten | `Select > Select All by Trait > Non-Manifold` → fixen |
| Langsam bei komplexen Meshes | Viele Polygone | `DECIMATE` vorher nutzen, oder `FAST`-Solver |
| Objekt verschwindet | Leere Schnittmenge | Positionen der Objekte prüfen |

---

## 🔗 LINKS

- **Fälle:** [Case 01: ArchViz Interior](../cases/case_01_archviz_interior.md) — Fenster/Türen in Wänden
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Verwandte Prompts:** [P01 Primitives](./01_geometry_basics.md), [P03 Modifiers Stack](./03_modifiers_stack.md)
- **Nächster:** [P03: Modifiers Stack](./03_modifiers_stack.md)
""",
"zh": """---
id: 02_boolean_operations
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human
---
# P02：布尔运算

**ID:** P02 | **类别:** Geometry Basics | **难度:** ⭐⭐ | **标签:** #boolean #modeling #modifiers #difference #union #intersect

---

## 🎯 目标
通过 MCP 在对象间执行布尔运算（Difference、Union、Intersect）

---

## 📝 提示词

```
在 "[OBJECT_A]"（基础）和 "[OBJECT_B]"（工具）之间执行布尔运算 [OPERATION]。
运算：DIFFERENCE（相减）、UNION（合并）、INTERSECT（相交）。
结果：对象 A 被修改，对象 B 可以删除。
```

---

## 🔧 MCP: `execute_blender_code`

```python
import bpy

# 设置
obj_a = bpy.data.objects.get("Wall")
obj_b = bpy.data.objects.get("Window_Cutout")

if not obj_a or not obj_b:
    raise ValueError("Objects not found")

# 确保 OBJECT 模式
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# 选择对象
bpy.ops.object.select_all(action='DESELECT')
obj_a.select_set(True)
obj_b.select_set(True)
bpy.context.view_layer.objects.active = obj_a

# 添加布尔修改器
bool_mod = obj_a.modifiers.new(name="Bool_Window", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'  # 'UNION', 'INTERSECT'
bool_mod.object = obj_b
bool_mod.solver = 'EXACT'  # 简单几何用 'FAST'

# 应用
bpy.ops.object.modifier_apply(modifier="Bool_Window")

# 删除工具对象（可选）
bpy.data.objects.remove(obj_b, do_unlink=True)

print(f"Boolean DIFFERENCE applied. {obj_a.name} modified.")
```

---

## 📊 运算类型

| 运算 | 可视结果 | 用例 |
|------|----------|------|
| **DIFFERENCE** | A 减 B | 门窗、开孔、凹槽 |
| **UNION** | A 加 B | 合并部件、融合网格 |
| **INTERSECT** | 仅相交部分 | 遮罩、形状裁剪 |

---

## 💡 高级模式

### 多个布尔（一次完成）
```python
# 一次多个相减
cutters = [bpy.data.objects.get(f"Cutter_{i}") for i in range(5)]
for cutter in cutters:
    mod = wall.modifiers.new(f"Bool_{cutter.name}", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'

# 全部应用
for mod in list(wall.modifiers):
    if mod.type == 'BOOLEAN':
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier=mod.name)

# 清理
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)
```

### 注意法线
```python
# 布尔运算前检查并修复法线
bpy.context.view_layer.objects.active = obj_a
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## ⚠️ 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 结果为空 | 法线内外反了 | `Mesh > Normals > Recalculate Outside` |
| 几何伪影 | 非流形边 | `Select > Select All by Trait > Non-Manifold` → 修复 |
| 复杂网格很慢 | 面数太多 | 先用 `DECIMATE`，或用 `FAST` solver |
| 对象消失 | 相交为空 | 检查对象位置 |

---

## 🔗 相关链接

- **案例:** [Case 01: ArchViz Interior](../cases/case_01_archviz_interior.md) — 墙体门窗
- **工作流:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **相关提示词:** [P01 Primitives](./01_geometry_basics.md), [P03 Modifiers Stack](./03_modifiers_stack.md)
- **下一个:** [P03: Modifiers Stack](./03_modifiers_stack.md)
""",
}

for lang, text in SETUP02.items():
    p = W / lang / "setups" / "setup_02_genesiscore_local.md"
    p.write_text(text, encoding="utf-8")
for lang, text in P02.items():
    p = W / lang / "prompts" / "02_boolean_operations.md"
    p.write_text(text, encoding="utf-8")
print("OK chunk A: setup_02 x3 + P02 x3")
