---
id: setup_07_ci_cd
lang: ru
category: setups
type: setup
status: full
tags: [ci, setup]
---
# SETUP 07: CI/CD INTEGRATION

**ID:** SETUP-07 | **Type:** Automated Pipeline | **Difficulty:** ⭐⭐ | **Time:** 20-40 min

---

> Когда применять: когда сцену или набор ассетов нужно регулярно рендерить и экспортировать, а ручной прогон перестал быть воспроизводимым: у кого-то другой Blender, у кого-то другие текстуры, и «у меня работает» больше не аргумент.

## 🎯 ЦЕЛЬ

Собрать пайплайн, где Blender запускается в фоновом режиме из командной строки, выполняет заранее записанные в репозитории скрипты рендера и экспорта, отдаёт артефакты и при этом **ломает сборку**, если сцена невалидна.

Настраиваем три вещи. Первая — разделение данных и логики: скрипты живут в git, а `.blend` считается входным артефактом, версия которого тоже в репозитории. Вторая — окружение: зафиксированная версия Blender и headless-драйверы, чтобы GPU-рендер и CPU-рендер не были разными сценами. Третья — уровни проверок: дешёвая валидация на каждом pull request и полный рендер по расписанию или тегу.

Принцип, из которого следует всё остальное: **CI не должен уметь рендерить красиво — он должен уметь повторяться**. Любой параметр, влияющий на результат, задаётся скриптом. Значение, набранное в окне настроек и сохранённое в `.blend`, воспроизвести невозможно: другой человек откроет файл, увидит то же самое и не догадается, что это было решением, а не дефолтом.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender | зафиксированная версия, распакованная из tar-архива дистрибутива | рендер должен идти тем же билдом, что и локально |
| Python из поставки Blender | bundled | системный Python не видит модуль `bpy` |
| `xvfb` | пакет Ubuntu | виртуальный X-сервер для EEVEE; Cycles в `-b` обычно обходится без него |
| `ffmpeg` | системный или статический | сборка превью из отрендеренных кадров |
| Раннер с GPU | опционально, отдельный пул | Cycles на CPU считает, но на порядок медленнее |
| Хранилище артефактов | встроенное у CI-провайдера | выгрузка превью, кадров и экспортированных ассетов |

## 📋 CI/CD СЦЕНАРИИ

| Сценарий | Триггер | Действия |
|----------|---------|----------|
| **PR Validation** | Pull Request | линт скриптов, проверка сцены, быстрый рендер одного кадра |
| **Nightly Build** | расписание (cron) | полный рендер, регрессионные тесты, метрики |
| **Release** | push тега | финальный рендер, экспорт ассетов, публикация |
| **Asset Update** | изменение текстур или скриптов | пересборка только зависимых сцен |

## 🛠️ НАСТРОЙКА

### Шаг 1. Зафиксировать версию Blender

Версия и URL архива задаются переменными окружения, а не зашиты в команды. Сам список релизов лежит на `https://download.blender.org/release/` — там же лежат файлы `.tar.xz` для Linux и `.zip` для Windows.

```yaml
env:
  BLENDER_VERSION: "4.2"
  # Полный список релизов: https://download.blender.org/release/
  BLENDER_URL: "https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"
```

> [!NOTE]
> Проверь конкретный патч-номер по списку релизов перед фиксацией в YAML. Сборка,
> которая работала месяц, падает через месяц только потому, что файл перестал
> существовать или его переименовали. Если команда не готова обновляться
> намеренно, хранить стоит не «последнюю», а конкретную проверенную версию —
> и отдельным шагом описывать процедуру апгрейда.

### Шаг 2. Композитное действие для установки

Отдельное composite-действие переиспользуется всеми джобами: иначе блок установки копируется в три места и через месяц разъезжается.

