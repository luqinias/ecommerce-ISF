# Research: Fundação

| # | Decisão | Alternativas | Motivo |
|---|---|---|---|
| R1 | Settings em `config/settings/{base,dev,prod,test}.py`, `DJANGO_SETTINGS_MODULE` default `config.settings.dev` no `manage.py` e `config.settings.prod` no `wsgi.py` | arquivo único com flags (padrão interno) | Feature pede settings por ambiente; mantém `python-dotenv` e `DEBUG=False` por default (C2) |
| R2 | Banco via `DATABASE_URL` (dj-database-url) **e** variáveis `DB_*` do padrão interno; sem nenhuma, SQLite | só `DB_*` | Compose e PaaS usam URL; equipe já conhece `DB_*` |
| R3 | `SiteConfiguration` singleton com `pk` fixo e `load()` com cache invalidado no `save()` | django-solo | Evita dependência; poucas linhas |
| R4 | HTMX 2.0.x vendorizado em `static/vendor/` | CDN | LGPD (sem terceiros), funciona offline, versionado |
| R5 | Fontes variáveis (WOFF2 latin) em `static/fonts/` com preload. Originalmente Manrope e JetBrains Mono; em 05/11/2026 trocadas por Fraunces (títulos, `font-display: optional`) e Inter (texto, `swap`), como na referência | Google Fonts | LGPD e LCP |
| R6 | Dropdowns e menu mobile em JS puro com `aria-expanded`; Alpine.js não é necessário | Alpine.js | Princípio IX: menos uma lib |
| R7 | Ícones SVG inline via `{% icone "nome" %}` (traço estilo lucide) | fonte de ícones | Sem request extra; `aria-hidden` |
| R8 | Healthcheck `/healthz/` faz `SELECT 1` e responde JSON `{"status": "ok"}`; 503 se o banco falhar | django-health-check | Princípio IX |
| R9 | 500 com template estático sem contexto de banco | — | Não pode depender do banco |
| R10 | E2E: pytest-playwright + `live_server` do pytest-django, `DJANGO_ALLOW_ASYNC_UNSAFE=true`, marcador `e2e` | Playwright standalone | Reusa fixtures e banco de teste |
| R11 | Docker: `python:3.12-slim` com uv, `collectstatic` no build, entrypoint roda `migrate` e sobe gunicorn; compose com `db` (postgres:16) | — | DoD: sobe com um comando |
