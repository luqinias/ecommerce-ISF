import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.catalogo.models import Category, Collection, Product, Variant

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo():
    call_command("carregar_catalogo_demo")


def test_carga_de_demonstracao(demo):
    assert 38 <= Product.objects.count() <= 45
    assert 6 <= Category.objects.filter(parent__isnull=True).count() <= 9
    assert Collection.objects.count() == 2
    assert not Product.objects.filter(is_demo=False).exists()
    assert not Product.objects.filter(images__isnull=True).exists()
    assert Collection.objects.filter(is_main=True).count() == 1
    call_command("carregar_catalogo_demo", "--se-vazio")
    assert Product.objects.count() <= 45


def test_comando_de_limpeza(demo):
    call_command("limpar_catalogo_demo", "--sim")
    assert not Product.objects.exists() and not Variant.objects.exists()


@pytest.fixture
def admin_client(client, django_user_model):
    user = django_user_model.objects.create_superuser("admin", "a@example.com", "senha-forte-123")
    client.force_login(user)
    return client


def test_admin_produto_mostra_ficha_tecnica_da_categoria(demo, admin_client):
    p = Product.objects.get(sku="GOT-001")
    resp = admin_client.get(reverse("admin:catalogo_product_change", args=[p.pk]))
    html = resp.content.decode()
    assert resp.status_code == 200
    assert 'name="attr__material"' in html and 'name="attr__autocompensante"' in html
    assert 'name="variants-0-attr__vazao"' in html


def test_admin_produto_novo_com_categoria_escolhida(demo, admin_client):
    cat = Category.objects.get(name="Kits")
    resp = admin_client.get(reverse("admin:catalogo_product_add") + f"?primary_category={cat.pk}")
    assert 'name="attr__area_atendida"' in resp.content.decode()


def test_admin_salva_atributos_validados(demo, admin_client):
    p = Product.objects.get(sku="KIT-001")
    url = reverse("admin:catalogo_product_change", args=[p.pk])
    dados = {
        "name": p.name, "slug": p.slug, "sku": p.sku, "primary_category": p.primary_category_id,
        "short_description": "x", "description": "y", "min_quantity": 1, "quantity_step": 1, "sale_unit": "kit",
        "active": "on", "relevance": 1, "categories": [p.primary_category_id],
        "attr__area_atendida": "abc", "attr__itens_inclusos": "Tudo",
        "variants-TOTAL_FORMS": 0, "variants-INITIAL_FORMS": 0, "images-TOTAL_FORMS": 0, "images-INITIAL_FORMS": 0,
    }  # fmt: skip
    resp = admin_client.post(url, dados)
    assert resp.status_code == 200  # erro de validação: número inválido
    dados["attr__area_atendida"] = "250"
    resp = admin_client.post(url, dados)
    assert resp.status_code == 302, resp.content.decode()[:2000]
    p.refresh_from_db()
    assert p.attributes == {"area_atendida": 250, "itens_inclusos": "Tudo"}


def test_admin_importacao_simulada(admin_client, tmp_path):
    from django.core.files.uploadedfile import SimpleUploadedFile

    from apps.catalogo.models import CatalogImport

    arq = SimpleUploadedFile("c.csv", b"sku_produto;nome;categoria\nA-1;Produto A;Bombas\n", content_type="text/csv")
    resp = admin_client.post(reverse("admin:catalogo_catalogimport_add"), {"file": arq, "dry_run": "on"})
    assert resp.status_code == 302
    imp = CatalogImport.objects.get()
    assert imp.status == "done" and "SIMULAÇÃO" in imp.summary
    assert not Product.objects.exists()
    detalhe = admin_client.get(reverse("admin:catalogo_catalogimport_change", args=[imp.pk]))
    assert "SIMULAÇÃO" in detalhe.content.decode()
