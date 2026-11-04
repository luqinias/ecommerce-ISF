"""Leituras do catálogo (sem efeitos colaterais)."""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Count, Prefetch, Q, QuerySet

from apps.catalogo.models import Category, Collection, Product

ORDENS = {
    "relevantes": ("Mais relevantes", ("-featured", "-relevance", "name")),
    "novidades": ("Novidades", ("-created_at", "name")),
    "nome": ("Nome (A–Z)", ("name",)),
}
ORDEM_PADRAO = "relevantes"


@dataclass
class Chip:
    rotulo: str
    slug: str
    total: int


def menu_categories() -> list[Category]:
    """Categorias raiz ativas com as filhas ativas em `menu_children`."""
    filhas = Prefetch("children", queryset=Category.objects.active().order_by("order", "name"), to_attr="menu_children")
    return list(Category.objects.active().roots().prefetch_related(filhas).order_by("order", "name"))


def menu_collections() -> list[Collection]:
    return list(Collection.objects.visible().order_by("order", "name"))


def produtos_ativos() -> QuerySet[Product]:
    return Product.objects.active()


def produtos_da_categoria(categoria: Category) -> QuerySet[Product]:
    """Categoria raiz inclui os produtos das subcategorias ativas."""
    ids = [categoria.pk, *categoria.children.active().values_list("pk", flat=True)]
    return produtos_ativos().filter(categories__in=ids).distinct()


def produtos_da_colecao(colecao: Collection) -> QuerySet[Product]:
    return produtos_ativos().filter(collections=colecao).distinct()


def buscar(termo: str) -> QuerySet[Product]:
    """Busca simples: todos os termos precisam aparecer em algum dos campos."""
    qs = produtos_ativos()
    termos = [t for t in termo.split() if len(t) >= 2][:6]
    if not termos:
        return qs.none()
    for t in termos:
        qs = qs.filter(
            Q(name__icontains=t)
            | Q(sku__icontains=t)
            | Q(short_description__icontains=t)
            | Q(primary_category__name__icontains=t)
            | Q(variants__sku__icontains=t)
        )
    return qs.distinct()


def normalizar_ordem(valor: str | None) -> str:
    return valor if valor in ORDENS else ORDEM_PADRAO


def ordenar(qs: QuerySet[Product], ordem: str) -> QuerySet[Product]:
    return qs.order_by(*ORDENS[normalizar_ordem(ordem)][1])


def filtrar_por_tipo(qs: QuerySet[Product], slug: str | None) -> tuple[QuerySet[Product], Category | None]:
    """Interseção com outra categoria (chip). Slug desconhecido é ignorado."""
    if not slug:
        return qs, None
    categoria = Category.objects.active().filter(slug=slug).first()
    if not categoria:
        return qs, None
    ids = [categoria.pk, *categoria.children.active().values_list("pk", flat=True)]
    return qs.filter(categories__in=ids).distinct(), categoria


def chips(base: QuerySet[Product], *, excluir: list[int] | None = None, limite: int = 12) -> list[Chip]:
    """Categorias presentes nos produtos da listagem, com a contagem da interseção."""
    ids = base.values("pk")
    qs = (
        Category.objects.active()
        .filter(products__in=ids)
        .exclude(pk__in=excluir or [])
        .annotate(total=Count("products", filter=Q(products__in=ids), distinct=True))
        .filter(total__gt=0)
        .order_by("-total", "order", "name")
    )
    return [Chip(c.name, c.slug, c.total) for c in qs[:limite]]


def categorias_com_total() -> list[Category]:
    """Todas as categorias ativas com o total de produtos ativos (grade 'Mostrar todas as categorias')."""
    return list(
        Category.objects.active()
        .select_related("parent")
        .annotate(total=Count("products", filter=Q(products__active=True), distinct=True))
        .filter(total__gt=0)
        .order_by("parent__order", "order", "name")
    )


def sugestoes(termo: str, limite: int = 6) -> list[Product]:
    return list(ordenar(buscar(termo), ORDEM_PADRAO).with_cards()[:limite])


def relacionados(produto: Product, limite: int = 5) -> list[Product]:
    """Mesma categoria principal primeiro; completa com categorias compartilhadas."""
    base = produtos_ativos().exclude(pk=produto.pk)
    mesmos = list(ordenar(base.filter(primary_category=produto.primary_category), ORDEM_PADRAO).with_cards()[:limite])
    if len(mesmos) < limite:
        ids = list(produto.categories.values_list("pk", flat=True))
        extra = ordenar(
            base.filter(categories__in=ids).exclude(pk__in=[p.pk for p in mesmos]).distinct(), ORDEM_PADRAO
        ).with_cards()[: limite - len(mesmos)]
        mesmos.extend(extra)
    return mesmos
