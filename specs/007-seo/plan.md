# Implementation Plan: SEO

**Branch**: `feat/007-seo` | **Spec**: [spec.md](spec.md)

## Summary
App `seo`: `sitemaps.py` (classes por entidade), `views.robots`, `jsonld.py` (funções puras que montam dicts schema.org a partir dos models) e template tags `{% jsonld_* %}` que emitem `<script type="application/ld+json">` com o filtro seguro `jsonld` (001). Partials `jsonld_home/listagem/produto` passam a usar as tags; `Organization`+`WebSite` entram no `base.html`.

## Constitution Check
V ✅ (núcleo da feature) · III ✅ (Product.additionalProperty gerado da ficha) · IX ✅ (sem `offers`).

## Project Structure
`apps/seo/{sitemaps,jsonld,views,urls}.py` · `apps/seo/templatetags/seo.py` · `tests/unit/seo/test_seo.py`
