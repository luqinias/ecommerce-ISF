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
