# CHANGELOG

## [2026-11-12] - 3.3.0 Appearance system как референс; сайт перекрашен в дизайн-токены; постоянный скриншот-гейт

### Added
- **`WIKI/references/appearance_system.md`** — очищенная дизайн-система внешнего вида
  (токены, компоненты, WCAG 2.2 AA, QA-чеклист), опубликована под
  `/en/references/appearance-system`; попадёт в БД и на сайт автоматически (223 статьи
  теперь публикуются, OG-карточка сгенерирована).
- **`web/scripts/screenshot-pages.mjs`** — постоянный гейт визуальной проверки: все
  305 страниц скриншотятся на 390/768/1440 px и проверяются на один `<h1>`,
  отсутствие горизонтального переполнения, видимый `<nav>` с `aria-label` и реальные
  ссылки, `lang` на `<html>`, ошибки консоли и неудавшиеся запросы.

### Changed
- **Сайт перекрашен в дизайн-систему appearance_system.md**: светлая тема по
  умолчанию (раньше — тёмная), тёплые stone-оттенки, акцент `#10796b` (4.6:1 на белом),
  радиусы из ramp (xs..step8), тени `shadow.1/shadow.2`, `body` 14px/20px как в
  системе, focus-visible 3px, пилюли (`radius.step7`) у тегов и бейджей, карточки на
  `shadow-1` с hover на `shadow.2`.
- Тёмная схема сохранена: те же имена токенов, другая палитра; сырых значений вне
  `:root` не осталось.

### Verification
- `npm run all` зелёный: 33 теста, оба SEO-гейта, preflight, 223 индексируемые страницы.
- 915 скриншотов (305 × 3 ширины): **0 проблем**.

## [2026-10-02] - 3.2.0 SEO-разметка, навигация, 74 статьи, честные языки

### Added
- **Своя OG-карточка 1200×630 у каждой из 222 статей.** Раньше все делили один
  `og-default.png`, и ссылка в мессенджере выглядела одинаково. Генератор проверяет
  покрытие cmap — кириллица и CJK не рисуются «тофу».
- **Иконки:** `favicon.svg`, `favicon.ico` (16/32/48), `apple-touch-icon.png`,
  `icon-192/512`, `icon-maskable-512`, `site.webmanifest`, `theme-color`, `generator`.
- **Футер в 4 колонки** — Материалы (14 категорий со счётчиками в текущем языке),
  Языки (реальные числа), Инструменты (поиск, RSS, llms.txt, sitemap), О проекте.
  Каждая колонка — `<nav>` со своим `aria-label`.
- **Мобильное верхнее меню** через `<details>/<summary>`, **без JavaScript**:
  панель раскрывается и при отключённом JS. Горизонтальный скролл выбран не был —
  он прятал бы половину пунктов.
- `content_quality.py` — гейт, который ловит то, чего не видит структурная проверка:
  `bool(bpy.ops...)` (всегда истинно), заглушки, пустые блоки кода, `status: full`
  ниже планки глубины, одинаковые абзацы в разных статьях.
- `api_compat.py` — разрешает каждый путь `bpy.*` из корпуса против установленного
  Blender интроспекцией, не выполняя код корпуса. Использует `dir()`, а не
  `hasattr()`: `bpy.ops` отвечает заглушкой на любой вопрос.
- `fix_empty_link_headings.py`, `regenerate_goal_sections.py`, гейт `validate.py` §15
  (заголовок с пустым телом).

### Fixed
- **222 страницы прокручивались вбок на мобильном.** Причина: `Prose.astro` принимал
  пропс `class` и не применял его, поэтому весь CSS `.prose` — включая
  `pre { overflow-x: auto }` — не действовал ни на одной статье.
- **Остаток того же класса:** в мобильной перезаписи `.layout` стояло голое `1fr`,
  а это `minmax(auto, 1fr)`, и `auto` не даёт колонке сжаться. Теперь `minmax(0, 1fr)`.
- **Длинные URL не переносились** — `overflow-wrap: anywhere` для ссылок и текста.
  `break-word` не подошёл бы: он не меняет min-content ширину, из которой считается
  трек грида, и переполнение вернулось бы.
