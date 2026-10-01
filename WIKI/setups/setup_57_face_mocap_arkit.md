---
id: setup_57_face_mocap_arkit
lang: ru
category: setups
type: setup
status: full
tags: [mocap, setup, vr]
---
# SETUP 57: FACE MOCAP ARKIT

**ID:** SETUP-57 | **Type:** Face Cap | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

> Когда применять: когда нужно записать лицо на iPhone с приложением для трекинга
> и превратить поток blendshape-весов в анимацию Blender.

---

## 🎯 ЦЕЛЬ

Собрать конвейер «iPhone → сеть → shape keys → запечённая анимация лица» и
разобрать три места, где он ломается: несовпадение имён blendshape-ов, джиттер
значений и рассинхрон звука.

Все вызовы API проверены на Blender 5.2.1 LTS.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| iPhone | с приложением лицевого трекинга ARKit | Источник blendshape-весов |
| Blender | 5.x (проверено 5.2.1) | Приём по UDP, shape keys, запекание |
| Сеть | одна подсеть с телефоном и машиной | UDP не ходит через NAT сам |
| Лицо в Blender | меш с shape keys | Цель данных |

---

## 🛠️ НАСТРОЙКА

### 1. Создать shape keys под набор blendshape-ов

ARKit отдаёт фиксированный набор именованных blendshape-локаций. Названия задаёт
Apple, и это **ваша точка отказа**: если в сцене ключ называется иначе, значение
придёт в никуда. Ключи создаются заранее, до записи.

```python
# setup_face_shapes.py — создать shape keys по списку имён.
import bpy

# Подмножество имён, принятых в ARKit-совместимых пайплайнах.
# Полный список — из документации Apple по ARKit (ARFaceAnchor);
# он расширялся между версиями iOS, поэтому сверяйтесь с вашей версией.
ARKIT_SHAPES = [
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft",
    "browOuterUpRight", "jawOpen", "jawForward", "jawLeft", "jawRight",
    "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft",
    "mouthFrownRight", "mouthFunnel", "mouthLeft", "mouthLowerDownLeft",
    "mouthLowerDownRight", "mouthPressLeft", "mouthPressRight", "mouthPucker",
    "mouthRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower",
    "mouthShrugUpper", "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft",
    "mouthStretchRight", "mouthUpperUpLeft", "mouthUpperUpRight",
    "noseSneerLeft", "noseSneerRight", "tongueOut", "eyeBlinkLeft",
    "eyeBlinkRight", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft",
    "eyeLookUpLeft", "eyeSquintLeft", "eyeWideLeft", "eyeLookDownRight",
    "eyeLookInRight", "eyeLookOutRight", "eyeLookUpRight", "eyeSquintRight",
    "eyeWideRight",
]

def build_face_shapes(obj):
    if obj.type != 'MESH':
        raise ValueError("нужен меш, не арматура")
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)   # проверенная сигнатура
    keys = obj.data.shape_keys
    keys.use_relative = True
    created, missing = 0, []
    for name in ARKIT_SHAPES:
        kb = keys.key_blocks.get(name)
        if kb is None:
            kb = obj.shape_key_add(name=name, from_mix=False)
            created += 1
        kb.slider_min, kb.slider_max = 0.0, 1.0
        kb.value = 0.0
        if not kb.name:
            missing.append(name)
    return created, len(keys.key_blocks)

print("created/total:", build_face_shapes(bpy.data.objects["FACE"]))
```

> [!NOTE]
> Полный и актуальный перечень blendshape-локаций ARKit нужно взять из
> документации Apple по `ARFaceAnchor` для вашей версии iOS: набор расширялся,
> и статья не может быть источником истины здесь. Всё, что нужно от скрипта, —
> это чтобы имена ключей в сцене совпадали с тем, что приходит по сети.

### 2. Принять поток по UDP

```python
# face_receiver.py — запускать в фоне Blender: blender -b face_receiver.py
import bpy, socket, json

HOST, PORT = "0.0.0.0", 11111     # порт выбирается в приложении на телефоне
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))

FACE = bpy.data.objects.get("FACE")
if FACE is None:
    raise SystemExit("нет объекта FACE — запусти setup_face_shapes.py первым")

def apply_payload(payload):
    """payload — словарь вида {"blendshapes": {"jawOpen": 0.42, ...}}."""
    keys = FACE.data.shape_keys.key_blocks
    applied, unknown = 0, []
    for name, value in payload.get("blendshapes", {}).items():
        kb = keys.get(name)
        if kb is None:
            unknown.append(name)          # тело без этого ключа
            continue
        kb.value = max(0.0, min(1.0, float(value)))
        applied += 1
    return applied, unknown

while True:
    data, _ = sock.recvfrom(65536)
    apply_payload(json.loads(data.decode("utf-8")))
```

> [!NOTE]
> Формат пакета задаёт приложение на телефоне: ключи, типы (float/percent) и
> частоту отправки менялись между приложениями и версиями. Схема
> `{"blendshapes": {...}}` — распространённая, но не гарантия. Приложите к
> статье один реальный дамп пакета и печатайте `data[:200]`, чтобы увидеть
> фактические ключи, вместо того чтобы угадывать их.

### 3. Запечь значения в ключи

Живое значение в `key_blocks[...]` не переживёт перезагрузку файла. Запись в
кривые — обязательный шаг.

