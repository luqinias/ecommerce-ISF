import pytest
from playwright.sync_api import expect

from apps.core.models import SiteConfiguration

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]
RASTREADORES = ("googletagmanager.com", "connect.facebook.net")


@pytest.fixture
def com_ids():
    c = SiteConfiguration.load()
    c.gtm_id = "GTM-TESTE123"
    c.meta_pixel_id = "1234567890"
    c.save()


def _registrar(page):
    pedidos = []
    page.route(
        "**/*",
        lambda r: (
            (pedidos.append(r.request.url), r.fulfill(status=200, body=""))
            if any(d in r.request.url for d in RASTREADORES)
            else r.continue_()
        ),
    )
    return pedidos


def test_nada_antes_e_carrega_apos_aceitar(base, pagina_desktop, com_ids):
    page = pagina_desktop
    pedidos = _registrar(page)
    page.goto(base + "/")
    expect(page.locator("#aviso-cookies")).to_be_visible()
    page.wait_for_timeout(500)
    assert pedidos == []
    page.get_by_role("button", name="Aceitar todos").click()
    expect(page.locator("#aviso-cookies")).to_be_hidden()
    page.wait_for_timeout(500)
    assert any("gtm.js?id=GTM-TESTE123" in u for u in pedidos)
    assert any("fbevents.js" in u for u in pedidos)
    pedidos.clear()
    page.goto(base + "/produtos/")
    page.wait_for_timeout(500)
    assert any("gtm.js" in u for u in pedidos)  # vale nas próximas páginas


def test_so_necessarios_nunca_carrega(base, pagina_desktop, com_ids):
    page = pagina_desktop
    pedidos = _registrar(page)
    page.goto(base + "/")
    page.get_by_role("button", name="Só os necessários").click()
    page.goto(base + "/produtos/")
    page.wait_for_timeout(500)
    assert pedidos == []
    expect(page.locator("#aviso-cookies")).to_be_hidden()
    page.get_by_role("button", name="Preferências de cookies").click()
    expect(page.locator("#aviso-cookies")).to_be_visible()


def test_revogar_recarrega_sem_rastreadores(base, pagina_desktop, com_ids):
    page = pagina_desktop
    pedidos = _registrar(page)
    page.goto(base + "/")
    page.get_by_role("button", name="Aceitar todos").click()
    page.context.add_cookies([{"name": "_ga", "value": "x", "url": base}])
    page.get_by_role("button", name="Preferências de cookies").click()
    pedidos.clear()
    with page.expect_navigation():
        page.get_by_role("button", name="Só os necessários").click()
    page.wait_for_timeout(500)
    assert pedidos == []
    assert "_ga" not in {c["name"] for c in page.context.cookies()}
