---
id: setup_15_comfyui_sdxl
lang: ru
category: setups
type: setup
status: full
tags: [blender, setup, stable-diffusion]
---
# SETUP 15: BLENDER + COMFYUI SDXL

**ID:** SETUP-15 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 45-75 min
**RU/EN Bilingual**

> Когда применять: когда текстуры нужны быстро, вариативно и в большом количестве — blackbase, concept art, заполнение невидимых поверхностей. Для финальных PBR-карт нужен отдельный пайплайн.

## 🎯 ЦЕЛЬ
Поднять ComfyUI локально как HTTP-сервис генерации картинок, научить его принимать карту глубины из Blender как управляющий сигнал (ControlNet) и забирать результат обратно в Blender как текстуру. На выходе — скрипт, который по кнопке кладёт сгенерированное изображение в Image Editor поверх материала.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| ComfyUI | текущий релиз | локальный генератор с HTTP API и очереди |
| Python | 3.10–3.12 (проверь `README` ComfyUI для своей версии) | рантайм ComfyUI |
| SDXL base | `sd_xl_base_1.0.safetensors` (~7 ГБ) | базовая модель, нативное разрешение 1024×1024 |
| SDXL refiner | `sd_xl_refiner_1.0.safetensors` (опционально) | доработка деталей на втором проходе |
| ControlNet для SDXL | например Canny/Depth варианты под SDXL | привязка генерации к геометрии из Blender |
| GPU | 8 ГБ VRAM минимум для SDXL в fp16; 12 ГБ комфортнее | инференс |
| Blender | 4.2 LTS+ | источник depth/normal map и приём результата |

> [!NOTE]
> Точный список моделей, который лежит в `models/controlnet/`, и их имена файлов меняются с выходом новых моделей. Смотри вкладку Files на huggingface.co у конкретной модели и папку `ComfyUI/models/controlnet/` — ComfyUI показывает в списке имя файла, а не «человеческое» имя модели.

## 🛠️ НАСТРОЙКА

### 1. Установить ComfyUI

```bash
# Вариант на Windows без возни с окружением: portable-сборка с NVIDIA
# качай с github.com/comfyanonymous/ComfyUI/releases, запускай run_nvidia_gpu.bat

# Вариант из исходников (работает везде, где есть CUDA/ROCm/Metal)
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
python -m pip install -r requirements.txt

# Старт сервера. Порт по умолчанию 8188, адрес по умолчанию только localhost
python main.py

# Полезные флаги запуска:
#   --listen 0.0.0.0     открыть наружу (осторожно: это открытый генератор)
#   --port 8189          другой порт, если 8188 занят
#   --disable-auto-launch  не открывать браузер при старте
```

Проверь, что сервис жив, до того как писать скрипты:

```bash
# Список нод, которые сервер реально знает — источник правды о версии
curl -s http://127.0.0.1:8188/object_info | python -c "import json,sys; print(len(json.load(sys.stdin)), 'node types')"

# Статистика: видно, какой backend (GPU/CPU) подхватился
curl -s http://127.0.0.1:8188/system_stats
```

### 2. Положить модели

```
ComfyUI/models/
├── checkpoints/   sd_xl_base_1.0.safetensors
├── controlnet/    controlnet-canny-sdxl-1.0.safetensors
│                  controlnet-depth-sdxl-1.0.safetensors
└── vae/           (необязательно, только если вынес VAE из модели)
```

Собственный VAE для SDXL имеет смысл выносить: fp16-вариант VAE от SDXL даёт чёрный NaN-шум, и в этом виновата не картинка, а переполнение в полуточном формате.

### 3. Отдать из Blender карту глубины

ControlNet в ComfyUI ждёт **обычное 8/16-битное изображение**, а не EXR. Поэтому глубину нормализуем в 0..1 и сохраняем в PNG.

```python
# blender_depth_pass.py — Blender: Text Editor → Run Script
import bpy, os

scene = bpy.context.scene
out_dir = os.path.join(os.path.expanduser("~"), "comfy_in")
os.makedirs(out_dir, exist_ok=True)

# 1) Включаем слои рендера, которые нам нужны
vl = scene.view_layers[0]
vl.use_pass_z = True          # Depth
vl.use_pass_normal = True     # Normal (пригодится для canny/lineart-пайплайнов)

# 2) Рендерим один кадр во внетактовый EXR — там глубина линейная и 32-битная
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
scene.render.filepath = os.path.join(out_dir, "depth.exr")
bpy.ops.render.render(write_still=True)

# 3) Нормализуем EXR в PNG через Compositor: Color Ramp растягивает
#    линейную глубину на 0..1, Save Image Operator пишет 8-битный PNG
scene.use_nodes = True
tree = scene.node_tree
tree.nodes.clear()

rl = tree.nodes.new("CompositorNodeRLayers")
ramp = tree.nodes.new("CompositorNodeColorRamp")
# Подставь свои near/far: near должен быть чуть ближе ближайшей геометрии,
# far — чуть дальше самой дальней, иначе весь кадр уедет в один конец градиента
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[1].position = 1.0
ramp.color_ramp.interpolation = 'EASE'

save = tree.nodes.new("CompositorNodeOutputFile")
save.base_path = out_dir
save.format.file_format = 'PNG'
save.format.color_mode = 'BW'
save.file_slots[0].path = "depth_norm"

tree.links.new(rl.outputs["Depth"], ramp.inputs["Fac"])
tree.links.new(ramp.outputs["Color"], save.inputs[0])

bpy.ops.render.render(write_still=True)
print("Готово:", out_dir)   # файл будет depth_norm0001.png — с номером кадра
```

