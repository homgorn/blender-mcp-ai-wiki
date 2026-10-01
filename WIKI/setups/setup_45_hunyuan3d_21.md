---
id: setup_45_hunyuan3d_21
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, blender, llm, mcp, pipeline, setup]
---
# SETUP 45: HUNYUAN3D 2.1 LOCAL

**ID:** SETUP-45 | **Type:** Local 3D Gen | **Difficulty:** ⭐⭐⭐ | **Time:** 2-3 h

> Когда применять: когда нужен 3D-генератор на своей машине — без отправки промптов и референсов в чужое облако. Hunyuan3D крутится локально, но весит и требует GPU, поэтому вся статья — про то, сколько места и VRAM нужно и как поднять сервис так, чтобы MCP его увидел.

## 🎯 ЦЕЛЬ

Hunyuan3D — open-source генератор от Tencent с двухстадийным пайплайном: сначала форма (shapе), затем текстуры. В отличие от [Tripo](setup_42_tripo_ai_api.md) и [Meshy](setup_43_meshy_api_v4.md), здесь платить не надо: платит твоё железо. Настраиваем локальный запуск, поднимаем свой HTTP-эндпоинт и прописываем его аддон через `BLENDERMCP_HUNYUAN3D_API_URL`, чтобы MCP-инструменты опрашивали задание и импортировали результат в сцену.

> [!NOTE]
> Наличие отдельной переменной `BLENDERMCP_HUNYUAN3D_API_URL` — сам по себе факт, что аддон умеет ходить в **поднятый тобой** сервис, а не только в облако Tencent. Это и делает слово «local» в названии честным. Точное имя скрипта запуска и его флаги смотри в README репозитория: они меняются между коммитами.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Ориентир | Зачем |
|---|---|---|
| GPU | 12 ГБ VRAM минимум, 16+ комфортно | обе стадии; текстуры — тяжёлая |
| CUDA | версия под твою карту | без неё будет CPU-режим и часы ожидания |
| Диск | 20-30 ГБ | веса моделей + кэш |
| RAM | 32 ГБ | выгрузка текстур |
| Python | 3.10-3.11, окружение venv | изолированные зависимости |
| Blender | 4.x LTS | импорт результата |

> [!NOTE]
> Требования к VRAM менялись от стадии к стадии. Ориентир «12 ГБ» — расхожая цифра из обсуждений, а не спецификация: точные значения для конкретного веса бери из model card в репозитории. На 8 ГБ текстурная стадия либо не запустится, либо уйдёт в очень долгий расчёт.

## 🛠️ НАСТРОЙКА

### 1. Клонируем и ставим зависимости

```bash
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git
cd Hunyuan3D-2

# Отдельное окружение: зависимости тяжёлые и конфликтуют с системными
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Проверяем, что видно GPU

```python
# venv_activate; python
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    free, total = torch.cuda.mem_get_info()
    print(f"VRAM: {free/2**30:.1f} / {total/2**30:.1f} GB free")
```

> [!NOTE]
> Имя проверочного скрипта и флаг выбора стадии (форма / текстура / обе) в репозитории менялись. Открой README и список файлов в корне перед запуском, а не полагайся на имя из этой статьи.

### 3. Поднимаем локальный сервис

```bash
# В репозитории Hunyuan3D-2 есть скрипт запуска с веб-интерфейсом.
# Точное имя файла и флаги — в README; типичный вид такой:
python app.py --server_port 7860
# Если нужен чистый HTTP-эндпоинт без UI — ищи в репозитории скрипт,
# который отдаёт JSON по HTTP, и подними именно его.
```

```python
# Проверяем, что сервис слушает наш порт
import socket
s = socket.socket(); s.settimeout(0.5)
print("7860:", "open" if s.connect_ex(("127.0.0.1", 7860)) == 0 else "closed")
s.close()
```

### 4. Прописываем аддон

```python
import os
for var in ("BLENDERMCP_HUNYUAN3D_API_URL",
            "BLENDERMCP_HUNYUAN3D_SECRET_ID",
            "BLENDERMCP_HUNYUAN3D_SECRET_KEY"):
    print(var, "=", os.environ.get(var, "<не задан>"))
