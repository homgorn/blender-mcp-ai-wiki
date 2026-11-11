# Спрос и E-E-A-T — что Google и llms.txt говорят нам

Собрано 2026-11-12 из первичных источников.

## Google: people-first content и E-E-A-T (developers.google.com, в этой сессии)

- Google явно относится к массовому AI-контенту через призму **"head value of content"**: effort, originality, accuracy. Прямая цитата из документа: «Conversely, automatically generating pages from feeds or using generative AI to produce large amounts of text without manual oversight or curation represents little to no effort.»
- На наш корпус это давит так: у нас 222 статьи, все AI-assisted, и **ни у одной нет видимой подписи автора**.
- «Who/How/Why»: Google требует, чтобы было очевидно, кто создал контент («Is it self-evident to your visitors who authored your content?»), как он создан (раскрытие роли автоматизации) и зачем (для людей, а не для поискового трафика).
- Мы удовлетворяем «How» частично: CHANGELOG честно говорит об AI-assisted переводах с `translation: ai`. Но читатель статьи об этом не видит — разметка `<meta generator="Astro">` у нас есть, disclosure для статей нет.
- **Вывод:** нужна страница «Как создаётся эта база знаний» + подпись на каждой статье (псевдоним владения, например «команда Blender MCP Wiki» со ссылкой на репозиторий) + блок «Методология» в каждой статье или хотя бы в референсах.

## llms.txt v2 (llmstxt.org, изменён 2026-08-10)

- Стандарт **AI-лабораторий**: OpenAI, Anthropic, Gemini публикуют llms.txt для своих dev-docs; Chrome Lighthouse проверяет его как часть agentic browsing; более 1000 сайтов публикуют. Наше соответствие формату v2 проверено по тексту спецификации 2026-08-10:
  - H1 + blockquote — есть;
  - `## Section` со списками ссылок + заметки — есть;
  - `.md` у каждой страницы + `rel=alternate` + `rel=describedby` — есть;
  - заголовок `Link:` не используется (Cloudflare Pages не даёт кастомные заголовки ответа?) — надо проверить `_headers` поддержку `Link:`; Cook: `_headers` в Cloudflare Pages поддерживает только ответные заголовки, `Link:` можно добавить. Это единственое расхождение.
- Как используется: **для inference**, не для обучения. Значит, наш llms.txt — это API для агентов, не SEO-актив.

## schema.org TechArticle

- Google показывает ровно 10K–100K доменов, использующих TechArticle, по данным за август 2026. Мы входим в эту группу — это нормальная, но не уникальная практика.
- Google (по данным TechArticle docs) принимает TechArticle как подтип Article для Article rich results.

## 0 измерения спроса — важная деклариция

Мы **не знаем** поисковый спрос на bpy/MCP-темы. `websearch` в этой среде возвращает полные отрицательные ответы (0 результатов), Google Trends/keyword-инструменты недоступны без ключей. Поэтому все приоритеты спроса — **выводы из косвенных данных**:
- 256 репозиториев на GitHub по запросу blender+mcp, из них 20+ > 100 звёзд (измерено);
- наличие Awesome-списков и use-case подборок (confirm receipt);
- 57 открытых issue у ahujasid/mcp-for-blender — энергия в issues.

**Рекомендация:** собрать хотя бы базовые сигналы до выбора следующего приоритета: Search Console (если домен верифицирован), stars tracking, ответы на Reddit/Discord, ручная проверка автодополнения по запросам «blender mcp», «blender ai agent», «blender python automation» в браузере.

## Помечено как "не подтверждено"

- Число ссылок на наш сайт в чужих документах (не измерено).
- Ранжирование в Google (поисковая консоль недоступна без авторизации).
- Доля AI-generated traffic (нет аналитики — мы её сознательно не ставим на статический сайт? SPEC не запрещает).