---
id: setup_16_automatic1111_api
lang: ru
category: setups
type: setup
status: full
tags: [api, blender, setup, stable-diffusion]
---
# SETUP 16: BLENDER + AUTOMATIC1111 API

**ID:** SETUP-16 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 30-45 min
**RU/EN Bilingual**

> Когда применять: когда в проекте уже есть A1111, нужна одна картинка здесь и там, а node-график ComfyUI избыточен. API A1111 — самый простой способ дёрнуть генерацию из Blender-скрипта.

## 🎯 ЦЕЛЬ
Поднять A1111 в режиме HTTP API и написать на Python клиента, который: делает txt2img по параметрам, гонит img2img по картинке из Blender, шлёт inpaint по маске и кладёт результат в Image Texture ноду. На выходе — один модуль с тремя функциями, который можно звать из любого хендлера Blender.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Stable Diffusion web UI (A1111) | 1.7.x / 1.10.x — ветка v1 | генератор; API-эндпоинты живут именно в v1, в v2 (Forge/развилки) пути меняются |
| Python-пакеты из `requirements.txt` A1111 | из репозитория | torch и зависимости |
| Модель-чекпойнт | SD 1.5 ~2 ГБ или SDXL ~7 ГБ | сам генератор; SDXL требует больше VRAM |
| Blender | 4.2 LTS+ | источник картинки/маски и приём результата |
| HTTP-клиент | стандартная библиотека (`urllib`) | внешние библиотеки не нужны, достаточно стандартного модуля |

> [!NOTE]
> Если ты на **v2/SD.Next или Forge**, не переноси флаги из этой статьи один в один: путь эндпоинтов, ключи запросов и часть флагов запуска там другие. Проверь свой `launch.py --help` и, если есть, `/sdapi/v1/options` — самый дешёвый способ убедиться, что API поднялся.

## 🛠️ НАСТРОЙКА

### 1. Запустить A1111 с API

```bash
# Вариант "в один файл" (portable-сборка): допиши флаги в webui-user.bat
#   .\webui-user.bat --api --port 7860
# Обычная установка:
python launch.py --api --port 7860

# Полезные флаги рядом с --api
#   --ckpt D:\models\sd15\v1-5-pruned.safetensors   свой чекпойнт без копирования в models/Stable-diffusion
#   --vae  D:\models\sd15\vae-ft-mse.safetensors     отдельный VAE
#   --xformers                                   меньше VRAM, быстрее (нужен xformers в окружении)
#   --api-auth user:pass                         базовая аутентификация для API
#   --ckpt-safe-dir ...                          путь к моделям с пробелами/кириллицей

# Проверка: сервер должен подняться на 127.0.0.1:7860
curl -s http://127.0.0.1:7860/sdapi/v1/sd-models
curl -s http://127.0.0.1:7860/sdapi/v1/samplers | python -c "import json,sys; print(json.load(sys.stdin)[:8])"
```

> [!NOTE]
> Наличие флага `--api-auth` и его точное написание проверь в своей сборке: `python launch.py --help`. Логика та же — A1111 начинает требовать Basic-аутентификацию для API, и клиент должен слать заголовок `Authorization`.

### 2. Минимальный клиент: транспорт

```python
# a1111_client.py — положи в Text Editor Blender или в свой пакет
import base64, json, urllib.request, urllib.error

BASE = "http://127.0.0.1:7860"
AUTH = None      # ("user", "pass") если запускал с --api-auth

def _url(path: str) -> str:
    return BASE + "/sdapi/v1/" + path.lstrip("/")

def api(path: str, payload: dict | None = None, method: str | None = None):
    """Единая точка входа. GET, если payload не передан, иначе POST с JSON."""
    headers = {"Content-Type": "application/json"}
    if AUTH:
        token = base64.b64encode(f"{AUTH[0]}:{AUTH[1]}".encode()).decode()
        headers["Authorization"] = "Basic " + token

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    m = method or ("POST" if data else "GET")
    req = urllib.request.Request(_url(path), data=data, headers=headers, method=m)
    with urllib.request.urlopen(req, timeout=300) as r:      # таймаут большой: генерация бывает долгой
        return json.loads(r.read())

def save_first(result: dict, path: str):
    """Ответ приходит как {"images": ["<base64 без заголовка>", ...]} — это PNG."""
    if not result.get("images"):
        raise RuntimeError("A1111 вернул пустой images: " + str(result)[:300])
    raw = base64.b64decode(result["images"][0])
    with open(path, "wb") as f:
        f.write(raw)
    return path
```

