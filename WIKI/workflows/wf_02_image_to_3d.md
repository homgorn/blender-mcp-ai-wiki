---
id: wf_02_image_to_3d
lang: ru
category: workflows
type: workflow
status: full
tags: [ai-3d, pipeline, workflow]
---
# WF 02: IMAGE-TO-3D

**ID:** WF-02 | **Type:** AI Generation Pipeline | **Difficulty:** ⭐⭐ | **Time:** 10-30 min per asset

---

> Когда применять: когда есть одна картинка — фото предмета, скетч, кадр из концепта — и из неё нужно за минуты получить болванку формы, с которой уже можно работать. Не финальный ассет, а блокаут.

## 🎯 ЦЕЛЬ

Провести 2D-изображение через три стадии: препроцессинг картинки, генерация сетки генератором, постобработка в Blender до состояния «можно показывать и можно отдавать дальше по пайплайну».

Честная оговорка, без которой статья врёт: **image-to-3D отдаёт болванку, а не ассет**. Типичный результат — непропорциональные формы, произвольный масштаб относительно реального, зеркальные UV, иногда дырявая геометрия, а текстуры может не быть вовсе. Экономия времени реальна и она большая: ручной блокаут часового объекта занимает секунды. Доводка до ассета занимает столько же, сколько и без генератора.

Поэтому ценность пайплайна не в генерации, а в дисциплине: одна и та же последовательность шагов, одинаковые проверки, одинаковый экспорт. Именно она превращает разовый эксперимент в повторяемый процесс.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| blender-mcp с генератором | проверить `get_addon_status` и статус конкретного генератора | генерация сетки |
| Исходное изображение | 512×1024 на длинной стороне, лучше на прозрачном или однотонном фоне | вход генератора |
| Python с Pillow | по необходимости | кадрирование, ресайз, замена фона |
| Blender | текущий рабочий | импорт, чистка, ретопология, запекание |
| Cycles | встроенный | запекание AO и нормалей требует рендер-движка |

> [!NOTE]
> Имена MCP-инструментов ниже взяты из подключённого сервера: `generate_hyper3d_model_via_text`,
> `poll_rodin_job_status`, `import_generated_asset`, `get_tripo_status`, `poll_tripo_job_status`,
> `import_generated_asset_tripo`, `get_hunyuan3d_status`, `poll_hunyuan_job_status`,
> `import_generated_asset_hunyuan`. Набор и имена зависят от версии аддона — сначала вызови
> `get_addon_status()` и посмотри, что доступно, вместо того чтобы идти по списку.

## 🛠️ НАСТРОЙКА

### Этап 1. Проверить, что генератор доступен

Не вызывай генерацию до проверки статуса: иначе потратишь итерацию на заведомо неработающую интеграцию и решишь, что пайплайн сломан.

```
get_addon_status                 # версия Blender и состав аддона
get_tripo_status                 # и/или get_hunyuan3d_status / get_hyper3d_status
```

### Этап 2. Препроцессинг изображения

Генераторы гораздо чувствительнее к фону, чем кажется: пёстрый фон превращается в пёструю геометрию, а объект, занимающий 20% кадра, получает 20% бюджета разрешения на себя.

```python
# scripts/preprocess_image.py
from PIL import Image

def prepare(src, dst, size=1024, pad_ratio=0.85):
    """Квадратный холст, объект внутри него занимает pad_ratio по большей стороне."""
    img = Image.open(src).convert("RGBA")

    # Если есть альфа-канал — используем его как маску, иначе белый угол
    # будет срезан и попадёт в геометрию
    if img.mode == "RGBA" and img.getchannel("A").getextrema()[0] < 255:
        bbox = img.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()
    else:
        bbox = Image.new("L", img.size, 255).getbbox()

    if bbox:
        img = img.crop(bbox)

    w, h = img.size
    side = int(max(w, h) / pad_ratio)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2))
    canvas = canvas.resize((size, size), Image.LANCZOS)
    canvas.save(dst)
    return dst

prepare("product_photo.jpg", "input_1024.png")
```

> [!NOTE]
> Про `rembg` (удаление фона нейросетью, `pip install rembg`) как про отдельный шаг:
> пакет и его модель существуют и используются именно так, но весит модель сотни
> мегабайт и тянет отдельные зависимости. Если фон однотонный, грубый кроп по
> альфе из скрипта выше даёт результат не хуже и не требует ничего ставить.
> Точные имена функций пакета сверяй по его документации — они менялись.

### Этап 3. Генерация

