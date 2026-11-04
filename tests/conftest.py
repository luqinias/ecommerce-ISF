import os

import pytest

# Playwright (sync) roda num loop de eventos; o live_server do Django precisa disso.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def _limpar_cache():
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def site_config(db):
    from apps.core.models import SiteConfiguration

    config = SiteConfiguration.load()
    config.whatsapp_number = "5511999990000"
    config.contact_email = "contato@example.com"
    config.quote_recipient_emails = "vendas@example.com\ncomercial@example.com"
    config.save()
    return config
