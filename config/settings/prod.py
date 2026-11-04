"""Produção: falha cedo sem as variáveis obrigatórias."""

import os

from .base import *  # noqa: F403
from .base import env_bool, require

DEBUG = False
SECRET_KEY = require("SECRET_KEY", os.getenv("SECRET_KEY", ""))
require("ALLOWED_HOSTS", os.getenv("ALLOWED_HOSTS", ""))

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = False

if EMAIL_BACKEND.endswith("console.EmailBackend") and os.getenv("BREVO_API_KEY"):  # noqa: F405
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
