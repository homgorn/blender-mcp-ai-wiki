# DATA SCHEMA

Версия БД: `1.0`. Контракт API: `1.1` (`/api/version`).
Файлы описаны по состоянию на 2026-09-28. Генерируются — руками не править.

## 1. `db/wiki_database.json` (9.4 МБ, 997 записей)

```jsonc
{
  "version": "1.0",
  "created": "<ISO-8601, время сборки>",
  "total_entries": 997,
  "statistics": { ... },          // см. §5
  "entries": [ Entry, ... ]
}
```

### Entry

| Поле | Тип | Источник | Описание |
|------|-----|----------|----------|
| `meta.id` | string | имя файла | уникальный ID: `setup_01_x` либо `01_geometry_basics__es` |
| `meta.orig_id` | string | имя файла | только для переводов; совпадает с ID оригинала |
| `meta.title` | string | первый `#`-заголовок | при отсутствии — имя файла в Title Case |
| `meta.category` | string | первый сегмент пути | `prompts`, `setups`, `workflows`, `cases`, `references`, … |
| `meta.type` | enum | категория | `prompt` \| `setup` \| `workflow` \| `case` \| `reference` \| `guide` |
| `meta.difficulty` | int 0..3 | число ⭐ в тексте | 0 = не указано |
| `meta.tags` | string[] | `#tag`, `Теги:`, `Tags:`, `tags:` | фильтруются hex-цвета, цифры, мусор |
| `meta.language` | enum | путь `multilang/{lang}` либо эвристика | `en` \| `ru` \| `es` \| `de` \| `zh` |
| `meta.is_translation` | bool | путь | `true` для всех файлов под `multilang/` |
| `meta.translation` | enum | frontmatter | `human` \| `template` \| `legacy` — честная маркировка качества перевода |
| `meta.status` | enum | frontmatter | `full` \| `stub` — только для `setups/workflows/cases` |
| `meta.description` | string ≤500 | первый абзац после H1 | используется в карточке и поиске |
| `meta.mcp_tools` | string[] | бэктики имён MCP-инструментов | например `execute_blender_code` |
| `meta.links` | `{text,url}[]` | внутренние md-ссылки | сырьё для графа и crossref |
| `meta.code_blocks` | int | подсчёт ```-блоков | метрика объёма |
| `meta.word_count` | int | `len(content.split())` | метрика объёма |
| `meta.created` / `meta.updated` | ISO-8601 | сборка / mtime файла | ⚠ `created` = время сборки, не дата авторства |
| `sections` | object[] | разбор по `##` | `{index, heading, content≤2000, word_count, has_code}` |
| `full_content` | string | файл целиком | API отдаёт максимум 30 000 символов + флаг `truncated` |
| `file_path` | string | путь от `WIKI/` | обратные слэши на Windows |
| `content_hash` | md5[:16] | содержимое | признак протухшей БД; проверяется тестами |

**Известная шероховатость:** `meta.created` проставляется временем сборки, поэтому БД не
побитово-воспроизводима. Для детекции реальных изменений использовать `content_hash`, а не
дифф всего файла.

## 2. `db/search_index.json` (416 КБ)

```
terms        : { слово -> [entry_id] }     // только title+description+tags+tools
tags         : { тег   -> [entry_id] }
tools        : { mcp_tool -> [entry_id] }
categories   : { категория -> [entry_id] }
languages    : { lang -> [entry_id] }
difficulties : { "0".."3" -> [entry_id] }
entry_lookup : { entry_id -> индекс в entries }
```

## 3. `db/graph.json` (448 КБ, 997 узлов / 1426 связей)

```
nodes: [{ id, title, category, lang, tags, file, x, y }]
links: [{ source, target, label }]
```
`x`/`y` — предрасчитанные координаты (см. `build_graph.py`): категории раскладываются по
секторам спирали Архимеда с золотым углом, радиус ~ `120 + 26·√i` + стабильный джиттер по
md5(id). Детерминированно: та же БД → та же картинка.

## 4. `site/data/*` (статика для браузера без API)

| Файл | Что это | Кто читает |
|------|---------|-----------|
| `meta.json` | лёгкий индекс: id, title, category, type, difficulty, tags, language, file, desc≤300 | `app.js` — первая отрисовка |
| `chunks/entries_{category}.json` | полные записи одной категории | `app.js` — при открытии статьи (ленивая догрузка) |
| `search_index.json` | поиск в статическом режиме | `app.js` |
| `graph.json` | граф с позициями | `graph.html` |
| `sitemap.json`, `langs.json` | навигация и счётчики | `app.js` |
| `wiki_database.json` | полная копия БД (legacy/fallback) | API-режим, отладка |

Инвариант: `meta.json.total` == сумма `chunks[*].total` == `db.total_entries` (гейт `validate.py` §7).

## 5. `statistics`

`total_entries`, `by_category`, `by_type`, `by_language`, `by_difficulty`, `top_tags` (30),
`top_tools` (20), `total_words`, `total_code_blocks`, `entries_with_code`.

## 6. Frontmatter (единственный вход для ручных полей)

```yaml
---
id: 01_geometry_basics      # не переопределяет path-derived id, но читается человеком
lang: es
orig_lang: ru
category: prompts
type: prompt
difficulty: 2
translation: human         # human | template | legacy
status: full                # full | stub — только setups/workflows/cases
---
```

Правило: frontmatter **не может** выдумать новые поля, которые дальше никто не читает.
Всё, что не описано в `build_database.extract_metadata`, в БД не попадёт.
