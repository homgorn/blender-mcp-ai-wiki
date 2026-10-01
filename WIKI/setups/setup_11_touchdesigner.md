---
id: setup_11_touchdesigner
lang: ru
category: setups
type: setup
status: full
tags: [blender, realtime, setup]
---
# SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS

**ID:** SETUP-11 | **Type:** Realtime Visuals / Interactive | **Difficulty:** ⭐⭐⭐ | **Time:** 60-90 min

> Когда применять: когда рендер Blender должен попадать в TouchDesigner вживую — VJ-сет, инсталляция, генеративная графика с реакцией на OSC-параметры.

---

## 🎯 ЦЕЛЬ
Собрать рабочий канал Blender → TouchDesigner и обратный канал управления параметрами. Отдельно настроить два независимых потока: поток картинки (видео, а не данные) и поток чисел (параметры, триггеры, OSC). На выходе — TouchDesigner, в котором видно рендер Blender и который управляет им по сети.

## 🎯 АРХИТЕКТУРА

```
Blender (Content)          OSC/NDI/Spout          TouchDesigner (Realtime)
┌─────────────────┐       OSC/UDP/TCP          ┌─────────────────┐
│  Models/Anim    │ ───────────────────────▶  │  Real-time    │
│  Cameras/Lights │  NDI/Spout (Video)        │  Render/Comp  │
│  Geometry Nodes │  Shared Memory            │  - VJ         │
│  Shaders        │  OSC (Params)             │  - Interactive│
└─────────────────┘                           └─────────────────┘
```

## 🔧 ОСНОВНЫЕ ПРОТОКОЛЫ

| Протокол | Задержка | Пропускная способность | Use Case |
|----------|----------|------------------------|----------|
| **OSC** | ~1-5ms | Низкая | Параметры, триггеры, синк |
| **NDI** | ~1-2 кадра | Высокая (4K60) | Видео поток |
| **Spout** | ~0-1 кадр | Высокая (GPU-direct) | Windows GPU sharing |
| **Shared Memory** | ~0ms | Очень высокая | Текстуры/геометрия |
| **WebSocket** | ~5-10ms | Средняя | Web/Remote |
| **ZeroMQ** | ~1-2ms | Высокая | Высоконагруженные |

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Blender | 4.2 LTS или новее | источник картинки и геометрии |
| TouchDesigner | 2023.x и новее | приём видео и OSC, композитинг в реальном времени |
| Python-пакет `pyosc` | любая совместимая с Python Blender | отправка OSC из Blender без ручной сборки пакетов |
| NDI-аддон для Blender (structify) | — | видеопоток NDI из окна Blender |
| NDI Tools (NDI 6 Tools, Test Patterns) | 6.x | проверка, что поток вообще идёт, без TouchDesigner |
| Windows | 10/11 | Spout и NDI существуют в основном под Windows; на Linux альтернатива — Pipe/Spout через wine отсутствует |

> [!NOTE]
> Список аддонов NDI/Spout для Blender меняется: проекты сторонние, не все поддерживают свежие версии Blender. Проверь в `Edit → Preferences → Add-ons`, что аддон совместим с твоей версией, прежде чем планировать пайплайн. Если аддон не собирается — рабочий запасной вариант описан в шаге 4 (кадры на диск + `Video File In TOP`).

## 🛠️ НАСТРОЙКА

### 1. Выбрать, что именно «живёт» в Blender

Режим рендера — первое, что определяет всю дальнейшую настройку:

```python
# Blender: Python Console или Text Editor
import bpy

scene = bpy.context.scene

# EEVEE — единственный вариант, дающий realtime-сток для видеопотока
scene.render.engine = 'BLENDER_EEVEE_NEXT'   # в Blender 4.2+
# В более старых версиях идентификатор движка — 'BLENDER_EEVEE'

# Разрешение потока под целевой выход TouchDesigner
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 30

# Кадры рендера пишем в PNG — NDI/Spout-аддоны берут кадр из Render Result,
# а не с диска, поэтому формат влияет только на отладочные рендеры
scene.render.image_settings.file_format = 'PNG'
```

> [!NOTE]
> Идентификатор движка рендера (`BLENDER_EEVEE_NEXT` против `BLENDER_EEVEE`) менялся между версиями Blender. Не хардкодь его в скриптах: читай значение из `bpy.context.scene.render.engine` и меняй в UI. Точный список доступных движков — `bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items`.

