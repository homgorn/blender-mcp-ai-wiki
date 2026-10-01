---
id: setup_37_blenderkit_assets
lang: ru
category: setups
type: setup
status: full
tags: [assets, setup]
---
# SETUP 37: BLENDERKIT ASSETS

**ID:** SETUP-37 | **Type:** Asset Lib | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

> Когда применять: нужна библиотека готовых моделей, материалов и HDRI, чтобы не тратить день на то, что уже сделали другие — и с понятной лицензией.

## 🎯 ЦЕЛЬ
Настроить BlenderKit как рабочий источник ассетов внутри Blender: найти и отфильтровать бесплатное, скачать пакетом, подключить как Asset Browser и проверить лицензию перед тем, как ассет попадёт в коммерческий проект. Отдельный блок — выгрузка своего ассета в общую библиотеку.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 4.x | хост аддона |
| Аддон BlenderKit | входит в поставку Blender, включается в Preferences → Add-ons | поиск, скачивание, загрузка своих ассетов |
| Аккаунт BlenderKit | `blenderkit.com` | избранное, история, загрузка ассетов |
| API-ключ | выдаётся в настройках аддона | доступ к REST API для батчей |

> [!NOTE]
> Точная схема авторизации в API менялась: ключ мог передаваться как query-параметр, как заголовок `Authorization`, или требовать отдельного токена. Не пиши запрос, пока не посмотришь, что именно показывает твоя панель настроек и что описано в документации по адресу `blenderkit.com/docs/`. Ниже примеры намеренно без конкретного способа подстановки ключа.

## 🛠️ НАСТРОЙКА

### 1. Включение аддона и авторизация
```python
import bpy

print("blenderkit загружен:",
      "blenderkit" in bpy.context.preferences.addons.keys())

# Локальная папка, куда аддон складывает скачанное
bk = bpy.context.preferences.addons.get("blenderkit")
if bk:
    prefs = bk.preferences
    for attr in dir(prefs):
        if not attr.startswith("_") and attr in (
                "api_key", "blenderkit_directory", "username", "search_limit"):
            print(attr, "=", getattr(prefs, attr))
```
Путь к библиотеке важен: если он внутри сетевого диска или в синхронизируемой папке, загрузка ассетов резко замедляется — файлы большие, и атомарные переименования по сети дорогие.

### 2. Поиск в UI
Панель BlenderKit в N-панели (Sidebar) даёт поиск с фильтрами по типу ассета: models, materials, HDRIs, textures, scenes, brushes, node groups. Практический порядок работы:

| Шаг | Что делаем | Зачем |
|---|---|---|
| 1 | Фильтр по типу | иначе в выдаче тонна того, что не нужно |
| 2 | Галочка «Free» | убирает платные ассеты из результата |
| 3 | Сортировка по популярности/оценке | ранний шум — внизу |
| 4 | Смотрим лицензию и разрешение текстур | определяет, годится ли ассет в коммерческий проект |

### 3. Установка ассета в сцену
Drag & drop из панели BlenderKit работает так: перетаскивание в 3D-вьюпорт создаёт объект, перетаскивание в Outliner импортирует ассет в сцену. Программный эквивалент — добавление через `bpy.ops.wm.append` по пути к файлу.

```python
import bpy

# Точный путь к библиотеке берём из настроек аддона, а не угадываем
bk = bpy.context.preferences.addons.get("blenderkit")
lib_dir = bk.preferences.blenderkit_directory if bk else r"C:\blenderkit_data"

print("библиотека:", lib_dir)
```
> [!NOTE]
> Имя свойства с путём к библиотеке — `blenderkit_directory`; выше оно используется как в примере, но проверь выводом `dir(prefs)`: поле могло быть переименовано. Путь — это фактически Asset Library, поэтому следующий шаг тоже требует его точного значения.

### 4. Подключение как Asset Browser
```python
# Asset Browser читает библиотеки из настроек, а не из кода.
# Здесь только проверяем, что каталог существует и не пуст.
import os

lib_dir = r"C:\blenderkit_data"
print("существует:", os.path.isdir(lib_dir))
if os.path.isdir(lib_dir):
    print("элементов:", len(os.listdir(lib_dir)))
```
Саму библиотеку добавляют через `Edit → Preferences → File Paths → Asset Libraries`: указать имя и корневой путь. После этого ассеты BlenderKit видны в Asset Browser, и их можно перетаскивать в сцену.

```python
# Проверка, что ассет помечен как asset-объект (иначе в браузере не появится)
for o in bpy.data.objects[:10]:
    if o.asset_data():
        print("asset:", o.name, "| catalog:", o.asset_data().catalog_id)
```

### 5. Батч через API
Для массовой загрузки (например, наполнить сцену 5 материалами + 3 моделями + 1 HDRI) удобнее REST API.

