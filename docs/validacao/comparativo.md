# Comparativo estrutural: referência × ISF (Fase 4)

> Os mesmos scripts e viewports da Fase 1 (`tools/engenharia_reversa/captura.py local`, `breakpoints.py`) foram rodados contra o sistema local em **modo produção** (`docker compose up --build`: gunicorn, PostgreSQL, WhiteNoise). As tabelas numéricas foram geradas por `tools/validacao/comparar.py` e estão completas em [`tabelas-geradas.md`](tabelas-geradas.md).
> **Como o conteúdo é diferente, comparamos estrutura e não pixels:** ordem das seções, grids, proporções, tokens e comportamentos.
>
> As imagens lado a lado ficam em `docs/validacao/lado-a-lado/{tipo}-{viewport}.png` (geradas por `tools/validacao/lado_a_lado.py`). Assim como os screenshots da referência, elas ficam **fora do git**, porque são material de estudo com conteúdo de terceiros. Para regenerar: rode a captura (seção 6) e depois o script.

## 1. Resumo

| Critério (Fase 4 / DoD) | Resultado |
|---|---|
| Todos os tipos de página do inventário existem | ✅ 13 tipos capturados (home, catálogo, categoria, subcategoria, coleção, produto, busca, novidades, sobre, contato, orçamento, termos/privacidade, 404) + blog opcional. Landings de segmento ficam fora (gap analysis) |
| Layout segue a referência nos 3 viewports | ✅ Mesma ordem de seções e mesmas colunas de grade em 390/768/1440 (tabelas abaixo), com divergências justificadas na seção 4 |
| Sem rolagem horizontal em 390 px | ✅ em todas as páginas |
| axe sem violações críticas ou sérias | ✅ 0 em todas as páginas (a referência tem 1 a 3 regras sérias/críticas por página) |
| LCP e CLS iguais ou melhores que a referência | ✅ LCP de 52–240 ms (referência: 240–2184 ms); CLS 0 em todas (referência chega a 0,146) |
| Comportamentos | ✅ cobertos por E2E (seção 3) |

## 2. Estrutura

### 2.1 Ordem das seções da home (1440 px)

| # | Referência | ISF | Componente |
|---|---|---|---|
| 1 | Hero com selo de datas, h1, CTAs, cards de prova, mosaico e cards flutuantes | Igual, com selo de coleções | H01 |
| 2 | Vitrine "Escolha pelo que…" com 6 trilhos | Vitrine com trilho de recém-chegados + categorias marcadas | H02/H03 |
| 3 | Próximas datas (3 cards) + banner largo | Coleções em destaque + banner da coleção principal | H04 |
| 4 | Portfólio masonry com "Ver mais" | Igual (projetos e instalações) | H05 |
| 5 | Tiles das maiores categorias | Igual | H06 |
| 6 | Como funciona (4 passos) | Igual | H07 |
| 7 | Faixa escura de prazos | Igual (prazos por coleção) | H08 |
| 8 | Por que nós + depoimentos | Igual; depoimentos ocultos até haver um autorizado | H09/H10 |
| 9 | FAQ em acordeão | Igual | H11 |

Produto: galeria · resumo (breadcrumb, selo, h1, código, descrição curta, seletor, quantidade, botão, garantias) · descrição + ficha técnica · relacionados, na mesma sequência. A seção "Avaliações" foi excluída de propósito (seção 4).

### 2.2 Grids (colunas visíveis)

| Página | Componente | Ref 390 | ISF 390 | Ref 768 | ISF 768 | Ref 1440 | ISF 1440 |
|---|---|---|---|---|---|---|---|
| categoria / catálogo | Grade de produtos | 2 | 2 | 3 | 3 | 5 | 5 |
| produto | Relacionados | 2 | 2 | 3 | 3 | 5 | 5 |
| home | Tiles de categoria | 2 | 2 | 4 | 4 | 6 | 6 |
| home | Como funciona | 2 | 2* | 2 | 2 | 4 | 4 |
| home | Portfólio | 2 | 2 | 2 | 2 | 4 | 4 |
| home | Cards de coleção/data | 1 | 1 | 1 | 1 | 3 | 3 |
| home | Trilho da vitrine (cards por linha) | 2,1 visíveis | 2,15 visíveis | 4,5 | 4,3 | 6 | 6 |

