---
id: setup_51_notion_obsidian_docs
lang: ru
category: setups
type: setup
status: full
tags: [docs, setup]
---
# SETUP 51: NOTION/OBSIDIAN DOCS SYNC

**ID:** SETUP-51 | **Type:** Docs | **Difficulty:** ⭐ | **Time:** 10 min
**RU/EN Bilingual**

> Когда применять: когда wiki растёт и её надо отдавать в Notion или Obsidian —
> как чтение, а не как «обновлённое зеркало, о котором никто не знает».

---

## 🎯 ЦЕЛЬ

Настроить односторонний экспорт базы знаний в два формата: Obsidian-vault (папка
`.md` с вики-ссылками) и Notion (JSON для импорта или API). Ключевое решение — **не
двусторонняя синхронизация**: источник правды один, markdown, экспорт read-only.

Всё, что ниже, основано на реально существующих скриптах этого репозитория
(`WIKI/scripts/build_database.py`, `WIKI/scripts/export_all.py`), а не на
придуманных командах.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Python | 3.10+ | Скрипты сборки базы и экспорта |
| `WIKI/scripts/build_database.py` | из репозитория | `db/wiki_database.json` — источник для экспорта |
| `WIKI/scripts/export_all.py` | из репозитория | CSV + Obsidian-vault + Notion JSON |
| Obsidian | любая Desktop-версия | Просмотр `.md`-vault без плагинов |
| Notion | аккаунт с правом создавать страницы | Импорт JSON либо API-загрузка |

---

## 🛠️ НАСТРОЙКА

### 1. Пересобрать базу — экспортировать из базы нельзя

Экспортёр читает `db/wiki_database.json`. Если база устарела, экспорт разнесёт по
Notion и Obsidian старые версии статей вместе с новыми.

```powershell
# Перейдите в каталог проекта
cd "<путь-к-проекту>"
python "WIKI\scripts\validate.py" --strict
python "WIKI\scripts\test_wiki.py"
```

### 2. Запустить экспорт

У `export_all.py` ровно два аргумента: `--chunk` (номер части) и `--chunks`
(на сколько частей резать). Один файл на ~1000 статей — это десятки мегабайт
JSON, поэтому дробить обязательно.

```powershell
# Проверено по исходнику WIKI/scripts/export_all.py
cd "<путь-к-проекту>\WIKI"
python scripts\export_all.py --chunk 0 --chunks 4
python scripts\export_all.py --chunk 1 --chunks 4
python scripts\export_all.py --chunk 2 --chunks 4
python scripts\export_all.py --chunk 3 --chunks 4
```

На выходе появляются три артефакта:

```
WIKI/db/wiki_export_0.csv            # заголовок: id,title,category,type,
                                     # difficulty,language,tags,tools,file,description
WIKI/export_obsidian/01_geometry_basics.md
WIKI/export_obsidian/01_geometry_basics__ru.md
WIKI/export_notion/notion_import_0.json
```

### 3. Понять формат Obsidian-заметки

Vault — это обычная папка с `.md`. Экспортёр пишет ровно такой файл: frontmatter,
заголовок, описание, раздел `## Links` с `[[вики-ссылками]]` и служебная строка
`_File:` с путём на оригинал.

```markdown
---
id: 01_geometry_basics
category: prompts
tags: [basics, bpy, bpy.ops, geometry, modeling, primitives, prompt]
lang: ru
---

# P01: PRIMITIVE CREATION BASICS

## Links
- [[07_instancing_arrays]]
- [[23_geometry_nodes_basics]]

_File: `prompts\01_geometry_basics.md`_
```

Имя файла — это `id` из базы. Для переводов `id` имеет суффикс `__ru`, поэтому
оригинал и перевод в одном vault не конфликтуют и оба остаются на связи.

### 4. Понять формат Notion-JSON

Это не «выгрузка страницы», а список объектов `page`, готовый к импорту: у каждой
страницы заданы свойства (Category, Lang, Difficulty, Tags, File) и один дочерний
блок с описанием.

```json
{
 "pages": [
  {
   "object": "page",
   "properties": {
    "title": [{"text": {"content": "P01: PRIMITIVE CREATION BASICS"}}],
    "Category": {"select": {"name": "prompts"}},
    "Lang": {"select": {"name": "ru"}},
    "Difficulty": {"number": 1},
    "Tags": {"multi_select": [{"name": "basics"}, {"name": "bpy"}]},
    "File": {"rich_text": [{"text": {"content": "prompts\\01_geometry_basics.md"}}]}
   },
   "children": [
    {"object": "block", "type": "paragraph",
     "paragraph": {"rich_text": [{"text": {"content": ""}}]}}
   ]
  }
 ]
}
```

