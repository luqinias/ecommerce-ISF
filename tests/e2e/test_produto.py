import pytest
from playwright.sync_api import expect

from tests.factories import CategoryFactory, ProductFactory, VariantFactory

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]

SCHEMA = [{"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True}]


@pytest.fixture
def produto():
    cat = CategoryFactory(name="Gotejamento", attribute_schema=SCHEMA)
    p = ProductFactory(name="Gotejador", sku="G1", primary_category=cat, min_quantity=100, quantity_step=100)
    VariantFactory(product=p, sku="G1-2", attributes={"vazao": 2})
    VariantFactory(product=p, sku="G1-4", attributes={"vazao": 4})
    return p


def test_variacao_bloqueia_botao_e_quantidade_respeita_minimo(base, pagina_desktop, produto):
    page = pagina_desktop
    page.goto(base + produto.get_absolute_url())
    botao = page.locator("[data-adicionar]")
    expect(botao).to_have_attribute("aria-disabled", "true")
    botao.click(force=True)  # aria-disabled: o usuário ainda consegue clicar e deve ver o aviso
    expect(page.locator("[data-aviso-variacao]")).to_be_visible()
    expect(page.locator("[data-aviso-variacao]")).to_have_text("Escolha vazão para continuar.")
    page.get_by_role("radio", name="4 L/h").check()
    expect(botao).to_have_attribute("aria-disabled", "false")
    expect(page.locator("[data-sku]")).to_have_text("G1-4")
    expect(page.locator("legend [data-valor-escolhido]")).to_have_text("4 L/h")
    qtd = page.locator("#quantidade")
    page.get_by_role("button", name="Aumentar quantidade").click()
    expect(qtd).to_have_value("200")
    page.get_by_role("button", name="Diminuir quantidade").click()
    page.get_by_role("button", name="Diminuir quantidade").click(force=True)
    expect(qtd).to_have_value("100")
    qtd.fill("30")
    qtd.blur()
    expect(qtd).to_have_value("100")
    qtd.fill("260")
    qtd.blur()
    expect(qtd).to_have_value("300")
