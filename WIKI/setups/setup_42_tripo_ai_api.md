---
id: setup_42_tripo_ai_api
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, api, setup]
---
# SETUP 42: TRIPO AI API

**ID:** SETUP-42 | **Type:** Text/Image-to-3D | **Difficulty:** ⭐⭐ | **Time:** 30-40 min

> Когда применять: когда нужен облачный text/image-to-3D по API с оплатой по кредитам, а не локальная модель — Tripo даёт готовый меш с PBR-картами, и задача состоит в том, чтобы корректно отправить задание, дождаться готовности и забрать результат в Blender.

## 🎯 ЦЕЛЬ

Настраиваем облачный конвейер Tripo: ключ → постановка задачи (по тексту и/или по картинке) → `job id` → опрос статуса → URL результата → импорт в Blender. Ключевое, что надо понимать до начала: **это не локальный инструмент**. Нужен аккаунт Tripo, ключ API и кредиты — бесплатный лимит при регистрации есть, дальше платно, поэтому статья честно разделяет то, что работает локально (Blender, MCP-тулы импорта), и то, что требует денег (сама генерация).

> [!NOTE]
> Точные имена полей ответа Tripo (имя ключа, которое возвращает `job id`, точный путь эндпоинта создания задачи, имена форматов экспорта) я намеренно не привожу: они менялись между версиями API. Ниже приведён **контракт**, а не конкретные имена. Сверяй `BASE`, путь и ключи с текущей документацией Tripo перед первым запуском.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Аккаунт Tripo | — | кредиты и ключ |
| Ключ API | — | авторизация запросов |
| Python + `requests` | 3.10+ | HTTP-обвязка |
| Blender | 4.x LTS | импорт результата |
| blender-mcp с Tripo-инструментами | текущий | опрос статуса и импорт |
| GLB / FBX / OBJ | — | форматы, которые Blender читает |

## 🛠️ НАСТРОЙКА

### 1. Проверяем, включён ли Tripo в этой сборке

```python
# В MCP-сессии вызови get_tripo_status() — вернёт, включён ли провайдер и задан ли ключ.
# Здесь — то же самое из Python: читаем переменные окружения, которые аддон видит.
import os
for var in ("BLENDERMCP_TRIPO_API_KEY", "TRIPO_API_KEY"):
    print(var, "set" if os.environ.get(var) else "missing")
```

> [!NOTE]
> Имя переменной окружения для Tripo уточни в настройках аддона в своей сборке. В текущем MCP-каталоге Tripo-инструменты есть (`get_tripo_status`, `poll_tripo_job_status`, `import_generated_asset_tripo`), но переменная, которую аддон читает, в документации проекта не зафиксирована — не выдумывай её, посмотри в UI аддона.

### 2. Каркас клиента: submit → poll → download

```python
import os, time, json, requests

BASE = "https://platform.tripo3d.ai"      # хост и префикс пути — сверь с документацией
KEY  = os.environ["TRIPO_API_KEY"]
HDRS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def submit(payload: dict) -> str:
    """Отправили промпт -> получили id задания. Имя ключа с id берём из ответа, не угадываем."""
    r = requests.post(f"{BASE}/v2/openapi/task", headers=HDRS, json=payload, timeout=60)
    r.raise_for_status()
    body = r.json()
    print("ответ на submit:", json.dumps(body)[:400])   # сначала посмотри, потом правь
    return body["data"]["task_id"]        # <-- путь по ответу: проверь фактический

def poll(task_id: str, timeout_s: int = 600) -> str:
    """Опрашиваем статус, пока задание не дошло до терминального состояния."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = requests.get(f"{BASE}/v2/openapi/task/{task_id}", headers=HDRS, timeout=30)
        r.raise_for_status()
        data = r.json()["data"]
        status = data.get("status")
        print(status, data.get("progress"))
        if status in ("success", "failed", "expired"):
            return data
        time.sleep(5)
    raise TimeoutError(task_id)
```

### 3. Ставим задачу из картинки + уточняющий текст

