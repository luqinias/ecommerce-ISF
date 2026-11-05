# Contexto da empresa — padrões internos adotados (Fase 0)

> Análise **somente leitura** de dois projetos internos da Irrigação Sem Fronteiras (ISF), feita em 2026-11-04.
> Nenhum arquivo `.env`, chave ou credencial foi lido ou reproduzido. Das variáveis de ambiente, registramos **apenas os nomes**, tirados do `.env.example`.

| Projeto | Caminho | Papel |
|---|---|---|
| `frotas_back` | `/home/lucaslira/back-irrigacao/frotas_back` | API Django do FarmEvolution (gestão de frotas agrícolas) |
| `farmevolution_web` | `/home/lucaslira/irrigacao/farmevolution_web` | Front Next.js do FarmEvolution |

**Observação de marca:** FarmEvolution é um **produto** da ISF. A landing assina "por ISF · Irrigação Sem Fronteiras", e os Termos e a Política de Privacidade ficam em `ias.irrigacaosemfronteiras.com.br`. Os dois projetos **não trazem logo, paleta nem textos institucionais da própria ISF**. Isso ficou registrado em `pendencias-empresa.md`.

---

## 1. Back-end Django (`frotas_back`)

### 1.1 Stack e dependências
| Item | Encontrado |
|---|---|
| Python | **3.12** (`requires-python >=3.12`, venv `python3.12`) |
| Django | **6.0.3** |
| Dependências | **uv** (`pyproject.toml` + `uv.lock`, com `[dependency-groups] dev`) e um `requirements.txt` paralelo (desatualizado: tem libs que não estão no pyproject) |
| Libs relevantes | `python-dotenv`, `dj-database-url`, `psycopg2-binary`, `pillow`, `django-jazzmin` (admin), `django-axes` (bloqueio de login), `django-anymail[brevo]` (e-mail), `django-storages[s3]`, `jsonschema`, `openpyxl`, `celery[redis]`, `redis`, DRF + simplejwt + drf-spectacular, `django-filter`, `django-cors-headers` |
| Dev | `pytest`, `pytest-django`, `pytest-cov`, `factory-boy`, `pytest-factoryboy`, `ruff`, `pylint-django` |

### 1.2 Estrutura e settings
- **Apps na raiz** do repositório (`core/`, `users/`, `products/`…), sem pasta `apps/`. O `core/` guarda settings, urls, wsgi/asgi, models base, `services/`, `events/`, `fields/` e `validators.py`.
- **Settings em arquivo único** (`core/settings.py`), com `python-dotenv` lendo `.env` e `os.getenv`. Os comportamentos variam por flags: `DEBUG`, `USE_S3`, `RUNNING_TESTS`.
- Os defaults são seguros: `DEBUG=False`. Em produção, `CACHE_URL` é obrigatório e o settings falha cedo com `ImproperlyConfigured`. Cookies `Secure` e `X_FRAME_OPTIONS=DENY` valem fora do DEBUG. `SECURE_PROXY_SSL_HEADER` e `SECURE_SSL_REDIRECT` são ligados por variável.
- `LANGUAGE_CODE="pt-br"`, `TIME_ZONE="America/Sao_Paulo"`, `USE_TZ=True`.

### 1.3 Infraestrutura
| Item | Encontrado |
|---|---|
| Banco | PostgreSQL em produção; SQLite em dev e testes (fallback automático) |
| Mídia | `FileSystemStorage` local; S3 (`django-storages`) quando `USE_S3=True`. Estáticos também vão para o S3 em produção |
| Cache | Redis em produção (`CACHE_URL`), LocMem em dev e testes |
| Filas | Celery + Redis (broker), resultado em `django-db`, modo eager nos testes |
| E-mail | Anymail/Brevo; console backend em DEBUG |
| Servidor | EC2 + **supervisor** + **gunicorn** + **Nginx** (ver `docs/chat-guide.md` e o README) |
| Docker | **Não há Dockerfile nem compose.** Docker só sobe a infra local com `docker run` (`postgres:16`, `redis:7`) |
| CI/CD | **Não há** pipeline versionado (nem `.github/` nem `.gitlab-ci`) |