Свойства из JSON **должны существовать в базе Notion заранее** с теми же именами
и типами (`select` / `number` / `multi_select` / `rich_text`). Иначе импорт
создаёт страницы без метаданных — и кросс-ссылки по тегам перестают работать.

### 5. Залить в Notion

Два пути. Импорт через UI проще и не требует токена; API-путь нужен для
автоматизации.

```powershell
# Путь A: UI. Собрать все части в один zip и импортировать:
#   Notion → Import → Markdown & CSV → zip
#   Перед импортом разложить части, переименовав их в *.md, иначе Notion
#   не примет .json.

# Путь B: API. Создать страницу одной командой:
$headers = @{
  "Authorization"  = "Bearer $env:NOTION_TOKEN"
  "Notion-Version" = "2022-06-28"
  "Content-Type"   = "application/json"
}
$body = Get-Content "WIKI\export_notion\notion_import_0.json" -Raw | ConvertFrom-Json
Invoke-RestMethod -Method Post -Uri "https://api.notion.com/v1/pages" `
  -Headers $headers -Body (@{
    parent = @{ database_id = $env:NOTION_DATABASE_ID }
    properties = $body.pages[0].properties
    children   = $body.pages[0].children
  } | ConvertTo-Json -Depth 20)
```

> [!NOTE]
> `Notion-Version` — это версия API Notion, а не Blender и не wiki. Значение
> `2022-06-28` использовалось здесь как пример; актуальную дату возьми из
> документации Notion (https://developers.notion.com) и держи её в конфиге
> проекта. Загрузка полного тела статьи (а не одного абзаца описания)
> делается отдельным вызовом с блоками — в экспортере её нет намеренно,
> чтобы JSON оставался разумного размера.

### 6. Договориться о direction of travel

| Среда | Роль | Обратная синхронизация |
|---|---|---|
| `WIKI/*.md` | Единственный источник правды | — |
| Obsidian vault | Чтение, поиск, граф вики-ссылок | Нет: правки в vault не возвращаются |
| Notion | Ревью, комментарии, задачи | Только через экспорт заметок, вручную |
| `db/wiki_database.json` | Производный артефакт | Перезаписывается сборкой |

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Полный цикл: пересобрать базу → разложить на 4 части → проверить
cd "<путь-к-проекту>"
python "WIKI\scripts\validate.py" --strict
python "WIKI\scripts\build_database.py"
python "WIKI\scripts\export_all.py" --chunk 0 --chunks 4
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `--chunks` | `4` | Больше статей — больше частей (Notion не любит гигантские импорты) |
| `--chunk` | `0..N-1` | Прогоняется по кругу; забытый чанк = дыра в базе |
| `id` в имени файла | `01_geometry_basics__ru` | Не менять: Obsidian-ссылки строятся по нему |
| `Tags` в Notion | `multi_select` | Длиннее 10 тегов экспортёр не пишет — следить за ростом |
| `description` | первые 1000 символов | Не хватает — править экспортёр, а не Notion |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| В Notion страницы без тегов и категории | В базе Notion нет свойств `Category` / `Tags` нужного типа | Создать свойства заранее: `Category`=select, `Difficulty`=number, `Tags`=multi_select |
| Заметки в Obsidian не связаны `[[...]]` | Экспортирована часть базы без поля `links` | Пересобрать базу и экспортировать заново, а не править vault руками |
| Переводы перезаписали оригиналы | Имя файла строилось из заголовка, а не из `id` | Экспортёр уже использует `id` с суффиксом `__ru` — не откатывай это |
| Notion отказался импортировать `.json` | Импорт через UI ждёт ZIP с `.md`/`.csv` | Переименовать части в `.md`, упаковать, импортировать |
| В базе старая версия статьи | Экспорт шёл до `build_database.py` | Порядок строго: validate → build → export |
| Части Obsidian «потерялись» | Экспортёр пишет по `m['id']`, коллизия перезатирает файл | Проверить, нет ли двух статей с одинаковым `id` — это баг, а не фича |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **Теги:** #docs, #setup
