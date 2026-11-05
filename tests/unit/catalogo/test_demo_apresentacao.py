"""Demonstração com aparência de catálogo real: ilustrações próprias, textos completos e sem marcações por item."""

import re

import pytest
from django.core.management import call_command

from apps.catalogo.models import Collection, Product, ProductImage
from apps.catalogo.services import demo_dados, demo_midia

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo():
    call_command("carregar_catalogo_demo")
    call_command("carregar_conteudo_demo")


def _texto_visivel(html: str) -> str:
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def test_cada_produto_tem_foto_detalhe_e_aplicacao(demo):
    assert set(Product.objects.values_list("sku", flat=True)) == set(demo_dados.PRODUTOS)
    for produto in Product.objects.prefetch_related("images"):
        tipos = [img.kind for img in produto.images.all()]
        assert tipos.count("product") == 2 and tipos.count("environment") == 1, produto.sku
    assert not ProductImage.objects.filter(card="").exists()  # miniaturas WebP geradas


def test_descricoes_completas_sem_texto_de_placeholder(demo):
    for produto in Product.objects.all():
        assert "Destaques:" in produto.description, produto.sku
        assert "fictício" not in produto.description and "[DEFINIR]" not in produto.description


def test_colecoes_de_demonstracao_tem_imagem(demo):
    assert Collection.objects.filter(is_demo=True).count() == 2
    assert not Collection.objects.filter(is_demo=True, image="").exists()


@pytest.mark.parametrize(
    "url",
    ["/", "/produtos/", "/categoria-produto/gotejamento/", "/produto/filtro-de-disco/", "/sobre/", "/contato/",
     "/novidades/", "/termos-de-uso/", "/politica-de-privacidade/"],
)  # fmt: skip
def test_paginas_sem_definir_nem_selo_demo(client, demo, url):
    resp = client.get(url)
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "[DEFINIR]" not in _texto_visivel(html)
    assert "selo--demo" not in html
    assert "Ambiente de demonstração" in html  # um aviso discreto, no rodapé


def test_recarregar_troca_a_demonstracao_sem_duplicar(demo):
    produtos, imagens = Product.objects.count(), ProductImage.objects.count()
    call_command("carregar_catalogo_demo", "--recarregar")
    call_command("carregar_conteudo_demo", "--recarregar")
    assert Product.objects.count() == produtos and ProductImage.objects.count() == imagens


def test_cache_de_midia_e_idempotente():
    demo_midia.gerar()
    assert demo_midia.gerar() == 0  # mesma versão: nada é redesenhado
    assert demo_midia.miniatura("demo/GOT-001.jpg", 400).exists()
