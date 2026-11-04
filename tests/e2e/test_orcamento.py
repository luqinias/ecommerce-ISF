from urllib.parse import unquote

import pytest
from playwright.sync_api import expect

from apps.core.models import SiteConfiguration
from apps.orcamentos.models import Quote
from tests.factories import CategoryFactory, ProductFactory, VariantFactory

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]

SCHEMA = [{"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True}]


@pytest.fixture
def cenario():
    config = SiteConfiguration.load()
    config.whatsapp_number = "5534999990000"
    config.quote_recipient_emails = "vendas@example.com"
    config.save()
    cat = CategoryFactory(name="Gotejamento", attribute_schema=SCHEMA)
    p = ProductFactory(name="Gotejador", sku="G1", primary_category=cat, min_quantity=100, quantity_step=100)
    VariantFactory(product=p, sku="G1-2", attributes={"vazao": 2})
    return p


def test_adicionar_revisar_e_enviar(base, pagina_desktop, cenario):
    page = pagina_desktop
    page.route("https://wa.me/**", lambda r: r.fulfill(status=200, body="whatsapp"))  # não sai para a internet
    page.goto(base + cenario.get_absolute_url())
    page.get_by_role("button", name="Aceitar todos").click()
    page.get_by_role("radio", name="2 L/h").check()
    page.get_by_role("button", name="Aumentar quantidade").click()
    page.locator("[data-adicionar]").click()
    expect(page.locator("#contador-lista")).to_have_text("1")
    expect(page.locator(".toast")).to_contain_text("Gotejador adicionado")
    page.locator(".toast a").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Vamos preparar seu orçamento?")
    expect(page.locator(".tabela-itens")).to_contain_text("G1-2")
    expect(page.locator("#qtd-1")).to_have_value("200")
    page.fill("#id_name", "Maria")
    page.fill("#id_email", "maria@example.com")
    page.fill("#id_phone", "34999990000")
    page.fill("#id_city", "Uberaba")
    page.select_option("#id_state", "MG")
    page.check("#id_consent")
    with page.expect_request("https://wa.me/**") as req:
        page.get_by_role("button", name="Enviar pedido de orçamento").click()
        expect(page.get_by_role("heading", level=1)).to_have_text("Sua solicitação foi recebida!")
    url = unquote(req.value.url)
    quote = Quote.objects.get()
    assert url.startswith("https://wa.me/5534999990000?text=") and quote.code in url and "200 peças" in url
    assert quote.items.get().variant_sku == "G1-2"


def test_orcamento_rapido_no_header(base, pagina_desktop, cenario):
    page = pagina_desktop
    page.goto(base + "/")
    link = page.locator("a[data-orcamento-rapido]")
    href = unquote(link.get_attribute("href"))
    assert href.startswith("https://wa.me/5534999990000?text=") and "orçamento rápido" in href
