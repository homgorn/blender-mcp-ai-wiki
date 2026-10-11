---
lang: en
tags: [addon, blender, mcp, reference, stable-diffusion]
---
# INSTALLATION GUIDE - COMPLETE SETUP

## Prerequisites
- Windows 10/11 (this guide)
- Blender 4.2+
- Python 3.10+ (bundled with Blender)
- Internet connection for model downloads

---

## Step 1: Install uv (Required)

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add to PATH (REQUIRED - restart PowerShell after)
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")

# Verify
uv --version
uvx --version
```

---

## Step 2: Install Blender

### Option A: MSI Installer (Recommended)
```powershell
# Download Blender installer for your version
# msiexec /i "путь\к\blender-<версия>-windows-x64.msi" /quiet /norestart
```

### Option B: Portable ZIP
```powershell
# Extract to a folder of your choice
# Run: <путь-к-папке>\blender.exe
```

### Verify
```powershell
# Find Blender path
where blender
# Or check typical install location
```

> [!NOTE]
> Версию Blender (например 4.2) выбирайте под свои задачи. Конкретный путь к инсталлятору зависит от того, куда вы его скачали.

---

## Step 3: Install blender-mcp (MCP Server + Addon)

```powershell
# Install addon to Blender
uvx blender-mcp install-addon

# Verify addon path
uvx blender-mcp addon-paths
```

---

## Step 4: Install GenesisCore Addon

```powershell
# Download GenesisCore zip from GitHub
# In Blender:
# 1. Edit → Preferences → Add-ons → Install from ZIP
# 2. Select downloaded zip file
# 3. Enable: Search "GenesisCore" → Check box
```

---

## Step 5: Install Dream Textures Addon

```powershell
# Download latest release:
# https://github.com/carson-katri/dream-textures/releases/latest
# Download: dream_textures-<version>.zip

# In Blender:
# 1. Edit → Preferences → Add-ons → Install from ZIP
# 2. Select downloaded ZIP
# 3. Enable: Dream Textures

# First run: Downloads PyTorch + diffusers (~2-4 GB)
# Preferences → Dream Textures → Download model: stabilityai/stable-diffusion-2-1-base
```

---

## Step 6: Configure OpenCode MCP

Create/Open: `C:\Users\<USERNAME>\.config\opencode\opencode.json`

```json
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

---

## Step 7: Configure GenesisCore (OpenRouter)

1. Get API key: https://openrouter.ai/keys
2. In Blender: Press `N` → **GenesisCore** tab
3. **Provider:** OpenRouter
4. **API Key:** Paste key
5. **Fetch Models** → Select: `deepseek/deepseek-chat` or `qwen/qwen-2.5-coder-32b`
6. **Tool Modules:** Enable all (Shift+click for multiple)
7. **Save Config**

---

## Step 8: Start Servers

### blender-mcp (for OpenCode/Claude/Cursor)
```powershell
# Terminal 1: Start MCP server
uvx blender-mcp
# Keep running
```

### In Blender (for both)
1. Press `N` → **MCP for Blender** tab
2. Check: Poly Haven, Poly Pizza, Sketchfab, etc.
3. Enter API keys in Preferences → Add-ons → MCP for Blender
4. Click **Start MCP Server**

### GenesisCore (for in-Blender chat)
1. Press `N` → **GenesisCore** tab
2. Click **Connect** (connects to internal server on :45677)
3. Chat with AI directly in Blender

---

## Step 9: Test Everything

### Test blender-mcp (via OpenCode)
```bash
# In OpenCode chat:
"Get the current Blender scene info"
"Create a cube at location (1, 2, 3)"
"Search Poly Haven for a concrete texture and apply to cube"
```

### Test GenesisCore (in Blender N-panel)
```
Prompt: "Create a low-poly house with a roof, door, and windows"
Prompt: "Add studio lighting: key, fill, rim lights"
Prompt: "Search Poly Haven for an HDRI and set as world environment"
```

### Test Dream Textures
1. Select cube → N-panel → **Dream Textures**
2. Prompt: "weathered brick wall, seamless"
3. Check **Seamless** → Generate
4. Apply to material

---

## API Keys Needed

| Service | Key | Where to Get | Where to Enter |
|---------|-----|--------------|----------------|
| **OpenRouter** | Required | https://openrouter.ai/keys | GenesisCore N-panel |
| **Poly Pizza** | Free | https://poly.pizza/settings/api | Blender Prefs → MCP for Blender |
| **Sketchfab** | Required | https://sketchfab.com/developers/api | Blender Prefs → MCP for Blender |
| **Hyper3D** | Required | https://hyper3d.ai/ | Blender Prefs → MCP for Blender |
| **Hunyuan3D** | SecretId/Key | https://3d.hunyuan.tencent.com/ | Blender Prefs → MCP for Blender |
| **DreamStudio** | Optional | https://beta.dreamstudio.ai/ | Blender Prefs → Dream Textures |

---

## Directory Structure (Final)

```
<ваш-проект>/
├── blender-<версия>-windows-x64.msi
├── blender-<версия>-windows-x64.zip
├── CHANGELOG.md
├── INDEX.md
├── addons/
│   ├── GenesisCore-main.zip
│   ├── blender-mcp-full.md
│   ├── blender-mcp.md
│   ├── dream-textures-full.md
│   ├── dream-textures.md
│   └── genesiscore.md
├── mcp/
│   ├── architecture.md
│   ├── clients.md
│   ├── server-api.md
│   └── setup-guide.md
├── guides/
│   ├── installation.md
│   ├── prompting.md
│   ├── troubleshooting.md
│   └── workflows.md
├── api/
│   ├── blender-api.md
│   ├── materials.md
│   ├── mesh-operations.md
│   └── scripting-patterns.md
├── workflows/
│   ├── animation.md
│   ├── scene-building.md
│   ├── text-to-3d.md
│   └── texture-generation.md
└── references/
    └── (additional docs)
```

> [!NOTE]
> Структура каталогов приведена как пример. Используйте любую удобную папку для проекта и версии Blender.

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| `uvx` not found | Restart PowerShell; check PATH |
| Blender not found | Run `uvx blender-mcp addon-paths` |
| Addon not showing | Restart Blender; check correct version folder |
| GenesisCore "Connecting..." | Port 45677 blocked; restart Blender |
| Dream Textures OOM | Reduce resolution; use fp16 |
| Poly Pizza 403 | Manual download + File → Import → glTF |

---

## Next Steps
1. Read [Prompting Guide](../guides/prompting.md)
2. Read [Workflows](../workflows/scene-building.md)
3. Explore [Blender API Patterns](../api/scripting-patterns.md)
4. Check [MCP Architecture](../mcp/architecture.md)

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [TROUBLESHOOTING GUIDE](troubleshooting.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [DREAM TEXTURES ADDON - DEEP DIVE](../addons/dream-textures.md), [GENESISCORE ADDON - DEEP DIVE](../addons/genesiscore.md)
- **По темам:** [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [SETUP 35: READY PLAYER ME AVATARS](../../../setups/setup_35_readyplayerme.md), [TEXT-TO-3D WORKFLOWS](../workflows/text-to-3d.md)
- **Теги:** #addon, #blender, #mcp, #reference, #stable-diffusion

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

