# Catálogo de componentes da referência (Fase 1)

> Nome do componente → partial Django proposto. Medidas em 1440 px salvo indicação. Screenshots em `screenshots/` (tipo/viewport) e `screenshots/comportamentos/` (estados).
> A coluna **ISF** diz o que acontece no projeto: ✅ implementar igual (estrutura/comportamento), 🔁 adaptar, ⛔ excluir (justificado em `gap-analysis.md`).

## 1. Moldura (todas as páginas)

| # | Componente | Onde | Estrutura e medidas | Estados e comportamento | Screenshot | ISF |
|---|---|---|---|---|---|---|
| C01 | **Faixa superior** (`cda-util`) | todas | 46 px, fundo escuro `#1E2530`, texto 14 px claro. 3 colunas: frase à esquerda ("Entrega para todo o Brasil"), frase central, link "Atendimento via WhatsApp" com ícone redondo à direita. Container 1220 px | No mobile mostra só a frase central e o ícone do WhatsApp | `home/1440.png` | ✅ `partials/faixa_superior.html` |
| C02 | **Cabeçalho principal** (`cda-main-row`) | todas | 65 px, fundo branco. Logo (180×44) · busca em pílula (cresce, 44 px de altura, botão redondo de lupa) · botão da lista (44×44, círculo) com contador | Busca com **sugestões ao digitar** (painel `cda-search-results`, produtos via Store API). Contador atualiza ao adicionar | `comportamentos/busca-digitando.png` | ✅ `partials/header.html`; sugestões com HTMX (`hx-get` com `delay:300ms`) |
| C03 | **Barra de navegação** (`cda-nav-d`) | todas ≥ 1090 px | 72 px, fundo areia `#EDE8DC`, sombra `0 6px 18px rgba(30,37,48,.22)`. Botão escuro em pílula "Todas as Categorias ▾", botão claro "Datas Especiais ▾", links Novidades/Sobre Nós/Blog/Contato (14,5 px, 700), CTA dourado "Solicitar orçamento rápido" (pílula, ícone de telefone) | **Sticky:** faixa 2+3 (`cda-sticky-wrap`) fica `position: fixed` ao rolar; a faixa superior some | `comportamentos/rolado.png` | ✅ |
| C04 | **Dropdown "Todas as Categorias"** (`cda-dd-panel.cda-cats`) | header | Painel 560×790, 2 colunas de 260 px, raio 16, borda `#EEE6D6`, sombra `0 16px 40px rgba(30,37,48,.16)`, padding 14. Cada item: ícone (emoji) + nome. Rodapé "Ver todas as categorias →". **31 itens** (exclui datas especiais) | Abre no **hover** e no clique; fecha com Esc e ao sair. Itens vêm da Store API (`/products/categories`) via JS | `comportamentos/dropdown-categorias.png` | 🔁 lista renderizada no servidor (sem XHR), ícone = imagem/ícone opcional da categoria; abre por clique/hover com `aria-expanded` |
| C05 | **Dropdown "Datas Especiais"** | header | Mesmo painel, 1 coluna, datas com mês | Igual ao C04 | `comportamentos/dropdown-datas.png` | 🔁 lista de **coleções**; rótulo configurável |
| C06 | **Menu mobile** (`cda-mobile-panel`) | < 1090 px | Botão hambúrguer (círculo) à esquerda do logo. Painel lateral esquerdo 335 px (86 %), overlay `rgba(30,37,48,.45)`, `transform` 0,3 s. Seções sanfonadas "Todas as Categorias ▾" e "Datas Especiais ▾", links, CTA dourado no fim | Trava a rolagem do body; fecha no X, no overlay e com Esc | `comportamentos/mobile-menu.png` | ✅ `<dialog>` ou painel com JS puro |
| C07 | **Mini-lista de orçamento** (`cda-cart-panel`) | header | Popover 300 px, raio 16, sombra média. Vazio: "Seu carrinho está vazio." Com itens: nome, "25×", botão "Ver carrinho" | Abre no clique do ícone | `comportamentos/carrinho-com-item.png` | 🔁 "Sua lista de orçamento", carregada por HTMX |
| C08 | **Rodapé** (`cda-footer`) | todas | Fundo `#1E2530`, texto `#C7CBD2` 15 px. Grid 3 colunas `1.4fr 1fr 1.3fr`, gap 48, padding 56/48. Col. 1: logo invertido, texto curto, 3 botões redondos (WhatsApp, Instagram, e-mail). Col. 2 "Navegue" (título serifado com traço dourado de 32 px): 5 links com marcador. Col. 3 "Atendimento": ícone + rótulo + valor (WhatsApp, e-mail, endereço). Linha base: "© ano · CNPJ" + Termos / Privacidade / Preferências de cookies | Hover de link em dourado. < 970 px vira 1 coluna (768: 2) | `home/1440.png` (fim) | ✅ `partials/footer.html` |
| C09 | **Banner de cookies** (`#cda-cookie`) | todas, 1ª visita | Card flutuante centralizado, 560×134, `bottom: 16px`, fundo escuro, raio 18, sombra forte. Texto + link "Saiba mais" (âncora `#cookies` da política). Botões "Só os necessários" (contorno) e "Aceitar todos" (primário). z-index alto | Reabre por "Preferências de cookies" no rodapé | `comportamentos/cookies-banner.png` | ✅ + LGPD: GTM/Pixel só após aceitar |
| C10 | **Rolar para cima** (`#ast-scroll-top`) | todas | Quadrado 32 px, canto inferior direito | Aparece após rolar; leva ao topo | `comportamentos/rolado.png` | ✅ (botão redondo com `aria-label`) |
| C11 | **Breadcrumb** | categoria, produto, orçamento | 13 px, `#5F6670`, separador "/" | Último item sem link | `produto/1440.png` | ✅ `componentes/breadcrumb.html` + JSON-LD |

