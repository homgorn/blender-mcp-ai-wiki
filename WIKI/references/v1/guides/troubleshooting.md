# TROUBLESHOOTING GUIDE

## Blender Installation Issues

### MSI Install Fails (Exit Code 1620)
```powershell
# Check install log
Get-Content C:\BLENDER ai\install.log -Tail 50

# Common causes:
# - Pending reboot required
# - Another MSI running
# - Insufficient permissions (run as Admin)
# - Corrupt download

# Fix: Re-download, run as Administrator
Start-Process msiexec.exe -ArgumentList "/i C:\BLENDER ai\blender-4.2.3-windows-x64.msi /qb" -Verb RunAs -Wait
```

### Blender Not Found After Install
```powershell
# Check common locations
Test-Path "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
Test-Path "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
Get-ChildItem "$env:LOCALAPPDATA\Programs\Blender Foundation\" -Recurse -Filter blender.exe
Get-ChildItem "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\" -Recurse -Filter "*lender*"

# Use portable version instead
# Extract ZIP to C:\BLENDER ai\Blender\ and run blender.exe directly
```

---

## uv / uvx Issues

### `uvx` Not Found / `spawn uvx ENOENT`
```powershell
# 1. Restart PowerShell/terminal completely
# 2. Verify PATH
$env:PATH -split ";" | Where-Object { $_ -like "*\.local\bin*" }

# 3. Add manually if missing
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")

# 4. Use full path in MCP config
where uvx
# → C:\Users\<USER>\.local\bin\uvx.exe
```

### Version Conflicts / Cache Issues
```bash
uv cache clean blender-mcp
uv cache clean --all
uvx --refresh blender-mcp
```

### Python Version Problems
```json
// In MCP config, pin Python 3.11
{
  "args": ["--python", "3.11", "blender-mcp"],
  "env": { "UV_PYTHON_PREFERENCE": "only-managed" }
}
```

---

## MCP Connection Issues

### "Connection Refused" / "Cannot Connect to Blender"
1. **Blender addon not running:**
   - Open Blender → N-panel → **MCP for Blender** → Click **Start MCP Server**
   - Or for GenesisCore: N-panel → **GenesisCore** → Click **Connect**

2. **Wrong port:**
   - blender-mcp: port 9876 (configurable via `BLENDER_PORT`)
   - GenesisCore: port 45677 (internal)

3. **Firewall/Antivirus blocking:**
   - Allow `python.exe` / `blender.exe` through Windows Firewall
   - Check private network profile

### Timeout on Commands
```bash
# Break complex requests into smaller steps
# Instead of: "Build entire city with 50 buildings"
# Do: "Create one building template" → "Array it 10x" → "Add variations"

# Increase timeout in client config if needed
```

### Tools Not Appearing in AI Client
```bash
# 1. Restart AI client COMPLETELY (not just window)
#    - Windows: Quit from system tray
#    - macOS: Cmd+Q
# 2. Check config syntax (valid JSON/TOML)
# 3. Verify uvx works in terminal: uvx blender-mcp --help
```

---

## GenesisCore Specific

### "Connecting..." Hangs Forever
```bash
# 1. Check port 45677 not in use
netstat -an | findstr 45677

# 2. Restart Blender completely
# 3. Check System Console (Window → Toggle System Console) for errors
# 4. Disable other addons that might conflict
```

### Model List Empty / "Failed to Fetch Models"
```bash
# 1. Verify API key is correct
# 2. Check internet connection / proxy
# 3. Try different provider (DeepSeek, OpenRouter, Ollama)
# 4. For Ollama: ensure ollama serve running, model pulled (ollama pull deepseek-coder)
```

### Tools Not Executing
```bash
# 1. Enable tool modules in N-panel (Shift+click for multiple)
#    Required: Common Tools, Object Tools, Material Tools
#    Optional: Polyhaven Tools, Asset Tools
# 2. Check System Console for Python errors
# 3. Some tools require specific context (e.g., active object)
```

---

## Dream Textures Issues

### Out of VRAM / CUDA OOM
```bash
# Reduce resolution: 512x512 max for 4GB VRAM
# Use fp16 (half precision) - default
# Close other GPU apps
# Enable Attention Slicing (Auto) in preferences
# Reduce steps: 20-30 instead of 50
```

