---
id: setup_42_tripo_ai_api
lang: ru
category: setups
status: full
---
# SETUP 42: TRIPO AI API

**ID:** SETUP-42 | **Type:** Text/Image-to-3D | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Tripo генерация. EN: Tripo generation.

## 1. Шаги / Steps
1. Tripo 2.5
2. Image+text prompt
3. PBR+rig
4. GLB/USDZ

## 2. MCP промпт / Prompt
```
RU: "Tripo API: image-to-3D + text refine 'worn leather', PBR, auto-rig quad" / EN: "Tripo API: image-to-3D + 'worn leather' refine, PBR, auto-rig"
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

### API setup
1. Ключ: https://platform.tripo3d.ai/ → API Keys.
2. Endpoint: `POST /v2/openapi/task` с `type: text_to_model` или `image_to_model`.
3. Poll `GET /v2/openapi/task/{id}` до `status: success`.
4. Скачай `model.glb` + `textures/*.png`.

### Параметры
| Параметр | Значение |
|----------|----------|
| mode | `high` для hero, `draft` для блокаута |
| texture | `true`, resolution 2048 |
| pbr | `true` (metallic/roughness/normal) |
| rig | `false` (риг отдельно Mixamo) |

### Blender cleanup
1. Import GLB → Apply scale → Recalculate normals.
2. Decimate до target tris → Smart UV (если UV грязные) → bake normal.
3. Материалы: Principled, BaseColor sRGB, остальные Non-Color.