## 2. Home

Ordem real das seções (1440): **Hero → Vitrine por categoria → Próximas datas → Portfólio → Categorias (tiles) → Como funciona → Faixa de prazos → Por que nós + Depoimentos → FAQ**. Altura total ≈ 10.650 px.

| # | Componente | Estrutura e medidas | Comportamento | ISF |
|---|---|---|---|---|
| H01 | **Hero** (`cda-hero`) | Fundo creme `#F4F1E9`, 749 px. Grid 2 col. (texto 615 px · mídia 585 px). Texto: selo em pílula "TEMPORADA 2026 · ● Outubro Rosa ● Novembro Azul ● Natal"; h1 56/62 serifado com uma palavra em itálico colorido; subtítulo 17 px; 2 CTAs (primário pílula 59 px + ghost); 3 **cards de prova** (ícone + título + texto, 196×167). Mídia: mosaico de 3 fotos (1 alta + 2) com legendas em pílula e 2 "cards flutuantes" (selo de data) | Sem carrossel. < 650 px: mosaico some e cards de prova viram lista | 🔁 `Banner` editável (selo, título com destaque, subtítulo, CTAs, até 3 imagens, cards flutuantes ligados a coleções) + `Highlight` (cards de prova) |
| H02 | **Vitrine por categoria** (`cda-vitrine`) | Kicker + h2 + link "Ver catálogo completo →". 6 blocos (`cda-vb`), cada um: h3 + subtítulo + "Ver todas →" e um **trilho** horizontal (`grid`, `overflow-x: auto`, `scroll-snap x mandatory`, gap 14) com 10 cards de produto (198×277; 6 visíveis em 1440, 2,1 em 390). 1º bloco "Acabou de chegar" (novidades); demais por categoria, ordenados por popularidade. Botão "Ver todas as categorias" no fim | Conteúdo carregado por **XHR** à Store API (1 chamada por bloco) — causa CLS 0,13 | 🔁 renderizado no servidor (sem CLS); blocos configuráveis: "Novidades" + categorias marcadas `show_on_home` |
| H03 | **Card de produto** (`cda-pc`) | 198 px (trilho) / 223 px (grade). Raio 16, borda `#EDE8DC`, fundo `#FBFAF6`. Imagem quadrada em fundo branco; selo opcional ("NOVO", "MAIS PEDIDO") em pílula no canto; **bolinhas de cor + "N cores"** sobre a imagem; nome (14 px, 600, 2–3 linhas com reticências); "Ver produto →" | Hover: `translateY(-4px)` + sombra (0,25 s). O card inteiro é um link | ✅ `componentes/card_produto.html`; "N cores" → "N variações" (ou "N opções de vazão" quando houver 1 atributo) |
| H04 | **Próximas datas** (`cda-datas`) | Fundo creme. Kicker + h2 + link "Ver todas as datas especiais →". Grid 3 col. (404 px, gap 22) de cards de data (raio 20, foto no topo, selo de mês colorido, h3, texto, rodapé "N produtos · Ver X →"); variação "DATA DE APOIO". Abaixo, **banner largo** (1256×513, 2 col. foto+texto escuro, chips de subcategorias e CTA dourado) | < 1110 px: 1 coluna | 🔁 `Collection` com `featured=True` (cards) + 1 coleção "principal" no banner |
| H05 | **Portfólio** (`cda-feito-aqui`) | Kicker + h2 (637 px) + parágrafo à direita. Grade masonry 4 col. (304 px, gap 14) com 12 itens (altos e baixos), legenda sobreposta (título + cliente) e selo "DESTAQUE"; **"Ver mais trabalhos (8) ↓" / "Ver menos ↑"** alterna classe `cda-open`; rodapé com link para Instagram | Clique no botão expande/recolhe (JS puro) | ✅ `PortfolioItem` (projeto/instalação) |
| H06 | **Categorias em tiles** (`cda-categorias`) | Fundo creme. Kicker + h2 + parágrafo. Grade 6 col. (198×259) com as 12 maiores categorias: imagem + nome + "N produtos". Botão "Ver todas as categorias →" | 4 col. em 768, 2 em 390 | ✅ |
| H07 | **Como funciona** (`cda-how`) | Fundo creme. Kicker + h2. 4 cards brancos (raio 20, padding 30/22): número "01" grande serifado na cor primária, título, texto | 2 col. < 930 px | ✅ `HowItWorksStep` |
| H08 | **Faixa de prazos** (`cda-band`) | Fundo escuro, padding 56. Esq.: h2 com trecho em itálico dourado, texto, CTA dourado (WhatsApp). Dir.: 3 mini-cards de prazo (traço colorido, nome da data, "Pedidos até **25 de setembro**…", "DEPOIS DISSO, SOB CONSULTA") | 1 col. no mobile | 🔁 "Janela de plantio/safra"; cards ligados a coleções com `order_deadline` |
| H09 | **Por que nós** (`cda-why`) | 2 col.: kicker, h2, 2 parágrafos, CTA primário · grade 2×2 de diferenciais (fundo creme, ícone, título, texto) | 1 col. no mobile | ✅ `Highlight` (tipo "por que nós") |
| H10 | **Depoimentos** (`cda-test`) | Pílula "DEPOIMENTOS", h2 com palavra em itálico, texto. 3 cards (creme, raio 20, aspas, ★★★★★, texto, autor + cargo) | 1 col. no mobile | ✅ `Testimonial`; **seção oculta se não houver depoimento** (não inventar) |
| H11 | **FAQ em acordeão** (`cda-faq`) | Fundo creme, container 900 px. Kicker, h2, texto. `<details>` brancos (raio 16, padding 4/24); `summary` 15,5 px/600 com ícone "+" em círculo que gira 45° (vira "×") | 1º item aberto; **não exclusivo** (vários podem ficar abertos) | ✅ `FAQItem` + JSON-LD `FAQPage` |

