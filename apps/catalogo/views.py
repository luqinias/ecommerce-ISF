"""Views públicas do catálogo: listagens (catálogo, categoria, subcategoria, coleção, busca) e produto."""

from __future__ import annotations

from dataclasses import dataclass, field

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.catalogo import selectors
from apps.catalogo.models import Category, Collection, Product


@dataclass
class Listagem:
    """O que muda entre as listagens; o layout é o mesmo (componentes L01–L08)."""

    titulo: str
    base: QuerySet[Product]
    url_nome: str
    url_args: list = field(default_factory=list)
    kicker: str = ""
    descricao: str = ""
    breadcrumb: list[tuple[str, str | None]] = field(default_factory=list)
    chips_excluir: list[int] = field(default_factory=list)
    texto_seo: str = ""
    titulo_seo: str = ""
    meta_descricao: str = ""
    noindex: bool = False
    objeto: object = None
    tipo: str = "catalogo"
    extra: dict = field(default_factory=dict)


def _url(nome: str, args: list, pagina: int) -> str:
    if pagina <= 1:
        return reverse(f"catalogo:{nome}", args=args)
    return reverse(f"catalogo:{nome}_pagina", args=[*args, pagina])


def _paginas_visiveis(atual: int, total: int) -> list[int | None]:
    """1 … 4 5 [6] 7 8 … 20 (None = reticências)."""
    if total <= 7:
        return list(range(1, total + 1))
    paginas = {1, total, atual - 1, atual, atual + 1}
    if atual <= 3:
        paginas |= {2, 3, 4}
    if atual >= total - 2:
        paginas |= {total - 3, total - 2, total - 1}
    saida, anterior = [], 0
    for p in sorted(x for x in paginas if 1 <= x <= total):
        if p - anterior > 1:
            saida.append(None)
        saida.append(p)
        anterior = p
    return saida


def _render_listagem(request, cfg: Listagem, pagina: int | None):
    if pagina == 1:
        destino = _url(cfg.url_nome, cfg.url_args, 1)
        if request.GET:
            destino += "?" + request.GET.urlencode()
        return HttpResponsePermanentRedirect(destino)
    pagina = pagina or 1
    ordem = selectors.normalizar_ordem(request.GET.get("ordem"))
    qs, tipo_ativo = selectors.filtrar_por_tipo(cfg.base, request.GET.get("tipo"))
    total_base = cfg.base.count()
    qs = selectors.ordenar(qs, ordem).with_cards()
    paginador = Paginator(qs, settings.CATALOG_PAGE_SIZE)
    try:
        pagina_obj = paginador.page(pagina)
    except (EmptyPage, PageNotAnInteger) as erro:
        if pagina == 1:
            pagina_obj = paginador.page(1)  # listagem vazia
        else:
            raise Http404 from erro

    # query string preservada nos links (sem a página)
    params = request.GET.copy()
    params.pop("pagina", None)
    query = params.urlencode()
    sufixo = f"?{query}" if query else ""
    paginas = [
        {"numero": n, "url": _url(cfg.url_nome, cfg.url_args, n) + sufixo} if n else None
        for n in _paginas_visiveis(pagina_obj.number, paginador.num_pages)
    ]
    params_chip = request.GET.copy()
    params_chip.pop("tipo", None)
    base_url = _url(cfg.url_nome, cfg.url_args, 1)

    contexto = {
        "cfg": cfg,
        "pagina": pagina_obj,
        "produtos": list(pagina_obj.object_list),
        "paginas": paginas,
        "pagina_anterior": paginas
        and pagina_obj.has_previous()
        and _url(cfg.url_nome, cfg.url_args, pagina_obj.number - 1) + sufixo,
        "pagina_seguinte": pagina_obj.has_next() and _url(cfg.url_nome, cfg.url_args, pagina_obj.number + 1) + sufixo,
        "total": paginador.count,
        "total_base": total_base,
        "ordem": ordem,
        "ordens": [(chave, rotulo) for chave, (rotulo, _) in selectors.ORDENS.items()],
        "chips": selectors.chips(cfg.base, excluir=cfg.chips_excluir),
        "tipo_ativo": tipo_ativo,
        "url_base": base_url,
        "query_chip": params_chip.urlencode(),
        "canonical": _url(cfg.url_nome, cfg.url_args, pagina_obj.number),
        "noindex": cfg.noindex or bool(request.GET.get("tipo") or request.GET.get("ordem")),
        **cfg.extra,
    }
    if cfg.tipo == "catalogo":
        contexto["todas_categorias"] = selectors.categorias_com_total()
    return render(request, "catalogo/listagem.html", contexto)


