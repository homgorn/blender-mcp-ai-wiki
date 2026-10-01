---
id: setup_17_krita_ai_diffusion
lang: ru
category: setups
type: setup
status: full
tags: [2d-ai, blender, setup]
---
# SETUP 17: BLENDER + KRITA AI DIFFUSION

**ID:** SETUP-17 | **Type:** 2D/3D Paint | **Difficulty:** ⭐ | **Time:** 30-45 min
**RU/EN Bilingual**

> Когда применять: когда AI-генерация нужна не «весь материал», а конкретный кусок — замазать дыру в текстуре, дорисовать латунную накладку, развернуть бесшовный участок. Blender тут нужен только как владелец текстуры, а рисовать удобнее в 2D.

## 🎯 ЦЕЛЬ
Собрать связку из трёх ролей: **Krita** — маски, подчистка и ручная дорисовка; **ComfyUI** — генерация (его поднимает плагин AI Diffusion); **Blender** — владелец конечной текстуры и место, где всё собирается в материал. На выходе — кнопка «почини вот здесь», после которой текстура в Blender обновилась сама.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Krita | 5.x (плагин рассчитан на современные сборки) | 2D-редактор с масками и слоями |
| Плагин **Krita AI Diffusion** | текущий релиз | генерация прямо в Krita |
| ComfyUI | см. SETUP 15 | бэкенд генерации, поднимается плагином или ставится вручную |
| Модель и (для inpaint/outpaint) inpainted-модель | SDXL или SD 1.5 inpainting | качество inpaint у обычной модели заметно ниже |
| Blender | 4.2 LTS+ | приём результата и финальный материал |
| Общая папка-обменник на диске | любая, лучше ASCII-путь | канал между приложениями |

> [!NOTE]
> Требования плагина к версии Krita и Python менялись с каждым релизом, а часть сборок приходит без работающего Python-плагинов. Проверяй совместимость по странице/репозиторию плагина перед установкой: несовместимость проявляется так, что панель AI Diffusion просто не появляется в списке докеров.

## 🛠️ НАСТРОЙКА

### 1. Поставить ComfyUI

Плагин умеет ставить ComfyUI сам (кнопка в настройках), но надёжнее сделать это руками — тогда же и версию выбираешь ты:

```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
python -m pip install -r requirements.txt
python main.py --port 8188
```

### 2. Установить плагин в Krita

Проще всего через встроенную установку: Krita умеет ставить плагины из репозитория, и это безопаснее ручного копирования.

```text
Krita → Settings → Manage Python Plugins → Install from URL…
  → вставь ссылку на репозиторий плагина (адрес бери из его README)

Если URL-установщика недоступен — вручную:
  1. Скачай zip плагина (страница Releases)
  2. Распакуй так, чтобы получилось: <Krita>/plug-ins/krita_ai_diffusion/
     (в Windows это %APPDATA%\krita\5.x\scripts\plug-ins\)
  3. Перезапусти Krita
  4. Window → Dockers → найди «AI Diffusion»
```

> [!NOTE]
> Точный путь к папке `plug-ins` зависит от того, portable это Krita или установленная в систему, и от номера версии в пути. Не выдумывай его — посмотри `Settings → Krita → System Resources`, там указан реальный каталог ресурсов, и клади плагин рядом с существующими папками плагинов.

### 3. Связать плагин с ComfyUI и скачать модели

> [!NOTE]
> Плагин не просто рисует картинку — он поднимает собственный небольшой сервер и уже через него говорит с ComfyUI. Отсюда два практических следствия: порт плагина (по умолчанию `127.0.0.1:8008`) не должен совпадать с 8188, который занят ComfyUI; и после перезапуска ComfyUI плагин переподключают кнопкой в настройках либо перезапуском Krita. Точный порт смотри в `AI Diffusion → Settings`, а не по памяти.

```text
AI Diffusion → Settings:
  • Backend            → ComfyUI
  • ComfyUI server URL → http://127.0.0.1:8188
  • (кнопка Test/Start server) — проверка связи; без неё плагин молча не работает
  • Resources → выбрать base-модель и, если нужен inpaint, inpainted-модель
    и скачать их прямо из плагина
```

