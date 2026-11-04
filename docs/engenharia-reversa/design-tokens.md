# Design tokens (Fase 1)

> Fonte de verdade em máquina: [`design-tokens.json`](design-tokens.json). Medido com `getComputedStyle` nos elementos-chave (`raw/captura.json`, chave `estilos`) e com varredura de largura de 320 a 1600 px (`raw/breakpoints.json`).
> **Regra:** da referência vêm **métricas** (proporções, alturas, grids, raios, sombras, breakpoints). **Cores e fontes** vêm do design system "Campo" da Fase 0 até a ISF entregar a marca (pendências P1 e P2).

## 1. Cores

A referência usa uma paleta de 4 papéis: **escuro** (`#1E2530`, faixa superior, rodapé, faixa de prazos, botão "Todas as Categorias"), **primária** petróleo (`#4E8E9E`/`#3A7382`, botões e links), **acento** ouro (`#C9A76B`, CTA de orçamento, kickers, traços) e **creme** (`#F4F1E9`, fundos de seção alternados com branco).

O projeto mantém os mesmos **papéis** com a paleta "Campo":

| Papel na referência | Referência | ISF (token CSS) |
|---|---|---|
| Fundo de seção alternado | `#F4F1E9` | `--bg` `#f5f4ef` |
| Superfície (cards, header) | `#FFFFFF` | `--surface` `#ffffff` |
| Barra de navegação | `#EDE8DC` | `--surface-3` `#e6e3da` |
| Fundo de card de produto | `#FBFAF6` | `--surface-card` `#faf9f5` |
| Bordas | `#EDE8DC` / `#CFC8B8` | `--border` `#dedad0` / `--border-strong` `#c7c2b5` |
| Texto | `#1E2530` | `--fg` `#1a1f1b` |
| Texto suave | `#5A6270` | `--fg-muted` `#555d56` |
| Primária (ação) | `#4E8E9E` | `--primary` `#1d6a44` (hover `#17573a`) |
| Acento / CTA de orçamento | `#C9A76B` | `--brand-gold` `#f2b01e` (fundo, texto escuro) · `--accent` `#9a6400` (texto) |
| Superfície escura | `#1E2530` | `--dark` `#11251a` ("Mata Noturna") |
| Texto sobre escuro | `#C7CBD2` | `--on-dark` `#e7ece8` / `--on-dark-muted` `#a3aea6` |

Contraste: a referência tem violações `color-contrast` em todas as páginas (kicker dourado sobre branco, cinzas claros). No projeto, o ouro **nunca** é usado como texto sobre fundo claro (regra "Campo"); kickers usam `--accent` `#9a6400` (AA sobre `#f5f4ef`).

## 2. Tipografia

| Uso | Referência | ISF |
|---|---|---|
| Títulos | Fraunces 600 (serifada) | Manrope 800, `letter-spacing: -0.025em` |
| Corpo | Inter 400, 16/26,4 | Manrope 400, 16/1,6 |
| Código/SKU | Inter | JetBrains Mono, `tabular-nums` |
| h1 hero | 56/62,7, -0,5 px | `clamp(2.25rem, 4vw + 1rem, 3.5rem)` |
| h1 de página / h2 | 40/46 | `clamp(1.625rem, 1.5vw + 1rem, 2.5rem)` |
| h3 | 22/28,6 | 1,375 rem |
| Subtítulo (lead) | 17/28 | 1,0625 rem |
| Navegação | 14,5 / 700 | 0,9 rem / 700 |
| Botão | 15 / 600 | 0,9375 rem / 700 |
| Kicker | 13 / 700, caixa alta, 2,5 px | 0,8125 rem / 800, caixa alta, 0,16 em |
| Breadcrumb | 13 | 0,8125 rem |
| Selo | 11 / 700 | 0,6875 rem / 800 |

O recurso de "palavra em itálico colorido" no h1/h2 (ex.: "marca ser *lembrada*") é reproduzido com `<em>` estilizado (`--primary`, sem itálico serifado, peso 800).

Fontes servidas localmente (`static/fonts/`, WOFF2), sem Google Fonts: evita requisição a terceiros antes do consentimento (LGPD) e melhora LCP.

## 3. Espaço, raio, sombra, movimento

- **Seções:** padding vertical 56–80 px no desktop, 40–48 px no mobile. Fundo alterna branco/creme como na referência.
- **Gaps:** 14 px (cards de vitrine, tiles, portfólio), 16 px (grade de produtos; 10 px no mobile), 22 px (datas), 48 px (colunas do rodapé e do produto).
- **Raios:** pílula para botões, chips, selos, busca e select de ordenação; 16 px para cards de produto, painéis e acordeão; 20 px para cards grandes (datas, passos, depoimentos, banner); 12 px para inputs (Campo).
- **Sombras:** "flat-at-rest" — cards sem sombra em repouso, sombra média no hover. Painéis/dropdowns `--shadow-md`; banner de cookies `--shadow-lg`; barra de navegação `--shadow-nav`.
- **Movimento:** hover de card `translateY(-4px)` + sombra em 250 ms; menu mobile 300 ms; tudo desligado em `prefers-reduced-motion`.

## 4. Layout e breakpoints

| Medida | Referência | ISF |
|---|---|---|
| Container | 1220 px (header/listas), 1320 px (home, padding 32), 1200 px (rodapé) | `--container: 1280px` com gutter 16/24/32 → área útil ≈ 1216–1256 px |
| Container estreito | 900 px (FAQ, texto SEO) | `--container-narrow: 900px` |
| Faixa superior | 46 px | 44 px |
| Header principal | 65 px | 68 px |
| Barra de navegação | 72 px | 64 px |

Breakpoints reais (varredura de 10 em 10 px): **640, 680, 820, 920, 960, 1080, 1100**. O projeto consolida em 4, com o mesmo efeito nos 3 viewports de validação:

| Token | Largura | O que muda (igual à referência) |
|---|---|---|
| base | < 640 | 1 coluna; grade de produtos 2; tiles 2; trilho com 2,1 cards visíveis; header compacto com hambúrguer |
| `sm` | ≥ 640 | grade 3; tiles 4; mosaico do hero; busca no header |
| `md` | ≥ 768 | rodapé 2 col.; depoimentos 3 col. |
| `lg` | ≥ 960 | grade 4; como funciona 4; rodapé 3 col.; produto em 2 colunas |
| `xl` | ≥ 1100 | grade 5; navegação desktop + CTA; datas 3; portfólio 4; tiles 6 |

> A referência mostra o produto em 1 coluna até 1100 px e o rodapé em 3 colunas a partir de 960 px. No projeto, o produto vira 2 colunas a partir de 960 px (melhor uso de tablet em paisagem). Divergência intencional, registrada em `docs/validacao/comparativo.md`.
