# SEO da referência (Fase 1)

> Coletado em cada amostra (`raw/captura.json`, chave `seo`). Plugin da referência: Rank Math.

## 1. Padrões de URL

| Tipo | Padrão | Observação |
|---|---|---|
| Home | `/` | |
| Catálogo | `/categorias-de-brindes/`, `/categorias-de-brindes/page/{n}/` | |
| Categoria | `/categoria-produto/{slug}/` | |
| Subcategoria | `/categoria-produto/{pai}/{filho}/` | |
| Produto | `/produto/{slug}/` | slug descritivo, sem ID |
| Busca | `/?s={termo}&post_type=product` | `noindex` |
| Post | `/{slug}/` | na raiz |
| Categoria de blog | `/category/{slug}/` | |
| Tag de produto | `/produto-tag/{slug}/` | |
| Filtro por chip | `?tipo={slug}` | `rel="nofollow"` no link |
| Ordenação | `?orderby=date\|title\|menu_order` | |

Todas com barra final e `https`. Sitemap em `/sitemap_index.xml` (índice com 7 sitemaps: páginas, posts, produtos em 3 partes, categorias de produto e de blog). `robots.txt`: `Disallow: /wp-admin/` + `Sitemap:`.

## 2. Metas por tipo de página

| Tipo | `<title>` (forma) | Description | Robots | Canonical | `og:type` | `og:image` |
|---|---|---|---|---|---|---|
| Home | "{Proposta} \| {Marca}" | ✔ 152 car. | index, follow, max-snippet:-1, max-image-preview:large | ✔ | website | ✗ |
| Catálogo | "Todos os produtos - {Marca}" | ✔ | index | ✔ | article | ✗ |
| Categoria | "{Categoria} para Empresas \| {Marca}" | ✔ ~130 | index | ✔ (sem `?tipo`) | article | ✗ |
| Produto | "{Nome curto do produto}" | ✔ ~146 | index | ✔ | **product** | ✔ |
| Busca | "{termo} - {Marca}" | ✗ | **noindex**, follow | ✗ | article | ✗ |
| Institucionais | "{Página} - {Marca}" | curta (7–28 car.) | index | ✔ | article | às vezes |
| Orçamento | "Solicitar Orçamento - {Marca}" | ✔ | **noindex** | ✗ | article | ✗ |
| 404 | "Page Not Found - {Marca}" | ✗ | **noindex** | ✗ | article | ✗ |

Twitter card `summary_large_image` em todas. `lang="pt-BR"`, `og:locale=pt_BR`.

**Problemas a não repetir:** descriptions curtas demais nas institucionais ("Contato", "Blog"); `og:type=article` em páginas que não são artigo; `og:image` ausente na maioria; título 404 em inglês; busca sem h1.

## 3. Dados estruturados (JSON-LD, `@graph`)

| Tipo de página | Tipos presentes |
|---|---|
| Todas | `Organization`, `WebSite`, `Place` (endereço) |
| Home | + `WebPage`, `Article` (incorreto), `Person` |
| Catálogo/categoria | + `CollectionPage`, `BreadcrumbList` |
| Produto | + `ItemPage`, `Product` (name, description, sku, category, weight, height/width/depth, image[]), `BreadcrumbList` — **sem `offers`** (sem preço) |
| Busca | + `SearchResultsPage` |
| Sobre | + `AboutPage` |
| Contato | + `ContactPage` |
| Post | + `BlogPosting`, `FAQPage` |

Não há `SearchAction` no `WebSite`, nem `FAQPage` na home (apesar do acordeão).

## 4. Breadcrumbs

Visíveis em categoria ("Início / Categorias / Mochilas"), produto ("Início / {categoria principal} / {produto}") e orçamento. Também em JSON-LD `BreadcrumbList`.

## 5. Padrão adotado na ISF (feature 007)

- URLs da tabela de `docs/mapeamento-dominio.md` §5, sempre com barra final.
- `<title>`: "{título da página} | {nome do site}"; produto: "{nome} | {nome do site}". Description com 120–160 caracteres; fallback a partir da descrição curta.
- Canonical absoluto em todas as páginas indexáveis; listagens filtradas/ordenadas apontam para a URL sem query (página `n` aponta para si mesma).
- `noindex` em busca, orçamento, 404 e páginas com filtro `?tipo=`.
- Open Graph completo (`og:type=product` no produto, `website` na home, `og:image` com fallback configurável).
- JSON-LD: `Organization` + `WebSite` (com `SearchAction`) em todas; `Product` sem `offers` (com `sku`, `brand`, `category`, `image`, `additionalProperty` vindo da ficha técnica); `BreadcrumbList`; `FAQPage` na home e onde houver FAQ; `CollectionPage` nas listagens.
- `django.contrib.sitemaps` em `/sitemap.xml` (produtos, categorias, coleções, páginas institucionais, posts) e `robots.txt` dinâmico apontando para ele.