Модель — это `.safetensors`, который кладётся в `ComfyUI/models/checkpoints/`. Плагин качает их сам, но знает не все модели: если твоей нет в списке, скачай вручную и перезапусти ComfyUI.

### 4. Раскладка работы: кто что делает

```text
Blender                      Krita                        ComfyUI
────────                     ─────                        ───────
Export Texture ▸ base.png ──▶ открыть как слой
                              нарисовать маску (белое = чинить)
Export ▸ mask.png ──────────▶ Save Layer/Selection as PNG
                              AI Diffusion → Inpaint, prompt
                              результат появляется слоем
                              Save Layer ▸ out.png
       ◀── Reload Texture ─── out.png на диске ◀───────── SaveImage
```

Маска из Krita и промпт — единственное, что реально нужно от 2D-редактора. Всё остальное (цвет, стиль, seamless) разумнее отдавать генератору.

### 5. Blender: текстура входит в материал

```python
# blender_krita_bridge.py — импорт текстуры и стандартный PBR-сетап
import bpy, os

TEXTURE_DIR = os.path.join(os.path.expanduser("~"), "krita_bridge")   # ASCII-путь
os.makedirs(TEXTURE_DIR, exist_ok=True)

MAPS = {                       # Blender images → файлы, которые приходят из Krita
    "basecolor":  "base.png",
    "roughness":  "rough.png",
    "normal":     "normal.png",     # normal НЕ должен быть flipped по каналам
    "height":     "height.png",
}

def setup_material(name="M_Krita"):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    nodes, links = tree.nodes, tree.links

    for key, filename in MAPS.items():
        path = os.path.join(TEXTURE_DIR, filename)
        if not os.path.exists(path):
            continue
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(path, check_existing=False)
        tex.image.colorspace_settings.name = {
            # цвет читается как sRGB, а карты — как линейные данные
            "basecolor": "sRGB",
            "roughness": "Non-Color", "normal": "Non-Color", "height": "Non-Color",
        }[key]
        links.new(tex.outputs["Color"], bsdf.inputs[key])
    return mat
```

### 6. Автоперезагрузка: Blender следит за папкой

```python
# Сторож за файлами. Работает и без внешних библиотек.
import bpy, os

TEXTURE_DIR = os.path.join(os.path.expanduser("~"), "krita_bridge")
_seen = {}                       # путь → mtime, чтобы неReload'ить без изменений

def _poll():
    """Вызывается из bpy.app.timers. Возвращает None = снять таймер,
    любое число = интервал до следующего вызова."""
    for filename in os.listdir(TEXTURE_DIR) if os.path.isdir(TEXTURE_DIR) else []:
        if not filename.lower().endswith((".png", ".exr")):
            continue
        path = os.path.join(TEXTURE_DIR, filename)
        mtime = os.path.getmtime(path)
        if _seen.get(path) == mtime:
            continue
        _seen[path] = mtime
        for img in bpy.data.images:
            if img.filepath_raw and os.path.abspath(img.filepath_raw) == os.path.abspath(path):
                img.reload()           # главный шаг: перечитать файл с диска
                img.update()
                print("reloaded:", filename)
    return 1.0                        # проверка раз в секунду

def start_watching():
    if _poll not in bpy.app.timers:
        bpy.app.timers.register(_poll, first_interval=1.0)

def stop_watching():
    if _poll in bpy.app.timers:
        bpy.app.timers.unregister(_poll)
```

> [!NOTE]
> `bpy.app.timers.register` в Blender 4.x имеет переименованные параметры (`first_interval` вместо `sleep` в некоторых сборках). Если увидишь `TypeError`, посмотри подпись функции в своей версии: `help(bpy.app.timers.register)`.

### 7. Отправка в Krita: маска наружу

Со стороны Krita, если нужно автоматизировать (Python Console: `Settings → Dockers → Python Console`):

