# Implementation Plan: Home e páginas institucionais

**Branch**: `feat/006-home-institucional` | **Spec**: [spec.md](spec.md)

## Summary
App `conteudo` com models `Banner`, `Highlight` (local: prova/por que nós), `HowItWorksStep`, `SectionText` (chave por seção), `PortfolioItem`, `Testimonial`, `FAQItem` (local: home/contato), `Page` + `PageSection`. `selectors.home()` monta o contexto com o mínimo de consultas. Views: home, sobre, contato (GET/POST, reaproveita `Quote` com origem contato), termos, privacidade e página genérica; `catalogo:novidades` com HTMX "Carregar mais". Comando `carregar_conteudo_demo`.

## Constitution Check
I ✅ · II ✅ (H01–H11, I01–I04) · III ✅ (vitrine por categorias marcadas, nada fixo) · V ✅ (1 h1, h2 por seção) · VIII ✅ (sem iframe de mapa; contato com consentimento) · IX ✅.

## Data model (resumo)
- **SectionText**: key (vitrine, datas, portfolio, categorias, como_funciona, faixa, por_que, depoimentos, faq, novidades_cta, contato_hero, sobre_cta) única; kicker, title, highlight, text, cta_label, cta_url.
- **Banner**: title, highlight, subtitle, badge_label, cta labels/urls, image_main/2/3 + captions, active, order.
- **Highlight**: placement (prova/por_que), icon, title, text, order, active.
- **HowItWorksStep**: title, text, order, active.
- **PortfolioItem**: title, subtitle (cultura · cidade), image, tall, featured, order, active, is_demo.
- **Testimonial**: author, role, text, rating (1–5), order, active.
- **FAQItem**: placement (home/contato), question, answer, order, active.
- **Page**: slug (único), kind (sobre/legal/livre), kicker, title, highlight, lead, updated_label, active, meta_*; **PageSection**: page, title, anchor, body, order.
