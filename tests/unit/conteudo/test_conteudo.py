import re
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.conteudo.models import FAQItem, Page, SectionText
from apps.conteudo.models import Testimonial as Depoimento
from apps.orcamentos.models import Quote
from tests.factories import CategoryFactory, CollectionFactory, ProductFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def conteudo():
    call_command("carregar_conteudo_demo")
    hoje = timezone.localdate()
    cat = CategoryFactory(name="Gotejamento", show_on_home=True)
    col = CollectionFactory(name="Safra", featured=True, is_main=True, order_deadline=hoje + timedelta(days=20))
    CollectionFactory(name="Lançamentos", featured=True)
    for i in range(12):
        p = ProductFactory(name=f"Produto {i}", primary_category=cat)
        p.collections.add(col)


def test_home_tem_as_secoes_na_ordem(client, conteudo):
    html = client.get("/").content.decode()
    assert html.count("<h1") == 1
    ids = ["hero-titulo", "vitrine-titulo", "colecoes-titulo", "portfolio-titulo", "categorias-titulo", "como-titulo",
           "faixa-titulo", "porque-titulo", "faq-titulo"]  # fmt: skip
    posicoes = [html.index(f'id="{i}"') for i in ids]
    assert posicoes == sorted(posicoes)
    assert "Recém-chegados" in html and 'id="vb-gotejamento"' in html
    assert "Ver mais projetos (2)" in html
    assert "Pedidos até" in html and "Safra" in html
    assert html.count('class="faq__item"') == 5


def test_sem_depoimentos_a_secao_nao_aparece(client, conteudo):
    assert "depoimentos-titulo" not in client.get("/").content.decode()
    Depoimento.objects.create(author="Fulano", text="Ótimo", authorized=False)
    assert "depoimentos-titulo" not in client.get("/").content.decode()
    Depoimento.objects.create(author="Ciclano", text="Muito bom", authorized=True, rating=4)
    html = client.get("/").content.decode()
    assert "depoimentos-titulo" in html and "★★★★<" in html


def test_texto_de_secao_editavel(client, conteudo):
    SectionText.objects.create(key="como_funciona", title="Quatro passos simples", kicker="Processo")
    html = client.get("/").content.decode()
    assert "Quatro passos simples" in html and ">Processo<" in html


def test_home_vazia_funciona(client):
    resp = client.get("/")
    assert resp.status_code == 200 and "[DEFINIR]" in resp.content.decode()


def test_paginas_institucionais(client, conteudo):
    sobre = client.get("/sobre/").content.decode()
    assert "Nossa história" in sobre and sobre.count("<h1") == 1
    priv = client.get("/politica-de-privacidade/").content.decode()
    assert 'id="cookies"' in priv and "Nesta página" in priv and "<ul><li>nome" in priv
    assert client.get("/termos-de-uso/").status_code == 200
    Page.objects.filter(slug="sobre").update(active=False)
    assert client.get("/sobre/").status_code == 404


def test_contato_grava_lead(client, conteudo):
    assert "Antes de entrar em contato" in client.get("/contato/").content.decode()
    dados = {
        "name": "João",
        "email": "j@example.com",
        "phone": "34 99999-1111",
        "message": "Quero irrigar 1 ha",
        "consent": "on",
    }
    resp = client.post("/contato/", dados)
    assert resp.status_code == 302
    q = Quote.objects.get()
    assert q.source == "contato" and q.message == "Quero irrigar 1 ha" and not q.items.exists()
    client.post("/contato/", {**dados, "website": "spam"})
    assert Quote.objects.count() == 1


def test_novidades_e_carregar_mais(client, conteudo):
    ProductFactory.create_batch(15)
    html = client.get("/novidades/").content.decode()
    assert len(re.findall(r'class="card-produto"', html)) == 20
    assert 'hx-get="/novidades/page/2/"' in html and "Entraram por último" in html
    pagina2 = client.get("/novidades/page/2/").content.decode()
    assert len(re.findall(r'class="card-produto"', pagina2)) == 7 and "Carregar mais" not in pagina2
    assert client.get("/novidades/page/3/").status_code == 404


def test_faq_de_contato_separado(client, conteudo):
    assert FAQItem.objects.filter(placement="contato").count() == 3
    assert "Quais são as formas de pagamento?" not in client.get("/").content.decode()


def test_demo_sem_depoimentos_e_idempotente():
    call_command("carregar_conteudo_demo")
    call_command("carregar_conteudo_demo", "--se-vazio")
    assert not Depoimento.objects.exists()
    assert Page.objects.filter(slug="sobre").count() == 1
