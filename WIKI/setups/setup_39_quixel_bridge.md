---
id: setup_39_quixel_bridge
lang: ru
category: setups
status: stub
---
# SETUP 39: QUIXEL BRIDGE STANDALONE

**ID:** SETUP-39 | **Type:** Megascans | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Quixel Bridge экспорт. EN: Quixel Bridge export.

## 1. Шаги / Steps
1. Bridge export
2. LOD + maps
3. Calibrated PBR
4. Blender plugin

## 2. MCP промпт / Prompt
```
RU: "Bridge export: love2d, 4k, LOD0-2, metallic/roughness/normal/AO/displacement" / EN: "Bridge export: 4k, LOD0-2, metal/rough/normal/AO/displace"
```

## 3. Проверка / Check
- [ ] Аддон/сервис отвечает
- [ ] Тестовая сцена собирается
- [ ] Экспорт читается целевым софтом

## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX
