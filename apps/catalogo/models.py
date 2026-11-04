"""Catálogo: categorias, coleções, produtos, variações e imagens.

Nenhuma regra conhece uma categoria ou atributo específico (princípio III): os atributos
técnicos são definidos como dados em `Category.attribute_schema`.
"""

from __future__ import annotations

import contextlib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.catalogo import schema as schema_attrs
from apps.catalogo.choices import (
    CATEGORY_ICONS,
    SALE_UNIT_ABBR,
    SALE_UNIT_PLURAL,
    AttributeType,
    CollectionColor,
    ImageKind,
    ImportStatus,
    SaleUnit,
)
from apps.core.models import ActiveModel, CleanSaveModel, TimeStampedModel

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def slug_unico(instancia, origem: str, campo: str = "slug", limite: int = 140) -> str:
    base = slugify(origem)[:limite].strip("-") or "item"
    slug, n = base, 2
    modelo = type(instancia)
    while modelo.objects.filter(**{campo: slug}).exclude(pk=instancia.pk).exists():
        sufixo = f"-{n}"
        slug = f"{base[: limite - len(sufixo)]}{sufixo}"
        n += 1
    return slug


class SeoFields(models.Model):
    meta_title = models.CharField(_("título SEO"), max_length=70, blank=True, help_text=_("Vazio = nome."))
    meta_description = models.CharField(_("meta description"), max_length=160, blank=True)

    class Meta:
        abstract = True


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def roots(self):
        return self.filter(parent__isnull=True)


