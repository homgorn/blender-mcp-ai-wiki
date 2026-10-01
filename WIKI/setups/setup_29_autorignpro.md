---
id: setup_29_autorignpro
lang: ru
category: setups
type: setup
status: full
tags: [rigging, setup]
---
# SETUP 29: AUTO-RIG PRO

**ID:** SETUP-29 | **Type:** Rig Pro | **Difficulty:** ⭐⭐⭐ | **Time:** 60 min
**RU/EN Bilingual**

> Когда применять: риг делается под продакшн — нужны пальцы, корректные скручивания конечностей и готовый экспорт под игровой движок, а не разовая анимация.

## 🎯 ЦЕЛЬ
Собрать в ARP (Auto-Rig Pro) риг, который переживёт передачу другой аниматору: с полными пальцами, раздельными IK/FK для рук и ног, рабочими корректирующими формами на сгибах и предсказуемым экспортом в FBX для Unity или Unreal. Настраиваем четыре вещи: генерацию рига из меша, распределение весов, систему управления и экспорт под движок.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x (совместимость проверяй на сайте автора) | хост |
| Auto-Rig Pro | платный аддон, есть триал | сам риг и экспорт |
| Лицензия / триал | активируется в Preferences аддона | разблокировка экспорта |
| Исходный меш | гуманоид, без лишней геометрии | вход Rig Builder |

> [!NOTE]
> Официальная страница аддона — `lucky3d.fr/arp/`. Там же указаны поддерживаемые версии Blender; ARP регулярно отстаёт по совместимости, поэтому проверь список до установки, а не после.

## 🛠️ НАСТРОЙКА

### 1. Установка аддона
Скачай zip аддона → `Edit → Preferences → Add-ons → Install…` → выбери архив → в списке включи **Auto-Rig Pro** → `Save Preferences`. В N-панели (Sidebar) появится вкладка аддона.

```python
import bpy

# Проверка, что аддон загрузился: его операторы попадают в bpy.ops.<пространство>
print("дополнения с 'rig' в имени:",
      [k for k in bpy.context.preferences.addons.keys() if "rig" in k.lower()])
print("версия Blender:", bpy.app.version_string)
```

> [!NOTE]
> Имена операторов аддона начинаются с префикса `arp_` и живут в отдельном пространстве имён внутри `bpy.ops`, но конкретные названия (`arp_rigify`, `arp_rig_build`, `arp_export`) не являются публичным API — они меняются между версиями. Надёжный способ узнать точные имена в своей сборке: навести курсор на кнопку в UI и посмотреть подсказку с `bpy.ops.имя.оператора()`.

### 2. Подготовка меша
```python
import bpy

ob = bpy.context.view_layer.objects.active
ob.name = "CHAR"

# Применить трансформации: ARP опирается на мировые координаты вершин
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Отделить всё, что не участвует в риге (волосы, одежда, пропсы)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.join()
me = ob.data

# Сбросить группы весов, если меш пришёл из другого рига
ob.vertex_groups.clear()
```

### 3. Rig Builder: сборка рига
В Rig Builder расставляешь части тела (голова, шея, позвоночник, ключицы, руки, кисти, пальцы, ноги, стопы, хвост/грудь при наличии), а затем жмёшь **Rig**. Что важно задать до генерации:

| Параметр Rig Builder | Значение | Когда менять |
|---|---|---|
| Число сегментов позвоночника | 3–5 | больше — для длинной спины, меньше — для короткой и быстрой анимации |
| Пальцы | полный набор (5 лучей) | без пальцев — если персонаж в перчатках, экономит вес и время |
| Скручивание (twist) конечностей | включено | выключить, если кисти и стопы не деформируются |
| IK для рук / ног | по необходимости | без рук IK анимация идёт быстрее, но теряется управление кистью |
| Плечи (shoulders) | включены | когда нужна дельта-деформация плечевого сустава |

### 4. Веса
Основной путь — автоматический, с последующей чисткой.

```python
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

# Тепловой метод: Blender распределяет веса по прогреву кости
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# Dual quaternion — обязателен для суставов, иначе колени «схлопываются»
for pb in arm.pose.bones:
    pb.use_deform_preserve_volume = True
```

Автовес почти всегда требует ручной чистки в трёх зонах: шея, запястье, щиколотка. Там, где ARP-веса «съехали», помогает контрольный меш (в самом аддоне — инструмент очистки весов в панели Rig Tools; точный пункт меню сверяй по документации версии).

```python
# Диагностика: какие группы весов пустые или почти пустые
report = [(g.name, len(g.name)) for g in ob.vertex_groups]
for g in ob.vertex_groups:
    if not any(x.group == g.index for v in ob.data.vertices for x in v.groups):
        print("пустая группа:", g.name)
```

