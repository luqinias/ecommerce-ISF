---
description: "Tasks — 002 Modelo do catálogo"
---

# Tasks: Modelo do catálogo

**Input**: `specs/002-catalogo-modelo/` · **Tests**: obrigatórios.

## Phase 1: Setup

- [X] T001 Adicionar `jsonschema` e `openpyxl` ao `pyproject.toml`

## Phase 2: Foundational

- [X] T002 `apps/catalogo/choices.py` (SaleUnit, AttributeType, ImageKind, CollectionColor, ImportStatus)
- [X] T003 `apps/catalogo/schema.py` (meta-schema, schema efetivo, validação de produto e variação)
- [X] T004 Models em `apps/catalogo/models.py` + migração
- [X] T005 `apps/catalogo/services/imagens.py` (miniaturas WebP, download/associação)
- [X] T006 `apps/catalogo/selectors.py` (menus) e ligação ao context processor
- [X] T007 [P] Factories em `tests/factories.py`

## Phase 3: US2 — Atributos por categoria (P1)

- [X] T008 [P] [US2] Testes de schema e validação em `tests/unit/catalogo/test_schema.py` e `test_models.py`
- [X] T009 [US2] Admin: Category (editor de schema com ajuda), Collection, Product (campos de atributos dinâmicos, inlines de variação e imagem), em `apps/catalogo/admin.py` e `forms.py`

## Phase 4: US1 — Importação e limpeza (P1)

- [X] T010 [P] [US1] Testes de importação (CSV, XLSX, dry-run, idempotência, erros por linha, imagens, extensão de schema) em `tests/unit/catalogo/test_importacao.py`
- [X] T011 [US1] `apps/catalogo/services/importacao.py`
- [X] T012 [US1] Commands `importar_catalogo` e `limpar_catalogo_demo`
- [X] T013 [US1] `CatalogImport` no admin (upload + relatório)
- [X] T014 [US1] `docs/importacao-catalogo.md` + `docs/exemplos/modelo-catalogo.{xlsx,csv}`

## Phase 5: US3 — Demonstração (P2)

- [X] T015 [P] [US3] Teste de carga de demonstração (contagens, is_demo, idempotência) em `tests/unit/catalogo/test_demo.py`
- [X] T016 [US3] `docs/exemplos/catalogo-demo.csv` (~40 produtos, 9 categorias, 2 coleções) e `services/demo.py` (placeholders Pillow)
- [X] T017 [US3] Command `carregar_catalogo_demo`

## Phase 6: Polish

- [X] T018 ruff + pytest verdes; atualizar pendências (P9, P15)

## Dependencies

T001 → T002–T006 → (US2 ∥ US1) → US3 (usa o serviço de importação) → Polish.