**Variáveis de ambiente esperadas (somente nomes):** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `CACHE_URL`, `USE_S3`, `USE_S3_IN_DEBUG`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, `AWS_STATIC_CUSTOM_DOMAIN`, `EMAIL_BACKEND`, `BREVO_API_KEY`, `DEFAULT_FROM_EMAIL`, `BASE_URL`, `TRUST_PROXY_HEADERS`, `SECURE_SSL_REDIRECT`, `CELERY_BROKER_URL`, além de variáveis específicas do domínio de frotas e de IA, que não se aplicam aqui.

### 1.4 Padrões de código
- **Nomes:** classes, campos, funções e variáveis em **inglês** (`Product`, `Supplier`, `min_unit_of_movement`). `verbose_name`, `help_text`, mensagens e docs em **pt-BR**, envolvidos em `gettext_lazy as _`. Comentários em pt-BR explicam o *porquê*. Há exceções pontuais em português (`TipoCombustivel`), mas o padrão dominante é o inglês.
- **Models base** (`core/models.py`):
  - `CleanSaveModel`: `save()` chama `full_clean()`, então a validação de domínio fica em `Model.clean()`;
  - `UUIDTimeStampedModel`: PK `UUIDField` + `created_at` / `updated_at`;
  - `ActiveUUIDTimeStampedModel`: acrescenta `active` (soft toggle). **Não há soft delete**; a exclusão é substituída por `active=False`.
- **Choices:** `models.TextChoices` em `choices.py` por app.
- **Camadas:** `services.py` para escrita transacional (`@transaction.atomic`), `selectors.py` para leitura, eventos de domínio pós-commit (`core/events`) e handlers finos. Apps simples deixam a regra em `Model.clean()`. Signals tradicionais coexistem.
- **Serviço de e-mail base:** `core/services/email.py` → `SendEmailBase` (texto + HTML, destinatários normalizados).
- **Admin:** Jazzmin com ícones Font Awesome e ordem de apps configurada; `list_display`, `search_fields`, `autocomplete_fields`, `filter_horizontal` e `get_queryset` com `select_related` / `prefetch_related`.
- **Autenticação:** `AUTH_USER_MODEL = "users.User"` (customizado), backend de login por e-mail ou username e `django-axes` (5 tentativas, 15 min de bloqueio).

### 1.5 Testes e qualidade
- **pytest + pytest-django** (`pytest.ini` com `DJANGO_SETTINGS_MODULE`, cobertura por app via `--cov`). Os arquivos de teste aparecem como `tests.py`, `tests/`, `test_*.py` e `tests_*.py`. **factory_boy** só em `refuel/tests/factories.py`. Cobertura global aproximada de 84%.
- **Ruff** (sem `[tool.ruff]` configurado, ou seja, regras padrão) e `pylint-django` (`.pylintrc`). **Não há pre-commit** nem tipagem estática (mypy). Usam-se type hints nos services.

### 1.6 Convenções de git
- **Conventional Commits em pt-BR**, minúsculas, com escopo opcional por app: `feat(maintenances): …`, `fix: …`, `test(dashboard): …`, `docs: …`.
- Branches: `main` + `feat/<descricao>` (também aparece `feature/…`).
- O README em pt-BR traz pré-requisitos, instalação, execução, variáveis e um guia manual separado (`COMO-RODAR-LOCALMENTE.md`).

---

## 2. Front-end (`farmevolution_web`)

**Stack:** Next.js 16, React 19, TypeScript, Tailwind v4, `lucide-react` (ícones), componentes de UI feitos in-house. O projeto **já usa Spec Kit** `1.0.9.dev0` com a integração `claude`, script `sh`, numeração sequencial e separador `-` (comandos `/speckit-*`), além de uma constituição em `.specify/memory/constitution.md`.