- **`og:locale:alternate` объявлял 5 языков на каждой странице**, включая 628
  несуществующих версий. Теперь строится из реальных alternates.
- **Главная говорила «5 языков»** — утверждение, которое мы признали ложным.
  `stats.languages` был `LANGS.length`, то есть числом объявленных языков. Заменено
  на вычисляемое из данных: 2 языка с полным корпусом плюс честный перечень остальных.
- **Гейт считал `&amp;` за 5 символов** и показывал два несуществующих превышения
  длины заголовка. Теперь декодирует сущности перед измерением.
- **FAQPage удалён полностью.** В `name` вопроса клался заголовок статьи — это не
  вопрос. Разметка без видимого Q&A — риск ручной меры, а расширенного сниппета с
  августа 2023 всё равно не было бы. Гейт падает при повторном появлении.
- `Article` → `TechArticle`: комментарий в коде утверждал, что TechArticle не даёт
  rich result. Неверно — это подтип `Article`, право на сниппет наследуется.

### Changed
- `TechArticle` + `BreadcrumbList` на 222/222 статьях.
- `title` ≤ 60 и `description` ≤ 155, обрезка по границе слова. Раньше 95 из 222
  описаний длиннее 160 и обрезались в выдаче.
- Корпус: **74 `status: stub` → 0**, плюс 9 старых статей, где метка `full` была
  завышена (134 слова и ноль блоков кода). Медиана 206 слов / 1 блок → ~900 / 9.

### Open
- **Версия Blender не решена** (`SDD/adr/0006`). Корпус написан против 4.x,
  установлена 5.2.1 LTS, 29 файлов содержат имён, которых в 5.2 нет — включая
  `bpy.ops.object.fluid_add`, отсутствующий полностью. Проверка готова и измеряет
  состояние одной командой.
- `npm run check` не работает: скрипт `astro check` есть, а `@astrojs/check`
  и `typescript` в зависимостях отсутствуют. Типы не проверяются никогда.
- Статус-бейдж («полная»/«черновик») не рендерится на страницах статей: в БД и в
  разметке значение есть, причина не найдена. Косметика.

## [2026-10-01] - 3.1.0 Поддомен blender-mcp-wiki, Pages вместо Workers, Shiki, теги, CI

### Changed
- **Хостинг пересмотрен: Cloudflare Pages, не Workers.** Первая версия выбрала
  Workers со статическими ассетами, и это было неверно для этой задачи: цель —
  кастомный hostname, чью apex-зону обслуживает **Timeweb**, а не Cloudflare.
  Разведка DNS это показала: `refertur.net` → `ns1..ns4.timeweb.*`. У Pages есть
  штатная привязка кастомного домена, и `wrangler pages deploy` — документированный
  путь именно для этого случая. Важное уточнение: отказ `@astrojs/cloudflare` от
  Pages касается **только on-demand рендеринга**; статический вывод адаптера не
  требует вообще, так что ограничение на нас не распространяется. Первое прочтение
  этой заметки как «Pages больше не вариант» было слишком широким (ADR 0005).
- **Домен зафиксирован:** `blender-mcp-wiki.r00m.ru`, проект Pages
  `blender-mcp-wiki` → `blender-mcp-wiki.pages.dev`. `PUBLIC_SITE_URL` больше не
  плейсхолдер, значение по умолчанию в конфиге — рабочий адрес.
- `wrangler.jsonc` переведён на `pages_build_output_dir`, убраны `html_handling`
  и `not_found_handling` (у Pages другой набор семантик), `preflight.mjs` проверяет
  именно Pages-конфигурацию и лимиты.

### Added
- **Shiki 4** — подсветка синтаксиса. Применяется к уже отрендеренному HTML
  регуляркой по `<pre><code class="language-x">`: `marked` экранирует содержимое,
  поэтому совпадение внутри блока кода невозможно. Неизвестный язык откатывается
  к обычному тексту, а не роняет сборку. Проверяется гейтом по артефакту
  (`verify-seo.mjs` §4c), а не логом сборки: Astro пересоздаёт модуль компонента
  на каждую страницу, поэтому «лог один раз» там не работает.
