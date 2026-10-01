---
id: setup_40_ambientcg_polyhaven
lang: ru
category: setups
type: setup
status: full
tags: [assets, automation, setup]
---
# SETUP 40: AMBIENTCG + POLYHAVEN BATCH

**ID:** SETUP-40 | **Type:** Free PBR | **Difficulty:** ⭐ | **Time:** 40-60 min

> Когда применять: когда нужна пачка бесплатных CC0-материалов и HDRI без ручного скачивания по одной штуке — общий API-запрос, раскладка на диск, проверка лицензии и подключение к сцене одним скриптом.

## 🎯 ЦЕЛЬ

ambientCG и Poly Haven — два CC0-источника, которые можно тянуть пачками: у Poly Haven есть документированный публичный API, у ambientCG — свой. Собираем один скрипт, который по списку ID тянет карты и HDRI, раскладывает их в предсказуемую структуру каталогов и отдаёт в Blender готовым материалом. Отдельно фиксируем главное про лицензию: оба источника CC0, но у ambientCG аттрибуция не обязательна, а у Poly Haven указание автора приветствуется — и то и другое менялось, поэтому проверяй страницу ассета.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Python | 3.10+ (можно встроенный в Blender) | скрипт пакетной загрузки |
| `requests` | 2.x | HTTP-запросы к API |
| Аккаунт Poly Haven | бесплатный | часть загрузок требует авторизации |
| Blender | 4.x LTS | применение HDRI и создание материалов |
| Диск | 5-20 ГБ на 10 материалов 2K | 8K-наборы весят сотни мегабайт |

## 🛠️ НАСТРОЙКА

### 1. Poly Haven: список ассетов через API

```python
import requests

BASE = "https://api.polyhaven.com"

r = requests.get(f"{BASE}/assets", params={"t": "textures"}, timeout=30)
r.raise_for_status()
assets = r.json()
print("textures:", len(assets))
print("первые id:", list(assets)[:5])
```

> [!NOTE]
> Хост `api.polyhaven.com` и пути `/assets`, `/info/<id>`, `/files/<id>` — те, что использовались до переезда Poly Haven на новый сайт. Если 404, открой документацию на polyhaven.com и возьми актуальный базовый URL: он менялся. Логику ниже правь в одном месте — в `BASE`.

### 2. Poly Haven: какие файлы качать

```python
def list_files(asset_id: str, res: str = "2k") -> dict:
    r = requests.get(f"{BASE}/files/{asset_id}", timeout=30)
    r.raise_for_status()
    return r.json()

info = list_files("wood_floor_deck")
# Структура ответа: ключ — тип карты (Diffuse/Roughness/Normal/Displacement/...),
# значение — словарь по разрешениям, в котором лежат вложенные dict'ы с "url"
print(list(info.keys()))
print(json.dumps(info, indent=2)[:600])
```

### 3. Скачиваем и раскладываем

```python
import json
from pathlib import Path

OUT = Path(r"C:/assets/free_pbr")

def download(url: str, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk); total += len(chunk)
    return total

def grab_polyhaven(asset_id: str, res: str = "2k") -> int:
    files = list_files(asset_id, res)
    base = OUT / "polyhaven" / asset_id
    written = 0
    for map_type, per_res in files.items():                 # Diffuse, Normal, ...
        entry = per_res.get(res) or next(iter(per_res.values()), None)
        if not entry:
            continue
        # url лежит во вложенном слое: {"1k": {"HDRI": {"url": ...}}} и т.п.
        urls = [v["url"] for v in entry.values()
                if isinstance(v, dict) and "url" in v]
        for u in urls:
            written += download(u, base / f"{map_type}_{Path(u).name}")
    return written

print(grab_polyhaven("wood_floor_deck", "2k") // 1024, "KB")
```

### 4. ambientCG: карточка ассета и ссылка на скачивание

```python
CG = "https://ambientcg.com"
r = requests.get(f"{CG}/api/v2/full_json", params={"id": "Metal032"}, timeout=60)
r.raise_for_status()
data = r.json()
print("имя:", data.get("displayName"))
# В ответе есть поле с идентификатором набора файлов и структура папок загрузки
print("ключи верхнего уровня:", sorted(data.keys())[:15])
```

> [!NOTE]
> Имя поля, в котором лежит ссылка на скачивание, у ambientCG менялось (`downloadFolders`, потом другие). Не хардкодь ключ — сначала напечатай `sorted(data.keys())` и достань нужный путь по факту. Формат самой ссылки `.../get?file=...` тоже сверь на странице ассета.

### 5. Скачиваем набор ambientCG

```python
def grab_ambientcg(asset_id: str, res: str = "1K-JPG") -> int:
    r = requests.get(f"{CG}/api/v2/full_json", params={"id": asset_id}, timeout=60)
    r.raise_for_status()
    data = r.json()
    written = 0
    for entry in data.get("downloadFolders", []):
        attr = entry.get("attribute", "")
        if res and res not in attr:
            continue
        # Downloadable в 1K-JPG: файлы лежат по одной ссылке на весь набор
        for f in entry.get("downloadable", {}).get("Resolution", []):
            for fl in f.get("downloadFilenames", []):
                url = f"{CG}/get?file={fl}"
                written += download(url, OUT / "ambientcg" / asset_id / f"{attr}.zip")
    return written

print(grab_ambientcg("Metal032", "1K-JPG") // 1024, "KB")
```

