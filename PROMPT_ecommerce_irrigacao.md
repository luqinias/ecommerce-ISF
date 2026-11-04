# Prompt — Catálogo/E-commerce Irrigação Sem Fronteiras (engenharia reversa + Spec Kit)

> Uso: coloque este arquivo na raiz do novo repositório e entregue-o ao agente (ex.: Claude Code) como instrução inicial. Execute as fases **na ordem**. Ao fim de cada fase, apresente um resumo e aguarde aprovação antes de seguir.

---

## 0. Papel e contexto

Você é um engenheiro de software sênior, especialista em Django e em engenharia reversa de interfaces web. Vai construir o site de catálogo/e-commerce de produtos agrícolas (irrigação) da empresa **Irrigação Sem Fronteiras** (https://www.linkedin.com/company/irrigacao-sem-fronteiras/).

O site deve reproduzir, **com a maior precisão possível em estrutura, layout, componentes e comportamento**, o sistema de referência **https://ciadaartebrindes.com.br/**, adaptado ao domínio de irrigação.

Os produtos e o catálogo da empresa **ainda não estão definidos**. O sistema precisa nascer com dados de demonstração e permitir **substituir todo o catálogo depois** sem alterar código.

---

## 1. Decisões já tomadas (não reabrir)

| Tema | Decisão |
|---|---|
| Arquitetura | **Django puro**, monolito, **renderização no servidor** (templates Django). Back e front no mesmo projeto e no mesmo deploy. |
| Proibido | React/SPA, Django Oscar, Saleor, WordPress ou qualquer framework de e-commerce pronto. |
| Interatividade | **HTMX** (e, se necessário, Alpine.js ou JS puro) para partes dinâmicas. Nada de build de front complexo. |
| Modelo de negócio inicial | **Catálogo + lista de orçamento**. Sem preço público, sem pagamento online, sem checkout. A conversão acontece por **WhatsApp** (link `wa.me` com mensagem pré-preenchida) e/ou **e-mail**. |
| Catálogo | Dados de demonstração marcados como tal, substituíveis por importação (CSV/XLSX) e pelo Django Admin. |
| Idioma | Interface, conteúdo e documentação em **pt-BR**. Código (nomes de classes, funções) segue o padrão do projeto interno analisado na Fase 0. |
| Futuro | Manter models limpos para permitir, depois, uma API com Django REST Framework ou venda online, **sem implementar isso agora**. |

---

## 2. O que já se sabe do sistema de referência

Use como ponto de partida e **confirme tudo** na Fase 1.

- **Stack da referência:** WordPress + WooCommerce + Elementor (tema Astra), Rank Math (SEO), LiteSpeed Cache, Google Tag Manager, Meta Pixel. Serve só como referência de comportamento; **não deve ser replicada tecnologicamente**.
- **Catálogo:** cerca de 522 produtos em cerca de 36 categorias, com hierarquia rasa (ex.: Agendas dentro de Cadernos). Um produto pode estar em **várias categorias**, inclusive "Datas Especiais" (Natal, Outubro Rosa…).
- **Listagem:** 30 produtos por página, paginação numerada, chips de categoria com contagem, ordenação por "Mais relevantes", "Novidades" e "Nome (A–Z)". Cada card tem nome, quantidade de cores, descrição curta e link "Ver produto". **Sem preço.**
- **URLs:** `/produto/{slug}/`, `/categoria-produto/{slug}/`, `/categoria-produto/{pai}/{filho}/`, `/categorias-de-brindes/page/{n}/`.
- **Produto:** do tipo variável, com atributo **Cor**; o botão fica bloqueado até escolher a variação ("Escolha uma cor para continuar"). Campos: código/SKU, dimensões, material, capacidade, peso, **quantidade mínima**. Galeria com foto de produto e de ambiente, breadcrumbs, "Ler descrição completa", produtos relacionados ("Você também pode gostar"), avaliações.
- **Conversão:** botão **"Adicionar ao orçamento"**, contador no cabeçalho, links `wa.me` com mensagem pré-preenchida ("Solicitar orçamento rápido"), página de solicitação de orçamento.
- **Home:** faixa superior, cabeçalho com menu "Todas as Categorias" (carregado via JS) e "Datas Especiais", hero com destaque sazonal, faixa de diferenciais, vitrine por categoria, próximas datas, portfólio de trabalhos com "Ver mais", "Como funciona" em 4 passos, bloco de prazos sazonais, "Por que nós", depoimentos, FAQ em acordeão, rodapé com contatos, banner de cookies, botão "rolar para cima".
- **Páginas:** Novidades, Sobre, Blog, Contato, Solicitar orçamento, Termos de uso e privacidade.

---

## 3. Fase 0 — Contexto da empresa (projetos internos)

Analise, **somente leitura**, dois projetos existentes da empresa para alinhar padrões:

- **Back-end Django:** `/home/lucaslira/back-irrigacao/frotas_back`
- **Front-end React:** `/home/lucaslira/irrigacao/farmevolution_web`

### 3.1 No projeto Django (`frotas_back`), levante:
- versão de Python e Django, gerenciador de dependências (pip/requirements, Poetry, uv) e bibliotecas usadas;
- estrutura de pastas e de apps, organização de `settings` (arquivo único, dividido por ambiente, `django-environ`, `.env`);
- banco de dados, storage de mídia, cache e filas, se houver;
- padrões de código: nomes (pt-BR ou inglês), models base (timestamps, soft delete, UUID), managers, services/selectors, signals;
- customizações do Django Admin, autenticação, permissões;
- testes (pytest ou unittest, factories, cobertura), lint/format (ruff, black, isort, flake8), pre-commit, tipagem;
- Docker/docker-compose, CI/CD, servidor (gunicorn/uvicorn, nginx), variáveis de ambiente esperadas (**somente os nomes, nunca os valores**);
- convenções de commits, branches e README.

### 3.2 No projeto React (`farmevolution_web`), levante:
- **identidade visual**: paleta de cores, tipografia, espaçamentos, raios, sombras, logos e ícones (tema, variáveis CSS, Tailwind config, styled-components etc.);
- componentes visuais recorrentes que devem ser traduzidos para templates/partials Django;
- tom de voz e textos institucionais reaproveitáveis.

### 3.3 Regras da Fase 0
- **Não copie segredos.** Não leia nem reproduza valores de `.env`, chaves ou credenciais.
- Não altere nada nesses diretórios.
- Se um padrão do projeto interno conflitar com a seção 1, **a seção 1 vence**. Registre o conflito.

### 3.4 Entregável
`docs/contexto-empresa.md`, com o resumo dos padrões adotados, a lista do que será reaproveitado (estrutura, libs, lint, Docker, tokens visuais) e as decisões sobre conflitos.

---

## 4. Fase 1 — Engenharia reversa do sistema de referência (Playwright)

### 4.1 Ferramental
- **Playwright para Python** (`pip install playwright pytest-playwright` e `playwright install chromium`), com scripts em `tools/engenharia_reversa/`.
- Opcional: `axe-playwright-python` para acessibilidade.

### 4.2 Regras de conduta (obrigatórias)
- Acesse **apenas páginas públicas**. Respeite `robots.txt`.
- Limite a taxa a **no máximo 1 requisição a cada 2 segundos**, com User-Agent identificável e genérico.
- **Não** submeta formulários, **não** adicione itens a orçamento que gerem contato real, **não** clique em links `wa.me` ou `mailto:`. Apenas registre os hrefs.
- **Não reproduza** no projeto final textos, fotos, logos, nome ou marca da referência. Extraia **estrutura, layout, hierarquia, componentes, comportamento e métricas visuais**. Todo conteúdo final usa dados da Irrigação Sem Fronteiras ou placeholders.
- Screenshots e HTML coletados são **material de estudo interno**: ficam em `docs/engenharia-reversa/` e vão para o `.gitignore` se a equipe preferir não versioná-los.

### 4.3 Inventário de páginas
1. Leia o sitemap (provável `sitemap_index.xml` do Rank Math) e os links do menu e do rodapé.
2. Classifique por **tipo de página**: home, catálogo geral, categoria, subcategoria, data especial, produto (simples e com variações), novidades, sobre, blog (lista e post), contato, solicitar orçamento, termos, 404.
3. Escolha **2 ou 3 amostras por tipo**. Não é preciso varrer todos os produtos.

### 4.4 Para cada página amostrada, colete
- **Screenshots full-page** em 3 viewports: 1440×900, 768×1024 e 390×844.
- **Árvore de seções**: ordem dos blocos, landmarks (`header`, `nav`, `main`, `footer`) e hierarquia de headings (h1 a h4).
- **Estilos computados** dos elementos-chave (body, headings, botões primário e secundário, links, cards, chips, inputs, badges): cor, fonte, tamanho, peso, line-height, padding, margin, raio, sombra, transições.
- **Layout**: largura máxima do container, grid (colunas por breakpoint), gaps e breakpoints reais (detecte as mudanças de layout).
- **Comportamentos**: o que muda ao interagir. Inclua, no mínimo:
  - dropdown/mega-menu "Todas as Categorias" e "Datas Especiais", menu mobile;
  - chips de filtro, ordenação, paginação;
  - seletor de variação bloqueando o botão, botão "+" de quantidade e validação da quantidade mínima;
  - "Adicionar ao orçamento" e atualização do contador (observe sem concluir o envio);
  - galeria de imagens, "Ler descrição completa", acordeão do FAQ, "Ver mais trabalhos";
  - banner de cookies, botão "rolar para cima", estados de hover e foco.
- **Rede**: requisições XHR/fetch disparadas (ex.: Store API do WooCommerce, `wc-ajax`), para entender quais partes são dinâmicas e qual payload trafega.
- **SEO**: `title`, meta description, canonical, Open Graph, robots, breadcrumbs, dados estruturados (JSON-LD), padrão de URL.
- **Acessibilidade** (axe) e métricas básicas de performance (LCP, CLS), para servir de linha de base.

### 4.5 Modelo de dados da referência
Consulte a API pública `/wp-json/wc/store/v1/products` (e `/products/categories`) com poucas páginas e o rate limit da seção 4.2. Documente campos, atributos, variações, relação entre categorias e tags e o que aparece em listagem versus página de produto.

### 4.6 Entregáveis da Fase 1 (`docs/engenharia-reversa/`)
- `inventario-paginas.md`: tipos de página, URLs amostradas e mapa de navegação.
- `componentes.md`: catálogo de componentes (nome, onde aparece, variações, estados, comportamento), com referência ao screenshot.
- `design-tokens.json` e `design-tokens.md`: cores, tipografia, espaçamentos, raios, sombras e breakpoints extraídos.
- `fluxos.md`: fluxos de navegação e de orçamento, passo a passo, com diagramas Mermaid.
- `modelo-dados-referencia.md`: entidades e campos observados.
- `seo.md`: padrões de URL, metas e dados estruturados.
- `screenshots/{tipo}/{viewport}.png`.
- `gap-analysis.md`: o que se aplica ao domínio de irrigação, o que precisa adaptação e o que não se aplica.

---

## 5. Fase 2 — Mapeamento de domínio (brindes → irrigação)

Produza `docs/mapeamento-dominio.md` traduzindo os conceitos da referência:

| Referência (brindes) | Irrigação Sem Fronteiras (proposta provisória) |
|---|---|
| Categorias de brinde | Categorias de produto. Sugestões **provisórias**: Gotejamento, Microaspersão, Aspersão, Tubos e Conexões, Filtragem, Automação e Controladores, Bombas, Fertirrigação, Kits |
| Datas Especiais (Natal, Outubro Rosa) | Coleções/campanhas configuráveis (ex.: por cultura, por época de plantio, lançamentos). O nome final será definido pela empresa |
| Variação por **Cor** | Variações por atributos técnicos (ex.: vazão, diâmetro, pressão, voltagem, comprimento), **definidos por categoria e configuráveis no admin** |
| Quantidade mínima | Quantidade mínima e unidade de venda (peça, metro, rolo, kit) |
| Portfólio "trabalhos para clientes" | Projetos/instalações realizadas |
| Personalização com logo | Não se aplica. Substituir por "dimensionamento/projeto sob consulta", se a empresa quiser |

**Não invente** dados reais da empresa (CNPJ, endereço, telefone, preços, especificações técnicas). Use placeholders explícitos (`[DEFINIR]`) e registre tudo em `docs/pendencias-empresa.md`.

---

## 6. Fase 3 — Especificação e construção com Spec Kit

### 6.1 Setup
```bash
uv tool install specify-cli
specify init . --integration claude   # confirme o nome da integração com: specify init --help
```
Os comandos do Spec Kit mudam entre versões. Confirme os disponíveis no agente (prefixo `/speckit-`) antes de começar. O fluxo esperado é:

`/speckit-constitution` → `/speckit-specify` → *(clarify, se existir)* → `/speckit-plan` → `/speckit-tasks` → *(analyze/checklist, se existirem)* → `/speckit-implement`

### 6.2 Constituição (`/speckit-constitution`)
Inclua, no mínimo, estes princípios:
1. Django puro com renderização no servidor; HTMX para interatividade; sem SPA.
2. Fidelidade à referência em estrutura, layout e comportamento, nunca em conteúdo ou marca.
3. **Catálogo substituível**: nenhuma regra de negócio depende de um produto, categoria ou atributo específico. Atributos técnicos são dados, não código.
4. Padrões do projeto interno (Fase 0) para estrutura, lint, testes e Docker.
5. SEO first: URLs amigáveis, HTML semântico, metas, sitemap e dados estruturados.
6. Mobile first e acessibilidade (WCAG 2.1 AA como meta).
7. Testes obrigatórios: unitários para models e serviços, E2E com Playwright para fluxos críticos.
8. LGPD: consentimento de cookies antes de qualquer script de rastreamento; dados de orçamento com finalidade declarada.
9. Simplicidade: não implementar pagamento, frete, estoque ou API antes de serem pedidos.

### 6.3 Features (uma spec por feature, nesta ordem)
Rode o ciclo completo do Spec Kit para cada uma. Use os entregáveis das Fases 0 a 2 como insumo.

1. **001-fundacao**: projeto Django, settings por ambiente, apps base, Docker, lint, testes, layout base (header, footer, tokens visuais), página 404.
2. **002-catalogo-modelo**: models, admin, importação e dados de demonstração (ver 6.4).
3. **003-catalogo-navegacao**: catálogo geral, páginas de categoria e subcategoria, coleções, chips com contagem, ordenação, paginação (30 por página), busca simples, menu "Todas as Categorias".
4. **004-produto**: página de produto com galeria, seletor de variação (bloqueia o botão até a escolha), especificações técnicas renderizadas a partir dos atributos, quantidade mínima, descrição expansível, breadcrumbs, relacionados.
5. **005-orcamento**: lista de orçamento na sessão, contador no header (HTMX), página de revisão, formulário (nome, empresa, e-mail, telefone/WhatsApp, cidade/UF, mensagem), gravação do `Orcamento` no banco, e-mail para a equipe e confirmação para o cliente, redirecionamento para `wa.me` com mensagem gerada a partir dos itens. Inclui também o botão "orçamento rápido" (WhatsApp direto). Proteção anti-spam com honeypot e limite de taxa.
6. **006-home-institucional**: home com todas as seções da referência, montada a partir de conteúdo **editável no admin** (banners, diferenciais, passos, prazos/campanhas, portfólio, depoimentos, FAQ), mais as páginas Sobre, Contato, Novidades, Termos e Privacidade.
7. **007-seo**: sitemap (`django.contrib.sitemaps`), robots.txt, metas e Open Graph por página, canonical, JSON-LD (`Organization`, `Product` sem preço, `BreadcrumbList`, `FAQPage`).
8. **008-lgpd-analytics**: banner de cookies com opções "só necessários" e "aceitar todos"; GTM e Pixel carregados apenas após consentimento; IDs vindos de configuração.
9. **009-blog** *(opcional, confirmar com a empresa)*: posts e categorias simples.
10. **010-deploy**: build de produção, estáticos (WhiteNoise ou o padrão interno), mídia, healthcheck, guia de deploy.

### 6.4 Modelo de dados mínimo (ponto de partida para o `/speckit-plan`)
- `Categoria`: nome, slug, pai (árvore rasa), descrição, imagem, ordem, ativa, `schema_atributos` (JSON definindo os atributos técnicos esperados: chave, rótulo, tipo, unidade, se gera variação).
- `Colecao`: equivalente a "Datas Especiais", com nome, slug, período opcional, destaque na home, ordem.
- `Produto`: nome, slug, SKU, descrição curta e completa, categorias (M2M), coleções (M2M), `atributos` (JSONField validado contra o schema da categoria), quantidade mínima, unidade de venda, ativo, destaque, `novidade_ate`, `is_demo`, timestamps.
- `Variacao`: produto, SKU, `atributos` (JSONField), imagem, ativa.
- `ImagemProduto`: produto, imagem, alt, tipo (produto/ambiente), ordem. Gere miniaturas WebP.
- `Orcamento` e `ItemOrcamento`: dados do contato, origem (site/WhatsApp), status (novo, em atendimento, respondido, fechado, perdido), itens com produto, variação e quantidade (snapshot do nome e do SKU).
- `ConfiguracaoSite` (singleton): nome, contatos, número de WhatsApp, e-mails de destino, redes sociais, IDs de analytics, textos padrão das mensagens.
- Conteúdo da home: `Banner`, `Diferencial`, `PassoComoFunciona`, `ItemPortfolio`, `Depoimento`, `PerguntaFrequente`.

### 6.5 Substituição do catálogo (requisito central)
- Comando `python manage.py importar_catalogo <arquivo.csv|xlsx> [--dry-run]`: **idempotente por SKU**, cria ou atualiza categorias, produtos, variações e atributos, baixa ou associa imagens e gera relatório de erros por linha.
- Comando `python manage.py limpar_catalogo_demo`: remove apenas registros com `is_demo=True`.
- Modelo de planilha documentado em `docs/importacao-catalogo.md`, com uma planilha-exemplo em `docs/exemplos/`.
- Fixture de demonstração com cerca de 40 produtos fictícios de irrigação, em 6 a 9 categorias e 2 coleções, com imagens placeholder geradas (sem fotos de terceiros).
- Import/export também pelo admin (ex.: `django-import-export`, se compatível com o padrão interno).

### 6.6 Estrutura sugerida (ajuste ao padrão da Fase 0)
```
config/            # settings (base, dev, prod), urls, wsgi
apps/
  core/            # layout, ConfiguracaoSite, context processors, utilidades
  catalogo/        # categorias, coleções, produtos, variações, importação
  orcamentos/      # lista na sessão, formulário, envio, admin de leads
  conteudo/        # home, institucionais, FAQ, depoimentos, portfólio
  seo/             # sitemaps, robots, JSON-LD
templates/         # base.html, partials/, componentes/ (um partial por componente do inventário)
static/            # css (tokens + componentes), js (HTMX, Alpine), img
tools/engenharia_reversa/
tests/             # unit + e2e (playwright)
docs/
```

---

## 7. Fase 4 — Validação

1. **Testes unitários e de integração** (pytest-django ou o padrão interno): models, validação de atributos contra o schema, importação, lista de orçamento, geração da mensagem `wa.me`, envio de e-mail.
2. **E2E com Playwright** para os fluxos críticos: navegar por categoria, ordenar e paginar; abrir produto, escolher variação e respeitar a quantidade mínima; adicionar ao orçamento, revisar e enviar; orçamento rápido; consentimento de cookies.
3. **Comparação com a referência**: com os mesmos scripts e viewports da Fase 1, gere screenshots do sistema local e produza `docs/validacao/comparativo.md` lado a lado. Como o conteúdo é diferente, compare **estrutura** (ordem das seções, grid, posições e proporções dos blocos, tokens visuais, comportamentos), não pixels. Liste as divergências e justifique as intencionais.
4. **Acessibilidade e performance**: axe sem violações críticas; LCP e CLS iguais ou melhores que a linha de base da referência.

---

## 8. Definition of Done

- [ ] Todos os tipos de página do inventário existem e seguem o layout da referência nos 3 viewports.
- [ ] Todos os componentes e comportamentos de `componentes.md` estão implementados ou têm a exclusão justificada.
- [ ] O catálogo de demonstração pode ser trocado por planilha, sem alterar código, com o fluxo testado.
- [ ] O fluxo de orçamento grava o lead, envia e-mail e abre o WhatsApp com a mensagem correta.
- [ ] SEO: sitemap, metas, canonical e JSON-LD válidos.
- [ ] Testes passando; lint limpo; projeto sobe com um comando (Docker ou o padrão interno).
- [ ] `README.md` com setup, comandos de importação e deploy; `docs/pendencias-empresa.md` atualizado.

---

## 9. Regras de comportamento do agente

- Ao fim de cada fase e de cada feature do Spec Kit, **pare, resuma e peça aprovação**.
- Dúvidas de negócio (nomes de categorias, coleções, textos, contatos, atributos técnicos) vão para `docs/pendencias-empresa.md`. Use placeholders e **não invente**.
- Se a página do LinkedIn exigir login, não tente contornar. Peça à equipe o logo, a paleta, os textos institucionais e os contatos.
- Commits pequenos e descritivos, seguindo a convenção do projeto interno.
- Não adicione dependências fora do necessário. Justifique cada nova biblioteca no `plan.md`.
- Nunca grave segredos no repositório. Use variáveis de ambiente e um `.env.example`.
