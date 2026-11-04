# Rotas: Navegação

| Rota | Parâmetros | Resposta |
|---|---|---|
| `/produtos/` · `/produtos/page/<n>/` | `ordem`, `tipo` | listagem de todos os ativos |
| `/categoria-produto/<slug>/` (+ `/page/<n>/`) | `ordem`, `tipo` | categoria raiz (inclui filhas); subcategoria → 301 para a URL com pai |
| `/categoria-produto/<pai>/<slug>/` (+ `/page/<n>/`) | `ordem`, `tipo` | subcategoria; pai errado → 404 |
| `/colecao/<slug>/` (+ `/page/<n>/`) | `ordem`, `tipo` | coleção vigente |
| `/busca/` | `q`, `ordem` | resultados (noindex) |
| `/busca/sugestoes/` | `q` (≥ 2 letras) | partial HTML com até 6 produtos |
