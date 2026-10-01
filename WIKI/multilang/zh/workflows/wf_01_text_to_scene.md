---
id: wf_01_text_to_scene
lang: zh
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# WF 01：文本生成场景

**ID:** WF-01 | **类型:** 端到端管线 | **难度:** ⭐⭐ | **用时:** 15-30 分钟

---

## 🎯 目标
完整管线：文字描述 → 3D 场景（几何、材质、灯光、相机、渲染）

---

## 📋 管线架构

```
USER PROMPT
    │
    ▼
┌─────────────────────────────────────┐
│  LLM AGENT (OpenCode/Claude)        │
│  - 解析描述                         │
│  - 规划步骤                         │
│  - 调用 MCP 工具                    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BLENDER-MCP SERVER (localhost:9876)│
│  - create_object                    │
│  - set_material                     │
│  - download_polyhaven_asset         │
│  - execute_blender_code             │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BLENDER (bpy 执行)                 │
│  - 创建几何                         │
│  - 指定材质                         │
│  - 布置灯光                         │
│  - 放置相机                         │
│  - 执行渲染                         │
└─────────────────────────────────────┘
    │
    ▼
结果: 渲染图 / .blend 文件 / GLB 导出
```

---

## 📝 提示词示例

### 简单：房间
```
"创建 5x5x3 米房间：地板、4 面墙、天花板。
在前墙开 1.5x1.5 米窗（boolean）。
材质：墙-白色灰泥，地板-拼花木，窗-玻璃。
灯光：Poly Haven HDRI 'studio' 2k。
相机：在角落看向中心，35mm。
渲染：Cycles 128 samples，1920x1080，保存到 //renders/room.png"
```

### 中等：地牢房间
```
"创建 10x10x5 米暗黑幻想地牢房间。
墙：开裂石砌 (PBR)。地板：缝隙带苔藓的石板。
道具：3 根柱子、2 个箱子、中央祭坛。
灯光：3 个点光源（火焰）+ 弱 HDRI 'dungeon'。
相机：低角度，祭坛 DOF。
渲染：256 samples，denoising ON"
```

---

## 🔧 按阶段的 MCP 命令

### 阶段 1：基础几何
```bash
"创建平面 'Floor' 10x10 米于 (0,0,0)"
"创建立方体 'Wall_Front' 10x0.2x3 米于 (0, -5, 1.5)"
```

### 阶段 2：布尔（窗/门）
```bash
"创建立方体 'Window_Cut' 2x0.3x1.5 米于 (0, -5.1, 1.5)
从 Wall_Front 减去 Window_Cut (DIFFERENCE)"
```

### 阶段 3：材质
```bash
"创建材质 'Mat_Parquet': BaseColor #8B7355, Roughness 0.6，赋给 Floor"
```

### 阶段 4：Poly Haven
```bash
"在 Poly Haven 搜索 HDRI 'studio' indoor 类 2k，下载并设为 World"
```

### 阶段 5：相机和渲染
```bash
"创建相机 'Cam_Main' 于 (7, -7, 4) 看向中心，35mm，设为活动相机，中心 DOF"
"设置 Cycles: 128 samples, denoising ON, 1920x1080，渲染到 //renders/scene_01.png"
```

---

## 🔗 相关链接

- **配置:** [Setup 01: blender-mcp](../setups/setup_01_blender_mcp_basic.md)
- **下一个:** [WF 02: Image-to-3D](../workflows/wf_02_image_to_3d.md)
