# Implementation Plan: Página de produto

**Branch**: `feat/004-produto` | **Spec**: [spec.md](spec.md)

## Summary
View `catalogo:produto` (slug) com `with_cards`-like prefetch; template `catalogo/produto.html` (P01–P11 de `componentes.md`); JS puro em `static/js/app.js` (módulos galeria, seletor de variação, quantidade, expansor, barra fixa — já estruturados na 001). Variações serializadas em `data-variacoes` (JSON) para o seletor. Validação definitiva no servidor (005).

## Technical Context
Sem dependências novas. Seletor = `fieldset` + `legend` + `input type=radio` estilizados em pílula (corrige o `select-name` crítico da referência). Diálogo de ampliação = `<dialog>` nativo.

## Constitution Check
I ✅ (rádios funcionam sem JS) · II ✅ (layout P01–P11) · III ✅ (seletor e ficha vêm do schema) · VI ✅ (fieldset/legend, aria-live, foco) · VII ✅ (unit + E2E) · IX ✅ (sem avaliações).

## Project Structure
`apps/catalogo/views.py::produto` · `templates/catalogo/produto.html` · `static/css/paginas.css` (produto) · `tests/unit/catalogo/test_produto.py` · `tests/e2e/test_produto.py`
