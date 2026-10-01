---
id: setup_49_ffmpeg_vse_pipeline
lang: ru
category: setups
type: setup
status: full
tags: [pipeline, setup, video]
---
# SETUP 49: FFMPEG + VSE PIPELINE

**ID:** SETUP-49 | **Type:** Video | **Difficulty:** ⭐⭐ | **Time:** 40 min

> Когда применять: когда нужно доделать монтаж и отдать клиенту файл, а Blender используется как VSE: сборка стрипов, прокси, а потом финальное кодирование через ffmpeg с правильными CRF, битрейтом и метаданными цвета.

## 🎯 ЦЕЛЬ

Blender умеет монтировать (Video Sequence Editor), но не лучший кодировщик под битрейт-контроль. Расклаиваем задачу на две части: VSE собирает таймлайн, прокси и финальную сборку; ffmpeg делает превью, инспекцию потоков, перекодирование в H.264/H.265 с заданным CRF и выгрузку мастер-файла. Отдельно разбираем HDR-метаданные — там главная ошибка в том, что перекодируешь в 8 бит и теряешь диапазон, даже если в команде написано «HDR».

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x LTS | VSE |
| ffmpeg / ffprobe | 4.x-7.x | кодирование и инспекция |
| Прокси-директория | отдельная папка кэша | иначе VSE будет читать тяжёлые исходники |
| Исходники | EXR-серия или ProRes | для HDR — только 10 бит |
| Диск | 2-3× размер исходников | прокси + мастер + превью |

## 🛠️ НАСТРОЙКА

### 1. Проверяем, что ffmpeg доступен и что умеет

```bash
ffmpeg -version
ffprobe -version
ffmpeg -encoders | grep -E "libx264|libx265|prores"
```

### 2. Создаём VSE-редактор и кладём стрипы

```python
import bpy
from pathlib import Path

SRC = Path(r"C:/edit/sources")

scene = bpy.context.scene
se = scene.sequence_editor_create()

# В 4.4+ коллекция называется strips, раньше — sequences. Берём то, что есть.
coll = se.strips if hasattr(se, "strips") else se.sequences
print("API:", "strips" if hasattr(se, "strips") else "sequences")

clips = sorted(SRC.glob("shot_*.mov"))
for i, p in enumerate(clips):
    strip = coll.new_movie(name=p.stem, filepath=str(p), channel=1, frame_start=i * 48 + 1)
    print(strip.name, strip.frame_final_duration, "кадров")
```

> [!NOTE]
> Переход `sequences` → `strips` в Blender 4.4 — ломающий для скриптов. Поэтому код выше сначала проверяет наличие атрибута, а не зашивает имя. Если пишешь скрипт под конкретную версию — зафиксируй её, иначе он сломается на следующем обновлении.

### 3. Кроссфейд между клипами

```python
a = coll.strips["shot_001"] if hasattr(coll, "strips") else coll.sequences["shot_001"]
b = coll.strips["shot_002"] if hasattr(coll, "strips") else coll.sequences["shot_002"]

bl = se.strips if hasattr(se, "strips") else se.sequences
bl.new_effect(type="CROSS", name="xf_001_002", channel=3,
              frame_start=a.frame_final_end - 12, frame_end=a.frame_final_end)

# Реальный кроссфейд = смещение второго клипа и его прозрачности
b.frame_start -= 12
b.frame_offset_start = 0
print("кроссфейд на кадрах:", a.frame_final_end - 12, "-", a.frame_final_end)
```

### 4. Текстовая плашка

```python
text = bl.new_effect(type="TEXT", name="slate", channel=4, frame_start=1, frame_end=48)
text.text = "SHOT 01 / TAKE 2"
print("text strip:", text.name, text.frame_final_duration)
```

### 5. Прокси

```python
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = 50
scene.render.use_proxy = True
# Каталог прокси задаётся в настройках Blender (Preferences -> File Paths ->
# Temporary Files) и/или через оператор ниже — имя оператора менялось между версиями
ops = [o for o in dir(bpy.ops.sequencer) if "proxy" in o]
print("proxy ops:", ops)
```

> [!NOTE]
> Набор операторов для прокси в VSE менялся: в разных версиях это `rebuild_proxy` / `proxy_build` / пересборка при импорте. Поэтому код печатает доступные имена, а не вызывает наугад. Включай `use_proxy` до добавления стрипов — иначе прокси не построятся.

### 6. Цвет и биты

```python
scene = bpy.context.scene
# 8 бит для SDR, 16 для HDR-последовательностей
scene.render.image_settings.color_depth = "16"
scene.render.image_settings.file_format = "OPEN_EXR"
print("view transform:", scene.view_settings.view_transform,
      "| look:", scene.view_settings.look)

# Стрипы читаются в своём colorspace — неверный здесь = мыло или пересветы
for s in (scene.sequence_editor.strips if hasattr(scene.sequence_editor, "strips")
          else scene.sequence_editor.sequences):
    if s.type == "MOVIE":
        print(s.name, "->", s.colorspace_settings.name)
```

