from django.contrib import messages
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from apps.catalogo import selectors as catalogo
from apps.conteudo import selectors
from apps.conteudo.forms import ContatoForm
from apps.conteudo.models import FAQItem, Page
from apps.core.ratelimit import limite_de_taxa
from apps.orcamentos import services as orcamentos
from apps.orcamentos.choices import QuoteSource


def home(request):
    return render(request, "conteudo/home.html", selectors.home())


def _pagina(request, slug: str):
    pagina = get_object_or_404(Page.objects.prefetch_related("sections"), slug=slug, active=True)
    template = "conteudo/pagina_legal.html" if pagina.kind == Page.Kind.LEGAL else "conteudo/pagina.html"
    return render(
        request,
        template,
        {"pagina": pagina, "secoes": list(pagina.sections.all()), "trilha": [("Início", "/"), (pagina.title, None)]},
    )


def sobre(request):
    return _pagina(request, "sobre")


def termos(request):
    return _pagina(request, "termos-de-uso")


def privacidade(request):
    return _pagina(request, "politica-de-privacidade")


def pagina(request, slug):
    return _pagina(request, slug)


@require_http_methods(["GET", "POST"])
@limite_de_taxa("contato", limite=5, janela=600)
def contato(request):
    form = ContatoForm(request.POST or None)
    if request.method == "POST":
        if form.e_robo:
            messages.success(request, "Mensagem enviada! Responderemos em breve.")
            return redirect("conteudo:contato")
        if form.is_valid():
            orcamentos.criar_orcamento(form.cleaned_data, [], origem=QuoteSource.CONTACT)
            messages.success(request, "Mensagem enviada! A equipe responde pelo canal que você informou.")
            return redirect("conteudo:contato")
    contexto = {
        "form": form,
        "texto": selectors.textos("contato")["contato"],
        "faq": list(FAQItem.objects.filter(active=True, placement=FAQItem.Placement.CONTACT)),
    }
    return render(request, "conteudo/contato.html", contexto)


POR_PAGINA_NOVIDADES = 20


def novidades(request, pagina: int = 1):
    base = selectors.novidades_base()
    qs, tipo_ativo = catalogo.filtrar_por_tipo(base, request.GET.get("tipo"))
    paginador = Paginator(qs.with_cards(), POR_PAGINA_NOVIDADES)
    try:
        pagina_obj = paginador.page(pagina)
    except EmptyPage as erro:
        raise Http404 from erro
    sufixo = f"?tipo={tipo_ativo.slug}" if tipo_ativo else ""
    proxima = ""
    if pagina_obj.has_next():
        proxima = reverse("conteudo:novidades_pagina", args=[pagina_obj.number + 1]) + sufixo
    t = selectors.textos("novidades", "novidades_cta")
    contexto = {
        "pagina": pagina_obj,
        "produtos": list(pagina_obj.object_list),
        "ultimos": list(base.with_cards()[:3]),
        "chips": catalogo.chips(base, limite=10),
        "tipo_ativo": tipo_ativo,
        "proxima": proxima,
        "total": paginador.count,
        "texto": t["novidades"],
        "cta": t["novidades_cta"],
        "colecoes": list(catalogo.menu_collections()),
        "noindex": bool(request.GET.get("tipo")) or pagina_obj.number > 1,
    }
    return render(request, "conteudo/novidades.html", contexto)
