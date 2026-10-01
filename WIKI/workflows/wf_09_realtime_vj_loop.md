---
id: wf_09_realtime_vj_loop
lang: ru
category: workflows
type: workflow
status: full
tags: [animation, workflow]
---
# WF 09: REALTIME VJ LOOP

**ID:** WF-09 | **Type:** Realtime | **Difficulty:** ⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен бесшовный цикл для выступления, студийного экрана или репетиции: 8 секунд, которые можно крутить в реальном времени, реагирующие на звук и управляемые извне.

## 🎯 ЦЕЛЬ

Процедурная сцена с жёстким требованием **замкнутости цикла**: первый и последний кадр совпадают, поэтому 8-секундный ролик можно ставить на повтор без «щелчка». Реакция на звук и внешнее управление — надстройка, которая не ломает замкнутость.

Главная ошибка в этой задаче — попытка делать это в Cycles. Cycles — движок офлайн-рендера. Реальное время — это EEVEE (в Blender 4.2+ он называется EEVEE Next) и вьюпорт. Всё, что ниже, проектируется под то, чтобы сцена **рендерилась во вьюпорте при 30+ fps**, а цикл потом рендерится офлайн с тем же результатом.

> [!NOTE]
> Идентификатор движка менялся: `BLENDER_EEVEE_NEXT` в Blender 4.2+ и `BLENDER_EEVEE` в более ранних. Никде не хардкодится — код читает текущий движок и подставляет подходящее имя. Точный список: `[i.identifier for i in scene.render.bl_rna.properties["engine"].enum_items]`.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с EEVEE | 4.2+ или старше, имя движка проверяем | рендер в реальном времени |
| Видеомикшер / внешний пульт | опционально | управление извне |
| UDP-сокет на localhost | стандартная библиотека Python | приём команд |
| Огибающая звука | CSV из внешнего анализа | реакция на звук |

## 🛠️ НАСТРОЙКА

### Этап 1. Кадровая сетка цикла

```bash
RU: "Цикл 8 секунд, 24 fps = 192 кадра. frame_start=1, frame_end=192 так, чтобы
     кадр 192 был дублем кадра 1 и при повторе не было скачка"
EN: "8 s loop, 24 fps = 192 frames. frame_start=1, frame_end=192 so frame 192
     duplicates frame 1 and looping has no jump"
```

```python
import bpy
sc = bpy.context.scene
FPS = 24
LOOP_FRAMES = 8 * FPS                  # 192

sc.render.fps = FPS
sc.frame_start = 1
# последний кадр цикла = дубль первого, поэтому range на единицу короче
sc.frame_end = LOOP_FRAMES
sc.use_preview_range = False
sc.sync_mode = 'FRAME_DROP'           # лучше рваный темп, чем замедление

def engine_evee():
    names = [i.identifier for i in sc.render.bl_rna.properties["engine"].enum_items]
    for cand in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        if cand in names:
            return cand
    raise RuntimeError(f"EEVEE не найден среди движков: {names}")

sc.render.engine = engine_evee()
print("движок:", sc.render.engine, "кадров в цикле:", sc.frame_end)
```

### Этап 2. Замкнутость: всё, что двигается, обязано вернуться

Любой параметр, который не возвращается в исходное состояние, ломает цикл. Ротация — целое число оборотов, шум — периодический, фаза — по кадрам цикла.

```python
import bpy, math
LOOP_FRAMES = 192

def loop_rotation(obj, axis, turns):
    """Целое число оборотов за цикл = бесшовность гарантирована."""
    obj.rotation_mode = 'XYZ'
    for f in range(sc.frame_start, sc.frame_end + 2):     # +1: последний дубль первого
        phase = 2 * math.pi * turns * ((f - sc.frame_start) / LOOP_FRAMES)
        obj.rotation_euler[axis] = phase
        obj.keyframe_insert("rotation_euler", index=axis, frame=f)

def loop_pingpong(obj, prop, index, lo, hi):
    """Треугольная волна: значение не скачет в конце цикла."""
    half = LOOP_FRAMES / 2
    for f in range(sc.frame_start, sc.frame_end + 2):
        t = ((f - sc.frame_start) % LOOP_FRAMES) / half
        val = lo + (hi - lo) * (1 - abs(1 - t))
        getattr(obj, prop)[index] = val
        obj.keyframe_insert(prop, index=index, frame=f)

pivot = bpy.data.objects.new("Loop_Pivot", None)
sc.collection.objects.link(pivot)
loop_rotation(pivot, 2, 1)              # ровно один оборот за 8 секунд
```

