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

export const CATEGORY_META: Record<string, { ru: string; en: string; es?: string; de?: string; zh?: string; icon: string; blurbRu: string; blurbEn: string; blurbEs?: string; blurbDe?: string; blurbZh?: string }> = {
  prompts: { ru: 'Промпты', en: 'Prompts', es: 'Prompts', de: 'Prompts', zh: '提示词', icon: '📝', blurbRu: 'Готовые промпты и bpy-скрипты для агентов', blurbEn: 'Ready-made prompts and bpy scripts for agents', blurbEs: 'Prompts y scripts bpy listos para agentes', blurbDe: 'Fertige Prompts und bpy-Skripte für Agenten', blurbZh: '现成的提示词和供智能体使用的 bpy 脚本' },
  setups: { ru: 'Сетапы', en: 'Setups', es: 'Configuraciones', de: 'Setups', zh: '设置', icon: '⚙️', blurbRu: 'Пошаговая настройка инструментов и пайплайнов', blurbEn: 'Step-by-step tool and pipeline configuration', blurbEs: 'Configuración paso a paso de herramientas y pipelines', blurbDe: 'Schrittweise Tool- und Pipeline-Konfiguration', blurbZh: '工具和管线的分步配置' },
  workflows: { ru: 'Воркфлоу', en: 'Workflows', es: 'Flujos de trabajo', de: 'Workflows', zh: '工作流', icon: '🔄', blurbRu: 'Сквозные процессы от входа до результата', blurbEn: 'End-to-end processes from input to result', blurbEs: 'Procesos de extremo a extremo desde la entrada al resultado', blurbDe: 'Ende-zu-Ende-Prozesse von der Eingabe zum Ergebnis', blurbZh: '从输入到结果的端到端流程' },
  cases: { ru: 'Кейсы', en: 'Cases', es: 'Casos', de: 'Cases', zh: '案例', icon: '📁', blurbRu: 'Разобранные проекты с решениями и подводными камнями', blurbEn: 'Worked projects with decisions and pitfalls', blurbEs: 'Proyectos analizados con decisiones y obstáculos', blurbDe: 'Ausgearbeitete Projekte mit Entscheidungen und Fallstricken', blurbZh: '已拆解的项目，包含决策与避坑指南' },
  references: { ru: 'Референсы', en: 'References', es: 'Referencias', de: 'Referenzen', zh: '参考', icon: '📚', blurbRu: 'Справочные данные по API, форматам, интеграциям', blurbEn: 'Reference data on APIs, formats, integrations', blurbEs: 'Datos de referencia sobre APIs, formatos, integraciones', blurbDe: 'Referenzdaten zu APIs, Formaten, Integrationen', blurbZh: '关于 API、格式、集成的参考数据' },
  mcp: { ru: 'MCP', en: 'MCP', es: 'MCP', de: 'MCP', zh: 'MCP', icon: '🔌', blurbRu: 'MCP-протокол и инструменты', blurbEn: 'MCP protocol and tools', blurbEs: 'Protocolo y herramientas MCP', blurbDe: 'MCP-Protokoll und Tools', blurbZh: 'MCP 协议与工具' },
  mcp_advanced: { ru: 'MCP (продвинутый)', en: 'MCP (advanced)', es: 'MCP (avanzado)', de: 'MCP (erweitert)', zh: 'MCP (进阶)', icon: '⚡', blurbRu: 'Продвинутые паттерны MCP', blurbEn: 'Advanced MCP patterns', blurbEs: 'Patrones avanzados de MCP', blurbDe: 'Erweiterte MCP-Muster', blurbZh: 'MCP 进阶模式' },
  integrations: { ru: 'Интеграции', en: 'Integrations', es: 'Integraciones', de: 'Integrationen', zh: '集成', icon: '🧩', blurbRu: 'Связки с внешним софтом', blurbEn: 'Third-party integrations', blurbEs: 'Integraciones con software externo', blurbDe: 'Anbindungen an externe Software', blurbZh: '第三方软件集成' },
  simulation: { ru: 'Симуляция', en: 'Simulation', es: 'Simulación', de: 'Simulation', zh: '仿真', icon: '🎲', blurbRu: 'Физика, кэш, симуляции', blurbEn: 'Physics, cache, simulations', blurbEs: 'Física, caché, simulaciones', blurbDe: 'Physik, Cache, Simulationen', blurbZh: '物理、缓存、仿真' },
  realtime: { ru: 'Real-time', en: 'Real-time', es: 'Tiempo real', de: 'Echtzeit', zh: '实时', icon: '⏱', blurbRu: 'Real-time и интерактив', blurbEn: 'Real-time and interactive', blurbEs: 'Tiempo real e interactivo', blurbDe: 'Echtzeit und Interaktivität', blurbZh: '实时与交互' },
  usd: { ru: 'USD', en: 'USD', es: 'USD', de: 'USD', zh: 'USD', icon: '📦', blurbRu: 'OpenUSD и пайплайны ассетов', blurbEn: 'OpenUSD and asset pipelines', blurbEs: 'OpenUSD y pipelines de assets', blurbDe: 'OpenUSD und Asset-Pipelines', blurbZh: 'OpenUSD 与资产管线' },
  pipeline: { ru: 'Пайплайн', en: 'Pipeline', es: 'Pipeline', de: 'Pipeline', zh: '管线', icon: '🏗', blurbRu: 'Оркестрация продакшна', blurbEn: 'Production orchestration', blurbEs: 'Orquestación de producción', blurbDe: 'Produktionsorchestrierung', blurbZh: '生产编排' },
  version_control: { ru: 'Версии', en: 'Versioning', es: 'Versionado', de: 'Versionierung', zh: '版本控制', icon: '🗂', blurbRu: 'Контроль версий ассетов', blurbEn: 'Asset versioning', blurbEs: 'Versionado de assets', blurbDe: 'Asset-Versionierung', blurbZh: '资产版本控制' },
  color: { ru: 'Цвет', en: 'Color', es: 'Color', de: 'Farbe', zh: '颜色', icon: '🎨', blurbRu: 'Цветовые пайплайны', blurbEn: 'Color pipelines', blurbEs: 'Pipelines de color', blurbDe: 'Farbpipelines', blurbZh: '颜色管线' },
  performance: { ru: 'Производительность', en: 'Performance', es: 'Rendimiento', de: 'Performance', zh: '性能', icon: '⚡', blurbRu: 'Оптимизация и бюджеты', blurbEn: 'Optimization and budgets', blurbEs: 'Optimización y presupuestos', blurbDe: 'Optimierung und Budgets', blurbZh: '优化与预算' },
  testing: { ru: 'Тестирование', en: 'Testing', es: 'Pruebas', de: 'Testing', zh: '测试', icon: '✅', blurbRu: 'Тесты и валидация ассетов', blurbEn: 'Asset tests and validation', blurbEs: 'Pruebas y validación de assets', blurbDe: 'Asset-Tests und Validierung', blurbZh: '资产测试与验证' },
  security: { ru: 'Безопасность', en: 'Security', es: 'Seguridad', de: 'Sicherheit', zh: '安全', icon: '🛡', blurbRu: 'Безопасность пайплайна', blurbEn: 'Pipeline security', blurbEs: 'Seguridad del pipeline', blurbDe: 'Pipeline-Sicherheit', blurbZh: '管线安全' },
  ml_ai: { ru: 'ML/AI', en: 'ML/AI', es: 'ML/IA', de: 'ML/KI', zh: 'ML/AI', icon: '🧠', blurbRu: 'Машинное обучение в Blender', blurbEn: 'Machine learning in Blender', blurbEs: 'Aprendizaje automático en Blender', blurbDe: 'Maschinelles Lernen in Blender', blurbZh: 'Blender 中的机器学习' },
  accessibility: { ru: 'Доступность', en: 'Accessibility', es: 'Accesibilidad', de: 'Barrierefreiheit', zh: '无障碍', icon: '♿', blurbRu: 'Доступность контента', blurbEn: 'Content accessibility', blurbEs: 'Accesibilidad del contenido', blurbDe: 'Inhaltszugänglichkeit', blurbZh: '内容无障碍' },
  collaboration: { ru: 'Командная работа', en: 'Collaboration', es: 'Colaboración', de: 'Zusammenarbeit', zh: '协作', icon: '👥', blurbRu: 'Командные процессы', blurbEn: 'Team processes', blurbEs: 'Procesos de equipo', blurbDe: 'Teamprozesse', blurbZh: '团队流程' },
  visuals: { ru: 'Визуал', en: 'Visuals', es: 'Visuales', de: 'Visuals', zh: '视觉', icon: '🖼', blurbRu: 'Визуальные материалы', blurbEn: 'Visual material', blurbEs: 'Material visual', blurbDe: 'Visuelle Materialien', blurbZh: '视觉素材' },
};

/** Get the localized category name for a language, falling back to en then ru. */
export function getCategoryName(category: string, lang: Lang): string {
  const meta = CATEGORY_META[category];
  if (!meta) return category;
  const key = lang as keyof typeof meta;
  return meta[key as 'ru' | 'en' | 'es' | 'de' | 'zh'] ?? meta.en ?? meta.ru ?? category;
}

/** Get the localized category blurb for a language, falling back to en then ru. */
export function getCategoryBlurb(category: string, lang: Lang): string {
  const meta = CATEGORY_META[category];
  if (!meta) return '';
  const blurbKey = `blurb${lang.charAt(0).toUpperCase() + lang.slice(1)}` as keyof typeof meta;
  return meta[blurbKey] ?? meta.blurbEn ?? meta.blurbRu ?? '';
}
