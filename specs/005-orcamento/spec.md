# Feature Specification: Lista e pedido de orçamento

**Feature Branch**: `005-orcamento` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "005-orcamento: lista de orçamento na sessão, contador no header (HTMX), página de revisão, formulário (nome, empresa, e-mail, telefone/WhatsApp, cidade/UF, mensagem), gravação do Orcamento no banco, e-mail para a equipe e confirmação para o cliente, redirecionamento para wa.me com mensagem gerada a partir dos itens. Inclui também o botão 'orçamento rápido' (WhatsApp direto). Proteção anti-spam com honeypot e limite de taxa."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Montar a lista sem sair da página (Priority: P1)
O visitante adiciona produtos (com variação e quantidade) à lista; o contador do header atualiza na hora e um aviso oferece "Ver lista". O mesmo produto/variação adicionado de novo soma a quantidade.

**Acceptance Scenarios**:
1. **Given** um produto com variação escolhida, **When** "Adicionar ao orçamento", **Then** o contador soma 1 item e aparece "Adicionado à lista · Ver lista" sem recarregar.
2. **Given** a mesma variação, **When** adicionada de novo, **Then** a quantidade é somada e o número de itens não muda.
3. **Given** um envio sem variação (ou com variação de outro produto, ou quantidade abaixo do mínimo), **When** chega ao servidor, **Then** é recusado (variação) ou ajustado ao mínimo/múltiplo (quantidade).
4. **Given** JavaScript desligado, **When** o formulário é enviado, **Then** o item entra na lista e o visitante vai para a página da lista.

### User Story 2 - Revisar e enviar o pedido (Priority: P1)
Na página "Vamos preparar seu orçamento" (passos 1 Seus produtos · 2 Seus dados · 3 Confirmação), o visitante ajusta quantidades, remove itens, preenche nome, empresa, e-mail, telefone/WhatsApp, cidade/UF e mensagem, aceita a finalidade dos dados e envia. O pedido é gravado, a equipe recebe e-mail, o cliente recebe confirmação e a página de confirmação abre o WhatsApp com a mensagem gerada dos itens.

**Acceptance Scenarios**:
1. **Given** itens na lista, **When** a quantidade é alterada ou um item é removido, **Then** a tabela e o contador atualizam.
2. **Given** dados válidos, **When** enviado, **Then** um orçamento com status "Novo", origem "site" e itens (nome e SKU congelados) é gravado; a lista é esvaziada; dois e-mails são enviados; a confirmação mostra o código e o botão do WhatsApp com os itens.
3. **Given** e-mail ou telefone inválido, ou consentimento não marcado, **When** enviado, **Then** os erros aparecem nos campos e nada é gravado.
4. **Given** o campo-armadilha preenchido (robô), **When** enviado, **Then** nada é gravado e a resposta parece sucesso.
5. **Given** mais de 5 envios em 10 minutos do mesmo IP, **When** outro envio chega, **Then** é recusado com mensagem amigável (429).
6. **Given** falha no envio de e-mail, **When** o pedido é enviado, **Then** o orçamento continua gravado e a falha fica registrada para a equipe.

### User Story 3 - Orçamento rápido (Priority: P2)
Botões "Solicitar orçamento rápido" (header, produto, listas) abrem o WhatsApp com mensagem pronta; na página da lista, "Enviar só pelo WhatsApp" registra o pedido com origem "WhatsApp" e abre a conversa com os itens.

### User Story 4 - Equipe acompanha os pedidos (Priority: P2)
No admin, a equipe vê os orçamentos com filtros por status/origem/data, os itens, muda o status (novo, em atendimento, respondido, fechado, perdido) e exporta CSV.

### Edge Cases
- Lista vazia: página mostra estado vazio e o formulário não aparece.
- Produto desativado depois de entrar na lista: item some da lista com aviso.
- Confirmação acessível só na mesma sessão que enviou.
- WhatsApp não configurado: a confirmação não abre WhatsApp e mostra o contato.

## Requirements *(mandatory)*
- **FR-001**: Lista guardada na sessão (30 dias), sem login.
- **FR-002**: Contador no header atualizado sem recarregar.
- **FR-003**: Validação no servidor de produto, variação, quantidade mínima e múltiplo.
- **FR-004**: Formulário com nome, empresa, e-mail, telefone/WhatsApp, cidade, UF, mensagem, consentimento com finalidade declarada e link para a política.
- **FR-005**: Gravação de orçamento e itens com cópia de nome, SKU, variação e unidade.
- **FR-006**: E-mail para a equipe (destinatários configuráveis) e confirmação para o cliente, sem perder o pedido se o e-mail falhar.
- **FR-007**: Mensagem do WhatsApp gerada dos itens (produto, variação, SKU, quantidade, unidade) + código do pedido.
- **FR-008**: Honeypot e limite de taxa por IP.
- **FR-009**: Admin com status, filtros, itens e exportação CSV.

## Success Criteria *(mandatory)*
- **SC-001**: Do produto ao pedido enviado em menos de 2 minutos.
- **SC-002**: 0 pedidos perdidos por falha de e-mail.
- **SC-003**: Envios automatizados com honeypot gravam 0 registros.

## Assumptions
- Destinatários vêm de `SiteConfiguration.quote_recipient_emails` (P4); sem eles, usa o e-mail de contato e registra aviso.
- Sem Celery (C5): e-mail enviado após o commit, na mesma requisição.
