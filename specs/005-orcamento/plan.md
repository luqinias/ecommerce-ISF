# Implementation Plan: Lista e pedido de orçamento

**Branch**: `feat/005-orcamento` | **Spec**: [spec.md](spec.md)

## Summary
`apps/orcamentos/lista.py` (lista na sessão), models `Quote`/`QuoteItem`, `services.py` (criar pedido, mensagem WhatsApp, e-mails em `on_commit`), `forms.py` (com honeypot e consentimento), views HTMX (adicionar, mini-lista, itens, página da lista, enviado, WhatsApp direto), limite de taxa em `apps/core/ratelimit.py` (cache do Django, decisão C11), e-mails texto+HTML (`apps/core/email.py`, inspirado em `SendEmailBase`), admin com ações de status e CSV.

## Technical Context
Sem dependências novas. E-mail: backend configurável (console em dev, Brevo/Anymail em produção). HTMX: respostas com `HX-Trigger` (toast) e swaps out-of-band do contador.

## Constitution Check
I ✅ (todos os fluxos funcionam sem JS) · IV ✅ (`UUIDTimeStampedModel`, services) · VIII ✅ (consentimento com finalidade, só os dados necessários, sem IP gravado) · IX ✅ (sem pagamento/checkout) · VII ✅.

## Data model
- **Quote**: id UUID, code (ORC-AAAA-NNNNN, único), name, company, email, phone, city, state (UF), message, source (site/whatsapp/contato), status (new/in_progress/answered/closed/lost), consent (bool) + consent_text, internal_notes, email_sent_at, email_error, created_at/updated_at.
- **QuoteItem**: quote, product (SET_NULL), variant (SET_NULL), product_name, product_sku, variant_label, variant_sku, quantity, unit.

## Project Structure
`apps/orcamentos/{lista,models,choices,forms,services,views,urls,admin}.py` · `apps/core/{email,ratelimit}.py` · `templates/orcamentos/*` · `templates/emails/*` · `tests/unit/orcamentos/*` · `tests/e2e/test_orcamento.py`
