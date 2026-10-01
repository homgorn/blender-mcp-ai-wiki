---
id: setup_35_readyplayerme
lang: ru
category: setups
type: setup
status: full
tags: [automation, blender, llm, mcp, rigging, setup, stable-diffusion]
---
# SETUP 35: READY PLAYER ME AVATARS

**ID:** SETUP-35 | **Type:** Avatar | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

> Когда применять: нужны десятки аватаров с готовым гуманоидным ригом для Web3, VR или быстрого прототипа — без моделирования и без риггинга.

## 🎯 ЦЕЛЬ
Настроить связку Ready Player Me → Blender: получить GLB по ссылке на аватар, импортировать его вместе с текстурой, проверить скелет и собрать коллекцию из нескольких аватаров одним проходом. Отдельный акцент — на пакетной обработке: ручная загрузка двадцати аватаров не масштабируется.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Ready Player Me | облачный сервис, `readyplayer.me` | генерация аватаров и выдача GLB |
| Аккаунт | регистрация на сайте | собственные аватары |
| Blender | 4.x | импорт glTF |
| glTF-импортёр | встроенный в Blender | формат GLB |

> [!NOTE]
> Ready Player Me выдаёт две вещи: 3D-модель (GLB) и 2D-фото аватара (PNG). Ссылки вида `https://models.readyplayer.me/<id>.glb` и `https://models.readyplayer.me/<id>.png` открываются без ключа — это публичные ссылки конкретного аватара. Полноценный REST API с ключом и созданием аватаров программно требует подписки, поэтому массовая генерация «по описанию» и массовая загрузка готовых ID — разные задачи с разными требованиями.

## 🛠️ НАСТРОЙКА

### 1. Получение ссылки
Создаёшь аватар на сайте, копируешь его ID (последний сегмент ссылки на аватар) и подставляешь в шаблон.

```python
import urllib.request

AVATAR_ID = "<id-аватара>"
BASE = "https://models.readyplayer.me"

def fetch(url, out):
    """Скачать бинарный файл по ссылке. Returns (путь, размер в байтах)."""
    req = urllib.request.Request(url, headers={"User-Agent": "blender-script"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(out, "wb") as f:
        f.write(data)
    return out, len(data)

glb = f"{BASE}/{AVATAR_ID}.glb"
png = f"{BASE}/{AVATAR_ID}.png?size=512"

print("3D:", glb)
print("2D:", png)
```

> [!NOTE]
> Параметры query-строки у ссылок RPM (например `size` для PNG или параметры текстурного атласа для GLB) менялись по мере развития сервиса. Базовые ссылки выше стабильны; точный список допустимых параметров — в документации RPM на readyplayer.me.

### 2. Импорт GLB
```python
import bpy

bpy.ops.import_scene.gltf(
    filepath=r"C:\work\rpm\avatar.glb",
    merge_vertices=True,
    import_pack_images=True,
)
```
`merge_vertices` важен для двух вещей: меньше мусора в топологии и корректные нормали. `import_pack_images` упаковывает текстуры внутрь blend-файла — для батча это удобно, для тяжёлых аватаров избыточно.

### 3. Проверка скелета
Аватары RPM приезжают с гуманоидным ригом, совместимым с Mixamo, и с костями глаз.

```python
arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
if arm:
    print("костей:", len(arm.data.bones))
    print("есть кисть:", "LeftHand" in arm.data.bones or
          any("Hand" in b.name for b in arm.data.bones))
    print("есть пальцы:", any("Index" in b.name for b in arm.data.bones))
```
Пальцев в стандартном риге RPM нет — как и у Mixamo. Если персонаж должен жестикулировать пальцами, риг дописывается вручную.

### 4. Разбор структуры объектов
```python
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        print(f"{o.name}: tris={tris} mods={[m.type for m in o.modifiers]} "
              f"mats={[m.name for m in o.data.materials]}")
    else:
        print(f"{o.name}: {o.type}")
```
RPM часто привозит несколько мешей (тело, волосы, одежда, глаза). Это нормально: они разделяются намеренно, чтобы волосы можно было заменить без перезагрузки всего аватара.

### 5. Что лежит внутри GLB
Формат glTF упаковывает в себя геометрию, текстуры и скелет, поэтому один файл может содержать сразу всё. Стоит знать заранее, что ожидать:

| Внутри | Как выглядит в Blender | На что смотреть |
|---|---|---|
| Тело и одежда | отдельные Mesh-объекты | количество объектов, лишние дубли |
| Текстурный атлас | один Image + UV-слой | размер атласа, не растянут ли |
| Вершинные цвета | Color Attribute на меше | без них аватар станет серым |
| Скелет | Armature + Skin-модификатор | имена костей и порядок |
| Выражения лица | Shape Keys на голове | набор ключей, нумерация |

