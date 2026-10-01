---
id: setup_18_substance_painter_live
lang: ru
category: setups
status: full
---
# SETUP 18: SUBSTANCE PAINTER LIVE-LINK

**ID:** SETUP-18 | **Type:** Texturing Pro | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Substance → Blender живой линк. EN: Substance → Blender live link.

## 1. Шаги / Steps
1. FBX/GLTF roundtrip
2. UDIM workflow
3. Smart materials
4. Live link plugin

## 2. MCP промпт / Prompt
```
RU: "Экспорт FBX с UDIM в Substance, запеки ID/curvature/AO, верни PBR 4k в Blender" / EN: "Export FBX with UDIM to Substance, bake ID/curvature/AO, return 4k PBR to Blender"
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

### Roundtrip
1. Blender → FBX с UDIM в Substance Painter.
2. Bake: ID, curvature, AO, thickness, position.
3. Smart materials + слои wear/dirt/damage.
4. Export 4k PBR → Blender Principled (BaseColor sRGB, остальные Non-Color).

### Проверка
- [ ] UDIM-тайлы совпадают
- [ ] Curvature-маски дают чистый edge wear

