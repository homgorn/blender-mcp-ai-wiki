---
id: setup_24_metashape_scan
lang: ru
category: setups
type: setup
status: full
tags: [photogrammetry, setup]
---
# SETUP 24: AGISOFT METASHAPE

**ID:** SETUP-24 | **Type:** Photogrammetry | **Difficulty:** ⭐⭐⭐ | **Time:** 60-150 min
**RU/EN Bilingual**

> Когда применять: когда фотограмметрию нужно повторить, а не сделать один раз: серия однотипных измерений, регулярный контроль объекта, батч из сотни объектов. Главное отличие от RealityCapture — у Metashape полноценная среда автоматизации: скрипты на Python, батч-обработка и повторяемость параметров.

## 🎯 ЦЕЛЬ
Описать пайплайн Metashape как воспроизводимый скрипт: выравнивание → разреженное и плотное облако → модель → UV → текстура → экспорт в OBJ/FBX. На выходе — `.py`-скрипт, который прогоняет съёмку от начала до конца без GUI, и понимание того, где в Blender продолжать: ретопология, запекание карт, экспорт.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Agisoft Metashape | 2.1 / 2.2 (Python 3) либо 1.9 (Python 2 — отдельно) | обработка |
| Лицензия | Standard/Pro/Education — влияет на число CPU-ядер и на экспорт | скорость |
| Python, совместимый с Metashape | версия зависит от мажорной версии Metashape | скрипты и батч |
| Blender | 4.2 LTS+ | приём результата |
| Scale bars либо референсные метки | для масштаба | реальный размер модели |
| Quad Remesher / QuadriFlow | см. примечание | ретопология для рендера |

> [!NOTE]
> Metashape 2.x использует Python 3, Metashape 1.9 — Python 2. Скрипты для них **не взаимозаменяемы**. Кроме того, набор методов `chunk` между версиями расширялся. Перед использованием скрипта проверь `dir(chunk)` в консоли Metashape — это надёжнее любого списка в статье.

## 🛠️ НАСТРОЙКА

### 1. Порядок и параметры шагов

```text
Классический порядок:
  1. Загрузка фото + Reference-панель (опционально)
  2. Alignment (сопоставление кадров)     → разреженное облако
  3. Оценка точности, добавление scale bar
  4. Dense cloud (плотное облако)         → XYZ-цвет
  5. Model (поверхность)
  6. Texture coordinates (UV)
  7. Texture (натяжка текстуры)
  8. Export (OBJ / FBX / PLY)
```

Где менять качество (в GUI и в скрипте параметры называются по-разному, но смысл один):

| Шаг | Быстро | Средне | Качественно |
|-----|--------|--------|-------------|
| Alignment | `downscale=4`, `generic_preselection=False` | `downscale=2`, `generic_preselection=True` | `downscale=1` |
| Dense cloud | `downscale=4` | `downscale=2` | `downscale=1`, `filter_stationary_points` |
| Model | `face_count=Low` | `face_count=Medium` | `face_count=High`, `face_count_quality` |
| Texture | 2048 | 4096 | 8192, `texture_size`, `ghosting_filter`, `white_balance` |

### 2. Скрипт: полный проход