```python
import json
import urllib.request

API = "https://www.blenderkit.com/api/v1/search/"

def search(query, asset_type="model", free_only=True):
    """Поиск ассетов. Поле token подставь по инструкции из docs."""
    payload = {
        "query": query,
        "asset_type": asset_type,          # model / material / hdri / texture
        "is_free": free_only,
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "User-Agent": "blender-pipeline/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

# res = search("concrete wall", asset_type="material")
# for item in res.get("results", [])[:5]:
#     print(item["name"], item.get("filesize"))
```

> [!NOTE]
> Тело запроса и набор полей (`query`, `asset_type`, `is_free`) приведены по смыслу. Фактические имена полей и требуемый заголовок авторизации уточни в документации API — BlenderKit менял схему, и запрос без правильного ключа вернёт 401 либо пустой список. Это не повод переписывать код, а повод сначала открыть один запрос в браузере и посмотреть ответ.

### 6. Скачивание файлов ассета
У ассета в ответе API есть несколько файлов (геометрия, текстуры, превью). Скачивать надо **все**, иначе материал придёт без карт.

```python
# Типичная структура: у каждого файла есть url, size, checksum
def iter_files(res):
    for result in res.get("results", []):
        for f in result.get("files", []):
            if f.get("download_type") in (None, "blend", "texture"):
                yield result["name"], f

# for name, f in iter_files(res):
#     print(name, f["url"], f.get("file_size"))
```

### 7. Загрузка своего ассета
```text
1. Отделить ассет: объект/материал помечается Asset (Object → Asset → Mark as Asset)
2. В N-панели BlenderKit: Upload → выбрать категорию и заполнить описание
3. Загрузить превью (опционально, но сильно повышает кликабельность)
4. Отправить на модерацию — ассет появляется в библиотеке после проверки
```
Приватные ассеты доступны только владельцу и требуют действующей подписки.

### 8. Лицензия — проверять всегда
```python
# Подпись ассета содержит условия; печатаем, а не принимаем на веру
res = search("wood", asset_type="material")
for r in res.get("results", [])[:3]:
    print(r.get("name"), "|", r.get("license_short_name"),
          "|", r.get("is_free"), "| автор:", r.get("user", {}).get("username"))
```
Бесплатный ассет не значит «любая лицензия»: у части ассетов ограничения на коммерческое использование, а часть — CC0, часть — royalty-free с указанием автора. Проверять надо до того, как ассет окажется в рендере.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```python
# Сводка по локальной библиотеке: сколько весит и сколько внутри
import os
lib = r"C:\blenderkit_data"
if os.path.isdir(lib):
    total = 0
    files = 0
    for root, _, names in os.walk(lib):
        for n in names:
            files += 1
            total += os.path.getsize(os.path.join(root, n))
    print(f"файлов: {files}, объём: {total/1024/1024:.0f} МБ")
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `asset_type` | `model` / `material` / `hdri` / `texture` | подставлять под задачу, иначе в выдаче мусор |
| фильтр Free | включён | выключать, когда нужен конкретный платный ассет |
| путь библиотеки | локальный SSD | сетевой диск — только если ассетов мало |
| `import_pack_images` | `False` | при батче, чтобы не раздувать blend-файл |
| модерация загрузки | требуется | сроки модерации — от нескольких часов до нескольких дней |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Панели BlenderKit нет | аддон не включён | `Preferences → Add-ons`, включить и перезапустить панель |
| Поиск возвращает пустоту | не авторизован либо фильтр Free слишком жёсткий | Войти в аккаунт, ослабить фильтры |
| API отдаёт 401 | не подставлен токен | Сверяться с документацией по авторизации |
| Скачался материал без карт | скачан только blend-файл | Качать все файлы ассета из ответа API |
| Asset Browser пуст | библиотека не добавлена в `File Paths` | Добавить путь и перезапустить Blender |
| Ассет не появляется в браузере | объект не помечен как Asset | `Object → Asset → Mark as Asset` |
| Импорт микроскопический | ассет в сантиметрах, сцена в метрах | Масштабировать вручную либо применить трансформации |
| Ассет «исчез» после переустановки Blender | путь к библиотеке сменился | Держать библиотеку в фиксированном месте и переподключать путь |
| Скачивание подвисает | библиотека на сетевом диске | Перенести локально, скачать, потом раздать по местам |

## 🖥 MCP-ПРОМПТ

```text
RU: "BlenderKit: 5 бесплатных материалов + 3 модели + 1 HDRI,
     только free, проверь лицензию каждого, вывеси размер и автора,
     импортируй в отдельную коллекцию" /
EN: "BlenderKit: 5 free materials + 3 models + 1 HDRI,
     free filter only, verify each license, print size and author,
     import into a dedicated collection"
```

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 39: QUIXEL BRIDGE STANDALONE](setup_39_quixel_bridge.md), [SETUP 40: AMBIENTCG + POLYHAVEN BATCH](setup_40_ambientcg_polyhaven.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md), [P36: ASSET LICENSING (PIZZA/SKETCHFAB/HAVEN)](../prompts/36_asset_licensing.md)
- **Теги:** #assets, #setup