### 2. Отправка параметров в TouchDesigner по OSC

Это самый надёжный канал: маленькие сообщения, никакой зависимости от версий видео-аддонов.

```bash
# Установка pyosc в Python, которым пользуется Blender, а не в системный Python.
# На Windows путь к нему примерно такой:
#   %APPDATA%\Blender Foundation\Blender\4.2\scripts\python\Lib\site-packages
# Точную версию подставь вместо 4.2 — она равна твоей версии Blender.
# Либо поставь пакет в отдельный venv и подключи его через
# Blender → Edit → Preferences → System → Python Paths.
pip install python-osc
```

```python
# blender_osc_bridge.py  — запускать из Blender: Text Editor → Run Script
import bpy
from pyosc.udp_client import SimpleUDPClient

TD_IP = "127.0.0.1"
TD_PORT = 3333           # порт, на котором в TouchDesigner слушает OSC In CHOP
client = SimpleUDPClient(TD_IP, TD_PORT)

def _send(scene):
    """Каждый кадр шлём в TouchDesigner то, что он не может узнать сам."""
    # Позиция камеры — TouchDesigner двигает ею свой 3D-слой
    cam = scene.camera
    if cam:
        client.send_message("/blender/cam/pos", list(cam.matrix_world.translation))
        client.send_message("/blender/cam/rot", list(cam.matrix_world.to_euler()))

    # Текущий кадр — для синхронизации с запуском аудио/видео в TD
    client.send_message("/blender/frame", scene.frame_current)

def start():
    if _send not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(_send)

def stop():
    if _send in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(_send)

if __name__ == "__main__":
    start()
```

На стороне TouchDesigner: `OSC In CHOP` (внутренний путь `tosi/in`) на порт 3333, на выходе — таблица каналов `/blender/cam/pos[0..2]` и `/blender/frame`. Дальше `Parameter CHOP` или `Math CHOP` превращают их в параметры.

### 3. Приём OSC обратно: ручки TouchDesigner управляют Blender

```python
# В Blender отдельным скриптом: поднимаем OSC-сервер и пишем значения в сцену
import bpy
import threading
from pyosc.osc_server import OSCServer

scene = bpy.context.scene

def handler(address, *args):
    """pyosc зовёт хендлер как handler('/address', value1, value2, ...)"""
    if address == "/td/mood" and args:
        # Один параметр на все материалы сцены — грубо, но наглядно
        scene.view_settings.exposure = float(args[0])

    if address == "/td/worley_scale" and args:
        node = bpy.data.node_groups.get("TDScratch")
        if node and "Scale" in node.inputs:
            node.inputs["Scale"].default_value = float(args[0])

server = OSCServer("127.0.0.1", 3334)   # отдельный порт, чтобы не конфликтовать с TX
server.bind(handler)

# OSCServer.listen() блокирующий — поднимаем в отдельном потоке,
# иначе скрипт запуска не вернёт управление в Blender
threading.Thread(target=server.listen, daemon=True).start()
print("OSC server on 3334")
```

### 4. Видеопоток: три пути, от простого к сложному

Путь A — самый предсказуемый: Blender пишет кадры, TouchDesigner читает их как видеофайл. Годится для проверки пайплайна и для выставочного проекта, где задержка в кадр не важна.

```python
# Blender: рендер последовательности в папку, которую смотрит TouchDesigner
import bpy, os
scene = bpy.context.scene
out_dir = os.path.join(os.path.expanduser("~"), "td_stream")
os.makedirs(out_dir, exist_ok=True)

scene.render.filepath = os.path.join(out_dir, "frame_")   # Blender допишет 0001.png
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(animation=True)   # блокирует UI на всё время секции
```

В TouchDesigner: `Video File In TOP` с этим путём → `Movie Out TOP` или в Composite. Это битмап по кадрам, не видеоданные, поэтому задержка и цвет ведут себя предсказуемо.

Путь B — NDI. Аддон для Blender отправляет кадр в NDI-имя, в TouchDesigner `Video In TOP` с Source = NDI читает его. Проверяется без Blender: сначала `NDI Test Patterns` в NDI Tools, потом `NDI Studio Monitor` — если картинка есть, Blender уже не при чём.

