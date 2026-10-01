---
id: case_13_hard_surface_gun
lang: ru
category: cases
status: full
tags: [case, modeling, render]
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

## 🎯 ЦЕЛЬ

Кейс категории «Кейсы», сложность ⭐⭐⭐.

1.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 14: FOOD RENDER (RAMEN)](case_14_food_r visualisation.md)
- **По темам:** [P22: PARTICLE SYSTEMS](../prompts/22_particles.md), [P43: CAMERA SWITCHING & MARKERS](../prompts/43_camera_switching.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md)
- **Теги:** #case, #modeling, #render