```

Аддон должен ходить в `127.0.0.1:<порт твоего сервиса>`, а не в облако. Если оставишь адрес облака по умолчанию, отправишь референс наружу.

### 5. Ставим задание

```python
# В текущем MCP-каталоге есть poll_hunyuan_job_status и import_generated_asset_hunyuan,
# но нет тула «создать задание» — задание создаётся в локальном сервисе
# (его веб-интерфейсом или HTTP-вызовом), а MCP его только опрашивает и импортирует.
#
# import_generated_asset_hunyuan(name="Cabin", zip_file_url="http://127.0.0.1:7860/.../out.zip")
#   ^ обрати внимание: аргумент называется zip_file_url, то есть результат
#     ожидается архивом .zip, а не «голым» .glb.
```

> [!NOTE]
> Это не домыслы: имя параметра `zip_file_url` в сигнатуре инструмента прямо указывает, что ожидается zip-архив. Согласуй с этим свой локальный сервис — он должен отдавать ссылку на zip, внутри которого лежат меш и PBR-карты.

### 6. Опрашиваем и импортируем

```python
# poll_hunyuan_job_status(job_id="...")
# import_generated_asset_hunyuan(name="Cabin", zip_file_url="...")
```

### 7. Импорт GLB вручную, если сервис отдаёт файл

```python
import bpy
from pathlib import Path

def import_glb(path: Path, coll="AI3D") -> bpy.types.Collection:
    c = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    for o in set(bpy.data.objects) - before:
        for old in list(o.users_collection):
            old.objects.unlink(o)
        c.objects.link(o)
    return c

# print(len(import_glb(Path(r"C:/assets/ai3d/hunyuan/cabin.glb")).objects))
```

### 8. Доводим результат

```python
import bpy

obj = next(iter(bpy.data.collections["AI3D"].objects))
print("полигонов:", len(obj.data.polygons), "| UV-слоёв:", len(obj.data.uv_layers))

dec = obj.modifiers.new("Decimate", "DECIMATE")
dec.ratio = 0.5
sub = obj.modifiers.new("Subdiv", "SUBSURF")
sub.levels, sub.render_levels = 1, 2

smooth_ops = [o for o in dir(bpy.ops.object) if "smooth" in o]
print("smoothing ops:", smooth_ops)
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Веса качаются отдельно от кода — проверь, сколько занято
du -sh checkpoints 2>/dev/null || dir /s checkpoints

# Держим локальный сервис живым между заданиями
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `BLENDERMCP_HUNYUAN3D_API_URL` | `http://127.0.0.1:<порт>` | обязательно локальный адрес, если не хочешь отправлять наружу |
| `SecretId` / `SecretKey` | из окружения | для локального сервиса часто не нужны, но аддон может требовать |
| текстурная стадия | `2K` | `4K` кратно дольше по времени и VRAM |
| `dec.ratio` | `0.3–0.6` | для игрового пропа |
| `Subdiv render_levels` | `2` | выше — резче силуэт, дольше рендер |
| порт сервиса | `7860` | любой свободный, аддон должен знать тот же |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `CUDA out of memory` | не хватает VRAM | закрой другие GPU-процессы, снизь разрешение текстур, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` |
| Идёт на CPU, всё очень долго | `torch.cuda.is_available()` = False | поставь torch с CUDA-сборкой под свою карту |
| `get_hunyuan3d_status` = disabled | аддон не видит `API_URL` | проверь переменную в окружении сервера, перезапусти Blender |
| `poll` не находит job | сервис перезапустился и потерял состояние | состояние держи на диске, не в памяти процесса |
| Импорт падает на zip | ожидался «голый» glb, пришёл архив | распакуй zip и импортируй содержимое |
| Текстуры не подхватились | карты лежат в zip, а не встроены | после распаковки подключи Image Texture вручную |
| Меш в форме «капли» | не отработала стадия формы | прогоняй обе стадии, а не только текстуры |
| Веса скачались не полностью | оборвалась загрузка | сверь размер файлов с ожидаемым из model card |
| Исходники в не-ASCII пути | часть загрузчиков не переваривает | держи checkpoints на латинском пути |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md)
- **Теги:** #ai-3d, #blender, #llm, #mcp, #pipeline, #setup