### 3. txt2img с параметрами, которые реально что-то значат

```python
def txt2img(prompt, negative="lowres, watermark, text", steps=28, cfg=7.0,
            width=768, height=768, seed=-1, sampler="DPM++ 2M Karras", ckpt=None):
    payload = {
        "prompt": prompt,
        "negative_prompt": negative,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_name": sampler,       # точное имя бери из /sdapi/v1/samplers
        "width": width,
        "height": height,
        "seed": seed,                  # -1 = случайный; фиксируй, если нужен повтор
        "batch_size": 1,
        "n_iter": 1,
        "tiling": True,                # seamless-тайлинг: чекбокс «Tiling» во вкладке txt2img
        "save_images": False,
        "send_images": True,
        "override_settings": {},       # сюда кладём смену модели/сэмплера
        "override_filter_rgba": True,
    }
    if ckpt:
        payload["override_settings"]["sd_model_checkpoint"] = ckpt
    return api("txt2img", payload)

# Пример: три варианта одной стены с разным зерном
for i in range(3):
    r = txt2img("weathered concrete wall, seamless, top-down", seed=1000 + i)
    save_first(r, rf"C:\tmp\wall_{i}.png")
    print(r["parameters"]["seed"], "→", r["info"].splitlines()[0])
```

### 4. img2img: картинка из Blender уходит в A1111

Данные в `img2img` передаются как base64-PNG, поэтому из Blender мы сначала пишем временный файл и читаем его байты — `bpy.types.Image.pixels` отдаёт float-массив, а не PNG.

```python
import bpy, tempfile, os, base64

def _image_to_png_b64(img: bpy.types.Image) -> str:
    tmp = os.path.join(tempfile.gettempdir(), "_a1111_src.png")
    # save_render применяет color management и пишет валидный PNG
    img.save_render(filepath=tmp)
    with open(tmp, "rb") as f:
        return base64.b64encode(f.read()).decode()

def img2img(img: bpy.types.Image, prompt, strength=0.55, steps=30, cfg=7.0, seed=-1):
    payload = {
        "init_images": [_image_to_png_b64(img)],   # список, не строка
        "prompt": prompt,
        "negative_prompt": "blurry",
        "denoising_strength": strength,             # главный параметр img2img
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_name": "DPM++ 2M Karras",
        "seed": seed,
        "width": img.size[0],
        "height": img.size[1],
        "tiling": True,
        "send_images": True,
    }
    return api("img2img", payload)

# Пример: взять Color из материала и «перерисовать» его в basecolor
mat = bpy.data.materials.get("M_Wall")
tex = next(n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE')
res = img2img(tex.image, "seamless concrete, flat lighting, no shadows", strength=0.45)
save_first(res, os.path.join(bpy.app.tempdir, "wall_ai.png"))
```

### 5. inpaint по маске из Blender

Маска — это картинка того же размера, где белым чинить, чёрным оставить. `inpainting_fill_in`: 0 — сохранять фон, 1 — рисовать фон, 2 — не трогать.

```python
def inpaint(src: bpy.types.Image, mask: bpy.types.Image, prompt,
            mask_blur=4, full_res=True, padding=32, fill_in=1):
    payload = {
        "init_images": [_image_to_png_b64(src)],
        "mask": _image_to_png_b64(mask),
        "prompt": prompt,
        "negative_prompt": "",
        "denoising_strength": 0.75,
        "inpainting_mask_invert": False,      # False = белое в маске чинится
        "mask_blur": mask_blur,
        "inpainting_full_res": full_res,
        "inpainting_full_res_padding": padding,
        "inpainting_fill_in": fill_in,
        "steps": 30, "cfg_scale": 7.5,
        "sampler_name": "DPM++ 2M Karras",
        "send_images": True,
    }
    return api("inpaint", payload)

# Маску в Blender рисуют кистью по Render Result / Image Editor и сохраняют PNG;
# из Blender она уходит тем же save_render-путём, что и исходник.
```

### 6. Обратный ход: достать параметры из чужой картинки

Если картинка уже отрисована и вшитые в неё параметры важны (для батча, для отката, для документации), `png-info` разбирает метаданные обратно в словарь.

