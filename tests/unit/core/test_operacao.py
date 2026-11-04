import importlib
import sys
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured, ValidationError

from apps.core.models import SiteConfiguration
from apps.core.whatsapp import formatar_mensagem, whatsapp_link


@pytest.mark.django_db
def test_healthz_ok(client):
    resp = client.get("/healthz/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
def test_healthz_503_quando_banco_falha(client):
    with mock.patch("apps.core.views.connection.cursor", side_effect=Exception("sem banco")):
        resp = client.get("/healthz/")
    assert resp.status_code == 503


def test_settings_de_producao_exigem_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "exemplo.com")
    sys.modules.pop("config.settings.prod", None)
    with mock.patch("dotenv.load_dotenv"), pytest.raises(ImproperlyConfigured):
        importlib.import_module("config.settings.prod")


def test_settings_base_tem_debug_falso_por_padrao(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    sys.modules.pop("config.settings.base", None)
    with mock.patch("dotenv.load_dotenv"):
        base = importlib.import_module("config.settings.base")
    assert base.DEBUG is False


@pytest.mark.django_db
def test_configuracao_e_singleton_e_invalida_cache():
    a = SiteConfiguration.load()
    a.site_name = "Teste"
    a.save()
    b = SiteConfiguration(site_name="Outra")
    b.save()
    assert SiteConfiguration.objects.count() == 1
    assert SiteConfiguration.load().site_name == "Outra"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("campo", "valor"), [("whatsapp_number", "+55 11 9999"), ("gtm_id", "UA-123"), ("meta_pixel_id", "abc")]
)
def test_configuracao_valida_formatos(campo, valor):
    config = SiteConfiguration.load()
    setattr(config, campo, valor)
    with pytest.raises(ValidationError) as erro:
        config.save()
    assert campo in erro.value.message_dict


def test_mensagem_mantem_placeholder_desconhecido():
    assert formatar_mensagem("Olá {produto} {x}", produto="Filtro") == "Olá Filtro {x}"


def test_whatsapp_link_sem_numero_cai_no_contato():
    assert whatsapp_link(SiteConfiguration(whatsapp_number="")) == "/contato/"


def test_whatsapp_link_codifica_mensagem():
    link = whatsapp_link(SiteConfiguration(whatsapp_number="5511999990000"), "Olá, {categoria}!", categoria="Filtros")
    assert link == "https://wa.me/5511999990000?text=Ol%C3%A1%2C%20Filtros%21"