- **`WIKI/scripts/tag_articles.py`** — теги всем оригиналам. У 127 из 182 не было
  ни одного тега, а это выключало `/api/tags`, поиск и подбор связанных статей.
  Теги берутся из заголовка по контролируемому словарю (никогда не выдумываются);
  уже заданные теги не перезаписываются. Скрипт создаёт frontmatter, если его нет,
  и **читает файл обратно** перед тем, как отчитаться об успехе: первая версия
  печатала `[ok]`, ничего не записав.
- **`.github/workflows/validate.yml`** — конвейер и сайт на каждом пуше и PR.
  Ничего не деплоит: деплой остаётся осознанным шагом с учётными данными.
- `web/.env.example` с готовым значением и указанием, где именно создавать CNAME.

### Fixed
- **Гейт врал о 80 файлах.** `quality_report.py` и `validate.py` сравнивали маркеры
  секций регистрозависимо, а bulk-файлы используют `## 🎯 Цель / Goal` и
  `## 🔗 Связи / Links`. Реальных пробелов было **2**, а не 80. Теперь сравнение
  регистронезависимо. `MULTILANG` больше не считается заменой секции связей: это
  таблица языков, а не перекрёстные ссылки, и её принятие за «СВЯЗИ» скрывало 49
  файлов без ссылок вообще.
- **Требование MCP к промптам про CLI.** P29 (batch CLI) и P40 (version control)
  управляются из шелла, а не из MCP-сессии. Критерий «как вызвать» теперь
  принимает и MCP, и блок команд.
- **Ссылки были прозой, а не ссылками.** 154 файла содержали
  `Setup 01 blender-mcp, WF-01, INDEX` — читаемо, но некликабельно и не обходимо
  краулером. Переписаны в настоящие markdown-ссылки, ранжированные по общим
  тегам (алфавитный порядок давал одинаковые `setup_01..05` в каждом файле, что
  не навигация, а шум).
- **19 файлов `references/v1/**` были не видны шести скриптам** из-за
  нерекурсивного `glob("*.md")`: у них не оказалось ни `lang:`, ни `status:`,
  ни `tags:`. Значение `lang` для них подставлялось эвристикой по содержимому.
  Все обходы переведены на `rglob`.
- **Мёртвая ссылка в `llms.txt`:** `/ru/references/text-to-3d` указывала на
  несуществующую страницу. Причина — жёстко зашитый `/ru/` в URL при выборе
  статей из оригиналов **всех** языков; английская статья получала русский адрес.
  Теперь используется `e.url`, а русский приоритет обеспечивается сортировкой.
  Поймал гейт мёртвых ссылок, а не чтение кода.
- **Мусор в тегах:** `tags: [a, b]` давал теги `setup]` и `list[str` — очистка
  срезала `*_\`#`, но не скобки. Теперь скобки отбрасываются в любом месте.
- `preflight.mjs` не разбирал значение `pages_build_output_dir` (кавычки вокруг
  ключа в JSONC) и печатал `?` вместо значения.

### Known
- **DNS остаётся на владельце.** Деплой не делает так, чтобы имя резолвилось:
  нужен CNAME `blender-mcp-wiki → blender-mcp-wiki.pages.dev` в зоне Timeweb. Cloudflare
  покажет `pending` раньше, чем запись появится; статус до проверки `dig` —
  «pending DNS», а не «готово».
- 63 файла остаются `status: stub` — это глубина текста, а не структуры; её
  нельзя закрыть скриптом. 161 перевод помечен `template` и не индексируется.

## [2026-10-01] - 3.0.0 Сайт на Astro + Cloudflare Workers, SEO и ИИ-оптимизация
### Added
- **`web/`** — статический сайт на Astro 7: 916 пререндеренных HTML-страниц,
  5 языков, поиск Pagefind (индекс на сборке), 834 markdown-близнеца.
- **Машиночитаемый слой:** `llms.txt` (спецификация v2), `llms-full.txt`
  (978 КБ, весь корпус), `robots.txt` с 11 поисковыми и 7 обучающими AI-краулерами,
  `rss.xml`. Статьи ссылаются на свой `.md` через
  `<link rel="alternate" type="text/markdown">` и на карту через `rel="describedby"`.
