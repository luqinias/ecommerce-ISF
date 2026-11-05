# Catálogo Irrigação Sem Fronteiras

Site de catálogo com **lista de orçamento** da Irrigação Sem Fronteiras (ISF). É um monolito **Django 6** renderizado no servidor, com **HTMX** e JS puro nas partes dinâmicas. Não tem preço público nem checkout: a conversão acontece por **WhatsApp** e **e-mail**.

- A estrutura, o layout e o comportamento seguem o estudo de referência em [`docs/engenharia-reversa/`](docs/engenharia-reversa/).
- Conteúdo e marca são da ISF. O que a empresa ainda não definiu aparece como `[DEFINIR]` e está em [`docs/pendencias-empresa.md`](docs/pendencias-empresa.md).
- Padrões e decisões: [`docs/contexto-empresa.md`](docs/contexto-empresa.md), [`docs/mapeamento-dominio.md`](docs/mapeamento-dominio.md) e a constituição em [`.specify/memory/constitution.md`](.specify/memory/constitution.md). As specs de cada feature estão em [`specs/`](specs/).

## Subir com um comando (Docker)

```bash
cp .env.example .env        # gere uma SECRET_KEY
docker compose up --build   # Postgres + app em http://localhost:8000
docker compose exec web python manage.py createsuperuser
```

Na primeira subida, o banco é migrado e recebe o catálogo e o conteúdo de demonstração.

## Desenvolvimento sem Docker

Requer Python 3.12 e [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
uv sync
uv run python manage.py migrate
uv run python manage.py carregar_catalogo_demo     # 42 produtos fictícios com imagens geradas
uv run python manage.py carregar_conteudo_demo     # home, Sobre, Termos, Privacidade, FAQ
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Site em http://127.0.0.1:8000/ · admin em `/admin/` · healthcheck em `/healthz/` · `/sitemap.xml` · `/robots.txt`. Sem `DATABASE_URL`/`DB_*`, usa SQLite. Em desenvolvimento, os e-mails saem no console.

## Trocar o catálogo de demonstração pelo real

Não exige alterar código. Guia completo: [`docs/importacao-catalogo.md`](docs/importacao-catalogo.md). Planilha-modelo: [`docs/exemplos/modelo-catalogo.xlsx`](docs/exemplos/modelo-catalogo.xlsx).

```bash
uv run python manage.py importar_catalogo catalogo.xlsx --dry-run --imagens ./fotos   # simula e mostra erros por linha
uv run python manage.py importar_catalogo catalogo.xlsx --imagens ./fotos             # importa (idempotente por SKU)
uv run python manage.py limpar_catalogo_demo                                          # remove só a demonstração
```

O admin também importa, em **Catálogo › Importações de catálogo**, com simulação e relatório. Os atributos técnicos de cada categoria (vazão, diâmetro…) são definidos no admin ou na planilha e geram a ficha técnica e o seletor de variações.

## Qualidade

```bash
uv run ruff check . && uv run ruff format --check .
uv run pytest                                  # unitários e integração
uv run playwright install chromium             # uma vez
uv run pytest -m e2e                           # ponta a ponta (navegação, produto, orçamento, cookies, home)
```

## Deploy

[`docs/deploy.md`](docs/deploy.md) cobre Docker e VM/EC2 com gunicorn, supervisor e Nginx, as variáveis de ambiente, backup e o checklist de go-live.

## Estrutura

```
config/            settings (base, dev, prod, test), urls, wsgi
apps/core/         models base, configuração do site, e-mail, limite de taxa, healthcheck, template tags
apps/catalogo/     categorias, coleções, produtos, variações, imagens, importação, listagens e produto
apps/orcamentos/   lista na sessão, pedido (Quote), e-mails, WhatsApp, admin de leads
apps/conteudo/     home e páginas editáveis, contato, novidades, blog (opcional)
apps/seo/          sitemap, robots, JSON-LD
templates/         base.html, partials/, componentes/, páginas por app, e-mails
static/            css (tokens, base, layout, componentes, páginas), js (app.js), htmx, fontes
tests/             unit/ e e2e/ (Playwright)
tools/             engenharia reversa (captura, comportamentos, breakpoints) e planilha-modelo
docs/              contexto, engenharia reversa, mapeamento, importação, deploy, validação, pendências
specs/             artefatos do Spec Kit (spec, plan, research, data model, tasks) por feature
```

## Comandos de gestão

| Comando | Para quê |
|---|---|
| `importar_catalogo <arquivo> [--dry-run] [--imagens DIR] [--demo] [--relatorio ARQ]` | importa ou atualiza o catálogo por planilha |
| `limpar_catalogo_demo [--sim]` | remove só produtos, categorias e coleções de demonstração |
| `carregar_catalogo_demo [--se-vazio]` | carrega o catálogo fictício |
| `carregar_conteudo_demo [--se-vazio]` | cria o conteúdo inicial da home e das páginas (sem depoimentos inventados) |
| `regenerar_midia_demo` | recria as imagens de demonstração que faltam (disco temporário, como no Render), sem alterar o banco |
