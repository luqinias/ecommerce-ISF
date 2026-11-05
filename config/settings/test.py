"""Testes (pytest)."""

import tempfile
from pathlib import Path

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "teste-somente"  # noqa: S105
ALLOWED_HOSTS = ["*"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "testes"}}
AXES_ENABLED = False
BASE_URL = "http://testserver"
# Ilustrações de demonstração pequenas e sem supersampling, num cache fora do projeto
DEMO_MIDIA_RAPIDA = True
DEMO_MIDIA_DIR = Path(tempfile.gettempdir()) / "isf-testes-demo-midia"