```python
# ВЫПОЛНЯЕТСЯ ВНУТРИ Krita. Модуль krita доступен только в её процессе —
# из Blender `import krita` не сработает, это принципиальное ограничение.
from krita import Krita

k = Krita.instance()
doc = k.activeDocument()
layer = doc.activeLayer()

print(doc.width(), doc.height(), layer.name())

# Положить активный слой отдельным PNG-файлом — так его и забирает Blender
out_url = doc.filePath()          # пока ничего не сохранено — будет пусто
print("doc:", out_url)
```

Из Blender наружу отдаётся тот же файл через `save_render` / экспорт, а забрать результат — через `img.reload()` (шаг 6). Обмен файлами здесь не костыль, а единственный надёжный канал: прямой IPC между Krita и Blender не существует.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверить, что ComfyUI жив и что плагин увидит те же ноды
curl -s http://127.0.0.1:8188/system_stats

# Забрать последний результат из папки ComfyUI вручную (обменная папка)
copy /Y "C:\ComfyUI\output\blender\inpaint_00001_.png" "C:\Users\me\krita_bridge\base.png"
```

```python
# Что вообще лежит в обменной папке и какого размера — полезно при отладке
import os
d = os.path.join(os.path.expanduser("~"), "krita_bridge")
for f in sorted(os.listdir(d)):
    p = os.path.join(d, f)
    print(f"{f:28s} {os.path.getsize(p)/1024:8.1f} KB  {int(os.path.getmtime(p))}")
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| Обменная папка | ASCII-путь без пробелов и кириллицы | если плагин не видит файл — сначала подозревай путь |
| `Denoise` (inpaint) | 0.4–0.7 | выше 0.9 замазанное место перестаёт вписываться в окружение |
| `Sampling steps` | 20–30 | 15 хватает для черновика |
| `Guidance scale` | 5–8 | ниже 4 — «мягкая» картинка, выше 10 — пережаренная |
| Размер маски | совпадать с исходником | Krita экспортирует маску в своём размере — приводи к размеру текстуры |
| Mask blur/ feather | 8–32 px | маленький feather даёт видимый шов на границе патча |
| Формат масок | 8-bit grayscale PNG | RGB-маски Krita плагин интерпретирует по первому каналу, это источник «инверта» |
| Тип операции | Inpaint / Outpaint / Fill / Control | Fill требует заливки всей маски, иначе плагин предложит Inpaint |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| В списке докеров нет AI Diffusion | Плагин не установлен или несовместим с версией Krita | Проверь `Manage Python Plugins`, переустанови, сверь версии |
| `Connection refused` в панели плагина | ComfyUI не запущен или на другом порту | Запусти `python main.py`, проверь URL и порт в настройках плагина |
| Генерация идёт минуты, картинки нет | ComfyUI считает, но `SaveImage` не отдаёт файл | Смотри консоль ComfyUI; проверь права на запись в `ComfyUI/output/` |
| Маска инвертирована — чинится не то место | Маска в RGB, плагин берёт один канал; либо инверт в самом плагине | Экспортируй маску как 8-bit grayscale (в Krita: Image → Desaturate → Save) |
| Текстура в Blender не обновляется | `filepath_raw` указывает не на тот файл | Сверь абсолютные пути; перезагрузи вручную `img.reload()` |
| Таймер не вызывается | `bpy.app.timers` живёт только пока активен цикл событий | Не запускай из headless-рендера: для CI используй setup_04 (headless) |
| Результат 512×512, а нужно 2048 | Плагин не смог найти в Krita нити для генерации | Генерируй на 512 и апскейль, либо иди через ComfyUI напрямую (SETUP 15) |
| Кириллица в имени файла → плагин его не видит | Кодировка пути | Держи обменную папку и файлы в ASCII |
| Нормаль выглядит «вдавленной» | Перепутаны green-канал или flip по Y | Нормали всегда экспортируй без flip; сверяйся с тестовой сферой |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md), [SETUP 12: BLENDER + UNREAL ENGINE 5 LIVE LINK](setup_12_unreal_livelink.md)
- **Теги:** #blender, #setup