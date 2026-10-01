---
id: setup_01_blender_mcp_basic
lang: es
orig_lang: ru
category: setups
type: setup
difficulty: 1
translation: human
---
# CONFIGURACIÓN 01: BLENDER-MCP BÁSICO

**ID:** SETUP-01 | **Tipo:** Infraestructura central | **Dificultad:** ⭐ | **Tiempo:** 10-15 min

---

## 🎯 OBJETIVO
Instalar y configurar blender-mcp para trabajar con agentes IDE (OpenCode, Cursor, VS Code, Codex, Claude Desktop)

---

## 📋 REQUISITOS PREVIOS

| Componente | Versión | Estado |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Obligatorio |
| **Python** | 3.10+ | ✅ Incluido en Blender |
| **uv** | latest | ✅ Obligatorio |
| **Git** | latest | ⚠️ Opcional |

---

## 🪟 INSTALACIÓN EN WINDOWS (PASO A PASO)

### 1. Instalar uv
```powershell
# PowerShell como administrador
irm https://astral.sh/uv/install.ps1 | iex

# Reiniciar la terminal
# Verificar
uv --version
uvx --version
```

### 2. Instalar el addon blender-mcp
```powershell
# Instalación automática en Blender
uvx blender-mcp install-addon

# Verificar la ruta
uvx blender-mcp addon-paths
# Debe mostrar: C:\Users\<USER>\AppData\Roaming\Blender Foundation\Blender\4.x\scripts\addons\blender_mcp.py
```

### 3. Configurar PATH (si no se encuentra uvx)
```powershell
# Encontrar uvx
where uvx
# Normalmente: C:\Users\<USER>\.local\bin\uvx.exe

# Añadir al PATH de usuario
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
# Reiniciar terminal/IDE
```

---

## 🔧 CONFIGURACIÓN DE BLENDER

### 1. Activar el addon
```
Edit → Preferences → Add-ons
Buscar: "MCP for Blender"
☑ Interface: MCP for Blender
```

### 2. Iniciar el servidor MCP
```
Panel N (tecla N) → pestaña "MCP for Blender"
☑ Poly Haven
☑ Poly Pizza (pegar la API key)
☐ Sketchfab (opcional)
☐ Hyper3D / Hunyuan3D (opcional)
🟢 Botón: "Start MCP Server"
```

### 3. Verificar en la consola del sistema
```
Window → Toggle System Console
Debe aparecer:
"BlenderMCP server started on localhost:9876"
```

---

## 🤖 CONFIGURACIÓN DE AGENTES IDE

### OpenCode (`~/.config/opencode/opencode.jsonc`)
```jsonc
{
  "mcp": {
    "blender-mcp": {
      "type": "local",
      "command": ["uvx", "blender-mcp"],
      "enabled": true,
      "environment": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

### Cursor (Settings → MCP → Add Server)
```json
{
  "mcpServers": {
    "blender": {
      "command": "cmd",
      "args": ["/c", "uvx", "blender-mcp"]
    }
  }
}
```

### VS Code (extensión MCP)
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

### Codex
```bash
codex mcp add blender -- uvx blender-mcp
```

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

---

## ✅ PRUEBA DE CONEXIÓN

### En OpenCode / terminal:
```bash
# Prueba simple
"Obtén información de la escena actual"
```

### Respuesta esperada:
```json
{
  "name": "Scene",
  "object_count": 2,
  "objects": [
    {"name": "Cube", "type": "MESH", "location": [0, 0, 0]},
    {"name": "Light", "type": "LIGHT", "location": [0, 0, 5]}
  ],
  "materials_count": 1
}
```

### Prueba de creación de objeto:
```bash
"Crea un cubo 'TestCube' en la posición (2, 0, 0) con escala (1, 2, 1)"
```

---

## 🔑 CLAVES API (OPCIONAL)

| Servicio | Dónde obtenerla | Dónde pegarla |
|--------|--------------|---------------|
| **Poly Pizza** | https://poly.pizza/settings/api | Blender Preferences → Add-ons → MCP for Blender → Poly Pizza API Key |
| **Sketchfab** | https://sketchfab.com/developers/api | Blender Preferences → Add-ons → MCP for Blender → Sketchfab API Key |
| **Hyper3D** | https://hyper3d.ai/ | Blender Preferences → Add-ons → MCP for Blender → Hyper3D API Key |
| **Hunyuan3D** | https://3d.hunyuan.tencent.com/ | Blender Preferences → Add-ons → MCP for Blender → SecretId/SecretKey |

---

## ⚠️ PROBLEMAS FRECUENTES

| Problema | Solución |
|----------|---------|
| `spawn uvx ENOENT` | Añadir `~/.local/bin` al PATH, reiniciar el IDE |
| `Connection refused` | Blender no está en marcha o el servidor MCP no se inició (N-panel → Start) |
| `Timeout` | Solicitud demasiado compleja → dividir en pasos |
| `Poly Pizza 403` | Bloqueo Cloudflare → descargar .glb manualmente → File → Import → glTF |
| `ModuleNotFoundError: mcp` | Ejecutar Blender como admin una vez para autoinstalar dependencias |

---

## 🔗 ENLACES

- **Prompts:** [P01-P05](../prompts/) — comandos básicos
- **Casos:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Flujos:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Siguiente:** [Setup 02: GenesisCore Local](../setups/setup_02_genesiscore_local.md)
