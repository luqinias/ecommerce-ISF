# Implementation Plan: Fundação do projeto

**Branch**: `feat/001-fundacao` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-fundacao/spec.md`

## Summary

Criar o monolito Django com settings por ambiente, os cinco apps do domínio, o singleton de configuração do site, o layout base (faixa superior, header com busca e lista, navegação com dropdowns, menu mobile, rodapé, banner de cookies e "rolar para cima") com os tokens "Campo" e as métricas da referência, páginas 404/500, healthcheck, Docker, ruff e pytest.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 6.0.x · python-dotenv · dj-database-url · psycopg2-binary · Pillow · django-jazzmin · django-axes · whitenoise · gunicorn · django-anymail[brevo]. Front: HTMX 2 (arquivo estático versionado), JS puro, CSS puro com custom properties

**Storage**: PostgreSQL 16 (prod/compose); SQLite (dev sem Docker e testes)

**Testing**: pytest + pytest-django + pytest-cov + factory-boy; E2E com pytest-playwright (marcador `e2e`)

**Target Platform**: Linux (container ou EC2 + gunicorn + Nginx)

**Project Type**: web (monolito server-rendered)

**Performance Goals**: LCP ≤ linha de base da referência por tipo de página; CLS ≤ 0,1

**Constraints**: sem build de front; nenhum recurso de terceiros antes do consentimento (fontes locais); sem rolagem horizontal em 390 px

**Scale/Scope**: catálogo de centenas de produtos; dezenas de orçamentos/dia

## Constitution Check

| Princípio | Como a feature atende | OK |
|---|---|---|
| I. Django puro / HTMX | Templates Django, HTMX vendorizado, JS puro para menu/dropdown/cookies | ✅ |
| II. Fidelidade na forma | Header/footer seguem `componentes.md` C01–C11 com tokens de `design-tokens.json`; textos ISF ou `[DEFINIR]` | ✅ |
| III. Catálogo substituível | Menus leem dados (listas vazias até 002) | ✅ |
| IV. Padrões internos | uv, dotenv, models base, Jazzmin, axes, ruff, pytest, factory-boy | ✅ |
| V. SEO | landmarks, 1 h1 por página, 404 `noindex`, bloco de metas no base | ✅ |
| VI. Mobile/a11y | CSS mobile first, skip link, foco visível, `aria-expanded`, reduced motion | ✅ |
| VII. Testes | unit (settings, config, views) + e2e (menu mobile, 404, cookies) | ✅ |
| VIII. LGPD | banner de cookies já na moldura; nenhum script de terceiros | ✅ |
| IX. Simplicidade | sem Celery, sem DRF, sem bundler | ✅ |

**Novas dependências e justificativa**

| Lib | Por quê |
|---|---|
| Django, python-dotenv, dj-database-url, psycopg2-binary, Pillow | padrão interno (Fase 0) |
| django-jazzmin, django-axes | admin e proteção de login do padrão interno |
| django-anymail[brevo] | e-mail transacional do padrão interno (usado na 005) |
| whitenoise | estáticos no mesmo deploy sem S3 (decisão C6) |
| gunicorn | servidor WSGI do padrão interno |
| HTMX (arquivo) | interatividade parcial exigida pela seção 1 do prompt; ~50 KB, sem build |
| pytest, pytest-django, pytest-cov, factory-boy, ruff | padrão interno |
| pytest-playwright | E2E exigido pelo princípio VII |

## Project Structure

### Documentation (this feature)

```text
specs/001-fundacao/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/rotas.md
└── tasks.md
```

### Source Code (repository root)

```text
config/
├── settings/{__init__,base,dev,prod,test}.py
├── urls.py · wsgi.py · asgi.py
apps/
├── core/        # models base, SiteConfiguration, context processors, healthz, 404/500, templatetags
├── catalogo/    # (vazio nesta feature)
├── orcamentos/  # (vazio)
├── conteudo/    # (vazio)
└── seo/         # (vazio)
templates/
├── base.html · 404.html · 500.html
├── partials/   faixa_superior, header, nav, menu_mobile, footer, cookies, rolar_topo
└── componentes/ botao, badge, breadcrumb, icone
static/
├── css/ tokens.css · base.css · layout.css · componentes.css
├── js/  app.js (menu, dropdowns, sticky, topo, cookies)
├── vendor/htmx.min.js
└── fonts/ manrope-*.woff2 · jetbrains-mono-*.woff2
tests/
├── conftest.py · factories.py
├── unit/
└── e2e/
Dockerfile · docker-compose.yml · .env.example · manage.py
```

**Structure Decision**: estrutura 6.6 do prompt com apps em `apps/` (decisão C3) e testes em `tests/` na raiz.

## Complexity Tracking

Nenhuma violação.
