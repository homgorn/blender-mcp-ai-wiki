#!/usr/bin/env node
/**
 * Post-build generator for the machine-readable layer.
 *
 * Why a script instead of Astro endpoints: every .ts file under src/pages/ is
 * parsed as JavaScript in this Astro 7 + Node 22.23 combination (esbuild "Unexpected
 * token" on any type annotation), so endpoints cannot be written there. Generating
 * these artifacts directly is also faster: 997 markdown twins are written with
 * fs.writeFile instead of 997 route compilations, and the output is byte-identical
 * to what the HTML pages advertise via <link rel="alternate" type="text/markdown">.
 *
 * Writes into dist/:
 *   llms.txt                     llmstxt.org v2 map of the site
 *   llms-full.txt                whole corpus, one file
 *   robots.txt                   crawler policy incl. AI bots
 *   rss.xml                      50 most recent articles
 *   {lang}/{cat}/{slug}.md       markdown twin of every article
 *
 * Run:  node scripts/generate-agent-files.mjs
 */
import { readFileSync, writeFileSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..');
const DIST = join(WEB, 'dist');
const DB = join(WEB, '..', 'WIKI', 'db', 'wiki_database.json');

const SITE = (process.env.PUBLIC_SITE_URL || process.env.SITE_URL || 'http://localhost:4321').replace(/\/+$/, '');
const LANGS = ['ru', 'en', 'es', 'de', 'zh'];
const LOCALE = { ru: 'ru-RU', en: 'en-US', es: 'es-ES', de: 'de-DE', zh: 'zh-CN' };
const NATIVE = { ru: 'Русский', en: 'English', es: 'Español', de: 'Deutsch', zh: '中文' };
const CATEGORY_META = {
  prompts: { icon: '📝', ru: 'Промпты', blurb: 'Готовые промпты и bpy-скрипты для агентов' },
  setups: { icon: '⚙️', ru: 'Сетапы', blurb: 'Пошаговая настройка инструментов и пайплайнов' },
  workflows: { icon: '🔄', ru: 'Воркфлоу', blurb: 'Сквозные процессы от входа до результата' },
  cases: { icon: '📁', ru: 'Кейсы', blurb: 'Разобранные проекты с решениями и подводными камнями' },
  references: { icon: '📚', ru: 'Референсы', blurb: 'Справочные данные по API, форматам, интеграциям' },
};

const slugify = (s) => s.toLowerCase().replace(/\.md$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
const stripFm = (md) => md.replace(/^---\n[\s\S]*?\n---\n?/, '').trimStart();
const abs = (p) => (p.startsWith('http') ? p : SITE + p);

const db = JSON.parse(readFileSync(DB, 'utf8'));
const entries = db.entries.map((e) => {
  const m = e.meta;
  const origId = m.orig_id ?? String(m.id).replace(/__[a-z]{2}$/, '');
  return {
    id: m.id,
    origId,
    lang: m.language,
    category: m.category || 'references',
    type: m.type || 'reference',
    title: m.title || origId,
    description: m.description || '',
    difficulty: m.difficulty || 0,
    tags: Array.isArray(m.tags) ? m.tags : [],
    status: m.status,
    translation: m.translation,
    isTranslation: Boolean(m.is_translation),
    wordCount: m.word_count || 0,
    codeBlocks: m.code_blocks || 0,
    updated: m.updated || '',
    body: stripFm(e.full_content || ''),
    url: `/${m.language}/${m.category || 'references'}/${slugify(origId)}`,
  };
});

const originals = entries.filter((e) => !e.isTranslation);
const indexable = (e) => !e.isTranslation || e.translation === 'human';
const write = (rel, body) => {
  const p = join(DIST, rel);
  mkdirSync(dirname(p), { recursive: true });
  writeFileSync(p, body, 'utf8');
  return p;
};

/* ------------------------------------------------- markdown twins (.md) */
let twins = 0;
for (const e of entries) {
  const fm = [
    '---',
    `title: ${JSON.stringify(e.title)}`,
    `id: ${e.id}`,
    `lang: ${e.lang}`,
    `category: ${e.category}`,
    `type: ${e.type}`,
    `difficulty: ${e.difficulty}`,
    `tags: [${e.tags.join(', ')}]`,
    e.status ? `status: ${e.status}` : null,
    e.translation ? `translation: ${e.translation}` : null,
    e.updated ? `updated: ${e.updated.slice(0, 10)}` : null,
    `word_count: ${e.wordCount}`,
    '---',
  ].filter(Boolean).join('\n');
  write(`${e.url}.md`, `${fm}\n\n${e.body.trim()}\n`);
  twins++;
}

/* ------------------------------------------------------------- llms.txt */
{
  const counts = originals.reduce((acc, e) => ((acc[e.category] = (acc[e.category] ?? 0) + 1), acc), {});
  const featured = originals
    .filter((e) => e.difficulty > 0 && e.codeBlocks > 0)
    .sort((a, b) => b.codeBlocks - a.codeBlocks)
    .slice(0, 12);

  const L = [];
  L.push('# Blender AI Wiki');
  L.push('');
  L.push(
    `> Открытая база знаний по Blender, MCP и AI-агентам: ${originals.length} статей — готовые промпты и bpy-скрипты, настройки инструментов, сквозные воркфлоу и разобранные кейсы. Каждая статья имеет markdown-версию по тому же URL с расширением .md.`,
  );
  L.push('');
  L.push(
    'Чтобы прочитать конкретную статью, берите её `.md`-версию: это исходный markdown без навигации и разметки, готовый для RAG и для вставки в контекст модели. Полный корпус — в /llms-full.txt (большой файл, только по запросу).',
  );
  L.push('');
  L.push(`Языки: ${LANGS.map((l) => `${l} (${NATIVE[l]})`).join(', ')}. По умолчанию — русский (/ru).`);
  L.push('');
  L.push('## Категории (начать отсюда)');
  L.push('');
  for (const [cat, n] of Object.entries(counts).sort((a, b) => b[1] - a[1])) {
    const m = CATEGORY_META[cat];
    if (!m) continue;
    L.push(`- [${m.icon} ${m.ru} (${n})](${abs(`/ru/${cat}`)}): ${m.blurb}`);
  }
  L.push('');
  L.push('## Статьи с готовым кодом');
  L.push('');
  for (const e of featured) {
    L.push(`- [${e.title}](${abs(`/ru/${e.category}/${slugify(e.origId)}`)}): ${e.description.slice(0, 160)}`);
  }
  L.push('');
  L.push('## Справочные данные');
  L.push('');
  L.push(`- [RSS](${abs('/rss.xml')}): последние обновления.`);
  L.push(`- [Sitemap](${abs('/sitemap-index.xml')}): полный список индексируемых страниц.`);
  L.push('');
  L.push('## Optional');
  L.push('');
  L.push(`- [Полный корпус одним файлом](${abs('/llms-full.txt')}): все статьи, для офлайн-индексации.`);
  L.push(`- [Выбор языка](${abs('/')}).`);
  L.push('');
  write('llms.txt', L.join('\n'));
}

/* -------------------------------------------------------- llms-full.txt */
{
  const docs = entries
    .filter(indexable)
    .sort((a, b) => a.lang.localeCompare(b.lang) || a.category.localeCompare(b.category) || a.title.localeCompare(b.title));
  const out = [
    `# Blender AI Wiki — полный корпус (${docs.length} документов)`,
    '',
    '> Все индексируемые статьи базы знаний, одним файлом.',
    '> Каждый документ отделён HTML-комментарием с его URL и метаданными.',
    '> Для выборочного чтения используйте /llms.txt.',
    '',
  ];
  for (const e of docs) {
    out.push(`<!-- source: ${abs(e.url)} | id: ${e.id} | lang: ${e.lang} (${LOCALE[e.lang]}) | category: ${e.category} | difficulty: ${e.difficulty} -->`);
    out.push('');
    out.push(`# ${e.title}`);
    out.push('');
    if (e.description) out.push(`> ${e.description}`, '');
    if (e.tags.length) out.push(`Tags: ${e.tags.map((t) => `#${t}`).join(' ')}`);
    out.push('');
    out.push(e.body.trim());
    out.push('', '---', '');
  }
  write('llms-full.txt', out.join('\n'));
}

/* ------------------------------------------------------------ robots.txt */
{
  const RETRIEVAL = ['OAI-SearchBot', 'ChatGPT-User', 'Claude-SearchBot', 'Claude-User',
    'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Meta-WebIndexer',
    'meta-externalfetcher', 'Amzn-SearchBot', 'Applebot'];
  const TRAINING = ['GPTBot', 'ClaudeBot', 'Amazonbot', 'CCBot', 'Bytespider',
    'meta-externalagent', 'Applebot-Extended'];
  const L = [
    '# Blender AI Wiki — база знаний по Blender, MCP и AI-агентам.',
    '#',
    '# Комментарии разрешены, каталог не закрыт. Статьи отдаются статическим HTML',
    '# и дополнительно в markdown по тому же URL (.md) — см. /llms.txt.',
    '',
    'User-agent: *',
    'Allow: /',
    '',
    '# --- AI: поиск и цитирование (разрешены) ---',
  ];
  for (const b of RETRIEVAL) L.push(`User-agent: ${b}`, 'Allow: /', '');
  L.push('# --- AI: обучение моделей (разрешено; см. SDD/ARCHITECTURE.md §8) ---');
  for (const b of TRAINING) L.push(`User-agent: ${b}`, 'Allow: /', '');
  L.push(`Sitemap: ${abs('/sitemap-index.xml')}`, '');
  write('robots.txt', L.join('\n'));
}

/* --------------------------------------------------------------- rss.xml */
{
  const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  // Originals only. Several originals are written in English (references,
  // usd, color, …), so "original" does not mean "Russian" — filter on
  // is_translation, never on language, or English articles would be dropped.
  const items = originals
    .slice()
    .sort((a, b) => (b.updated ?? '').localeCompare(a.updated ?? ''))
    .slice(0, 50)
    .map((e) => [
      '    <item>',
      `      <title>${esc(e.title)}</title>`,
      `      <link>${abs(e.url)}</link>`,
      `      <guid isPermaLink="true">${abs(e.url)}</guid>`,
      e.updated ? `      <pubDate>${new Date(e.updated).toUTCString()}</pubDate>` : '',
      `      <description>${esc(e.description.slice(0, 400))}</description>`,
      `      <category>${esc(e.category)}</category>`,
      '    </item>',
    ].filter(Boolean).join('\n'))
    .join('\n');
  write('rss.xml', [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0">',
    '  <channel>',
    '    <title>Blender AI Wiki</title>',
    '    <link>' + SITE + '</link>',
    '    <description>База знаний по Blender, MCP и AI-агентам</description>',
    '    <language>ru-RU</language>',
    items,
    '  </channel>',
    '</rss>',
    '',
  ].join('\n'));
}

/* ------------------------------------------------------------------ done */
const kb = (p) => Math.round(statSync(join(DIST, p)).size / 1024);
console.log(`OK agent files: md-twins=${twins} llms.txt=${kb('llms.txt')}KB llms-full.txt=${kb('llms-full.txt')}KB robots=${kb('robots.txt')}KB rss=${kb('rss.xml')}KB`);
