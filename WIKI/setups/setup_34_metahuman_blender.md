---
id: setup_34_metahuman_blender
lang: ru
category: setups
type: setup
status: full
tags: [blender, character, setup]
---
# SETUP 34: METAHUMAN → BLENDER

**ID:** SETUP-34 | **Type:** MetaHuman | **Difficulty:** ⭐⭐⭐ | **Time:** 60 min
**RU/EN Bilingual**

> Когда применять: персонаж MetaHuman сделан в MetaHuman Creator и нужно отрендерить его в Blender или вытащить в другой движок.

## 🎯 ЦЕЛЬ
Провести MetaHuman в Blender по официальному пути (MetaHuman Creator → Unreal Engine → Quixel Bridge → FBX) и собрать рабочий материал в Principled BSDF. Отдельно разбираем то, что Epic не поддерживает официально: волосы (groom), материалы и LOD — там нужен ручной обход, и честное описание этого обхода полезнее обещаний «одной кнопкой».

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| MetaHuman Creator | в браузере, актуальный | создание персонажа |
| Unreal Engine | 5.x | обязательный посредник: MetaHuman живёт в UE |
| Quixel Bridge | плагин для UE | импорт MetaHuman и экспорт в Blender |
| Blender | 4.x | сборка материалов и рендер |

> [!NOTE]
> Официального аддона Epic для Blender не существует: MetaHuman — актив внутри Unreal Engine, а не формат. Всё, что ниже, — это связка UE + Bridge + FBX, а не «импорт MetaHuman в Blender». Если где-то обещают прямой импорт, стоит уточнить, чей это код и какой у него статус поддержки.

## 🛠️ НАСТРОЙКА

### 1. Создание персонажа
MetaHuman Creator работает в браузере: собираешь лицо и тело, применяешь материал из библиотеки, выбираешь уровень детализации. На выходе — акты в Content Browser проекта Unreal.

```text
1. MetaHuman Creator в браузере → собрать лицо/тело
2. Export to Unreal Engine → выбрать проект UE и качество (Nanite / нет)
3. В UE: Content → готовые ассеты персонажа (Body, Face, Eyelashes, Hair)
4. Для каждого ассета: LOD-уровни создаются автоматически
```

### 2. Установка Bridge для UE
```text
1. Quixel Bridge ставится из Epic Games Launcher как плагин к вашему UE
2. В UE: Window → Quixel Bridge → Launch → вкладка сцены
3. Авторизация через аккаунт Epic
```

> [!NOTE]
> Quixel Bridge периодически переписывается, а часть функций переезжала между плагинами и встроенными инструментами UE. Перед тем как строить на нём пайплайн, открой его в своей версии UE и посмотри, есть ли вкладка экспорта в Blender: если её нет, работай через обычный FBX-экспорт из UE.

### 3. Экспорт из UE в FBX
```text
1. В Content Browser выбрать ассет персонажа
2. Bridge → Export → выбрать целевой путь и набор ассетов
   (Body LOD0..LOD4, Face, Eyelashes)
3. Формат: FBX, Include → Meshes / Skeletal Meshes
4. Настройки: Import into Scene выключить, если работаешь через файл
```
Если Bridge не даёт экспорт — тот же результат даёт стандартный экспорт UE: выделить Static/Skeletal Mesh → Asset Actions → Export → FBX.

### 4. Импорт в Blender и базовая проверка
```python
import bpy

bpy.ops.import_scene.fbx(
    filepath=r"C:\work\metahuman\mh_body_LOD0.fbx",
    automatic_bone_orientation=True,
    use_anim=False,
    mesh_smooth_type='FACE',
)

for o in bpy.data.objects:
    if o.type == 'MESH':
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        print(f"{o.name}: вершин={len(o.data.vertices)} треугольников={tris}")
    elif o.type == 'ARMATURE':
        print(f"{o.name}: костей={len(o.data.bones)}")
```

### 5. Материалы: главный объём работы
MetaHuman использует собственный шейдер на текстурах, в Blender его нет. Карты (albedo, normal, roughness, RMA) приезжают файлами, шейдер собирается вручную.

```python
import bpy

def build_skin_material(name, base_color_path, normal_path, rma_path):
    """Собрать кожу MetaHuman из карт. RMA = R:ao G:roughness B:metallic."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

    def tex(path):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(path, check_existing=True)
        n.location = (-800, 0)
        return n

    nt.links.new(tex(base_color_path).outputs['Color'],
                 bsdf.inputs['Base Color'])
    nt.links.new(tex(normal_path).outputs['Color'],
                 bsdf.inputs['Normal'])

    # RMA -> отдельные каналы
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    sep.location = (-500, -200)
    nt.links.new(tex(rma_path).outputs['Color'], sep.inputs['Color'])
    nt.links.new(sep.outputs['Green'], bsdf.inputs['Roughness'])   # G = roughness
    nt.links.new(sep.outputs['Blue'], bsdf.inputs['Metallic'])     # B = metallic
    return mat
```

