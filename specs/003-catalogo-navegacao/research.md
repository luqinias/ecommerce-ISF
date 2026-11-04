# Research: Navegação

| # | Decisão | Motivo |
|---|---|---|
| R1 | Ordem "Mais relevantes" = `-featured, -relevance, name`; "Novidades" = `-created_at`; "Nome" = `name` | Mapeia "menu_order/date/title" da referência para campos do modelo |
| R2 | Parâmetros `?ordem=relevantes|novidades|nome` e `?tipo=<slug>` | pt-BR e estáveis; `tipo` igual à referência |
| R3 | Categoria raiz lista produtos dela e das filhas (`categories__in`) + `distinct()` | Equivale ao comportamento do WooCommerce |
| R4 | Busca: `icontains` por termo (AND entre termos, OR entre campos) | Simples, sem dependência; volume pequeno |
| R5 | Sugestões: endpoint `/busca/sugestoes/` devolve partial; sem JS, o form leva a `/busca/` | Progressivo |
| R6 | `/page/1/` → 301 para a URL sem página; página fora do intervalo → 404 | Evita conteúdo duplicado |
