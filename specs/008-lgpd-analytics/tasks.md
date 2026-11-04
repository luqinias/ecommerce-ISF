# Implementation Plan: Consentimento e analytics

**Branch**: `feat/008-lgpd-analytics` | **Spec**: [spec.md](spec.md)

## Summary
`base.html` expõe os IDs num `<script type="application/json" id="isf-analytics">` (dado inerte, não executa). `app.js` (módulo de cookies da 001) passa a injetar GTM (`gtm.js?id=`) e Meta Pixel (`fbevents.js`) somente no evento `isf:consentimento` = `todos`; na revogação apaga cookies conhecidos e recarrega. Sem novas dependências.

## Constitution Check
VIII ✅ (núcleo) · I ✅ (JS puro) · IX ✅.

## Tasks
- [X] T001 Bloco JSON de configuração no `base.html` (só com IDs preenchidos)
- [X] T002 Injeção de GTM/Pixel após aceite; limpeza na revogação (`static/js/app.js`)
- [X] T003 Testes unitários (bloco só com IDs) e E2E (0 requisições antes; carga após aceite; nada com "necessários")
