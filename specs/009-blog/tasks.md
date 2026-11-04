# Implementation Plan: Blog

**Branch**: `feat/009-blog` | **Spec**: [spec.md](spec.md)

## Summary
Models `PostCategory` e `Post` no app `conteudo`; views `blog`, `blog_categoria`, `post` protegidas por `site.blog_enabled`; templates `conteudo/blog.html` e `conteudo/post.html` (I05/I06); sitemap `PostsSitemap` condicional; JSON-LD `BlogPosting`. Sem dependências.

## Constitution Check
IX ✅ (sem comentários) · V ✅ · I ✅.

## Tasks
- [X] T001 Models + admin + migração
- [X] T002 Views, URLs e templates
- [X] T003 Sitemap e JSON-LD
- [X] T004 Testes (desativado = 404; agendamento; paginação; JSON-LD)
