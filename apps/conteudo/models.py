"""Conteúdo editável da home e das páginas institucionais."""

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.catalogo.choices import CATEGORY_ICONS
from apps.core.models import ActiveModel, CleanSaveModel, TimeStampedModel

ICONES = [
    *CATEGORY_ICONS,
    ("check", _("check")),
    ("users", _("pessoas")),
    ("shield", _("escudo")),
    ("clock", _("relógio")),
    ("map-pin", _("local")),
    ("star", _("estrela")),
]


class Ordered(models.Model):
    order = models.PositiveIntegerField(_("ordem"), default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class SectionText(models.Model):
    class Key(models.TextChoices):
        VITRINE = "vitrine", _("Home · vitrine por categoria")
        DATAS = "datas", _("Home · próximas coleções")
        PORTFOLIO = "portfolio", _("Home · portfólio")
        CATEGORIAS = "categorias", _("Home · categorias")
        COMO = "como_funciona", _("Home · como funciona")
        FAIXA = "faixa", _("Home · faixa de prazos")
        POR_QUE = "por_que", _("Home · por que nós")
        DEPOIMENTOS = "depoimentos", _("Home · depoimentos")
        FAQ = "faq", _("Home · perguntas frequentes")
        NOVIDADES = "novidades", _("Novidades · topo")
        NOVIDADES_CTA = "novidades_cta", _("Novidades · card de ajuda")
        CONTATO = "contato", _("Contato · topo")

    key = models.CharField(_("seção"), max_length=20, choices=Key.choices, unique=True)
    kicker = models.CharField(_("chamada (kicker)"), max_length=60, blank=True)
    title = models.CharField(_("título"), max_length=160, blank=True)
    highlight = models.CharField(_("trecho em destaque no título"), max_length=60, blank=True)
    text = models.TextField(_("texto"), blank=True)
    cta_label = models.CharField(_("botão: texto"), max_length=60, blank=True)
    cta_url = models.CharField(
        _("botão: link"), max_length=300, blank=True, help_text=_("Use 'whatsapp' para abrir o WhatsApp.")
    )

    class Meta:
        verbose_name = _("texto de seção")
        verbose_name_plural = _("textos de seção")

    def __str__(self):
        return self.get_key_display()


class Banner(CleanSaveModel, TimeStampedModel, ActiveModel, Ordered):
    badge_label = models.CharField(_("selo (ex.: Temporada)"), max_length=40, blank=True)
    title = models.CharField(_("título"), max_length=120)
    highlight = models.CharField(_("trecho em destaque"), max_length=60, blank=True)
    subtitle = models.TextField(_("subtítulo"), blank=True)
    cta_label = models.CharField(_("botão principal"), max_length=60, default="Pedir orçamento")
    cta_url = models.CharField(_("link do botão principal"), max_length=300, default="whatsapp")
    cta2_label = models.CharField(_("botão secundário"), max_length=60, default="Ver produtos ↓", blank=True)
    cta2_url = models.CharField(_("link do botão secundário"), max_length=300, default="#vitrine", blank=True)
    image_main = models.ImageField(_("imagem principal (vertical)"), upload_to="home/", blank=True)
    caption_main = models.CharField(_("legenda principal"), max_length=60, blank=True)
    image_2 = models.ImageField(_("imagem 2"), upload_to="home/", blank=True)
    caption_2 = models.CharField(_("legenda 2"), max_length=60, blank=True)
    image_3 = models.ImageField(_("imagem 3"), upload_to="home/", blank=True)
    caption_3 = models.CharField(_("legenda 3"), max_length=60, blank=True)
    is_demo = models.BooleanField(_("demonstração"), default=False)

    class Meta(Ordered.Meta):
        verbose_name = _("banner da home")
        verbose_name_plural = _("banners da home")

    def __str__(self):
        return self.title


class Highlight(ActiveModel, Ordered):
    class Placement(models.TextChoices):
        PROOF = "prova", _("Hero · cards de prova")
        WHY = "por_que", _("Por que nós")

    placement = models.CharField(_("onde aparece"), max_length=10, choices=Placement.choices)
    icon = models.CharField(_("ícone"), max_length=20, choices=ICONES, default="check")
    title = models.CharField(_("título"), max_length=80)
    text = models.CharField(_("texto"), max_length=240, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = _("diferencial")
        verbose_name_plural = _("diferenciais")

    def __str__(self):
        return self.title


class HowItWorksStep(ActiveModel, Ordered):
    title = models.CharField(_("título"), max_length=80)
    text = models.CharField(_("texto"), max_length=240)

    class Meta(Ordered.Meta):
        verbose_name = _("passo do 'como funciona'")
        verbose_name_plural = _("passos do 'como funciona'")

    def __str__(self):
        return self.title


class PortfolioItem(ActiveModel, Ordered):
    title = models.CharField(_("título"), max_length=100)
    subtitle = models.CharField(_("cultura · cidade/UF"), max_length=120, blank=True)
    system = models.CharField(_("sistema"), max_length=80, blank=True)
    image = models.ImageField(_("foto"), upload_to="portfolio/")
    tall = models.BooleanField(_("foto alta (ocupa 2 linhas)"), default=False)
    featured = models.BooleanField(_("selo de destaque"), default=False)
    is_demo = models.BooleanField(_("demonstração"), default=False)

    class Meta(Ordered.Meta):
        verbose_name = _("projeto do portfólio")
        verbose_name_plural = _("portfólio de projetos")

    def __str__(self):
        return self.title


class Testimonial(ActiveModel, Ordered):
    author = models.CharField(_("autor"), max_length=80)
    role = models.CharField(_("cargo / propriedade"), max_length=120, blank=True)
    text = models.TextField(_("depoimento"))
    rating = models.PositiveSmallIntegerField(_("estrelas"), default=5, choices=[(i, i) for i in range(1, 6)])
    authorized = models.BooleanField(_("uso autorizado pelo cliente"), default=False)

    class Meta(Ordered.Meta):
        verbose_name = _("depoimento")
        verbose_name_plural = _("depoimentos")

    def __str__(self):
        return self.author


class FAQItem(ActiveModel, Ordered):
    class Placement(models.TextChoices):
        HOME = "home", _("Home")
        CONTACT = "contato", _("Contato")

    placement = models.CharField(_("onde aparece"), max_length=10, choices=Placement.choices, default=Placement.HOME)
    question = models.CharField(_("pergunta"), max_length=200)
    answer = models.TextField(_("resposta"))

    class Meta(Ordered.Meta):
        verbose_name = _("pergunta frequente")
        verbose_name_plural = _("perguntas frequentes")

    def __str__(self):
        return self.question


class Page(TimeStampedModel, ActiveModel):
    class Kind(models.TextChoices):
        ABOUT = "sobre", _("Sobre")
        LEGAL = "legal", _("Legal (termos, privacidade)")
        FREE = "livre", _("Livre")

    slug = models.SlugField(_("endereço"), max_length=80, unique=True)
    kind = models.CharField(_("tipo"), max_length=10, choices=Kind.choices, default=Kind.FREE)
    kicker = models.CharField(_("chamada"), max_length=60, blank=True)
    title = models.CharField(_("título"), max_length=160)
    highlight = models.CharField(_("trecho em destaque"), max_length=60, blank=True)
    lead = models.TextField(_("introdução"), blank=True)
    updated_label = models.CharField(
        _("texto de atualização"), max_length=60, blank=True, help_text=_("Ex.: Atualizado em 4 de novembro de 2026")
    )
    meta_description = models.CharField(_("meta description"), max_length=160, blank=True)
    is_demo = models.BooleanField(_("demonstração"), default=False)

    class Meta:
        verbose_name = _("página")
        verbose_name_plural = _("páginas")
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        fixas = {
            "sobre": "conteudo:sobre",
            "termos-de-uso": "conteudo:termos",
            "politica-de-privacidade": "conteudo:privacidade",
        }
        if self.slug in fixas:
            return reverse(fixas[self.slug])
        return reverse("conteudo:pagina", args=[self.slug])


class PageSection(Ordered):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections", verbose_name=_("página"))
    title = models.CharField(_("título"), max_length=160)
    anchor = models.SlugField(_("âncora"), max_length=60, blank=True, help_text=_("Ex.: cookies (vira #cookies)."))
    body = models.TextField(
        _("texto"), help_text=_("Linha em branco separa parágrafos; linhas começando com '- ' viram lista.")
    )

    class Meta(Ordered.Meta):
        verbose_name = _("seção")
        verbose_name_plural = _("seções")

    def __str__(self):
        return self.title