Путь C — Spout. Оба приложения на одной видеокарте, кадр не покидает GPU. Аддон Blender отдаёт кадр в Spout-шину, `Spout In TOP` в TouchDesigner его забирает. Проще всего для быстрых визуалов, но Spout — это Windows-only и требует, чтобы Blender не был в модальном диалоге.

Быстрый снимок одного кадра (для отладки, не для потока):

```python
# Снимок 3D-вьюпорта без рендера — быстро, но без EEVEE-освещения
bpy.ops.render.opengl(write_still=True, view_context=True)
bpy.data.images["Render Result"].save_render(filepath=r"C:\tmp\td_debug.png")
```

### 5. Проверка сквозного канала

```
1. Blender: запусти скрипт OSC-моста, поставь frame_current = 1
2. TouchDesigner: OSC In CHOP читает /blender/frame — значение должно расти
3. TouchDesigner: добавь в сеть Video In TOP (NDI/Spout) или Video File In TOP
4. Blender: в NDI Tools убедись, что поток называется так, как его ищет TD
5. Двигай камеру в Blender — картинка в TD обязана ехать без перезапуска
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Диагностика одним куском — вставить в Blender Python Console
import bpy, socket, sys

print("engine      :", bpy.context.scene.render.engine)
print("fps         :", bpy.context.scene.render.fps)
print("handlers    :", [f.__name__ for f in bpy.app.handlers.frame_change_post])
print("osc client  :", "pyosc ok" if "pyosc" in sys.modules else "pyosc NOT imported")

# Проверяем, что порт, который слушает TD, действительно живой на этой машине
probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
probe.settimeout(0.5)
try:
    probe.sendto(b"\x00", ("127.0.0.1", 3333))
    print("udp 3333    : отправлено без ошибки (это не доказывает, что слушатель есть)")
except OSError as e:
    print("udp 3333    :", e)
finally:
    probe.close()
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| `TD_PORT` (OSC out) | 3333 | если порт занят — смени и в `SimpleUDPClient`, и в OSC In CHOP |
| `TD_PORT` (OSC in) | 3334 | разведи входящий и исходящий OSC по разным портам, иначе сообщения зацикливаются |
| `frame_change_post` | список хендлеров | всегда проверяй перед `remove()`, иначе `ValueError` при повторном запуске |
| `scene.render.fps` | 30 | под audio-такт в TouchDesigner ставь целое число |
| `resolution_x/y` | 1920×1080 | NDI-аддоны часто умеют меньше — сверься с документацией аддона |
| Видеопротокол | NDI / Spout / файл | NDI для передачи по сети, Spout для одной GPU, файл для отладки |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| В TouchDesigner нет ни одного канала OSC In | Blender-скрипт не запущен, либо `pyosc` не импортировался в Python Blender | Проверь `sys.modules` в консоли Blender; пакет ставится в Python Blender, не в системный Python |
| Значения приходят, но не меняются | Хендлер навешен на `frame_change_pre`, а сцена не пересчитывается | Используй `frame_change_post`; для параметров сцены этого достаточно |
| `ValueError: <func> not found in list` при повторном запуске | Хендлер добавился дважды и `remove()` снимает несуществующий | Перед добавлением проверяй `if _send not in bpy.app.handlers.frame_change_post` |
| Видеопоток в TD чёрный, хотя OSC работает | Аддон отправляет кадр из окна, а окно Blender свёрнуто или перекрыто | Разверни окно с 3D-вьюпортом; в настройках аддона выбери источник — Viewport или Camera |
| Кадр в TD отстаёт на 2-3 кадра | Кодирование/декодирование видео по сети | Переходи на Spout (общая GPU) либо снижай `resolution_percentage` |
| После рендера `python` падает с `AttributeError` на `file_format` | Оператор рендера вернул `CANCELLED`, результата нет | Проверяй результат оператора перед `save_render` |
| OSC-сервер вешает интерфейс Blender | `OSCServer.listen()` блокирующий, вызван из Text Editor | Запускай в `threading.Thread(..., daemon=True)` |
| Цвета в TD и рендере Blender не совпадают | Разные view transform в двух приложениях | Приводи оба к одному view transform; TouchDesigner работает в линейном пространстве |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [EEVEE NEXT (BLENDER 4.2+)](../realtime/eevee_next.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #realtime, #setup