---
lang: ru
orig_lang: en
translation: ai
---
# ВОРКФЛОУ ГЕНЕРАЦИИ ТЕКСТУР

## Обзор
Несколько подходов к созданию PBR-текстур и материалов.

---

## Метод 1: Dream Textures (локальный Stable Diffusion)
**Лучше всего для:** собственных текстур, бесшовного тайлинга, инпейнтинга, проекции
**Стоимость:** бесплатно (локальный GPU)
**Качество:** высокое, полный контроль

### Базовая генерация текстуры
```
1. Выберите объект → N-панель → Dream Textures
2. Вкладка: "Generate Texture"
3. Промпт: "weathered brick wall, moss in cracks, seamless"
4. Отметить: "Seamless" (для тайлинга)
5. Модель: stabilityai/stable-diffusion-2-1-base
6. Размер: 512x512 (или 1024x1024, если хватает VRAM)
7. Нажать: Generate
8. Нажать: "Apply to Material" или перетащить в ноды шейдера
```

### Проекция текстуры (Depth-to-Image)
```
1. Смоделируйте геометрию (стена, пол, персонаж)
2. Выделите грани под текстурирование (Edit Mode → Select faces)
3. Local View (/) — изолировать объект
4. Dream Textures → "Project Dream Texture"
5. Модель: stabilityai/stable-diffusion-2-depth (REQUIRED)
6. Промпт: "ancient stone temple, moss, cracks, torch lighting"
7. Data Source: "Depth" или "Depth and Color"
8. Нажать: Project Dream Texture
9. Автоматически создаёт материал + UV
```

### Инпейнтинг (исправление швов / правка)
```
1. Откройте сгенерированную текстуру в Image Editor
2. Замаскируйте проблемную область (brush tool)
3. Dream Textures → Inpaint
4. Промпт: "seamless continuation of stone texture"
5. Генерирует только замаскированную область
```

### Аутпейнтинг (расширение текстуры)
```
1. Image Editor → выберите текстуру
2. Dream Textures → Outpaint
3. Выберите начало отсчёта (центр, край, угол)
3. Промпт: "extend brick wall pattern"
4. Увеличивает размер холста
```

### Ре-стилизация через render pass
```
1. Настройте сцену Cycles с базовым освещением
2. Добавьте ноду "Dream Texture" в Compositor
3. Соедините Render Layers → Dream Texture → Composite
4. Промпт: "cyberpunk neon, volumetric fog, photorealistic"
5. Повторный рендер → ИИ преобразует каждый кадр
```

### Апскейл средствами ИИ
```
1. Текстура в низком разрешении (512x512)
2. Dream Textures → Upscale
3. Модель: stabilityai/stable-diffusion-x4-upscaler
4. Выход: 2048x2048
```

---

## Метод 2: Poly Haven Textures (бесплатно, отобрано вручную)
**Лучше всего для:** готовых к продакшену PBR, стабильного качества
**Стоимость:** бесплатно (CC0)
**Качество:** профессиональное, 1k-8k

### Воркфлоу (через blender-mcp / GenesisCore)
```bash
# Через ИИ:
"Search Poly Haven textures for 'metal' category 'rusted' at 2k resolution
Download 'RustedIron' and apply to object 'Pipe'"

# Шаги:
1. search_polyhaven_assets(asset_type="textures", categories="metal")
2. download_polyhaven_asset(asset_id="RustedIron", asset_type="textures", resolution="2k")
3. set_texture(object_name="Pipe", texture_id="RustedIron")
```

### Какие карты входят в набор
- Base Color (Diffuse) — базовый цвет
- Roughness — шероховатость
- Normal (OpenGL) — нормали
- Metallic — металличность
- AO (Ambient Occlusion) — затенение окружения
- Height/Displacement — высота/смещение

### Варианты разрешения
| Разрешение | Применение |
|------------|------------|
| 1k | Превью, мобильные устройства, фон |
| 2k | Стандартный продакшен |
| 4k | Ключевые ассеты, крупные планы |
| 8k | Предельная детализация, кино |

---

## Метод 3: Процедурный / нодовый (средства самого Blender)
**Лучше всего для:** бесконечного разнообразия, параметричности, GPU не требуется
**Стоимость:** бесплатно
**Качество:** математическая точность

### Паттерн на шуме Вороного
```python
# Выполнять через execute_blender_code
import bpy

mat = bpy.data.materials.new("ProceduralMetal")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Ноды
output = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
voronoi = nodes.new('ShaderNodeTexVoronoi')
color_ramp = nodes.new('ShaderNodeValToRGB')
mapping = nodes.new('ShaderNodeMapping')
tex_coord = nodes.new('ShaderNodeTexCoord')

# Раскладка
tex_coord.location = (-600, 0)
mapping.location = (-400, 0)
voronoi.location = (-200, 0)
color_ramp.location = (0, 0)
principled.location = (200, 0)
output.location = (400, 0)

# Настройка
voronoi.feature = 'SMOOTH_F1'
voronoi.metric = 'MANHATTAN'
color_ramp.color_ramp.elements[0].position = 0.3
color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1)
color_ramp.color_ramp.elements[1].position = 0.7
color_ramp.color_ramp.elements[1].color = (0.8, 0.7, 0.6, 1)

# Связи
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
links.new(voronoi.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(voronoi.outputs['Distance'], principled.inputs['Roughness'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Анимировать масштаб mapping
mapping.inputs['Scale'].default_value = (5, 5, 5)
```

