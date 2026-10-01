---
lang: ru
orig_lang: en
translation: ai
---
# ВОРКФЛОУ АНИМАЦИИ

## Обзор
Пайплайны риггинга, анимации и рендера в Blender.

---

## Риггинг

### Rigify (гуманоид)
```
1. Импортировать меш персонажа (T-pose или A-pose)
2. Добавить Armature → Human (Meta-Rig)
3. Отмасштабировать/сдвинуть мета-риг под меш
4. Сгенерировать риг (кнопки Rigify → Generate)
5. Parenting: Mesh → Armature (Automatic Weights)
6. При необходимости — чистка весов (weight paint)
```

### Auto-Rig Pro / Rigify Pro (продвинутый уровень)
- Лучше работают лицевые риги
- Переключение IK/FK
- Собственные формы костей

### Простой риг (реквизит/механика)
```
1. Добавить кости под каждую подвижную часть
2. Подчинить кости мешу (Bone Heat / Envelope)
3. Добавить ограничения: Copy Location/Rotation/Scale
4. Добавить драйверы под механические связи
```

---

## Анимация по ключам

### Базовый воркфлоу
```
1. Задать диапазон кадров: Scene → Frame Start/End
2. Поза на кадре 1 → вставить ключи (I → Location/Rotation/Scale)
3. Перейти на кадр 50 → Поза → вставить ключи
4. Graph Editor: почистить кривые, задать интерполяцию
5. Dope Sheet: подстроить тайминг
```

### Типы интерполяции
| Тип | Применение |
|-----|------------|
| Bezier | Плавное, естественное движение (по умолчанию) |
| Linear | Механическое движение, постоянная скорость |
| Constant | Удержание позы (ступенчато) |
| Elastic/Bounce | Мультяшные эффекты |

### Советы по Graph Editor
```
- T: меню интерполяции
- V: тип хендла (Auto, Vector, Aligned, Free)
- Shift+E: автоматическая подрезка хендлов
- Period (.) на нампаде: Frame selected
- Ctrl+Click: добавить ключ в позиции курсора
```

---

## NLA (нелинейная анимация)

### Action-стрипы
```
1. Создать actions: Walk, Run, Idle, Attack
2. NLA Editor → Push Down (stash) для каждого action
3. Смешивать стрипы: наложение для переходов
4. Extrapolation: Hold / Nothing / Repeat
5. Слоистые стрипы: аддитивные слои для деталей
```

### Воркфлоу
```
Base Layer: цикл ходьбы (repeat)
Layer 1: вариация взмаха рук (additive)
Layer 2: поворот головы (override)
Layer 3: мимика (override)
```

---

## Motion Capture / ретаргетинг

### Импорт BVH/FBX
```
1. File → Import → BVH / FBX
2. Создаётся арматура с анимацией
3. Ретаргетинг на ваш риг:
   - Добавить ограничения: Copy Rotation (цель — кость mocap)
   - Либо использовать аддон Retargeting (в Rigify он встроен)
```

### Воркфлоу ретаргетинга (Rigify)
```
1. Импортировать mocap → создаётся арматура "Mocap"
2. Выбрать свой риг Rigify
3. Bone Constraints → Copy Rotation → Target: кость Mocap
4. Bake Action (Pose → Animation → Bake Action)
5. Чистка: убрать ограничения, упростить ключи
```

---

## Процедурная анимация

### Драйверы
```python
# Драйвер: вращение шестерёнки от другой шестерёнки
# Выражение драйвера: -var * (teeth_a / teeth_b)

# Настройка через Python
driver = gear_b.driver_add('rotation_euler', 2).driver
driver.type = 'SCRIPTED'
var = driver.variables.new()
var.name = 'gear_a_rot'
var.targets[0].id = gear_a
var.targets[0].data_path = 'rotation_euler[2]'
driver.expression = '-gear_a_rot * 0.5'  # передаточное число 2:1
```

### Анимация в Geometry Nodes
```
1. Geometry Nodes → Object Info → взять анимируемый объект
2. Использовать номер кадра: #frame
3. Math-ноды для процедурного движения
4. Instance on points со смещением по анимации
```

### Симуляция (физика)
```
- Rigid Body: падающие объекты, разрушения
- Cloth: флаги, плащи, одежда
- Fluid: вода, дым, огонь
- Particles: магические эффекты, обломки, толпа
- Soft Body: желе, деформация плоти
```

---

## Анимация камеры

### Долли/кран
```
1. Добавить кривую (Bezier) под путь движения
2. Камера → ограничение Follow Path
3. Empty-цель → ограничение Track To
4. Анимировать Curve Evaluation (0→1 по кадрам)
```

