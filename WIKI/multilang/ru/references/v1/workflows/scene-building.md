---
lang: ru
orig_lang: en
translation: ai
---
# ВОРКФЛОУ — ПРОИЗВОДСТВЕННЫЕ ПАЙПЛАЙНЫ

## Воркфлоу 1: Генерация сцены из текста

### Через GenesisCore (чат внутри Blender)
```
1. Откройте Blender → N-панель → GenesisCore
2. Настройте OpenRouter + модель (DeepSeek/Qwen)
3. Включите инструменты: Common, Object, Material, Polyhaven
4. Последовательность промптов:
   
   "Create a cyberpunk alley scene:
   - Wet pavement plane 20x20m
   - Neon signs using emission materials (cyan, magenta, yellow)
   - Steam particles from grates
   - Hovering vehicle (simple primitive shapes)
   - Search Poly Haven for 'urban' HDRI at 2k, set as world
   - Camera: low angle looking down alley, 35mm lens"
```

### Через blender-mcp (внешний ИИ)
```
Промпт для OpenCode/Claude:
"Build a cyberpunk alley scene in Blender:
1. Create 20x20m plane for wet pavement at z=0
2. Add emission materials for neon signs (cyan, magenta, yellow) on cubes
3. Create particle system for steam on plane areas
4. Build simple hovering vehicle from primitives
5. Search Poly Haven for 'urban' HDRI, download 2k, set as world
6. Add camera at (-5, -10, 3) looking at (0,0,1), 35mm lens
7. Set render to Cycles, 256 samples, denoising on"
```

---

## Воркфлоу 2: Пайплайн генерации текстур

### Связка GenesisCore + Dream Textures
```
Фаза 1 — Геометрия (GenesisCore):
"Create a medieval castle wall section: 
- 10x5m stone wall with crenellations
- Wooden door with iron hinges
- Arrow slits as boolean cutouts
- Stone floor tiles"

Фаза 2 — Материалы (Dream Textures):
1. Выберите объект стены → N-панель → Dream Textures
2. Сгенерировать: "weathered medieval stone wall, moss in cracks, seamless" 
   → Check Seamless → Generate → Apply
3. Выберите дверь → "aged oak wood, iron studs, seamless" → Apply
4. Выберите пол → "cobblestone pathway, worn, seamless" → Apply

Фаза 3 — Полировка (GenesisCore):
"Add vertex paint for moss variation on wall
Add geometry nodes for procedural ivy on top edges
Set up 3-point lighting for texture showcase"
```

### Только Dream Textures (проекция текстур)
```
1. Смоделируйте базовую геометрию (стена, пол, реквизит)
2. Выделите все грани под текстурирование
3. Войдите в Local View (/)
4. Dream Textures → Project Dream Texture
5. Промпт: "ancient dungeon corridor, stone bricks, torch lighting, moss"
6. Модель: stabilityai/stable-diffusion-2-depth
7. Нажмите Project Dream Texture
8. UV корректируются автоматически
```

---

## Воркфлоу 3: Сборка сцены из готовых ассетов

### Poly Haven + Poly Pizza + Sketchfab
```
"Create a cozy library scene using free assets:

1. Poly Haven:
   - Search models: 'bookshelf', 'wooden chair', 'desk lamp'
   - Search HDRI: 'library', 'indoor', 2k
   - Download all at 2k

2. Poly Pizza (low-poly fill):
   - Search: 'book', 'scroll', 'candle', 'potion bottle'
   - Licence: CC0 (no attribution)
   - Download, normalize_size=1.0, target_size=0.15

3. Sketchfab (hero pieces):
   - Search: 'ornate desk', 'grandfather clock'
   - Get preview, download at target_size=1.5m

4. Assembly:
   - Position bookshelves along walls
   - Scatter Poly Pizza books on shelves (random rotation)
   - Place hero desk center, chair beside
   - Add HDRI as world environment
   - Add area lights for desk lamp, candle glow
   - Camera: wide angle from doorway"
```

---

## Воркфлоу 4: Генерация 3D средствами ИИ + чистка

### Hyper3D Rodin / Hunyuan3D
```
"Generate a fantasy creature concept:
1. Create Hyper3D job: 'dragon whelp, cute, stylized, low poly'
2. Poll status every 30s until complete
3. Import result
4. Cleanup:
   - Decimate modifier (ratio 0.3) for game-ready
   - Separate loose parts (P → By Loose Parts)
   - Create materials for each part (scales, eyes, horns)
   - UV unwrap (Smart UV Project)
   - Bake normal map from high-poly (if needed)
5. Rig: Add armature, auto-weight, basic pose"
```

---

## Воркфлоу 5: Процедурная генерация на Geometry Nodes

### Генератор городского квартала
```
"Create Geometry Nodes setup for procedural city block:

1. Base grid: 10x10, 20m spacing
2. Building height: random 10-50m (seed controlled)
3. Building shape: extruded random polygons
4. Windows: array on faces, random offset
5. Roofs: flat/hipped/gabled (weighted random)
6. Street level: sidewalk, road markings, lamps
7. Variations: 
   - Park lots (empty with trees)
   - Plaza (fountain + benches)
   - Alleyways (dumpsters, fire escapes)

Controls exposed in modifier panel:
- Seed, Block Size, Density, Height Range, Style Mix"
```

### Blender Python для Geometry Nodes
```python
# Выполнять через execute_blender_code
import bpy

ng = bpy.data.node_groups.new("CityBlock", 'GeometryNodeTree')
# ... программная сборка дерева нод ...
# API Geometry Nodes см. в api/blender-api.md
```

---

## Воркфлоу 6: Анимация и риггинг