```python
# pipeline.py — запускается в metashape.exe --run pipeline.py
import Metashape, os, sys

chunk = Metashape.app.document.chunk

# Каталоги. Используй os.path.join: обратные слэши в строках-константах
# ломаются при переносе скрипта на другую ОС.
PHOTOS = r"C:\scans\chair\images"
OUT    = r"C:\scans\chair"

DOWNSCALE      = 2      # alignment
DENSE_DOWNSCALE= 2
FACE_COUNT     = Metashape.Medium
TEXTURE_SIZE   = 4096

# 1. Список фото: расширения верхнего регистра — разные на камерах
exts = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
photos = []
for name in os.listdir(PHOTOS):
    if name.lower().endswith(exts):
        photos.append(os.path.join(PHOTOS, name))
photos.sort()      # порядок имён влияет на нумерацию кадров и на стабильность
print("фотографий:", len(photos))

# 2. Загрузка. chunk.addPhotos умеет брать список либо снимать кадры с камеры
chunk.addPhotos(photos)

# 3. Ограничить перекрытие между кадрами (сильно ускоряет, если снимали
#    с избыточностью)
chunk.matchPhotos(downscale=DOWNSCALE, generic_preselection=True,
                  overlap=0.75)

# 4. Выравнивание + разреженное облако
chunk.alignCameras()
print("камер:", len(chunk.cameras), "| точек:", len(chunk.tie_points))

# 5. Фильтрация: выкидываем точки с высокой ошибкой и слабой связностью
chunk.filterTiePoints(min_viewing_angle=10,
                      reprojection_error=0.5,
                      reconstruction_error=0.5)

# 6. Плотное облако
chunk.buildDepthMaps(downscale=DENSE_DOWNSCALE, filter_mode='blur')
chunk.buildPointCloud()

# 7. Модель
chunk.buildModel(source_data=Metashape.PointCloudData,
                 face_count=FACE_COUNT,
                 face_count_quality=50)

# 8. Развёртка и текстура
chunk.buildUV(page_count=1, texture_size=TEXTURE_SIZE)
chunk.buildTexture(texture_size=TEXTURE_SIZE,
                   ghosting_filter=True,
                   white_balance=False)

# 9. Экспорт. save_as=False — не трогаем .psx-проект на диске
chunk.exportModel(path=os.path.join(OUT, "model.obj"),
                  texture_format=Metashape.ImageFormatJPEG,
                  texture_size=TEXTURE_SIZE,
                  save_as=False,
                  export_format=Metashape.ModelFormatOBJ)

print("готово:", os.path.join(OUT, "model.obj"))
```

> [!NOTE]
> Имена аргументов в Metashape менялись между версиями (например, параметры фильтрации и `save_as`). Если скрипт падает на `TypeError`, сначала проверь: `help(chunk.buildModel)`, `help(chunk.buildTexture)`, `dir(chunk.filterTiePoints)`. Это 10 секунд и точнее, чем любая статья.

### 3. Масштаб: scale bar и reference

Без этого модель произвольного размера, и в Blender всё придётся угадывать.

```text
Вариант A — Scale Bar (две точки + расстояние):
  1. Взять известное расстояние (длина стола, рост человека)
  2. В Metashape: правый клик на 2 точки → Add Scale Bar → вписать длину
  3. Либо скриптом:
       chunk.addScaleBar(point1_id, point2_id, distance)
     Точки берутся из tie_points: chunk.tie_points.items()

Вариант B — Reference-панель (координаты известны):
  1. Снимки с известными GPS-координатами грузятся с выравниванием
     по координатам, потом:
       chunk.addMarker(point_id)
       marker.reference.location = Metashape.Vector([lon, lat, alt])
       marker.reference.altitude = ...
       marker.reference.coordinate_system = "EPSG:4326"
  2. Либо CRS всего проекта:
       chunk.crs = Metashape.CoordinateSystem("EPSG:4326")
       chunk.crs.estimate_scale()   # масштаб выводится из GPS
```

```python
# Масштаб по GPS — полезно для съёмки с дрона и для больших объектов
def apply_geographic_scale(chunk):
    chunk.crs = Metashape.CoordinateSystem("EPSG:4326")
    ok = chunk.crs.estimate_scale()
    print("масштаб вычислен:", ok)
    if ok:
        print("координаты центра:", chunk.center)
    return ok
```

### 4. Батч: серия объектов

```python
# batch.py — цикл по всем съёмкам. Запускать на отдельной машине
# или в фоне: Metashape держит память между проектами.
import Metashape, os, glob, sys

BASE = r"C:\scans"
for proj in sorted(glob.glob(os.path.join(BASE, "*"))):
    images = os.path.join(proj, "images")
    if not os.path.isdir(images):
        continue

    doc = Metashape.Document()
    chunk = doc.chunk

    photos = sorted(
        os.path.join(images, n) for n in os.listdir(images)
        if n.lower().endswith(('.jpg', '.jpeg', '.png'))
    )
    print("=" * 40, proj, len(photos), "фото")

    chunk.addPhotos(photos)
    chunk.matchPhotos(downscale=2, generic_preselection=True, overlap=0.75)
    chunk.alignCameras()
    chunk.filterTiePoints(reprojection_error=0.5)
    chunk.buildDepthMaps(downscale=2, filter_mode='blur')
    chunk.buildPointCloud()
    chunk.buildModel(source_data=Metashape.PointCloudData, face_count=Metashape.Medium)
    chunk.buildUV(page_count=1, texture_size=4096)
    chunk.buildTexture(texture_size=4096, ghosting_filter=True)

    doc.save(os.path.join(proj, "project.psx"))
    chunk.exportModel(path=os.path.join(proj, "model.obj"), save_as=False)
    print("OK", proj)
```

