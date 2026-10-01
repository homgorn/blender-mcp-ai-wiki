---
id: setup_44_rodin_hyper3d
lang: ru
category: setups
status: full
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

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX

---

## FULL GUIDE

### Генерация
1. Front+side фото → Rodin job → poll до DONE.
2. Скачай GLB + PBR.
3. Cleanup: decimate 15k, Smart UV, bake normal.
4. Scale to meters, origin to base.

### Проверка
- [ ] Пропорции совпадают с референсом
- [ ] Текстуры 2k, без растяжек на лице/руках

