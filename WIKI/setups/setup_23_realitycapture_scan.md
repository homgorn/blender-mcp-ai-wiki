---
id: setup_23_realitycapture_scan
lang: ru
category: setups
status: full
---
# SETUP 23: REALITYCAPTURE SCAN TO BLENDER

**ID:** SETUP-23 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 40-60 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Фотограмметрия → game-ready. EN: Photogrammetry → game-ready.

## 1. Шаги / Steps
1. RC CLI
2. Laser+photo align
3. Decimate/retopo
4. PBR bake 8k

## 2. MCP промпт / Prompt
```
RU: "Импорт RC mesh 5M tris → Quad Remesher 20k → Smart UV → bake 8k→2k" / EN: "Import RC 5M mesh → Quad Remesher 20k → Smart UV → bake 8k→2k"
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

### Пайплайн
1. RC: align → dense → mesh 5M → simplify preview.
2. Export OBJ + 8k textures.
3. Blender: Quad Remesher 20k → Smart UV → bake normal/AO/curvature с high.
4. LOD: 20k/8k/2k + billboard.

### Проверка
- [ ] Масштаб реальный (scale bar)
- [ ] Normal map без швов на стыках чанков

