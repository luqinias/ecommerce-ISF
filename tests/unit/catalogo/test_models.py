from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.catalogo.models import Collection, Product, Variant
from tests.factories import SCHEMA_GOTEJO, CategoryFactory, CollectionFactory, ProductFactory, ProductImageFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def gotejo():
    return CategoryFactory(name="Gotejamento", attribute_schema=SCHEMA_GOTEJO)


def test_arvore_tem_no_maximo_dois_niveis(gotejo):
    filha = CategoryFactory(name="Fitas", parent=gotejo)
    with pytest.raises(ValidationError):
        CategoryFactory(name="Neta", parent=filha)


def test_categoria_com_filhas_nao_pode_virar_filha(gotejo):
    CategoryFactory(parent=gotejo)
    outra = CategoryFactory()
    gotejo.parent = outra
    with pytest.raises(ValidationError):
        gotejo.save()


def test_url_de_subcategoria_inclui_pai(gotejo):
    filha = CategoryFactory(name="Fitas gotejadoras", parent=gotejo)
    assert filha.get_absolute_url() == "/categoria-produto/gotejamento/fitas-gotejadoras/"


def test_subcategoria_herda_atributos(gotejo):
    filha = CategoryFactory(
        parent=gotejo, attribute_schema=[{"key": "espessura", "label": "Espessura", "type": "number"}]
    )
    chaves = [a["key"] for a in filha.effective_schema]
    assert chaves == ["material", "autocompensante", "pressao_max", "vazao", "espessura"]


def test_schema_invalido_na_categoria():
    with pytest.raises(ValidationError) as erro:
        CategoryFactory(attribute_schema=[{"key": "x", "type": "number"}])
    assert "attribute_schema" in erro.value.message_dict


def test_produto_valida_atributos(gotejo):
    with pytest.raises(ValidationError) as erro:
        ProductFactory(primary_category=gotejo, attributes={"pressao_max": "abc"})
    assert "attributes" in erro.value.message_dict
    p = ProductFactory(
        primary_category=gotejo, attributes={"pressao_max": 2, "material": "PE", "autocompensante": True}
    )
    assert p.spec_rows == [("Material", "PE"), ("Autocompensante", "Sim"), ("Pressão máxima", "2 bar")]


def test_produto_minimo_multiplo_do_passo(gotejo):
    with pytest.raises(ValidationError):
        ProductFactory(primary_category=gotejo, attributes={"pressao_max": 1}, min_quantity=30, quantity_step=20)


def test_slug_unico_gerado():
    a = ProductFactory(name="Filtro de disco")
    b = ProductFactory(name="Filtro de disco")
    assert a.slug == "filtro-de-disco" and b.slug == "filtro-de-disco-2"


def test_categoria_principal_entra_nas_categorias(gotejo):
    p = ProductFactory(primary_category=gotejo, attributes={"pressao_max": 1})
    assert list(p.categories.all()) == [gotejo]


def test_variacao_valida_e_unica(gotejo):
    p = ProductFactory(primary_category=gotejo, attributes={"pressao_max": 1})
    Variant.objects.create(product=p, sku="V1", attributes={"vazao": 2})
    with pytest.raises(ValidationError):
        Variant.objects.create(product=p, sku="V2", attributes={"vazao": 2})
    with pytest.raises(ValidationError):
        Variant.objects.create(product=p, sku="V3", attributes={"vazao": "muito"})
    with pytest.raises(ValidationError):
        Variant.objects.create(product=p, sku="V4", attributes={})
    v = Variant.objects.create(product=p, sku="V5", attributes={"vazao": 4.5})
    assert v.label == "Vazão: 4,5 L/h"


def test_novidade_por_data():
    hoje = timezone.localdate()
    assert ProductFactory(new_until=hoje + timedelta(days=1)).is_new
    assert not ProductFactory(new_until=hoje - timedelta(days=1)).is_new
    assert not ProductFactory().is_new


def test_colecao_visivel_por_periodo():
    hoje = timezone.localdate()
    CollectionFactory(name="Sem período")
    CollectionFactory(name="Vigente", starts_on=hoje - timedelta(days=1), ends_on=hoje + timedelta(days=1))
    CollectionFactory(name="Passada", starts_on=hoje - timedelta(days=30), ends_on=hoje - timedelta(days=1))
    CollectionFactory(name="Inativa", active=False)
    assert sorted(c.name for c in Collection.objects.visible()) == ["Sem período", "Vigente"]


def test_colecao_fim_antes_do_inicio():
    hoje = timezone.localdate()
    with pytest.raises(ValidationError):
        CollectionFactory(starts_on=hoje, ends_on=hoje - timedelta(days=1))


def test_so_uma_colecao_principal():
    a = CollectionFactory(is_main=True)
    CollectionFactory(is_main=True)
    a.refresh_from_db()
    assert not a.is_main


def test_imagem_gera_miniaturas_webp():
    img = ProductImageFactory()
    assert img.card.name.endswith(".webp") and img.large.name.endswith(".webp")
    assert img.alt_text == img.product.name


def test_produto_inativo_ou_categoria_inativa_fica_fora():
    ativo = ProductFactory()
    ProductFactory(active=False)
    cat = ProductFactory().primary_category
    cat.active = False
    cat.save()
    assert list(Product.objects.active()) == [ativo]
