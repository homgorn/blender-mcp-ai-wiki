# SDD — Spec-Driven Development

Источник истины по статусам и запуску. Обновлено: **2026-10-01**.

Документы: [`SPEC.md`](SPEC.md) (что) · [`ARCHITECTURE.md`](ARCHITECTURE.md) (как устроено) ·
[`SEO.md`](SEO.md) (продвижение) · [`SCHEMA.md`](SCHEMA.md) (форматы данных) ·
[`API.md`](API.md) (HTTP-контракт локального API) · [`adr/`](adr/) (почему так) ·
[`../CHANGELOG.md`](../CHANGELOG.md) (история) · [`../web/README.md`](../web/README.md) (сайт).

## Окружение
- Python **3.11+** (проверено на 3.12). Пайплайн данных — только стандартная библиотека.
- Node **≥22.12** (проверено на 22.23) — нужен Astro 7. Требуется для `web/`.
- Единственная необъявленная зависимость Python: **PyYAML** (есть фолбэк-парсер,
  ADR 0004); ставится `pip install pyyaml`.
- PowerShell: `New-Item` вместо `mkdir -p`, `;` вместо `&&`.

## Быстрый старт
```powershell
# Полный цикл: корпус → БД → экспорты → сайт → все гейты
$env:PUBLIC_SITE_URL = "https://<ваш-домен>"
python "C:\BLENDER ai\WIKI\scripts\run_all.py"

# Части пайплайна
python "C:\BLENDER ai\WIKI\scripts\run_all.py" --fast        # без экспортов
python "C:\BLENDER ai\WIKI\scripts\run_all.py" --skip-site    # без Astro
python "C:\BLENDER ai\WIKI\scripts\run_all.py" --step build_database.py
python "C:\BLENDER ai\WIKI\scripts\validate.py"               # 13 секций по корпусу
python "C:\BLENDER ai\WIKI\scripts\test_wiki.py"              # 22 теста
python "C:\BLENDER ai\WIKI\scripts\quality_report.py"         # бэклог пробелов

# Сайт отдельно
cd "C:\BLENDER ai\web"
npm install
npm run all            # build → agent files → pagefind → SEO-гейты
npm run preflight      # домен + лимиты Pages, обязателен перед деплоем
npm run deploy         # all + preflight + wrangler pages deploy

# Локальный HTTP API (поиск по всей базе, JSON для агентов)
python "C:\BLENDER ai\WIKI\scripts\wiki_api.py" --port 8099
```

## Порядок сборки (зависимости, а не привычка)
```
fix_frontmatter → fix_lang_frontmatter → mark_stubs → check_missing
  → build_database → build_graph → export_all ×4 → rebuild_crossref
  → build_index → build_site
  → [гейт] validate.py → [гейт] test_wiki.py → quality_report
  → [сайт] astro build → agent files → pagefind → [гейт] verify-seo
           → [гейт] verify-consistency → [гейт] preflight
```
Нарушение порядка = сайт отдаёт устаревшие данные, и именно поэтому оркестратор
один. Два новых шага в начале лечат данные, а не маскируют их: `fix_frontmatter`
снимает битый YAML, `fix_lang_frontmatter` записывает язык один раз явным решением.

## Правила проекта
1. Каждый чанк работы — отдельный скрипт в `WIKI/scripts/`, идемпотентный.
2. После каждого изменения — `run_all.py` (или минимум `validate.py` + `test_wiki.py`).
3. Все `.md` — UTF-8. Проверять через python, не через вывод PowerShell (консоль garbles кириллицу).
4. PowerShell: `New-Item` вместо `mkdir -p`, `;` вместо `&&`.
5. Ничего не редактируется руками в `WIKI/db/`, `WIKI/site/data/`, `WIKI/export_*` — это артефакты.
6. Правка спеки — вместе с кодом. Несовпадение чисел в SPEC ловит `validate.py` §12.
7. Решение, меняющее архитектуру → ADR в `SDD/adr/`.

## Что где лежит
| Документ | О чём |
|----------|-------|
| `SPEC.md` | что делаем, границы, критерии приёмки, техдолг |
| `ARCHITECTURE.md` | компоненты, поток данных, инварианты, отказы |
| `SCHEMA.md` | форматы `db/*` и `site/data/*` |
| `API.md` | HTTP-контракт (версионирован) |
| `adr/` | 4 ADR: почему blender-mcp, зеркала переводов, чанки+граф, stdlib-only |
| `../WIKI/CONTRIBUTING.md` | как писать статью |
| `../WIKI/quality_report.md` | текущий бэклог по пробелам в контенте (автогенерация) |
| `../WIKI/templates/` | эталон структуры для 4 типов статей |
| `../WIKI/scripts/README.md` | роли всех скриптов и порядок сборки |

## Статусы задач
- [x] DONE · [>] IN PROGRESS · [ ] TODO

## Эпики
- [x] E1. `validate.py` + базовая валидация
- [x] E2. Промпты P16–P30 полные
- [x] E3. Мёрж корня + INDEX
- [x] E4. Переводы (человеческие, es/de/zh)
- [x] E5. Сайт MVP + граф + deep-link
- [x] E6. Чистка + scripts README
- [x] E7. Добивка по критике (9 пунктов)
- [x] E8. P41–P50, топ-15 stub→full, чанки сайта, +12 переводов, предрасчётный граф, Blender HDRI
- [x] E9. Инженерный харденинг: кэш БД в API, ETag/304, потоки, контракт API, тесты,
      оркестратор, инвариант зеркал, чистка 5 осиротевших переводов, документация
      (ARCHITECTURE / SCHEMA / API / adr / CONTRIBUTING)
- [x] E10. Astro + Cloudflare: 916 статических страниц, SEO-гейты (2 независимых),
      llms.txt v2 + markdown-близнецы, preflight деплоя, общий пайплайн
- [x] E11. Данные: явный `lang:` (вместо догадки при сборке), снят битый YAML из
      frontmatter 538 файлов, устранено 163 коллизии URL, честная классификация
      indexable/duplicate/shadow
- [x] E12. Публикация и долг: поддомен `blender-mcp-wiki.r00m.ru`, Cloudflare Pages
      вместо Workers, Shiki, теги у всех 182 оригиналов, структурные пробелы 80 → 0,
      `validate.py --strict` в конвейере, CI на GitHub Actions, 6 скриптов переведены
      на рекурсивный обход (19 файлов `references/v1/**` были не видны гейтам)

## Текущее состояние
997 записей БД · 182 оригинала · 916 опубликованных страниц · 203 индексируемые ·
631 noindex-зеркало · 834 `.md`-близнеца · 0 битых ссылок · все гейты зелёные.

## Открытые вопросы
Перенесены в `SPEC.md` §6: контроль версий (git), CI, хостинг, объём человеческих переводов.
Решения по ним не приняты — это осознанно, а не забыто.
