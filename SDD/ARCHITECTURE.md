# ARCHITECTURE

Обновлено: 2026-10-01. Источник истины по архитектуре.

Документы: [`SPEC.md`](SPEC.md) (что) · [`SCHEMA.md`](SCHEMA.md) (данные) ·
[`API.md`](API.md) (HTTP) · [`SEO.md`](SEO.md) (продвижение) ·
[`adr/`](adr/) (почему так) · [`../CHANGELOG.md`](../CHANGELOG.md) (история).

## 1. Система целиком

```
                        ┌──────────────── python (stdlib) ────────────────┐
markdown корпус         │                                                 │
WIKI/prompts    50      │  fix_frontmatter → fix_lang_frontmatter →        │
WIKI/setups     60      │  mark_stubs → build_database → build_graph →      │
WIKI/workflows  28      │  export_all ×4 → crossref → index → site        │
WIKI/cases      16      │                                   │              │
WIKI/references 19+10   │                                   ▼              │
WIKI/multilang  163×5   │                        WIKI/db/wiki_database.json│
        │                │                        (997 записей, 9.4 МБ)    │
        └────────────────┴──────────────────────────────┬────────────────┘
                                                       │ читается на сборке
                                                       ▼
                                          web/  Astro 7 (static)
                                                       │
                        ┌──────────────────────────────┼──────────────┐
                        ▼                              ▼              ▼
                  916 HTML-страниц              llms.txt / .md     sitemap.xml
                  203 индексируемых             llms-full.txt     robots.txt
                  631 noindex-зеркало           834 .md-близнеца   rss.xml
                                                       │
                                        ┌──────────────┴───────────────┐
                                        ▼                              ▼
                                 Pagefind (поиск)          Cloudflare Workers
                                                            (static assets, edge)
```

Два независимых конвейера:

| | Роль | Состояние |
|---|------|-----------|
| `WIKI/scripts/run_all.py` | пайплайн данных: markdown → БД → экспорты → сайт → 5 гейтов | **основной** |
| `web/` | Astro-сборка + SEO-гейты + деплой | поверх данных |
| `WIKI/scripts/wiki_api.py` | HTTP API + legacy-сайт на `:8099` | локально, для разработки и агентов |

Публикуется только Astro-сайт. Python-API остаётся как локальный инструмент:
он даёт полнотекстовый поиск по всей базе и JSON для агентов, но не является
публичным сервисом (см. `SPEC.md` §3).

## 2. Один источник правды — и три места, где это легко сломать

Источник контента — markdown. Всё остальное генерируется. За это платим тремя
известными точками отказа, каждая из которых уже стоила реального бага:

| Точка отказа | Что произошло | Чем закрыто |
|---|---|---|
| **Правило дедупликации продублировано** в трёх местах: `content.ts`, `astro.config.mjs`, гейты | sitemap выпадал на 163 страницы, потому что фильтр считал shadow-зеркала noindex | `verify-consistency.mjs` сверяет sitemap с реально опубликованными страницами |
| **Домен был зашит в константу**, а конфиг брал из env | страницы рекламировали один origin, sitemap — другой | `src/lib/site-url.ts` — единственный источник, оба берут из `import.meta.env.SITE` |
| **Язык выводился эвристикой** на каждой сборке | русские статьи публиковались под `/en/` | `lang:` пишется в frontmatter, сборка его только читает (`fix_lang_frontmatter.py`) |

Общее правило: **любое решение, которое влияет на SEO, должно быть вычислено
в одном месте и проверено гейтом.** Два гейта на каждую сборку:
`verify-seo.mjs` (каждый артефакт сам по себе) и `verify-consistency.mjs`
(артефакты согласованы между собой).

## 3. Классификация страниц

Одна статья × 5 языков = один URL или пять. Отсюда три состояния:

| Состояние | Что это | Публикуется | robots | canonical | sitemap | llms-full |
|---|---|---|---|---|---|---|
| **indexable** | оригинал или перевод `human` | да | `index, follow` | себя | да | да |
| **duplicate** | зеркало `template`/`legacy` | да | `noindex, follow` | оригинал | нет | нет |
| **shadow** | язык зеркала == язык оригинала | **нет** | — | — | URL = у оригинала | нет |

163 shadow-зеркала: русский оригинал и `multilang/ru/…` дают один URL.
631 duplicate: переводы-шаблоны в es/de/zh (и en, где оригинал русский).
Итого 203 индексируемые страницы из 997 записей БД.

## 4. Пайплайн и гейты

```
fix_frontmatter      снять tags: из frontmatter (лечит битый YAML)
fix_lang_frontmatter записать lang: один раз, явным решением
mark_stubs           status: / translation:
check_missing        паритет multilang
build_database       → db/*.json
build_graph          → db/graph.json (позиции предрасчитаны)
export_all ×4        CSV / Notion / Obsidian
rebuild_crossref     crossref/*
build_index          INDEX.md
build_site           site/data (legacy)
── гейты ──
validate.py          13 секций по корпусу и БД
test_wiki.py         22 теста инвариантов
quality_report.py    бэклог пробелов (не гейт)
── сайт ──
npm run all          astro build → agent files → pagefind → 2 SEO-гейта
npm run preflight    домен, конфиг, лимиты Workers
```

`run_all.py` требует `PUBLIC_SITE_URL` для шага сайта: сборка без него зашила бы
`localhost` в canonical и sitemap, и такой сайт нельзя публиковать.

## 5. Узкие места

| Узкое место | Решение | Остаточная цена |
|---|---|---|
| `build_database.py` 4–5 с, 9.4 МБ JSON | API кэширует по mtime | полная пересборка, инкрементальной нет |
| `dist/` 22 МБ / 2663 файла | в пределах лимитов Workers (20 000 / 25 МБ) | 3.8 МБ gzip HTML на полный обход |
| 916 страниц × 55 с сборка | приемлемо для статики | CI будет медленным, нужен кэш `node_modules` |
| Поиск | Pagefind, индекс на сборке | индексирует только `[data-pagefind-body]` (834 из 916) |

## 6. Границы и отказы

| Что | Поведение |
|-----|-----------|
| `PUBLIC_SITE_URL` не задан | `run_all.py` и `preflight.mjs` останавливают деплой |
| Порт занят (API) | понятное сообщение, код 2 |
| `dist/` не собран | `preflight` требует артефакты до `wrangler deploy` |
| Шаблонный перевод в sitemap | `verify-consistency` валит сборку |
| Битая внутренняя ссылка | `verify-seo` валит сборку |
| Осиротевший перевод | `validate.py` §11 валит сборку |
| `Content-Type` для `.md` | Workers назначает по расширению; `text/markdown` подтверждён замером |

## 7. Чего сознательно нет

- Публичный API с авторизацией и rate-limit (локальный инструмент).
- Инкрементальная сборка БД.
- Подсветка синтаксиса (Shiki) — `marked` без неё.
- CI: гейты автоматизируемы (`run_all.py`, `npm run all`), но не запускаются
  автоматически нигде.
- Свои markdown-зеркала `llms-full.txt` (используем генератор поверх БД).

Подробности продвижения: [`SEO.md`](SEO.md).
