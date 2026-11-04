# Quickstart: Fundação

```bash
cp .env.example .env            # ajuste SECRET_KEY
uv sync
uv run python manage.py migrate
uv run python manage.py runserver   # http://127.0.0.1:8000/ · /healthz/ · /admin/
```

Docker: `cp .env.example .env && docker compose up --build`.

Qualidade: `uv run ruff check . && uv run ruff format --check . && uv run pytest` · E2E: `uv run playwright install chromium && uv run pytest -m e2e`.

Validação manual: `/` em 390, 768 e 1440 px; menu mobile (botão, Esc, overlay); dropdowns no desktop; cookies (aceitar, recusar, reabrir pelo rodapé); `/nao-existe/` (404 com busca).
