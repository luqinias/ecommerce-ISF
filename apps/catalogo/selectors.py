"""Leituras do catálogo (sem efeitos colaterais)."""

from __future__ import annotations

from django.db.models import Prefetch

from apps.catalogo.models import Category, Collection


def menu_categories() -> list[Category]:
    """Categorias raiz ativas com as filhas ativas em `menu_children`."""
    filhas = Prefetch("children", queryset=Category.objects.active().order_by("order", "name"), to_attr="menu_children")
    return list(Category.objects.active().roots().prefetch_related(filhas).order_by("order", "name"))


def menu_collections() -> list[Collection]:
    return list(Collection.objects.visible().order_by("order", "name"))