### 2.1 Identidade visual — design system "Campo" (`DESIGN.md`, `app/globals.css`)
O norte criativo é "O Caderno de Campo": papel quente, tinta verde-floresta e ouro de colheita como assinatura.

| Token | Claro | Escuro | Uso |
|---|---|---|---|
| `--bg` | `#f5f4ef` | `#0e1310` | fundo ("Papel") |
| `--surface` | `#ffffff` | `#151b17` | cartões e inputs |
| `--surface-2` / `-3` | `#efede6` / `#e6e3da` | `#1b231e` / `#232d27` | hover, cabeçalhos, skeleton |
| `--border` / `-strong` | `#dedad0` / `#c7c2b5` | `#29332c` / `#3a473e` | bordas |
| `--fg` / `-muted` / `-subtle` | `#1a1f1b` / `#555d56` / `#676e67` | `#e7ece8` / `#a3aea6` / `#849089` | texto |
| `--primary` / `-hover` | `#1d6a44` / `#17573a` | `#46b980` / `#5bc792` | **única cor de ação** |
| `--primary-soft` / `-fg` | `#e2efe7` / `#145033` | `#183526` / `#8fdcb3` | badges e botão soft |
| `--brand-gold` | `#f2b01e` | `#f2b01e` | assinatura da marca, CTA da landing (nunca texto sobre papel) |
| `--accent` | `#9a6400` | `#f2b53c` | acento textual |
| `--danger` / `--info` / `--success` | `#b42318` / `#1d5fa8` / `#1b7a45` | — | semânticos, cada um com par `*-soft` / `*-soft-fg` |
| `--sidebar` | `#11251a` | `#0a0f0c` | superfície escura da marca ("Mata Noturna") |
| `--ring` | `#2f8a5c` | `#5bc792` | foco |

- **Tipografia:** **Manrope** (corpo e títulos, pesos 400 a 800, títulos com `letter-spacing: -0.025em`) e **JetBrains Mono** (códigos e SKUs, `tabular-nums`). Escala: display 2.75rem/800, headline 28px/800, title 16px/700, body 14px/1.5, label 13px/600, caption 12px/600, micro 11px/700.
- **Raios:** 6 / 8 (controles) / 12 (callouts) / 16px (cartões); badges em pílula.
- **Sombras:** `sm 0 1px 2px rgb(26 31 27/.06)`, `md` para popovers, `lg 0 24px 48px -12px rgb(26 31 27/.22)` para dialogs. Regra *flat-at-rest*: nada flutua em repouso.
- **Controles:** alturas 32/40/48px; foco com borda primária + anel de 3px a 20%; container de até 1280px com gutter de 16px no mobile e 32px a partir de `md`.
- **Movimento:** 150–250ms, respeitando `prefers-reduced-motion`.
- **Acessibilidade:** meta WCAG 2.2 AA verificada nos dois temas.
- **Logo:** só existe o do FarmEvolution (gota + folha, gradiente `#FFD24D` → `#E09A00`). **Não reutilizar como logo da ISF.**

Há uma segunda fonte, `frotas_back/identidade-visual-farmevolution.md` (app mobile e e-mails), com outra paleta: verde `#69BC6D`, verde profundo `#143C14` e fonte de sistema. Ela é **inconsistente** com o web. Adotamos o "Campo" porque é a versão web, tem tokens claro/escuro e contraste AA já verificado.

### 2.2 Componentes a traduzir para partials Django
| Front (React) | Partial Django proposto |
|---|---|
| `ui/button` (primary, secondary, ghost, danger, soft; sm, md, lg, icon; loading) | `componentes/botao.html` + classes `.btn .btn--primary …` |
| `ui/badge` (tons soft/soft-fg, com ponto) | `componentes/badge.html` (selos "Novidade", "Demo", contagem) |
| `ui/field` (label, dica, erro via `aria-describedby`) | `componentes/campo.html` (form de orçamento) |
| `common/section` (cartão de 16px, cabeçalho com borda) | `componentes/secao.html` |
| `ui/empty-state`, `ui/skeleton`, `ui/spinner` | estados vazio e carregando (HTMX `hx-indicator`) |
| `ui/dialog`, `ui/tabs`, `ui/toaster` | `<dialog>` nativo, abas da ficha técnica, toast de "adicionado ao orçamento" |
| `landing/faq-section` | acordeão do FAQ (`<details>`) |
| `landing/landing-header`, `landing/footer`, `landing/contact-section` | `partials/header.html`, `partials/footer.html`, bloco de contato |

