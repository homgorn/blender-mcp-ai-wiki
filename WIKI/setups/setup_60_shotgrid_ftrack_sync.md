---
id: setup_60_shotgrid_ftrack_sync
lang: ru
category: setups
type: setup
status: full
tags: [production, setup]
---
# SETUP 60: SHOTGRID / FTRACK SYNC

**ID:** SETUP-60 | **Type:** Production | **Difficulty:** ⭐⭐⭐ | **Time:** 35 min
**RU/EN Bilingual**

> Когда применять: когда над шотом работают несколько человек и нужно, чтобы
> «версия 3», «Mount» и «в работе» значили одно и то же в трекере и в Blender.

---

## 🎯 ЦЕЛЬ

Описать порядок работы между Blender и продакшн-трекером (ShotGrid / ftrack) так,
чтобы он не зависел от конкретных полей и конкретной версии API.

Статья **намеренно не приводит ни одного имени поля или метода API** трекера:
схема сущностей и набор полей настраиваются в каждой студии по-своему, а имена
endpoints меняются между версиями. Придуманное имя метода хуже, чем его
отсутствие: по нему начнут писать интеграцию.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 5.x (проверено 5.2.1) | Публикация версий, метаданные, аннотации |
| ShotGrid или ftrack | версия вашей студии | Хранение шотов, задач, версий, заметок |
| Python | 3.10+ | Скрипт публикации |
| Сетевое хранилище | NFS/SMB | Куда кладутся версии `.blend` |
| ffmpeg | 7.x+ (проверено 9.0.1) | Превью-ролик для ревью |

---

## 🛠️ НАСТРОЙКА

### 1. Разделить ответственность: что читаем, что пишем

```
        Трекер (источник правды по статусам)
             │  pull: список моих задач, имена шотов, заметки ревью
             ▼
   ┌──────────────────────┐   push: новая версия + метаданные + превью
   │        Blender       │ ────────────────────────────────────────────▶
   └──────────────────────┘
```

Односторонняя запись — в трекер. Чтение — в обе стороны, но без конфликтов:
люди не правят `.blend` через трекер, только статусы и комментарии.

### 2. Описать маппинг файлом, а не кодом

Единственный артефакт, который реально переживёт смену версии трекера, — ваш
собственный файл соответствия. Он не «API трекера», он — контракт вашего пайплайна.
Обратите внимание: внутри описаны **роли**, а не имена полей студии.

```json
{
  "tracker": "shotgrid",
  "roles": {
    "shot_code":      {"from": "code of the shot entity",            "note": "обычно код вроде sh010"},
    "task_name":      {"from": "name of the task entity",           "note": "в студии может быть 'Mount' или 'Lighting'"},
    "version_id":     {"from": "human-readable version identifier",  "note": "берём из Publish, не из имени файла"},
    "review_notes":   {"from": "annotation threads on the version",  "note": "только текст, без вложений"},
    "storage_root":   {"from": "per-project storage root",           "note": "куда публикуем .blend"}
  },
  "publish": {
    "blend_subdir":   "blend",
    "preview_subdir": "preview",
    "manifest_name":  "manifest.json",
    "extensions":     [".blend", ".exr", ".mp4"]
  },
  "status_policy": {
    "push":   ["in_progress", "ready_for_review", "final"],
    "pull":   ["todo", "in_progress", "on_hold"]
  }
}
```

### 3. Опубликовать версию из Blender

```python
# publish_version.py — Blender пишет файлы и манифест, трекеру достаётся
# только этот манифест. Никаких полей трекера скрипт не знает.
import bpy, json, os, hashlib, datetime, shutil

def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

def publish(shot_code, task_name, storage_root, frame_range):
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(storage_root, "blend", shot_code, task_name, stamp)
    os.makedirs(out, exist_ok=True)

    # Упаковать и сжать: в трекер уходит маленький файл (проверено в 5.2)
    bpy.ops.file.pack_all()
    blend = os.path.join(out, f"{shot_code}_{task_name}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)

    manifest = {
        "shot_code":  shot_code,
        "task":       task_name,
        "published":  stamp,
        "blender":    bpy.app.version_string,
        "frame_range": list(frame_range),
        "files":      [{"name": os.path.basename(blend),
                        "sha256": sha256(blend),
                        "bytes": os.path.getsize(blend)}],
    }
    mpath = os.path.join(out, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return mpath

print(publish("sh010", "Mount", "//storage/shots", (1, 250)))
```

