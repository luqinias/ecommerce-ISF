import json
import re

import pytest

from tests.factories import CategoryFactory, ProductFactory, ProductImageFactory, VariantFactory

pytestmark = pytest.mark.django_db

SCHEMA = [
    {"key": "material", "label": "Material", "type": "text"},
    {"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True},
    {"key": "diametro", "label": "Diâmetro", "type": "choice", "choices": [20, 16], "unit": "mm", "variant": True},
]


@pytest.fixture
def produto():
    pai = CategoryFactory(name="Irrigação")
    cat = CategoryFactory(name="Gotejamento", parent=pai, attribute_schema=SCHEMA)
    p = ProductFactory(name="Gotejador X", sku="GX", primary_category=cat, attributes={"material": "PE"},
                       min_quantity=100, quantity_step=50, sale_unit="piece", description="Texto longo. " * 80)  # fmt: skip
    VariantFactory(product=p, sku="GX-2-16", attributes={"vazao": 2, "diametro": 16})
    VariantFactory(product=p, sku="GX-4-20", attributes={"vazao": 4, "diametro": 20})
    ProductImageFactory(product=p)
    ProductImageFactory(product=p, kind="environment")
    for i in range(6):
        ProductFactory(name=f"Vizinho {i}", primary_category=cat)
    return p


def test_pagina_do_produto(client, produto):
    resp = client.get("/produto/gotejador-x/")
    html = resp.content.decode()
    assert resp.status_code == 200
    assert html.count("<h1") == 1
    # seletor gerado do schema, em fieldset com legend (acessível)
    assert re.search(r"<legend>Vazão:", html) and re.search(r"<legend>Diâmetro:", html)
    assert html.index('value="20"') < html.index('value="16"')  # ordem das opções da definição
    assert 'aria-disabled="true"' in html
    assert "Escolha vazão e diâmetro para continuar." in html
    assert 'min="100"' in html and 'step="50"' in html
    assert "Mínimo de 100 peças, em múltiplos de 50" in html
    # ficha técnica
    assert "<dt>Material</dt><dd>PE</dd>" in html
    assert "<dt>Vazão</dt><dd>2 L/h, 4 L/h</dd>" in html
    # breadcrumb com pai
    assert 'href="/categoria-produto/irrigacao/">Irrigação</a>' in html
    # galeria e descrição expansível
    assert html.count("data-galeria-mini") == 2
    assert "Ler descrição completa" in html
    # relacionados
    assert html.count('class="card-produto"') == 5


def test_json_de_variacoes(client, produto):
    html = client.get("/produto/gotejador-x/").content.decode()
    bruto = re.search(r'data-variacoes="([^"]+)"', html).group(1).replace("&quot;", '"')
    dados = json.loads(bruto)
    assert {d["sku"] for d in dados} == {"GX-2-16", "GX-4-20"}
    assert dados[0]["atributos"] == {"vazao": "2", "diametro": "16"}


def test_produto_sem_variacao_tem_botao_liberado(client):
    ProductFactory(name="Kit simples")
    html = client.get("/produto/kit-simples/").content.decode()
    assert "data-adicionar aria-disabled" not in html
    assert "<fieldset" not in html


def test_produto_inativo_404(client, produto):
    produto.active = False
    produto.save()
    assert client.get("/produto/gotejador-x/").status_code == 404


def test_whatsapp_do_produto(client, produto, site_config):
    html = client.get("/produto/gotejador-x/").content.decode()
    assert "https://wa.me/5511999990000?text=" in html
    assert "Gotejador%20X%20%28GX%29%2C%20quantidade%3A%20100" in html
