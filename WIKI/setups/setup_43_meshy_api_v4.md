---
id: setup_43_meshy_api_v4
lang: ru
category: setups
status: stub
tags: [ai-3d, api, setup]
---
# SETUP 43: MESHY API V4

**ID:** SETUP-43 | **Type:** Text-to-3D/Texture | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Meshy полный цикл. EN: Meshy full cycle.

## 1. Шаги / Steps
1. Text-to-3D
2. Text-to-texture
3. Remesh/retopo
4. Animate/rig

## 2. MCP промпт / Prompt
```
RU: "Meshy: text-to-3D 'stylized orc axe', text-to-texture, auto-UV, rig" / EN: "Meshy: text-to-3D 'stylized orc axe', text-to-texture, auto-UV, rig"
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

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md), [SETUP 44: RODIN / HYPER3D GEN](setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md)
- **По темам:** [SETUP 47: ZERO123 / INSTANTMESH](setup_47_zero123_instantmesh.md), [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #ai-3d, #api, #setup

