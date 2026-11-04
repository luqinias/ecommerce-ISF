# Inventário de páginas da referência (Fase 1)

> Coleta em 2026-11-04 com Playwright (`tools/engenharia_reversa/`), só páginas públicas, `robots.txt` respeitado (só `/wp-admin/` é bloqueado), 1 navegação a cada 2 s, User-Agent `ISF-EstudoDeLayout/1.0`, scripts de rastreamento bloqueados, nenhum formulário enviado e nenhum link `wa.me`/`mailto:` seguido.
> Dados brutos: `raw/inventario.json` (sitemap), `raw/captura.json` (estrutura, estilos, SEO, axe, rede), `raw/comportamentos.json`, `raw/breakpoints.json`. Screenshots: `screenshots/{tipo}/{viewport}.png` (o sufixo `-2` é a segunda amostra do tipo). Esse material é de estudo interno e fica fora do git (`.gitignore`).

## 1. Fonte: sitemap (Rank Math)

| Sitemap | URLs |
|---|---|
| `page-sitemap.xml` | 17 páginas |
| `post-sitemap.xml` | 12 posts de blog |
| `product-sitemap1..3.xml` | 523 (catálogo + 522 produtos) |
| `product_cat-sitemap.xml` | 42 categorias (2 subcategorias: `cadernos/agendas`, `garrafas-e-squeezes/garrafas-termicas`) |
| `category-sitemap.xml` | 4 categorias de blog |

Na Store API há **42 categorias de produto**, sendo 12 "datas especiais" misturadas às categorias comuns (Dia das Mães, Natal, Outubro Rosa…) e 1 guarda-chuva (`brindes-corporativos`, com 474 produtos). As categorias "de verdade" são cerca de 29.

## 2. Tipos de página e amostras

| Tipo | URL(s) amostrada(s) | Status | h1 | Observação |
|---|---|---|---|---|
| Home | `/` | 200 | 1 | 9 seções de conteúdo (ver `componentes.md`) |
| Catálogo geral | `/categorias-de-brindes/`, `/categorias-de-brindes/page/2/` | 200 | 1 | Hero de categoria + chips das maiores categorias + "Ver todas as categorias ↓" (lista completa em grid) + grade de 30 |
| Categoria | `/categoria-produto/canetas/`, `/categoria-produto/mochilas/` | 200 | 1 | Hero com contagem, chips de **categorias relacionadas** (`?tipo=`), ordenação, grade 5 col., paginação, "Não encontrou?", texto SEO |
| Subcategoria | `/categoria-produto/cadernos/agendas/`, `/categoria-produto/garrafas-e-squeezes/garrafas-termicas/` | 200 | 1 | Mesmo template de categoria; breadcrumb inclui o pai |
| Data especial | `/categoria-produto/fim-de-ano-natal/`, `/categoria-produto/outubro-rosa/` | 200 | 1 | Mesmo template de categoria (são `product_cat`) |
| Produto | `/produto/kit-talheres-fibra-de-bambu-personalizado/` (5 cores), `/produto/kit-churrasco-premium-estojo-bambu-personalizado/` (1 cor) | 200 | 1 | Todos os 60 produtos amostrados na API são `variable` com atributo único "Cores" |
| Busca | `/?s=garrafa&post_type=product` | 200 | **0** | Template padrão do tema (sem h1, sem hero). `noindex` |
| Novidades | `/novidades/` | 200 | 1 | Hero + destaque de 3 + grade (carregada via Store API) |
| Sobre | `/sobre-cia-da-arte-brindes/` | 200 | 1 | 8 seções institucionais |
| Blog (lista) | `/blog/` | 200 | 1 | Hero + lista carregada por `wp-json/wp/v2/posts` |
| Blog (post) | `/brindes-novembro-azul/`, `/tipos-de-personalizacao-de-brindes/` | 200 | 1 | Artigo + FAQ + "Continue lendo" + comentários |
| Contato | `/contato/` | 200 | 1 | Hero, canais, mapa (Google Maps), FAQ |
| Solicitar orçamento | `/solicitar-orcamento-2/` (passo 1, carrinho) e `/finalizacao-de-orcamento/` (passo 2, checkout) | 200 | 1 | Fluxo em 3 passos sobre o carrinho/checkout do WooCommerce. `noindex` |
| Termos / Privacidade | `/termos-de-uso-e-privacidade/`, `/politica-de-privacidade/` | 200 | 1 | Seções numeradas "01 … 11" com âncoras |
| Landing de segmento | `/agro/` | 200 | 1 | Página longa sem header/footer padrão (landing). **Fora do escopo** (ver gap analysis) |
| 404 | `/pagina-inexistente-estudo-isf/` | 404 | 1 | "Esta página não existe." + busca. `noindex` |

