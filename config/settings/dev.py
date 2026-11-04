"""Desenvolvimento local."""

import os

from .base import *  # noqa: F403
from .base import env_bool, env_list

DEBUG = env_bool("DEBUG", True)
SECRET_KEY = os.getenv("SECRET_KEY") or "dev-inseguro-nao-usar-em-producao"
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
STORAGES = {**STORAGES, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}  # noqa: F405
