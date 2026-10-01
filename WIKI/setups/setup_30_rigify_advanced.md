---
id: setup_30_rigify_advanced
lang: ru
category: setups
status: full
---
# SETUP 30: RIGIFY ADVANCED + FACE

**ID:** SETUP-30 | **Type:** Rig | **Difficulty:** ⭐⭐⭐ | **Time:** 45 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Rigify + лицо + corrective. EN: Rigify + face + correctives.

## 1. Шаги / Steps
1. Meta-rig samples
2. Face rig
3. Rigify-to-Unity
4. Correctives

## 2. MCP промпт / Prompt
```
RU: "Rigify human + face rig 52 кости, corrective shapes колени/локти, game export" / EN: "Rigify human + 52-bone face, knee/elbow correctives, game export"
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

### Rigify + лицо
1. Meta-rig human + face rig (52 кости: jaw/eyes/brows/lips).
2. Generate → weights auto → чистка: плечи/таз градиенты, пальцы по фалангам.
3. Correctives: колени/локти (см. P34).
4. Game export: bake deform, remove drivers.

### Проверка
- [ ] Экстремальные позы без разрывов
- [ ] Лицо: 6 базовых эмоций читаются

