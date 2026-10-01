# Blender AI Wiki — web

Статический сайт базы знаний. Astro 7 → Cloudflare Workers (static assets).
Без рантайм-сервера, без БД, без внешних зависимостей на этапе выполнения.

## Что здесь лежит

```
web/
├─ astro.config.mjs        site, sitemap, языки, noindex-правило
├─ wrangler.jsonc          деплой на Workers (static assets)
├─ public/_headers         security + cache + CSP + Link: rel=describedby
├─ pagefind.config.json    индекс поиска (root_selector = [data-pagefind-body])
└─ src/
   ├─ lib/site-url.ts      ЕДИНСТВЕННЫЙ источник канонического домена
   ├─ lib/site.ts          константы: языки, категории, названия
   ├─ lib/content.ts       чтение БД, классификация страниц, URL, ссылки
   ├─ lib/seo.ts           buildSeo (canonical/robots) + JSON-LD
   ├─ layouts/BaseLayout   весь <head>: meta, OG, hreflang, JSON-LD, llms.txt
   ├─ components/          Prose (markdown→HTML), EntryCard, LangSwitch
   └─ pages/               /, /{lang}, /{lang}/{cat}, /{lang}/{cat}/{slug}
scripts/
├─ generate-agent-files.mjs  llms.txt, llms-full.txt, robots.txt, rss.xml, .md-близнецы
├─ verify-seo.mjs            гейт: head-теги, JSON-LD, hreflang, sitemap, llms.txt
└─ verify-consistency.mjs    гейт: артефакты согласованы между собой
```

## Команды

```powershell
npm install

# локальная разработка
npm run dev

# полный цикл: сборка → агентские файлы → индекс поиска → 2 гейта
$env:PUBLIC_SITE_URL="https://<ваш-домен>"
npm run all

# отдельно
npm run build          # astro build
npm run agents         # llms.txt / llms-full.txt / robots.txt / rss.xml / .md
npm run index          # pagefind --site dist
npm run verify         # оба гейта
```

## Перед деплоем — обязательно

`PUBLIC_SITE_URL` **обязателен**. Он попадает в canonical, hreflang, Open Graph,
sitemap и robots.txt. Сборка с `localhost` проходит гейты, но `verify-seo` её
заваливает: нельзя публиковать сайт, у которого канонический адрес — `localhost`.

```powershell
npx wrangler login       # один раз
$env:PUBLIC_SITE_URL="https://blender-ai-wiki.<subdomain>.workers.dev"
npm run deploy           # build + verify + wrangler deploy
```

## Правило дедупликации (обязательно к соблюдению)

Одна и та же статья существует в 5 языках. Из этого следуют три состояния,
и правило применяется **везде одинаково** — в `content.ts`, `astro.config.mjs`
и обоих гейтах. Расхождение правил = страницы, которые выпадают из sitemap
или получают неверный canonical (это уже случалось).

| Состояние | Что это | Публикуется | robots | canonical | В sitemap |
|---|---|---|---|---|---|
| **indexable** | оригинал или перевод `human` | да | `index, follow` | на себя | да |
| **duplicate** | зеркало `template`/`legacy` | да | `noindex, follow` | на оригинал | нет |
| **shadow** | язык зеркала == язык оригинала | **нет** | — | — | путь принадлежит оригиналу |

Shadow-зеркала возникают потому, что русский оригинал и `multilang/ru/…`
дают один и тот же URL (163 коллизии). Публиковать оба нельзя: вторая
копия перебьёт первую и получит `noindex`.

## SEO и ИИ-оптимизация

**Для поисковиков:** canonical, взаимные hreflang-кластеры (5 языков + x-default)
и в `<head>`, и через `xhtml:link` в sitemap, JSON-LD `Article` + `BreadcrumbList`,
Open Graph + Twitter, один `<h1>` на страницу, статический HTML без JS-зависимости,
короткий title (≤62 символа) и осмысленный description.

> `Article`, а не `TechArticle`: Google принимает только Article / NewsArticle /
> BlogPosting. `meta keywords` не выводится — Google прямо говорит, что на
> индексацию и ранжирование он не влияет.

**Для языковых моделей:** `llms.txt` (спецификация v2, карта сайта),
`llms-full.txt` (весь корпус, 978 КБ), markdown-близнец каждой статьи по тому
же URL с расширением `.md` (ссылается `rel="alternate" type="text/markdown"`),
`rel="describedby"` на llms.txt, `robots.txt` с явным списком AI-краулеров.

> Честно: **Google Search игнорирует llms.txt** (официальная позиция в его
> AI optimization guide). Это инструмент для LLM-агентов и цитирования
> ответами, а не фактор ранжирования в Google.

## Гейты

`verify-seo.mjs` проверяет каждую страницу и артефакт по отдельности:
заголовки, длины, canonical, robots, OG/Twitter, JSON-LD (парсится как JSON!),
hreflang, наличие `.md`-близнеца, sitemap, llms.txt, битые внутренние ссылки
по всем 916 HTML.

`verify-consistency.mjs` проверяет, что артефакты **согласованы между собой**:
страница не `noindex`, но есть в sitemap; `noindex`-зеркало не попало в
`llms-full.txt` или RSS; sitemap покрывает все индексируемые страницы.

## Известные ограничения

- Синтаксис подсветки кода не подключён (`marked` без Shiki) — блоки кода
  выводятся как `<pre>`. Увеличивает размер страницы, но не влияет на SEO.
- Поиск индексирует только `[data-pagefind-body]` — 834 страницы из 916.
  Категории и поиск не в индексе намеренно.
- `dist/` ≈ 22 МБ (3.8 МБ gzip на HTML). Лимиты Workers: 20 000 файлов и
  25 МБ на файл — у нас 2663 файла, максимум 978 КБ.