### 4. Отправить workflow в ComfyUI

Граф — это обычный JSON: ключ словаря = id ноды, `inputs` ссылаются на выходы других нод как `[id_ноды, индекс_выхода]`.

```json
{
  "3": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
  },
  "5": {
    "class_type": "EmptyLatentImage",
    "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
  },
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "weathered concrete wall, seamless, top-down lighting", "clip": ["3", 1]}
  },
  "7": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "blurry, watermark, text, frame", "clip": ["3", 1]}
  },
  "4": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 0, "steps": 30, "cfg": 7.0,
      "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
      "model": ["3", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]
    }
  },
  "8": {
    "class_type": "VAEDecode",
    "inputs": {"samples": ["4", 0], "vae": ["3", 2]}
  },
  "9": {
    "class_type": "SaveImage",
    "inputs": {"filename_prefix": "blender/base", "images": ["8", 0]}
  }
}
```

> [!NOTE]
> `class_type` — это идентификаторы нод из конкретной сборки ComfyUI. В ванильном это `CheckpointLoaderSimple` / `EmptyLatentImage` / `KSampler` / `VAEDecode` / `SaveImage`, но любой установленный custom-пакет может их переопределить. Сверяйся с выводом `/object_info` — это единственный источник правды о том, что сервер действительно умеет.

### 5. Полный цикл из Blender: submit → poll → забрать в материал

```python
# blender_comfy_bridge.py — запускать из Blender
import bpy, json, os, time, uuid, urllib.request, urllib.parse
from pathlib import Path

COMFY = "http://127.0.0.1:8188"
IN_DIR = Path.home() / "comfy_in"
OUT_DIR = Path.home() / "comfy_out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def _get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def _post_json(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def upload_image(path: Path) -> str:
    """Отдаём карту глубины серверу. Возвращает имя файла, как его видит ComfyUI."""
    boundary = uuid.uuid4().hex
    name = path.name
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n".encode(),
        b"Content-Type: image/png\r\n\r\n", path.read_bytes(), b"\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}--\r\n".encode(),
    ])
    req = urllib.request.Request(
        COMFY + "/upload/image", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        info = json.loads(r.read())
    return info["name"] + ((" [input]" + info.get("subfolder", "")) if info.get("subfolder") else "")

def submit(graph: dict) -> str:
    r = _post_json(COMFY + "/prompt", {"prompt": graph, "client_id": "blender"})
    if r.get("node_errors"):
        raise RuntimeError("ComfyUI отклонил граф: " + json.dumps(r["node_errors"])[:400])
    return r["prompt_id"]

def wait_done(prompt_id: str, timeout=600):
    """Поллинг /history вместо WebSocket — проще, а для батча разницы нет."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        hist = json.loads(_get(f"{COMFY}/history/{prompt_id}"))
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(1.0)
    raise TimeoutError("ComfyUI не закончил за отведённое время")

def fetch_output(node_out: dict):
    """Скачиваем первый файл из outputs SaveImage-ноды и кладём его на диск."""
    img = node_out["images"][0]
    q = urllib.parse.urlencode({
        "filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img["type"],
    })
    dest = OUT_DIR / img["filename"]
    dest.write_bytes(_get(f"{COMFY}/view?{q}"))
    return dest

def load_into_material(png_path: Path, mat_name="M_AI_BaseColor"):
    """Заменяем текстуру в существующем материале — не создаём новый."""
    mat = bpy.data.materials.get(mat_name)
    if not mat or not mat.use_nodes:
        print("Материал не найден или без нод:", mat_name); return
    tree = mat.node_tree
    tex = next((n for n in tree.nodes if n.type == 'TEX_IMAGE'), None)
    if not tex:
        print("В материале нет Image Texture"); return
    if tex.image is None:
        tex.image = bpy.data.images.load(str(png_path), check_existing=False)
    else:
        tex.image.filepath = str(png_path)
        tex.image.reload()
    # Генерированная картинка в sRGB, и её нужно интерпретировать как sRGB
    tex.image.colorspace_settings.name = 'sRGB'
    print("Текстура обновлена:", png_path.name)
```

