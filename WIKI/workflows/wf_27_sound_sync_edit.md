---
id: wf_27_sound_sync_edit
lang: ru
category: workflows
type: workflow
status: full
tags: [audio, workflow]
---
# WF 27: SOUND-SYNC EDIT

**ID:** WF-27 | **Type:** Audio | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда кадры рендера уже есть и нужно их подмонтировать под музыку: нарезка по биту, синхронизация сцены, нормализация громкости, экспорт с аудио.

## 🎯 ЦЕЛЬ

Музыка становится **сеткой монтажа**, а не украшением: длительность сцены выводится из трека, смена плана ставится на доли, громкость приводится к целевой, а на выходе идёт ролик с синхронной звуковой дорожкой.

Единственный надёжный способ синхронизации — считать кадры, а не «слушать и подкручивать». Всё остальное (визуальный бит, реакция света, движение камеры) — надстройка поверх сетки, построенной по темпу.

> [!NOTE]
> В Blender **нет** встроенного аудио-анализа для шейдеров и геометрии: ноды шейдеров не видят звук, а драйверы не читают огибающую. Реакция на звук делается так: огибающую считают вне Blender, записывают в CSV или в F-кривые, и уже ими управляют через драйверы. Инструменты анализа — DAW или `ffmpeg` (фильтры `astats`, `ebur128`); в самой статье используется только то, что гарантированно есть.

## 📋 ЧТО ПОНАДОБИТЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с VSE (Sequence Editor) | встроенный | монтаж и синхронизация |
| Аудиофайл | WAV/MP3, BPM известен или измерен | сетка монтажа |
| `ffmpeg` в PATH | версия любая recent | нормализация громкости и проверка |
| Готовые кадры/ролики | PNG-последовательность или видео | материал для монтажа |

## 🛠️ НАСТРОЙКА

### Этап 1. Сцена под трек, а не наоборот

```bash
RU: "Монтаж под музыку: трек //audio/theme.mp3, 128 BPM, 24 fps.
     Сделай маркеры на каждый бит и на каждую долю, длительность сцены = трек,
     полосы в VSE, экспорт //renders/reel_"
EN: "Music-synced edit: track //audio/theme.mp3, 128 BPM, 24 fps.
     Mark every beat and every subdivision, scene length = track,
     strips in the VSE, export to //renders/reel_"
```

```python
import bpy, math

BPM, FPS = 128.0, 24
SEC = 212.4                       # длительность трека, сек — измерь, не угадывай

sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start = 0                # 0-based: так маркеры и кадры совпадают без смещения
sc.frame_end = int(SEC * FPS)
sc.sync_mode = 'AUDIO_SYNC'       # проигрывание вьюпорта по звуку, а не по таймеру

def frames_per_beat(bpm, fps, division=1):
    """Кадров на одну долю. division=2 -> восьмая, 4 -> шестнадцатая."""
    return 60.0 / bpm * fps / division

F = frames_per_beat(BPM, FPS)
print(f"128 BPM @ {FPS} fps -> бит = {F:.3f} кадра, 1/4 = {F/4:.3f} кадра")
```

### Этап 2. Маркеры по биту и по долям

Маркеры — это и есть редакционная карта: по ним и режут, и потом сверяются.

```python
import bpy
sc = bpy.context.scene
for mk in list(sc.timeline_markers):
    sc.timeline_markers.remove(mk)

def mark_grid(fpb, fps, frame_end, prefix):
    n = 0
    f = 0.0
    while f <= frame_end:
        sc.timeline_markers.new(f"{prefix}_{n:03d}", frame=int(round(f)))
        f += fpb
        n += 1
    return n

beat_fpb = 60.0 / BPM * FPS
nb = mark_grid(beat_fpb, FPS, sc.frame_end, "beat")
ns = mark_grid(beat_fpb / 4, FPS, sc.frame_end, "sub")   # шестнадцатые
print(f"маркеров: битов {nb}, долей {ns}, всего {len(sc.timeline_markers)}")
```

### Этап 3. Аудио в VSE

Имя коллекции API для полос менялось в Blender 4.4: было `sequence_editor.sequences`, стало `sequence_editor.strips`. Код ниже пробует оба и падает с понятным сообщением, а не молча.