\* Corrigido nesta fase (antes: 1 coluna no celular). Portfólio vem de `breakpoints_local.json` e coleções, do CSS: a demo tem uma única coleção em destaque fora do banner, e o extrator genérico só mede grids com 3 ou mais itens visíveis. Na referência, o trilho tem 10 itens por bloco; na demo, até 8, porque há menos produtos por categoria (diferença de dados, não de layout).

### 2.3 Breakpoints

| Mudança | Referência (px) | ISF (px) |
|---|---|---|
| Grade 2→3, tiles 2→4, mosaico do hero, busca no header | 640–680 | 640 |
| Grade 3→4 | 820 | 960 |
| Rodapé 1→3, como funciona 2→4 | 920–960 | 960 |
| Navegação desktop e CTA (some o hambúrguer) | 1080 | 1100 |
| Grade 4→5, coleções 1→3, portfólio 2→4, tiles 4→6 | 1100 | 1100 |

Os 7 breakpoints da referência foram consolidados em 4 (`sm 640`, `md 768`, `lg 960`, `xl 1100`), como decidido em `design-tokens.md`. Nos três viewports de validação o resultado é idêntico.

### 2.4 Tokens e métricas de componentes (1440 px)

| Componente | Referência | ISF | Observação |
|---|---|---|---|
| Container | 1220–1320 px | 1280 px − gutter 32 = 1216 px úteis | dentro da faixa |
| Faixa superior / header / nav | 46 / 65 / 72 px | 44 / 68 / 64 px | proporção mantida |
| Botões e chips | pílula (raio 100 px) | pílula (raio 999 px) | igual |
| Cards de produto, tiles, painéis | raio 16 px, borda clara, hover −4 px + sombra | raio 16 px, borda clara, hover −4 px + sombra | igual |
| Cards grandes (passos, coleções, depoimentos) | raio 20 px | raio 20 px | igual |
| h1 de página / h2 de seção | 38–40 px / 40 px | 40 px / 36 px (`clamp`) | escala fluida |
| Tipografia | Fraunces + Inter | Manrope + JetBrains Mono | identidade ISF provisória ("Campo"), P2 |
| Cores | petróleo, ouro, escuro, creme | verde-floresta, ouro, "Mata Noturna", papel | mesmos papéis, paleta da empresa (P2) |
| Foco | `outline 3px dotted` | contorno 2 px + anel 3 px | mais visível (WCAG) |

## 3. Comportamentos (verificados por E2E em `tests/e2e/`)

| Comportamento | Referência | ISF | Teste |
|---|---|---|---|
| Dropdown "Todas as Categorias" (hover/clique, Esc) | ✔ | ✔ | `test_moldura.py` |
| Menu mobile (abre, fecha no X/overlay/Esc, trava rolagem) | ✔ | ✔ | `test_moldura.py` |
| Chips com contagem, ordenação, paginação | ✔ | ✔ | `test_navegacao.py` |
| Sugestões de busca ao digitar | ✔ | ✔ (HTMX) | `test_navegacao.py` |
| Variação bloqueia o botão + aviso | ✔ | ✔ | `test_produto.py` |
| Quantidade mínima com +/− (e múltiplo) | ✔ | ✔ | `test_produto.py` |
| Adicionar ao orçamento + contador | ✔ (redireciona) | ✔ (toast, fica na página) | `test_orcamento.py` |
| Revisar e enviar → WhatsApp com os itens | ✔ | ✔ + gravação do lead + e-mails | `test_orcamento.py` |
| Orçamento rápido (wa.me) | ✔ | ✔ | `test_orcamento.py` |
| FAQ não exclusivo, "Ver mais" do portfólio | ✔ | ✔ | `test_home.py` |
| "Carregar mais" em novidades | ✔ | ✔ (HTMX) | `test_home.py` |
| Banner de cookies e reabertura pelo rodapé | ✔ | ✔ | `test_cookies.py` |
| Rastreadores só após "Aceitar todos" | ✗ (scripts no HTML) | ✔ | `test_cookies.py` |
| Header sticky, rolar para cima, galeria, descrição expansível | ✔ | ✔ | revisão visual + unit |

