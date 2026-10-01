---
id: setup_30_rigify_advanced
lang: ru
category: setups
type: setup
status: full
tags: [rigging, setup]
---
# SETUP 30: RIGIFY ADVANCED + FACE

**ID:** SETUP-30 | **Type:** Rig | **Difficulty:** ⭐⭐⭐ | **Time:** 90 min
**RU/EN Bilingual**

> Когда применять: нужен риг, который можно передать аниматору и который не сломается при добавлении корректирующих форм на колени и локти.

## 🎯 ЦЕЛЬ
Пройти полный цикл Rigify: от мета-рига и генерации до кастомной части тела, добавить мимику и корректирующие формы на сгибах, и понять, что именно уходит в игровой движок. Ключевая честная оговорка: Rigify делает тело, а лицо — отдельная работа на shape keys и контроллерах.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | генерация и правка рига |
| Rigify | входит в поставку Blender, включается в Preferences → Add-ons | генерация рига из мета-рига |
| Мета-риг | из пресетов аддона, шаблон `rigify/presets` | базовая форма скелета |
| Меш персонажа | гуманоид, деформационная топология без пересечений | веса и коррективы |

> [!NOTE]
> Rigify пережил крупное обновление в ветке 4.x: пресеты и названия «типов частей тела» (limb type) менялись. Перед генерацией открой список пресетов в самом аддоне и сверься с `Help → Manual` твоей версии — копировать имена из обзоров 3.x нельзя.

## 🛠️ НАСТРОЙКА

### 1. Включение аддона и осмотр пресетов
```python
import bpy

# Включить из кода (в UI: Preferences → Add-ons → Rigify)
if "rigify" not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module="rigify")

# Проверить, что оператор генерации зарегистрирован.
# bpy.ops.<путь> — не значение: getattr создаёт заглушку, поэтому
# `bool(bpy.ops.pose.rigify_generate)` всегда истинно и не проверяет ничего.
# dir() же перечисляет реально зарегистрированные операторы.
print("rigify_generate доступен:", "rigify_generate" in dir(bpy.ops.pose))
print("blender:", bpy.app.version_string, "| python:", bpy.app.version)
```
Пресеты мета-ригов лежат в каталоге аддона; путь виден в `Preferences → Add-ons → Rigify`. Там есть `basic`, `human`, `human-no-face` (или близкие по смыслу) — выбирай тот, чья развёртка пропорций совпадает с твоим мешем, иначе осевая сетка уедет.

### 2. Установка пропорций мета-рига
Пропорции выставляются прямо на костях в Edit Mode. Плечи — шире таза, длина бедра — по канону персонажа. Именно здесь экономится время: после генерации мета-риг больше не редактируется.

```python
# Пересчитать длины костей мета-рига вниз по иерархии
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.armature.calculate_roll(type='POSITIVE_X')
bpy.ops.object.mode_set(mode='OBJECT')
```

### 3. Генерация рига
```python
arm = bpy.context.view_layer.objects.active
bpy.context.view_layer.objects.active = arm

# Оператор генерации; перед вызовом мета-риг уже размечен
bpy.ops.pose.rigify_generate()
```
После генерации риг распадается на коллекции `rig` (управляющие кости, DEF-заменители) и `deform` (кости, к которым реально цепляются веса и коррективы). Мета-риг уезжает в коллекцию `metarig` и не участвует в анимации — его можно скрыть или удалить.

```python
print("коллекции:", [c.name for c in bpy.data.armatures[0].collections])
```

### 4. Кастомная часть тела
Rigify умеет добавлять части: например, хвост или шею животного. Процедура: добавить кости в мета-риг с правильными префиксами (`DEF-`, `ORG-`), задать им тип деформации, добавить пользовательский пресет в `rigify/presets`, после чего он появится в списке при следующем открытии аддона.

```python
# Префиксы имён — то, на что Rigify опирается при генерации.
# DEF- деформируемые, ORG- «органы» (например, вспомогательные), WGT- веса.
arm = bpy.data.armatures[0]
print("DEF-костей:", len([b for b in arm.bones if b.name.startswith("DEF-")]))
```

### 5. Веса
```python
ob = next(o for o in bpy.context.selected_objects if o.type == 'MESH')
rig = next(o for o in bpy.context.scene.objects
           if o.type == 'ARMATURE' and o.data.collections.get("deform"))

bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
```
Ручная правка весов в Rigify идёт по коллекции `WGT-` через инструмент Weight Paint на деформационных костях. Типичные зоны ручной правки: таз (перекрытие бёдер), подмышка, шея.

```python
# Диагностика «съехавших» весов на стыке суставов
for z in ("pelvis.L", "thigh.L", "DEF-spine.03"):
    vg = rig.vertex_groups.get(z)
    if vg:
        w = [g.weight for v in ob.data.vertices for g in v.groups
             if g.group == vg.index]
        if w:
            print(z, "min", min(w), "max", max(w))
```

### 6. Корректирующие формы
Rigify не имеет встроенной системы коррективов — их делают shape keys с драйверами. Схема: ставишь деформацию в предельную позу, добавляешь shape key, цепляешь к нему драйвер от контроллера, возвращаешь позу в ноль.

