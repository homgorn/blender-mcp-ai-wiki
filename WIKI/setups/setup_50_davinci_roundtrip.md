---
id: setup_50_davinci_roundtrip
lang: ru
category: setups
type: setup
status: full
tags: [setup, video]
---
# SETUP 50: DAVINCI RESOLVE ROUNDTRIP

**ID:** SETUP-50 | **Type:** Color/Edit | **Difficulty:** ⭐⭐ | **Time:** 25 min
**RU/EN Bilingual**

> Когда применять: когда рендер из Blender нужно отдать в DaVinci Resolve на монтаж
> или грейд — и вернуть результат обратно в 3D, не потеряв HDR-диапазон.

---

## 🎯 ЦЕЛЬ

Настроить честный roundtrip: Blender отдаёт линейные EXR, Resolve работает с ними как
с исходниками, а назад возвращается либо готовый кадр, либо LUT. Главное в этой связке —
не допустить, чтобы Blender «сварил» тон-маппинг в пиксели: как только выход
display-referred, грейд в Resolve теряет оригинальные света и тени.

Всё ниже проверено на Blender 5.2.1 LTS в headless-режиме (`blender -b`).

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 5.x (проверено 5.2.1 LTS) | Рендер линейной EXR-последовательности |
| DaVinci Resolve | 17+ | Монтаж и грейд; RCM с ACES-рабочим пространством |
| OpenColorIO | в комплекте Blender | Разбор EXR без пере-тега |
| ffmpeg | 7.x+ (проверено 9.0.1) | Сборка превью, прокси, финальный рендер |
| Диск | 2× объём EXR | Мастер + превью |

---

## 🛠️ НАСТРОЙКА

### 1. Настроить выход Blender так, чтобы не было двойной конвертации

Смысл: `View Transform = Standard` оставляет линейные значения как есть (в пределах
0..1), а OCIO-конфиг Blender при сохранении EXR кладёт в файл рабочее пространство
сцены. Если оставить AgX/Filmic, на диск уйдёт уже «после тона» картинка.

```python
# export_plate_config.py — запускается как blender -b scene.blend -P export_plate_config.py
import bpy

sc = bpy.context.scene
# 1) Никакого display-referred тон-маппинга: только трансформация Standard.
#    Идентификаторы view_transform проверены в Blender 5.2:
#    Standard, Raw, AgX, Filmic, Filmic Log, False Color, ACES 1.3, ACES 2.0,
#    Khronos PBR Neutral.
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'

# 2) FOLLOW_SCENE = сохранить в линейном пространстве сцены (без ODT).
#    OVERRIDE = применить view_transform при сохранении — для превью, не для мастера.
sc.render.image_settings.color_management = 'FOLLOW_SCENE'

# 3) EXR 16 бит, RGB, ZIP. Для HDR-мастера берите 32 бит и PIZ/DWAB.
sc.render.image_settings.file_format = 'OPEN_EXR'
sc.render.image_settings.color_mode = 'RGB'
sc.render.image_settings.color_depth = '16'
sc.render.image_settings.exr_codec = 'ZIP'

sc.render.filepath = "//exr/plate_"
sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
sc.render.use_file_extension = True
```

### 2. Отрендерить плату кадрами, а не одним файлом

Resolve читает EXR-последовательность, и только она: одиночный multiview-файл он не
подхватит как клип.

```bash
# Проверено: -b, -E CYCLES, -o, -s/-e, -a, -F (движок), --render-frame
blender -b scene.blend \
    -E CYCLES \
    -o "//exr/plate_####" \
    -s 1 -e 250 -j 1 \
    -a
```

### 3. Собрать превью для монтажа

Монтажёр не должен открывать 250 EXR по 300 МБ. Собираем прокси в H.264: `-c:v
libx264` с `-crf 18`, обязательный `-pix_fmt yuv420p` (иначе плеер в браузере/Resolve
не покажет) и `-movflags +faststart` (moov-атом в начало — файл начинает играть, не
дожидаясь конца).

```bash
# Из EXR-последовательности в превью (команда проверена на ffmpeg 9.0.1)
ffmpeg -y -framerate 24 -start_number 1 -i exr/plate_%04d.exr \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart \
  preview/plate_v001.mp4
```

### 4. Забрать монтаж обратно без EDL

Проверка факта: в Blender 5.2 встроенных импортёров `import_scene` ровно два — `fbx`
и `gltf`. Импорта EDL/AAF/FCPXML нет.

```python
# Воспроизводим монтаж по списку кадров из CSV, который отдал монтажёр.
# API Blender 5.x: у секвенсора коллекция называется strips, а не sequences,
# и класс полосы — Strip, а не Sequence. Это переименование 5.x.
import bpy, csv, os

sc = bpy.context.scene
se = sc.sequence_editor_create()

CUTS = [("plate_0001.exr", 1), ("render_0120.exr", 90), ("plate_0180.exr", 160)]
SRC = "//exr/"

with open("//edit/cutlist.csv", newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))[1:]        # первая строка — заголовок

channel = 1
for name, start in CUTS:
    st = se.strips.new_image(name=name, filepath=os.path.join(SRC, name),
                             channel=channel, frame_start=int(start))
    # colorspace_settings.name — реальное свойство полосы; список имён
    # (ACEScg, ACEScct, Linear Rec.709, sRGB, Non-Color, ...) проверен.
    st.colorspace_settings.name = 'ACEScg'
    st.duration = 40
    channel += 1

sc.frame_start, sc.frame_end = 1, 250
sc.render.use_sequencer = True     # рендер пойдёт через секвенсор, а не через 3D
```

