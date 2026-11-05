"""Settings comuns a todos os ambientes.

Valores sensíveis vêm de variáveis de ambiente (`.env` em dev, lido por python-dotenv).
Defaults são seguros: sem `DEBUG`, sem hosts liberados.
"""

import mimetypes
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Imagens base slim nem sempre conhecem estes tipos (usados nas miniaturas e fontes).
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("font/woff2", ".woff2")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "sim", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "")
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "axes",
    "anymail",
    "apps.core",
    "apps.catalogo",
    "apps.orcamentos",
    "apps.conteudo",
    "apps.seo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site",
            ],
            "builtins": ["apps.core.templatetags.isf"],
        },
    },
]

# Banco: DATABASE_URL tem prioridade; depois DB_* (padrão interno); senão SQLite.
if os.getenv("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=60)}
elif os.getenv("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHE_URL = os.getenv("CACHE_URL", "")
if CACHE_URL.startswith("redis"):
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": CACHE_URL}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "isf"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# django-axes: mesmo padrão do projeto interno (5 tentativas, 15 min).
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.25
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Cache das ilustrações do catálogo de demonstração (gerado no build do Docker; ver apps/catalogo/services/demo_midia.py)
DEMO_MIDIA_DIR = Path(os.getenv("DEMO_MIDIA_DIR", str(BASE_DIR / ".cache" / "demo-midia")))
DEMO_MIDIA_RAPIDA = env_bool("DEMO_MIDIA_RAPIDA", False)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

USE_S3 = env_bool("USE_S3", False)
SERVE_MEDIA = env_bool("SERVE_MEDIA", False)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
if USE_S3:
    # Só mídia vai para o S3 (decisão C6). Requer `uv sync --extra s3`.
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME", ""),
            "region_name": os.getenv("AWS_S3_REGION_NAME", ""),
            "custom_domain": os.getenv("AWS_S3_CUSTOM_DOMAIN") or None,
            "querystring_auth": False,
            "file_overwrite": False,
        },
    }

# E-mail: Brevo via Anymail quando houver chave; console em dev.
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
ANYMAIL = {"BREVO_API_KEY": os.getenv("BREVO_API_KEY", "")}
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "Irrigação Sem Fronteiras <nao-responda@example.com>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # lista de orçamento dura 30 dias
SESSION_SAVE_EVERY_REQUEST = False

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

TRUST_PROXY_HEADERS = env_bool("TRUST_PROXY_HEADERS", False)
if TRUST_PROXY_HEADERS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simples": {"format": "{levelname} {asctime} {name}: {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simples"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
    "loggers": {"django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False}},
}

JAZZMIN_SETTINGS = {
    "site_title": "ISF · Admin",
    "site_header": "Irrigação Sem Fronteiras",
    "site_brand": "ISF · Catálogo",
    "welcome_sign": "Administração do catálogo e dos orçamentos",
    "copyright": "Irrigação Sem Fronteiras",
    "show_ui_builder": False,
    "navigation_expanded": True,
    "order_with_respect_to": ["orcamentos", "catalogo", "conteudo", "core", "auth", "axes"],
    "icons": {
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "core.siteconfiguration": "fas fa-sliders-h",
        "catalogo.category": "fas fa-sitemap",
        "catalogo.collection": "fas fa-layer-group",
        "catalogo.product": "fas fa-tint",
        "catalogo.catalogimport": "fas fa-file-import",
        "orcamentos.quote": "fas fa-file-signature",
        "conteudo.banner": "fas fa-image",
        "conteudo.highlight": "fas fa-star",
        "conteudo.howitworksstep": "fas fa-list-ol",
        "conteudo.portfolioitem": "fas fa-tractor",
        "conteudo.testimonial": "fas fa-comment",
        "conteudo.faqitem": "fas fa-question-circle",
        "conteudo.page": "fas fa-file-alt",
        "conteudo.post": "fas fa-newspaper",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
}
JAZZMIN_UI_TWEAKS = {
    "theme": "default",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-success",
    "accent": "accent-success",
}

# Catálogo
CATALOG_PAGE_SIZE = 30


def require(name: str, value: str) -> str:
    """Falha cedo quando uma configuração obrigatória de produção está ausente."""
    if not value:
        raise ImproperlyConfigured(f"Variável de ambiente obrigatória ausente: {name}")
    return value