- **SEO:** взаимные hreflang-кластеры (5 языков + x-default) в `<head>` и в
  sitemap, JSON-LD `Article` + `BreadcrumbList` + `FAQPage`, Open Graph + Twitter,
  один `<h1>`, title ≤62 символа, description из текста раздела «Цель».
- **Два независимых гейта:** `web/scripts/verify-seo.mjs` (каждый артефакт) и
  `verify-consistency.mjs` (согласованность артефактов между собой).
  `web/preflight.mjs` — домен, конфиг, лимиты Workers перед деплоем.
- `WIKI/scripts/fix_frontmatter.py`, `fix_lang_frontmatter.py` — лечат данные.
- `SDD/SEO.md`, `SDD/adr/0005-astro-cloudflare-workers-static-assets.md`.
- Сайт встроен в общий пайплайн: `run_all.py` собирает Astro и гоняет SEO-гейты.

### Fixed (найдено гейтами, а не при просмотре)
- **163 коллизии URL:** русский оригинал и `multilang/ru/…` давали один адрес;
  вторая копия перебивала первую и получала `noindex`. Shadow-зеркала больше не
  публикуются.
- **Русские статьи публиковались под `/en/`:** `build_database.py` перезаписывал
  объявленный в frontmatter `lang` догадкой. Приоритет исправлен:
  путь → frontmatter → детектор.
- **Терялся frontmatter у 538 файлов:** `tags: **, 8b7355` в YAML — `*` это алиас,
  PyYAML падал, а `except: pass` молча выбрасывал метаданные. Строка `tags:`
  убрана как производная (её и так перезаписывает разбор тела).
- **Страницы и sitemap рекламировали разные домены:** origin был константой в
  layout и env-переменной в конфиге. Теперь один источник — `src/lib/site-url.ts`.
- **Canonical у всех зеркал был самореферентным:** layout считал `url` сам, а
  `buildSeo()` не использовался.
- **Фильтр sitemap выкидывал 163 индексируемые страницы:** shadow-путь совпадает
  с путём оригинала, и его нельзя помечать noindex.
- hreflang был в подчёркнутом виде (`ru_RU`) вместо BCP-47 (`ru-RU`).
- `/404.html` отдавал 307: добавлен `html_handling: "drop-trailing-slash"`.
- Инлайн CSS увеличил gzip с 3.8 до 6.1 МБ — откачено, решение зафиксировано.

### Changed
- Хостинг: **Cloudflare Workers со статическими ассетами**, не Pages — Cloudflare
  помечает Pages как legacy, а `@astrojs/cloudflare` с v13 его не поддерживает.
- `Article` вместо `TechArticle`: Google принимает только Article / NewsArticle /
  BlogPosting. `meta keywords` не выводится — на ранжирование не влияет.

### Known
- `PUBLIC_SITE_URL` обязателен для деплоя (значение в конфиге — плейсхолдер).
- `/og-default.png` не создан: OG-ссылки ведут на несуществующий файл.
- 80 файлов с пробелами в структуре, 63 `status: stub` — см. `WIKI/quality_report.md`.

## [2026-09-28] - 2.3.0 Инженерный харденинг: API, тесты, оркестратор, инварианты, документация
### Added
- `scripts/run_all.py` — весь пайплайн одной командой с гейтами и таймингами (`--fast/--skip-tests/--step`).
- `scripts/test_wiki.py` — 22 теста (unittest): парсинг frontmatter/тегов/ID, инварианты БД,
  зеркала переводов, артефакты сайта, HTTP-контракт API на случайном порту.
- Документация: `SDD/ARCHITECTURE.md`, `SDD/SCHEMA.md`, `SDD/API.md`, `SDD/adr/0001..0004`,
  `WIKI/CONTRIBUTING.md`, `WIKI/templates/{prompt,setup,workflow,case}.md`, `.gitignore`.
- API: `/api/version`, `/api/openapi.json`, явный флаг усечения `truncated`/`total_chars`,
  предрасчётный граф из `db/graph.json`, фильтры `lang`/`category` в `/api/graph`.
- Валидатор: секция 7 (meta.json + чанки против БД, позиции графа), 11 (осиротевшие переводы),
  12 (числа SPEC против БД), 13 (конформанс шаблонам, гейт по `--strict`).

