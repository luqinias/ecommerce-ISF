---
description: "Tasks — 001 Fundação"
---

# Tasks: Fundação do projeto

**Input**: `specs/001-fundacao/` (plan, research, data-model, contracts, quickstart)
**Tests**: obrigatórios (constituição, princípio VII).

## Phase 1: Setup

- [X] T001 Dependências no `pyproject.toml` (grupos `dev` e `engenharia-reversa`) e `uv.lock`
- [X] T002 [P] `manage.py`, `config/{urls,wsgi,asgi}.py`, `config/settings/{base,dev,prod,test}.py`
- [X] T003 [P] `.env.example` (só nomes e valores de exemplo), `.gitignore` atualizado
- [X] T004 [P] `[tool.ruff]` e `[tool.pytest.ini_options]` no `pyproject.toml`
- [X] T005 [P] `Dockerfile`, `docker-compose.yml`, `docker/entrypoint.sh`, `.dockerignore`

## Phase 2: Foundational

- [X] T006 Apps `apps/{core,catalogo,orcamentos,conteudo,seo}` com `apps.py`
- [X] T007 Models base em `apps/core/models.py` (`CleanSaveModel`, `TimeStampedModel`, `UUIDTimeStampedModel`, `ActiveModel`)
- [X] T008 `SiteConfiguration` singleton + admin + migração em `apps/core/`
- [X] T009 Context processors em `apps/core/context_processors.py`
- [X] T010 Template tags `apps/core/templatetags/isf.py` (`whatsapp_url`, `icone`, `definir`)
- [X] T011 Jazzmin + axes configurados em `config/settings/base.py`

## Phase 3: US1 — Moldura do site (P1) 🎯 MVP

**Independent Test**: `/` nos 3 viewports mostra faixa, header, nav/menu mobile e rodapé.

- [X] T012 [P] [US1] Teste: home 200, 1 h1, landmarks, `[DEFINIR]` sem config em `tests/unit/core/test_layout.py`
- [X] T013 [P] [US1] E2E: menu mobile abre/fecha (botão, Esc, overlay); dropdown desktop em `tests/e2e/test_moldura.py`
- [X] T014 [US1] Fontes e HTMX em `static/fonts/`, `static/vendor/`
- [X] T015 [US1] CSS: `static/css/{tokens,base,layout,componentes}.css`
- [X] T016 [US1] Templates `templates/base.html` e `templates/partials/*`
- [X] T017 [US1] JS `static/js/app.js` (dropdowns, menu mobile, sticky, rolar para cima, cookies)
- [X] T018 [US1] Home provisória `apps/core/views.py` + `templates/core/home.html`

## Phase 4: US2 — 404 útil (P2)

- [X] T019 [P] [US2] Teste 404 (status, noindex, busca) e 500 estático em `tests/unit/core/test_erros.py`
- [X] T020 [US2] `templates/404.html`, `templates/500.html`

## Phase 5: US3 — Operação (P1)

- [X] T021 [P] [US3] Teste `/healthz/` (200 e 503) e defaults seguros de settings em `tests/unit/core/test_operacao.py`
- [X] T022 [US3] View `healthz` em `apps/core/views.py`
- [X] T023 [US3] README inicial com setup

## Phase 6: Polish

- [X] T024 `ruff check`, `ruff format`, `pytest` verdes
- [X] T025 Verificação visual nos 3 viewports (screenshots locais)

## Dependencies

Setup → Foundational → US1 → (US2 ∥ US3) → Polish. US2 e US3 só dependem do Foundational e do `base.html`.
