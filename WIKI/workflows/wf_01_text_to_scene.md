---
id: wf_01_text_to_scene
lang: ru
category: workflows
status: full
tags: [assets, pipeline, render, workflow]
---
# WF 01: TEXT-TO-SCENE

**ID:** WF-01 | **Тип:** End-to-End Pipeline | **Сложность:** ⭐⭐ | **Время:** 15-30 мин

---

## 🎯 ЦЕЛЬ
Полный пайплайн: текстовое описание → 3D сцена (геометрия, материалы, свет, камера, рендер)

---

## 📋 АРХИТЕКТУРА ПАЙПЛАЙНА

```
USER PROMPT
    │
    ▼
┌─────────────────────────────────────┐
│  LLM AGENT (OpenCode/Claude)        │
│  - Парсит описание                  │
│  - Планирует шаги                   │
│  - Вызывает MCP tools               │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BLENDER-MCP SERVER (localhost:9876)│
│  - create_object                    │
│  - set_material                     │
│  - download_polyhaven_asset         │
│  - execute_blender_code             │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BLENDER (bpy execution)            │
│  - Geometry creation                │
│  - Material assignment              │
│  - Lighting setup                   │
│  - Camera positioning               │
│  - Render execution                 │
└─────────────────────────────────────┘
    │
    ▼
RESULT: Rendered image / .blend file / GLB export
```

---

## 📝 ПРИМЕРЫ ПРОМПТОВ

### Простой: Комната
```
"Создай комнату 5x5x3м: пол, 4 стены, потолок.
Добавь окно 1.5x1.5м в передней стене (boolean).
Материалы: стены - белая штукатурка, пол - паркет, окно - стекло.
Свет: HDRI 'studio' 2k от Poly Haven.
Камера: в углу, направлена в центр, 35mm.
Рендер: Cycles, 128 samples, 1920x1080, сохранить //renders/room.png"
```

### Средний: Игровая локация
```
"Создай данжон-комнату 10x10x5м в стиле dark fantasy.
Стены: каменная кладка с трещинами (PBR).
Пол: каменные плиты с мхом в щелях.
Реквизит: 3 колонны, 2 сундука, алтарь в центре.
Освещение: 3 точечных источника (огонь) + слабое HDRI 'dungeon'.
Частицы: пыль в лучах света (volume scatter).
Камера: низкий ракурс, DOF на алтаре.
Рендер: 256 samples, denoising ON"
```

### Сложный: Процедурный город
```
"Сгенерируй процедурный квартал 200x200м:
- Сетка 10x10 зданий, случайная высота 10-50м
- Архитектура: модернизм / неоклассика / футуризм (веса 40/30/30)
- Дороги между зданиями, тротуары, фонари каждые 20м
- Парки в 15% случаев вместо зданий
- HDRI 'city_day' 4k, солнечный свет
- LOD система: близкие здания высокополигональные, дальние - lowpoly
- Экспорт: GLB с LOD уровнями, текстуры 2k"
```

---

## 🔧 MCP КОМАНДЫ ПОЭТАПНО

### Этап 1: Базовая геометрия
```bash
# Очистка
"Удали все объекты кроме камеры и света"

# Пол
"Создай плоскость 'Floor' 10x10м в (0,0,0)"

# Стены (4 шт.)
"Создай куб 'Wall_Front' 10x0.2x3м в (0, -5, 1.5)"
"Создай куб 'Wall_Back' 10x0.2x3м в (0, 5, 1.5)"
"Создай куб 'Wall_Left' 0.2x10x3м в (-5, 0, 1.5)"
"Создай куб 'Wall_Right' 0.2x10x3м в (5, 0, 1.5)"

# Потолок
"Создай плоскость 'Ceiling' 10x10м в (0,0,3)"
```

### Этап 2: Булевы операции (окна/двери)
```bash
# Окно
"Создай куб 'Window_Cut' 2x0.3x1.5м в (0, -5.1, 1.5)
Вычти Window_Cut из Wall_Front (DIFFERENCE)"

# Дверь
"Создай куб 'Door_Cut' 1x0.3x2.2м в (-2, -5.1, 1.1)
Вычти Door_Cut из Wall_Front (DIFFERENCE)"
```

### Этап 3: Материалы
```bash
# Пол - паркет
"Создай материал 'Mat_Parquet': BaseColor #8B7355, Roughness 0.6, Metallic 0
Присвой к Floor"

# Стены - штукатурка
"Создай материал 'Mat_Plaster': BaseColor #F5F0E8, Roughness 0.85, Metallic 0
Присвой к Wall_Front, Wall_Back, Wall_Left, Wall_Right, Ceiling"

# Стекло
"Создай материал 'Mat_Glass': Transmission 1.0, IOR 1.45, Roughness 0
Присвой к окнам (если созданы отдельные объекты)"
```

### Этап 4: Ассеты из Poly Haven
```bash
# HDRI
"Найди на Poly Haven HDRI 'studio' категорию 'indoor' 2k
Скачай и поставь как World Environment"

# Модели (опционально)
"Найди на Poly Haven модель 'chair' категорию 'furniture' 1k
Скачай и размести 3 стула вокруг стола"
```

### Этап 5: Камера и рендер
```bash
# Камера
"Создай камеру 'Cam_Main' в (7, -7, 4) поворот (0.9, 0, 0.8)
Сделай активной: bpy.context.scene.camera = bpy.data.objects['Cam_Main']
Настрой: 35mm, DOF на объект в центре"

# Рендер
"Настрой Cycles: 128 samples, denoising ON, 1920x1080
Рендер и сохрани в //renders/scene_01.png"
```

---

## 🎯 ПАРАМЕТРЫ КАЧЕСТВА

| Уровень | Samples | Denoising | Resolution | Time (RTX 3080) |
|---------|---------|-----------|------------|-----------------|
| **Draft** | 32 | ON | 1280x720 | ~15 сек |
| **Preview** | 64 | ON | 1920x1080 | ~30 сек |
| **Final** | 128 | ON | 1920x1080 | ~1 мин |
| **Production** | 256 | ON + OptiX | 3840x2160 | ~5 мин |

---

## 💡 ПРО ТИПЫ

### Авто-сохранение промежуточных состояний
```python
# В execute_blender_code
import bpy
bpy.ops.wm.save_as_mainfile(filepath="//wip/scene_step_01.blend")
```

### Версионирование
```python
import datetime
version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bpy.ops.wm.save_as_mainfile(filepath=f"//versions/scene_v{version}.blend")
```

### Пакетный рендер вариантов
```python
variants = ["day", "night", "golden_hour"]
for variant in variants:
    # Сменить HDRI
    # Рендер
    bpy.context.scene.render.filepath = f"//renders/scene_{variant}.png"
    bpy.ops.render.render(write_still=True)
```

---

## ⚠️ ЧАСТЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

| Проблема | Причина | Решение |
|----------|---------|---------|
| Рендер чёрный | Нет света / камера неактивна | Проверить `bpy.context.scene.camera` и свет |
| Текстуры розовые | UV не развернуты | `Smart UV Project` перед материалами |
| Boolean не работает | Неверные нормали / non-manifold | `Recalculate Normals`, `Select Non-Manifold` |
| Память (OOM) | Слишком много полигонов | `Decimate`, уменьшить samples, tiling |
| Рендер завис | Бесконечный цикл в драйверах | Проверить drivers, ограничить время |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md), [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md)
- **Теги:** #assets, #pipeline, #render, #workflow