```python
import bpy

sc = bpy.context.scene
se = sc.sequence_editor or sc.sequence_editor_create()

def strips_container(se):
    for attr in ("strips", "sequences"):
        coll = getattr(se, attr, None)
        if coll is not None:
            return coll
    raise AttributeError(
        "не нашёл ни sequence_editor.strips, ни sequence_editor.sequences — "
        "проверь имя в API своей версии")

strips = strips_container(se)

audio = bpy.data.sounds.load(bpy.path.abspath("//audio/theme.mp3"))
s1 = strips.new_sound(name="Theme", filepath=audio.filepath, channel=1, frame_start=0)
s1.volume = 1.0
s1.sound = audio
print("полос:", [getattr(s, "name", "?") for s in strips])
```

> [!NOTE]
> Сигнатуры `new_sound` / `new_image` / `new_movie` тоже менялись (добавлялись необязательные параметры вроде `fit_method`). Если твой вызов ругается на неизвестный аргумент — вызови `bpy.ops.sequencer` со списком доступных операторов или посмотри `getattr(strips, "new_sound").__doc__` в Python-консоли.

### Этап 4. Резать по биту

Не режем вручную: составляем монтажный план (EDL) как обычный CSV, который потом можно и в монтажку отдать, и скриптом разложить по полосам.

```python
import csv, bpy

beat_fpb = 60.0 / BPM * FPS
SHOTS = ["open_hall", "closeup_face", "wide_room", "insert_hands", "outro_title"]
# длительность каждого плана — целое число битов: 8, 16, 8, 16, 32
plan = [8, 16, 8, 16, 32]
assert len(plan) == len(SHOTS), "число планов должно совпадать с числом кадров"

edl, cursor = [], 0.0
for shot, beats in zip(SHOTS, plan):
    length = beats * beat_fpb
    edl.append(dict(shot=shot, start_frame=int(round(cursor)),
                    end_frame=int(round(cursor + length)), beats=beats,
                    sec_start=round(cursor / FPS, 3), sec_len=round(length / FPS, 3)))
    cursor += length

with open(bpy.path.abspath("//renders/edl.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(edl[0]))
    w.writeheader(); w.writerows(edl)

for e in edl:
    print(f"{e['shot']:<16} {e['start_frame']:>6} .. {e['end_frame']:<6} "
          f"({e['beats']} бит, {e['sec_len']} с)")
```

### Этап 5. Громкость

Стриминговые площадки требуют интегрированной громкости около **−14 LUFS** и пиков не выше −1 dBTP. Проверяется и приводится внешним инструментом, не на глаз.

```bash
# измерить текущую громкость (фильтр ebur128 печатает итог в конце)
ffmpeg -hide_banner -i "audio/theme.mp3" -af ebur128=peak=true -f null -

# привести к целевой громкости: I=-14 LUFS, TP=-1 dBTP, LRA=11
ffmpeg -hide_banner -i "audio/theme.mp3" -af loudnorm=I=-14:TP=-1.0:LRA=11 \
       -ar 48000 "audio/theme_norm.wav"
```

```python
# вернуть нормализованный трек в сцену
import bpy
se = bpy.context.scene.sequence_editor
strips = strips_container(se)
old = next((s for s in strips if s.type == 'SOUND'), None)
start = old.frame_start if old else 0
if old: strips.remove(old)
norm = bpy.data.sounds.load(bpy.path.abspath("//audio/theme_norm.wav"))
strips.new_sound(name="Theme_norm", filepath=norm.filepath, channel=1, frame_start=start)
```

### Этап 6. Реакция на звук: огибающая снаружи, драйверы внутри

Огибающую считают вне Blender и кладут в CSV. Дальше Blender просто читает числа.

```bash
# пример: RMS-огибающая в CSV (амплитуда в dB на каждое окно).
# Пути здесь уже настоящие, относительные к каталогу проекта — ffmpeg запускается из оболочки,
# а не из Blender, и префикс // (относительный путь Blender) для него не действует.
ffmpeg -hide_banner -i "audio/theme.wav" -ac 1 -ar 1000 \
       -af "astats=metadata=1:reset=24,ametadata=print:key=lavfi.astats.Overall.RMS_level" \
       -f null - 2>&1 | grep RMS_level > out/env_raw.txt
```

