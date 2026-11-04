# Guia de deploy

O site é um único processo Django (gunicorn) com PostgreSQL. Estáticos saem pelo **WhiteNoise** (nomes com hash + gzip/brotli). Mídia (fotos do catálogo e do admin) fica num volume servido pelo Nginx, ou no **S3** (`USE_S3=True`). Não há fila nem worker: os e-mails de orçamento saem logo após a gravação do pedido.

> A forma de produção ainda não foi decidida (pendência **P7**): Docker ou EC2 com supervisor, gunicorn e Nginx, como no projeto interno. As duas estão descritas abaixo.

## 1. Variáveis de ambiente (produção)

| Variável | Obrigatória | Exemplo / observação |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | ✔ | `config.settings.prod` (o padrão do `wsgi.py`) |
| `SECRET_KEY` | ✔ | chave longa e aleatória. Sem ela a aplicação **não sobe** |
| `ALLOWED_HOSTS` | ✔ | `catalogo.exemplo.com.br` |
| `CSRF_TRUSTED_ORIGINS` | ✔ | `https://catalogo.exemplo.com.br` |
| `BASE_URL` | ✔ | `https://catalogo.exemplo.com.br` (canonical, sitemap, JSON-LD, links dos e-mails) |
| `DATABASE_URL` ou `DB_*` | ✔ | `postgres://usuario:senha@host:5432/isf` |
| `CACHE_URL` | recomendada | `redis://host:6379/0`. Com vários workers, deixa o limite de taxa e o cache da configuração compartilhados |
| `EMAIL_BACKEND`, `BREVO_API_KEY`, `DEFAULT_FROM_EMAIL` | ✔ para e-mail | com `BREVO_API_KEY`, o backend do Brevo (Anymail) é ativado automaticamente |
| `TRUST_PROXY_HEADERS` | atrás de proxy | `True` (lê `X-Forwarded-Proto` e `X-Forwarded-For`) |
| `SECURE_SSL_REDIRECT` | recomendada | `True` quando o proxy não redireciona sozinho |
| `SECURE_HSTS_SECONDS` | recomendada | comece com `3600`; depois `31536000` |
| `SECURE_COOKIES` | | `True` (padrão). Só desligue para testar em HTTP |
| `USE_S3` + `AWS_*` | opcional | mídia no S3 (requer `uv sync --extra s3`) |
| `SERVE_MEDIA` | não usar em produção | serve `/media/` pelo Django (só no compose local) |
| `LOAD_DEMO_DATA` | | `True` carrega a demonstração **apenas se o banco estiver vazio** (entrypoint do Docker) |

Depois do primeiro deploy, preencha no admin **Configurações do site** (WhatsApp, e-mails que recebem orçamentos, endereço, CNPJ, redes, IDs de GTM e Pixel). Esses dados vêm de `docs/pendencias-empresa.md`.

## 2. Docker

```bash
cp .env.example .env              # preencha as variáveis de produção
docker compose up -d --build      # Postgres + app; migra e carrega a demo se o banco estiver vazio
docker compose exec web python manage.py createsuperuser
```

- O `docker-compose.yml` do repositório é para **ambiente local em HTTP**: serve mídia pelo Django e desliga cookies `Secure`. Em produção, use um proxy com HTTPS na frente, `SECURE_COOKIES=True` e mídia pelo Nginx (volume `media`) ou no S3. Para isso, sobrescreva com um `docker-compose.prod.yml`.
- A imagem roda como usuário não-root, já traz os estáticos coletados (manifest com hash) e tem `HEALTHCHECK` em `/healthz/`.
- Para atualizar: `git pull && docker compose up -d --build`. As migrações rodam no entrypoint.

## 3. VM / EC2 sem Docker (padrão do projeto interno)

```bash
sudo useradd -m isf && sudo mkdir -p /srv/isf/{app,media} /var/log/isf
cd /srv/isf/app && git clone <repo> . && uv sync --frozen --no-default-groups
export DJANGO_SETTINGS_MODULE=config.settings.prod   # e as demais variáveis (ex.: /etc/isf.env)
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
uv run python manage.py createsuperuser
```

- Gunicorn com supervisor: [`exemplos/supervisor.conf`](exemplos/supervisor.conf).
- Nginx com HTTPS (Let's Encrypt), mídia e proxy: [`exemplos/nginx.conf`](exemplos/nginx.conf). Ajuste `MEDIA_ROOT` (ou um link simbólico) para `/srv/isf/media`.

## 4. Healthcheck e monitoramento

- `GET /healthz/` → `200 {"status": "ok"}` quando a aplicação e o banco respondem; `503` se o banco falhar. Use no load balancer, no Docker e no uptime monitor.
- Logs vão para stdout/stderr (nível em `LOG_LEVEL`). Falhas de envio de e-mail ficam registradas no próprio orçamento (campo "erro de e-mail" no admin), sem perder o lead.

## 5. Backup

- **Banco:** `pg_dump` diário (os orçamentos são a informação mais valiosa).
- **Mídia:** o volume `media` (ou o bucket S3, com versionamento).
- O catálogo também pode ser reconstruído pela planilha (`importar_catalogo`). Guarde a última planilha importada.

## 6. Checklist de go-live

- [ ] `python manage.py check --deploy` sem avisos (HSTS e `SECURE_SSL_REDIRECT` configurados)
- [ ] `BASE_URL` com o domínio final; `robots.txt` e `sitemap.xml` conferidos e o sitemap enviado ao Search Console
- [ ] Configuração do site preenchida (sem `[DEFINIR]` visível): WhatsApp, e-mails, endereço, CNPJ, horário
- [ ] Teste de orçamento de ponta a ponta: e-mail da equipe, confirmação do cliente e WhatsApp
- [ ] Catálogo real importado e `limpar_catalogo_demo` executado; conteúdo de demonstração da home revisado (itens marcados como demonstração)
- [ ] Textos de Termos e Política de Privacidade validados (P5)
- [ ] IDs de GTM e Pixel, se forem usados (P19); conferir que só carregam após "Aceitar todos"
- [ ] Backups agendados
- [ ] CI opcional: [`exemplos/ci-github-actions.yml`](exemplos/ci-github-actions.yml) (P8)
