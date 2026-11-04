import pytest
from django.core.management import call_command
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def conteudo():
    call_command("carregar_conteudo_demo")


def test_faq_e_ver_mais_projetos(base, pagina_desktop, conteudo):
    page = pagina_desktop
    page.goto(base + "/")
    itens = page.locator(".faq__item")
    expect(itens.nth(0)).to_have_attribute("open", "")
    itens.nth(2).locator("summary").click()
    expect(itens.nth(2)).to_have_attribute("open", "")
    expect(itens.nth(0)).to_have_attribute("open", "")  # não exclusivo
    extra = page.locator(".portfolio__item--extra").first
    expect(extra).to_be_hidden()
    botao = page.get_by_role("button", name="Ver mais projetos (2) ↓")
    botao.click()
    expect(extra).to_be_visible()
    expect(page.get_by_role("button", name="Ver menos ↑")).to_have_attribute("aria-expanded", "true")


def test_carregar_mais_novidades(base, pagina_desktop):
    from tests.factories import ProductFactory

    ProductFactory.create_batch(25)
    page = pagina_desktop
    page.goto(base + "/novidades/")
    expect(page.locator("#lista-novidades > li")).to_have_count(20)
    page.get_by_role("link", name="Mostrar mais produtos").click()
    expect(page.locator("#lista-novidades > li")).to_have_count(25)
    expect(page.get_by_role("link", name="Mostrar mais produtos")).to_have_count(0)
