from django import template
from django.utils.html import format_html

from apps.core.templatetags.isf import jsonld as serializar
from apps.seo import jsonld

register = template.Library()


def _script(dados) -> str:
    return format_html('<script type="application/ld+json">{}</script>', serializar(dados))


@register.simple_tag(takes_context=True)
def jsonld_site(context):
    site = context["site"]
    return _script(jsonld.grafo(jsonld.organizacao(site), jsonld.website(site)))


@register.simple_tag
def jsonld_produto(produto, site, trilha, imagens=None):
    return _script(jsonld.grafo(jsonld.produto(produto, site, imagens), jsonld.breadcrumb(trilha)))


@register.simple_tag
def jsonld_listagem(titulo, url, produtos, trilha):
    return _script(jsonld.grafo(jsonld.colecao_pagina(titulo, url, produtos), jsonld.breadcrumb(trilha)))


@register.simple_tag
def jsonld_faq(perguntas):
    dados = jsonld.faq(perguntas)
    return _script(jsonld.grafo(dados)) if dados else ""


@register.simple_tag
def jsonld_breadcrumb(trilha):
    return _script(jsonld.grafo(jsonld.breadcrumb(trilha)))


@register.simple_tag
def jsonld_post(post, site, trilha):
    return _script(jsonld.grafo(jsonld.artigo(post, site), jsonld.breadcrumb(trilha)))