## 3. Catálogo, categoria, subcategoria, coleção, busca

| # | Componente | Estrutura e medidas | Comportamento | ISF |
|---|---|---|---|---|
| L01 | **Hero de categoria** (`cda-cat-hero`) | Card creme com raio, dentro do container 1220: breadcrumb, h1 (serifado), descrição (≤ 520 px) e, à direita, pílula branca "**50** produtos" | — | ✅ |
| L02 | **Chips** (`cda-cat-chips`) | Pílulas (gap 8): "Todos" ativo (escuro) + categorias **relacionadas** com contagem em `<small>`. No catálogo geral: as 12 maiores + "Ver todas as categorias ↓" (abre grade com todas, `cda-loja-cats`, 7 col.) | Link `?tipo=<slug>` (`rel="nofollow"`) filtra pela interseção | ✅ interseção categoria × outra categoria/coleção, contagem real |
| L03 | **Ordenação** (`woocommerce-ordering`) | À direita da barra de chips: "N produtos" + "Ordenar" + `select` em pílula (13 px, raio 999): **Mais relevantes / Novidades / Nome (A–Z)** | Troca recarrega a página (`?orderby=`), preserva `?tipo=` | ✅ (auto-submit com JS, botão "Aplicar" no `<noscript>`) |
| L04 | **Grade de produtos** (`ul.products`) | 5 col. (≥ 1110), 4 (830–1110), 3 (650–830), 2 (< 650). Gap 16 (10 no mobile). 30 por página | — | ✅ |
| L05 | **Paginação** | Pílulas 42 px, atual escura, "→" próxima; abaixo "Mostrando 1–30 de 50 produtos". URL `/page/N/` | — | ✅ |
| L06 | **"Não encontrou o que procura?"** (`cda-cat-ajuda`) | Card creme: h3 + texto + botão "Falar no WhatsApp" (mensagem cita a categoria) | Link `wa.me` | ✅ |
| L07 | **Texto SEO** (`cda-cat-seo`) | Container estreito, h2 + parágrafos com links internos | — | ✅ `Category.seo_text` (rich text simples) |
| L08 | **Card de produto (novidades)** | Variante com categoria em kicker, "1 cor" e "Ver opções →" | "Carregar mais novidades" (XHR) | 🔁 paginação HTMX "Carregar mais" |