```python
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.context.view_layer.objects.active = ob

sk = ob.shape_key_add(name="Basis")
knee = ob.shape_key_add(name="KneeFix")
knee.slider_min, knee.slider_max = 0.0, 1.0

# Драйвер: значение ключа = положение контроллера
drv = knee.driver_add("value").driver
drv.type = 'SCRIPTED'
drv.expression = "min(1.0, max(0.0, ctrl_angle))"
```
Затем, чтобы ключи не накапливали деформацию при последовательных правках: `bpy.ops.object.shape_key_retime()` в Object Mode.

> [!NOTE]
> Имена контроллеров Rigify стабильны для дефолтных пресетов (например `DEF-spine.03`), но для кастомных частей тела ты задаёшь их сам. Имя в выражении драйвера должно точно совпадать с именем кости или свойства, которое ты используешь — иначе драйвер молча даёт 0.

### 7. Лицо
Rigify лицо не рисует. Рабочий минимум для продакшна:

| Задача | Инструмент | Комментарий |
|---|---|---|
| Базовые эмоции | shape keys на голове | 10–15 базовых форм достаточно для большинства проектов |
| Произвольная мимика | лицевой риг на костях + dельты | существенно дороже, обычно отдельная задача |
| Липсинк | отдельная артикуляционная раскладка | либо готовый набор, либо покупной |

```python
# Проверка: сколько ключей формы на лице и в каком они диапазоне
face_keys = ob.data.shape_keys.key_blocks if ob.data.shape_keys else []
print("ключей формы:", len(face_keys))
for k in face_keys:
    print(f"  {k.name}: {k.value:.2f} (min {k.slider_min}, max {k.slider_max})")
```

### 8. Экспорт
```python
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig

bpy.ops.export_scene.fbx(
    filepath=r"C:\work\export\char_rigify.fbx",
    use_selection=True,
    object_types={'ARMATURE', 'MESH'},
    add_leaf_bones=False,
    path_mode='AUTO',
    bake_anim=False,
)
```
Unity и Unreal не понимают скелет Rigify напрямую: ни одна из этих платформ не имеет маппинга под DEF/ORG-кости. Варианты — ретаргет готовых анимаций через общего родителя (Hierarchy Bone) либо экспорт в стандартный гуманоидный скелет через промежуточный риг.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Сводка по ригу: чего сколько, чтобы понять, что сгенерировалось
rig = bpy.data.objects["rig"]
bpy.ops.object.mode_set(mode='POSE')
print("управляющих костей:", len(rig.pose.bones))
print("деформационных:", len([b for b in rig.data.bones if b.use_deform]))
bpy.ops.object.mode_set(mode='OBJECT')
```

| Параметр | Значение | Когда менять |
|---|---|---|
| пресет мета-рига | `human` | `basic` — когда детальные пропорции не нужны |
| сегменты позвоночника | 3–5 | больше — для длинной спины, меньше — для скорости |
| `bpy.ops.pose.rigify_generate()` | вызов из Pose Mode или Object Mode с активной арматурой | повторный вызов пересобирает риг заново |
| `shape_key_retime()` | Object Mode | после каждой серии правок ключей формы |
| `add_leaf_bones` | `False` | `True` — если движок требует хвосты у листьев |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `rigify_generate` не появляется в меню | аддон не включён либо активна не та арматура | Включить Rigify, выделить именно мета-риг |
| Кости называются `DEF-spine` вместо ожидаемого имени | кастомный пресет не подхватился | Проверить префиксы `DEF-` и папку `rigify/presets` |
| Драйвер ключа всегда 0 | имя в выражении не совпадает с реальным | Распечатать `rig.pose.bones` и сверить посимвольно |
| Веса съехали на тазу | автовес не справился с пересечением | Ручная правка весов по зоне, либо контрольный меш |
| Лимб не деформируется | кость не попала в коллекцию `deform` | Проверить коллекции арматуры |
| В движке нет анимаций | экспортирован DEF-скелет, а движок ждёт гуманоид | Ретаргет через общего родителя либо промежуточный риг |
| После генерации форма деформировалась | мета-риг редактировали после генерации | Правки вносятся в мета-риг, затем генерация повторяется |

## 🖥 MCP-ПРОМПТ

```text
RU: "Rigify: human-пресет, spine 5, generate rig, ARMATURE_AUTO,
     shape key KneeFix + драйвер, shape_key_retime, экспорт FBX" /
EN: "Rigify: human preset, spine 5, generate rig, ARMATURE_AUTO,
     KneeFix shape key + driver, shape_key_retime, FBX export"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 27: MIXAMO AUTO-RIG](setup_27_mixamo_autorig.md), [SETUP 28: ACCURIG / ACTORCORE RIG](setup_28_accurig_cc.md), [SETUP 29: AUTO-RIG PRO](setup_29_autorignpro.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P17: RIGIFY HUMANOID SETUP](../prompts/17_rigify_setup.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #rigging, #setup