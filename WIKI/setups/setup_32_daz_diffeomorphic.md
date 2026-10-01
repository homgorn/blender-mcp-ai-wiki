---
id: setup_32_daz_diffeomorphic
lang: ru
category: setups
type: setup
status: full
tags: [blender, character, setup]
---
# SETUP 32: DAZ → BLENDER (DIFFEOMORPHIC)

**ID:** SETUP-32 | **Type:** Daz Bridge | **Difficulty:** ⭐⭐ | **Time:** 45 min
**RU/EN Bilingual**

> Когда применять: работаешь с Daz Studio и хочешь переносить персонажа в Blender без потери морфов, JCM и волос.

## 🎯 ЦЕЛЬ
Настроить связку Daz Studio + аддон Diffeomorphic в Blender и провести персонажа из Daz в сцену: тело с морфами, коррекции суставов (JCM), волосы и одежда. Разбираем, где Diffeomorphic ускоряет работу, а где всё равно приходится доводить руками, потому что его цель — не «идеальный импорт», а рабочая связка двух программ.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Daz Studio | 4.x | источник персонажа и контент |
| Контент Daz | установленный через Daz Central / Install Manager | нужные гены, одежда, пресеты |
| Diffeomorphic | релиз под свою пару версий | аддон-мост в Blender |
| Blender | версия, поддержанная Diffeomorphic | цель импорта |
| Модели Daz | бесплатные стартовые модели | с чего начинать, чтобы проверить связку |

> [!NOTE]
> Diffeomorphic живёт в репозитории организации Diffeomorphic на GitHub и распространяется в виде скрипта-установщика, который запускается **из Daz Studio** (раздел скриптинга), а не копируется вручную в папку аддонов Blender. Точный способ запуска и требуемые версии — в README актуального релиза: связка версионно-чувствительная, и это её главная хрупкость.

## 🛠️ НАСТРОЙКА

### 1. Порядок установки
Порядок жёсткий, и нарушение даёт «аддон включился, но ничего не происходит».

1. Установить Daz Studio и хотя бы один пакет контента через Daz Central.
2. Убедиться, что персонаж открывается в Daz и выглядит нормально.
3. Запустить установщик Diffeomorphic **из Daz Studio**.
4. В Blender: `Edit → Preferences → Add-ons`, найти Diffeomorphic и включить.
5. Перезапустить Blender.

```python
import bpy

print("blender:", bpy.app.version_string)
print("daz/diff аддоны:",
      [k for k in bpy.context.preferences.addons.keys()
       if "daz" in k.lower() or "diffeo" in k.lower()])
```

### 2. Первичный экспорт из Daz
В Daz сохраняем сцену персонажа. Важно, что имя сцены и имя корня в Daz станут именами объектов в Blender — это единственный мост между ними.

```python
# Сцены Daz импортируются как отдельные коллекции в Blender
for c in bpy.data.collections:
    print(c.name, "->", len(c.objects), "объектов")
```

### 3. Импорт персонажа
Через панель Diffeomorphic в Blender выбирается нужная сцена из Daz. Основные переключатели, которые имеет смысл выставить сразу:

| Переключатель | Состояние | Смысл |
|---|---|---|
| Import face / body morphs | вкл | тянуть активные морфы лица и тела |
| Joint correction morphs (JCM) | вкл | смягчить «слом» на локтях и коленях |
| Shape keys вместо поз | как удобнее | иногда JCM проще приехать готовыми ключами |
| Materials | по необходимости | тянуть ли материалы UberSurface |

> [!NOTE]
> Конкретные названия чекбоксов в панели Diffeomorphic отличаются от перечисленных — они зависят от версии аддона. Открывай панель и читай подписи на месте; список выше дан по смыслу, а не как цитата из UI.

### 4. Проверка того, что пришло
```python
# Что должно быть в сцене после импорта
for o in bpy.data.objects:
    if o.type == 'MESH':
        keys = len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0
        print(f"{o.name}: вершин={len(o.data.vertices)} ключей={keys}")
    elif o.type == 'ARMATURE':
        print(f"{o.name}: костей={len(o.data.bones)}")

# Модификатор Armature на меше — признак того, что деформация подключена
for o in bpy.data.objects:
    if o.type == 'MESH':
        print(o.name, [m.type for m in o.modifiers])
```

### 5. Ручная доводка деформации
Даже с JCM на сгибах остаётся провал. Лечится либо весами, либо дополнительным модификатором.

```python
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')

# Dual quaternion: без него плечо и колено заметно «сжимаются»
for pb in arm.pose.bones:
    pb.use_deform_preserve_volume = True

# Плавная деформация поверх основной — классический приём для Daz-импорта
mesh_ob = next(o for o in bpy.data.objects
               if o.type == 'MESH' and len(o.data.vertices) > 5000)
sub = mesh_ob.modifiers.new("Subdiv_deform", 'SUBSURF')
sub.levels = 1
sub.render_levels = 2
```

