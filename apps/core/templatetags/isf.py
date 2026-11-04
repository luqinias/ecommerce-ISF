"""Template tags e filtros do site (carregados como builtins)."""

from urllib.parse import quote

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.core.icones import ICONES
from apps.core.models import DEFINIR, SiteConfiguration
from apps.core.whatsapp import whatsapp_link

register = template.Library()


@register.simple_tag
def icone(nome: str, tamanho: int = 20, classe: str = ""):
    """SVG inline decorativo (aria-hidden). Ícone desconhecido vira um círculo neutro."""
    corpo = ICONES.get(nome, '<circle cx="12" cy="12" r="9"/>')
    return format_html(
        '<svg class="icone {}" width="{}" height="{}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{}</svg>',
        classe,
        tamanho,
        tamanho,
        mark_safe(corpo),
    )


@register.simple_tag(takes_context=True)
def whatsapp_url(context, mensagem: str = "", **valores) -> str:
    """Link wa.me com a mensagem; sem número configurado, leva à página de contato."""
    site = context.get("site") or SiteConfiguration.load()
    return whatsapp_link(site, mensagem or site.whatsapp_default_message, **valores)


@register.filter
def definir(valor):
    """Mostra [DEFINIR] quando o valor está vazio."""
    return valor if valor not in (None, "") else DEFINIR


@register.filter
def e_definir(valor) -> bool:
    return not valor or str(valor).strip().startswith(DEFINIR)


@register.filter
def urlencode_text(valor) -> str:
    return quote(str(valor))


@register.simple_tag(takes_context=True)
def url_absoluta(context, caminho: str = "") -> str:
    """URL absoluta a partir de BASE_URL (canonical, Open Graph, JSON-LD)."""
    from django.conf import settings

    if caminho.startswith(("http://", "https://")):
        return caminho
    request = context.get("request")
    caminho = caminho or (request.path if request else "/")
    return settings.BASE_URL + caminho


@register.filter
def jsonld(valor) -> str:
    """Serializa um dict como JSON seguro para <script type="application/ld+json">."""
    import json

    texto = json.dumps(valor, ensure_ascii=False, separators=(",", ":"))
    texto = texto.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(texto)


@register.simple_tag(takes_context=True)
def cta_href(context, url: str, mensagem: str = "") -> str:
    """Link de CTA editável: 'whatsapp' abre o WhatsApp; o resto é usado como está."""
    if (url or "").strip().lower() == "whatsapp":
        site = context.get("site") or SiteConfiguration.load()
        return whatsapp_link(site, mensagem or site.quick_quote_message)
    return url or "#"


@register.simple_tag
def titulo_destacado(titulo: str, destaque: str = ""):
    """Título com um trecho em destaque (<em>). Se o trecho não está no título, é anexado ao fim."""
    from django.utils.html import escape

    titulo, destaque = escape(titulo or ""), escape(destaque or "")
    if not destaque:
        return mark_safe(titulo)
    if destaque in titulo:
        return mark_safe(titulo.replace(destaque, f"<em>{destaque}</em>", 1))
    return mark_safe(f"{titulo} <em>{destaque}</em>")


@register.filter
def texto_rico(texto: str):
    """Texto simples → parágrafos e listas ('- ' no início da linha). Tudo escapado."""
    from django.utils.html import escape

    blocos = [b.strip() for b in (texto or "").replace("\r\n", "\n").split("\n\n") if b.strip()]
    html = []
    for bloco in blocos:
        paragrafo, lista = [], []
        for linha in bloco.split("\n"):
            if linha.strip().startswith("## "):
                if paragrafo:
                    html.append("<p>" + "<br>".join(paragrafo) + "</p>")
                    paragrafo = []
                if lista:
                    html.append("<ul>" + "".join(lista) + "</ul>")
                    lista = []
                html.append(f"<h2>{escape(linha.strip()[3:])}</h2>")
            elif linha.strip().startswith("- "):
                if paragrafo:
                    html.append("<p>" + "<br>".join(paragrafo) + "</p>")
                    paragrafo = []
                lista.append(f"<li>{escape(linha.strip()[2:])}</li>")
            else:
                if lista:
                    html.append("<ul>" + "".join(lista) + "</ul>")
                    lista = []
                paragrafo.append(escape(linha))
        if paragrafo:
            html.append("<p>" + "<br>".join(paragrafo) + "</p>")
        if lista:
            html.append("<ul>" + "".join(lista) + "</ul>")
    return mark_safe("".join(html))
