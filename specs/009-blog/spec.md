# Feature Specification: Blog (opcional)

**Feature Branch**: `009-blog` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "009-blog (opcional, confirmar com a empresa): posts e categorias simples."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ler artigos (Priority: P2)
Com o blog ativado, o visitante vê "Blog" no menu e no rodapé; a lista mostra o artigo mais recente em destaque, chips de categoria e uma grade de cards (imagem, categoria, título, resumo, tempo de leitura); o artigo tem breadcrumb, data, texto e "Continue lendo".

**Acceptance Scenarios**:
1. **Given** o blog desativado (padrão), **When** `/blog/` é acessado, **Then** 404 e nenhum link para o blog aparece.
2. **Given** o blog ativado e posts publicados, **When** `/blog/` abre, **Then** o mais recente aparece em destaque e os demais em grade de 12 por página.
3. **Given** um post com publicação futura ou rascunho, **When** acessado, **Then** 404.
4. **Given** um post, **When** aberto, **Then** tem `BlogPosting` e `BreadcrumbList` em JSON-LD e entra no sitemap.

### User Story 2 - Equipe publica (Priority: P2)
No admin, a equipe cria categorias e posts (título, categoria, resumo, texto simples com listas, capa, data de publicação, rascunho/publicado).

## Requirements *(mandatory)*
- **FR-001**: Liga/desliga em Configuração do site (`blog_enabled`).
- **FR-002**: Posts com publicação agendada (data) e rascunho.
- **FR-003**: Lista com filtro por categoria e paginação; post com relacionados da mesma categoria.
- **FR-004**: Sem comentários (gap analysis).

## Success Criteria *(mandatory)*
- **SC-001**: Blog desativado não expõe nenhuma URL nem link.

## Assumptions
- Decisão de ter blog e autoria: pendência P14. Conteúdo de demonstração não é criado para o blog.
