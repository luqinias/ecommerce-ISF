# Feature Specification: Navegação do catálogo

**Feature Branch**: `003-catalogo-navegacao`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "003-catalogo-navegacao: catálogo geral, páginas de categoria e subcategoria, coleções, chips com contagem, ordenação, paginação (30 por página), busca simples, menu 'Todas as Categorias'."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegar por categoria, filtrar, ordenar e paginar (Priority: P1)

O produtor abre "Todas as Categorias", entra em "Gotejamento", vê o total de produtos, filtra pelos chips de categorias relacionadas (com contagem), ordena por "Novidades" e passa para a página 2.

**Why this priority**: é o caminho principal de descoberta (fluxo 1 de `fluxos.md`).

**Independent Test**: com o catálogo de demonstração, abrir uma categoria com mais de 30 produtos (ou o catálogo geral), conferir 30 cards, a paginação, a contagem dos chips e a ordem por nome.

**Acceptance Scenarios**:

1. **Given** uma categoria com N produtos ativos, **When** a página abre, **Then** mostra breadcrumb, título, descrição, "N produtos", chips "Todos" + categorias relacionadas com contagem, seletor "Ordenar" (Mais relevantes, Novidades, Nome A–Z), até 30 cards e paginação numerada com "Mostrando 1–30 de N produtos".
2. **Given** a listagem, **When** o visitante escolhe "Nome (A–Z)", **Then** os produtos aparecem em ordem alfabética e o filtro escolhido é mantido.
3. **Given** um chip "Filtragem 4", **When** clicado, **Then** a listagem mostra os 4 produtos que estão nas duas categorias e o chip fica ativo.
4. **Given** uma subcategoria, **When** acessada, **Then** o endereço inclui a categoria pai e o breadcrumb mostra Início › Pai › Filha; a categoria pai lista também os produtos das filhas.
5. **Given** a página 99 inexistente, **When** acessada, **Then** retorna 404.

---

### User Story 2 - Buscar um produto pelo nome ou código (Priority: P1)

O visitante digita "filtro" na busca do header: aparecem sugestões enquanto digita; ao confirmar, vê a página de resultados no mesmo layout das listagens.

**Why this priority**: atalho de quem já sabe o que quer.

**Independent Test**: buscar por um trecho do nome e por um SKU de variação.

**Acceptance Scenarios**:

1. **Given** produtos com "filtro" no nome, **When** a busca é feita, **Then** a página mostra "Resultados para "filtro"", a contagem e os cards.
2. **Given** um SKU de variação, **When** buscado, **Then** o produto dele aparece.
3. **Given** a digitação de 2 ou mais letras, **When** o visitante pausa, **Then** até 6 sugestões aparecem com foto, nome e categoria, mais "Ver todos os resultados".
4. **Given** uma busca sem resultado, **When** feita, **Then** aparece um estado vazio com sugestões de categorias e o atalho de WhatsApp.

---

### User Story 3 - Explorar coleções e o catálogo geral (Priority: P2)

O visitante abre uma coleção pelo menu ("Coleções ▾") ou o catálogo geral ("Ver todos os produtos"); no catálogo geral, os chips mostram as maiores categorias e "Ver todas as categorias" abre a lista completa.

**Acceptance Scenarios**:

1. **Given** uma coleção vigente, **When** aberta, **Then** mostra o período/prazo, os produtos e chips por categoria.
2. **Given** uma coleção fora do período ou inativa, **When** acessada, **Then** retorna 404.
3. **Given** o catálogo geral, **When** aberto, **Then** mostra todos os produtos ativos, chips das maiores categorias e o botão para ver todas.

### Edge Cases

- `?ordem=` desconhecido → usa "Mais relevantes".
- `?tipo=` de categoria inexistente → ignorado.
- `/page/1/` → redireciona para a URL sem página.
- Categoria inativa → 404; produto inativo nunca aparece.
- Subcategoria acessada pela URL de raiz → redireciona para a URL canônica.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Listagens de catálogo geral, categoria, subcategoria, coleção e busca DEVEM compartilhar a mesma estrutura (hero, barra de chips e ordenação, grade, paginação, ajuda por WhatsApp, texto de SEO).
- **FR-002**: Paginação DEVE ter 30 produtos por página, numerada, em URLs `/page/N/`.
- **FR-003**: Ordenação DEVE oferecer Mais relevantes (destaque e relevância), Novidades (mais recentes) e Nome (A–Z).
- **FR-004**: Chips DEVEM mostrar categorias relacionadas aos produtos da listagem com a contagem real da interseção.
- **FR-005**: Busca DEVE procurar em nome, SKU (produto e variação), descrição curta e categoria, com todos os termos.
- **FR-006**: Sugestões de busca DEVEM aparecer sem recarregar a página.
- **FR-007**: Listagens filtradas, ordenadas e de busca DEVEM ser `noindex` e ter canonical para a URL limpa.
- **FR-008**: O menu "Todas as Categorias" e o menu de coleções DEVEM listar as categorias e coleções ativas.
- **FR-009**: Cards DEVEM mostrar imagem, selos (Novo, Destaque, Demonstração), quantidade de opções, nome e "Ver produto →", sem preço.

## Success Criteria *(mandatory)*

- **SC-001**: Do menu à página 2 de uma categoria ordenada em 3 cliques.
- **SC-002**: Sugestões de busca aparecem em menos de 1 s após a pausa na digitação.
- **SC-003**: Listagens sem rolagem horizontal em 390 px e com 2/3/5 colunas em 390/768/1440 px.
- **SC-004**: Listagem com 30 produtos sem consultas N+1 (número de consultas constante).

## Assumptions

- Chips de categoria usam `?tipo=<slug>`, como na referência.
- A busca é simples (contém/termos); busca textual avançada fica fora do escopo.
