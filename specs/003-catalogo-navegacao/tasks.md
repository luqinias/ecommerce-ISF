---
description: "Tasks — 003 Navegação do catálogo"
---

# Tasks: Navegação do catálogo

## Phase 1: Foundational
- [X] T001 Selectors: ordenação, chips com contagem, busca, base de listagem em `apps/catalogo/selectors.py`
- [X] T002 Componentes: `templates/componentes/{card_produto,paginacao,breadcrumb}.html`

## Phase 2: US1 — Categoria, chips, ordem, paginação (P1) 🎯
- [X] T003 [P] [US1] Testes em `tests/unit/catalogo/test_navegacao.py`
- [X] T004 [US1] Views `lista`, `categoria`, `subcategoria` com `_listagem` genérica
- [X] T005 [US1] Template `templates/catalogo/listagem.html` + CSS da listagem

## Phase 3: US2 — Busca e sugestões (P1)
- [X] T006 [P] [US2] Testes de busca e sugestões
- [X] T007 [US2] Views `busca` e `sugestoes` + `templates/catalogo/_sugestoes.html`

## Phase 4: US3 — Coleções e catálogo geral (P2)
- [X] T008 [US3] View `colecao` e chips "Ver todas as categorias" no catálogo geral

## Phase 5: Polish
- [X] T009 E2E: navegar por categoria, ordenar e paginar (`tests/e2e/test_navegacao.py`)
- [X] T010 ruff + pytest; screenshots 390/768/1440