class Category(CleanSaveModel, TimeStampedModel, ActiveModel, SeoFields):
    name = models.CharField(_("nome"), max_length=120)
    slug = models.SlugField(_("endereço (slug)"), max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("categoria pai"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    description = models.TextField(_("descrição"), blank=True)
    seo_text = models.TextField(_("texto de SEO"), blank=True, help_text=_("Aparece no fim da listagem."))
    image = models.ImageField(_("imagem"), upload_to="categorias/", blank=True)
    icon = models.CharField(_("ícone"), max_length=30, choices=CATEGORY_ICONS, default="droplet")
    order = models.PositiveIntegerField(_("ordem"), default=0)
    show_on_home = models.BooleanField(_("vitrine na home"), default=False)
    attribute_schema = models.JSONField(
        _("atributos técnicos"),
        default=list,
        blank=True,
        help_text=_(
            "Lista de atributos. Ex.: "
            '[{"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": true}]. '
            "Tipos: text, number, boolean, choice (com choices). variant=true gera variação."
        ),
    )
    is_demo = models.BooleanField(_("demonstração"), default=False, db_index=True)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        verbose_name = _("categoria")
        verbose_name_plural = _("categorias")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.parent.name} › {self.name}" if self.parent_id else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.parent_id:
            return reverse("catalogo:subcategoria", args=[self.parent.slug, self.slug])
        return reverse("catalogo:categoria", args=[self.slug])

    def clean(self):
        if self.parent_id:
            if self.parent_id == self.pk:
                raise ValidationError({"parent": _("A categoria não pode ser pai dela mesma.")})
            if self.parent.parent_id:
                raise ValidationError({"parent": _("A árvore tem no máximo 2 níveis: escolha uma categoria raiz.")})
            if self.pk and self.children.exists():
                raise ValidationError({"parent": _("Esta categoria já tem subcategorias; ela precisa ser raiz.")})
        try:
            schema_attrs.validar_definicao(self.attribute_schema or [])
        except ValidationError as e:
            raise ValidationError({"attribute_schema": e.messages}) from e

    @property
    def effective_schema(self) -> list[dict]:
        pai = self.parent.attribute_schema if self.parent_id else []
        return schema_attrs.combinar(pai, self.attribute_schema)

    @property
    def variant_attributes(self) -> list[dict]:
        return [a for a in self.effective_schema if a.get("variant")]


class CollectionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def visible(self, hoje=None):
        """Ativas e dentro do período (quando houver período)."""
        hoje = hoje or timezone.localdate()
        return (
            self.active()
            .filter(models.Q(starts_on__isnull=True) | models.Q(starts_on__lte=hoje))
            .filter(models.Q(ends_on__isnull=True) | models.Q(ends_on__gte=hoje))
        )


class Collection(CleanSaveModel, TimeStampedModel, ActiveModel, SeoFields):
    name = models.CharField(_("nome"), max_length=120)
    slug = models.SlugField(_("endereço (slug)"), max_length=140, unique=True, blank=True)
    description = models.TextField(_("descrição"), blank=True)
    seo_text = models.TextField(_("texto de SEO"), blank=True)
    image = models.ImageField(_("imagem"), upload_to="colecoes/", blank=True)
    starts_on = models.DateField(_("início"), null=True, blank=True)
    ends_on = models.DateField(_("fim"), null=True, blank=True)
    order_deadline = models.DateField(
        _("pedidos até"), null=True, blank=True, help_text=_("Prazo mostrado na faixa de prazos da home.")
    )
    deadline_note = models.CharField(_("observação do prazo"), max_length=120, blank=True)
    color = models.CharField(_("cor"), max_length=10, choices=CollectionColor.choices, default=CollectionColor.GREEN)
    featured = models.BooleanField(_("destaque na home"), default=False)
    is_main = models.BooleanField(_("banner principal na home"), default=False)
    order = models.PositiveIntegerField(_("ordem"), default=0)
    is_demo = models.BooleanField(_("demonstração"), default=False, db_index=True)

    objects = CollectionQuerySet.as_manager()

    class Meta:
        verbose_name = _("coleção")
        verbose_name_plural = _("coleções")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(self, self.name)
        super().save(*args, **kwargs)
        if self.is_main:
            Collection.objects.exclude(pk=self.pk).filter(is_main=True).update(is_main=False)

    def get_absolute_url(self):
        return reverse("catalogo:colecao", args=[self.slug])

    def clean(self):
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": _("O fim precisa ser depois do início.")})

    @property
    def period_label(self) -> str:
        if not self.starts_on:
            return ""
        inicio = MESES[self.starts_on.month - 1]
        if not self.ends_on or self.ends_on.month == self.starts_on.month:
            return inicio
        return f"{inicio}–{MESES[self.ends_on.month - 1]}"


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True, primary_category__active=True)

    def with_cards(self):
        """Tudo o que o card de produto precisa, sem N+1."""
        return self.select_related("primary_category", "primary_category__parent").prefetch_related(
            models.Prefetch("images", queryset=ProductImage.objects.order_by("order", "id")),
            models.Prefetch("variants", queryset=Variant.objects.filter(active=True).order_by("order", "id")),
        )


