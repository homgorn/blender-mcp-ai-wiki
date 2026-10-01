/**
 * The one place the canonical origin is defined.
 *
 * Astro reads `site` from astro.config.mjs and exposes it as `import.meta.env.SITE`
 * to every module, so the config is the single source of truth and this module
 * never hardcodes a second copy. A hardcoded constant in the layout while the
 * config used the env var produced pages advertising one origin and a sitemap
 * advertising another — the worst possible SEO bug, because each file looked fine.
 *
 * Priority: PUBLIC_SITE_URL (build env) -> astro.config `site` -> localhost.
 */
const RAW = (import.meta.env?.PUBLIC_SITE_URL || import.meta.env?.SITE || 'http://localhost:4321').toString();

/** No trailing slash. */
export const SITE_URL = RAW.replace(/\/+$/, '');

/** True when the build ran without a real origin — the SEO gate warns on this. */
export const SITE_URL_IS_LOCAL = /^https?:\/\/localhost|^https?:\/\/127\.0\.0\.1/.test(SITE_URL);
