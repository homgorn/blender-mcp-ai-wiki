---
id: setup_01_blender_mcp_basic
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 1
translation: human
---
# SETUP 01: BLENDER-MCP BASIS

**ID:** SETUP-01 | **Typ:** Kern-Infrastruktur | **Schwierigkeit:** ⭐ | **Zeit:** 10-15 Min

---

## 🎯 ZIEL
Blender-mcp installieren und für IDE-Agenten einrichten (OpenCode, Cursor, VS Code, Codex, Claude Desktop)

---

## 📋 VORAUSSETZUNGEN

| Komponente | Version | Status |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Erforderlich |
| **Python** | 3.10+ | ✅ In Blender enthalten |
| **uv** | latest | ✅ Erforderlich |
| **Git** | latest | ⚠️ Optional |

---

## 🪟 WINDOWS-INSTALLATION (SCHRITT FÜR SCHRITT)

### 1. uv installieren
```powershell
# PowerShell als Administrator
irm https://astral.sh/uv/install.ps1 | iex

# Terminal neu starten
# Prüfen
uv --version
uvx --version
```

### 2. Blender-mcp Addon installieren
```powershell
# Automatische Installation in Blender
uvx blender-mcp install-addon

# Pfad prüfen
uvx blender-mcp addon-paths
# Sollte zeigen: C:\Users\<USER>\AppData\Roaming\Blender Foundation\Blender\4.x\scripts\addons\blender_mcp.py
```

### 3. PATH einrichten (falls uvx nicht gefunden)
```powershell
# uvx finden
where uvx
# Normalerweise: C:\Users\<USER>\.local\bin\uvx.exe

# Zum Benutzer-PATH hinzufügen
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
# Terminal/IDE neu starten
```

---

## 🔧 BLENDER-EINRICHTUNG

### 1. Addon aktivieren
```
Edit → Preferences → Add-ons
Suchen: "MCP for Blender"
☑ Interface: MCP for Blender
```

### 2. MCP-Server starten
```
N-Panel (Taste N) → Reiter "MCP for Blender"
☑ Poly Haven
☑ Poly Pizza (API-Key einfügen)
☐ Sketchfab (optional)
☐ Hyper3D / Hunyuan3D (optional)
🟢 Button: "Start MCP Server"
```

### 3. In der Systemkonsole prüfen
```
Window → Toggle System Console
Es sollte erscheinen:
"BlenderMCP server started on localhost:9876"
```

---

## 🤖 IDE-AGENTEN KONFIGURATION

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

### VS Code (MCP-Erweiterung)
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

## ✅ VERBINDUNGSTEST

### In OpenCode / Terminal:
```bash
# Einfacher Test
"Hole Informationen über die aktuelle Szene"
```

### Erwartete Antwort:
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

### Objekterstellungs-Test:
```bash
"Erstelle einen Würfel 'TestCube' an Position (2, 0, 0) mit Skalierung (1, 2, 1)"
```

---

## 🔑 API-SCHLÜSSEL (OPTIONAL)

| Dienst | Wo erhalten | Wo einfügen |
|--------|--------------|---------------|
| **Poly Pizza** | https://poly.pizza/settings/api | Blender Preferences → Add-ons → MCP for Blender → Poly Pizza API Key |
| **Sketchfab** | https://sketchfab.com/developers/api | Blender Preferences → Add-ons → MCP for Blender → Sketchfab API Key |
| **Hyper3D** | https://hyper3d.ai/ | Blender Preferences → Add-ons → MCP for Blender → Hyper3D API Key |
| **Hunyuan3D** | https://3d.hunyuan.tencent.com/ | Blender Preferences → Add-ons → MCP for Blender → SecretId/SecretKey |

---

## ⚠️ HÄUFIGE PROBLEME

| Problem | Lösung |
|----------|---------|
| `spawn uvx ENOENT` | `~/.local/bin` zum PATH hinzufügen, IDE neu starten |
| `Connection refused` | Blender läuft nicht oder MCP-Server nicht gestartet (N-Panel → Start) |
| `Timeout` | Anfrage zu komplex → in Schritte aufteilen |
| `Poly Pizza 403` | Cloudflare-Block → .glb manuell laden → File → Import → glTF |
| `ModuleNotFoundError: mcp` | Blender einmal als Admin starten für Auto-Install der Deps |

---

## 🔗 LINKS

- **Prompts:** [P01-P05](../prompts/) — Basisbefehle
- **Fälle:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **Nächster:** [Setup 02: GenesisCore Local](../setups/setup_02_genesiscore_local.md)
