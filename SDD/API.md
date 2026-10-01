# HTTP API CONTRACT

Версия контракта: **1.1** (`GET /api/version`). Реализация: `WIKI/scripts/wiki_api.py` (только stdlib).
Машиночитаемый вариант: `GET /api/openapi.json`.

```
python scripts/wiki_api.py --port 8099 [--host 127.0.0.1] [--quiet]
```
Слушает **только localhost по умолчанию**: это dev-инструмент, не публичный сервис.
Авторизации, rate-limit и TLS здесь нет сознательно (см. `SDD/SPEC.md` §3).

## Правила

1. Все ответы — JSON, UTF-8, `Content-Type: application/json; charset=utf-8`.
2. `Access-Control-Allow-Origin: *` (локальный dev; при выносе наружу — заменить).
3. Каждый ответ несёт `ETag`; при совпадении `If-None-Match` отдаётся `304` без тела.
4. `Cache-Control`: `no-store` для динамики, `max-age=300, must-revalidate` для `/site/data/*`.
5. **GET ничего не меняет.** Побочные эффекты только у `POST /api/rebuild` и `POST /api/export`.
6. Ошибки: 4xx/5xx с телом `{"error": "...", ...}`, не пустой ответ.

## Эндпоинты

| Метод | Путь | Параметры | Ответ |
|-------|------|-----------|-------|
| GET | `/api/health` | — | `{ok, entries, version, api}` |
| GET | `/api/version` | — | `{api, db, python, contract}` |
| GET | `/api/openapi.json` | — | OpenAPI 3.0.3 |
| GET | `/api/stats` | — | объект `statistics` |
| GET | `/api/tags` | — | `{tags: {тег: [id]}}` |
| GET | `/api/list` | `category, lang, type, limit(1..200, деф 50), offset` | `{total, limit, offset, total_pages, items[]}` |
| GET | `/api/entry` | `id` | `{meta, sections, file, full_content, truncated, truncated_at, total_chars}` |
| GET | `/api/search` | `q, lang, category, limit(1..50, деф 10)` | `{items[], cached}` |
| GET | `/api/sitemap` | — | `{total, items:[{id, lang, cat, url}]}` |
| GET | `/api/graph` | `limit(1..5000, деф 300), lang, category` | `{nodes[] (с x/y), links[], total_nodes}` |
| POST | `/api/rebuild` | — | `{ok, out}` — пересборка БД, сброс кэша |
| POST | `/api/export` | `format, chunk, chunks` | `{ok, format, out, files}` |
| GET | `/api/export` | — | **405** — «GET must not mutate state» |
| GET | `/site/…` | — | статика из `WIKI/site/` |
| — | всё остальное | — | `404 {error, routes[]}` |

## Важные детали

- `full_content` в `/api/entry` обрезан до 30 000 символов. Обрезка **явная**:
  `truncated: true` и `truncated_at: 30000`; `total_chars` — полный размер. Раньше обрезка была
  молчаливой, и клиент не мог отличить полную статью от огрызка.
- `total_pages` считается по `total` и `limit`; при пустом результате `total_pages = 0`.
- `cached: true` означает попадание в кэш процесса (TTL 120 с), а не «из БД не искали».
- `/api/graph` отдаёт **предрассчитанные** `x`/`y` из `db/graph.json`; `lang`/`category`
  фильтруют, `limit` применяется после фильтрации.
- БД перечитывается при изменении mtime — можно править markdown и делать `POST /api/rebuild`
  без перезапуска сервера.

## Примеры

```powershell
Invoke-RestMethod "http://127.0.0.1:8099/api/health"
Invoke-RestMethod "http://127.0.0.1:8099/api/search?q=displacement&limit=3"
Invoke-RestMethod "http://127.0.0.1:8099/api/list?category=prompts&limit=5&offset=0"
Invoke-RestMethod "http://127.0.0.1:8099/api/entry?id=41_displacement_micro"
Invoke-RestMethod "http://127.0.0.1:8099/api/openapi.json"
Invoke-RestMethod -Method Post "http://127.0.0.1:8099/api/export?format=csv&chunk=0&chunks=4"
```

Проверка контракта автотестами: `python scripts/test_wiki.py` (класс `TestApiContract`
поднимает сервер на случайном порту и проверяет коды, ETag/304, пагинацию, 404/405).