### Fixed
- **API парсил 9.4 МБ JSON на каждый запрос** → кэш в памяти с перечитом по mtime.
- API был однопоточным: долгий запрос на статику блокировал `/api/*` → `ThreadingHTTPServer`.
- Нет `ETag`/`Cache-Control` → браузер каждый раз тянул 2.6 МБ чанков → ETag + 304 + `max-age=300`.
- `full_content` обрезался до 30 000 символов молча → теперь `truncated`/`truncated_at`/`total_chars`.
- `GET /api/export` менял состояние (писал файлы) → перенесён на POST, GET отдаёт 405.
- `/api/graph` игнорировал `limit` и считал связи заново → использует `db/graph.json` с позициями.
- Занятый порт давал трейсбек → понятное сообщение и код выхода 2.
- Удалено 5 осиротевших зеркал `multilang/*/prompts/01_primitive_creation.md` (побайтовые дубли
  P01 после переименования оригинала; попадали в БД/сайт/API как отдельные статьи).
- В оригинале P01 исправлены 2 ссылки на удалённое имя файла.
- `validate.py` не проверял `site/data/meta.json` и `chunks/*` — то есть артефакты, которые
  реально грузит сайт после чанкинга.
- SDD/SPEC.md содержал прямое противоречие: P41–P50 значились и в scope, и в «не-целях».
- `validate.py` **падал с UnicodeEncodeError** на консоли без UTF-8 (cp1251/cp1252) — валидатор,
  который не может напечатать результат, бесполезен. Добавлен `reconfigure(encoding="utf-8")`
  в `validate.py`, `test_wiki.py`, `run_all.py`.
- Шаблоны в `WIKI/templates/` ломали §9 (проверка ссылок) плейсхолдерами вида `./xx_slug.md` →
  исключены из скана ссылок, как и зеркала-переводы.
- `run_all.py` рапортовал `PIPELINE GREEN`, хотя упавший шаг `build_index.py` не считался гейтом
  → `build_index` повышен до гейта (ошибка была поймана только потому, что вывод показался вручную).

### Added (продолжение)
- `scripts/quality_report.py` + `WIKI/quality_report.md` — находки конформанса шаблонам
  превращены в отслеживаемый бэклог вместо строчки в логе. Сейчас **80 файлов** с пробелами.

### Changed
- **Ломающее изменение API:** удалён `GET /api/translate`. Он был словарной подстановкой по
  разделу `SEC_HEAD`, а не переводом; потребителей не имел. Контракт: 1.1.
- `SPEC.md` переписан по фактическим числам (997 записей, 41 full / 63 stub, 21 human-перевод),
  §2 теперь проверяется гейтом.
- `SDD/README.md` — Environment, быстрый старт, порядок сборки, правила, E9.

### Known
- `PUBLIC_SITE_URL` обязателен для деплоя; в конфиге стоит плейсхолдер
  `blender-ai-wiki.pages.dev`. Настоящий домен — после первого `wrangler deploy`.
- PyYAML — единственная внешняя зависимость Python, нигде не объявлена
  (`pip install pyyaml`); фолбэк-парсер frontmatter реализован и покрыт тестом,
  сверяющим его вывод с PyYAML на всех 815 реальных блоках.
- Домен, CI, объём человеческих переводов, глубина содержания — открытые вопросы
  (`SPEC.md` §6). Контроль версий закрыт: репозиторий под git, 1090 файлов.

## [2026-09-28] - Blender live: HDRI studio task done
### Done
- Blender 5.2.1 LTS доступен via MCP (addon 1.6/protocol 5 vs expected 9 — `search_polyhaven_assets` сломан из-за расхождения версий, задокументировано).
- Задача «HDRI studio 2k как world» выполнена обходным путём: `studio_small_09_2k.hdr` с API Poly Haven скачан через urllib в Blender и назначен через Environment Texture ноды (поиск по типу, не по имени). Проверено: world=World, env_image на месте + скриншот viewport.
- Рекомендация: обновить аддон `uvx mcp-for-blender install-addon` + restart Blender для протокола 9.

