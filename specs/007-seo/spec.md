# Feature Specification: SEO

**Feature Branch**: `007-seo` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "007-seo: sitemap (django.contrib.sitemaps), robots.txt, metas e Open Graph por página, canonical, JSON-LD (Organization, Product sem preço, BreadcrumbList, FAQPage)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Buscadores encontram e entendem o catálogo (Priority: P1)
Um buscador lê `/robots.txt`, encontra `/sitemap.xml` com home, listagens, categorias, coleções, produtos e páginas; em cada página indexável encontra título, descrição, canonical, Open Graph e dados estruturados válidos.

**Acceptance Scenarios**:
1. **Given** o site, **When** `/robots.txt` é lido, **Then** libera o site, bloqueia `/admin/`, `/orcamento/` e `/busca/` e aponta o sitemap absoluto.
2. **Given** produtos ativos e inativos, **When** `/sitemap.xml` é lido, **Then** só os ativos (e categorias/coleções visíveis) aparecem, com `lastmod`.
3. **Given** a página de um produto, **When** analisada, **Then** tem JSON-LD `Product` (nome, SKU, descrição, imagens, marca, categoria, propriedades da ficha) **sem** `offers`, e `BreadcrumbList` igual ao breadcrumb visível.
4. **Given** a home com FAQ, **When** analisada, **Then** tem `Organization`, `WebSite` com `SearchAction` e `FAQPage`.
5. **Given** listagens filtradas, busca, orçamento e 404, **When** analisadas, **Then** são `noindex`.

### User Story 2 - Compartilhar um produto (Priority: P2)
Ao colar o link de um produto no WhatsApp, a prévia mostra título, descrição e imagem (`og:type=product`, `og:image` absoluta).

## Requirements *(mandatory)*
- **FR-001**: Sitemap XML com home, páginas estáticas, categorias, coleções visíveis, produtos ativos e páginas institucionais ativas.
- **FR-002**: `robots.txt` dinâmico com URL absoluta do sitemap.
- **FR-003**: Toda página indexável com `<title>` único, meta description, canonical absoluto e Open Graph; imagem padrão configurável.
- **FR-004**: JSON-LD `Organization` + `WebSite` em todas; `Product` (sem preço) e `BreadcrumbList` no produto; `BreadcrumbList` e `CollectionPage` nas listagens; `FAQPage` onde há FAQ.
- **FR-005**: JSON-LD escapado com segurança (sem injeção de `</script>`).

## Success Criteria *(mandatory)*
- **SC-001**: 100% dos blocos JSON-LD válidos como JSON e com `@context` schema.org.
- **SC-002**: Nenhuma página indexável sem canonical.

## Assumptions
- `BASE_URL` define o domínio canônico (P6).
