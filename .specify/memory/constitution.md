# Constituição — Catálogo Irrigação Sem Fronteiras (ecommerce-isf)

## Princípios fundamentais

### I. Django puro, renderizado no servidor
- O site é um **monolito Django** (Python 3.12, Django 6.0.x). Back e front ficam no mesmo projeto e no mesmo deploy.
- Toda página é HTML renderizado por templates Django. Interatividade parcial usa **HTMX**; comportamentos locais (abrir menu, galeria, seletor) usam **JS puro** pequeno e progressivo. Alpine.js só entra se o JS puro ficar mais complexo que ele.
- **Proibido:** React/SPA, bundlers de front (webpack, vite), Django Oscar, Saleor, WordPress ou qualquer framework de e-commerce pronto.
- As páginas DEVEM funcionar sem JavaScript no essencial (navegar, ver produto, enviar orçamento pelo formulário). O JS melhora, não habilita.

### II. Fidelidade à referência na forma, nunca no conteúdo
- Estrutura, layout, hierarquia, componentes e comportamento seguem `docs/engenharia-reversa/` (inventário, componentes, tokens de layout, fluxos).
- Nenhum texto, foto, logo, nome ou marca da referência entra no projeto. Conteúdo é da ISF ou placeholder `[DEFINIR]`.
- Identidade visual (cores, tipografia) vem dos tokens "Campo" da Fase 0 até a ISF fornecer a marca. Da referência vêm só métricas de layout.
- Divergências intencionais de estrutura são registradas em `docs/validacao/comparativo.md`.

### III. Catálogo substituível (inegociável)
- Nenhuma regra de negócio, template ou teste depende de um produto, categoria, coleção ou atributo específico.
- Atributos técnicos são **dados**: definidos em `Category.attribute_schema` e validados em `Product.attributes` / `Variant.attributes`. Adicionar um atributo novo NÃO exige código nem migração.
- Todo dado de demonstração tem `is_demo=True` e é removível com `limpar_catalogo_demo`. A importação por planilha é idempotente por SKU.

### IV. Padrões internos da empresa
- Seguem `docs/contexto-empresa.md`: uv + `pyproject.toml`; `python-dotenv` com defaults seguros (`DEBUG=False`); código em inglês e textos, `verbose_name` e docs em pt-BR; models base `CleanSaveModel` / `UUIDTimeStampedModel`; escrita em `services.py`, leitura em `selectors.py`; Jazzmin + django-axes no admin; ruff (check + format); pytest + pytest-django + factory-boy; Conventional Commits em pt-BR.
- Conflitos com a seção 1 do prompt foram resolvidos a favor dela (decisões C1–C15 em `docs/contexto-empresa.md`).

### V. SEO first
- URLs amigáveis em pt-BR, estáveis e com barra final; um único `<h1>` por página; HTML semântico com landmarks.
- Toda página indexável tem `title`, meta description, canonical e Open Graph. Páginas de erro, busca e orçamento são `noindex`.
- Sitemap XML, `robots.txt` e JSON-LD (`Organization`, `WebSite`, `Product` sem preço, `BreadcrumbList`, `FAQPage`) são gerados a partir dos dados.

### VI. Mobile first e acessível
- CSS escrito do menor para o maior viewport. Os três viewports de referência (390, 768, 1440) são obrigatórios na validação. Sem rolagem horizontal.
- Meta WCAG 2.1 AA: contraste, foco visível, navegação por teclado, `aria-*` nos componentes dinâmicos, `prefers-reduced-motion` respeitado. axe sem violações críticas ou sérias.

### VII. Testes obrigatórios
- Testes unitários para models, validação de atributos, serviços (importação, orçamento, mensagem `wa.me`, e-mail) e selectors.
- E2E com Playwright para os fluxos críticos: navegar por categoria/ordenar/paginar; produto com variação e quantidade mínima; adicionar ao orçamento e enviar; orçamento rápido; consentimento de cookies.
- Nenhuma feature é concluída com teste falhando ou lint sujo.

### VIII. LGPD
- Nenhum script de rastreamento (GTM, Meta Pixel) é carregado antes do consentimento explícito. "Só necessários" é sempre uma opção tão visível quanto "Aceitar todos".
- O formulário de orçamento declara a finalidade dos dados e coleta só o necessário para responder ao orçamento.
- IDs de analytics vêm de configuração, nunca do código.

### IX. Simplicidade
- Não implementar pagamento, preço público, frete, estoque, contas de cliente, avaliações ou API antes de serem pedidos.
- Cada dependência nova é justificada no `plan.md` da feature. Sem Celery/Redis enquanto o volume não pedir.
- Models permanecem limpos (sem lógica de apresentação) para permitir DRF ou venda online no futuro.

## Restrições técnicas e de segurança

- Segredos só em variáveis de ambiente; `.env.example` lista os nomes. Nada de segredo no repositório.
- Produção: `DEBUG=False`, cookies `Secure`, HSTS configurável, `X_FRAME_OPTIONS=DENY`, CSRF em todo formulário.
- Formulário de orçamento: honeypot + limite de taxa por IP via cache do Django.
- Estáticos com WhiteNoise; mídia local ou S3 (`USE_S3`). PostgreSQL em produção, SQLite permitido em dev e testes.
- O projeto sobe com um comando (`docker compose up`) e também roda com `uv run` sem Docker.

## Fluxo de desenvolvimento

- Cada feature passa por: `/speckit-specify` → `/speckit-clarify` (quando houver ambiguidade) → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`. Os artefatos ficam em `specs/NNN-nome/`.
- Dúvidas de negócio vão para `docs/pendencias-empresa.md` e viram placeholder; nunca dados inventados.
- Commits pequenos, no padrão `tipo(escopo): descrição` em pt-BR.
- Gate de qualidade antes de fechar uma feature: `uv run ruff check .`, `uv run ruff format --check .` e `uv run pytest` verdes.

## Governança

- Esta constituição prevalece sobre preferências individuais e sobre os templates do Spec Kit. O `plan.md` de cada feature DEVE ter a seção "Constitution Check" respondida; violações exigem justificativa na tabela "Complexity Tracking".
- Emendas: alteração neste arquivo com nota de versão. MAJOR para remover ou redefinir princípio; MINOR para princípio ou seção nova; PATCH para redação.
- A revisão de cada feature verifica os princípios III (catálogo substituível), V (SEO), VI (acessibilidade) e VIII (LGPD) explicitamente.

**Version**: 1.0.0 | **Ratified**: 2026-11-04 | **Last Amended**: 2026-11-04
