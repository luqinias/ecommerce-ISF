import json
import re

import pytest
from django.core.management import call_command

from apps.conteudo.models import FAQItem
from tests.factories import CategoryFactory, CollectionFactory, ProductFactory, ProductImageFactory, VariantFactory

pytestmark = pytest.mark.django_db

SCHEMA = [
    {"key": "material", "label": "Material", "type": "text"},
    {"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True},
]


def blocos(html):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def tipos(html):
    return [n["@type"] for b in blocos(html) for n in b["@graph"]]


@pytest.fixture
def produto():
    cat = CategoryFactory(name="Gotejamento", attribute_schema=SCHEMA)
    p = ProductFactory(name='Gotejador "X" </script>', primary_category=cat, attributes={"material": "PE"})
    VariantFactory(product=p, attributes={"vazao": 2})
    ProductImageFactory(product=p)
    return p


def test_robots(client):
    txt = client.get("/robots.txt").content.decode()
    assert "Disallow: /admin/" in txt and "Disallow: /orcamento/" in txt
    assert "Sitemap: http://testserver/sitemap.xml" in txt


def test_sitemap_so_ativos(client, produto):
    inativo = ProductFactory(name="Fora", active=False)
    CollectionFactory(name="Safra")
    call_command("carregar_conteudo_demo")
    xml = client.get("/sitemap.xml").content.decode()
    assert f"http://testserver{produto.get_absolute_url()}" in xml
    assert inativo.get_absolute_url() not in xml
    assert "/categoria-produto/gotejamento/" in xml and "/colecao/safra/" in xml and "/sobre/" in xml
    assert "<lastmod>" in xml


def test_produto_jsonld_sem_preco_e_escapado(client, produto):
    resp = client.get(produto.get_absolute_url())
    html = resp.content.decode()
    assert html.count("</script>") == html.count("<script")  # nenhum script quebrado pelo nome
    grafo = [n for b in blocos(html) for n in b["@graph"]]
    prod = next(n for n in grafo if n["@type"] == "Product")
    assert prod["name"] == 'Gotejador "X" </script>' and "offers" not in prod
    assert prod["image"][0].startswith("http://testserver/")
    nomes = {p["name"]: p["value"] for p in prod["additionalProperty"]}
    assert nomes == {"Material": "PE", "Vazão": "2"}
    bc = next(n for n in grafo if n["@type"] == "BreadcrumbList")
    assert [i["name"] for i in bc["itemListElement"]] == ["Início", "Gotejamento", produto.name]
    assert {"Organization", "WebSite"} <= set(tipos(html))
    assert '<meta property="og:type" content="product">' in html
    assert f'<link rel="canonical" href="http://testserver{produto.get_absolute_url()}">' in html


def test_home_faq_e_site(client):
    FAQItem.objects.create(question="Tem mínimo?", answer="Sim.")
    html = client.get("/").content.decode()
    t = tipos(html)
    assert "FAQPage" in t and "WebSite" in t and "Organization" in t
    site = next(n for b in blocos(html) for n in b["@graph"] if n["@type"] == "WebSite")
    assert site["potentialAction"]["target"]["urlTemplate"] == "http://testserver/busca/?q={search_term_string}"


def test_listagem_collectionpage_e_noindex_em_filtro(client, produto):
    html = client.get("/categoria-produto/gotejamento/").content.decode()
    assert "CollectionPage" in tipos(html) and "BreadcrumbList" in tipos(html)
    assert "noindex" not in html
    filtrado = client.get("/categoria-produto/gotejamento/?ordem=nome").content.decode()
    assert "noindex" in filtrado and "CollectionPage" not in tipos(filtrado)


@pytest.mark.parametrize("url", ["/busca/?q=x", "/orcamento/", "/nao-existe/"])
def test_noindex(client, url):
    assert "noindex" in client.get(url).content.decode()


def test_paginas_tem_titulo_descricao_e_canonical(client, produto):
    call_command("carregar_conteudo_demo")
    vistos = set()
    for url in [
        "/",
        "/produtos/",
        "/categoria-produto/gotejamento/",
        produto.get_absolute_url(),
        "/sobre/",
        "/contato/",
        "/novidades/",
        "/politica-de-privacidade/",
    ]:
        html = client.get(url).content.decode()
        titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
        assert titulo and titulo not in vistos, url
        vistos.add(titulo)
        assert re.search(r'<meta name="description" content="[^"]{20,}"', html), url
        assert 'rel="canonical"' in html, url