### Тряска от руки
```
1. Камера → добавить модификатор Noise (Graph Editor)
2. Scale: 0.01-0.05, Strength: 0.1-0.5
3. Либо: Python-скрипт для процедурной тряски
```

### DOF (глубина резкости)
```
1. Камера → Depth of Field → Focus Object: целевой Empty
2. F-Stop: 1.4-2.8 (малая глубина) / 8-16 (большая)
3. Анимировать Focus Distance для перевода фокуса
```

---

## Рендер анимации

### Настройки
```python
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 250
scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Вывод
scene.render.filepath = "//renders/anim_####.png"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 15
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.5
scene.render.motion_blur_samples = 16
```

### Motion Blur
```
Cycles:
- Render → Motion Blur → Position: Center/Start/End
- Shutter: 0.5 (шторка 180°)
- Samples: 16+ для качества

EEVEE:
- Render → Motion Blur → включить
- Steps: 8-16
```

### Сборка кадров в видео
```bash
# Отрендерить кадры
blender -b scene.blend -E CYCLES -o //renders/frame_#### -f 1..250

# Скодировать в видео (ffmpeg)
ffmpeg -framerate 24 -i //renders/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Либо в Blender: Video Sequencer → Add → Image Sequence → Export FFmpeg
```

---

## Alembic-кэш (пайплайн)

### Экспорт
```python
bpy.ops.wm.alembic_export(
    filepath="animation.abc",
    start=1, end=250,
    selected=True,
    flatten=True,
    subsamples=4
)
```

### Импорт
```python
bpy.ops.wm.alembic_import(
    filepath="animation.abc",
    as_background_job=False
)
```

---

## Анимация толпы

### Инстансинг частицами
```
1. Плоскость-эмиттер → Particle System (Hair)
2. Render → Object → Collection (выбрать коллекцию с персонажем)
3. Advanced → Rotation: Velocity/Random
4. Scale: Random 0.9-1.1
5. Использовать инстансы коллекции для разнообразия
```

### Толпа на Geometry Nodes
```
1. Сетка точек
2. Случайно выбрать персонажа из коллекции
3. Инстансировать со случайным смещением по анимации
4. Look-at цель для направления
```

---

## Синхронизация губ

### Papagayo / Rhubarb
```
1. Аудио → Rhubarb Lip Sync → .json/.tsv
2. Импорт в Blender (аддон Papagayo или свой скрипт)
3. Сопоставить фонемы с shape keys
4. Запечь в анимацию shape keys
```

### Настройка Shape Keys
```
1. Создать basis + фонемные формы (A, E, I, O, U, M и т. д.)
2. Управлять каждым shape key с дорожки фонем
3. Сгладить в Graph Editor
```

---

## Экспорт для игровых движков

### Unity/Unreal (FBX)
```python
bpy.ops.export_scene.fbx(
    filepath="character.fbx",
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL',
    bake_space_transform=True,
    object_types={'ARMATURE', 'MESH'},
    use_armature_deform_only=True,
    add_leaf_bones=False,
    primary_bone_axis='Y_FORWARD',
    secondary_bone_axis='X_UP'
)
```

### Веб (GLTF)
```python
bpy.ops.export_scene.gltf(
    filepath="character.glb",
    export_format='GLB',
    use_selection=True,
    export_animations=True,
    export_frame_range=True,
    export_frame_step=1,
    export_force_sampling=True,
    export_skins=True,
    export_morph=True
)
```

---

## Советы по производительности

### Оптимизация анимации
```
- Меньше ключей: упрощать кривые (Graph Editor → Key → Simplify)
- Использовать actions для переиспользуемых циклов
- Запекать физику в ключи для рендер-фермы
- Прокси/low-res меши для анимации во вьюпорте
- Скрывать тяжёлые коллекции на время анимации
```

### Рендер-ферма
```
1. Раздать кадры по машинам
2. Использовать Flamenco (рендер-ферма Blender) или Deadline
3. Общее хранилище для ассетов
4. Alembic-кэши для данных симуляции
5. Собрать → скодировать → проверить
```

---

## Анимация с ИИ (через MCP)

### Примеры промптов
```
"Animate camera: 360° orbit around object over 120 frames, ease in/out"
"Create walk cycle for rigged character: 24 frames, loop seamlessly"
"Add noise modifier to camera rotation for handheld feel"
"Set up DOF rack focus from object A to B over 60 frames"
"Create particle explosion at frame 50, 200 particles, 2 second life"
"Bake rigid body simulation for 100 falling boxes to keyframes"
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](../api/scripting-patterns.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md)
- **По темам:** [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [CASE 04: CHARACTER RIG & ANIMATION](../../../cases/case_04_character_rig.md), [CASE 06: ANIMATION LOOP](../../../cases/case_06_animation_loop.md)
- **Теги:** #animation, #frame, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