## [2026-09-25] - E8: P41–P50, топ-15 upgrade, чанки сайта, переводы+12
### Added
- Промпты P41–P50 full (displacement, portals/caustics, camera switching, mocap retarget, GN simulation, UDIM, Alembic, Eevee-vs-Cycles, farm submit, turntable QA). Scope: P01–P50.
- Топ-15 stub→full (`upgrade_top15.py`): setups 09/11/12/13/14/18/23/30/44/56, wf 04/05/06/08, case_08.
- Human-переводы +12 (`gen_human12a/b`): setup_02, wf_02, P02, P09 → es/de/zh.
- Зеркала P16–P50 во всех языках (паритет 164/язык).
- Сайт: `data/meta.json` + `data/chunks/entries_{cat}.json` (14 чанков), ленивая загрузка в `app.js`.
- Граф: предрасчёт позиций в `build_graph.py`, `graph.html` без force-layout.
- `scripts/wiki_const.HUMAN_MIRRORS` — единый источник для mark_stubs/validate.
### Fixed
- SPEC scope обновлён (P01–P50).
### Status
- Blender: ретест ниже. DB/validate — в финальной проверке.

## [2026-09-24] - Full-scan cleanup: misc dupes, links, tags
### Fixed
- Удалены 25 дублей `multilang/*/misc/` (проверено `check_misc.py`: orphans=0).
- Починены битые ссылки (`fix_links.py`, 29 файлов): case_02 → `../prompts/`, wf_01/setup_01 → `references/v1`, wf_04 → setup_30, P07 → P25, P08 → `./10_node_groups`, v1-наследие → `scene-building.md`.
- Frontmatter добавлен в 6 legacy-файлов (`translation: legacy`).
- Теги: фильтр мусора (hex-цвета, `**`, цифры) — top-теги чистые.
- `validate.py` переведён на full-scan: все ссылки (кроме шаблонных зеркал), дубли ID, пустые тела, мусор в тегах.
- `mark_stubs.py` идемпотентен (уважает существующий `translation`).
- Пересобраны DB (817), graph (817/901), site/data, INDEX, crossref, экспорты 4/4.
- `validate.py` → RESULT: OK.
### Status
- Scope: P01–P40 full. DB 817 entries (было 842: −25 misc-дублей).

## [2026-09-24] - Full pass: P01 parity, DB 842, site+API verified
### Fixed
- Multilang паритет: `01_primitive_creation.md` добавлен в es/de/zh (было 133, стало 134 везде).
- Frontmatter id в 3 новых файлах приведён к имени файла.
- `scripts/README.md`: добавлены `check_missing.py`, `rebuild_crossref.py`, `upgrade_top10.py`.
- Пересобраны DB (842 entries), graph (817 nodes / 1001 links), site/data, INDEX, crossref, экспорты 4/4.
- `validate.py` → RESULT: OK. API health/search/list/entry + `site/graph.html` (200) проверены.
### Status
- Blender живой тест: процесс не запущен, `:9876 ConnectionRefused` — задача ждёт запущенного Blender с MCP Server (инструкция в `setups/setup_01`).
- Scope: P01–P40 full (подтверждено validate: nums 1–40).

## [2026-09-24] - SDD Release: P31–P40, site v2, 5-lang, DB 839
### Added
- Prompts P16–P20 (animation), P21–P30 (physics/GN/MCP), P31–P40 (render/lighting/camera/MCP/pipeline) — full files, total prompts = 40.
- Setups 09–60 (bulk) + top-10 upgraded to full (ComfyUI, Tripo, Meshy, Flamenco, ambientCG, WF/Case addenda).
- Workflows WF 01–28, Cases 01–16.
- Multilang en/ru/es/de/zh (human: setup_01 es/de/zh, wf_01 es/de/zh, P01 es/de/zh; rest: header+full body template).
- Site v2: `site/` (index, graph.html, markdown renderer, deep-link `#entry=`), `site/data` (DB, index, graph, sitemap, langs).
- API: health/stats/tags/list/entry/search/export/translate/graph/rebuild (+ sitemap, full_content in entry).
- Scripts: validate.py, build_database/graph/index/site, bulk_multilang, export_all, rebuild_crossref, upgrade_top10, gen_p16_p20, gen_p21_p30.
- SDD/: README, SPEC (scope P01–P40 full), TECH_DESIGN.
- Visuals: `visuals/diagrams/mcp_architecture.svg`, `prompt_anatomy.svg`.
- Root v1 merged to `WIKI/references/v1/`, root dupes removed, installers → `archive/`.
### Fixed
- 3 broken links (P07→P25, P08→P10, setup_01→references/v1).
- Multilang ID collisions (`id__lang` + `orig_id`), language detection priority.
- cp1251 console confusion documented in `scripts/README.md`.
### Scope note
- Scope fixed: P01–P40 full. P41–P50 postponed (old "50 prompts" mentions cleaned; SPEC documents this).