```python
# Разбор одного GLB: скелет, ключи лица, UV и вершинные цвета
mesh = next(o for o in bpy.data.objects if o.type == 'MESH' and o.name != "Armature")
print("UV-слоёв:", len(mesh.data.uv_layers))
print("вершинных цветов:", len(mesh.data.color_attributes))
print("шейп-ключей:",
      [k.name for k in mesh.data.shape_keys.key_blocks][:12]
      if mesh.data.shape_keys else "нет")
print("модификаторы:", [(m.name, m.type) for m in mesh.modifiers])
```

### 6. Батч: коллекция из N аватаров
```python
import os

OUT = r"C:\work\rpm"
AVATARS = ["<id-1>", "<id-2>", "<id-3>", "<id-4>", "<id-5>"]
os.makedirs(OUT, exist_ok=True)

def import_avatar(avatar_id, collection_name):
    path = os.path.join(OUT, f"{avatar_id}.glb")
    if not os.path.exists(path):
        fetch(f"{BASE}/{avatar_id}.glb", path)

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path, merge_vertices=True)
    new = [o for o in bpy.data.objects if o not in before]

    coll = bpy.data.collections.get(collection_name) or \
           bpy.data.collections.new(collection_name)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll, new

for aid in AVATARS:
    coll, objs = import_avatar(aid, "RPM_batch")
    print(aid, "->", len(objs), "объектов")
```

### 7. Расстановка по сцене
```python
# Аватары одного батча перекрываются: разложить в ряд
colls = [c for c in bpy.data.collections if c.name == "RPM_batch"]
for i, coll in enumerate(colls):
    for o in coll.objects:
        o.location.x = i * 1.0
```

### 8. Проверка материалов и вершинных цветов
Аватары RPM используют один текстурный атлас с вершинными цветами: цвет волос и кожи часто приезжает именно вершинными цветами, а не отдельными картами. Если их не сохранить при экспорте, персонаж станет серым.

```python
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
print("vertex colors:", len(mesh.data.color_attributes))
for ca in mesh.data.color_attributes:
    print("  слой:", ca.name, "| домен:", ca.domain,
          "| data_type:", ca.data_type)

# Цвета атрибута -> Color Attribute нода в шейдере материала
mat = next((m for m in bpy.data.materials if m and m.use_nodes), None)
if mat:
    nt = mat.node_tree
    attr = nt.nodes.new('ShaderNodeAttribute')
    attr.attribute_type = 'GEOMETRY'
    attr.attribute_name = mesh.data.color_attributes[0].name
    attr.location = (-600, -300)
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    print("подключено:", attr.attribute_name)
```

### 9. 2D-портрет
Фото аватара используется как референс при текстурировании вручную либо как плоский «аватар» для тех, кому нужен 2D-стиккер.

```python
fetch(f"{BASE}/{AVATARS[0]}.png?size=512", r"C:\work\rpm\portrait.png")
img = bpy.data.images.load(r"C:\work\rpm\portrait.png", check_existing=True)
print("портрет:", tuple(img.size), "| colorspace:",
      img.colorspace_settings.name)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Сводка по батчу: сколько аватаров, сколько полигонов суммарно
total = 0
for o in bpy.data.objects:
    if o.type == 'MESH':
        total += sum(len(p.vertices) - 2 for p in o.data.polygons)
print("всего треугольников:", total)
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `merge_vertices` | `True` | `False` — когда важно сохранить исходные UV-швы |
| `import_pack_images` | `True` | `False` — при большом батче, чтобы не раздувать blend-файл |
| PNG `size` | `512` | `256` для превью, `1024` для качественной текстуры |
| Коллекция | отдельная на каждый аватар или общая на батч | отдельная — когда аватары редактируются независимо |
| Кости глаз | оставить | удалить, если анимация лица делается морфами |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| 404 на ссылку `.glb` | неверный ID или приватный аватар | Проверить ID на странице аватара, убрать пробелы |
| Текстуры не подтянулись | атлас не скачался | `import_pack_images=True`, при необходимости скачать вручную |
| Модель маленькая | аватар нормализован по своему росту | Масштабировать вручную, единицы сцены не при чём |
| Кости не на месте | импорт разложил арматуру в сторону | Переимпортировать с `merge_vertices` и проверить `use_transform` |
| Все аватары в одной точке | импорт не сдвигает объекты | Расставить по X вручную, скриптом |
| Нет нормалей | GLB без нормалей | `shade_smooth_by_angle` либо перегенерировать |
| Пальцев нет | в риге RPM их нет по умолчанию | Дописать вручную или взять риг с пальцами (ARP, Rigify) |

## 🖥 MCP-ПРОМПТ

```text
RU: "Скачай GLB по ID, импортируй в отдельную коллекцию,
     merge_vertices=True, выведи треугольники и список костей,
     расставь 10 аватаров по X с шагом 1.0" /
EN: "Download GLB by ID, import into its own collection,
     merge_vertices=True, print triangle count and bone list,
     lay out 10 avatars along X with 1.0 spacing"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 15: BLENDER + COMFYUI SDXL](setup_15_comfyui_sdxl.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md)
- **Теги:** #automation, #blender, #llm, #mcp, #rigging, #setup, #stable-diffusion