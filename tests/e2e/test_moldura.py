import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def test_menu_mobile_abre_e_fecha(base, pagina_mobile):
    page = pagina_mobile
    page.goto(base + "/")
    menu = page.locator("#menu-mobile")
    expect(menu).to_be_hidden()
    page.get_by_role("button", name="Abrir menu").click()
    expect(menu).to_be_visible()
    page.keyboard.press("Escape")
    expect(menu).to_be_hidden()
    page.get_by_role("button", name="Abrir menu").click()
    page.locator(".menu-mobile__fundo").click(position={"x": 370, "y": 400})
    expect(menu).to_be_hidden()
    assert page.evaluate("document.documentElement.scrollWidth") <= 390


def test_dropdown_categorias_desktop(base, pagina_desktop):
    page = pagina_desktop
    page.goto(base + "/")
    gatilho = page.get_by_role("button", name="Todas as Categorias")
    gatilho.click()
    expect(page.locator("#dd-categorias")).to_be_visible()
    expect(gatilho).to_have_attribute("aria-expanded", "true")
    page.keyboard.press("Escape")
    expect(page.locator("#dd-categorias")).to_be_hidden()


def test_404_dentro_da_moldura(base, pagina_desktop):
    page = pagina_desktop
    resp = page.goto(base + "/nao-existe/")
    assert resp.status == 404
    expect(page.get_by_role("heading", level=1)).to_have_text("Esta página não existe.")
