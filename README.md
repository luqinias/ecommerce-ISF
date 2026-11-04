# Catálogo Irrigação Sem Fronteiras

Site de catálogo com **lista de orçamento** da Irrigação Sem Fronteiras (ISF). Monolito **Django** renderizado no servidor, com **HTMX** e JS puro para as partes dinâmicas. Sem preço público, sem checkout: a conversão acontece por **WhatsApp** e **e-mail**.

> Estrutura, layout e comportamento seguem o estudo de referência em [`docs/engenharia-reversa/`](docs/engenharia-reversa/). Conteúdo e marca são da ISF; o que a empresa ainda não definiu aparece como `[DEFINIR]` e está listado em [`docs/pendencias-empresa.md`](docs/pendencias-empresa.md).

## Requisitos

- Python 3.12 e [uv](https://docs.astral.sh/uv/)
- Opcional: Docker + Docker Compose

## Subir localmente

```bash
cp .env.example .env                 # ajuste SECRET_KEY
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Healthcheck: http://127.0.0.1:8000/healthz/

### Com Docker (um comando)

```bash
cp .env.example .env
docker compose up --build
```

Sobe o Postgres e a aplicação (gunicorn) em http://localhost:8000/, aplica as migrações e carrega os dados de demonstração.

## Qualidade

```bash
uv run ruff check . && uv run ruff format --check .
uv run pytest                                   # unitários e integração
uv run playwright install chromium              # uma vez
uv run pytest -m e2e                            # ponta a ponta (Playwright)
```

## Estrutura

```
config/            settings (base, dev, prod, test), urls, wsgi
apps/core/         models base, configuração do site, layout, healthcheck
apps/catalogo/     categorias, coleções, produtos, variações, importação
apps/orcamentos/   lista de orçamento, formulário, leads
apps/conteudo/     home e páginas institucionais editáveis
apps/seo/          sitemap, robots, JSON-LD
templates/         base.html, partials/, componentes/
static/            css (tokens + componentes), js, fontes, htmx
tests/             unit/ e e2e/
specs/             artefatos do Spec Kit por feature
docs/              contexto, engenharia reversa, mapeamento, pendências
tools/             scripts de engenharia reversa e validação
```
