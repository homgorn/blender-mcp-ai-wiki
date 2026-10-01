---
id: setup_31_makehuman_mpfb
lang: ru
category: setups
type: setup
status: full
tags: [character, setup]
---
# SETUP 31: MAKEHUMAN / MPFB

**ID:** SETUP-31 | **Type:** Base Human | **Difficulty:** ⭐ | **Time:** 20 min
**RU/EN Bilingual**

> Когда применять: нужен параметрический человек как отправная точка — для прототипа, для стокового персонажа или чтобы не моделить гуманоида с нуля.

## 🎯 ЦЕЛЬ
Получить в Blender параметрически управляемого человека через MPFB (MakeHuman Project for Blender), разобраться, как устроены таргеты (morphs), одежда и скелет, и выгрузить результат в FBX для рига или движка. Отдельно: MPFB — это не MakeHuman 1.x, это переписанный аддон, и старые инструкции к нему неприменимы.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | хост аддона |
| MPFB | релиз под свою версию Blender | генерация человека, таргеты, одежда |
| MPFB-ресурсы | пакеты с одеждой и материалами | обход голого тела |
| Старый MakeHuman 1.x | не нужен | можно держать, но в Blender он больше не интегрирован |

> [!NOTE]
> Официальная точка входа по MPFB — сообщество makehumancommunity, репозиторий проекта ищется там. Не указываю конкретный URL: аддон регулярно меняет имя пакета и способ установки между релизами. Смотри `Help → Manual → Add-ons` в своей сборке или README актуального релиза — там указан способ установки для твоей версии.

## 🛠️ НАСТРОЙКА

### 1. Установка аддона
```bash
# Установка из исходников в папку аддонов Blender
git clone <репозиторий-MPFB> mpfb
# затем: Edit → Preferences → Add-ons → Install… → выбрать zip-пакет аддона
# или положить папку mpfb в %APPDATA%\Blender Foundation\Blender\<версия>\scripts\addons
```
После включения аддона в 3D-вьюпорте появляется отдельная вкладка с панелью MPFB, в N-панели — меню операций.

```python
import bpy

print("blender:", bpy.app.version_string)
print("дополнения:", [k for k in bpy.context.preferences.addons.keys()
                       if "mpfb" in k.lower() or "makehuman" in k.lower()])
```

### 2. Создание человека
Панель MPFB даёт набор базовых параметров: пол, возраст, рост, телосложение (мускулистость, полнота), отдельные блоки под лицо и под тело. Параметры — это не ползунки в сцене, а **таргеты**: контрольные вершины, которые по умолчанию скрыты.

```python
import bpy

human = next((o for o in bpy.data.objects if o.type == 'MESH'), None)
if human:
    print("объект:", human.name)
    print("вершин:", len(human.data.vertices))
    if human.data.shape_keys:
        keys = human.data.shape_keys.key_blocks
        print("ключей формы:", len(keys))
        for k in list(keys)[:10]:
            print(f"  {k.name}: value={k.value:.3f} "
                  f"(slider {k.slider_min}..{k.slider_max})")
```

### 3. Работа с таргетами
Таргеты — это shape keys с нулевым значением, которые можно поднимать и опускать.

```python
def set_target(obj, name_part, value):
    """Найти таргет по подстроке имени и выставить значение."""
    sk = obj.data.shape_keys
    if not sk:
        return None
    for k in sk.key_blocks:
        if name_part.lower() in k.name.lower():
            k.value = max(k.slider_min, min(k.slider_max, value))
            return k
    return None

human = next(o for o in bpy.data.objects if o.type == 'MESH')
# Не угадывай имена — выведи их:
print([k.name for k in human.data.shape_keys.key_blocks][:20])
```

> [!NOTE]
> Имена таргетов заданы сообществом MakeHuman и включают идиомы вроде `macro`, `detail`, `male`/`female` и коды регионов. Не переводи и не переименовывай их: одежда и пресеты из пакетов рассчитаны на эти имена. Просто выведи список — он сам покажет структуру.

### 4. Скелет
MPFB умеет добавить к человеку скелет. Это отдельное действие, и после него меш получает арматуру и веса.

```python
rig = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
if rig:
    print("костей:", len(rig.data.bones))
    for pb in rig.pose.bones:
        pb.use_deform_preserve_volume = True
```
Проверка привязки — та же, что и для любого рига: у каждой кости должна быть непустая группа весов.

```python
def bone_weight_report(rig, mesh):
    for b in rig.data.bones[:8]:
        vg = rig.vertex_groups.get(b.name)
        if vg is None:
            print(b.name, "-> нет группы")
            continue
        n = sum(1 for v in mesh.data.vertices for g in v.groups
                if g.group == vg.index)
        print(b.name, "->", n, "вершин")

if rig and human:
    bone_weight_report(rig, human)
```

### 5. Одежда
Одежда приходит отдельными объектами (прокси в терминологии MakeHuman). Каждый вариант — отдельный объект в сцене, и одежда привязана к телу: при смене параметров таргета она растягивается вместе с ним.

