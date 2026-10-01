---
id: setup_43_meshy_api_v4
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, api, setup]
---
# SETUP 43: MESHY API V4

**ID:** SETUP-43 | **Type:** Text-to-3D/Texture | **Difficulty:** ⭐⭐ | **Time:** 40-50 min

> Когда применять: когда нужен облачный цикл целиком — text-to-3D, потом text-to-texture, ремеш, анимация — через HTTP API Meshy, потому что в текущей сборке blender-mcp интеграции с Meshy нет.

## 🎯 ЦЕЛЬ

Собираем полный цикл через публичный REST API Meshy: ключ → создание задачи любого типа → `task id` → опрос → ссылка на результат → импорт в Blender. Отдельные MCP-инструменты у Meshy в текущем MCP-каталоге **отсутствуют** — это факт, а не упущение: интеграции нет, всё делается HTTP-вызовами из `execute_blender_code` или из внешнего скрипта. Отдельно проговариваем деньги: Meshy даёт небольшой бесплатный лимит, дальше тарифы по кредитам, и цены пересматриваются.

> [!NOTE]
> Название «v4» в заголовке статьи — версия поколения API на момент написания. Имена полей ответа, точный базовый хост и префиксы путей менялись между мажорными версиями Meshy. Ниже везде приведён контракт, а конкретные ключи надо брать из текущей документации (docs.meshy.ai), а не из памяти.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Аккаунт Meshy | — | кредиты и ключ |
| Ключ API | — | Bearer-авторизация |
| Python + `requests` | 3.10+ | HTTP-обвязка |
| Blender | 4.x LTS | импорт и чистка |
| GLB / FBX | — | форматы выгрузки |

## 🛠️ НАСТРОЙКА

### 1. Ключ и базовый хост

```python
import os
KEY = os.environ["MESHY_API_KEY"]

# Хост и префикс версионирования берём из документации: менялись и хост, и путь
BASE = "https://api.meshy.ai"
HDRS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
print("key len:", len(KEY), "| base:", BASE)
```

> [!NOTE]
> `https://api.meshy.ai` — указан как база по умолчанию. Если отдаёт 404 или 401 сразу, открой docs.meshy.ai и возьми актуальный хост: у Meshy менялись и домен, и структура путей, и способ доставки результата (иногда результат приходит сразу в ответе, а не ссылкой).

### 2. Универсальный контракт: submit → poll → result

```python
import time, json, requests

def create_task(path: str, payload: dict) -> str:
    """Создали задачу -> получили id. Ключ с id смотри в ответе, не угадывай."""
    r = requests.post(f"{BASE}{path}", headers=HDRS, json=payload, timeout=60)
    r.raise_for_status()
    body = r.json()
    print("submit ->", json.dumps(body)[:400])
    return body["result"]        # <-- путь по ответу: проверь фактический

def poll(task_id: str, timeout_s: int = 600) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = requests.get(f"{BASE}/textures/{task_id}", headers=HDRS, timeout=30)
        # ^ конкретный путь опроса свой у каждого типа задачи — смотри документацию
        r.raise_for_status()
        data = r.json()["result"]
        print(data.get("status"), data.get("progress"))
        if data.get("status") in ("SUCCEEDED", "FAILED", "CANCELED", "EXPIRED"):
            return data
        time.sleep(6)
    raise TimeoutError(task_id)
```

> [!NOTE]
> Путь опроса зависит от типа задачи: text-to-3D, text-to-texture, remesh, rigging и анимация обслуживаются разными маршрутами. В примере это сделано параметром-шаблоном. Точные идентификаторы статусов (`SUCCEEDED` или `succeeded` — регистр тоже менялся) сверь в документации.

### 3. Text-to-3D

```python
payload = {
    "mode": "preview",                     # preview быстрее и дешевле, preview=false — финал
    "prompt": "stylized orc axe, notched blade, leather wrap on haft",
    "should_remesh": True,
    "should_texture": True,
    "should_rig": False,
}
# task_id = create_task("/textures", payload)   # путь для text-to-3D свой — сверь
# data = poll(task_id)
# print(data.get("model_urls"))
```

### 4. Text-to-texture по готовому мешу

```python
tex_payload = {
    "mode": "preview",
    "image_url": "https://.../your_axe.png",   # рендер меша с белым фоном
    "prompt": "worn pitted steel, bloodstained wooden haft, stylized game asset",
    "base_mesh_id": "секция моделей в ответе на text-to-3D",
}
# tex_id = create_task("/textures", tex_payload)
```

### 5. Ремеш и ретопология