```yaml
# .github/actions/setup-blender/action.yml
name: "Setup Blender"
description: "Install and configure Blender for CI"
inputs:
  version:
    description: "Blender version"
    required: false
    default: "4.2"

runs:
  using: "composite"
  steps:
    - name: Download Blender
      run: |
        VERSION="${{ inputs.version }}"
        URL="https://download.blender.org/release/Blender${VERSION%.*}/blender-${VERSION}-linux-x64.tar.xz"
        wget -q "$URL" -O blender.tar.xz
        tar -xf blender.tar.xz
        echo "$(pwd)/blender-${VERSION}-linux-x64/blender" >> $GITHUB_PATH
      shell: bash

    - name: Install xvfb
      run: sudo apt-get update && sudo apt-get install -y xvfb
      shell: bash

    - name: Verify Blender
      run: |
        blender --version
      shell: bash
```

### Шаг 3. Скрипт валидации сцены

Это самый дешёвый и самый полезный скрипт в пайплайне: он ловит битые пути к текстурам, пустые материалы, объекты вне кадра и несохранённые изменения — раньше, чем потрачены часы рендера.

```python
# scripts/validate_scene.py — запускается как: blender -b scene.blend -P scripts/validate_scene.py
import bpy, os, sys

errors = []
report = []

# 1. Разрешить //-пути относительно самого blend-файла, а не рабочего каталога
bpy.ops.file.make_paths_absolute()

# 2. Пропавшие текстуры
for img in bpy.data.images:
    if img.source == 'FILE' and not os.path.exists(bpy.path.abspath(img.filepath)):
        errors.append(f"missing image: {img.name} -> {img.filepath}")

# 3. Объекты с материалом, но без геометрии / с пустым мешем
for ob in bpy.data.objects:
    if ob.type == 'MESH' and len(ob.data.polygons) == 0:
        errors.append(f"empty mesh: {ob.name}")

# 4. Объекты без материала — почти всегда недосделанная работа
for ob in bpy.data.objects:
    if ob.type == 'MESH' and len(ob.data.materials) == 0:
        report.append(f"no material (warn): {ob.name}")

# 5. Камера и рендер-движок
if not bpy.context.scene.camera:
    errors.append("scene has no camera")

for line in report:
    print("WARN:", line)
for line in errors:
    print("ERROR:", line)

print(f"validate_scene: {len(errors)} errors, {len(report)} warnings")

if errors:
    # В фоновом режиме SystemExit прерывает Blender, и процесс возвращает
    # ненулевой код выхода — именно его читает CI.
    sys.exit(1)
```

> [!NOTE]
> Проверь фактический код возврата в своей версии Blender одной командой:
> запусти скрипт с `sys.exit(1)` вручную и посмотри на `$?` (в PowerShell — на
> `$LASTEXITCODE`). Если ненулевой код не доходит до CI, замени завершение на
> `bpy.ops.wm.quit_blender()` в конце скрипта и проверь ещё раз.

### Шаг 4. Скрипт превью

```python
# scripts/render_preview.py
import bpy
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32                    # превью: дёшево и шумно, это нормально
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 50      # превью не обязано быть полным размером
scene.render.filepath = "//preview/preview_"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

bpy.ops.render.render(write_still=True)
print("preview rendered:", scene.render.filepath)
```

### Шаг 5. Скрипт полного рендера

```python
# scripts/render_full.py
import bpy, sys, argparse

argv = sys.argv[sys.argv.index("--") + 1:]
parser = argparse.ArgumentParser()
parser.add_argument("--resolution", choices=["1080p", "4k"], default="1080p")
parser.add_argument("--samples", type=int, default=256)
parser.add_argument("--output", default="//renders/")
parser.add_argument("--device", choices=["CPU", "GPU"], default="CPU")
args = parser.parse_args(argv)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = args.device
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.use_denoising = True

res_map = {"1080p": (1920, 1080), "4k": (3840, 2160)}
scene.render.resolution_x, scene.render.resolution_y = res_map[args.resolution]
scene.render.resolution_percentage = 100

scene.render.filepath = args.output
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '32'

bpy.ops.render.render(animation=True)
print("full render complete:", args.resolution, "@", args.samples, "samples")
```

