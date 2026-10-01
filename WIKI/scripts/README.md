# WIKI SCRIPTS — README

Все скрипты запускаются из PowerShell, рабочая папка любая (пути внутри абсолютные).
Требования: Python 3.11+ (единственная внешняя зависимость — `PyYAML`, есть фолбэк),
Node ≥22.12 для шага сайта.

## Обычный запуск: одна команда

```powershell
$env:PUBLIC_SITE_URL = "https://<ваш-домен>"
python "C:\BLENDER ai\WIKI\scripts\run_all.py"
```
Делает всё в правильном порядке и прогоняет гейты. Финал: `PIPELINE GREEN`.

`PUBLIC_SITE_URL` обязателен для шага сайта: он попадает в canonical, hreflang,
Open Graph, sitemap и robots. Без него сборка зашила бы `localhost` во все эти
файлы, и пайплайн останавливается с предупреждением.

| Флаг | Что меняет |
|------|-----------|
| `--fast` | пропустить экспорты CSV/Notion/Obsidian |
| `--skip-tests` | не запускать `test_wiki.py` |
| `--skip-site` | не собирать Astro-сайт и не запускать SEO-гейты |
| `--step build_database.py` | один шаг (отладка) |

## Порядок сборки и почему он такой

```
fix_frontmatter.py ──► fix_lang_frontmatter.py ──► mark_stubs.py
   ──► check_missing.py ──► build_database.py ──► build_graph.py
   ──► export_all.py ×4 ──► rebuild_crossref.py ──► build_index.py ──► build_site.py
   ──► [гейт] validate.py ──► [гейт] test_wiki.py ──► quality_report.py
   ──► [сайт] npm run all (astro build → agent files → pagefind → 2 SEO-гейта)
   ──► [сайт] npm run preflight
```

Это граф зависимостей, а не привычка. Два первых шага лечат данные, а не маскируют
их: `fix_frontmatter` снимает битый YAML, `fix_lang_frontmatter` записывает язык
один раз явным решением вместо догадки при каждой сборке.

Отдельные шаги (когда нужен точечный запуск):

```powershell
python "C:\BLENDER ai\WIKI\scripts\validate.py"      # 13 секций full-scan, exit 0/1
python "C:\BLENDER ai\WIKI\scripts\validate.py" --strict   # + конформанс шаблонам как гейт
python "C:\BLENDER ai\WIKI\scripts\test_wiki.py"     # 22 теста, exit 0/1
$env:WIKI_SLOW_TESTS=1; python "C:\BLENDER ai\WIKI\scripts\test_wiki.py"   # + validate внутри
python "C:\BLENDER ai\WIKI\scripts\wiki_api.py" --port 8099 [--quiet]
#   сайт: http://127.0.0.1:8099/site/    API: http://127.0.0.1:8099/api/
```

## Роли скриптов

### Гейты (ломают сборку при проблеме)
| Скрипт | Роль |
|--------|------|
| `validate.py` | 13 секций: кодировки, структура, промпты, дубли корня, БД, паритет языков, синхронность site/data, frontmatter, битые ссылки, ID/тела/теги, **осиротевшие переводы**, **совпадение чисел со SPEC**, конформанс шаблонам |
| `test_wiki.py` | юнит-тесты парсинга, инвариантов БД, артефактов сайта и HTTP-контракта API |

### Сборка
| Скрипт | Роль |
|--------|------|
| `fix_frontmatter.py` | убирает производную строку `tags:` из frontmatter. Нужна потому, что неотфильтрованный `tags: **, 8b7355` ломает YAML (`*` — алиас), а `extract_frontmatter` глотал ошибку, теряя `id`/`lang`/`translation` у 538 файлов |
| `fix_lang_frontmatter.py` | один раз записывает `lang:` в файлы без него и печатает таблицу решения на ревью. Язык — авторские метаданные, а не результат эвристики при каждой сборке |
| `build_database.py` | скан md → `db/wiki_database.json`, `search_index.json`, `wiki_export.json`. Здесь же `CATEGORIES`, фильтр тегов и приоритет языка (путь → frontmatter → детектор) |
| `build_graph.py` | узлы/линки + **предрасчёт позиций** в `db/graph.json` |
| `build_site.py` | копирует артефакты в `site/data`, пишет `meta.json` и `chunks/entries_{cat}.json` |
| `export_all.py` | `--chunk N --chunks M`: CSV + Notion + Obsidian |
| `build_index.py` | `WIKI/INDEX.md` из реального скана |
| `rebuild_crossref.py` | `WIKI/crossref/*` из статистики БД |
| `bulk_multilang.py` | `--lang X --chunk N --chunks M [--only ...] [--force]`: зеркала переводов |
| `mark_stubs.py` | маркировка `status:` и `translation:` (идемпотентен) |
| `fix_links.py` | фикс известных битых ссылок и legacy-frontmatter (идемпотентен) |

### Сервис
| Скрипт | Роль |
|--------|------|
| `wiki_api.py` | HTTP API + раздача сайта. Контракт: `SDD/API.md`, схема: `/api/openapi.json` |
| `check_missing.py` | паритет multilang между языками |
| `wiki_const.py` | **единственный** источник `HUMAN_MIRRORS` для `mark_stubs.py` и `validate.py` |

### Генераторы контента (одноразовые, отработали; оставлены как история)
`bulk_generate2.py` (сетапы 15–60, воркфлоу 09–28, кейсы 07–16) · `gen_p16_p20.py` · `gen_p21_p30.py` ·
`gen_human12a.py` / `gen_human12b_part1.py` / `gen_human12b_part2.py` (human-переводы) ·
`upgrade_top10.py` / `upgrade_top15.py` (stub→full) · `check_misc.py`

### PowerShell-обвязка
`check.ps1` — короткая проверка (БД непустая + паритет) для быстрого «жив ли проект».
`hook.ps1` — вызывается из git-хука, если репозиторий будет создан (см. `SDD/SPEC.md` §6).

## Эндпоинты API (контракт 1.1)

Полное описание — `SDD/API.md`. Кратко:

| Метод | Путь |
|-------|------|
| GET | `/api/health`, `/api/version`, `/api/openapi.json`, `/api/stats`, `/api/tags`, `/api/sitemap` |
| GET | `/api/list?category=&lang=&type=&limit=&offset=` |
| GET | `/api/entry?id=` (явные `truncated`/`total_chars`) |
| GET | `/api/search?q=&lang=&category=&limit=` |
| GET | `/api/graph?limit=&lang=&category=` (предрасчётные `x`/`y`) |
| POST | `/api/rebuild`, `/api/export?format=&chunk=&chunks=` |
| GET | `/site/…` — статика с ETag/304 |

`GET /api/export` возвращает 405: GET не должен менять состояние.

## Важно про кодировки

- Все `.md` — **UTF-8**. PowerShell `Get-Content`/`Select-Object` показывают кракозябры для
  кириллицы и эмодзи — это проблема консоли (cp1251), а не файла. Проверять через
  `python -c "print(open(f,encoding='utf-8').read()[:200])"` или через `validate.py` §1.
- Не писать `.md` через `Set-Content` без `-Encoding UTF8`.

## Как добавить статью

`WIKI/CONTRIBUTING.md`: шаблон из `WIKI/templates/`, имя файла → ID, затем `run_all.py`.