### 7. Рендер сиквенции из Blender

```python
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "FFMPEG"
ff = scene.render.ffmpeg
print("format:", [i.identifier for i in
                   type(ff).bl_rna.properties["format"].enum_items])
print("codec:", [i.identifier for i in
                  type(ff).bl_rna.properties["codec"].enum_items])
print("crf:", [i.identifier for i in
                type(ff).bl_rna.properties["constant_rate_factor"].enum_items])
```

```bash
# В фоне: кодирование всей секвенции силами Blender
blender -b edit.blend -a
```

### 8. Превью через ffmpeg

```bash
ffmpeg -i master.mov -vf "fps=24,scale=1280:-2" -c:v libx264 -crf 23 -preset veryfast \
       -c:a aac -b:a 128k preview.mp4
```

### 9. Мастер и раздача

```bash
# ProRes 422 HQ — мастер без поколений: переживёт следующую перекодировку без потерь
ffmpeg -i master.mov -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s16le master_prores.mov

# H.264 — раздача
ffmpeg -i master.mov -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
       -movflags +faststart -c:a aac -b:a 192k delivery_h264.mp4

# H.265 — меньше весит, хуже совместимость
ffmpeg -i master.mov -c:v libx265 -crf 20 -preset slow -pix_fmt yuv420p \
       -tag:v hvc1 delivery_h265.mp4
```

### 10. HDR-метаданные

```bash
# Пометить как BT.2020 PQ без пережатия потока
ffmpeg -i hdr.mov -c copy \
  -color_primaries bt2020 -color_trc smpte2084 -colorspace bt2020nc \
  -color_range tv hdr_tagged.mov

# Проверить, что реально лежит внутри — всегда сверяй, а не верь флажкам
ffprobe -v error -select_streams v:0 -show_entries \
  stream=pix_fmt,color_space,color_transfer,color_primaries,bits_per_raw_sample \
  -of default=noprint_wrappers=1 hdr_tagged.mov
```

> [!NOTE]
> Строгое соответствие BT.2020 + PQ требует 10 бит. Если исходник 8-битный, теги будут правдой только наполовину: диапазон уже потерян при съёмке или конвертации. Проверяй `bits_per_raw_sample` в выводе `ffprobe` до, а не после того, как отдал файл.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Превью-стрип 1:1, чтобы поймать битые кадры до полного рендера
ffmpeg -i master.mov -vf "select='eq(n\,0)+not(mod(n\,48))'" -vsync vfr check_sheet_%03d.png
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `-crf` | `18` раздача / `23` превью | ниже — больше файл, выше — артефакты |
| `-preset` | `slow` финал / `veryfast` превью | влияет только на скорость и размер |
| `-pix_fmt` | `yuv420p` для совместимости | `yuv422p10le` для мастеров и HDR |
| `prores_ks -profile:v` | `3` = 422 HQ | `0` = Proxy для черновиков |
| `-movflags +faststart` | для mp4 в вебе | без него не будет прогрессивного стрима |
| `color_depth` в Blender | `16` для HDR | `8` для SDR хватает и быстрее |
| `resolution_percentage` | `50` для прокси | `100` на финале |
| `-b:a` | `192k` AAC | `-c:a copy` если исходник уже приемлем |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `AttributeError: 'SequenceEditor' has no 'strips'` | версия до 4.4 | используй `sequences`; код с проверкой `hasattr` работает в обоих |
| VSE тормозит при скрабе | прокси не построены | `render.use_proxy = True` **до** импорта стрипов |
| Цвета мылят в VSE | неверный colorspace у стрипа | `strip.colorspace_settings.name` под реал. формат |
| HDR-ролик после ffmpeg серый | 10 бит превратились в 8 | `-pix_fmt yuv422p10le`, проверь `bits_per_raw_sample` |
| mp4 не играется в браузере | нет faststart | `-movflags +faststart` |
| Звук рассинхронизирован | ffmpeg пережал аудио вместе с видео | `-c:a copy` для черновика, `-af aresample=async=1` если ресемплишь |
| Прерывистый прогресс / не играется вовсе | H.265 без `hvc1` | добавь `-tag:v hvc1` |
| «Файл повреждён» в монтажке | прерванная запись | `ffmpeg -i bad.mov -c copy fixed.mov` |
| Blender не кодирует в ProRes | зависит от сборки ffmpeg в Blender | кодируй через системный ffmpeg, Blender отдай PNG/EXR-серию |
| Клипы в разных FPS | разные исходники | приведи к одному FPS до сборки, иначе таймлайн разъедется |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 50: DAVINCI RESOLVE ROUNDTRIP](setup_50_davinci_roundtrip.md)
- **По темам:** [SETUP 55: AI UPSCALE PIPELINE](setup_55_ai_upscale_pipeline.md), [SETUP 59: WEB VIEWER EXPORT](setup_59_web_viewer_export.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md)
- **Теги:** #pipeline, #setup, #video