## [2026-09-12] - Initial Setup & Documentation

### Added
- **Blender 4.2.3** downloaded (MSI + portable ZIP) to `C:\BLENDER ai\`
- **GenesisCore** addon downloaded from GitHub (ZIP)
- **Complete wiki documentation** structure created at `C:\BLENDER ai\`

### Documentation Created

#### Addons
- `addons/genesiscore.md` - GenesisCore overview & usage
- `addons/genesiscore-full.md` - Complete GenesisCore deep dive (source code analysis)
- `addons/blender-mcp.md` - blender-mcp overview & usage  
- `addons/blender-mcp-full.md` - Complete blender-mcp deep dive (server + addon source)
- `addons/dream-textures.md` - Dream Textures overview
- `addons/dream-textures-full.md` - Complete Dream Textures wiki (Setup, Image Gen, Projection, Inpaint, Render Engine)

#### MCP Protocol
- `mcp/architecture.md` - MCP architecture for Blender, both implementations compared
- `mcp/setup-guide.md` - Installation prerequisites (in guides/installation.md)
- `mcp/clients.md` - Client configs (OpenCode, Claude, Cursor, Codex, Docker)
- `mcp/server-api.md` - Server tool reference

#### Guides
- `guides/installation.md` - Complete step-by-step install (uv, Blender, addons, MCP, API keys)
- `guides/prompting.md` - Effective AI prompting patterns, templates, cheat sheets
- `guides/workflows.md` - Production workflows index
- `guides/troubleshooting.md` - Common issues & fixes

#### Blender API
- `api/blender-api.md` - Complete bpy reference (objects, mesh, materials, nodes, modifiers, animation, geo nodes, render, import/export)

#### Workflows
- `workflows/scene-building.md` - 9 production pipelines (Text-to-3D, Texture Gen, Asset Assembly, AI 3D Gen, Geo Nodes, Animation, Optimization, Batch, Version Control)

#### Index
- `INDEX.md` - Master navigation with comparison matrix, quick start, file index

### Infrastructure
- Consolidated all files into single `C:\BLENDER ai\` directory
- Wiki structure: addons/, mcp/, guides/, api/, workflows/, references/

---

## Next Steps (Pending)

### Immediate
- [ ] Install Blender MSI (run as admin)
- [ ] Install GenesisCore addon via Blender Preferences
- [ ] Install Dream Textures addon (download latest release)
- [ ] Run `uvx blender-mcp install-addon`
- [ ] Configure OpenRouter API key in GenesisCore
- [ ] Start MCP servers and test

### Short-term
- [ ] Test GenesisCore chat with DeepSeek/Qwen
- [ ] Test blender-mcp with OpenCode
- [ ] Test Dream Textures texture generation
- [ ] Configure Poly Pizza / Sketchfab API keys
- [ ] Try Hyper3D / Hunyuan3D generation

### Long-term
- [ ] Local Text-to-3D (TripoSR/MeshGPT)
- [ ] Geometry Nodes automation scripts
- [ ] Custom tool development for GenesisCore
- [ ] Batch rendering pipeline

---

## File Inventory

### Downloaded Assets
```
C:\BLENDER ai\
├── blender-4.2.3-windows-x64.msi      (160 MB) - Blender installer
├── blender-4.2.3-windows-x64.zip      (271 MB) - Portable Blender
├── addons\GenesisCore-main.zip        (50 KB)  - GenesisCore addon source
```

### Documentation (16 files, ~400 KB)
```
addons/ (6 files)
mcp/ (4 files)
guides/ (4 files)
api/ (1 file)
workflows/ (1 file)
INDEX.md, CHANGELOG.md
```