> [!NOTE]
> Сокеты Principled BSDF переименовывались в Blender 4.x (`Subsurface` → `Subsurface Weight`, `Specular` → `Specular IOR Level`, `Emission` → `Emission Color`). Прежде чем соединять ноды кодом, выведи список: `print([s.name for s in bsdf.inputs])`.

### 6. Нормали: проверка обязательна
MetaHuman запекает нормали в карты с перевёрнутым зелёным каналом под DirectX. В Blender по умолчанию OpenGL, поэтому зелёный канал надо инвертировать — иначе всё будет «в пузырях».

```python
n = bpy.data.images.load(r"C:\work\metahuman\textures\body_nrm.png",
                         check_existing=True)
n.colorspace_settings.name = 'Non-Color'
print("colorspace:", n.colorspace_settings.name,
      "| alpha_mode:", n.alpha_mode)
```
Инверсия делается нодой **RGB to BW → Invert** либо переключателем цветового пространства; какой именно путь выбрал твой пайплайн — вопрос вкуса, результат один.

### 7. Волосы (groom)
Самый болезненный пункт. Волосы MetaHuman — groom-ассеты UE, в Blender их нет.

| Вариант | Что получится | Цена |
|---|---|---|
| Оставить без волос | лысый персонаж | 0 |
| Конвертировать groom в кривые в UE и выгрузить | отдельный объект кривых, без физ-привязки к голове | высокая, геометрия тяжёлая |
| Взять готовую причёску из стока | согласованный вид, но не «тот самой» MetaHuman | средняя |

> [!NOTE]
> Переход «Groom → Curves» есть в Unreal, и получившиеся кривые можно выгрузить через FBX. Но качество сильно зависит от настроек конвертации, и результат не эквивалентен groom-ассету UE. Не рассчитывай на round-trip.

### 8. LOD
```python
def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)

for name in ("mh_body_LOD0", "mh_body_LOD1", "mh_body_LOD2"):
    o = bpy.data.objects.get(name)
    print(name, "→", tris(o) if o else "нет объекта")
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Итог перед рендером: материалы, текстуры, бюджет геометрии
print("материалов:", len(bpy.data.materials))
print("изображений:", len(bpy.data.images))
for img in bpy.data.images:
    if img.source == 'FILE':
        print(f"  {img.name} {tuple(img.size)} {img.colorspace_settings.name}")
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `image.colorspace_settings.name` | `Non-Color` для карт данных | `sRGB` только для цветных карт (albedo) |
| LOD | `LOD0` для рендера | `LOD2`/`LOD3` — для превью и реального времени |
| `mesh_smooth_type` | `FACE` | `EDGE` — когда нужны хард-нормали |
| RMA-разделение | `R`=AO, `G`=roughness, `B`=metallic | у MetaHuman раскладка именно такая |
| Принципиал 4.x | сокеты с новыми именами | сверяться по выводу `bsdf.inputs` |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Экспорт в Blender недоступен в Bridge | функция переехала или изменился плагин | Экспортировать FBX стандартными средствами UE |
| Нет волос | groom — формат UE, не Blender | Конвертировать в кривые в UE либо взять стоковую причёску |
| Кожа в «пузырях» | зелёный канал нормалей не инвертирован | Инвертировать G или включить DirectX-трактовку |
| Металлический или стеклянный вид | каналы RMA перепутаны | Проверить раскладку: G=roughness, B=metallic |
| `KeyError` при обращении к сокету | сокет переименован в 4.x | Вывести `[s.name for s in bsdf.inputs]` и соединять по факту |
| Текстуры фиолетовые | для карт данных стоит sRGB | Поставить `Non-Color` |
| Анимация не едет | FBX выгружен без скелета | Экспортировать Skeletal Mesh, а не Static Mesh |
| Файл сцены весит сотни мегабайнут | втянуты все LOD и микротекстуры | Оставить LOD0–LOD2, крупные карты вынести наружу |

## 🖥 MCP-ПРОМПТ

```text
RU: "Собери материал кожи MetaHuman из albedo/normal/RMA,
     поставь Non-Color на карты данных, выведи LOD-бюджет треугольников" /
EN: "Build a MetaHuman skin material from albedo/normal/RMA,
     set Non-Color on data maps, print LOD triangle budgets"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 32: DAZ → BLENDER (DIFFEOMORPHIC)](setup_32_daz_diffeomorphic.md), [SETUP 36: VROID STUDIO → BLENDER](setup_36_vroid_studio.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #blender, #character, #setup