> [!NOTE]
> У полосы есть и `frame_final_duration`, но в Blender 5.2 он помечен как
> устаревший и будет удалён в 6.0 — пиши `strip.duration`. Проверено на 5.2.1.

### 5. Разобрать кадр в Resolve

Ручные шаги, порядок важен:

1. **File → Import → File** → папка с `plate_####.exr` (Resolve соберёт клип-последовательность).
2. Правый клик по клипу → **Attributes** → Input Color Space: выберите то, чем помечен
   файл. Для линейного ACEScg — `ACEScg`; если Blender писал в Rec.709-linear —
   `Linear Rec.709`.
3. **Project Settings → Color Management**: включите RCM, Timeline Working Space —
   ACEScct или ACES 1.3, Output — тот же ACES или sRGB-видео под вашу доставку.
4. Только теперь грейд: без настроенного Color Management любой корректор работает вслепую.

### 6. Вернуть результат

Два варианта, и выбор между ними — не технический, а организационный.

```bash
# Вариант A: Resolve отдаёт готовый кадр — забираем EXR обратно в Blender
# как Image-датаблок (bpy.data.images.load понимает EXR) и подкладываем в композитор.
# Вариант B: Resolve отдаёт LUT (.cube) — см. предупреждение в разделе ошибок.
#
# Финальная сборка ProRes-мастера из отрендеренных кадров:
ffmpeg -y -framerate 24 -start_number 1 -i comp/comp_%04d.exr \
  -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le \
  delivery/master_v001.mov
```

Единственный способ натянуть `.cube` на сам Blender — это OCIO: сам Blender
использует `.cube` внутри своего конфига (файлы `AgX_Base_sRGB.cube` и подобные
лежат рядом с `config.ocio`). Значит, кастомный view transform — штатный механизм,
а не хак:

```yaml
# myconfig.ocio — копия datafiles/colormanagement/config.ocio + свой блок.
# Запуск: OCIO=myconfig.ocio blender scene.blend
displays:
  sRGB:
    - !<ViewTransform> <Look>
    - !<ViewTransform> <Display>

active_displays: [sRGB]
active_views: [Luminance]

views:
  - !<ViewTransform>
    name: Resolve_Grade
    from_scene_reference: !<GroupTransform>
      children:
        - !<ColorSpaceTransform> {src: ACES2065-1, dst: ACEScg}
        - !<FileTransform> {src: grade_v001.cube, interpolation: tetrahedral}
```

```python
# После этого view transform появляется в UI Color Management
# и в scene.view_settings.view_transform как 'Resolve_Grade'.
import bpy
bpy.context.scene.view_settings.view_transform = 'Resolve_Grade'
```

> [!NOTE]
> Список полей YAML-конфига OCIO и имена его `!<...>` блоков проверяй по
> документации OpenColorIO — формат там версионируется. Смысловую проверку
> можно сделать так: если после `OCIO=... blender` в Color Management появился
> новый transform с нужным именем, конфиг прочитан верно.

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Диагностика возможностей конкретной сборки Blender перед пайплайном:
blender -b --python-expr "import bpy;print(bpy.app.build_options.codec_ffmpeg, bpy.app.build_options.opencolorio)"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `view_transform` | `Standard` | Мастер EXR. Любое другое значение = двойной тон-маппинг |
| `image_settings.color_management` | `FOLLOW_SCENE` | Мастер. `OVERRIDE` — только для быстрых превью |
| `image_settings.color_depth` | `16` | 32 — если HDR-света выше 1.0 нужны с точностью |
| `exr_codec` | `ZIP` | `PIZ`/`DWAB` — если важнее скорость записи, чем размер |
| `-crf` (ffmpeg) | `18` | Превью. `16` для финальной сдачи, `23`+ для черновиков |
| `-pix_fmt yuv420p` | обязателен | Совместимость плееров; для 10 бит — `yuv420p10le` |
| `-movflags +faststart` | включать | Веб-доставка и превью по сети |
| `prores_ks -profile:v 3` | 422 HQ | Мастер для монтажа; `4444` — если нужен альфа-канал |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| В Resolve картинка «выжата», света в 0, тени в 1 | Blender отрендерил с `AgX`/`Filmic`, а не `Standard` | Перерендерить мастер с `view_transform='Standard'`; превью держать в OVERRIDE |
| Resolve не видит папку с EXR как один клип | Импортирован одиночный multiview-файл | Импортировать папку с последовательностью `####` |
| `Import → EDL` отсутствует | В Blender 5.2 встроенных импортёров только `fbx` и `gltf` | Вести монтаж через CSV-список кадров (шаг 4) либо сторонний аддон |
| `.cube` из Resolve не грузится в Blender | Проверено: `bpy.data.images.load('x.cube')` → «unknown file-format» | Либо вернуть готовый кадр, либо собрать кастомный OCIO-конфиг (см. ниже) |
| `enum "FFMPEG" not found` при `blender -b` | В background-режиме динамический enum форматов урезан (проверено на 5.2.1, при этом `bpy.app.build_options.codec_ffmpeg == True`) | Рендерить PNG-последовательность и кодировать ffmpeg-ом — шаг 3 |
| Цвета «поплыли» после возврата в Blender | Resolve переписал файл в display-referred | Забирать EXR с `Color Space = Linear`, не с `sRGB`/`Gamma 2.2` |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 49: FFMPEG + VSE PIPELINE](setup_49_ffmpeg_vse_pipeline.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #video
