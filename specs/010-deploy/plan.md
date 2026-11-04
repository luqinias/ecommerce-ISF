# Implementation Plan: Deploy

**Branch**: `feat/010-deploy` | **Spec**: [spec.md](spec.md)

## Summary
Ajustes no `Dockerfile` (multi-stage não é necessário; imagem slim com uv), `docker-compose.yml` (Postgres + web + volume de mídia), `SERVE_MEDIA` opcional, `manage.py check --deploy` limpo com HSTS configurável, `docs/deploy.md`, exemplos `docs/exemplos/nginx.conf`, `docs/exemplos/supervisor.conf` e `docs/exemplos/ci-github-actions.yml`. Validação real com Docker.

## Constitution Check
IX ✅ (sem orquestrador novo) · Restrições técnicas ✅ (segredos só em env).

## Tasks
- [X] T001 `SERVE_MEDIA` e ajustes de produção em settings/urls
- [X] T002 Build e subida reais com `docker compose up --build`; `/healthz/`
- [X] T003 `docs/deploy.md` + exemplos Nginx, supervisor e CI
- [X] T004 README final (setup, importação, deploy)
