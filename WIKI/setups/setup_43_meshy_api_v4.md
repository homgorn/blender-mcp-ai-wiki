---
id: setup_43_meshy_api_v4
lang: ru
category: setups
status: full
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

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX

---

## FULL GUIDE

### Endpoints
- `POST /v4/text-to-3d`, `POST /v4/image-to-3d`, `POST /v4/text-to-texture`.
- Poll до `SUCCEEDED`, скачай GLB/FBX + textures.

### Текстурирование существующего меша
1. Загрузи свой OBJ + промпт стиля.
2. Meshy вернёт PBR-сет + auto-UV.
3. В Blender: замени материалы, проверь texel density.

### Лимиты
- Draft: быстро/дешево для итераций; Refine: 1 раз в конце.

