# Contrato de rotas: Fundação

| Rota | Método | Resposta | Notas |
|---|---|---|---|
| `/` | GET | 200 HTML (home provisória, substituída na 006) | 1 `h1` |
| `/healthz/` | GET | 200 `{"status":"ok"}` · 503 `{"status":"erro"}` | sem cache |
| `/admin/` | GET/POST | admin Jazzmin | axes |
| rota inexistente | GET | 404 HTML com `robots noindex` | dentro da moldura |
| erro interno | — | 500 HTML estático | sem banco |

Contexto global (context processors): `site` (SiteConfiguration), `menu_categorias`, `menu_colecoes` (vazias até 002), `lista_orcamento_total` (0 até 005). Template tag `{% whatsapp_url mensagem %}`.
