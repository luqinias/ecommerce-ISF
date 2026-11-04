# Feature Specification: Deploy

**Feature Branch**: `010-deploy` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "010-deploy: build de produção, estáticos (WhiteNoise ou o padrão interno), mídia, healthcheck, guia de deploy."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir em produção com segurança (Priority: P1)
A equipe constrói a imagem, configura as variáveis e sobe a aplicação atrás de um proxy com HTTPS; estáticos comprimidos e com hash, mídia persistente (volume, Nginx ou S3), migrações automáticas e healthcheck para o orquestrador.

**Acceptance Scenarios**:
1. **Given** um clone limpo e `.env`, **When** `docker compose up --build`, **Then** Postgres e app sobem, migrações rodam, a demonstração é carregada e `/healthz/` responde 200.
2. **Given** produção sem `SECRET_KEY` ou `ALLOWED_HOSTS`, **When** a app inicia, **Then** falha com mensagem clara.
3. **Given** `manage.py check --deploy` em produção, **When** executado com as variáveis recomendadas, **Then** não há alertas críticos.
4. **Given** o guia, **When** seguido em uma VM (EC2) com gunicorn + supervisor + Nginx, **Then** o site sobe sem Docker.

## Requirements *(mandatory)*
- **FR-001**: Imagem de produção sem dependências de desenvolvimento, usuário não-root, `collectstatic` no build, healthcheck.
- **FR-002**: Estáticos via WhiteNoise (hash + compressão); mídia por volume com Nginx/S3 recomendados e `SERVE_MEDIA` para instalações pequenas.
- **FR-003**: Guia `docs/deploy.md` (Docker e VM), com variáveis, Nginx, backup, atualização e checklist de go-live.
- **FR-004**: Proposta de CI (ruff + pytest) como exemplo, sem ativar (pendência P8).

## Success Criteria *(mandatory)*
- **SC-001**: `docker compose up --build` deixa o site respondendo em menos de 3 minutos em máquina comum.

## Assumptions
- Escolha final entre Docker e EC2/supervisor: pendência P7.