### 6. Создаём материал из скачанных карт

```python
import bpy
from pathlib import Path

def pbr_material_from_folder(folder: Path, mat_name: str) -> bpy.types.Material:
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    links.clear()

    out  = nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled");  bsdf.location = (300, 0)

    wanted = {"color": "Base Color", "roughness": "Roughness", "metal": "Metallic"}
    for stem, socket in wanted.items():
        hit = next(folder.glob(f"*{stem}*.jpg"), None) or next(folder.glob(f"*{stem}*.png"), None)
        if not hit:
            continue
        tex = nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(hit))
        tex.location = (-100, 0)
        links.new(tex.outputs["Color"], bsdf.inputs[socket])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

folder = next((OUT / "ambientcg" / "Metal032").glob("*.zip"), None)
print("zip распакован в:", folder)
```

### 7. Ставим HDRI как окружение

```python
import bpy

scene = bpy.context.scene
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
env = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(r"C:/assets/free_pbr/polyhaven/studio_small_08/HDRI_2k.hdr")
world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
print("view transform:", scene.view_settings.view_transform,
      "| exposure:", scene.view_settings.exposure)
```

### 8. Лицензия: что можно, а что нет

Оба источника CC0 — это значит «можно использовать в коммерции без обязательного указания авторства». Практическая проверка всё равно нужна, потому что условия переписывались и у ambientCG, и у Poly Haven:

```python
# Собираем происхождение каждого файла в один отчёт — проще отвечать на вопросы клиента
import json
from pathlib import Path

MANIFEST = Path(r"C:/assets/free_pbr/MANIFEST.json")
entries = [
    {"id": "wood_floor_deck", "source": "polyhaven", "license": "CC0-1.0", "res": "2k"},
    {"id": "Metal032",        "source": "ambientcg", "license": "CC0-1.0", "res": "1K-JPG"},
]
MANIFEST.write_text(json.dumps(entries, indent=2), encoding="utf-8")
print(MANIFEST.read_text(encoding="utf-8"))
```

> [!NOTE]
> Формулировки лицензий на сайтах менялись. Относись к CC0 как к рабочему предположению для черновиков и продакшена, но перед сдачей клиенту сверься со страницей конкретного ассета. Авторство указывать полезно всегда, даже когда оно не обязательно.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверяем, что Poly Haven API вообще отвечает, до того как строить пайплайн
curl -s -o NUL -w "%{http_code}\n" "https://api.polyhaven.com/assets?t=hdris"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `t` (тип ассета) | `textures`, `hdris`, `models` | брать из документации, значения менялись |
| `res` | `1k` / `2k` / `4k` | 2K для превью, 4K для финального рендера |
| `displacement_method` в Cycles | `BUMP` | на превью быстрее, `DISPLACEMENT` на финале |
| `bg.inputs["Strength"]` | `1.0` | 0.3-0.5 для студийных HDRI, 2+ для уличных |
| `view_transform` | `AgX` (Blender 4.x) | `Filmic` в 3.x, `Standard` для точных цветов |
| пауза между запросами | `0.3-1.0` с | бережёт лимит и не ловит 429 |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| 404 на `/assets` | база переехала | открой документацию polyhaven.com, поправь `BASE` |
| 401/403 на скачивании | нужна авторизация | войди в аккаунт и подставь токен в заголовок |
| `KeyError` по ключу ответа | смена схемы API | сначала `print(list(info.keys()))`, потом читай ключ |
| Скачался один файл вместо набора | вложенность `url` глубже одного уровня | рекурсивно обходи dict и собирай всё, что имеет `url` |
| 429 при пакетной загрузке | слишком частые запросы | пауза между запросами, retry с задержкой |
| HDRI-картинка не отображается | `view_transform` срезает диапазон | подними `exposure` или смени `view_transform` |
| Цвета «кислотные» | Linear/Non-Color не выставлен | Color Data = sRGB для цветовых карт, Non-Color для roughness/normal |
| Материал без roughness-карты | в наборе имя `Roughness` с большой буквы | поиск регистронезависимый |
| Диск кончился на 8K | 8K UDIM = 64 плитки | качай 2K для библиотеки, 8K точечно под финал |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 35: READY PLAYER ME AVATARS](setup_35_readyplayerme.md), [SETUP 37: BLENDERKIT ASSETS](setup_37_blenderkit_assets.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 39: QUIXEL BRIDGE STANDALONE](setup_39_quixel_bridge.md)
- **По темам:** [P18: DRIVERS & CONSTRAINTS](../prompts/18_drivers_constraints.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P27: POLY HAVEN ASSET PIPELINE](../prompts/27_polyhaven_pipeline.md)
- **Теги:** #assets, #automation, #setup