```python
def read_png_info(png_path: str) -> dict:
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    info = api("png-info", {"image": b64})
    # {"info": "job: ...\nStep: 30, Sampler: ..., CFG scale: 7, Seed: 123, ...",
    #  "json": {...}, "items": {...}}
    return info.get("json") or info.get("items") or {}

meta = read_png_info(r"C:\tmp\wall_0.png")
print("seed:", meta.get("Seed"), "| model:", (meta.get("Model") or "")[:40])
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Список моделей, доступных серверу (нужно для override_settings)
curl -s http://127.0.0.1:7860/sdapi/v1/sd-models

# Точное имя сэмплера — строкой нужно то, что вернул сервер, а не то что в UI
curl -s http://127.0.0.1:7860/sdapi/v1/samplers | python -c "import json,sys;[print(s) for s in json.load(sys.stdin)]"

# Список встроенных VAE
curl -s http://127.0.0.1:7860/sdapi/v1/sd-vae

# Текущие опции (можно поменять через POST /options, например переключить UI-тему)
curl -s http://127.0.0.1:7860/sdapi/v1/options | python -c "import json,sys;d=json.load(sys.stdin);print(d['sd_model_checkpoint'], d['show_progress_in_title'])"
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| `denoising_strength` | 0.3–0.5 для img2img, 0.7–0.9 для inpaint | выше 0.9 картинка уходит от исходника полностью |
| `cfg_scale` | 4–9 для SD 1.5, 5–8 для SDXL | выше 12 — артефакты и «пережаренный» результат |
| `steps` | 25–35 | 20 достаточно для черновика, 40+ для финальной |
| `sampler_name` | значение из `/sdapi/v1/samplers` | никогда не пиши руками — строки менялись между версиями |
| `seed` | `-1` = случайно | фиксируй для воспроизводимого батча |
| `mask_blur` | 2–8 | слишком большое размытие съедает детали на границе патча |
| `inpainting_full_res_padding` | 16–64 | поднимай, если по краю маски видно ореол от перехода |
| `tiling` | `True` | для бесшовных текстур; для одиночной картинки выключай |
| `override_settings` | `{"sd_model_checkpoint": ...}` | удобнее, чем переключать чекпойнт в UI перед каждой генерацией |

### Очередь и отмена

A1111 обрабатывает запросы последовательно, поэтому клиент должен быть терпеливым и уметь отмену:

```python
import urllib.error

def interrupt():
    """Остановить текущую генерацию — например, по Escape в Blender.
    Внимание: этот обработчик живёт в корне сервера, а не под /sdapi/v1,
    поэтому здесь BASE собирается вручную."""
    with urllib.request.urlopen(BASE + "/interrupt", timeout=5) as r:
        return r.status

# Обработка занятого/ошибочного сервера
try:
    r = txt2img("test")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "replace")
    if e.code == 400:
        print("Сервер отверг запрос — скорее всего неверное имя сэмплера или модели:\n", body[:400])
    else:
        print(e.code, body[:400])
```

> [!NOTE]
> Путь отмены генерации (`/interrupt`) — единственный, который лежит не под `/sdapi/v1`, и он менялся между версиями A1111. Если получаешь 404, посмотри вкладку Network в браузере, нажав Stop в UI: там будет точный путь, который зовёт сама страница.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| `404` на любой `/sdapi/v1/...` | Запущено без `--api` | Дописать `--api` и перезапустить |
| `HTTP 401` | Включён `--api-auth`, клиент не шлёт `Authorization` | Добавь Basic-заголовок в `api()` |
| `HTTP 400` и текст про `Invalid sampler_name` | Сэмплер назван как в UI, а не как в API | Возьми точную строку из `/sdapi/v1/samplers` |
| `Connection refused` | Сервер на другом порту или не запущен | Проверь флаг `--port`; по умолчанию 7860 |
| Ответ приходит через несколько минут, клиент падает | Таймаут `urlopen` меньше времени генерации | Подними таймаут (в коде 300 с) |
| Картинка в Blender темнее/светлее оригинала | `save_render` применил view transform повторно | Читай PNG-файл и грузи через `bpy.data.images.load()`, а не конвертируй float-пиксели |
| Маска инвертирована: чинится ровно то, что не нужно | `inpainting_mask_invert=True` | Поставь `False` и убери альфу из маски |
| Текстура обновилась, но в рендере старая | Image datablock не перечитал файл | `img.filepath = path; img.reload()`, затем `img.update()` |
| В логе A1111 «Bad request» без деталей | Ошибка валится в stderr GUI, а не в HTTP-ответ | Смотри консоль, где запущен `launch.py` |
| Батч из 20 картинок занимает полчаса и кажется «зависшим» | Очередь обрабатывается последовательно | Отправляй по одной и делай `interrupt()` для отмены остатка |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 15: BLENDER + COMFYUI SDXL](setup_15_comfyui_sdxl.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #api, #blender, #setup, #stable-diffusion