## 4. Produto

Layout: grid 2 col. (galeria 590 · resumo 562, gap 48); abaixo, corpo 2 col. (descrição · ficha técnica em aside); avaliações; "Você também pode gostar" (5 cards); **barra fixa inferior no mobile**.

| # | Componente | Estrutura e medidas | Comportamento | ISF |
|---|---|---|---|---|
| P01 | **Galeria** | Imagem principal quadrada (raio 16, borda), lupa no canto (tela cheia, PhotoSwipe), 8 miniaturas 100 px abaixo (6 no mobile); setas "Foto anterior/Próxima" | Clique na miniatura troca a imagem; escolher a variação troca para a foto da variação; zoom ao passar o mouse | ✅ JS puro: miniaturas, troca por variação, `<dialog>` para tela cheia. ⛔ zoom no hover (baixo valor) |
| P02 | **Resumo** | Breadcrumb · selo da categoria principal (pílula) · h1 serifado (~34 px) · "Cód. TAL582" · descrição curta | — | ✅ |
| P03 | **Seletor de variação** | `select` nativo escondido + **swatches** redondos 40 px (borda branca 2 px + anel `#D9D0BE`), rótulo "Cor: escolha uma cor", link "Limpar" | Escolher → `aria-pressed`, anel escuro, rótulo mostra o valor, botão é liberado, SKU muda (ex.: TAL582-PT) | 🔁 um grupo de botões por atributo de variação (pílulas com texto: "16 mm", "2 L/h"), select nativo como fallback |
| P04 | **Quantidade** | Stepper `−` [25] `+` (52 px, fundo `#F1ECE2`), `min` = mínimo | `−` não passa do mínimo; digitar abaixo volta ao mínimo; texto "Mínimo de 25 unidades · você ajusta tudo antes de enviar" | ✅ + `step` (múltiplo) e unidade ("metros", "rolos") |
| P05 | **Botão "Adicionar ao orçamento"** | Pílula dourada, ocupa o resto da linha | **Bloqueado** (`disabled` visual, cursor `not-allowed`) até escolher a variação; clique sem escolha mostra "Escolha uma cor para continuar." (`role="alert"`). Ao adicionar: contador do header soma a quantidade e **redireciona para o passo 1 do orçamento** | 🔁 HTMX: adiciona sem sair da página, atualiza contador e mostra toast com "Ver lista"; sem JS, POST normal com redirect |
| P06 | **Garantias** | Lista com ícones: "Orçamento sem compromisso…", "Enviamos para todo o Brasil" | — | ✅ textos `[DEFINIR]` |
| P07 | **Descrição expansível** | Artigo com altura limitada + gradiente; botão "Ler descrição completa ↓" | Expande (classe) | ✅ |
| P08 | **Ficha técnica** (`cda-prod-ficha`) | Aside creme, raio 16: h2 "Especificações", `dl` com linhas Conteúdo, Material, Medidas, Cores, Código | Estática | ✅ gerada de `attribute_schema` + `attributes` (+ unidade) |
| P09 | **Avaliações** | h2 + "Nenhuma avaliação ainda" + botão "Escrever uma avaliação" | Formulário de comentário do WooCommerce | ⛔ (ver gap) |
| P10 | **Relacionados** | "Você também pode gostar": 5 cards | Mesma categoria | ✅ |
| P11 | **Barra fixa mobile** (`cda-prod-barra`) | "Escolha a cor" + botão "Adicionar ao orçamento" fixo no rodapé | Rola até o seletor | ✅ |

## 5. Orçamento (3 passos)