```bash
# Вариант A: сервис с текстовым запросом, где картинка — подсказка
generate_hyper3d_model_via_text(
    text_prompt="a weathered wooden barrel, hand painted stylised game asset",
    bbox_condition=[1.0, 1.2, 1.0]      # пропорции габаритной коробки
)
poll_rodin_job_status(request_id="<из ответа генерации>")
import_generated_asset(request_id="<из ответа генерации>", name="Barrel_AI")

# Вариант B: сервис, работающий именно с изображением
# (Tripo / Hunyuan — в текущем MCP-каталоге есть get_*_status, poll_*_job_status,
#  import_generated_asset_*). Конкретный инструмент для загрузки картинки
# смотри в своём каталоге тулов.
```

> [!NOTE]
> Поля вроде `bbox_condition` и конкретные числовые строки статусов генераторов
> здесь намеренно не выписаны: набор параметров и строковые значения статусов
> отличаются между сборками аддона и между сервисами. Ориентируйся на фактический
> ответ инструмента — в нём есть и идентификатор задачи, и её состояние.

### Этап 4. Импорт и чистка геометрии

Первое, что делает пайплайн с результатом генерации, — выбрасывает мусор. Дырявые оболочки, висящие вершины и внутренние грани в сгенерированной сетке есть почти всегда.

```python
import bpy, sys, os

path = sys.argv[sys.argv.index("--") + 1:]
if path:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path[0])

mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)

# Отдельные куски (например, «диск» и «ножка», если генератор не понял форму)
# склеиваем: без этого UV и запекание ломаются на стыках
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0005)   # порог в метрах
bpy.ops.mesh.delete(type='LOOSE')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.dissolve_degenerate(dist=0.00001, edges=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("clean:", len(mesh.data.vertices), "verts,", len(mesh.data.polygons), "faces")
```

> [!NOTE]
> Набор операций нормалей менялся между версиями: до 4.1 «гладкие нормали по углу»
> включались флагом на меше, а в 4.1 этот флаг убрали в пользу модификатора
> *Smooth by Angle*. Оператор `normals_make_consistent` остаётся на месте,
> но если его нет в твоей сборке, замени шаг на перебор полигонов с
> `polygon.use_smooth` в Python. Имена операторов проверь так:
> `hasattr(bpy.ops.mesh, "normals_make_consistent")`.

### Этап 5. Масштаб и пропорции

Генератор не знает реального размера предмета. Если не задать масштаб вручную, «бочка» окажется двухметровой, а потом внезапно — сантиметровой в экспорте.

```python
import bpy

mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')

# Привести к реальному размеру: высота ~0.9 м у barrel
mesh.dimensions.z = 0.9
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Опустить на землю, чтобы ноль сцены совпадал с основанием
for v in mesh.data.vertices:
    v.co.z -= min((mesh.matrix_world @ v.co).z for v in mesh.data.vertices)

print("final size:", tuple(round(d, 3) for d in mesh.dimensions))
```

### Этап 6. Ретопология и UV

Сырая сетка генератора почти всегда в неудобной топологии: неравномерные треугольники, нет петель, ничего не пригодно для ручной правки.

```python
import bpy, math

mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)

# Простой путь: децимация до бюджета. Минус — топология остаётся трёугольной
dec = mesh.modifiers.new("Decimate", 'DECIMATE')
dec.ratio = 0.25
bpy.ops.object.modifier_apply(modifier=dec.name)

# Альтернатива для аккуратной топологии: Quad Remesher (аддон, платный,
# не входит в стандартную поставку) или bpy.ops.object.voxel_remesh()
# перед последующим сглаживанием.

# UV: Smart Project даёт приемлемую развёртку на круглых предметах
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.01)
bpy.ops.object.mode_set(mode='OBJECT')

print("after retopo:", len(mesh.data.polygons), "faces,", len(mesh.data.uv_layers), "uv layers")
```

### Этап 7. Материал PBR

Текстура от генератора, если она есть, обычно непригодна для продакшена: разрешение низкое, UV зеркальные, карта нормалей отсутствует. Практичнее построить карты заново, запекая из геометрии.

```python
import bpy

mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = mesh

mat = bpy.data.materials.new("M_AI_Base")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value = (0.55, 0.42, 0.28, 1.0)
bsdf.inputs['Roughness'].default_value = 0.65
if bsdf.inputs.get('Metallic'):
    bsdf.inputs['Metallic'].default_value = 0.0
mesh.data.materials.clear()
mesh.data.materials.append(mat)

# AO и кривизну запекаем в отдельные текстуры — это и есть «изображение» предмета
ao_img = bpy.data.images.new("AO", width=2048, height=2048)
ao_img.filepath_raw = "//textures/ao.png"
ao_img.file_format = 'PNG'
bpy.ops.object.bake(type='AO')
ao_img.save()

curv_img = bpy.data.images.new("Curvature", width=2048, height=2048)
curv_img.filepath_raw = "//textures/curvature.png"
curv_img.file_format = 'PNG'
bpy.ops.object.bake(type='EMIT')
curv_img.save()
```