```bash
# Запуск headless на Windows (metashape.exe вместо .sh на Linux/macOS)
"C:\Program Files\Agisoft\Metashape Pro\metashape.exe" \
    -r pipeline.py                     # -r = запустить скрипт
    -platform offscreen                # без окна; полезно для сервера
```

### 5. Blender: приём и продолжение работы

```python
# metashape_import.py — Blender: Text Editor → Run Script
import bpy, os

MODEL = r"C:\scans\chair\model.obj"

def import_metashape(filepath=MODEL):
    if not os.path.exists(filepath):
        print("нет файла:", filepath); return
    with bpy.context.temp_override():
        bpy.ops.wm.obj_import(filepath=filepath, forward_axis='NEGATIVE_Z', up_axis='Y')
    ob = bpy.context.view_layer.objects.active
    print(f"{ob.name}: {len(ob.data.vertices):,} v, {len(ob.data.polygons):,} f, "
          f"размер {tuple(round(d, 3) for d in ob.dimensions)}")
    return ob

ob = import_metashape()

# То же для облака точек (PLY). Расширение импорта зависит от версии
# Blender — в 4.x это wm.point_cloud_import, в 3.x был import_mesh.ply
# bpy.ops.wm.point_cloud_import(filepath=r"C:\scans\chair\cloud.ply")
```

```python
# Проверка масштаба: если модель «примерно 1 м» — можно работать,
# если 0.01 или 100 — возвращаться в Metashape за scale bar
import bpy

ob = bpy.context.view_layer.objects.active
if ob:
    big = max(ob.dimensions)
    verdict = ("подозрительно мало" if big < 0.2 else
               "подозрительно много" if big > 50 else "правдоподобно")
    print(f"наибольшая сторона: {big:.3f} м — {verdict}")
    print("ориентиры: стул ~0.6, стол ~0.8, дверь 2.0, человек 1.75, авто 4.5")
```

### 5. Лидар и другие входные данные

Фотограмметрия — не единственный вход. Metashape умеет работать и с другой геометрией, и это меняет весь пайплайн:

```text
Вход                        Что получается                  Особенности
─────────────────────────  ─────────────────────────────    ──────────────────────
Фотографии с камеры         Сетка + цвет, произвольный      Стандартный случай
                           масштаб
Лидар (DJI, REVO, Leica)    Точная форма, слабый цвет       Лидарные точки импортируются
                                                         отдельным шагом; для текстуры
                                                         всё равно нужны фотографии
Скан из мобильного          Сетка среднего качества         Проблемы с масштабом, см.
приложения                 с известными размерами           SETUP 25
Одиночные размеры           Один вымеренный объект          Нужен для VR-калибровки
Изображения с EXIF GPS      Реальный масштаб из координат   crs.estimate_scale()
```

```python
# Импорт лидарных точек: путь зависит от версии Metashape и типа файла
# (форматы: LAS/LAZ от DJI и Leica, proprietary — от Matterport и др.)
def import_lidar(chunk, path):
    chunk.importPointCloud(path=r"C:\scans\dronelidar\points.ply",
                           format=Metashape.PointCloudFormatPLY)
    print("точек после импорта лидара:", len(chunk.tie_points))
    # Дальше: buildPointCloud / buildModel с source_data=PointCloudData
```

> [!NOTE]
> Имена констант форматов и сигнатура `importPointCloud` различаются между версиями Metashape 1.x и 2.x. Проверь `help(chunk.importPointCloud)` в консоли Metashape перед использованием. Также: лидарные форматы — LAS/LAZ/PLY, а не proprietary-файлы производителей; конвертация нужна отдельным инструментом.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```text
Ориентиры по объёму данных (средняя дистанция, объект ~1 м):
  фото 24 МП   400–800 снимков   →  модель 1–3 млн полигонов
  фото 45 МП   200–500 снимков   →  модель 2–6 млн полигонов
  Лидар (DJI/REVO) + текстуры    →  модель 5–20 млн, резче форма

Время (8 ядер CPU, без GPU):
  Alignment 400 фото      ~5–15 мин
  Dense cloud downscale=2  ~20–60 мин
  Model (High)            ~10–30 мин
  Texture 4K              ~10–40 мин
  Итого: 45–150 мин на объект
```

