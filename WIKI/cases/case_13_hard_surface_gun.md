---
id: case_13_hard_surface_gun
lang: ru
category: cases
status: full
---
# CASE 13: HARD-SURFACE SCI-FI GUN

**ID:** CASE-13 | **Type:** Hardsurface | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

## 🎯 Задача / Brief
RU: Bevel weights, boolean, baked normals
EN: Bevel weights, boolean, baked normals

## Чек-лист / Checklist
- [ ] Блокаут/пропорции
- [ ] Топология/UV без ошибок
- [ ] PBR 2k+, нейминг
- [ ] Свет/камера/рендер
- [ ] Экспорт GLB/FBX + превью

## 🔗 WF-07, Setup 01/08, INDEX

---

## FULL PROCESS

1. Блокаут примитивами + boolean вырезы (trigger, mag well).
2. Bevel по весам: внешние 0.02, внутренние 0.005.
3. Weighted normals для чистых бликов.
4. Bake normal 4k с cage 0.01.
5. PBR: gunmetal + worn edges (curvature mask) + grip polymer.
6. LOD: 8k → 3k → 800 tris.