```python
bpy.ops.object.select_all(action='DESELECT')
cloth = next((o for o in bpy.data.objects
              if o.type == 'MESH' and o.name != human.name), None)
if cloth:
    cloth.select_set(True)
    bpy.context.view_layer.objects.active = cloth
    print("одежда:", cloth.name,
          "модификаторов:", [m.type for m in cloth.modifiers])
```
Одежда зачастую приходит с модификаторами (Subdivision, Shrinkwrap или Data Transfer) — не применяй их до экспорта, иначе она перестанет реагировать на таргеты.

### 6. Сохранение и повторное использование
Готового человека имеет смысл сохранить отдельным blend-файлом: иначе параметры таргетов придётся подбирать заново.

```python
# Отдельный blend под библиотеку персонажей
bpy.ops.wm.save_as_mainfile(
    filepath=r"C:\work\mphuman\humans.fuse.blend",
    copy=True,          # copy=True — текущий файл останется прежним
)

# Ассеты из пакетов подключаются через Append, а не Link:
# link тянет внешний файл и ломается при его перемещении
bpy.ops.wm.append(
    filepath=r"C:\Users\<user>\AppData\Roaming\Blender Foundation\Blender\4.x\scripts\addons\<addon>\assets.human.female.json",
    directory=r"C:\Users\<user>\AppData\Roaming\Blender Foundation\Blender\4.x\scripts\addons\<addon>\",
    filename="<файл-ресурса>",
    link=False,
)
```

> [!NOTE]
> Путь к пакетам ресурсов зависит от способа установки аддона (архивом в addons или через extensions) и от версии Blender. Точный путь смотри в `Preferences → Add-ons` и в самом аддоне — в текстовом поле ресурсов, если оно есть в панели.

### 7. Экспорт
```python
bpy.ops.object.select_all(action='DESELECT')
human.select_set(True)
if rig:
    rig.select_set(True)
bpy.context.view_layer.objects.active = human

bpy.ops.export_scene.fbx(
    filepath=r"C:\work\mphuman\base_human.fbx",
    use_selection=True,
    object_types={'MESH', 'ARMATURE'},
    apply_unit_scale=True,
    add_leaf_bones=False,
    mesh_smooth_type='FACE',
    path_mode='AUTO',
)
```
Таргеты в FBX не попадают: морфы превращаются в shape keys только если экспортировать их как Blend Shapes через настройки FBX, и не все движки это читают. Для универсальности применяют таргеты перед экспортом.

```python
# Применить все таргеты разом перед экспортом, если движок не понимает морфы
sk = human.data.shape_keys
if sk:
    for k in sk.key_blocks:
        k.value = 0.0   # reset -> значения из вкладки MPFB надо выставить заранее
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Итоговая сводка по сцене: что получилось
for o in bpy.data.objects:
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons) \
        if o.type == 'MESH' else 0
    print(f"{o.name:24s} {o.type:9s} tris={tris:6d} mods={[m.type for m in o.modifiers]}")
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `shape_key.value` | `0.0 – 1.0` | диапазон ограничен `slider_min`/`slider_max` конкретного таргета |
| `use_deform_preserve_volume` | `True` | `False` — если части тела «схлопываются» на сгибах |
| `object_types` | `{'MESH','ARMATURE'}` | `{'MESH'}` — когда риг будет сделан позже (Mixamo, ARP) |
| `add_leaf_bones` | `False` | `True` — если движок требует хвосты |
| Применять модификаторы одежды | нет | только перед экспортом, если дальше не нужны таргеты |

Порядок действий, который экономит время: сначала выставить все таргеты, потом надеть одежду, потом добавить скелет, и только в конце — экспорт. Любая из этих операций в обратном порядке заставит переделывать предыдущую.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Аддон не появился в списке | не та версия Blender или не распакован архив | Проверить требования релиза, ставить через Install… |
| Таргет не находится по имени | имя на языке сообщества, а не английское | Вывести `key_blocks` и искать по подстроке |
| Одежда «отстала» от тела | таргет тела изменён после надевания одежды | Настроить таргеты до надевания, либо обновить прокси |
| Морфы пропали при экспорте | FBX не выгружает их как Blend Shapes | Применить таргеты перед экспортом |
| Персонаж в 10 раз меньше роста | единицы сцены не совпадают с единицами аддона | Проверить `Scene Unit Settings`, применить трансформации |
| Скелет не появился | скелет добавляется отдельным действием, не автоматически | Добавить скелет из панели MPFB, затем перепривязать веса |

## 🖥 MCP-ПРОМПТ

```text
RU: "MPFB: создать человека, вывести список таргетов, сбросить значения,
     добавить скелет, применить preserve volume, экспорт FBX" /
EN: "MPFB: create human, list shape-key targets, reset values,
     add skeleton, preserve volume, FBX export"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 32: DAZ → BLENDER (DIFFEOMORPHIC)](setup_32_daz_diffeomorphic.md), [SETUP 34: METAHUMAN → BLENDER](setup_34_metahuman_blender.md), [SETUP 36: VROID STUDIO → BLENDER](setup_36_vroid_studio.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **Теги:** #character, #setup