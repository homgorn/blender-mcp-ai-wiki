---
id: setup_53_flamenco_farm
lang: ru
category: setups
status: full
---
# SETUP 53: FLAMENCO FARM CLUSTER

**ID:** SETUP-53 | **Type:** Render Farm | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Ферма Flamenco. EN: Flamenco farm.

## 1. Шаги / Steps
1. Manager+workers
2. Shared storage
3. Job split
4. Monitor

## 2. MCP промпт / Prompt
```
RU: "Manager+3 workers, NFS storage, split 1-250 по 25 кадров, мониторинг" / EN: "Manager+3 workers, NFS, split 1-250 by 25, monitor"
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

### Топология
`Manager :8080` + workers с доступом к общей папке (NFS/SMB).
Версия Blender одинаковая везде.

### Сабмит
1. Blend со всеми текстурами packed или относительными путями `//`.
2. Job: frames 1-250 chunk 25, samples 128, output `//renders/`.
3. Мониторинг: failed frames → перезапуск только их.

### Типовые ошибки
- Разные пути текстур → розовые материалы. Лечится `File → External Data → Make All Paths Relative`.
- Разные версии Blender → разный результат. Пинь версию.