`manifest.json` — это то, что делает публикацию проверяемой: трекеру не нужен
доступ к вашим дискам, достаточно файла с хэшами. И когда версия «пропала»,
первый вопрос — совпадает ли `sha256`.

### 4. Сделать превью для ревью

```bash
# Превью — отдельная папка версии, отдельным битрейтом.
# Проверено на ffmpeg 9.0.1:
ffmpeg -y -framerate 24 -start_number 1 -i exr/sh010_####.exr \
  -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart \
  "preview/sh010_Mount_20261002_101500.mp4"
```

Ограничение по длине — организационное, а не техническое: ревьюер смотрит
первые 15 секунд. Если превью длиннее, в нём почти никто не досмотрит до конца.

### 5. Забрать заметки ревью в Blender

Заметки ревью — единственное, что должно приходить в 3D обратно, и только в
одном-единственном виде: маркеры на таймлайне плюс текстовый блок. Так их видит
animator, который не знает, что такое трекер.

```python
# pull_notes.py — читает нормализованный JSON (его собрал скрипт трекера),
# а не полезет в API трекера из Blender.
import bpy, json, datetime

def pull_notes(path):
    with open(path, encoding="utf-8") as fh:
        notes = json.load(fh)

    sc = bpy.context.scene
    # Маркер = место + короткий текст. Всё длинное — в текстовый блок.
    for m in list(sc.timeline_markers):
        if m.name.startswith("REV_"):
            sc.timeline_markers.remove(m)

    stamp = datetime.datetime.now().strftime("%H%M")
    txt = bpy.data.texts.get("REVIEW_NOTES") or bpy.data.texts.new("REVIEW_NOTES")
    txt.clear()

    for n in notes["items"]:
        frame = int(n.get("frame") or sc.frame_start)
        txt.write(f"{frame}\t{n['author']}\t{n['body']}\n")
        sc.timeline_markers.new(f"REV_{frame}_{n['author'][:8]}", frame=frame)
    return len(notes["items"])

print("notes:", pull_notes("//storage/inbox/sh010_review.json"))
```

### 6. Отдать статус и версию обратно

```python
# push_status.py — Blender не ходит в трекер. Он только пишет файл,
# а на стороне трекера маленький скрипт его читает и обновляет сущности.
import json, os, datetime

def request_status(shot_code, task_name, state, blend_manifest_path, root):
    assert state in ("in_progress", "ready_for_review", "final")
    req = {
        "shot_code": shot_code,
        "task": task_name,
        "state": state,
        "version": datetime.datetime.now().isoformat(timespec="seconds"),
        "manifest": os.path.relpath(blend_manifest_path, root).replace("\\", "/"),
    }
    out_dir = os.path.join(root, "requests")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{shot_code}_{task_name}_{req['version'].replace(':','-')}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(req, fh, ensure_ascii=False, indent=2)
    return path

print(request_status("sh010", "Mount", "ready_for_review",
                      "//storage/shots/blend/sh010/Mount/manifest.json", "//storage"))
```

Такой «файловый мост» медленнее прямого вызова API и полностью это окупает:
он переживает смену трекера, его видно в логах, и его можно проверить вручную.

### 7. Обработать мост на стороне трекера

Скрипт, который читает папку запросов, — единственное место, где живёт знание о
конкретном трекере. Он маленький, и его легко заменить, когда студия сменит
систему.

