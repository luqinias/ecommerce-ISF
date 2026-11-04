import json
from unittest import mock

import pytest
from django.core import mail
from django.urls import reverse

from apps.orcamentos.models import Quote
from apps.orcamentos.services import mensagem_whatsapp
from tests.factories import CategoryFactory, ProductFactory, VariantFactory

pytestmark = pytest.mark.django_db

SCHEMA = [{"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True}]
DADOS = {
    "name": "Maria Silva", "company": "Sítio Boa Água", "email": "maria@example.com", "phone": "(34) 99999-0000",
    "city": "Uberaba", "state": "MG", "message": "Área de 2 ha", "consent": "on",
}  # fmt: skip


@pytest.fixture
def catalogo():
    cat = CategoryFactory(name="Gotejamento", attribute_schema=SCHEMA)
    got = ProductFactory(name="Gotejador", sku="G1", primary_category=cat, min_quantity=100, quantity_step=100)
    v2 = VariantFactory(product=got, sku="G1-2", attributes={"vazao": 2})
    VariantFactory(product=got, sku="G1-4", attributes={"vazao": 4})
    tubo = ProductFactory(name="Tubo PE", sku="T1", sale_unit="meter", min_quantity=50, quantity_step=50)
    return {"got": got, "v2": v2, "tubo": tubo}


def adicionar(client, produto, variacao=None, qtd=None, htmx=True, **extra):
    dados = {
        "product": produto.pk,
        "variant": variacao.pk if variacao else "",
        "quantity": qtd or produto.min_quantity,
        **extra,
    }
    headers = {"HTTP_HX_REQUEST": "true"} if htmx else {}
    return client.post(reverse("orcamentos:adicionar"), dados, **headers)


def test_adicionar_com_htmx_atualiza_contador_e_toast(client, catalogo):
    resp = adicionar(client, catalogo["got"], catalogo["v2"])
    assert resp.status_code == 200
    assert 'id="contador-lista"' in resp.content.decode() and 'hx-swap-oob="true"' in resp.content.decode()
    gatilho = json.loads(resp["HX-Trigger"])["isf:toast"]
    assert "Gotejador adicionado" in gatilho["mensagem"] and gatilho["link"] == "/orcamento/"


def test_mesma_variacao_soma_quantidade(client, catalogo):
    adicionar(client, catalogo["got"], catalogo["v2"], 100)
    adicionar(client, catalogo["got"], catalogo["v2"], 250)  # arredonda para 300
    sessao = client.session["lista_orcamento"]
    assert sessao == {f"{catalogo['got'].pk}:{catalogo['v2'].pk}": 400}


def test_quantidade_abaixo_do_minimo_vai_ao_minimo(client, catalogo):
    adicionar(client, catalogo["tubo"], qtd=10)
    assert list(client.session["lista_orcamento"].values()) == [50]


def test_variacao_obrigatoria_e_do_mesmo_produto(client, catalogo):
    resp = adicionar(client, catalogo["got"])
    assert "Escolha uma opção" in json.loads(resp["HX-Trigger"])["isf:toast"]["mensagem"]
    outra = VariantFactory(sku="X-1")
    resp = adicionar(client, catalogo["got"], outra)
    assert "inválida" in json.loads(resp["HX-Trigger"])["isf:toast"]["mensagem"]
    assert "lista_orcamento" not in client.session or not client.session["lista_orcamento"]


def test_sem_js_usa_radios_e_redireciona(client, catalogo):
    resp = adicionar(client, catalogo["got"], htmx=False, attr_vazao="4")
    assert resp.status_code == 302 and resp["Location"] == "/orcamento/"
    html = client.get("/orcamento/").content.decode()
    assert "G1-4" in html and "Vazão: 4 L/h" in html


def test_produto_inativo_sai_da_lista(client, catalogo):
    adicionar(client, catalogo["tubo"])
    catalogo["tubo"].active = False
    catalogo["tubo"].save()
    html = client.get("/orcamento/").content.decode()
    assert "saíram do catálogo" in html and "Sua lista está vazia" in html


def test_atualizar_e_remover_item(client, catalogo):
    adicionar(client, catalogo["tubo"])
    chave = next(iter(client.session["lista_orcamento"]))
    resp = client.post(reverse("orcamentos:item", args=[chave]), {"quantidade": 120}, HTTP_HX_REQUEST="true")
    assert 'value="100"' in resp.content.decode()  # 120 → múltiplo de 50 a partir de 50
    resp = client.post(reverse("orcamentos:item", args=[chave]), {"remover": "1"}, HTTP_HX_REQUEST="true")
    assert "Sua lista está vazia" in resp.content.decode()


def test_mini_lista(client, catalogo):
    assert "vazia" in client.get("/orcamento/mini/").content.decode()
    adicionar(client, catalogo["tubo"])
    assert "Tubo PE" in client.get("/orcamento/mini/").content.decode()


def test_enviar_pedido_grava_envia_emails_e_confirma(client, catalogo, site_config, django_capture_on_commit_callbacks):
    adicionar(client, catalogo["got"], catalogo["v2"], 200)
    adicionar(client, catalogo["tubo"], qtd=100)
    with django_capture_on_commit_callbacks(execute=True):
        resp = client.post("/orcamento/", DADOS)
    quote = Quote.objects.get()
    assert resp.status_code == 302 and resp["Location"] == f"/orcamento/enviado/{quote.pk}/"
    assert quote.code.startswith("ORC-") and quote.status == "new" and quote.source == "site" and quote.consent
    assert quote.phone == "(34) 99999-0000"
    itens = list(quote.items.values_list("product_sku", "variant_sku", "quantity", "unit"))
    assert itens == [("G1", "G1-2", 200, "peças"), ("T1", "", 100, "metros")]
    assert len(mail.outbox) == 2
    equipe, cliente = mail.outbox
    assert equipe.to == ["vendas@example.com", "comercial@example.com"] and quote.code in equipe.subject
    assert equipe.reply_to == ["maria@example.com"] and "G1-2" in equipe.body
    assert cliente.to == ["maria@example.com"]
    quote.refresh_from_db()
    assert quote.email_sent_at and not quote.email_error
    assert client.session["lista_orcamento"] == {}
    pagina = client.get(resp["Location"]).content.decode()
    assert "Pedido de orçamento enviado" in pagina and "https://wa.me/5511999990000?text=" in pagina


def test_confirmacao_so_na_mesma_sessao(client, catalogo, site_config):
    adicionar(client, catalogo["tubo"])
    resp = client.post("/orcamento/", DADOS)
    from django.test import Client

    assert Client().get(resp["Location"]).status_code == 404


def test_erros_de_formulario_nao_gravam(client, catalogo):
    adicionar(client, catalogo["tubo"])
    resp = client.post("/orcamento/", {**DADOS, "phone": "123", "consent": ""})
    html = resp.content.decode()
    assert resp.status_code == 200 and "Informe o telefone com DDD" in html
    assert not Quote.objects.exists()


def test_honeypot_finge_sucesso(client, catalogo):
    adicionar(client, catalogo["tubo"])
    resp = client.post("/orcamento/", {**DADOS, "website": "http://spam"})
    assert resp.status_code == 302 and not Quote.objects.exists()


def test_limite_de_taxa(client, catalogo):
    adicionar(client, catalogo["tubo"])
    for _ in range(5):
        client.post("/orcamento/", {**DADOS, "phone": "1"})
    assert client.post("/orcamento/", DADOS).status_code == 429


def test_falha_de_email_nao_perde_pedido(client, catalogo, site_config, django_capture_on_commit_callbacks):
    adicionar(client, catalogo["tubo"])
    falha = mock.patch("apps.core.email.EmailMultiAlternatives.send", side_effect=OSError("SMTP fora"))
    with falha, django_capture_on_commit_callbacks(execute=True):
        client.post("/orcamento/", DADOS)
    quote = Quote.objects.get()
    assert "SMTP fora" in quote.email_error and quote.email_sent_at is None


def test_sem_destinatarios_registra_aviso(client, catalogo, django_capture_on_commit_callbacks):
    adicionar(client, catalogo["tubo"])
    with django_capture_on_commit_callbacks(execute=True):
        client.post("/orcamento/", DADOS)
    assert "Nenhum destinatário" in Quote.objects.get().email_error
    assert [m.to for m in mail.outbox] == [["maria@example.com"]]


def test_mensagem_whatsapp_com_itens(client, catalogo):
    adicionar(client, catalogo["got"], catalogo["v2"])
    client.post("/orcamento/", DADOS)
    msg = mensagem_whatsapp(Quote.objects.get())
    assert "ORC-" in msg and "Maria Silva — Sítio Boa Água" in msg and "Uberaba/MG" in msg
    assert "• 100 peças — Gotejador (Vazão: 2 L/h) [G1-2]" in msg


def test_orcamento_rapido_pela_lista(client, catalogo, site_config):
    adicionar(client, catalogo["tubo"])
    resp = client.post("/orcamento/whatsapp/")
    quote = Quote.objects.get()
    assert quote.source == "whatsapp" and resp["Location"].startswith("https://wa.me/5511999990000?text=")
    assert not mail.outbox


def test_codigo_sequencial():
    a, b = Quote.objects.create(), Quote.objects.create()
    assert int(b.code[-5:]) == int(a.code[-5:]) + 1


def test_admin_exporta_csv(client, catalogo, django_user_model):
    adicionar(client, catalogo["tubo"])
    client.post("/orcamento/", DADOS)
    admin = django_user_model.objects.create_superuser("adm", "a@e.com", "senha-123-forte")
    client.force_login(admin)
    resp = client.post(reverse("admin:orcamentos_quote_changelist"),
                       {"action": "exportar_csv", "_selected_action": [str(Quote.objects.get().pk)]})  # fmt: skip
    assert resp["Content-Type"].startswith("text/csv") and "Tubo PE" in resp.content.decode()
