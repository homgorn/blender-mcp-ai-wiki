# SEO и оптимизация под языковые модели

Обновлено: 2026-10-01. Проверяется гейтами `web/scripts/verify-seo.mjs`
(каждый артефакт отдельно) и `web/scripts/verify-consistency.mjs` (согласованность).

## 1. Текущее состояние (замерено, не заявлено)

| Метрика | Значение | Проверяет |
|---------|----------|-----------|
| Опубликовано HTML-страниц | 916 | build |
| Индексируемых (`index, follow`) | 203 | `verify-consistency` §1 |
| `noindex`-зеркал с canonical на оригинал | 631 | `verify-seo` §3 |
| Shadow-зеркал (не публикуются) | 163 | `verify-consistency` |
| URL в sitemap | 279 | `verify-seo` §4 |
| Страниц в индексе Pagefind | 834 | build |
| `.md`-близнецов | 834 | `verify-consistency` §5 |
| Битых внутренних ссылок | 0 | `verify-seo` §6 |
| Доля HTML в gzip | 3.78 МБ | замер |

## 2. Поисковики

**Реализовано:**
- `rel="canonical"` — на себя у индексируемых, на оригинал у зеркал.
- Взаимные hreflang-кластеры: 5 языков + `x-default`, и в `<head>`
  (`<link rel="alternate" hreflang>`), и через `xhtml:link` в sitemap.
  Оба механизма нужны — это разные вещи, sitemap их не заменяет.
- JSON-LD: `Article` + `BreadcrumbList` (+ `FAQPage`, где есть раздел цели).
- Open Graph + Twitter Card, `og:locale` в подчёркнутом виде (`ru_RU`),
  hreflang в дефисном (`ru-RU`) — это разные спецификации.
- Один `<h1>` на страницу: заголовок рендерит layout, дублирующий `#` из
  markdown вырезается.
- `title` ≤ 62 символа, `description` — из текста раздела «Цель», а не из
  метаданных статьи.
- `llms.txt` и `robots.txt` в корне, `<link rel="sitemap">` в `<head>`.
- Статический HTML: контент в разметке, без JS-зависимости.

**Намеренно не сделано и почему:**
- `meta keywords` — Google: «not used by Google Search, and it has no effect on
  indexing and ranking at all».
- `TechArticle` — валидный schema.org, но Google принимает только
  `Article` / `NewsArticle` / `BlogPosting`. Используется `Article`.
- `HowTo` — убран из галереи Google; наш контент и так покрыт `Article`.
- `og:image` указывает на `/og-default.png`, которого пока нет → следующая задача.

## 3. Языковые модели

Спецификация [`llms.txt` v2](https://llmstxt.org/) (ревизия 2026-08-10).

| Артефакт | Размер | Назначение |
|----------|--------|-----------|
| `/llms.txt` | 4 КБ | карта сайта: категории + 12 статей с кодом + служебные ссылки |
| `/llms-full.txt` | 978 КБ | весь корпус, 203 документа, разделены `<!-- source: -->` |
| `/ru/prompts/41-….md` | 4 КБ | markdown-близнец статьи по тому же URL |

- Страница ссылается на свой `.md` через
  `<link rel="alternate" type="text/markdown">` и на карту через
  `rel="describedby"`. В `public/_headers` то же продублировано заголовком
  `Link:` — так agents получают подсказку и на не-HTML-ассетах.
- `robots.txt` перечисляет 11 поисковых AI-краулеров и 7 обучающих
  (`GPTBot`, `ClaudeBot`, `CCBot`, `Google-Extended`, `Amazonbot`,
  `meta-externalagent`, `Applebot-Extended`) — все разрешены: база открытая.
  Как закрыть обучение, не потеряв цитируемость, — `ARCHITECTURE.md` §7.
- `Content-Type: text/markdown` для `.md` подтверждён замером через
  `wrangler dev` (Cloudflare назначает по расширению).

**Честная граница:** Google Search **игнорирует** `llms.txt` — это позиция его
AI optimization guide. Файл нужен LLM-агентам и цитированию в ответах, а не
ранжированию в Google. Не рассчитывайте на него как на SEO-фактор.

## 4. Домен

`PUBLIC_SITE_URL` — единственный источник origin (`web/src/lib/site-url.ts`,
через `import.meta.env.SITE`). Попадает в canonical, hreflang, OG, sitemap,
robots, llms.txt и RSS.

Сборка без `https://`-origin невозможна для деплоя: `run_all.py` и
`web/preflight.mjs` её останавливают, `verify-seo.mjs` падает на `localhost`.

> Origin по умолчанию — `https://bender-skills.refertur.net`, это и есть рабочий
> домен, а не плейсхолдер. Он задан в `web/astro.config.mjs` (единый источник) и
> дублируется в `PUBLIC_SITE_URL` для сборки. Менять нужно в обоих местах, либо
> только в переменной окружения для локального прогона.
>
> Деплой идёт в Cloudflare Pages, имя проекта `bender-skills`, поэтому целевой адрес
> Pages — `bender-skills.pages.dev`. Apex-зону `refertur.net` обслуживает **Timeweb**,
> а не регистратор, поэтому кастомный домен заработает только после CNAME
> `bender-skills → bender-skills.pages.dev` в панели Timeweb. Cloudflare покажет
> домен как `pending` раньше, чем запись появится, — это не «задеплоено».

## 5. Что измерять после публикации

| Метрика | Где | Ожидание |
|---------|-----|----------|
| Индексация | Google Search Console → «Покрытие» | 203 страницы, без «Просканировано, но не проиндексировано» из-за дублей |
| Ошибки краулера | Search Console → «Страницы» | 0 битых ссылок (проверено на сборке) |
| Core Web Vitals | Search Console → «Основные интернет-показатели» | CLS/LCP в норме (статика, CSS один файл) |
| AI-цитируемость | `https://<домен>/llms-full.txt` в RAG-пайплайне | статьи находятся по описанию задачи |
| Cloudflare | Workers → Analytics | 404 только на реально несуществующих URL |

## 6. Долг

| Объём | Задача | Приоритет |
|-------|--------|-----------|
| 1 файл | `/og-default.png` — сейчас OG-ссылка ведёт на несуществующий файл | высокий (соцсети) |
| 80 файлов | пробелы в структуре статей (`WIKI/quality_report.md`) | средний |
| 63 файла | `status: stub` | средний |
| 1 файл | подсветка синтаксиса через Shiki | низкий (на размер, не на SEO) |
| 175 файлов | человеческий перевод вместо `template` | низкий |
