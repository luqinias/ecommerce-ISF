"""regenerar_midia_demo: recria arquivos de demonstração ausentes (disco temporário), sem alterar o banco."""

import io

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from PIL import Image

from apps.catalogo.models import Product, ProductImage
from apps.catalogo.services import demo as demo_catalogo
from apps.conteudo.models import Banner, PortfolioItem

pytestmark = pytest.mark.django_db


def _nomes():
    nomes = []
    for img in ProductImage.objects.order_by("pk"):
        nomes += [img.image.name, img.card.name, img.large.name]
    banner = Banner.objects.get(is_demo=True)
    nomes += [banner.image_main.name, banner.image_2.name, banner.image_3.name]
    nomes += [item.image.name for item in PortfolioItem.objects.order_by("pk")]
    return nomes


@pytest.fixture
def demo():
    call_command("carregar_catalogo_demo")
    call_command("carregar_conteudo_demo")


def test_recria_todos_os_arquivos_nos_mesmos_nomes(demo, capsys):
    nomes = _nomes()
    assert all(nomes) and len(nomes) > 100
    for nome in nomes:  # simula o deploy: banco intacto, pasta de mídia vazia
        default_storage.delete(nome)
    assert not any(default_storage.exists(n) for n in nomes)

    call_command("regenerar_midia_demo")

    assert all(default_storage.exists(n) for n in nomes)
    assert _nomes() == nomes  # nenhum registro mudou de nome
    saida = capsys.readouterr().out
    assert f"{ProductImage.objects.count()} imagens de produto" in saida


def test_miniaturas_recriadas_sao_webp_no_tamanho_certo(demo):
    img = ProductImage.objects.order_by("pk").first()
    for nome in (img.image.name, img.card.name, img.large.name):
        default_storage.delete(nome)
    call_command("regenerar_midia_demo")
    for campo, lado in (("card", 400), ("large", 900)):
        with default_storage.open(getattr(img, campo).name, "rb") as arquivo, Image.open(arquivo) as webp:
            assert webp.format == "WEBP"
            assert max(webp.size) <= lado  # no modo rápido dos testes a original é menor que 400 px


def test_idempotente_e_so_recria_o_que_falta(demo):
    img = ProductImage.objects.order_by("pk").first()
    default_storage.delete(img.card.name)  # só a miniatura sumiu
    primeira = demo_catalogo.regenerar_midia()
    assert primeira["recriadas"] == 0 and primeira["miniaturas"] == 1
    segunda = demo_catalogo.regenerar_midia()
    assert segunda == {"recriadas": 0, "miniaturas": 0, "colecoes": 0, "reais_ausentes": 0}


def test_nao_inventa_imagem_de_produto_real(demo):
    produto = Product.objects.order_by("pk").first()
    produto.is_demo = False
    produto.save(update_fields=["is_demo"])
    buffer = io.BytesIO()
    Image.new("RGB", (50, 50), "red").save(buffer, format="PNG")
    real = ProductImage(product=produto, order=99)
    real.image.save("foto-real.png", ContentFile(buffer.getvalue()), save=False)
    real.save()
    default_storage.delete(real.image.name)

    contagem = demo_catalogo.regenerar_midia()

    assert contagem["reais_ausentes"] == 1
    assert not default_storage.exists(real.image.name)
