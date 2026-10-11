# Security Policy

## Reporting a vulnerability

Report privately through GitHub's **Security → Report a vulnerability** tab
rather than opening a public issue.

Include: what you found, which file or page, how to reproduce, and what an
attacker gains. A proof of concept is welcome; please keep it minimal.

Do not open a public issue for an unreported vulnerability.

## Response

| | |
|---|---|
| Acknowledgement | 3 working days |
| First assessment | 7 working days |
| Fix or mitigation plan | 14 working days |

These are targets, not guarantees. If a report needs longer, you will get an
interim note rather than silence.

## What this project does and does not hold

**No secrets are committed.** `.env` is the only place a key lives and it is
gitignored; `.env.example` carries the variable names with empty values and is
the only environment file in the repository. Cloudflare and GitHub credentials are
expected to live in `.env` locally and in repository secrets in CI.

If you find a key in this repository, treat it as compromised: report it rather
than opening a pull request that makes it public. It must be revoked, not edited
out of the file — the history keeps it.

## Trust boundaries worth knowing

- **The site is fully static.** No backend, no database, no session, no cookies.
  There is no login and no user data to steal. The deploy target is Cloudflare
  Pages serving files from `dist/`.
- **The Content-Security-Policy is strict.** `script-src 'self' 'wasm-unsafe-eval'`
  with no `'unsafe-inline'`; a gate fails the build on any inline handler. If you
  find yourself wanting to add `'unsafe-inline'`, that is the signal to move the
  code into a module instead.
- **The markdown corpus is authored content**, rendered through `marked` and
  highlighted by Shiki. Content comes from the repository, not from users, so
  there is no stored-XSS surface from third parties. If a contribution workflow
  ever accepts articles from outside the repo, that assumption breaks and this
  section must be rewritten.
- **Corpus code blocks are never executed by any gate.** `api_compat.py` resolves
  the API paths they mention by introspection; it does not run the snippets.
- **The local Python API** (`WIKI/scripts/wiki_api.py`) binds to `127.0.0.1` and
  is not authenticated. Do not expose it — not on a public interface, not through
  a tunnel. It is a development convenience.

## Out of scope

- Vulnerabilities in Blender, in the MCP servers, or in the third-party tools the
  articles describe. Report those to their maintainers.
- Lack of authentication on the site. There is no user account to protect.