```python
import bpy, re, math

def load_envelope(path):
    """Парсит вывод ametadata в список float. Формат примитивный, поэтому честно: если формат
    изменится, load_envelope вернёт пустой список и ты это увидишь по печати."""
    out = []
    rx = re.compile(r"RMS_level=(-?\d+(?:\.\d+)?)")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = rx.search(line)
            if m:
                v = float(m.group(1))
                out.append(0.0 if v <= -70 else 10 ** (v / 20))   # dB -> линейная амплитуда
    return out

env = load_envelope(r"C:\BLENDER ai\out\env_raw.txt")
print("окон огибающей:", len(env), "макс:", round(max(env), 3) if env else None)

# реакция: масштаб объекта по огибающей через ключи (надёжнее драйвера по внешнему файлу)
ob = bpy.data.objects["PulseCube"]
STEP = max(1, len(env) // (bpy.context.scene.frame_end or 1))
for f in range(1, (bpy.context.scene.frame_end or 1) + 1, STEP):
    amp = env[min(f // STEP, len(env) - 1)] if env else 0.0
    ob.scale = (1.0 + amp * 0.4,) * 3
    ob.keyframe_insert("scale", frame=f)
```

### Этап 7. Экспорт с аудио

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format = 'MPEG4'
sc.render.ffmpeg.codec = 'H264'
sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.ffmpeg.audio_codec = 'AAC'
sc.render.filepath = r"//renders/reel_"
bpy.ops.render.render(animation=True)
```

> [!NOTE]
> Набор кодеков в `ffmpeg` зависит от того, как Blender собран (и от того, включён ли ffmpeg вообще). Если `file_format = 'FFMPEG'` не принимается — сначала проверь доступные форматы: `[i.identifier for i in sc.render.image_settings.bl_rna.properties["file_format"].enum_items]`. Надёжная запасная схема — отрендерить PNG-последовательность и собрать видео внешним ffmpeg.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `render.fps` | 24 / 25 / 30 | под частоту кадров трека и площадки |
| кадров на бит | `60/bpm × fps` | базовая единица монтажа |
| `sync_mode` | `'AUDIO_SYNC'` | проигрывание по звуку в реальном времени |
| `frame_start` | `0` | так маркеры и кадры не разъезжаются на единицу |
| `loudnorm I` | `−14` LUFS | целевая интегрированная громкость для стриминга |
| `loudnorm TP` | `−1.0` dBTP | пик, чтобы не было клиппинга на транскодере |
| `constant_rate_factor` | `'HIGH'` | ниже — меньше файл, выше — меньше артефактов |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `AttributeError` на `sequences` / `strips` | переименование API в 4.4 | резолвер выше: пробует оба имени |
| Монтаж «едет» на доли | длительность плана не кратна биту | длительности задавать целым числом битов (8/16/32) |
| Видео без звука | `audio_codec` не задан или полоса не в кадре | `ffmpeg.audio_codec='AAC'`, проверить `frame_start` полосы |
| Звук «хрипящий» после транскодера | пик выше −1 dBTP | нормализация `loudnorm` до −1 dBTP |
| Сцена проигрывается рывками | `sync_mode` выключен или сцена тяжелее реального времени | `AUDIO_SYNC` и облегчить сцену |
| Реакция на звук не работает | ждали, что шейдер услышит аудио | огибающую считать вне Blender и вести через ключи/драйверы |
| Кадры и звук расходятся к концу | fps рендера и fps трека разные | одинаковый `fps` + рендер ровно `frame_end` кадров |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` со сценой длиной ровно в трек, маркерами на биты и доли, аудиополосой в VSE, монтажным планом `//renders/edl.csv`, и готовый файл `//renders/reel_*.mp4` с AAC-дорожкой.

Характеристики — **оценка по порядку величины, а не измеренный результат**: ролик 3.5 минуты при 24 fps — это порядка 5000 кадров. В VSE-рендере (то есть пересборка из готовых клипов) это секунды-десятки секунд. Рендер 3D-сцены под 24 кода — совсем другая история, см. [WF 01](wf_01_text_to_scene.md). Файл 1920×1080, 3.5 минуты, H264 CRF `HIGH` с AAC — порядка 50–150 МБ.

**Это оценка.** Время зависит от того, что именно рендерится (VSE-пересборка или 3D), и от битрейта; измеряй у себя.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md), [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md)
- **По темам:** [WF 06: ARCHVIZ WORKFLOW](wf_06_archviz_workflow.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md), [WF 08: BATCH PROCESSING](wf_08_batch_processing.md)
- **Теги:** #audio, #workflow