Запекание требует активного движка рендера и работает через оператор `bpy.ops.object.bake`; типы карт (`AO`, `EMIT`, `NORMAL`, `ROUGHNESS`, `DIFFUSE`) берутся из списка допустимых значений этого оператора в твоей версии.

```python
# Карта нормалей с разрешения с использованием High Poly-копии
bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT')
```

> [!NOTE]
> Параметры запекания настолько зависят от версии и настроек (distance, cage,
> margin, `selected_to_active`), что писать их значения в статье —
> гарантированно устареть через месяц. Открывай панель запекания
> (`Object Data → Texture` или вкладка запекания в свойствах объекта) и
> выставляй руками; то, что нужно для нормалей с разрешения, — это
> Target = Image Texture, Source = выбранный High Poly, Include: Only
> Closest / Cage. Всё остальное в панели можно оставить по умолчанию,
> пока не видно конкретных артефактов.

### Этап 8. Экспорт

```python
import bpy, os

os.makedirs(bpy.path.abspath("//exports/ai3d"), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath("//exports/ai3d/barrel.glb"),
    export_format='GLB',
    export_apply=True,          # модификаторы — в сетку, а не остаются в файле
    export_materials='EXPORT',
    export_image_format='AUTO',
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_animations=False,
)
print("saved:", bpy.path.abspath("//exports/ai3d/barrel.glb"))
```

## ✅ РЕЗУЛЬТАТ

**На выходе:** один `.glb` с геометрией, развёрткой UV, одним материалом и (если запекание прошло) текстурами AO и кривизны 2048×2048, плюс сам `.blend` со скриптами — чтобы результат можно было повторить, а не только получить.

**Форматы:** `.glb` (основной), при необходимости `.fbx` и `.obj` для движков без glTF.

**Кадров:** один ассет — это один результат, не анимация. Если в пайплайне несколько предметов, сцена при выводе состоит из N объектов и одного общего света.

**Оценка времени по порядку величины, конкретных замеров нет:** препроцессинг картинки — секунды; сама генерация — от единиц секунд до нескольких минут, в зависимости от сервиса и очереди; чистка, ретопология и запекание карт 2k — десятки секунд на GPU, единицы минут на CPU. Замеры в этой статье не приводятся: сильно зависят от сервиса, железа и размера результата.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| размер входа | 512–1024 по длинной стороне | меньше 512 — форма «мылится», больше 1024 время растёт без заметного выигрыша |
| `pad_ratio` | 0.8–0.9 | при 1.0 объект касается краёв и обрезается по габаритам |
| порог `remove_doubles` | 0.0005 (в метрах) | при крупном объекте поднять, иначе склеятся отдельные детали |
| `Decimate.ratio` | 0.2–0.4 | ниже 0.1 форма начинает «схлопываться» в грани |
| `smart_project angle_limit` | 66° | меньше — больше швов на цилиндрах |
| размер запечённых карт | 2048 | 4096 оправдано только для hero-ассетов |
| `export_apply` | `True` | без него модификаторы не попадут в файл |
| `export_animations` | `False` | для статичного предмета; для персонажа — `True` |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Фон попал в геометрию | фон не отделён, а кроп не сработал | альфа-маска вместо белого угла, проверить результат визуально |
| Модель «полая», видна изнанка | инвертированные нормали | `normals_make_consistent` на этапе чистки |
| Модель в неудобном масштабе | генератор не знает реального размера | задать `dimensions` вручную на этапе 5 |
| UV зеркальные, запекание едет | топология не пригодна для развёртки | ретопология до `Smart Project`, а не поверх сырой сетки |
| Текстуры 512, мыльно | разрешение результата генератора | пережать AO и кривизну заново в 2048 из своей геометрии |
| Карта нормалей вдавленная | запечатано из Low Poly вместо High Poly | запекать с High Poly в качестве Source |
| Экспорт пустой или без материалов | скрипт отработал до того, как сцена была готова | порядок этапов фиксировать скриптом, а не вручную |
| Генерация «не сработала» без ошибки | статус генератора был disabled | проверить `get_*_status` до генерации, а не после |

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md), [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md)
- **По темам:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](../setups/setup_45_hunyuan3d_21.md), [SETUP 44: RODIN / HYPER3D](../setups/setup_44_rodin_hyper3d.md), [SETUP 42: TRIPO AI API](../setups/setup_42_tripo_ai_api.md), [WF 19: VOXEL ART PIPELINE](wf_19_voxel_art_pipeline.md), [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md)
- **Теги:** #ai-3d, #pipeline, #workflow