```python
# Инструмент, который экономит часы: логирование прогресса в файл
import Metashape, time

def timed(label, fn, *args, **kwargs):
    t0 = time.time()
    result = fn(*args, **kwargs)
    dt = time.time() - t0
    with open(r"C:\scans\timing.log", "a", encoding="utf-8") as f:
        f.write(f"{label:24s} {dt:8.1f}s\n")
    print(f"{label:24s} {dt:8.1f}s")
    return result

chunk = Metashape.app.document.chunk
timed("alignCameras",     chunk.alignCameras)
timed("buildDepthMaps",   chunk.buildDepthMaps, downscale=2)
timed("buildPointCloud",  chunk.buildPointCloud)
timed("buildModel",       chunk.buildModel, source_data=Metashape.PointCloudData,
                          face_count=Metashape.Medium)
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| `matchPhotos.downscale` | 4 черновик, 2 рабочий, 1 финал | меньше = точнее и медленнее |
| `overlap` | 0.75 | выше 0.8, если кадры сняты с запасом |
| `reprojection_error` | 0.3–0.6 | ниже 0.3 отсекает слишком много точек |
| `filter_mode` в buildDepthMaps | `blur` | попробуй `none`, если `blur` теряет детали |
| `face_count` | Low/Medium/High | High = в разы больше времени |
| `page_count` в buildUV | 1 | 2 и больше — раскладка на несколько тайлов |
| `texture_size` | 4096 | 8192 требует много RAM |
| `ghosting_filter` | `True` | обязателен при движущемся объекте/людях в кадре |
| `white_balance` | `True` | выравнивает цвет между кадрами; иногда портит задуманный оттенок |
| `save_as=False` при экспорте | всегда | иначе перезапишет .psx-проект |

### Про экспорт: OBJ против FBX

```text
OBJ + отдельный текстурный атлас:
  + простой, читается везде, текстура одним файлом
  − вершины раскрыты (дублирование на швах): файл в разы больше

FBX:
  + общая топология (shared vertices), компактнее
  − UV и материалы интерпретируются по-разному в разных программах

PLY:
  + для облака точек, большой XYZ-цвет
  − как меш бесполезен (нет граней)
```

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| `alignCameras` сопоставил 10 из 400 кадров | Мало перекрытия, нет текстуры, блики | Метки/текстура, другой свет, переснять |
| `TypeError` на любом методе скрипта | Версия Metashape не та, что ожидал скрипт | `help(chunk.buildModel)` в консоли, адаптируй вызов |
| Модель размером 0.003 м | Нет scale bar | `addScaleBar` или `crs.estimate_scale()` |
| Текстура размытая на краях | Мало ракурсов или `face_count` слишком низкий | Переснять основание, `face_count=High` |
| Чёрные «призраки» в текстуре | Люди или движение в кадрах | `ghosting_filter=True`, переснять без людей в кадре |
| Текстура в одном тоне, полосы | Пересвет на части кадров | Изменить экспозицию при съёмке, уменьшить диафрагму |
| `buildModel` ест всю RAM | `face_count=High` + большое облако | Понизить face_count, увеличить downscale в dense cloud |
| Экспорт OBJ весит больше, чем входные фото | Развёрнутая топология | Перейти на FBX или на экспорт с `save_as=False` |
| Blender падает на импорте | 15 млн полигонов OBJ | Прорежить в Metashape на этапе Model, а не в Blender |
| Импорт OBJ вверх ногами | Не заданы оси | `forward_axis='NEGATIVE_Z', up_axis='Y'` |
| Батч упал на середине и потерял 3 часа | Нет промежуточного сохранения | `doc.save()` после каждого объекта; устойчивость важнее красоты |
| `.psx` не сохраняется | Нет прав на каталог или проект read-only | Проверь путь; сохраняй в ASCII-каталог |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 23: REALITYCAPTURE SCAN TO BLENDER](setup_23_realitycapture_scan.md), [SETUP 25: POLYCAM / LUMA / KIRI SCAN](setup_25_polycam_luma.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **Теги:** #photogrammetry, #setup