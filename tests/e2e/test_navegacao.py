import pytest
from playwright.sync_api import expect

from tests.factories import CategoryFactory, ProductFactory

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def catalogo():
    raiz = CategoryFactory(name="Gotejamento")
    outra = CategoryFactory(name="Filtragem")
    for i in range(33):
        ProductFactory(name=f"Produto {i:02d}", primary_category=raiz, relevance=i)
    ProductFactory(name="AAA Filtro", primary_category=outra, categorias=[raiz])


def test_navegar_por_categoria_ordenar_e_paginar(base, pagina_desktop, catalogo):
    page = pagina_desktop
    page.goto(base + "/")
    page.get_by_role("button", name="Todas as Categorias").click()
    page.locator("#dd-categorias").get_by_role("link", name="Gotejamento").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Gotejamento")
    expect(page.locator(".grade-produtos > li")).to_have_count(30)
    page.select_option("#ordem", "nome")
    page.wait_for_url("**ordem=nome")
    expect(page.locator(".card-produto__nome").first).to_have_text("AAA Filtro")
    page.get_by_role("link", name="Página 2").click()
    page.wait_for_url("**/page/2/?ordem=nome")
    expect(page.locator(".grade-produtos > li")).to_have_count(4)
    page.get_by_role("link", name="Todos", exact=True).click()
    page.locator(".chip", has_text="Filtragem").click()
    expect(page.locator(".grade-produtos > li")).to_have_count(1)


def test_sugestoes_de_busca(base, pagina_desktop, catalogo):
    page = pagina_desktop
    page.goto(base + "/")
    page.fill("#busca-q", "filtro")
    expect(page.locator("#busca-sugestoes .sugestao")).to_have_count(1)
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", level=1)).to_contain_text("filtro")