## 4. Divergências intencionais

| # | Divergência | Justificativa |
|---|---|---|
| D1 | Identidade visual (cores, fontes, logo) | Princípio II: a fidelidade é na forma, não na marca. Tokens "Campo" até a ISF entregar a marca (P1, P2) |
| D2 | Ao adicionar ao orçamento, a página não redireciona | Facilita montar uma lista com vários itens. O toast leva à lista (gap analysis) |
| D3 | Contador = número de itens, não soma de quantidades | Unidades diferentes (metro, rolo, peça) não se somam |
| D4 | Seletor de variação em pílulas de texto, não swatches de cor | Atributos técnicos (vazão, diâmetro), definidos por categoria |
| D5 | Sem avaliações de produto, zoom no hover, tags, landings de segmento e SEO local | `gap-analysis.md` (princípio IX e pendências P13) |
| D6 | Vitrines, menus e listagens renderizados no servidor | Elimina o CLS de 0,13 a 0,15 da referência e funciona sem JS |
| D7 | Passos 1 e 2 do orçamento na mesma página | Uma navegação a menos. O passo 3 continua sendo uma página própria |
| D8 | Produto em 2 colunas a partir de 960 px (referência: 1100 px) | Melhor uso do tablet na horizontal |
| D9 | Depoimentos ocultos sem conteúdo autorizado | Regra de não inventar depoimentos (P17) |
| D10 | Mapa do contato como link, sem iframe | Nenhum recurso de terceiros antes do consentimento (LGPD) |
| D11 | Títulos e textos próprios | Os textos padrão foram reescritos. Uma varredura automática das frases da referência contra o código só encontra rótulos funcionais citados no prompt ("Adicionar ao orçamento", "Solicitar orçamento rápido", "Ler descrição completa", "Você também pode gostar", "Todas as Categorias") e termos genéricos ("Política de privacidade", "Preferências de cookies") |

## 5. Problemas encontrados e corrigidos nesta fase

| Problema | Correção |
|---|---|
| Kicker dourado com contraste 4,44:1 em fundo creme (axe, sério) | Token `--accent` de `#9a6400` para `#8a5900` (≥ 5:1 em todos os fundos) |
| Faixa superior fora de landmarks (axe `region`) | Virou `<aside aria-label="Atendimento">` |
| "Como funciona" em 1 coluna no celular | 2 colunas, como na referência |
| Frases de marketing da referência reaproveitadas como texto padrão | Reescritas (D11) |
| Erro 500 em produção por falta do manifest de estáticos (só aparecia no container) | `collectstatic` com settings de produção no build + teste de regressão `test_estaticos_producao.py` |
| Mídia sem tipo `image/webp` na imagem slim; `.env` sobrescrevendo variáveis do compose local | Tipos MIME registrados; valores fixos no compose local |
| Banner de cookies com `id="cookies"`, o mesmo da âncora da política de privacidade | Renomeado para `aviso-cookies` |

## 6. Como reproduzir

```bash
docker compose up -d --build
uv run python tools/engenharia_reversa/captura.py local http://localhost:8000   # → docs/validacao/{raw,screenshots}
uv run python tools/engenharia_reversa/breakpoints.py http://localhost:8000     # → docs/engenharia-reversa/raw/breakpoints_local.json
uv run python tools/validacao/comparar.py > docs/validacao/tabelas-geradas.md
uv run python tools/validacao/lado_a_lado.py                                    # requer as capturas da Fase 1
uv run pytest && uv run pytest -m e2e
```
