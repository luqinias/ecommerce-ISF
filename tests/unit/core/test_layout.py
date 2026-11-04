import re

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_tem_moldura_completa(client):
    resp = client.get(reverse("conteudo:home"))
    html = resp.content.decode()
    assert resp.status_code == 200
    assert html.count("<h1") == 1
    for marco in ("<header", "<nav", "<main", "<footer"):
        assert marco in html
    assert 'class="pular-conteudo"' in html
    assert 'id="aviso-cookies"' in html
    assert "Todas as Categorias" in html


def test_sem_configuracao_mostra_definir_e_nao_inventa_contato(client):
    html = client.get("/").content.decode()
    assert "[DEFINIR]" in html
    assert "wa.me" not in html  # sem número, nada de link de WhatsApp


def test_com_whatsapp_configurado_gera_link_wa_me(client, site_config):
    html = client.get("/").content.decode()
    links = re.findall(r'href="(https://wa\.me/[^"]+)"', html)
    assert links
    assert all(link.startswith("https://wa.me/5511999990000?text=") for link in links)
    assert "contato@example.com" in html


def test_menus_vazios_nao_quebram(client):
    html = client.get("/").content.decode()
    assert "As categorias aparecem aqui" in html


def test_banner_de_cookies_some_com_consentimento(client):
    client.cookies["isf_consent"] = "necessarios"
    html = client.get("/").content.decode()
    assert re.search(r'id="aviso-cookies"[^>]*hidden', html)