Outras páginas do sitemap não amostradas: `/clinicas/`, `/empresas-rh/` (landings de segmento), `/brindes-personalizados-uberaba-mg/` e similares (SEO local), `/obrigado/` (agradecimento).

## 3. Mapa de navegação

```mermaid
flowchart LR
  subgraph Header["Header (todas as páginas)"]
    U[Faixa superior: frase + WhatsApp]
    L[Logo] --> H[Home]
    B[Busca] --> R[Resultados de busca]
    C[Ícone da lista] --> MC[Mini-lista] --> O1
    TC[Todas as Categorias ▾] --> CAT[Categoria]
    DE[Datas Especiais ▾] --> DT[Data especial]
    N[Novidades] --> NOV[Novidades]
    S[Sobre Nós] --> SOB[Sobre]
    BL[Blog] --> BLG[Blog]
    CT[Contato] --> CON[Contato]
    Q[Solicitar orçamento rápido] -.wa.me.-> W((WhatsApp))
  end
  H --> CATG[Catálogo geral /page/n] --> P[Produto]
  CAT --> SUB[Subcategoria] --> P
  CAT --> P
  DT --> P
  NOV --> P
  R --> P
  P -->|Adicionar ao orçamento| O1[Orçamento 1: Seus produtos]
  O1 -->|Prosseguir para cotação| O2[Orçamento 2: Seus dados]
  O2 -->|Enviar| O3[Orçamento 3: Confirmação] -.-> W
  BLG --> POST[Post]
  subgraph Footer
    F1[Todos os produtos] --> CATG
    F2[Termos] --> TER[Termos]
    F3[Privacidade] --> PRI[Privacidade]
    F4[Preferências de cookies] --> CK[Banner de cookies]
  end
```

## 4. Métricas de linha de base (1440 × 900, rastreadores bloqueados)

| Tipo | LCP (ms) | CLS | Violações axe (críticas/sérias) |
|---|---|---|---|
| Home | 1316 | **0,129** | 0 / 1 regra (`color-contrast`, 20 nós) |
| Catálogo | 792 | 0,002 | 0 / 1 |
| Categoria | 2184 | 0,002 | 0 / 2 (`color-contrast`, `link-in-text-block`) |
| Subcategoria | 1200 | 0,002 | 0 / 2 |
| Data especial | 1196 | 0,002 | 0 / 2 |
| Produto | 1740 | 0,010 | **1** (`select-name`) / 2 |
| Busca | 1832 | 0,121 | 0 / 1 |
| Novidades | 1440 | 0,146 | 0 / 1 |
| Sobre | 1276 | 0,003 | 0 / 1 |
| Blog | 3232 | 0,087 | 0 / 1 |
| Contato | 1084 | 0,002 | 0 / 1 |
| Orçamento | 1388 | 0,002 | 0 / 1 |
| Termos | 240 | 0,007 | 0 / 1 |
| 404 | 248 | 0,004 | 0 / 1 |

Todas as páginas também têm violações moderadas recorrentes: dois `contentinfo` (footer dentro de footer), `heading-order` (rodapé usa `h4` depois de `h2`) e `region`. Metas do projeto: LCP ≤ linha de base de cada tipo, CLS ≤ 0,1 em todos (a referência passa de 0,1 na home, busca e novidades por carregar vitrines via JS), zero violações críticas ou sérias.