```python
payload = {
    "type": "image_to_model",
    "file": {"type": "jpg", "file_type": "file_url", "url": "https://.../ref.jpg"},
    "prompt": "worn leather satchel, stitched seams, soft edges",
    "face_limit": 1000,
    "texture": True,
}
# task_id = submit(payload)
# data = poll(task_id)
# print(json.dumps(data, indent=2)[:800])   # здесь придёт ссылка на модель
```

> [!NOTE]
> Имена полей `type`, `file`, `prompt`, а также значения `image_to_model` / `text_to_model` и флаг текстурирования — сверяй с документацией: их переименовывали. Смысл запроса неизменен — картинка плюс текстовое уточнение, на выходе ссылка на файл модели.

### 4. Скачиваем результат

```python
from pathlib import Path
import requests

def download_result(model_url: str, out_dir=Path(r"C:/assets/ai3d/tripo")) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    r = requests.get(model_url, stream=True, timeout=300)
    r.raise_for_status()
    dest = out_dir / Path(model_url.split("?")[0]).name
    with open(dest, "wb") as f:
        for chunk in r.iter_content(1 << 16):
            f.write(chunk)
    return dest

# dest = download_result(data["model"]["pbr_model"]["url"])
# print(dest, dest.stat().st_size // 1024, "KB")
```

### 5. Импорт в Blender

```python
import bpy
from pathlib import Path

def import_ai3d(path: Path, coll_name="AI3D") -> bpy.types.Collection:
    coll = bpy.data.collections.get(coll_name) or bpy.data.collections.new(coll_name)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))          # .glb / .gltf
    new = sorted(set(bpy.data.objects) - before, key=lambda o: o.name)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll

# coll = import_ai3d(dest)
# print(len(coll.objects), "объектов")
```

> [!NOTE]
> Ранг-файлы (скелет и анимация) приходят отдельными файлами в своём формате и в glTF не всегда переезжают. Если нужен риг — импортируй скелет отдельно, формат подбирай по документации; не рассчитывай, что GLB принесёт позу.

### 6. То же самое через MCP-тулы

```python
# get_tripo_status()                      -> включён ли провайдер
# poll_tripo_job_status(request_id="...") -> статус и прогресс
# import_generated_asset_tripo(request_id="...", name="TripoSatchel")
```

Эти три вызова — контракт: id задания ты получаешь сам (шаг 2), MCP умеет опрашивать и импортировать. Создания задачи среди них нет.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверка баланса/кредитов — запрос без изменений состояния
curl -s -H "Authorization: Bearer $TRIPO_API_KEY" "https://platform.tripo3d.ai/v2/openapi/user/balance"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `BASE` | хост Tripo API | сверь с документацией, менялся |
| таймаут опроса | `600` с | генерация сложной сцены дольше 5 мин |
| интервал опроса | `5` с | меньше — упрёшься в лимит запросов |
| текстура | `true` | `false` быстрее, но меш без PBR |
| формат выгрузки | GLB | для игр; OBJ/FBX — если нужна совместимость |
| лимит полигонов | `face_limit` | меньше = быстрее и дешевле по кредитам |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| 401/403 от API | ключ не задан или не передан | проверь заголовок `Authorization: Bearer <ключ>` |
| `KeyError: 'task_id'` | путь к id в ответе другой | напечатай `json.dumps(body)`, поправь разбор |
| Задание вечно `running` | счётчик кредитов кончился | проверь баланс; часть платформ «съедает» задание молча |
| Импорт пустой | файл скачался как HTML-заглушка | проверь размер и первые байты до `gltf`-импорта |
| Меш в неверном масштабе | облако не знает про метры | `normalize()` как в [SETUP 38](setup_38_fab_epic.md) |
| Нет нормалей/руфнесса | заказывал без текстуры | перезакажи с текстурой либо запеки в Blender |
| MCP: Tripo disabled | провайдер не включён в аддоне | включи в настройках аддона и перезапусти Blender |
| Разные `request_id` форматы | MCP ждёт свой, API отдаёт свой | перескажи id точно, без обрезки |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 43: MESHY API V4](setup_43_meshy_api_v4.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md), [SETUP 44: RODIN / HYPER3D GEN](setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md)
- **По темам:** [SETUP 47: ZERO123 / INSTANTMESH](setup_47_zero123_instantmesh.md), [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #ai-3d, #api, #setup