### Пайплайн анимации персонажа
```
1. Импорт/генерация персонажа (Mixamo, Hyper3D, вручную)
2. Rigify:
   - Добавить мета-риг Rigify (Human)
   - Подогнать кости под меш
   - Сгенерировать риг
   - Parenting с автоматическими весами
3. Анимация:
   - Импорт motion capture (BVH/FBX)
   - Ретargeting на Rigify
   - Чистка: NLA-стрипы, слои action
4. Экспорт:
   - FBX для игровых движков
   - GLTF для веба
   - Alembic для кэша симуляции
```

### Анимация камеры
```
"Create cinematic camera path:
1. Add Bezier curve for dolly path
2. Add camera, Follow Path constraint
3. Add Empty for target, Track To constraint
4. Animate curve evaluation (0-1 over frames)
5. Add DOF: focus on target Empty, f-stop 1.8
6. Motion blur: Cycles → 0.5 shutter, 16 samples"
```

---

## Воркфлоу 7: Оптимизация под real-time

### Пайплайн игрового ассета
```
Вход: high-poly модель (Sketchfab/Hyper3D/вручную)

1. Ретопология:
   - Instant Meshes / Quad Remesher
   - Цель: 1-5k трисов (пропсы), 10-30k (персонажи)

2. UV Unwrap:
   - Швы на жёстких рёбрах
   - Упаковка островов (margin 0.005)
   - UDIM при текстурах >4k

3. Запекание (Cycles):
   - Normal (Tangent Space, 4k)
   - AO (16 samples, 4k)
   - Curvature (4k)
   - Position (для масок)
   - Material ID

4. Текстурирование (Substance/Blender):
   - PBR-воркфлоу metal/rough
   - Смарт-материалы + кастомные детали

5. Экспорт:
   - GLTF: раздельные текстуры, сжатие Draco
   - Проверка: gltf-transform inspect
   - LOD: 100%, 50%, 25%, 10% от числа полигонов
```

---

## Воркфлоу 8: Пакетная обработка / автоматизация

### Настройка рендер-фермы
```
# Рендер через Blender CLI
blender -b scene.blend -E CYCLES -o //render/frame_#### -f 1..250

# Распределённый рендер (Flamenco или своя реализация)
# 1. Раздать кадры по машинам
# 2. Синхронизировать ассеты через общее хранилище
# 3. Собрать результат
```

### Шаблон пакетного скрипта на Python
```python
# Запуск: blender -b -P batch_script.py

import bpy
import sys

def process_scene(scene_path, output_dir):
    bpy.ops.wm.open_mainfile(filepath=scene_path)
    
    scene = bpy.context.scene
    scene.render.filepath = output_dir
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    
    bpy.ops.render.render(animation=True, write_still=False)
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    # Аргументы после --
    argv = sys.argv[sys.argv.index("--")+1:]
    process_scene(argv[0], argv[1])
```

---

## Воркфлоу 9: Контроль версий для .blend

### Настройка Git LFS
```bash
# .gitattributes
*.blend filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.hdr filter=lfs diff=lfs merge=lfs -text
*.exr filter=lfs diff=lfs merge=lfs -text
*.glb filter=lfs diff=lfs merge=lfs -text
*.gltf filter=lfs diff=lfs merge=lfs -text

# Инициализация
git lfs install
git lfs track "*.blend" "*.png" "*.hdr" "*.exr" "*.glb"
git add .gitattributes
```

### Diff .blend-файлов
```bash
# Используйте blendfile-utils или собственный скрипт
# Для осмысленного diff экспортируйте в обменный формат:
blender -b scene.blend -P export_gltf.py
# Затем diff по .gltf (JSON)
```

---

## Матрица решений: какой инструмент когда?

| Задача | Основной инструмент | Запасной вариант |
|--------|---------------------|------------------|
| Быстрая геометрия | Чат GenesisCore | blender-mcp |
| Сложная логика сцены | blender-mcp + Codex/Claude | GenesisCore |
| Генерация текстур | Dream Textures | Текстуры Poly Haven |
| Ключевые ассеты | Sketchfab / Hyper3D | Ручное моделирование |
| Фоновый реквизит | Poly Pizza | Модели Poly Haven |
| HDRI-освещение | Poly Haven (оба) | Poly Haven |
| Автоматизация кодом | execute_blender_code | Geometry Nodes |
| Игровые ассеты | Dream Textures + Retopo | Substance Painter |
| Анимация | Rigify + NLA | Ручные ключи |
| Пакетный рендер | CLI + Flamenco | Вручную |

---

## Советы по надёжной автоматизации

1. **Всегда проверяйте перед действием:** `get_scene_info` → план → выполнение
2. **Используйте именованные объекты:** явные имена > «куб, который я только что сделал»
3. **Проверяйте режим:** перед трансформациями убедитесь, что включён режим `OBJECT`
4. **Применяйте масштаб:** `Ctrl+A → Scale` до bevel/array/модификаторов
5. **Уникальные данные:** при дублировании мешей используйте `.copy()`
6. **Сохраняйтесь инкрементально:** `bpy.ops.wm.save_as_mainfile(filepath="scene_v001.blend")`
7. **Используйте коллекции:** группируйте по типу (Geometry, Lights, Cameras, FX)

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [TEXT-TO-3D WORKFLOWS](text-to-3d.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md)
- **По темам:** [P18: DRIVERS & CONSTRAINTS](../../../prompts/18_drivers_constraints.md), [P45: GEOMETRY NODES SIMULATION ZONES](../../../prompts/45_gn_simulation.md), [SETUP 35: READY PLAYER ME AVATARS](../../../setups/setup_35_readyplayerme.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](../../../setups/setup_45_hunyuan3d_21.md)
- **Теги:** #ai-3d, #animation, #assets, #automation, #blender, #geometry-nodes, #mcp, #modeling

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

