# Implementation Plan: Navegação do catálogo

**Branch**: `feat/003-catalogo-navegacao` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

## Summary

Uma view de listagem genérica (`apps/catalogo/views.py::_listagem`) alimentada por "contextos" (catálogo, categoria, subcategoria, coleção, busca) que definem o queryset base, o hero e o breadcrumb. Leituras em `selectors.py` (ordenação, chips com contagem, busca). Templates `catalogo/listagem.html` + partials (hero, barra, card, paginação, ajuda, SEO). Sugestões de busca via HTMX (`hx-get` com `delay:300ms`) devolvendo um partial.

## Technical Context

Python 3.12 · Django 6.0 · HTMX 2 · sem dependências novas. Paginação com `django.core.paginator.Paginator` e URLs `/page/N/`. Consultas: `with_cards()` (select/prefetch) + contagem de chips com `Count(distinct)`.

## Constitution Check

| Princípio | Atendimento | OK |
|---|---|---|
| I | GET puro para filtros/ordem/paginação (funciona sem JS); HTMX só nas sugestões | ✅ |
| II | Estrutura L01–L08 de `componentes.md` | ✅ |
| III | Nenhuma categoria hard-coded; chips calculados | ✅ |
| V | noindex + canonical em filtros/busca; breadcrumbs; h1 único | ✅ |
| VI | Grade 2/3/4/5 colunas; chips com `aria-current` | ✅ |
| VII | Testes de selectors, views, paginação, busca e E2E navegar/ordenar/paginar | ✅ |

## Project Structure

```text
apps/catalogo/{selectors.py, views.py, urls.py}
templates/catalogo/{listagem.html, _sugestoes.html}
templates/componentes/{card_produto.html, paginacao.html, breadcrumb.html}
static/css/paginas.css (listagem)
tests/unit/catalogo/test_navegacao.py · tests/e2e/test_navegacao.py
```
