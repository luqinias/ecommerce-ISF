import pytest


@pytest.fixture
def base(live_server):
    return live_server.url


@pytest.fixture
def pagina_mobile(browser):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="pt-BR")
    page = ctx.new_page()
    yield page
    ctx.close()


@pytest.fixture
def pagina_desktop(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR")
    page = ctx.new_page()
    yield page
    ctx.close()