### Model Download Fails
```bash
# 1. Check internet
# 2. For gated models: set HF_TOKEN in preferences
# 3. Try different model: stabilityai/stable-diffusion-2-1-base
# 4. Manual download: huggingface.co → download → Import Checkpoint
```

### macOS Quarantine (Not Windows)
```bash
xattr -r -d com.apple.quarantine ~/Library/Application\ Support/Blender/3.3/scripts/addons/dream_textures/.python_dependencies
```

### Slow Generation
```bash
# Use lower steps (20-30)
# Smaller resolution (512x512)
# Scheduler: DPM++ 2M Karras (faster)
# Enable Speed Optimizations: Half Precision
```

---

## blender-mcp Specific

### Poly Pizza Download Fails (Cloudflare 403)
```
Error: "Poly Pizza's CDN returned a Cloudflare bot-protection challenge"

Fix:
1. Download .glb manually from https://poly.pizza
2. File → Import → glTF 2.0
3. Or use residential IP (not VPN/datacenter)
```

### Headless Blender (`blender -b`) Commands Don't Execute
```
blender-mcp requires Blender GUI for command execution.
Use: blender (with GUI) or xvfb-run -a blender (Linux headless)
```

### Safe Mode Blocks Script
```
Error: "Rejected by safe mode - ..."

Fix:
1. Rewrite without: os, subprocess, open(), eval(), exec()
2. Use only: bpy, bmesh, mathutils, math, random, json, uuid
3. Or disable: BLENDER_MCP_SAFE_MODE=0 (default)
```

---

## Asset Integration Issues

### Poly Haven Assets Not Appearing
```bash
# 1. Enable "Use Poly Haven" in Blender N-panel → MCP for Blender
# 2. Check cache: %TEMP%\polyhaven_models\ / polyhaven_hdris\
# 3. Clear cache and retry
```

### Sketchfab Requires API Key
```bash
# 1. Get key: https://sketchfab.com/developers/api
# 2. Blender Preferences → Add-ons → MCP for Blender → Sketchfab API Key
# 3. Or env: BLENDERMCP_SKETCHFAB_API_KEY
```

### Hyper3D / Hunyuan3D Not Working
```bash
# 1. Enable in N-panel
# 2. Add API keys in Preferences
# 3. Check credits/quota on provider dashboard
# 4. Free tier may have limits
```

---

## Performance Issues

### Blender Freezes / Unresponsive
```bash
# 1. Check System Console for infinite loops
# 2. Reduce object count in scene
# 3. Disable heavy modifiers (Subsurf high levels)
# 4. Use simpler geometry for AI generation
```

### Large .blend Files
```bash
# File → Clean Up → Unused Data Blocks
# File → External Data → Automatically Pack Resources (or unpack)
# Delete unused materials, textures, meshes
# Use Linked libraries for repeated assets
```

---

## Debugging Tools

### Blender System Console
```
Windows: Window → Toggle System Console
macOS: /Applications/Blender.app/Contents/MacOS/Blender (in Terminal)
Linux: Run blender from terminal
```

### MCP Server Logs
```bash
# blender-mcp: Runs in terminal where you started uvx
# GenesisCore: Check Blender System Console
```

### Enable Verbose Logging
```python
# In Blender Python console:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'object_name'` | Object doesn't exist | Check spelling, use `bpy.data.objects.get()` |
| `AttributeError: 'NoneType'` | Context is None (background mode) | Run Blender with GUI |
| `RuntimeError: Operator not available` | Wrong mode (EDIT vs OBJECT) | `bpy.ops.object.mode_set(mode='OBJECT')` |
| `MemoryError` | Out of RAM/VRAM | Reduce resolution, close apps |
| `ModuleNotFoundError` | Missing Python package | uvx handles deps; check .python_dependencies |

---

## Getting Help

1. **Blender System Console** - First place to look
2. **GitHub Issues:**
   - GenesisCore: https://github.com/AIGODLIKE/GenesisCore/issues
   - blender-mcp: https://github.com/ahujasid/blender-mcp/issues
   - Dream Textures: https://github.com/carson-katri/dream-textures/issues
3. **Discord:**
   - blender-mcp: https://discord.gg/SNqPn4TcKQ
   - Dream Textures: https://discord.gg/EmDJ8CaWZ7
4. **Documentation:** This wiki + official docs