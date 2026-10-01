---
id: setup_40_ambientcg_polyhaven
lang: ru
category: setups
status: full
---
# SETUP 40: AMBIENTCG + POLYHAVEN BATCH

**ID:** SETUP-40 | **Type:** Free PBR | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Пачка бесплатных PBR. EN: Batch free PBR.

## 1. Шаги / Steps
1. Batch download
2. PBR sets
3. HDRI batch
4. MCP search

## 2. MCP промпт / Prompt
```
RU: "Скачай 10 PBR 2k ambientCG+PolyHaven: concrete/wood/metal/fabric + 3 HDRI studio" / EN: "Download 10 free 2k PBR ambientCG+PolyHaven + 3 studio HDRIs"
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

### Источники
- Poly Haven (CC0): textures + HDRIs, API без ключа.
- ambientCG (CC0): `https://ambientcg.com/api/v2/downloads` batch.

### Структура пачки
```
//assets/pbr/{surface}/2k/{surface}_2k_{map}.png
//assets/hdri/{name}_{res}.hdr
```

### Проверка каждой текстуры
- [ ] Все карты одного разрешения
- [ ] Normal OpenGL (не DirectX)
- [ ] Roughness/metallic Non-Color

