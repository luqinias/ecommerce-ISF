"""Montagem da home e das páginas a partir do conteúdo editável + catálogo."""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Count, Q
from django.utils import timezone

from apps.catalogo import selectors as catalogo
from apps.catalogo.models import Category, Collection, Product, ProductImage
from apps.conteudo.models import Banner, FAQItem, Highlight, HowItWorksStep, PortfolioItem, SectionText, Testimonial

# Textos genéricos usados enquanto a equipe não edita a seção (P18). Nada de dado real inventado.
PADROES = {
    "vitrine": {"kicker": "Catálogo", "title": "Linhas de produto em destaque", "cta_label": "Abrir o catálogo →", "cta_url": "/produtos/"},
    "datas": {"kicker": "Coleções", "title": "Campanhas para planejar a safra com antecedência.", "cta_label": "Ver todos os produtos →", "cta_url": "/produtos/"},
    "portfolio": {"kicker": "Projetos", "title": "Sistemas que já estão irrigando no campo.", "text": "Alguns projetos e instalações acompanhados pela equipe. [DEFINIR] fotos e dados reais dos clientes.", "cta_label": "Fale com a equipe sobre o seu projeto →", "cta_url": "whatsapp"},
    "categorias": {"kicker": "Mais categorias", "title": "Outras linhas do catálogo", "text": "Além das linhas em destaque, o catálogo tem outras categorias. Estas são as que têm mais produtos.", "cta_label": "Ver todos os produtos →", "cta_url": "/produtos/"},
    "como_funciona": {"kicker": "Como funciona", "title": "Do pedido à instalação, em quatro etapas."},
    "faixa": {"title": "Programe a compra antes do plantio.", "highlight": "Evite a alta temporada.", "text": "[DEFINIR] Prazos de pedido por safra e região.", "cta_label": "Combinar o prazo pelo WhatsApp", "cta_url": "whatsapp"},
    "por_que": {"kicker": "Por que a ISF?", "title": "[DEFINIR] Diferenciais da Irrigação Sem Fronteiras.", "text": "[DEFINIR] Texto institucional sobre a empresa, área de atuação e atendimento.", "cta_label": "Falar com a equipe no WhatsApp", "cta_url": "whatsapp"},
    "depoimentos": {"kicker": "Depoimentos", "title": "Quem já irriga com a gente", "highlight": "recomenda"},
    "faq": {"kicker": "Dúvidas frequentes", "title": "Dúvidas comuns sobre catálogo e orçamento", "text": "Se a sua dúvida não estiver aqui, a equipe responde pelo WhatsApp ou e-mail."},
    "novidades": {"kicker": "Novidades", "title": "Lançamentos", "highlight": "do catálogo", "text": "Os produtos mais recentes aparecem primeiro. Veja o que entrou e monte a sua lista de orçamento."},
    "novidades_cta": {"kicker": "Não encontrou?", "title": "Procurando um produto específico?", "text": "Conte o que você precisa irrigar e a equipe indica as opções.", "cta_label": "Pedir pelo WhatsApp", "cta_url": "whatsapp"},
    "contato": {"kicker": "Contato", "title": "Converse com a equipe", "highlight": "pelo canal que preferir", "text": "Orçamento, dúvida técnica ou acompanhamento de pedido: chame no WhatsApp, mande um e-mail ou preencha o formulário."},
}  # fmt: skip


@dataclass
class Texto:
    kicker: str = ""
    title: str = ""
    highlight: str = ""
    text: str = ""
    cta_label: str = ""
    cta_url: str = ""


def textos(*chaves: str) -> dict[str, Texto]:
    salvos = {s.key: s for s in SectionText.objects.filter(key__in=chaves)}
    saida = {}
    for chave in chaves:
        base = dict(PADROES.get(chave, {}))
        if chave in salvos:
            s = salvos[chave]
            for campo in ("kicker", "title", "highlight", "text", "cta_label", "cta_url"):
                if getattr(s, campo):
                    base[campo] = getattr(s, campo)
        saida[chave] = Texto(**base)
    return saida


def novidades_base():
    return catalogo.produtos_ativos().order_by("-created_at", "name")


def vitrine(por_bloco: int = 10) -> list[dict]:
    hoje = timezone.localdate()
    blocos = []
    novos = list(
        catalogo.produtos_ativos().filter(new_until__gte=hoje).order_by("-created_at").with_cards()[:por_bloco]
    )
    if len(novos) < 4:
        novos = list(novidades_base().with_cards()[:por_bloco])
    if novos:
        blocos.append(
            {
                "id": "novidades",
                "titulo": "Recém-chegados",
                "texto": "Novidades recentes do catálogo.",
                "url": "/novidades/",
                "produtos": novos,
            }
        )
    for cat in Category.objects.active().filter(show_on_home=True).select_related("parent").order_by("order", "name"):
        produtos = list(catalogo.ordenar(catalogo.produtos_da_categoria(cat), "relevantes").with_cards()[:por_bloco])
        if produtos:
            blocos.append(
                {
                    "id": cat.slug,
                    "titulo": cat.name,
                    "texto": cat.description,
                    "url": cat.get_absolute_url(),
                    "produtos": produtos,
                }
            )
    return blocos


def colecoes_home():
    base = Collection.objects.visible().annotate(
        total=Count("products", filter=Q(products__active=True), distinct=True)
    )
    principal = base.filter(is_main=True).first()
    destaques = list(base.filter(featured=True).exclude(pk=principal.pk if principal else None).order_by("order")[:3])
    return destaques, principal


def tiles_categorias(limite: int = 12) -> list[Category]:
    cats = list(
        Category.objects.active()
        .select_related("parent")
        .annotate(total=Count("products", filter=Q(products__active=True), distinct=True))
        .filter(total__gt=0)
        .order_by("-total", "order", "name")[:limite]
    )
    for cat in cats:
        if not cat.image:
            img = (
                ProductImage.objects.filter(product__categories=cat, product__active=True, kind="product")
                .order_by("product__relevance", "order")
                .last()
            )
            cat.tile_url = img.card_url if img else ""
        else:
            cat.tile_url = cat.image.url
    return cats


def prazos(limite: int = 3) -> list[Collection]:
    hoje = timezone.localdate()
    return list(Collection.objects.visible().filter(order_deadline__gte=hoje).order_by("order_deadline")[:limite])


def home() -> dict:
    destaques, principal = colecoes_home()
    return {
        "banner": Banner.objects.filter(active=True).order_by("order", "id").first(),
        "textos": textos(*[k for k in PADROES if not k.startswith(("novidades", "contato"))]),
        "provas": list(Highlight.objects.filter(active=True, placement=Highlight.Placement.PROOF)[:3]),
        "por_que": list(Highlight.objects.filter(active=True, placement=Highlight.Placement.WHY)[:4]),
        "blocos": vitrine(),
        "colecoes_destaque": destaques,
        "colecao_principal": principal,
        "selo_colecoes": list(Collection.objects.visible().order_by("order")[:3]),
        "portfolio": list(PortfolioItem.objects.filter(active=True)),
        "categorias": tiles_categorias(),
        "passos": list(HowItWorksStep.objects.filter(active=True)[:4]),
        "prazos": prazos(),
        "depoimentos": list(Testimonial.objects.filter(active=True, authorized=True)[:3]),
        "faq": list(FAQItem.objects.filter(active=True, placement=FAQItem.Placement.HOME)),
        "total_produtos": Product.objects.active().count(),
    }