### 2.3 Tom de voz
Português do Brasil, **direto e operacional**, em segunda pessoa ("você") e com coloquialidade leve ("Fale com a gente", "A gente conversa"). Frases curtas, orientadas a benefício concreto. Há uma regra explícita em `PRODUCT.md`: **não inventar depoimentos, clientes ou números de uso**. Isso coincide com a regra deste projeto.

**Reaproveitáveis como base, com adaptação:** "Fale com a gente", o formato de FAQ (pergunta direta e resposta objetiva) e a assinatura "ISF · Irrigação Sem Fronteiras". Nenhum texto institucional da ISF (sobre, missão, contatos) foi encontrado.

---

## 3. O que será reaproveitado

| Área | Decisão para o e-commerce |
|---|---|
| Python / Django | Python **3.12**, Django **6.0.x** |
| Dependências | **uv** com `pyproject.toml` + `uv.lock` e grupo `dev`. Sem `requirements.txt` paralelo; se o deploy pedir um, ele é gerado com `uv export` |
| Env | `python-dotenv` + `.env.example`, com os mesmos nomes de variáveis quando se aplicarem (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_*`, `USE_S3`, `AWS_*`, `BREVO_API_KEY`, `DEFAULT_FROM_EMAIL`, `CACHE_URL`, `TRUST_PROXY_HEADERS`…) e defaults seguros (`DEBUG=False`) |
| Banco | PostgreSQL em produção e no compose; SQLite como fallback em dev e testes |
| Models base | `CleanSaveModel` / `UUIDTimeStampedModel` / `ActiveUUIDTimeStampedModel` (portados para `apps/core/models.py`) |
| Nomes | código em inglês; `verbose_name`, textos, URLs e docs em pt-BR |
| Camadas | `services.py` (escrita), `selectors.py` (leitura) e regras em `Model.clean()` |
| Admin | **Jazzmin** (ícones e ordem configurados) + **django-axes** no login do admin |
| E-mail | **django-anymail[brevo]**; console backend em dev; classe base inspirada em `SendEmailBase` |
| Mídia | `FileSystemStorage` por padrão, S3 opcional via `USE_S3` (mesmo padrão) |
| Planilhas | `openpyxl` (XLSX) + `csv` da biblioteca padrão |
| Validação JSON | `jsonschema` para validar `atributos` contra `schema_atributos` |
| Testes | pytest + pytest-django + pytest-cov + factory-boy (factories por app, desde o início) |
| Lint | **ruff** (check + format), agora com `[tool.ruff]` explícito |
| Servidor | **gunicorn** atrás de Nginx (mesmo modelo do EC2 interno) |
| Git | Conventional Commits em pt-BR com escopo por app; branches `feat/<descricao>` |
| Spec Kit | mesma integração do front (`claude`, `sh`, numeração sequencial, comandos `/speckit-*`) |
| Visual | tokens "Campo" (cores claro/escuro, raios, sombras, alturas de controle), traduzidos para variáveis CSS puras. A tipografia Manrope + JetBrains Mono foi substituída em 05/11/2026 pela da referência (Fraunces + Inter) |

---

## 4. Conflitos e decisões

Quando a decisão envolvia escolha, seguimos a opção marcada como recomendada.

| # | Padrão interno | Este projeto | Motivo |
|---|---|---|---|
| C1 | Front é SPA Next.js/React | **Django templates + HTMX** (sem React, sem build) | Seção 1 do prompt vence |
| C2 | Settings em arquivo único | **`config/settings/{base,dev,prod,test}.py`** com o mesmo `python-dotenv` e os mesmos defaults seguros | A feature 001 pede settings por ambiente. Mantemos a lib e a filosofia "falhar fechado" |
| C3 | Apps na raiz | **`apps/<app>`** (core, catalogo, orcamentos, conteudo, seo) | Estrutura sugerida em 6.6. O nome do pacote do app fica em pt-BR, porque é parte do domínio e das URLs; classes e campos ficam em inglês |
| C4 | Nomes de model em pt-BR no prompt (`Categoria`, `Produto`, `Orcamento`…) | Classes em **inglês**: `Category`, `Collection`, `Product`, `Variant`, `ProductImage`, `Quote`, `QuoteItem`, `SiteConfiguration`, `Banner`, `Highlight`, `HowItWorksStep`, `PortfolioItem`, `Testimonial`, `FAQItem`. `verbose_name` em pt-BR | Seção 1: "código segue o padrão do projeto interno". Os management commands mantêm os nomes do prompt (`importar_catalogo`, `limpar_catalogo_demo`) porque são interface de operação documentada |
| C5 | Celery + Redis para tarefas assíncronas | **Sem Celery por enquanto.** E-mail enviado dentro de `transaction.on_commit`, com falha registrada sem perder o lead | Princípio 9 (simplicidade). Volume de orçamentos baixo. Celery entra depois se for preciso |
| C6 | Estáticos no S3 em produção | **WhiteNoise** para estáticos; S3 opcional apenas para mídia (`USE_S3`) | Monolito com um único deploy (seção 1 e feature 010). Menos infraestrutura |
| C7 | Sem Docker para a aplicação | **Dockerfile + docker-compose** (web + postgres) para subir com um comando. O deploy continua compatível com gunicorn/supervisor/Nginx | DoD: "projeto sobe com um comando" |
| C8 | Sem CI | **Fora do escopo agora.** Proposta de um GitHub Actions mínimo (ruff + pytest) na feature 010, se a equipe quiser | Não há padrão interno a seguir; fica registrado como pendência |
| C9 | DRF / JWT / CORS / drf-spectacular | **Não incluídos** | Não há API agora (seção 1, "Futuro"). Os models ficam limpos para uma API futura |
| C10 | `django-import-export` (sugerido em 6.5) não existe no interno | **Não adotar.** A importação fica num service próprio (`apps/catalogo/services/importacao.py`), usado pelo command e por uma tela de upload no admin, com o mesmo relatório e `--dry-run` | Idempotência por SKU, variações e atributos JSON exigem lógica própria. Evita duas implementações e uma dependência a mais |
| C11 | Rate limit via DRF throttling | Limite de taxa do formulário de orçamento com **cache do Django** (decorator simples) + honeypot | Sem DRF. Sem lib nova |
| C12 | Paleta mobile (`#69BC6D`) × paleta web "Campo" (`#1d6a44`) | **"Campo"** como base provisória. Paleta e logo da ISF são **pendência** | Tem tokens claro/escuro e contraste AA verificado. A marca ISF real ainda não foi fornecida |
| C13 | Logo FarmEvolution | **Não usar.** Wordmark textual "Irrigação Sem Fronteiras" como placeholder | O logo é de outro produto |
| C14 | `pylint-django` + ruff | **Só ruff** | Uma ferramenta cobre lint e format. Menos dependências |
| C15 | Sem pre-commit | Não adicionar agora; `ruff` e `pytest` documentados no README | Regra "não adicione dependências fora do necessário" |

---

## 5. Insumos para as próximas fases
- **Fase 1:** os tokens "Campo" serão a *identidade*. Da referência extraímos apenas **métricas de layout** (container, grid, espaçamentos, proporções) e comportamento.
- **Fase 3:** a constituição do Spec Kit deve citar as decisões C1 a C15.
- Pendências para a empresa: ver `docs/pendencias-empresa.md`.
