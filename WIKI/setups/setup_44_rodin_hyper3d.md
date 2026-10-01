---
id: setup_44_rodin_hyper3d
lang: ru
category: setups
status: stub
tags: [ai-3d, setup]
---
# SETUP 44: RODIN / HYPER3D GEN

**ID:** SETUP-44 | **Type:** Image-to-3D | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Rodin генерация. EN: Rodin generation.

## 1. Шаги / Steps
1. Rodin Gen-1
2. Multi-view
3. PBR bake
4. Blender cleanup

## 2. MCP промпт / Prompt
```
RU: "Rodin: front+side фото → 3D, decimate 15k, Smart UV, bake normal" / EN: "Rodin: front+side photos → 3D, decimate 15k, Smart UV, bake normal"
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

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 43: MESHY API V4](setup_43_meshy_api_v4.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md), [SETUP 47: ZERO123 / INSTANTMESH](setup_47_zero123_instantmesh.md)
- **По темам:** [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **Теги:** #ai-3d, #setup

