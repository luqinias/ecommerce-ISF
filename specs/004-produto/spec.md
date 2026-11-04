# Feature Specification: Página de produto

**Feature Branch**: `004-produto` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "004-produto: página de produto com galeria, seletor de variação (bloqueia o botão até a escolha), especificações técnicas renderizadas a partir dos atributos, quantidade mínima, descrição expansível, breadcrumbs, relacionados."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escolher a variação e a quantidade (Priority: P1)

O produtor abre um gotejador, vê as fotos, escolhe a vazão (2, 4 ou 8 L/h), ajusta a quantidade respeitando o mínimo e o múltiplo e só então consegue adicionar ao orçamento.

**Independent Test**: abrir um produto com variações, tentar adicionar sem escolher (aviso), escolher, ajustar quantidade abaixo do mínimo (volta ao mínimo) e adicionar.

**Acceptance Scenarios**:
1. **Given** produto com variações, **When** a página abre, **Then** o botão "Adicionar ao orçamento" aparece bloqueado e o rótulo diz "escolha uma opção".
2. **Given** botão bloqueado, **When** clicado, **Then** aparece "Escolha {atributo} para continuar." e nada é enviado.
3. **Given** a escolha de um valor, **When** feita, **Then** o botão é liberado, o código (SKU) passa a ser o da variação e a foto da variação (se houver) é exibida.
4. **Given** mínimo 100 e múltiplo 100, **When** o visitante digita 30, **Then** a quantidade volta para 100; "+" vai para 200; "−" não passa do mínimo.
5. **Given** combinação inexistente em produto com 2 atributos de variação, **When** um valor é escolhido, **Then** os valores incompatíveis do outro atributo ficam indisponíveis.

### User Story 2 - Entender o produto (Priority: P1)

O visitante lê a descrição curta, abre "Ler descrição completa", consulta a ficha técnica (gerada dos atributos), navega pelas fotos (miniaturas, setas, ampliar) e pelo breadcrumb.

**Acceptance Scenarios**:
1. **Given** atributos preenchidos, **When** a página abre, **Then** a ficha técnica lista cada atributo com unidade, mais código, unidade de venda, mínimo e opções disponíveis.
2. **Given** várias fotos, **When** uma miniatura é clicada, **Then** a foto principal muda; "ampliar" abre a foto grande num diálogo que fecha com Esc.
3. **Given** descrição longa, **When** "Ler descrição completa" é clicado, **Then** o texto expande e o botão vira "Mostrar menos".

### User Story 3 - Continuar navegando (Priority: P2)

Abaixo, "Você também pode gostar" mostra 5 produtos relacionados. No celular, uma barra fixa inferior leva ao seletor/adicionar.

### Edge Cases
- Produto sem variação: botão liberado desde o início.
- Produto sem imagem: placeholder neutro.
- Produto inativo ou de categoria inativa: 404.
- Sem JavaScript: o seletor é um formulário de rádios comum e o servidor valida a variação.

## Requirements *(mandatory)*
- **FR-001**: Galeria com imagem principal, miniaturas, anterior/próxima e ampliação acessível.
- **FR-002**: Seletor por atributo de variação, gerado da definição da categoria; botão bloqueado até combinação válida.
- **FR-003**: Quantidade com mínimo, múltiplo e unidade de venda.
- **FR-004**: Ficha técnica gerada dos atributos (nenhum atributo fixo no template).
- **FR-005**: Descrição expansível; breadcrumb Início › (pai) › categoria › produto.
- **FR-006**: Relacionados (até 5) da mesma categoria e de categorias compartilhadas.
- **FR-007**: Orçamento rápido pelo WhatsApp com produto, variação e quantidade na mensagem.
- **FR-008**: Barra fixa no mobile.

## Success Criteria *(mandatory)*
- **SC-001**: 100% das tentativas de adicionar sem variação são bloqueadas com aviso.
- **SC-002**: Nenhuma violação crítica de acessibilidade no seletor (rótulos de grupo).
- **SC-003**: CLS da página ≤ 0,1.

## Assumptions
- Avaliações de produto ficam fora (gap analysis). O envio para a lista é implementado na 005; aqui o formulário já aponta para o endpoint.
