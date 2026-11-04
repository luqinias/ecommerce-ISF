"""Contexto global: configuração do site, menus e contador da lista de orçamento."""

from django.utils.functional import SimpleLazyObject

from apps.core.models import SiteConfiguration


def _menus():
    """Menus vêm do catálogo; até ele existir, listas vazias (FR-010)."""
    try:
        from apps.catalogo import selectors
    except ImportError:
        return [], []
    return selectors.menu_categories(), selectors.menu_collections()


def _total_lista(request) -> int:
    try:
        from apps.orcamentos.lista import ListaOrcamento
    except ImportError:
        return 0
    return len(ListaOrcamento(request))


def site(request):
    menus = SimpleLazyObject(_menus)
    return {
        "site": SimpleLazyObject(SiteConfiguration.load),
        "menu_categorias": SimpleLazyObject(lambda: menus[0]),
        "menu_colecoes": SimpleLazyObject(lambda: menus[1]),
        "lista_orcamento_total": SimpleLazyObject(lambda: _total_lista(request)),
        "consentimento_cookies": request.COOKIES.get("isf_consent", ""),
    }
