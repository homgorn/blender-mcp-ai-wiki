/**
 * Single source of truth for site-wide constants.
 * If the Cloudflare Pages domain changes, change it in astro.config.mjs AND here.
 */
import { SITE_URL } from './site-url';

export const SITE_NAME = 'Blender AI Wiki';
export const SITE_NAME_RU = 'База знаний Blender + MCP + AI';
export { SITE_URL };
export const TWITTER_HANDLE = '@blenderaiwiki';

export const LANGS = ['ru', 'en', 'es', 'de', 'zh'] as const;
export type Lang = (typeof LANGS)[number];

export const DEFAULT_LANG: Lang = 'ru';

export const LANG_META: Record<Lang, { label: string; native: string; locale: string; ogLocale: string; dir: 'ltr' | 'rtl' }> = {
  ru: { label: 'Russian', native: 'Русский', locale: 'ru-RU', ogLocale: 'ru_RU', dir: 'ltr' },
  en: { label: 'English', native: 'English', locale: 'en-US', ogLocale: 'en_US', dir: 'ltr' },
  es: { label: 'Spanish', native: 'Español', locale: 'es-ES', ogLocale: 'es_ES', dir: 'ltr' },
  de: { label: 'German', native: 'Deutsch', locale: 'de-DE', ogLocale: 'de_DE', dir: 'ltr' },
  zh: { label: 'Chinese', native: '中文', locale: 'zh-CN', ogLocale: 'zh_CN', dir: 'ltr' },
};

export const CATEGORIES = ['prompts', 'setups', 'workflows', 'cases', 'references'] as const;
export type Category = (typeof CATEGORIES)[number];

export const CATEGORY_META: Record<string, { ru: string; en: string; icon: string; blurbRu: string; blurbEn: string }> = {
  prompts: { ru: 'Промпты', en: 'Prompts', icon: '📝', blurbRu: 'Готовые промпты и bpy-скрипты для агентов', blurbEn: 'Ready-made prompts and bpy scripts for agents' },
  setups: { ru: 'Сетапы', en: 'Setups', icon: '⚙️', blurbRu: 'Пошаговая настройка инструментов и пайплайнов', blurbEn: 'Step-by-step tool and pipeline configuration' },
  workflows: { ru: 'Воркфлоу', en: 'Workflows', icon: '🔄', blurbRu: 'Сквозные процессы от входа до результата', blurbEn: 'End-to-end processes from input to result' },
  cases: { ru: 'Кейсы', en: 'Cases', icon: '📁', blurbRu: 'Разобранные проекты с решениями и подводными камнями', blurbEn: 'Worked projects with decisions and pitfalls' },
  references: { ru: 'Референсы', en: 'References', icon: '📚', blurbRu: 'Справочные данные по API, форматам, интеграциям', blurbEn: 'Reference data on APIs, formats, integrations' },
  mcp: { ru: 'MCP', en: 'MCP', icon: '🔌', blurbRu: 'MCP-протокол и инструменты', blurbEn: 'MCP protocol and tools' },
  mcp_advanced: { ru: 'MCP (продвинутый)', en: 'MCP (advanced)', icon: '⚡', blurbRu: 'Продвинутые паттерны MCP', blurbEn: 'Advanced MCP patterns' },
  integrations: { ru: 'Интеграции', en: 'Integrations', icon: '🧩', blurbRu: 'Связки с внешним софтом', blurbEn: 'Third-party integrations' },
  simulation: { ru: 'Симуляция', en: 'Simulation', icon: '🎲', blurbRu: 'Физика, кэш, симуляции', blurbEn: 'Physics, cache, simulations' },
  realtime: { ru: 'Real-time', en: 'Real-time', icon: '⏱', blurbRu: 'Real-time и интерактив', blurbEn: 'Real-time and interactive' },
  usd: { ru: 'USD', en: 'USD', icon: '📦', blurbRu: 'OpenUSD и пайплайны ассетов', blurbEn: 'OpenUSD and asset pipelines' },
  pipeline: { ru: 'Пайплайн', en: 'Pipeline', icon: '🏗', blurbRu: 'Оркестрация продакшна', blurbEn: 'Production orchestration' },
  version_control: { ru: 'Версии', en: 'Versioning', icon: '🗂', blurbRu: 'Контроль версий ассетов', blurbEn: 'Asset versioning' },
  color: { ru: 'Цвет', en: 'Color', icon: '🎨', blurbRu: 'Цветовые пайплайны', blurbEn: 'Color pipelines' },
  performance: { ru: 'Производительность', en: 'Performance', icon: '⚡', blurbRu: 'Оптимизация и бюджеты', blurbEn: 'Optimization and budgets' },
  testing: { ru: 'Тестирование', en: 'Testing', icon: '✅', blurbRu: 'Тесты и валидация ассетов', blurbEn: 'Asset tests and validation' },
  security: { ru: 'Безопасность', en: 'Security', icon: '🛡', blurbRu: 'Безопасность пайплайна', blurbEn: 'Pipeline security' },
  ml_ai: { ru: 'ML/AI', en: 'ML/AI', icon: '🧠', blurbRu: 'Машинное обучение в Blender', blurbEn: 'Machine learning in Blender' },
  accessibility: { ru: 'Доступность', en: 'Accessibility', icon: '♿', blurbRu: 'Доступность контента', blurbEn: 'Content accessibility' },
  collaboration: { ru: 'Командная работа', en: 'Collaboration', icon: '👥', blurbRu: 'Командные процессы', blurbEn: 'Team processes' },
  visuals: { ru: 'Визуал', en: 'Visuals', icon: '🖼', blurbRu: 'Визуальные материалы', blurbEn: 'Visual material' },
};
