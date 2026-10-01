---
id: setup_01_blender_mcp_basic
lang: zh
orig_lang: ru
category: setups
type: setup
difficulty: 1
translation: human
---
# 配置 01：BLENDER-MCP 基础

**ID:** SETUP-01 | **类型:** 核心基础设施 | **难度:** ⭐ | **用时:** 10-15 分钟

---

## 🎯 目标
安装并配置 blender-mcp，使其与 IDE 智能体协作（OpenCode、Cursor、VS Code、Codex、Claude Desktop）

---

## 📋 前置要求

| 组件 | 版本 | 状态 |
|------|------|------|
| **Blender** | 4.0+ | ✅ 必需 |
| **Python** | 3.10+ | ✅ Blender 自带 |
| **uv** | latest | ✅ 必需 |
| **Git** | latest | ⚠️ 可选 |

---

## 🪟 WINDOWS 安装（分步）

### 1. 安装 uv
```powershell
# 以管理员身份运行 PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# 重启终端
# 验证
uv --version
uvx --version
```

### 2. 安装 blender-mcp 插件
```powershell
# 自动安装到 Blender
uvx blender-mcp install-addon

# 检查路径
uvx blender-mcp addon-paths
# 应显示: C:\Users\<USER>\AppData\Roaming\Blender Foundation\Blender\4.x\scripts\addons\blender_mcp.py
```

### 3. 配置 PATH（如果找不到 uvx）
```powershell
# 查找 uvx
where uvx
# 通常: C:\Users\<USER>\.local\bin\uvx.exe

# 添加到用户 PATH
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
# 重启终端/IDE
```

---

## 🔧 BLENDER 设置

### 1. 启用插件
```
Edit → Preferences → Add-ons
搜索: "MCP for Blender"
☑ Interface: MCP for Blender
```

### 2. 启动 MCP 服务器
```
N 面板（按 N 键）→ "MCP for Blender" 选项卡
☑ Poly Haven
☑ Poly Pizza（粘贴 API 密钥）
☐ Sketchfab（可选）
☐ Hyper3D / Hunyuan3D（可选）
🟢 按钮: "Start MCP Server"
```

### 3. 在系统控制台中检查
```
Window → Toggle System Console
应出现：
"BlenderMCP server started on localhost:9876"
```

---

## 🤖 IDE 智能体配置

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

### VS Code (MCP 扩展)
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

## ✅ 连接测试

### 在 OpenCode / 终端中：
```bash
# 简单测试
"获取当前场景信息"
```

### 预期回复：
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

### 创建对象测试：
```bash
"在位置 (2, 0, 0) 创建立方体 'TestCube'，缩放 (1, 2, 1)"
```

---

## 🔑 API 密钥（可选）

| 服务 | 获取地址 | 粘贴位置 |
|------|----------|----------|
| **Poly Pizza** | https://poly.pizza/settings/api | Blender Preferences → Add-ons → MCP for Blender → Poly Pizza API Key |
| **Sketchfab** | https://sketchfab.com/developers/api | Blender Preferences → Add-ons → MCP for Blender → Sketchfab API Key |
| **Hyper3D** | https://hyper3d.ai/ | Blender Preferences → Add-ons → MCP for Blender → Hyper3D API Key |
| **Hunyuan3D** | https://3d.hunyuan.tencent.com/ | Blender Preferences → Add-ons → MCP for Blender → SecretId/SecretKey |

---

## ⚠️ 常见问题

| 问题 | 解决方法 |
|------|----------|
| `spawn uvx ENOENT` | 将 `~/.local/bin` 加入 PATH，重启 IDE |
| `Connection refused` | Blender 未运行或 MCP 服务器未启动（N 面板 → Start） |
| `Timeout` | 请求太复杂 → 拆分成小步骤 |
| `Poly Pizza 403` | Cloudflare 拦截 → 手动下载 .glb → File → Import → glTF |
| `ModuleNotFoundError: mcp` | 以管理员身份运行一次 Blender 以自动安装依赖 |

---

## 🔗 相关链接

- **提示词:** [P01-P05](../prompts/) — 基础命令
- **案例:** [Case 02: Game Props](../cases/case_02_game_props.md)
- **工作流:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md)
- **下一个:** [Setup 02: GenesisCore Local](../setups/setup_02_genesiscore_local.md)