```python
# apply_requests.py — запускается на стороне трекера (по cronу или вручную).
# Здесь и только здесь появляются имена полей вашего инстанса.
import json, os, glob, logging

ROOT = "//storage"
REQUESTS = os.path.join(ROOT, "requests")
log = logging.getLogger("apply_requests")

def read_requests():
    for path in sorted(glob.glob(os.path.join(REQUESTS, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            yield path, json.load(fh)

def publish_to_tracker(req):
    """ЗАГЛУШКА. Реализация зависит от вашего трекера и его версии:
    найти сущность шота по req['shot_code'], найти задачу по req['task'],
    создать версию, приложить превью, выставить статус req['state']."""
    raise NotImplementedError(
        "заполняется под ваш ShotGrid/ftrack: имена полей берите у админа студии"
    )

for path, req in read_requests():
    try:
        publish_to_tracker(req)
        os.replace(path, path + ".done")   # сначала переименовать, потом слать уведомление
        log.info("applied %s -> %s", req["shot_code"], req["state"])
    except NotImplementedError:
        raise
    except Exception as exc:
        log.exception("failed %s: %s", path, exc)
        # Файл оставляем: он будет обработан снова после починки.
```

Порядок «сначала переименовать, потом слать уведомление» — не формальность:
иначе при падении между публикацией и записью статуса вы получите версию в
трекере без соответствующей записи в логе, и расхождение обнаружится через месяц.

### 8. Аутентификация и доступы — только через администратора студии

| Что нужно | Как это обычно устроено |
|---|---|
| Адрес | URL сайта ShotGrid или сервера ftrack |
| Идентификация скрипта | Имя приложения/скрипта, заведённое админом |
| Секрет | Токен или пароль, выданный админом |
| Права | Минимально необходимые: создавать версии, читать заметки |

> [!NOTE]
> Имена переменных окружения, параметров аутентификации и структура ответа
> API у ShotGrid и ftrack свои и меняются между версиями; в ftrack доступ
> обычно оформляется через персональный API-токен, в ShotGrid — через
> пару «имя сайта + имя скрипта» и ключ. Берите эти значения у того, кто
> администрирует ваш инстанс, и держите их в секрете окружения CI, а не в
> репозитории. Официальные страницы продуктов: https://www.ftrack.com/ и
> https://www.autodesk.com/products/flow-production-tracking/

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр / артефакт | Значение | Когда менять |
|---|---|---|
| `pipeline_map.json` | роли, а не имена полей | Единственное, что правится при переезде на другой трекер |
| `manifest.json` | sha256 + версия Blender | Обязателен: без него «версия пропала» не диагностируется |
| `compress=True` при сохранении | включать | Уменьшает и загрузку, и размер версии в трекере |
| Имя версии | `YYYYMMDD_HHMMSS` | Сортируется лексикографически — не нужно разбирать |
| `status_policy.push` | `in_progress` / `ready_for_review` / `final` | Согласовать с продюсером: кто имеет право ставить `final` |
| Маркер `REV_*` | кадр + первые 8 символов автора | Animator видит это в таймлайне без открытия трекера |

> [!NOTE]
> Конкретные имена сущностей и полей (код шота, имя задачи, идентификатор
> версии) настраиваются в каждом проекте. Статья их не приводит намеренно:
> выдуманное имя поля неотличимо от настоящего, и интеграция, написанная по
> выдумке, падает на первой же авторизации.

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Интеграция работает у одного и падает у другого | Имена полей взяты из чужого проекта | Держать маппинг в `pipeline_map.json`, а не в коде |
| Статус «в работе», версия в трекере есть | Двусторонняя запись: статус затирается | Сделать трекер единственным владельцем статусов |
| Версия открылась, но битые пути | `.blend` не упакован | `bpy.ops.file.pack_all()` перед `save_as_mainfile(compress=True)` |
| Заметки ревью не на таймлайне | Формат JSON изменился, скрипт молча прочитал 0 items | Проверять счётчик `notes:` в выводе, а не «посмотрел — вроде ок» |
| `sha256` разошёлся при проверке | Файл перезаписан поверх версии | Версии иммутабельны: новая правка — новая папка с новым штампом |
| Публикация едет по второму кругу | Скрипт читает свой же запрос | Файлы запросов живут в отдельной папке и очищаются после обработки |
| CI падает на авторизации | Токен в репозитории протух | Секреты в CI-секретах, ротация по расписанию |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **Теги:** #production, #setup
