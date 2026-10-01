---
id: setup_47_zero123_instantmesh
lang: ru
category: setups
status: stub
tags: [ai-3d, setup]
---
# SETUP 47: ZERO123 / INSTANTMESH

**ID:** SETUP-47 | **Type:** Multi-view 3D | **Difficulty:** ⭐⭐⭐ | **Time:** 30 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Мультивью реконструкция. EN: Multi-view reconstruction.

## 1. Шаги / Steps
1. Zero123++ views
2. InstantMesh LRM
3. NeRF→mesh
4. Texture refine

## 2. MCP промпт / Prompt
```
RU: "Zero123++: 6 views из 1 фото → InstantMesh → textured mesh" / EN: "Zero123++: 6 views from 1 photo → InstantMesh → textured mesh"
```

## 3. Проверка / Check
- [ ] Аддон/сервис отвечает
- [ ] Тестовая сцена собирается
- [ ] Экспорт читается целевым софтом

## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 43: MESHY API V4](setup_43_meshy_api_v4.md), [SETUP 44: RODIN / HYPER3D GEN](setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md)
- **По темам:** [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **Теги:** #ai-3d, #setup