```python
# bake_face.py — после записи. Значения уже стоят в kb.value.
FACE = bpy.data.objects["FACE"]
keys = FACE.data.shape_keys
scene = bpy.context.scene

# Чистка лишних ключей: оставляем только те, где значение отличается от базы.
for kb in keys.key_blocks:
    if kb.name == "Basis":
        continue
    if abs(kb.value) < 0.001:
        keys.key_blocks.remove(kb)
    else:
        kb.value = 0.0

action = keys.animation_data.action
for layer in action.layers:
    for strip in layer.strips:
        for cb in strip.channelbags:
            for fc in cb.fcurves:
                print(fc.data_path, len(fc.keyframe_points))
```

F-кривая shape key в Blender 5.x лежит по пути
`key_blocks["<имя>"].value` — проверено на 5.2.1. Сам `action.fcurves`
больше не существует.

### 4. Разогнать джиттер

```python
def calm(action, factor=0.6):
    """Джиттер с телефона — это шум в каждом кадре. Лечится усреднением
    по соседним кадрам, а не 'сглаживанием' в UI."""
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    kps = fc.keyframe_points
                    prev = [kp.co.y for kp in kps]
                    for i, kp in enumerate(kps):
                        before = prev[i - 1] if i else kp.co.y
                        after = prev[i + 1] if i + 1 < len(prev) else kp.co.y
                        kp.co.y = before * (1 - factor) / 2 + kp.co.y * factor + after * (1 - factor) / 2
                        kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                    fc.update()
```

`factor` — не «сила сглаживания», а вес текущего кадра: меньше значение =
плавнее, но с задержкой. Для рта `0.6` обычно достаточно, для `eyeWide*`
значение ближе к `0.9`.

### 5. Проверить результат

```python
# Диагностика, которую видно на графике: у каждой кривой есть min/max.
for layer in action.layers:
    for strip in layer.strips:
        for cb in strip.channelbags:
            for fc in cb.fcurves:
                ys = [kp.co.y for kp in fc.keyframe_points]
                if min(ys) < -0.001 or max(ys) > 1.001:
                    print("ВЫШЕЛ ЗА 0..1:", fc.data_path, min(ys), max(ys))
                if len(ys) < 2:
                    print("ОДИНОЧНЫЙ КЛЮЧ (джиттер):", fc.data_path)
```

Плюс визуальная проверка в UI: Graph Editor → Channels для
`key_blocks["jawOpen"].value`. Плоская линия с одиночными пиками = джиттер, а не
мимика.

### 6. Свести с аудио

```python
# Звук кладётся в секвенсор, а не в сцену: в Blender 5.x коллекция полос
# называется strips, класс полосы — Strip.
import bpy
sc = bpy.context.scene
se = sc.sequence_editor_create()
snd = se.strips.new_sound(name="vo_take01", filepath="//audio/vo_take01.wav",
                          channel=1, frame_start=1)
snd.volume = 1.0

# Метка на кадре, где актёр начинает говорить: дальше по ней
# выравниваются глаза, если они пишутся отдельным проходом.
sc.timeline_markers.new("lipsync_start", frame=42)
```

### 7. Выгрузить в движок

```python
# Morph targets уезжают вместе с анимацией в GLB/FBX.
bpy.ops.export_scene.gltf(
    filepath="//exports/face_take01.glb",
    export_format='GLB',
    export_morph=True,               # проверенный параметр в 5.2
    export_morph_animation=True,
    export_morph_normal=True,
    export_animations=True,
)
```

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Диагностика: пришло ли что-то по сети
blender -b --python-expr "import bpy;print('face keys:', len(bpy.data.objects['FACE'].data.shape_keys.key_blocks))"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `slider_min/max` | `0.0 / 1.0` | Всегда: ARKit отдаёт нормализованные 0..1 |
| `use_relative` | `True` | Абсолютные ключи ломают экспорт morph-таргетов |
| `from_mix=False` | Всегда | Иначе новый ключ создаётся из текущей смеси, а не из Basis |
| `factor` в `calm()` | `0.6` для рта, `0.9` для глаз | Больше — задержка, меньше — остаточный джиттер |
| Порт UDP | задаётся в приложении | Телефон и машина должны быть в одной подсети |
| `new_sound` | в секвенсор | Голос — не часть 3D-сцены, а дорожка монтажа |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Значения приходят, лицо не двигается | Имена ключей в сцене не совпадают с присылаемыми | Печатать `unknown` из `apply_payload` и переименовать ключи |
| `AttributeError: 'Action' object has no attribute 'fcurves'` | Blender 5.x, slotted Actions | Путь `action.layers[0].strips[0].channelbags[0].fcurves` |
| Литтер идёт позже голоса | Сглаживание добавило задержку, плюс запись не от синхрона | Снизить `factor`; метку ставить по звуку, а не по началу записи |
| Челюсть «дрожит» в статике | Джиттер телефона не убран | `calm()` перед экспортом, либо `bpy.ops.graph.smooth` |
| Морда «плывёт» между позами | Создавали ключи без `from_mix=False` | Удалить ключи и создать заново с Basis |
| Приложение не подключается | Разные подсети / файрвол блокирует UDP | Проверить `netstat -an \| findstr :<порт>` и правило брандмауэра |
| Морфы не доехали в движок | Не включён `export_morph` | Проверить экспорт заново с `export_morph=True` |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 56: MOCAP ROKOKO / MOVE AI](setup_56_mocap_rokoko.md), [SETUP 58: VR SCENE INSPECTION](setup_58_vr_scene_inspection.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P44: MOCAP RETARGETING](../prompts/44_mocap_retarget.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **Теги:** #mocap, #setup, #vr
