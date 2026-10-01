---
id: case_07_stylized_barrel
lang: ru
category: cases
status: full
tags: [case, pipeline, render, unity]
---
# CASE 07: STYLIZED BARREL (HAND-PAINT)

**ID:** CASE-07 | **Type:** Game | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

## 🎯 Задача / Brief
RU: PBR hand-paint, 1.2k tris, Unity export
EN: PBR hand-paint, 1.2k tris, Unity export

## Чек-лист / Checklist
- [ ] Блокаут/пропорции
- [ ] Топология/UV без ошибок
- [ ] PBR 2k+, нейминг
- [ ] Свет/камера/рендер
- [ ] Экспорт GLB/FBX + превью

## 🔗 WF-07, Setup 01/08, INDEX

---

## FULL PROCESS

1. Блокаут: цилиндр 12 граней + крышка + обручи (torus).
2. Bevel weights: грани обручей 1.0, доски 0.3.
3. UV: Smart Project + seams по краям досок.
4. Bake: normal с high (subdiv 2) на low.
5. Hand-paint: base wood → grain streaks → edge highlight → dirt in crevices.
6. Export GLB 1.2k tris + 2k textures.

## 🎯 ЦЕЛЬ

Кейс категории «Кейсы», сложность ⭐⭐.

1.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 13: HARD-SURFACE SCI-FI GUN](case_13_hard_surface_gun.md)
- **По темам:** [CASE 14: FOOD RENDER (RAMEN)](case_14_food_r visualisation.md), [P22: PARTICLE SYSTEMS](../prompts/22_particles.md), [P39: EXPORT PRESETS (GLB/FBX/USD)](../prompts/39_export_presets.md)
- **Теги:** #case, #pipeline, #render, #unity