class Product(CleanSaveModel, TimeStampedModel, SeoFields):
    name = models.CharField(_("nome"), max_length=200)
    slug = models.SlugField(_("endereço (slug)"), max_length=220, unique=True, blank=True)
    sku = models.CharField(_("código (SKU)"), max_length=60, unique=True)
    short_description = models.CharField(_("descrição curta"), max_length=300, blank=True)
    description = models.TextField(
        _("descrição completa"), blank=True, help_text=_("Texto simples; linha em branco separa parágrafos.")
    )
    primary_category = models.ForeignKey(
        Category, verbose_name=_("categoria principal"), on_delete=models.PROTECT, related_name="primary_products"
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_("categorias"),
        related_name="products",
        blank=True,
        help_text=_("A categoria principal entra automaticamente."),
    )
    collections = models.ManyToManyField(Collection, verbose_name=_("coleções"), related_name="products", blank=True)
    attributes = models.JSONField(_("atributos técnicos"), default=dict, blank=True)
    min_quantity = models.PositiveIntegerField(_("quantidade mínima"), default=1)
    quantity_step = models.PositiveIntegerField(
        _("múltiplo de venda"), default=1, help_text=_("Ex.: 50 = vende de 50 em 50.")
    )
    sale_unit = models.CharField(_("unidade de venda"), max_length=10, choices=SaleUnit.choices, default=SaleUnit.PIECE)
    active = models.BooleanField(_("ativo"), default=True, db_index=True)
    featured = models.BooleanField(_("destaque"), default=False)
    new_until = models.DateField(_("novidade até"), null=True, blank=True)
    relevance = models.IntegerField(
        _("relevância"), default=0, help_text=_("Maior aparece primeiro em 'Mais relevantes'.")
    )
    is_demo = models.BooleanField(_("demonstração"), default=False, db_index=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("produto")
        verbose_name_plural = _("produtos")
        ordering = ["-relevance", "name"]
        indexes = [models.Index(fields=["active", "-relevance", "name"]), models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(self, self.name, limite=220)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogo:produto", args=[self.slug])

    def clean(self):
        erros = {}
        if self.min_quantity < 1:
            erros["min_quantity"] = _("Mínimo de 1.")
        if self.quantity_step < 1:
            erros["quantity_step"] = _("Mínimo de 1.")
        elif self.min_quantity % self.quantity_step:
            erros["min_quantity"] = _("A quantidade mínima precisa ser múltipla do múltiplo de venda.")
        if self.primary_category_id:
            definicao = self.primary_category.effective_schema
            self.attributes = {k: v for k, v in (self.attributes or {}).items() if v not in (None, "")}
            try:
                schema_attrs.validar_atributos(self.attributes, definicao, variante=False)
            except ValidationError as e:
                erros["attributes"] = [m for msgs in e.message_dict.values() for m in msgs]
        if erros:
            raise ValidationError(erros)

    # ---------- leitura (apresentação simples, sem regra de negócio) ----------
    @cached_property
    def schema(self) -> list[dict]:
        return self.primary_category.effective_schema

    @property
    def variant_attributes(self) -> list[dict]:
        return [a for a in self.schema if a.get("variant")]

    @property
    def spec_rows(self) -> list[tuple[str, str]]:
        """Linhas da ficha técnica na ordem do schema (só atributos de produto preenchidos)."""
        linhas = []
        for attr in self.schema:
            if attr.get("variant"):
                continue
            valor = (self.attributes or {}).get(attr["key"])
            if valor not in (None, ""):
                linhas.append((attr["label"], schema_attrs.formatar_valor(valor, attr)))
        return linhas

    @property
    def is_new(self) -> bool:
        return bool(self.new_until and self.new_until >= timezone.localdate())

    @property
    def unit_label(self) -> str:
        return SaleUnit(self.sale_unit).label

    @property
    def unit_plural(self) -> str:
        return SALE_UNIT_PLURAL.get(self.sale_unit, self.sale_unit)

    @property
    def unit_abbr(self) -> str:
        return SALE_UNIT_ABBR.get(self.sale_unit, self.sale_unit)

    def ensure_primary_in_categories(self) -> None:
        """A categoria principal sempre faz parte das categorias do produto."""
        if self.primary_category_id and not self.categories.filter(pk=self.primary_category_id).exists():
            self.categories.add(self.primary_category_id)

    @property
    def options_summary(self) -> dict | None:
        """Resumo das variações para o card: '3 opções · 2 · 4 · 8 L/h' (usa o prefetch de with_cards)."""
        variacoes = [v for v in self.variants.all() if v.active]
        if not variacoes:
            return None
        atributos = self.variant_attributes
        resumo = {"total": len(variacoes), "valores": [], "unidade": "", "rotulo": "", "mais": False}
        if atributos:
            attr = atributos[0]
            vistos = []
            for v in variacoes:
                valor = (v.attributes or {}).get(attr["key"])
                if valor is not None and valor not in vistos:
                    vistos.append(valor)
            with contextlib.suppress(TypeError):
                vistos.sort()
            resumo["valores"] = [schema_attrs.formatar_valor(x, {**attr, "unit": ""}) for x in vistos[:4]]
            resumo["mais"] = len(vistos) > 4
            resumo["unidade"] = attr.get("unit", "")
            resumo["rotulo"] = attr["label"]
        return resumo

    @property
    def main_image(self):
        imagens = list(self.images.all())
        return imagens[0] if imagens else None


class Variant(CleanSaveModel, models.Model):
    product = models.ForeignKey(Product, verbose_name=_("produto"), on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(_("código (SKU)"), max_length=60, unique=True)
    attributes = models.JSONField(_("atributos da variação"), default=dict, blank=True)
    image = models.ForeignKey(
        "ProductImage", verbose_name=_("imagem"), null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    active = models.BooleanField(_("ativa"), default=True)
    order = models.PositiveIntegerField(_("ordem"), default=0)

    class Meta:
        verbose_name = _("variação")
        verbose_name_plural = _("variações")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} — {self.label}"

    def clean(self):
        if not self.product_id:
            return
        definicao = self.product.schema
        try:
            schema_attrs.validar_atributos(self.attributes, definicao, variante=True)
        except ValidationError as e:
            raise ValidationError({"attributes": [m for msgs in e.message_dict.values() for m in msgs]}) from e
        iguais = Variant.objects.filter(product_id=self.product_id, attributes=self.attributes).exclude(pk=self.pk)
        if iguais.exists():
            raise ValidationError({"attributes": _("Já existe uma variação com esses mesmos valores.")})
        if self.image_id and self.image.product_id != self.product_id:
            raise ValidationError({"image": _("A imagem precisa ser do mesmo produto.")})

    @property
    def label(self) -> str:
        partes = []
        for attr in self.product.variant_attributes:
            valor = (self.attributes or {}).get(attr["key"])
            if valor is not None:
                partes.append(f"{attr['label']}: {schema_attrs.formatar_valor(valor, attr)}")
        return " · ".join(partes) or self.sku


class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("produto"), on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(_("imagem"), upload_to="produtos/%Y/%m/")
    card = models.ImageField(_("miniatura (card)"), upload_to="produtos/miniaturas/", blank=True, editable=False)
    large = models.ImageField(_("versão grande"), upload_to="produtos/miniaturas/", blank=True, editable=False)
    alt = models.CharField(_("texto alternativo"), max_length=200, blank=True, help_text=_("Vazio = nome do produto."))
    kind = models.CharField(_("tipo"), max_length=12, choices=ImageKind.choices, default=ImageKind.PRODUCT)
    order = models.PositiveIntegerField(_("ordem"), default=0)
    source = models.CharField(_("origem"), max_length=500, blank=True, editable=False)

    class Meta:
        verbose_name = _("imagem do produto")
        verbose_name_plural = _("imagens do produto")
        ordering = ["order", "id"]

    def __str__(self):
        return self.alt_text

    def save(self, *args, **kwargs):
        from apps.catalogo.services.imagens import gerar_miniaturas

        mudou = True
        if self.pk:
            anterior = ProductImage.objects.filter(pk=self.pk).values_list("image", flat=True).first()
            mudou = anterior != self.image.name
        if mudou or not self.card:
            gerar_miniaturas(self)
        super().save(*args, **kwargs)

    @property
    def alt_text(self) -> str:
        return self.alt or self.product.name

    @property
    def card_url(self) -> str:
        return (self.card or self.image).url

    @property
    def large_url(self) -> str:
        return (self.large or self.image).url


class CatalogImport(models.Model):
    file = models.FileField(_("planilha (CSV ou XLSX)"), upload_to="importacoes/")
    dry_run = models.BooleanField(_("simulação (não grava nada)"), default=True)
    status = models.CharField(_("situação"), max_length=10, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    summary = models.CharField(_("resumo"), max_length=300, blank=True)
    report = models.JSONField(_("relatório"), default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("enviado por"), null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(_("enviado em"), auto_now_add=True)

    class Meta:
        verbose_name = _("importação de catálogo")
        verbose_name_plural = _("importações de catálogo")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file.name} — {self.get_status_display()}"


__all__ = ["AttributeType", "CatalogImport", "Category", "Collection", "Product", "ProductImage", "Variant"]
