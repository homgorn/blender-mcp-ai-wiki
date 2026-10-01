---
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