@require_GET
def lista(request, pagina: int | None = None):
    cfg = Listagem(
        titulo="Todos os produtos",
        kicker="Catálogo",
        descricao="Todo o catálogo em um só lugar. Escolha o produto, veja as opções disponíveis e monte a sua lista de orçamento.",
        base=selectors.produtos_ativos(),
        url_nome="lista",
        breadcrumb=[("Início", "/"), ("Todos os produtos", None)],
        meta_descricao="Catálogo completo de produtos de irrigação. Monte a sua lista e peça um orçamento sem compromisso.",
        tipo="catalogo",
    )
    return _render_listagem(request, cfg, pagina)


def _cfg_categoria(categoria: Category) -> Listagem:
    trilha = [("Início", "/"), ("Produtos", reverse("catalogo:lista"))]
    if categoria.parent_id:
        trilha.append((categoria.parent.name, categoria.parent.get_absolute_url()))
        args = [categoria.parent.slug, categoria.slug]
        nome = "subcategoria"
    else:
        args = [categoria.slug]
        nome = "categoria"
    trilha.append((categoria.name, None))
    excluir = [categoria.pk, *categoria.children.values_list("pk", flat=True)]
    if categoria.parent_id:
        excluir.append(categoria.parent_id)
    return Listagem(
        titulo=categoria.name,
        kicker=categoria.parent.name if categoria.parent_id else "Categoria",
        descricao=categoria.description,
        base=selectors.produtos_da_categoria(categoria),
        url_nome=nome,
        url_args=args,
        breadcrumb=trilha,
        chips_excluir=excluir,
        texto_seo=categoria.seo_text,
        titulo_seo=categoria.meta_title,
        meta_descricao=categoria.meta_description or categoria.description[:160],
        objeto=categoria,
        tipo="categoria",
    )


@require_GET
def categoria(request, slug: str, pagina: int | None = None):
    cat = get_object_or_404(Category.objects.active().select_related("parent"), slug=slug)
    if cat.parent_id:  # subcategoria pela URL de raiz → URL canônica
        destino = _url("subcategoria", [cat.parent.slug, cat.slug], pagina or 1)
        return redirect(destino + (f"?{request.GET.urlencode()}" if request.GET else ""), permanent=True)
    return _render_listagem(request, _cfg_categoria(cat), pagina)


@require_GET
def subcategoria(request, pai: str, slug: str, pagina: int | None = None):
    cat = get_object_or_404(
        Category.objects.active().select_related("parent"), slug=slug, parent__slug=pai, parent__active=True
    )
    return _render_listagem(request, _cfg_categoria(cat), pagina)


@require_GET
def colecao(request, slug: str, pagina: int | None = None):
    col = get_object_or_404(Collection.objects.visible(), slug=slug)
    descricao = col.description
    cfg = Listagem(
        titulo=col.name,
        kicker="",  # o template usa o rótulo configurável de coleções
        descricao=descricao,
        base=selectors.produtos_da_colecao(col),
        url_nome="colecao",
        url_args=[col.slug],
        breadcrumb=[("Início", "/"), ("Produtos", reverse("catalogo:lista")), (col.name, None)],
        texto_seo=col.seo_text,
        titulo_seo=col.meta_title,
        meta_descricao=col.meta_description or descricao[:160],
        objeto=col,
        tipo="colecao",
        extra={"colecao": col, "hoje": timezone.localdate()},
    )
    return _render_listagem(request, cfg, pagina)


@require_GET
def busca(request, pagina: int | None = None):
    termo = (request.GET.get("q") or "").strip()[:80]
    cfg = Listagem(
        titulo=f"Resultados para “{termo}”" if termo else "Buscar produtos",
        kicker="Busca",
        descricao="" if termo else "Digite o nome, o código ou o tipo de produto que você procura.",
        base=selectors.buscar(termo),
        url_nome="busca",
        breadcrumb=[("Início", "/"), ("Busca", None)],
        noindex=True,
        tipo="busca",
        extra={"termo": termo},
    )
    return _render_listagem(request, cfg, pagina)


@require_GET
def sugestoes(request):
    termo = (request.GET.get("q") or "").strip()[:80]
    produtos = selectors.sugestoes(termo) if len(termo) >= 2 else []
    return render(request, "catalogo/_sugestoes.html", {"produtos": produtos, "termo": termo})


def produto(request, slug: str):  # implementado na feature 004
    raise Http404


def novidades(request):  # implementado na feature 006
    raise Http404