> [!NOTE]
> Про денойзер: в Cycles доступно несколько реализаций (`OPTIX`, `OPENIMAGEDENOISE`,
> а в части сборок ещё один). `OPTIX` требует NVIDIA-карту и на CPU-раннере упадёт,
> поэтому в общем пайплайне оставляй денойзер по умолчанию и включай конкретный
> только в джобе с GPU. Полный список значений этого поля смотри в
> `Render Properties → Sampling → Denoiser` своей версии.

### Шаг 6. Скрипт экспорта

```python
# scripts/export_assets.py
import bpy, os, sys, argparse

argv = sys.argv[sys.argv.index("--") + 1:]
parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", default="exports/")
parser.add_argument("--formats", nargs="+", default=["GLB"])
args = parser.parse_args(argv)

os.makedirs(args.output_dir, exist_ok=True)

for obj in bpy.data.objects:
    if obj.type != 'MESH' or not obj.get("export", True):
        continue

    for fmt in args.formats:
        fmt_dir = os.path.join(args.output_dir, fmt.lower())
        os.makedirs(fmt_dir, exist_ok=True)
        filepath = os.path.join(fmt_dir, obj.name.replace(" ", "_") + "." + fmt.lower())

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        if fmt == "GLB":
            bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB',
                                      use_selection=True, export_apply=True)
        elif fmt == "FBX":
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True,
                                    apply_unit_scale=True,
                                    object_types={'ARMATURE', 'MESH'})

print("export done ->", args.output_dir)
```

> [!NOTE]
> Набор аргументов у операторов экспорта разный и менялся между версиями
> (`bpy.ops.export_scene.gltf`, `bpy.ops.export_scene.fbx`, экспорт в USD
> вынесен в отдельную группу операторов). Не переноси флаги из одной версии в
> другую списком — вызови оператор один раз, открой его параметры через
> `bpy.ops.export_scene.gltf.get_rna_type().properties`, и сверяйся с тем, что
> реально есть. Нераспознанный именованный аргумент в Python — это `TypeError`,
> и пайплайн упадёт целиком, а не «предупредит и продолжит».

### Шаг 7. Workflow

```yaml
# .github/workflows/blender.yml
name: Blender CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'scenes/**/*.blend'
      - 'scripts/**/*.py'
      - '.github/workflows/blender.yml'
  pull_request:
    branches: [main]
    paths:
      - 'scenes/**/*.blend'
      - 'scripts/**/*.py'
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  validate:
    name: Validate scene
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-blender
      - name: Validate
        run: |
          xvfb-run -a blender -b scenes/main.blend -P scripts/validate_scene.py
      - name: Lint render scripts
        run: |
          python -m pip install --upgrade pip flake8
          flake8 scripts/ --max-line-length=120 --ignore=E501,W503

  render-preview:
    name: Render preview (PR)
    needs: validate
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-blender
      - name: Preview
        run: |
          xvfb-run -a blender -b scenes/main.blend -P scripts/render_preview.py
      - uses: actions/upload-artifact@v4
        with:
          name: render-preview
          path: preview/
          retention-days: 7

  render-full:
    name: Full render
    needs: validate
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    timeout-minutes: 240
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-blender
      - name: Full render
        run: |
          xvfb-run -a blender -b scenes/main.blend -P scripts/render_full.py -- \
            --resolution 1080p --samples 256 --device CPU --output //renders/
      - uses: actions/upload-artifact@v4
        with:
          name: renders
          path: renders/
          retention-days: 30
```

### Шаг 8. Порядок аргументов командной строки

Это место, где чаще всего теряется час: `-f 1`, `-a` и `-P` выполняются именно в том порядке, в котором написаны.