### 6. ControlNet: привязка к геометрии

Для того чтобы картинка легла на конкретную форму, в граф добавляются три ноды: загрузчик ControlNet, применение (условное и безусловное) и правильная подмена входа. У SDXL ControlNet применяется **дважды** — к positive и к negative, иначе результат «плывёт».

```text
ControlNetLoader → ControlNetApplyAdvanced (positive) ─┐
ControlNetLoader → ControlNetApplyAdvanced (negative) ─┤→ KSampler
LoadImage(depth_norm0001.png) → image ───────────────┘
```

Практические значения: `strength` 0.4–0.8 для depth (выше — начинает копировать артефакты карты), `start_percent` 0.0–0.4, `end_percent` 0.8–1.0. Для canny `strength` обычно 0.3–0.6.

> [!NOTE]
> Имена входов у `ControlNetApplyAdvanced` (`image`, `strength`, `start_percent`, `end_percent`) и способ подмены входов у `KSampler` в разных сборках различаются: в некоторых виртуальных нодах `ControlNet` подключается отдельной нодой `SetLatentNoiseMask`/`LatentComposite`, в других — через `control_net_name` в `KSampler`. Смотри JSON, который ComfyUI сохраняет при сохранении графа в UI: это точная схема твоей сборки.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Очередь: посмотреть, что в работе и что ждёт
curl -s http://127.0.0.1:8188/queue

# Прервать текущую генерацию (из Blender — когда пользователь нажал Esc)
curl -s -X POST http://127.0.0.1:8188/interrupt

# Сбросить очередь целиком
curl -s -X POST http://127.0.0.1:8188/queue -H "Content-Type: application/json" -d '{"clear": true}'
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| `width` / `height` | 1024×1024 для SDXL | ниже 768 качество падает, выше — растёт время и VRAM |
| `steps` | 25–35 | меньше 20 — каша, больше 50 — почти без выигрыша |
| `cfg` | 5.5–8 | выше 10 текст превращается в мешанину |
| `sampler_name` / `scheduler` | `dpmpp_2m` + `karras` | рабочая связка по умолчанию, `euler`/`dpmpp_sdekarras` для другой стилистики |
| `denoise` | 1.0 для txt2img, 0.3–0.6 для img2img | ниже 0.3 результат слишком близок к исходнику |
| `seed` | любое целое, `-1` = случайный | **фиксируй seed**: без него невозможно воспроизвести удачный результат |
| ControlNet `strength` | 0.4–0.8 (depth) | понижай, если на картинке видны артефакты геометрии |
| `filename_prefix` | `blender/base` | по нему ты находишь результат в `ComfyUI/output/` |

### Про «PBR из ComfyUI»

Стоит сказать прямо: **ComfyUI не выдаёт корректный PBR-набор**. `basecolor` получается осмысленно, `roughness`/`metallic`/`normal` — нет. Варианты, которые реально работают:

- **basecolor + вручную**: генерация цвета, roughness/height из процедурных нод Blender или из базовых карт с запеканием в Blender;
- **кастом-пайплайн**: готовые наборы нод (normal/roughness из картинки через depth→normal) — они сторонние, имена нод надо брать из `/object_info`;
- **gbexr/texture-экспорт из Substance Designer**, а не из ComfyUI — см. SETUP 19.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| `Connection refused` при `urlopen` | ComfyUI не запущен или слушает не на 8188 | Проверь `python main.py` в консоли и флаг `--port` |
| `HTTP 400` на `/prompt` | JSON графа невалиден или нет такого файла модели | Тело ответа содержит `node_errors` — печатай его целиком, а не первые 400 символов |
| Картинка с чёрными квадратами / NaN-шумом | fp16 VAE, вынесенный из SDXL без фикса | Поставь fp32 VAE или убери отдельный VAE совсем |
| ControlNet ничего не делает | Подключён только к positive, либо `strength` слишком низкий | Примени к обоим conditioner'ам, подними `strength` до 0.6 для проверки |
| Результат «не налезает» на форму | Карта глубины пустая или инвертированная | Проверь, что `Depth` идёт в Color Ramp с монотонным ростом, а не инверсией |
| Текстура в Blender не обновилась | Image datablock остался с кэшем | `img.reload()`, плюс `img.filepath = str(path)` перед reload |
| Текстура в Blender темнее, чем на картинке | colorspace стоит `Non-Color` | Для basecolor должно быть `sRGB`; `Non-Color` — только для normal/roughness/height |
| OOM на 8 ГБ VRAM | SDXL целиком + ControlNet | Понизь batch_size до 1, отключи превью в UI ComfyUI, используй fp16-веса |
| Очередь растёт, интерфейс встал | Клиент шлёт запросы без ограничения rate | Перед `submit` проверяй `/queue`; в UI у ComfyUI есть лимит на размер очереди |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md)
- **Теги:** #blender, #setup, #stable-diffusion