### Генератор кирпича (Geometry Nodes → текстура)
```python
# Создаёт процедурный кирпичный паттерн с раствором
# Через Geometry Nodes генерируется меш → запекается в текстуру
```

---

## Метод 4: Dream Textures + Poly Haven (гибрид)
**Лучше всего для:** ключевых ассетов с собственными деталями на отобранной базе

### Воркфлоу
```
1. База: скачать Poly Haven "ConcreteFloor01" (набор PBR 2k)
2. Доработка: Dream Textures Inpaint
   - Замаскировать области под "cracks with glowing moss"
   - "painted graffiti symbols"
   - "water puddles with reflections"
3. Запекание: объединить в единый набор текстур
4. Применение: один материал со всеми картами
```

---

## Метод 5: Substance / внешние инструменты
**Лучше всего для:** AAA-продакшена, командных пайплайнов
**Стоимость:** подписка
**Интеграция:** экспорт из Blender → Substance → импорт

### Пайплайн
```
1. Blender: моделирование + UV unwrap
2. Экспорт: GLTF/FBX с UV
3. Substance Painter: смарт-материалы + кастом
4. Экспорт: PBR-карты (4k)
5. Blender: импорт карт → настройка Principled BSDF
```

---

## Настройка PBR-материала (стандарт)

### Соединения Principled BSDF
```
Image Texture (Base Color) ──────────────────→ Base Color
Image Texture (Roughness) ──────────────────→ Roughness (Color Space: Non-Color)
Image Texture (Normal) → Normal Map ────────→ Normal
Image Texture (Metallic) ───────────────────→ Metallic (Non-Color)
Image Texture (Height) → Displacement ──────→ Displacement (Material Settings)
Image Texture (AO) ─────────────────────────→ Mix with Base Color (Multiply)
```

### Скрипт для сборки нод
```python
# Выполнять через execute_blender_code
import bpy

def setup_pbr_material(obj, name, maps_dict):
    """maps_dict: {'base_color': img, 'roughness': img, 'normal': img, ...}"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Base Color
    if 'base_color' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['base_color']
        tex.image.colorspace_settings.name = 'sRGB'
        links.new(tex.outputs['Color'], principled.inputs['Base Color'])
    
    # Roughness
    if 'roughness' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['roughness']
        tex.image.colorspace_settings.name = 'Non-Color'
        links.new(tex.outputs['Color'], principled.inputs['Roughness'])
    
    # Normal
    if 'normal' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['normal']
        tex.image.colorspace_settings.name = 'Non-Color'
        normal_map = nodes.new('ShaderNodeNormalMap')
        links.new(tex.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
    
    # Metallic
    if 'metallic' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['metallic']
        tex.image.colorspace_settings.name = 'Non-Color'
        links.new(tex.outputs['Color'], principled.inputs['Metallic'])
    
    # Height/Displacement
    if 'height' in maps_dict:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = maps_dict['height']
        tex.image.colorspace_settings.name = 'Non-Color'
        disp = nodes.new('ShaderNodeDisplacement')
        links.new(tex.outputs['Color'], disp.inputs['Height'])
        links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
        # Включить в Material Settings
        mat.displacement_method = 'BOTH'
    
    # Назначение материала
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat
```

---

## Рекомендации по разрешению текстур

| Тип ассета | Дистанция просмотра | Разрешение |
|------------|----------------------|------------|
| Ключевой пропс (hero) | Крупный план | 4k-8k |
| Персонаж | Средняя | 2k-4k |
| Окружение | Средняя | 2k |
| Фон | Дальняя | 1k-2k |
| Мобайл/веб | Любая | 1k-2k |
| VR/AR | Ближняя | 2k-4k |

---

## Советы по оптимизации

### Управление VRAM (Dream Textures)
```bash
# Preferences → Dream Textures:
- Precision: fp16 (по умолчанию)
- Speed: Half Precision
- Memory: Attention Slicing (Auto)
- Tile Size: 512 (для апскейла)
```

### Пакетная генерация текстур
```python
# Сгенерировать несколько вариантов
for i, prompt in enumerate(prompts):
    bpy.ops.dream_texture.generate(
        prompt=prompt,
        seed=i * 1000,
        width=512,
        height=512,
        seamless=True
    )
    # Сохранить каждый
    img = bpy.data.images[-1]
    img.filepath_raw = f"//textures/tex_{i:03d}.png"
    img.save()
```

### Соглашение по именам
```
{asset}_{map}_{resolution}.{ext}
Примеры:
- wall_basecolor_2k.png
- wall_roughness_2k.png
- wall_normal_2k.exr
- wall_height_2k.png
- wall_metallic_2k.png
- wall_ao_2k.png
```

---

## Решение проблем

| Проблема | Решение |
|----------|---------|
| Видны швы | включите "Seamless" в Dream Textures; прогоните Inpaint по краям |
| Размытая текстура | увеличьте разрешение; проверьте масштаб UV; возьмите модель качественнее |
| Неверные цвета | проверьте Color Space (sRGB vs Non-Color) у каждой карты |
| Перевёрнутые нормали | инвертируйте Y в ноде Normal Map; проверьте OpenGL vs DirectX |
| Displacement не работает | Material Settings → Displacement: "BOTH" или "Displacement Only" |
| OOM | снизьте разрешение; включите Attention Slicing; закройте другие программы |

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [ANIMATION WORKFLOWS](animation.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](../api/scripting-patterns.md)
- **По темам:** [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md), [CASE 03: PRODUCT VISUALIZATION](../../../cases/case_03_product_viz.md)
- **Теги:** #reference, #texturing