Шум, который должен быть периодическим, считается через синус от номера кадра, а не через случайность.

```python
import bpy, math
driven = bpy.data.objects["Reactive_Core"]
for f in range(sc.frame_start, sc.frame_end + 2):
    t = 2 * math.pi * (f - sc.frame_start) / LOOP_FRAMES     # 0..2pi за цикл
    s = 1.0 + 0.15 * math.sin(3 * t)                        # период ровно один цикл
    driven.scale = (s, s, s)
    driven.keyframe_insert("scale", frame=f)
```

### Этап 3. Проверка цикла — автоматическая, не на глаз

```python
import bpy, os
sc = bpy.context.scene
out = bpy.path.abspath("//vj/check")
os.makedirs(out, exist_ok=True)
sc.render.resolution_x, sc.render.resolution_y = 640, 360
sc.render.image_settings.file_format = 'PNG'

def render_frame(n):
    sc.frame_set(n)
    sc.render.filepath = os.path.join(out, f"chk_{n:04d}.png")
    bpy.ops.render.render(write_still=True)

render_frame(sc.frame_start)
render_frame(sc.frame_end)

a = bpy.data.images.load(os.path.join(out, f"chk_{sc.frame_start:04d}.png"))
b = bpy.data.images.load(os.path.join(out, f"chk_{sc.frame_end:04d}.png"))
pa, pb = list(a.pixels), list(b.pixels)
diff = sum(abs(x - y) for x, y in zip(pa, pb)) / max(len(pa), 1)
print(f"средняя разница пикселей между 1 и {sc.frame_end}: {diff:.6f}")
print("цикл замкнут" if diff < 0.002 else "цикл РАЗОМКНУТ — найди незамкнутую анимацию")
```

### Этап 4. Реакция на звук

Как и в [WF 27](wf_27_sound_sync_edit.md): огибающую считают вне Blender, здесь она приходит с частотой кадра цикла.

```python
import bpy, os

csv_path = r"C:\BLENDER ai\out\env_loop.csv"
amps = []
if os.path.exists(csv_path):
    with open(csv_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                amps.append(float(line.replace(",", ".")))
print("окон огибающей:", len(amps))

ob = bpy.data.objects["Audio_Reactive_Array"]
for f in range(sc.frame_start, sc.frame_end + 2):
    i = int((f - sc.frame_start) * len(amps) / LOOP_FRAMES) if amps else 0
    amp = amps[min(i, len(amps) - 1)] if amps else 0.3
    ob.scale = (1.0, 1.0, 0.4 + amp * 4.0)
    ob.keyframe_insert("scale", frame=f)
```

### Этап 5. Внешнее управление (мост к пульту/TouchDesigner)

Обмен идёт через UDP локально. Никаких внешних пакетов не нужно — стандартный `socket`.

```python
import bpy, socket, threading, json

def make_receiver(port=8765):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))          # только localhost: наружу не выставляем
    sock.settimeout(0.05)                    # не блокируем UI

    def loop():
        while True:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                msg = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            for target, val in msg.items():
                ob = bpy.data.objects.get(target)
                if ob is None:
                    continue
                setattr(ob, "rotation_euler",
                        tuple(val) if isinstance(val, list) else ob.rotation_euler)
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return sock

sock = make_receiver(8765)
print("слушаю 127.0.0.1:8765")
```

Формат пакета: JSON вида `{"Loop_Pivot": [0.0, 0.0, 1.5708]}`. Отправить вручную:

```python
import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(json.dumps({"Loop_Pivot": [0, 0, 0.785]}).encode("utf-8"), ("127.0.0.1", 8765))
```

> [!NOTE]
> Приём в отдельном потоке и запись в `rotation_euler` из него — не идеальная схема: Blender не любит изменение данных из чужого потока. Рабочий компромисс — поток только складывает команды в очередь, а очередь разбирается из таймера на `bpy.app.timers` в главном потоке. Если начнутся артефакты, переходи на этот вариант.

