"""Regressão: em produção os estáticos usam manifest com hash; toda referência precisa existir."""

import pytest
from django.core.management import call_command
from django.test import override_settings

pytestmark = pytest.mark.django_db

PAGINAS = ["/", "/produtos/", "/novidades/", "/contato/", "/orcamento/", "/nao-existe/"]


def test_paginas_renderizam_com_manifest(client, tmp_path, settings):
    storages = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
    with override_settings(STORAGES=storages, STATIC_ROOT=tmp_path, DEBUG=False):
        call_command("collectstatic", "--noinput", verbosity=0)
        call_command("carregar_conteudo_demo")
        for url in PAGINAS:
            resp = client.get(url)
            assert resp.status_code in (200, 404), url
            assert "/static/css/tokens." in resp.content.decode(), url  # nome com hash
