# Feature Specification: Fundação do projeto

**Feature Branch**: `001-fundacao`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "001-fundacao: projeto Django, settings por ambiente, apps base, Docker, lint, testes, layout base (header, footer, tokens visuais), página 404."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitante vê o esqueleto do site com a identidade provisória (Priority: P1)

Um visitante abre qualquer página do site e encontra a mesma moldura da referência: faixa superior de atendimento, cabeçalho com logo, busca, botão da lista de orçamento, barra de navegação ("Todas as Categorias", "Datas Especiais"/coleções, Novidades, Sobre, Blog, Contato e o CTA "Solicitar orçamento rápido") e rodapé com marca, redes, links de navegação, atendimento e linha legal. No celular, a navegação vira um menu lateral aberto por um botão.

**Why this priority**: todas as outras features renderizam dentro desta moldura.

**Independent Test**: subir o projeto, abrir `/` e uma URL inexistente nos três viewports e conferir header, footer e menu mobile.

**Acceptance Scenarios**:

1. **Given** o site no ar, **When** o visitante abre a página inicial em 1440 px, **Then** vê faixa superior, cabeçalho fixo ao rolar, barra de navegação e rodapé com as colunas Marca, Navegue e Atendimento.
2. **Given** viewport de 390 px, **When** o visitante toca no botão de menu, **Then** um painel lateral abre com as categorias, as coleções, os links institucionais e o CTA de orçamento; ele fecha pelo botão "Fechar", pela tecla Esc ou tocando fora.
3. **Given** dados de contato ainda não fornecidos, **When** a página é renderizada, **Then** os campos aparecem como `[DEFINIR]` e nenhum dado real é inventado.

---

### User Story 2 - Visitante que erra a URL recebe uma 404 útil (Priority: P2)

Quem acessa um endereço inexistente vê uma página "Esta página não existe." com busca e atalhos para o catálogo, dentro da moldura do site, com status HTTP 404 e `noindex`.

**Why this priority**: é parte do inventário de páginas e evita becos sem saída.

**Independent Test**: requisitar `/qualquer-coisa-inexistente/` e verificar status 404, título, busca e links.

**Acceptance Scenarios**:

1. **Given** uma URL inexistente, **When** é acessada, **Then** a resposta tem status 404, `<h1>` "Esta página não existe.", campo de busca e links para o catálogo e para a home.

---

### User Story 3 - Equipe sobe e mantém o projeto com um comando (Priority: P1)

Um desenvolvedor clona o repositório, copia `.env.example` para `.env` e sobe tudo com `docker compose up` (ou `uv run` sem Docker). Lint e testes rodam com um comando cada.

**Why this priority**: DoD exige "sobe com um comando, lint limpo, testes passando".

**Independent Test**: `docker compose up --build` responde 200 em `/` e em `/healthz/`; `uv run ruff check .` e `uv run pytest` passam.

**Acceptance Scenarios**:

1. **Given** um clone limpo, **When** o desenvolvedor executa `docker compose up --build`, **Then** banco e aplicação sobem, as migrações rodam e o site responde.
2. **Given** o ambiente de dev, **When** executa `uv run pytest`, **Then** os testes da fundação passam.
3. **Given** `DEBUG` ausente no ambiente, **When** a aplicação inicia, **Then** roda com `DEBUG=False` (default seguro) e falha cedo sem `SECRET_KEY` em produção.

### Edge Cases

- `ConfiguracaoSite` ainda não existe no banco: o layout usa os defaults com `[DEFINIR]`, sem erro 500.
- JavaScript desabilitado: links da navegação continuam acessíveis (o menu "Todas as Categorias" é um link para o catálogo; o painel é um realce).
- Usuário com `prefers-reduced-motion`: transições do menu e do header são desligadas.
- Erro 500: página simples, sem dependência de banco.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE ter settings separados por ambiente (base, dev, prod, test), lidos de variáveis de ambiente, com `DEBUG=False` por padrão.
- **FR-002**: O sistema DEVE ter os apps `core`, `catalogo`, `orcamentos`, `conteudo` e `seo` registrados (os três últimos podem nascer vazios).
- **FR-003**: O sistema DEVE oferecer um singleton de configuração do site (nome, contatos, WhatsApp, e-mails de destino, redes sociais, IDs de analytics, textos padrão de mensagens) editável no admin e disponível em todos os templates.
- **FR-004**: O layout base DEVE reproduzir a estrutura do header e do footer da referência (ver `docs/engenharia-reversa/componentes.md`) usando os tokens visuais "Campo".
- **FR-005**: O layout DEVE ter skip link, landmarks (`header`, `nav`, `main`, `footer`) e um único `<h1>` por página, definido pela página filha.
- **FR-006**: O sistema DEVE responder 404 com template próprio e `noindex`, e 500 com template estático.
- **FR-007**: O sistema DEVE expor `/healthz/` que responde 200 quando a aplicação e o banco estão acessíveis.
- **FR-008**: O admin DEVE usar o tema interno (Jazzmin) e bloquear tentativas repetidas de login (axes).
- **FR-009**: O repositório DEVE ter lint/format (ruff), testes (pytest), Dockerfile, docker-compose e `.env.example` sem valores secretos.
- **FR-010**: Itens de menu que dependem de features futuras (categorias, coleções) DEVEM renderizar listas vazias sem quebrar.

### Key Entities

- **Configuração do site**: registro único com nome do site, contatos, número de WhatsApp, e-mails de destino, redes sociais, IDs de GTM e Pixel, textos padrão de mensagens e rótulo do menu de coleções.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um desenvolvedor novo sobe o site localmente em até 10 minutos seguindo o README.
- **SC-002**: As páginas `/` e 404 não têm rolagem horizontal em 390, 768 e 1440 px.
- **SC-003**: axe não aponta violações críticas ou sérias no layout base.
- **SC-004**: 100% dos testes e do lint passam no estado entregue.

## Assumptions

- O logo da ISF não existe ainda (P1): usamos wordmark textual.
- Paleta provisória "Campo" (P2). Tipografia Manrope + JetBrains Mono servida localmente (sem CDN de fontes, por LGPD e performance).
- O menu "Datas Especiais" usa o rótulo configurável de coleções.
- Busca, catálogo, orçamento e páginas institucionais apontam para rotas reservadas que serão implementadas nas features seguintes.