### Этап 6. Воспроизведение в реальном времени и финальный рендер

```python
import bpy, math
sc = bpy.context.scene
ob = bpy.data.objects["Reactive_Core"]
rng = bpy.data.objects["Audio_Reactive_Array"]

# быстрый превью-рендер вьюпорта во весь экран
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_perspective = 'CAMERA'
        area.spaces.active.shading.type = 'RENDERED'

if not bpy.app.background:
    bpy.ops.screen.animation_play()

# офлайн-рендер того же самого: EEVEE -> PNG-последовательность -> сборка в видео
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.filepath = r"//vj/loop_"
bpy.ops.render.render(animation=True)
```

Сборка в видео делается внешним ffmpeg, потому что тайминг цикла должен совпасть с монтажным:

```bash
ffmpeg -y -framerate 24 -i "vj/loop_0001.png" -c:v libx264 -crf 16 -pix_fmt yuv420p "vj/loop.mp4"
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `LOOP_FRAMES` | `fps × секунды` | длина цикла; 192 кадра — универсально монтируется |
| `frame_end` | равен `LOOP_FRAMES`, не на единицу меньше | последний кадр намеренно дубль первого |
| `sync_mode` | `'FRAME_DROP'` | лучше пропуск кадра, чем замедление |
| `shading.type` | `'RENDERED'` | превью с реальным освещением; `'MATERIAL'` быстрее, но обманывает |
| разница пикселей 1↔N | < 0.002 | порог, при котором цикл считается замкнутым |
| оборотов за цикл | целое число | дробное число = щелчок на стыке |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Щелчок при повторе цикла | какой-то параметр не вернулся в начальное значение | прогнать проверку из этапа 3 и найти незамкнутую анимацию |
| `ValueError` на `engine` | хардкод имени EEVEE | резолвер `engine_evee()` выше |
| Вьюпорт 8 fps, сцена «тяжёлая» | слишком много объектов/материалов для EEVEE | инстансы вместо копий, один материал, отключить тени у мелких объектов |
| Звук реагирует с задержкой | огибающая грубее кадра | считать огибающую с частотой не ниже частоты кадров |
| Пропы при проигрывании | `sync_mode` не настроен | `FRAME_DROP`, уменьшить нагрузку |
| Порты UDP не принимают | сокет слушает только localhost | это осознанное ограничение; наружу не выставлять без необходимости |
| FFmpeg не собрал видео | кадры начинаются с 0001, а не с 0000 | сверить нумерацию и `-framerate` под фактический префикс |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с 192-кадровым замкнутым циклом, PNG-последовательность `//vj/loop_####.png`, готовый `loop.mp4` и скрипт-приёмник команд на 127.0.0.1:8765.

Характеристики — **оценка по порядко величины, а не измеренный результат**: сцена на 5–20 тыс. полигонов с одним-двумя материалами в EEVEE держит 30–60 fps на средней дискретной видеокарте. Рендер 192 кадров 1920×1080 в EEVEE — единицы секунд на кадр на старых картах, доли секунды на новых, то есть от десятков секунд до нескольких минут. Кадр PNG 1920×1080 — 2–6 МБ, весь цикл — сотни мегабайт, поэтому для видео сразу рендерят в H.264.

**Это оценка.** Всё зависит от количества объектов, материала и GPU; измеряй у себя, и для превью ориентируйся на fps во вьюпорте, а не на время офлайн-рендера.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md), [WF 14: CLOTH FASHION SHOW](wf_14_cloth_fashion_show.md), [WF 17: STOP-MOTION FELT LOOK](wf_17_stop_motion_felt.md), [WF 23: VIRTUAL PRODUCTION LED](wf_23_virtual_production_led.md), [WF 24: PHOTOGRAMMETRY CLEANUP](wf_24_photogrammetry_cleanup.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](../cases/case_04_character_rig.md), [CASE 06: ANIMATION LOOP](../cases/case_06_animation_loop.md), [P14: CAMERA & COMPOSITION](../prompts/14_camera_composition.md)
- **Теги:** #animation, #workflow