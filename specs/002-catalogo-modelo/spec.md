# Feature Specification: Modelo do catálogo, admin, importação e dados de demonstração

**Feature Branch**: `002-catalogo-modelo`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "002-catalogo-modelo: models, admin, importação e dados de demonstração (ver 6.4 e 6.5 do prompt)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Equipe troca o catálogo inteiro por planilha (Priority: P1)

A equipe comercial recebe o catálogo real (ou uma parte dele) numa planilha. Ela roda a importação em modo de simulação, lê o relatório de erros por linha, corrige a planilha e importa de verdade. Rodar a mesma planilha de novo não duplica nada: produtos e variações são atualizados pelo código (SKU). Depois remove os dados de demonstração com um comando.

**Why this priority**: requisito central (6.5): o catálogo ainda não existe e precisa ser substituível sem alterar código.

**Independent Test**: importar `docs/exemplos/modelo-catalogo.xlsx` com `--dry-run` (nada gravado, relatório gerado), depois sem `--dry-run` (produtos criados), de novo (0 criados, N atualizados) e rodar `limpar_catalogo_demo` (só itens de demonstração somem).

**Acceptance Scenarios**:

1. **Given** uma planilha válida, **When** a importação roda com simulação, **Then** o relatório mostra quantos produtos, variações e categorias seriam criados ou atualizados e nada é gravado.
2. **Given** uma planilha com uma linha sem nome e outra com atributo inválido, **When** a importação roda, **Then** o relatório aponta as duas linhas com o motivo e as linhas válidas são importadas.
3. **Given** um produto já importado, **When** a mesma planilha é importada de novo com outro nome, **Then** o produto existente é atualizado (mesmo SKU) e nenhuma duplicata é criada.
4. **Given** produtos de demonstração e produtos reais, **When** a limpeza de demonstração roda, **Then** só os registros de demonstração são removidos.
5. **Given** acesso ao admin, **When** a equipe envia a planilha pela tela de importação, **Then** vê o mesmo relatório e pode escolher simular ou importar.

---

### User Story 2 - Equipe define atributos técnicos por categoria, sem programador (Priority: P1)

No admin, a equipe define para cada categoria os atributos técnicos esperados (ex.: vazão em L/h, diâmetro em mm), o tipo de cada um, a unidade e se ele gera variação. Ao cadastrar um produto, a ficha técnica é validada contra essa definição.

**Why this priority**: princípio III (atributos são dados, não código).

**Independent Test**: criar uma categoria com um atributo numérico "vazão (L/h)", tentar salvar um produto com "vazão = abc" (erro) e com "vazão = 2" (salva).

**Acceptance Scenarios**:

1. **Given** uma categoria com atributo numérico obrigatório, **When** um produto é salvo sem ele ou com texto, **Then** o admin mostra o erro no campo.
2. **Given** um atributo do tipo lista de opções, **When** o produto usa um valor fora da lista, **Then** o salvamento é recusado.
3. **Given** um atributo que gera variação, **When** variações são cadastradas, **Then** cada uma informa um valor válido e duas variações iguais do mesmo produto são recusadas.
4. **Given** uma subcategoria, **When** o produto é cadastrado nela, **Then** valem os atributos da subcategoria somados aos da categoria pai.

---

### User Story 3 - Site nasce com catálogo de demonstração (Priority: P2)

Ao subir o projeto pela primeira vez, a equipe carrega um catálogo fictício de irrigação (~40 produtos, 9 categorias, 2 coleções) com imagens placeholder geradas, todo marcado como demonstração.

**Why this priority**: permite construir e validar navegação, produto e orçamento antes do catálogo real.

**Independent Test**: rodar o carregamento de demonstração e verificar contagens, imagens e marcação de demonstração.

**Acceptance Scenarios**:

1. **Given** um banco vazio, **When** o carregamento de demonstração roda, **Then** existem cerca de 40 produtos ativos em 6 a 9 categorias e 2 coleções, todos marcados como demonstração e com imagem.
2. **Given** o catálogo de demonstração já carregado, **When** o carregamento roda de novo, **Then** nada é duplicado.

### Edge Cases

- Planilha com coluna obrigatória ausente: a importação aborta com mensagem clara antes de processar linhas.
- SKU de variação repetido em produtos diferentes: linha rejeitada.
- Imagem com URL inacessível: produto importado, aviso na linha.
- Categoria referenciada que não existe: é criada (hierarquia "Pai > Filha"), registrada no relatório.
- Remoção de atributo do schema de uma categoria com produtos que o usam: produtos continuam válidos até a próxima edição; o admin avisa.
- Árvore com mais de 2 níveis: recusada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE manter categorias em árvore de no máximo 2 níveis, com nome, endereço amigável, descrição, texto de SEO, imagem, ícone, ordem, status e definição de atributos técnicos.
- **FR-002**: O sistema DEVE manter coleções (equivalente a "Datas Especiais") com período opcional, prazo de pedido opcional, destaque na home, cor e ordem.
- **FR-003**: Produtos DEVEM ter nome, endereço amigável, SKU único, descrições curta e completa, categoria principal, categorias adicionais, coleções, atributos técnicos, quantidade mínima, múltiplo, unidade de venda, status, destaque, data limite de "novidade" e marcação de demonstração.
- **FR-004**: Atributos de produtos e variações DEVEM ser validados contra a definição da categoria principal (e da categoria pai), por tipo (texto, número, sim/não, lista de opções), obrigatoriedade e opções.
- **FR-005**: Variações DEVEM ter SKU único, valores para todos os atributos que geram variação, imagem opcional e status; combinações repetidas no mesmo produto são recusadas.
- **FR-006**: Imagens de produto DEVEM ter texto alternativo, tipo (produto ou aplicação em campo), ordem e versões reduzidas em WebP geradas automaticamente.
- **FR-007**: A importação DEVE aceitar CSV e XLSX, ser idempotente por SKU, criar ou atualizar categorias, coleções, produtos, variações e atributos, associar imagens (URL ou arquivo local), suportar simulação e gerar relatório de erros por linha.
- **FR-008**: A limpeza DEVE remover apenas registros marcados como demonstração.
- **FR-009**: A importação DEVE estar disponível por linha de comando e pelo admin, com o mesmo relatório.
- **FR-010**: O modelo da planilha DEVE estar documentado, com planilha-exemplo.

### Key Entities

- **Categoria**, **Coleção**, **Produto**, **Variação**, **Imagem de produto**: ver data-model.md.
- **Importação de catálogo**: registro de cada importação feita pelo admin (arquivo, simulação, relatório, autor, data).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma planilha de 500 linhas é importada em menos de 1 minuto (sem download de imagens).
- **SC-002**: Reimportar a mesma planilha cria 0 registros novos.
- **SC-003**: 100% das linhas inválidas aparecem no relatório com número da linha e motivo.
- **SC-004**: Trocar o catálogo de demonstração pelo real não exige nenhuma alteração de código.

## Assumptions

- Os atributos técnicos de demonstração são fictícios (P15). Nomes de categorias são provisórios (P9).
- Descrições são texto simples com parágrafos (sem HTML livre), para evitar conteúdo inseguro vindo de planilha.
- Sem preço, estoque ou frete (princípio IX).