### 5. Корректирующие формы
Ригируемые плечи и локти деформируются неидеально — появляется провал. ARP чинит это либо корректирующими формами (corrective shapes, доступны для части суставов), либо через дельту на управляющих костях.

```python
# Ручная корректирующая форма: дельта кости -> ключ формы
arm = bpy.data.objects["rig"]
print("костей управления:", [b.name for b in arm.pose.bones][:12])

sk = ob.shape_key_add(name="Basis")
corr = ob.shape_key_add(name="ShoulderFix")
corr.slider_min = 0.0
corr.slider_max = 1.0
drv = corr.driver_add("value").driver
drv.expression = "max(0.0, 1.0 - shoulder_ctrl)"   # имя контроллера уточни
```

> [!NOTE]
> Конкретные имена управляющих костей (`.L` / `_L`, `upper_arm`, `ForeArm`) задаются самим аддоном и различаются между версиями и настройками. Не копируй имя из документации другого аддона — выведи `arm.pose.bones` и найди нужное.

### 6. Экспорт под игровой движок
Раздел **Game Tools** собирает чистый риг: только деформационные кости, без control-костей и без вспомогательных целей. Это то, что увидит движок.

```python
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

bpy.ops.export_scene.fbx(
    filepath=r"C:\work\export\char_game.fbx",
    use_selection=True,
    object_types={'ARMATURE', 'MESH'},
    apply_unit_scale=True,
    global_scale=1.0,
    add_leaf_bones=False,
    path_mode='AUTO',
    mesh_smooth_type='FACE',
)
```

> [!NOTE]
> Список игровых пресетов (Unity Standard / Unity Mecanim / Unreal / Godot и другие) менялся между версиями аддона. Открывай панель Game Tools в своей сборке и выбирай оттуда — не по памяти и не по скриншоту из другой статьи.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Что уедет в движок: перечень костей деформации и их веса
deform = [b.name for b in arm.data.bones if b.use_deform]
print("деформационных костей:", len(deform))

# Проверка рига в предельных позах — обязательный шаг перед экспортом
for name in ("rig", "CHAR"):
    o = bpy.data.objects.get(name)
    if o and o.type == 'ARMATURE':
        print(name, "→", len(o.pose.bones), "костей управления")
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `parent_set(type=)` | `ARMATURE_AUTO` | `ARMATURE_WITH_EMPTY_GROUP` — когда тепловой вес не справляется |
| `use_deform_preserve_volume` | `True` | `False` — если аниматор жалуется на «резину» в суставах |
| `add_leaf_bones` | `False` | `True` — если движок требует висячие кости |
| `object_types` | `{'ARMATURE','MESH'}` | `{'MESH'}` — когда риг уже вшит в движке |
| `mesh_smooth_type` | `FACE` | `EDGE` — для хард-нормалей |
| число сегментов позвоночника | 3–5 | больше — длинная спина, меньше — скорость |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Экспорт в FBX пустой | не выделен риг, либо не сделан Game Tools export | Выделить меш + риг, повторить пресет в Game Tools |
| В Unity анимация не распознаётся | нет пресета под движок либо лишние кости | Использовать пресет Unity, а не «просто FBX» |
| Суставы «сжимаются» при сгибе | линейные веса | `use_deform_preserve_volume = True` |
| Плечи проваливаются в прыжке | нет корректирующих форм | Добавить shape key + драйвер, либо включить shoulders |
| Кисть отрывается от предплечья | автовес не захватил зону запястья | Весать вручную, проверить группу кисти |
| Аддон не появился в Add-ons | архив не того формата или несовместимая версия | Распаковать zip, проверить требования на `lucky3d.fr/arp/` |
| Импорт FBX кладёт кости боком | не задан bone orientation | Переимпортировать с `automatic_bone_orientation=True` |

## 🖥 MCP-ПРОМПТ

```text
RU: "Auto-Rig Pro Rig Builder: spine 5, полные пальцы, twist, shoulders on,
     ARMATURE_AUTO, preserve volume, экспорт пресетом Unity" /
EN: "ARP Rig Builder: spine 5, full fingers, twist, shoulders on,
     ARMATURE_AUTO, preserve volume, export with the Unity preset"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 27: MIXAMO AUTO-RIG](setup_27_mixamo_autorig.md), [SETUP 28: ACCURIG / ACTORCORE RIG](setup_28_accurig_cc.md), [SETUP 30: RIGIFY ADVANCED + FACE](setup_30_rigify_advanced.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [P17: RIGIFY HUMANOID SETUP](../prompts/17_rigify_setup.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #rigging, #setup