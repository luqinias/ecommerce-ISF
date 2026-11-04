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


def test_sem_ids_nao_ha_bloco_de_analytics(client):
    assert "isf-analytics" not in client.get("/").content.decode()


def test_ids_configurados_viram_dado_inerte(client, site_config):
    site_config.gtm_id = "GTM-ABC1234"
    site_config.meta_pixel_id = "1234567890"
    site_config.save()
    html = client.get("/").content.decode()
    import json

    bloco = re.search(r'<script type="application/json" id="isf-analytics">(.*?)</script>', html).group(1)
    assert json.loads(bloco) == {"gtm": "GTM-ABC1234", "pixel": "1234567890"}
    assert "googletagmanager.com/gtm.js" not in html and 'fbevents.js"' not in html  # nada carregado no HTML