```bash
# НЕПРАВИЛЬНО: кадр 1 отрендерится раньше, чем скрипт поменяет настройки,
# и на выходе будет кадр из дефолтов сцены
blender -b scene.blend -f 1 -P scripts/render_preview.py

# ПРАВИЛЬНО: сначала выполняется скрипт, затем рендерится кадр
blender -b scene.blend -P scripts/render_preview.py -f 1

# Аргументы после "--" уходят в sys.argv скрипта, а не в сам Blender
blender -b scene.blend -P scripts/render_full.py -- --samples 512
```

### Шаг 9. GitLab CI

Тот же пайплайн в терминах GitLab — стадии вместо джоб, `artifacts` вместо `upload-artifact`.

```yaml
stages: [test, render, export, deploy]

variables:
  BLENDER_VERSION: "4.2"

before_script:
  - apt-get update -qq && apt-get install -y -qq blender xvfb ffmpeg

validate:
  stage: test
  script:
    - xvfb-run -a blender -b scenes/main.blend -P scripts/validate_scene.py

render_preview:
  stage: render
  script:
    - xvfb-run -a blender -b scenes/main.blend -P scripts/render_preview.py
  artifacts:
    paths: [preview/]
    expire_in: 1 week

deploy:
  stage: deploy
  script:
    - aws s3 sync exports/ "$ASSET_BUCKET/latest/" --delete
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  when: manual
```

> [!NOTE]
> Дистрибутивный пакет `blender` в репозиториях Ubuntu отстаёт от официального
> релиза на несколько версий. Если важна именно новая версия, ставь её из
> архива дистрибутива (Шаг 2), а не из `apt`.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `cycles.samples` (превью) | 24–64 | превью нужно для оценки композиции, а не качества |
| `cycles.samples` (финал) | 128–1024 | ниже 128 сцена с SSS или стеклом будет шумной |
| `resolution_percentage` | 50 для превью | вдвое меньше линейного разрешения вчетверо дешевле по времени |
| `render.image_settings.file_format` | `OPEN_EXR_MULTILAYER` для финала, `PNG` для превью | EXR нужен, чтобы пересобирать грейд без повторного рендера |
| `cycles.device` | `CPU` по умолчанию | `GPU` ставится отдельной джобе, где гарантированно есть карта |
| `timeout-minutes` | 15 для валидации, 240 для полного рендера | слишком маленький таймаут убивает длинный рендер на середине |
| `retention-days` | 7 для превью, 30 для релизов | артефакты съедают место квотированного хранилища |
| `BLENDER_VERSION` | одна зафиксированная версия на все джобы | рассинхрон версий даёт артефакты, которые не воспроизводятся локально |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| CI зелёный, картинка неправильная | скрипт выполнялся после `-f 1` и не успел поменять настройки | `-P script.py` всегда раньше `-f`/`-a` |
| `TypeError` на неизвестном аргументе экспорта | флаги скопированы из другой версии Blender | сверяться с `get_rna_type().properties` оператора в своей версии |
| Текстуры «пропали» в CI, локально есть | `//`-пути не разрешились: рабочий каталог раннера другой | `bpy.ops.file.make_paths_absolute()` перед экспортом и рендером |
| Денойзер падает на CPU-раннере | выбран GPU-специфичный денойзер | оставить денойзер по умолчанию, GPU-настройки — в отдельной джобе |
| Пайплайн зелёный, артефакта нет | скрипт вернул 0, но ничего не отрендерил | проверять ненулевой код возврата и наличие файлов в `preview/` |
| Рендер в 20 раз медленнее локального | раннер без GPU при `device = 'GPU'` | явный `CPU` на дешёвых раннерах, GPU — на отдельном пуле |
| Полный рендер съедает квоту и падает | нет `paths`-фильтра, тянутся все файлы сцены | сузить `paths` в триггере до `scenes/**` и `scripts/**` |
| Уведомление всегда «зелёное» | в job уведомлений `${{ job.status }}` — статус самого этого джоба | прокидывать статусы через `needs.*.result` или отдельную сводку |
| Windows-локально работает, Linux-раннер падает | в пути есть русские буквы или пробелы | держать в репозитории только ASCII-пути |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #ci, #setup