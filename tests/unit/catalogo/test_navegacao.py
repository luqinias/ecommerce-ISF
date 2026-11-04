import re
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from apps.catalogo import selectors
from apps.catalogo.models import Product
from tests.factories import CategoryFactory, CollectionFactory, ProductFactory, VariantFactory

pytestmark = pytest.mark.django_db

VAR = [{"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True}]


@pytest.fixture
def arvore():
    raiz = CategoryFactory(name="Gotejamento", attribute_schema=VAR)
    filha = CategoryFactory(name="Fitas", parent=raiz)
    filtro = CategoryFactory(name="Filtragem")
    produtos = [ProductFactory(name=f"Gotejador {i:02d}", primary_category=raiz, relevance=i) for i in range(32)]
    fita = ProductFactory(name="Fita 16", primary_category=filha)
    ambos = ProductFactory(name="Filtro de disco", primary_category=filtro, categorias=[raiz])
    for p in produtos[:2]:
        VariantFactory(product=p, attributes={"vazao": 2})
    return {"raiz": raiz, "filha": filha, "filtro": filtro, "fita": fita, "ambos": ambos}


def nomes(html):
    return re.findall(r'class="card-produto__nome">([^<]+)<', html)


def test_categoria_raiz_inclui_filhas_e_pagina_em_30(client, arvore):
    resp = client.get("/categoria-produto/gotejamento/")
    html = resp.content.decode()
    assert resp.status_code == 200
    assert len(nomes(html)) == 30
    assert "34 produtos" in html.replace("<b>", "").replace("</b>", "")
    assert "Mostrando 1–30 de 34 produtos" in html
    pagina2 = client.get("/categoria-produto/gotejamento/page/2/").content.decode()
    assert len(nomes(pagina2)) == 4
    assert client.get("/categoria-produto/gotejamento/page/3/").status_code == 404


def test_page_1_redireciona(client, arvore):
    resp = client.get("/categoria-produto/gotejamento/page/1/?ordem=nome")
    assert resp.status_code == 301 and resp["Location"] == "/categoria-produto/gotejamento/?ordem=nome"


def test_subcategoria_url_canonica_e_breadcrumb(client, arvore):
    assert client.get("/categoria-produto/fitas/").status_code == 301
    assert client.get("/categoria-produto/outro-pai/fitas/").status_code == 404
    html = client.get("/categoria-produto/gotejamento/fitas/").content.decode()
    assert nomes(html) == ["Fita 16"]
    assert 'href="/categoria-produto/gotejamento/">Gotejamento</a>' in html


def test_ordenacao(client, arvore):
    html = client.get("/categoria-produto/gotejamento/?ordem=nome").content.decode()
    lista = nomes(html)
    assert lista == sorted(lista)
    relevantes = nomes(client.get("/categoria-produto/gotejamento/").content.decode())
    assert relevantes[0] == "Gotejador 31"
    assert 'name="robots" content="noindex' in html


def test_chips_com_contagem_e_filtro(client, arvore):
    html = client.get("/categoria-produto/gotejamento/").content.decode()
    assert re.search(r"Filtragem <small>1</small>", html)
    filtrado = client.get("/categoria-produto/gotejamento/?tipo=filtragem").content.decode()
    assert nomes(filtrado) == ["Filtro de disco"]
    assert 'aria-current="true">Filtragem' in filtrado
    ignorado = client.get("/categoria-produto/gotejamento/?tipo=nao-existe").content.decode()
    assert len(nomes(ignorado)) == 30


def test_produto_inativo_e_categoria_inativa(client, arvore):
    Product.objects.filter(name="Fita 16").update(active=False)
    assert "Fita 16" not in client.get("/categoria-produto/gotejamento/fitas/").content.decode()
    arvore["filtro"].active = False
    arvore["filtro"].save()
    assert client.get("/categoria-produto/filtragem/").status_code == 404


def test_busca_por_nome_sku_e_variacao(client, arvore):
    v = VariantFactory(product=arvore["fita"], sku="FITA-XYZ-16", attributes={"vazao": 1.6})
    assert nomes(client.get("/busca/?q=filtro disco").content.decode()) == ["Filtro de disco"]
    assert nomes(client.get(f"/busca/?q={v.sku.lower()}").content.decode()) == ["Fita 16"]
    vazio = client.get("/busca/?q=inexistente").content.decode()
    assert "Nenhum produto encontrado" in vazio and "noindex" in vazio


def test_sugestoes(client, arvore):
    html = client.get("/busca/sugestoes/?q=got").content.decode()
    assert html.count('class="sugestao"') == 6
    assert "Ver todos os resultados" in html
    assert client.get("/busca/sugestoes/?q=g").content.decode().strip() == ""


def test_colecao_vigente_e_fora_do_periodo(client):
    hoje = timezone.localdate()
    col = CollectionFactory(name="Safra", starts_on=hoje - timedelta(days=1), order_deadline=hoje + timedelta(days=10))
    ProductFactory(name="Kit safra").collections.add(col)
    html = client.get("/colecao/safra/").content.decode()
    assert nomes(html) == ["Kit safra"] and "Pedidos até" in html
    CollectionFactory(name="Antiga", ends_on=hoje - timedelta(days=1))
    assert client.get("/colecao/antiga/").status_code == 404


def test_catalogo_geral_tem_todas_categorias(client, arvore):
    html = client.get("/produtos/").content.decode()
    assert "Ver todas as categorias" in html and 'id="todas-categorias"' in html
    assert 'rel="canonical" href="http://testserver/produtos/"' in html


def test_menu_lista_categorias_e_colecoes(client, arvore):
    CollectionFactory(name="Lançamentos")
    html = client.get("/").content.decode()
    assert 'href="/categoria-produto/gotejamento/"' in html
    assert 'href="/categoria-produto/gotejamento/fitas/"' in html
    assert 'href="/colecao/lancamentos/"' in html


def test_listagem_sem_n_mais_1(client, arvore):
    client.get("/categoria-produto/gotejamento/")
    with CaptureQueriesContext(connection) as ctx:
        client.get("/categoria-produto/gotejamento/")
    poucas = len(ctx.captured_queries)
    ProductFactory.create_batch(5, primary_category=arvore["raiz"])
    with CaptureQueriesContext(connection) as ctx:
        client.get("/categoria-produto/gotejamento/")
    assert len(ctx.captured_queries) == poucas


def test_paginas_visiveis():
    from apps.catalogo.views import _paginas_visiveis

    assert _paginas_visiveis(1, 3) == [1, 2, 3]
    assert _paginas_visiveis(6, 20) == [1, None, 5, 6, 7, None, 20]


def test_selector_ordem_desconhecida():
    assert selectors.normalizar_ordem("xpto") == "relevantes"
