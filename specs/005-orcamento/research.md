# Research: Orçamento
| # | Decisão | Motivo |
|---|---|---|
| R1 | Itens da sessão como `{"<produto>:<variação>": quantidade}` | Pequeno, serializável; dados sempre lidos do banco (preço/estoque não existem) |
| R2 | Contador = número de itens (não soma de quantidades) | Unidades diferentes (metro, peça) não se somam |
| R3 | Confirmação por UUID **e** sessão | Evita expor dados pessoais a quem tenha o link |
| R4 | Abrir o WhatsApp na confirmação (mesma aba após 1,5 s, com botão de fallback) | Pop-up é bloqueado; o pedido já está gravado antes |
| R5 | Rate limit: 5 envios / 10 min por IP (hash do IP só na chave do cache, nunca no banco) | LGPD + C11 |
| R6 | Código legível `ORC-AAAA-NNNNN` sequencial por ano | Referência na conversa com o cliente |
