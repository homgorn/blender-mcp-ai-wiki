---
id: setup_11_touchdesigner
lang: ru
category: setups
status: stub
tags: [blender, realtime, setup]
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

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [EEVEE NEXT (BLENDER 4.2+)](../realtime/eevee_next.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #realtime, #setup

