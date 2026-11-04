# Rotas: Orçamento
| Rota | Método | HTMX | Resposta |
|---|---|---|---|
| `/orcamento/` | GET | — | passos 1 e 2 |
| `/orcamento/` | POST | — | grava pedido → 303 `/orcamento/enviado/<uuid>/`; erros → 200 com form; 429 no limite |
| `/orcamento/adicionar/` | POST | sim | 204 + `HX-Trigger: isf:toast` + contador OOB · sem HTMX: 303 `/orcamento/` |
| `/orcamento/item/<chave>/` | POST (`quantidade` ou `remover`) | sim | partial dos itens + contador OOB · sem HTMX: 303 |
| `/orcamento/mini/` | GET | sim | partial da mini-lista |
| `/orcamento/whatsapp/` | POST | — | grava pedido origem WhatsApp → 303 wa.me |
| `/orcamento/enviado/<uuid>/` | GET | — | confirmação (mesma sessão), `noindex` |
