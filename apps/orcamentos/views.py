"""Lista de orçamento e envio do pedido. Tudo funciona sem JS; com HTMX, sem recarregar a página."""

from __future__ import annotations

import json

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.catalogo.models import Product, Variant
from apps.core.ratelimit import limite_de_taxa
from apps.orcamentos import services
from apps.orcamentos.choices import QuoteSource
from apps.orcamentos.forms import QuoteForm
from apps.orcamentos.lista import ErroLista, ListaOrcamento
from apps.orcamentos.models import Quote

SESSAO_ENVIADOS = "orcamentos_enviados"


def _htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


def _contador_oob(request, lista: ListaOrcamento) -> str:
    return render_to_string(
        "partials/contador_lista.html", {"lista_orcamento_total": len(lista), "oob": True}, request=request
    )


def _toast(resp: HttpResponse, mensagem: str, *, link: str = "", rotulo: str = "", tipo: str = "") -> HttpResponse:
    resp["HX-Trigger"] = json.dumps({"isf:toast": {"mensagem": mensagem, "link": link, "rotulo": rotulo, "tipo": tipo}})
    return resp


@require_POST
def adicionar(request):
    lista = ListaOrcamento(request)
    produto = get_object_or_404(Product.objects.active(), pk=request.POST.get("product") or 0)
    variacao = None
    if request.POST.get("variant"):
        variacao = Variant.objects.filter(pk=request.POST["variant"]).first()
    else:
        # sem JS: a variação vem dos rádios attr_<chave>
        escolhidos = {k[5:]: v for k, v in request.POST.items() if k.startswith("attr_")}
        if escolhidos:
            for v in produto.variants.filter(active=True):
                if all(str(v.attributes.get(k)) == val for k, val in escolhidos.items()):
                    variacao = v
                    break
    try:
        item = lista.adicionar(produto, variacao, request.POST.get("quantity"))
    except ErroLista as erro:
        if _htmx(request):
            return _toast(HttpResponse(status=200), str(erro), tipo="erro")
        messages.error(request, str(erro))
        return redirect(produto.get_absolute_url())
    texto = f"{item.produto.name} adicionado à lista ({item.quantidade} {item.unidade})."
    if _htmx(request):
        resp = HttpResponse(_contador_oob(request, lista))
        return _toast(resp, texto, link=reverse("orcamentos:lista"), rotulo="Ver lista →")
    messages.success(request, texto)
    return redirect("orcamentos:lista")


@require_GET
def mini(request):
    lista = ListaOrcamento(request)
    return render(request, "orcamentos/_mini.html", {"itens": lista.itens()})


@require_POST
def item(request, chave: str):
    lista = ListaOrcamento(request)
    if "remover" in request.POST:
        lista.remover(chave)
    else:
        lista.atualizar(chave, request.POST.get("quantidade"))
    if not _htmx(request):
        return redirect("orcamentos:lista")
    html = render_to_string("orcamentos/_itens.html", {"itens": lista.itens()}, request=request)
    return HttpResponse(html + _contador_oob(request, lista))


@require_http_methods(["GET", "POST"])
@limite_de_taxa("orcamento", limite=5, janela=600)
def lista_view(request):
    lista = ListaOrcamento(request)
    itens = lista.itens()
    if lista.removidos:
        messages.warning(request, "Alguns produtos saíram do catálogo e foram retirados da sua lista.")
    form = QuoteForm(request.POST or None)
    if request.method == "POST" and itens:
        if form.e_robo:
            # robô: finge sucesso sem gravar nada
            return redirect("orcamentos:lista")
        if form.is_valid():
            quote = services.criar_orcamento(form.cleaned_data, itens, origem=QuoteSource.SITE)
            lista.limpar()
            enviados = request.session.get(SESSAO_ENVIADOS, [])
            request.session[SESSAO_ENVIADOS] = [*enviados[-9:], str(quote.pk)]
            return redirect("orcamentos:enviado", pk=quote.pk)
    return render(request, "orcamentos/lista.html", {"itens": itens, "form": form})


@require_POST
@limite_de_taxa("orcamento-wpp", limite=10, janela=600)
def whatsapp(request):
    """Orçamento rápido a partir da lista: registra o pedido (origem WhatsApp) e abre a conversa."""
    lista = ListaOrcamento(request)
    itens = lista.itens()
    if not itens:
        return redirect("orcamentos:lista")
    quote = services.criar_orcamento({}, itens, origem=QuoteSource.WHATSAPP)
    link = services.link_whatsapp(quote)
    lista.limpar()
    return redirect(link or reverse("orcamentos:lista"))


@require_GET
def enviado(request, pk):
    if str(pk) not in request.session.get(SESSAO_ENVIADOS, []):
        raise Http404
    quote = get_object_or_404(Quote.objects.prefetch_related("items"), pk=pk)
    abrir = request.session.pop(f"wpp-aberto-{pk}", None) is None
    request.session[f"wpp-aberto-{pk}"] = True
    return render(
        request,
        "orcamentos/enviado.html",
        {
            "quote": quote,
            "itens": list(quote.items.all()),
            "link_whatsapp": services.link_whatsapp(quote),
            "abrir": abrir,
        },
    )