| # | Componente | Estrutura | Comportamento | ISF |
|---|---|---|---|---|
| O01 | **Stepper** (`cda-flow-steps`) | 3 passos numerados em círculo: 1 Seus produtos · 2 Seus dados · 3 Confirmação; passo ativo com traço dourado embaixo | — | ✅ |
| O02 | **Tabela de itens** | Cabeçalho Produto / Quantidade; linha: remover (×), miniatura, nome + variação, SKU, stepper | "Atualizar carrinho", "← Continuar adicionando produtos", "Prosseguir para cotação" (dourado) | ✅ HTMX para remover/alterar sem recarregar |
| O03 | **Formulário de dados** | h1 "Como podemos falar com você?"; Nome*, Telefone*, E-mail*, Mensagem (opcional) | — | 🔁 + Empresa, Cidade/UF; honeypot; consentimento/finalidade |
| O04 | **Resumo "Seu pedido"** | Card à direita: itens × quantidade, texto de privacidade com link, aviso "Ao enviar, abriremos o WhatsApp com seu orçamento pronto… Você também receberá uma confirmação por e-mail.", botão "Enviar sua solicitação de cotação" | Envio → passo 3 "Sua solicitação foi recebida!" + abre `wa.me` | ✅ |

## 6. Institucionais

| # | Página | Estrutura | ISF |
|---|---|---|---|
| I01 | **Novidades** | Hero 2 col. (kicker, h1 com itálico, texto · card "Últimos lançamentos" com 3 itens e selo "● ATUALIZADO"); "Os mais recentes primeiro" + chips de categoria + grade 5 col. com selo NOVO + "Carregar mais"; card escuro "Procurando um brinde específico?" + WhatsApp; bloco SEO com chips de coleções | ✅ |
| I02 | **Sobre** | Hero com mosaico, 4 cards de números; história + linha do tempo; técnicas (4 cards); 6 compromissos; portfólio; segmentos atendidos; depoimentos; CTA final escuro com ficha da empresa (CNPJ, endereço, horário) | 🔁 seções editáveis (`Page` com blocos simples); conteúdo `[DEFINIR]` |
| I03 | **Contato** | Hero com selo "Atendimento aberto agora", h1, horário em card; 3 cards de canal (WhatsApp destacado escuro, e-mail, Instagram); bloco "Com estas informações, a proposta sai na primeira resposta" (checklist) + **formulário "Mande sua mensagem"** (nome, empresa, e-mail, WhatsApp, cidade, estado, ocasião, quantidade, mensagem); "Onde estamos" + mapa; FAQ | 🔁 formulário de contato grava como `Quote` origem "contato" sem itens; mapa só com consentimento (⛔ iframe Google Maps antes do aceite) |
| I04 | **Termos / Privacidade** | Hero creme com data de atualização e 3 cards-resumo; sumário lateral fixo ("Nesta página", item ativo) + seções numeradas "01…11"; CTA escuro para a outra política | ✅ `LegalPage` editável |
| I05 | **Blog (lista)** | Hero com post em destaque (2 col.); "Todos os artigos" + chips de categoria + grade 3 col. de cards (imagem, categoria em kicker, título serifado, resumo, "N min de leitura"); faixa do Instagram | ✅ feature 009 (opcional) |
| I06 | **Blog (post)** | Artigo, FAQ, "Continue lendo", comentários | 🔁 sem comentários |
| I07 | **404** | h1 "Esta página não existe.", texto, busca | ✅ + links para catálogo e home |

## 7. Elementos atômicos

| Átomo | Medidas | ISF |
|---|---|---|
| Botão primário | pílula, 16/28 padding, 15 px/600, fundo petróleo `#4E8E9E` (hover `#3A7382`), texto branco, transição .25 s | `.btn.btn--primary` (cor primária "Campo") |
| Botão ghost | igual, transparente, borda 1 px `#CFC8B8` | `.btn.btn--ghost` |
| CTA dourado | pílula 11/21, 14,5 px/700, fundo `#C9A76B`, texto escuro | `.btn.btn--accent` (ouro "Campo" `#f2b01e`) |
| Kicker | 13 px/700, caixa alta, `letter-spacing: 2.5px`, dourado | `.kicker` (acento) |
| Link com seta | 14,5 px/600, petróleo, "→" | `.link-seta` |
| Selo/badge | pílula 11 px/700, caixa alta | `componentes/badge.html` |
| Chip | pílula 13 px, borda clara; ativo escuro | `.chip`, `.chip--ativo` |
| Input | 40–48 px, borda `#A6A08E`, raio 8–12 | `componentes/campo.html` (tokens "Campo") |
| Swatch | círculo 40 px | 🔁 pílula de texto para atributos técnicos |
| Stepper de quantidade | 52 px | `componentes/quantidade.html` |
| Foco | `outline: 3px dotted` | 🔁 anel de foco "Campo" (3 px, 20 %) — mais visível |