```python
# Ремеш задаётся либо флагом в text-to-3D (should_remesh), либо отдельной задачей,
# которой скармливается URL модели из шага 3:
remesh_payload = {
    "model_id": "секция моделей из ответа на text-to-3D",
    "topology": "quad",          # tri | quad
    "target_face_count": 15000,
}
# remesh_id = create_task("/remesh", remesh_payload)   # путь сверь
```

### 6. Скачиваем и импортируем в Blender

```python
from pathlib import Path
import bpy, requests

def fetch(url: str, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
    return out

def import_model(path: Path, coll="AI3D") -> bpy.types.Collection:
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

# glb_url = [u for u in data["model_urls"] if u.endswith(".glb")][0]
# path = fetch(glb_url, Path(r"C:/assets/ai3d/meshy/orc_axe.glb"))
# print(len(import_model(path).objects), "объектов")
```

### 7. Приводим меш в порядок после импорта

```python
import bpy

obj = bpy.data.objects.get("orc_axe") or next(iter(bpy.data.collections["AI3D"].objects))
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

dec = obj.modifiers.new("Decimate", "DECIMATE")
dec.ratio = 0.5
sub = obj.modifiers.new("Subdiv", "SUBSURF")
sub.levels, sub.render_levels = 1, 2

# Сглаживание по углу: имя оператора менялось между 4.0 и 4.1
smooth_ops = [o for o in dir(bpy.ops.object)
              if "smooth" in o or "auto" in o]
print("available:", smooth_ops)
```

> [!NOTE]
> В 4.1 оператор авто-сглаживания переименован (было `shade_auto_smooth`, стало `shade_smooth_by_angle`). Проверь список и вызови тот, что есть в твоей версии — точечный вызов надёжнее, чем зашитое имя.

### 7. Оценка стоимости до запуска

```python
# Перед пакетной генерацией считаем, во сколько обойдётся партия.
# Конкретную стоимость кредита бери из аккаунта — она меняется, и в статье
# любой «примерный» тариф станет устаревшим быстрее, чем любой другой факт.
PLAN = [
    {"task": "text-to-3D preview", "count": 30},
    {"task": "text-to-3D final",   "count": 5},
    {"task": "text-to-texture",    "count": 5},
    {"task": "remesh",             "count": 5},
]
for row in PLAN:
    print(f"{row['task']:22s} x{row['count']:<3d} -> всего задач: {row['count']}")
print("Итого операций:", sum(r["count"] for r in PLAN))
# Затем сверь расход: GET <endpoint баланса> из документации
```

Прежде чем запускать пакет, прогони одну задачу в режиме предпросмотра и посмотри результат. Разница между дешёвым превью и платным финалом обычно окупает потраченные пять минут.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверка кредитов/профиля перед пакетной генерацией
curl -s -H "Authorization: Bearer $MESHY_API_KEY" "https://api.meshy.ai/users/meshy/balance"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `mode` | `preview` | `text`/`refine` для финального качества, дороже |
| `should_remesh` | `True` | меш с нормалями вместо «капли» |
| `should_texture` | `True` | без текстуры меш бесполезен для продакшена |
| `should_rig` | `True` для персонажей | требует валидной топологии, чинит артефакты |
| `topology` | `quad` | `tri` быстрее и дешевле |
| `target_face_count` | `15000` | игровой проп; `50000+` для крупных планов |
| интервал опроса | `6` с | меньше — лимит запросов |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| 401 сразу | ключ не тот или срок истёк | перевыпусти ключ в аккаунте |
| 404 на любом пути | сменилась версия API | сверь `BASE` и префикс с документацией |
| `KeyError` по ключу ответа | схема ответа другая | напечатай `json.dumps(body)[:800]` и поправь разбор |
| Задача висит в `PENDING` дольше минуты | очередь платформы | это нормально; не перезапускай — создашь дубль |
| Меш «капля» без текстуры | не заказан ремеш/текстура | повтори с `should_remesh` и `should_texture` |
| UV растянуты | авто-UV на неправильной топологии | quad-ремеш перед текстурированием |
| Скелет не импортировался | формат скелета не в GLB | импортируй скелет отдельным файлом |
| Blender-mcp не знает про Meshy | интеграции нет в этой сборке | делай через HTTP, как выше |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 16: BLENDER + AUTOMATIC1111 API](setup_16_automatic1111_api.md), [SETUP 44: RODIN / HYPER3D GEN](setup_44_rodin_hyper3d.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md)
- **По темам:** [SETUP 47: ZERO123 / INSTANTMESH](setup_47_zero123_instantmesh.md), [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md)
- **Теги:** #ai-3d, #api, #setup