### 6. Волосы
Волосы в Daz — генетический ассет, в Blender их надо конвертировать. Два направления:

```python
# Проверить, чем представлены волосы после импорта
for o in bpy.data.objects:
    if o.type in {'CURVE', 'SURFACE', 'MESH'}:
        mods = [m.type for m in o.modifiers]
        if 'PARTICLE_SYSTEM' in mods or 'CURVES' in mods:
            print(o.name, "→", mods)
```
Конвертация выполняется из панели Diffeomorphic: волосы переводятся либо в систему частиц, либо в кривые (curves). Выбор влияет на то, чем ты будешь их дальше красить и рендерить.

> [!NOTE]
> Точные названия пунктов конвертации волос («Particles» / «Curves» / «Hair Curves») менялись между версиями аддона вместе с переходом Blender на новую систему кривых. Открывай панель Diffeomorphic в своей сборке и выбирай там; в коде через bpy эти пункты вызывать не стоит — они часть UI аддона, а не стабильный API.

### 7. Одежда
```python
# Одежда в Daz — отдельные объекты со своей физикой; в Blender
# симуляцию придётся перенастраивать, веса из Daz не переносятся
cloth_like = [o.name for o in bpy.data.objects
              if o.type == 'MESH' and any(
                  m.type == 'CLOTH' for m in o.modifiers)]
print("объекты с физикой:", cloth_like)
```

### 8. Экспорт для движка
```python
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type in {'MESH', 'ARMATURE'}:
        o.select_set(True)
bpy.context.view_layer.objects.active = arm

bpy.ops.export_scene.fbx(
    filepath=r"C:\work\export\daz_char.fbx",
    use_selection=True,
    object_types={'MESH', 'ARMATURE'},
    apply_unit_scale=True,
    add_leaf_bones=False,
    mesh_smooth_type='FACE',
    path_mode='AUTO',
)
```
Морфы в FBX: если движку нужны blendshape-анимации лица, перенеси ключи формы как Blend Shapes через настройки экспорта и проверь, что целевой движок читает именно этот набор.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Итоговая проверка перед сдачей: полигоны, ключи формы, модификаторы
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    keys = len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0
    print(f"{o.name:30s} tris={tris:7d} shapekeys={keys:3d} "
          f"mods={[m.type for m in o.modifiers]}")
```

| Параметр | Значение | Когда менять |
|---|---|---|
| JCM | вкл | выкл — когда морфы конфликтуют с ручными правками |
| `use_deform_preserve_volume` | `True` | `False` — если ключи деформируются неожиданно |
| `Subsurf.levels` | `1` | `2` — когда сетка от Daz слишком грубая для крупных планов |
| `object_types` | `{'MESH','ARMATURE'}` | `{'MESH'}` — если риг будет свой |
| `add_leaf_bones` | `False` | `True` — под требования движка |
| `mesh_smooth_type` | `FACE` | `EDGE` — для хард-нормалей |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Аддон включился, панели нет | ставился в папку аддонов вручную вместо установщика из Daz | Ставить установщиком из Daz Studio, потом перезапустить Blender |
| Импортируется пустая сцена | сцена в Daz не сохранена под тем же именем | Сохрани сцену в Daz, проверь имя сцены |
| Пропали морфы лица | переключатель импорта морфов выключен | Включить импорт face/body morphs и переимпортировать |
| JCM ломает позу вручную | JCM-морфы конфликтуют с твоими правками | Выключить JCM, оставить только форму и веса |
| Колено проваливается | линейные веса на тонкой сгибной зоне | `use_deform_preserve_volume = True` |
| Волосы невидимы в рендере | частицы без рендерера или кривые без материала | Назначь материал и проверь настройки рендера волос |
| Одежда «протекает» сквозь тело | физика Daz не перенесена, весов нет | Перенастроить Cloth/Sim либо сделать одежду статичной |
| Импорт занимает десятки минут | сцена с тяжёлым контентом и Subdiv | Отключай невидимые объекты до импорта, импортируй по частям |

## 🖥 MCP-ПРОМПТ

```text
RU: "После импорта Diffeomorphic: включи preserve volume на всех костях,
     добавь Subsurf 1 на основной меш, перечисли ключи формы,
     проверь модификаторы и выгрузи FBX" /
EN: "After Diffeomorphic import: enable preserve volume on all bones,
     add Subsurf 1 to the body mesh, list shape keys,
     audit modifiers and export FBX"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 34: METAHUMAN → BLENDER](setup_34_metahuman_blender.md), [SETUP 36: VROID STUDIO → BLENDER](setup_36_vroid_studio.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #blender, #character, #setup