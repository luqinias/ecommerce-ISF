# Implementation Plan: Modelo do catálogo

**Branch**: `feat/002-catalogo-modelo` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

## Summary

Models do catálogo (`Category`, `Collection`, `Product`, `Variant`, `ProductImage`, `CatalogImport`) com validação de atributos via JSON Schema gerado da definição da categoria; admin Jazzmin com campos de atributos gerados dinamicamente; serviço de importação CSV/XLSX idempotente por SKU (usado pelo command e pelo admin); limpeza e carga de demonstração (CSV de exemplo + imagens placeholder geradas com Pillow).

## Technical Context

**Language/Version**: Python 3.12 · Django 6.0

**Primary Dependencies**: + `jsonschema` (validação de atributos, padrão interno) · + `openpyxl` (XLSX, padrão interno) · Pillow (miniaturas WebP, já presente)

**Storage**: tabelas do app `catalogo`; imagens em `MEDIA_ROOT/produtos/`

**Testing**: pytest; factories em `tests/factories.py`

**Performance Goals**: importação de 500 linhas < 1 min sem imagens (bulk de leituras por SKU, transação única)

**Constraints**: nenhuma regra depende de categoria/atributo específico

## Constitution Check

| Princípio | Atendimento | OK |
|---|---|---|
| III. Catálogo substituível | atributos em `attribute_schema`; importação idempotente; `is_demo` + limpeza | ✅ |
| IV. Padrões internos | `CleanSaveModel` (regra em `clean()`), `services/` (escrita), `selectors.py` (leitura), `TextChoices`, jsonschema, openpyxl | ✅ |
| VII. Testes | unit para validação de schema, importação (dry-run, idempotência, erros), limpeza, miniaturas | ✅ |
| IX. Simplicidade | sem django-import-export (C10), sem preço/estoque | ✅ |

**Dependências novas**: `jsonschema` e `openpyxl` (ambas já usadas no projeto interno; necessárias para FR-004 e FR-007).

## Project Structure

```text
apps/catalogo/
├── models.py          # Category, Collection, Product, Variant, ProductImage, CatalogImport
├── choices.py         # SaleUnit, AttributeType, ImageKind, CollectionColor
├── schema.py          # meta-schema da definição e geração do JSON Schema de produto/variação
├── selectors.py       # leitura (menus; listagens na 003)
├── services/
│   ├── importacao.py  # parse CSV/XLSX, upsert por SKU, relatório
│   ├── imagens.py     # miniaturas WebP e associação de imagens
│   └── demo.py        # catálogo de demonstração + placeholders
├── admin.py · forms.py
└── management/commands/{importar_catalogo,limpar_catalogo_demo,carregar_catalogo_demo}.py
docs/importacao-catalogo.md · docs/exemplos/{modelo-catalogo.xlsx,modelo-catalogo.csv,catalogo-demo.csv}
tests/unit/catalogo/
```

## Complexity Tracking

Nenhuma violação.
