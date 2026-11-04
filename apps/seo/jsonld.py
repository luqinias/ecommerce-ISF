"""Dados estruturados schema.org montados a partir dos models (funções puras → dict)."""

from __future__ import annotations

from django.conf import settings
from django.urls import reverse

CONTEXTO = "https://schema.org"


def absoluta(caminho: str) -> str:
    if not caminho:
        return ""
    return caminho if caminho.startswith("http") else settings.BASE_URL + caminho


def organizacao(site) -> dict:
    dados = {
        "@type": "Organization",
        "@id": absoluta("/#organizacao"),
        "name": site.site_name,
        "url": absoluta("/"),
        "logo": absoluta("/static/img/favicon.svg"),
    }
    redes = [url for _, url in site.social_links]
    if redes:
        dados["sameAs"] = redes
    contato = {}
    if site.contact_email:
        contato["email"] = site.contact_email
    if site.whatsapp_number:
        contato["telephone"] = "+" + site.whatsapp_number
    if contato:
        dados["contactPoint"] = {
            "@type": "ContactPoint",
            "contactType": "sales",
            "areaServed": "BR",
            "availableLanguage": "pt-BR",
            **contato,
        }
    return dados


def website(site) -> dict:
    return {
        "@type": "WebSite",
        "@id": absoluta("/#site"),
        "name": site.site_name,
        "url": absoluta("/"),
        "inLanguage": "pt-BR",
        "publisher": {"@id": absoluta("/#organizacao")},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": absoluta(reverse("catalogo:busca")) + "?q={search_term_string}",
            },
            "query-input": "required name=search_term_string",
        },
    }


def breadcrumb(trilha) -> dict:
    itens = []
    for posicao, (nome, url) in enumerate(trilha or [], start=1):
        item = {"@type": "ListItem", "position": posicao, "name": str(nome)}
        if url:
            item["item"] = absoluta(url)
        itens.append(item)
    return {"@type": "BreadcrumbList", "itemListElement": itens}


def produto(p, site, imagens=None) -> dict:
    imagens = imagens if imagens is not None else list(p.images.all())
    dados = {
        "@type": "Product",
        "@id": absoluta(p.get_absolute_url()) + "#produto",
        "name": p.name,
        "sku": p.sku,
        "url": absoluta(p.get_absolute_url()),
        "description": p.short_description or p.description[:300] or p.name,
        "category": p.primary_category.name,
        "brand": {"@type": "Brand", "name": site.site_name},
    }
    if imagens:
        dados["image"] = [absoluta(i.large_url) for i in imagens[:6]]
    propriedades = [{"@type": "PropertyValue", "name": rotulo, "value": valor} for rotulo, valor in p.spec_rows]
    variacoes = [v for v in p.variants.all() if v.active]
    if variacoes:
        for attr in p.variant_attributes:
            valores = sorted({str(v.attributes.get(attr["key"])) for v in variacoes if attr["key"] in v.attributes})
            if valores:
                propriedades.append(
                    {
                        "@type": "PropertyValue",
                        "name": attr["label"],
                        "value": ", ".join(valores),
                        "unitText": attr.get("unit", ""),
                    }
                )
    if propriedades:
        dados["additionalProperty"] = propriedades
    # Sem `offers`: o catálogo não tem preço público (seção 1 do prompt).
    return dados


def faq(perguntas) -> dict | None:
    perguntas = list(perguntas)
    if not perguntas:
        return None
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f.question, "acceptedAnswer": {"@type": "Answer", "text": f.answer}}
            for f in perguntas
        ],
    }


def colecao_pagina(titulo: str, url: str, produtos) -> dict:
    return {
        "@type": "CollectionPage",
        "name": titulo,
        "url": absoluta(url),
        "isPartOf": {"@id": absoluta("/#site")},
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "url": absoluta(p.get_absolute_url()), "name": p.name}
                for i, p in enumerate(produtos, start=1)
            ],
        },
    }


def artigo(post, site) -> dict:
    dados = {
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "datePublished": post.published_at.isoformat(),
        "dateModified": post.updated_at.isoformat(),
        "url": absoluta(post.get_absolute_url()),
        "inLanguage": "pt-BR",
        "articleSection": post.category.name,
        "publisher": {"@id": absoluta("/#organizacao")},
        "author": {"@type": "Person", "name": post.author_name}
        if post.author_name
        else {"@id": absoluta("/#organizacao")},
    }
    if post.cover:
        dados["image"] = absoluta(post.cover.url)
    return dados


def grafo(*nos) -> dict:
    return {"@context": CONTEXTO, "@graph": [n for n in nos if n]}
