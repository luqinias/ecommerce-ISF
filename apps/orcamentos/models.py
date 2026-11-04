"""Pedidos de orçamento (leads). Itens guardam cópia de nome e SKU: o catálogo pode mudar depois."""

from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedModel
from apps.orcamentos.choices import UFS, QuoteSource, QuoteStatus


class Quote(UUIDTimeStampedModel):
    code = models.CharField(_("código"), max_length=20, unique=True, editable=False)
    name = models.CharField(_("nome"), max_length=120, blank=True)
    company = models.CharField(_("empresa / propriedade"), max_length=120, blank=True)
    email = models.EmailField(_("e-mail"), blank=True)
    phone = models.CharField(_("telefone / WhatsApp"), max_length=20, blank=True)
    city = models.CharField(_("cidade"), max_length=80, blank=True)
    state = models.CharField(_("UF"), max_length=2, choices=UFS, blank=True)
    message = models.TextField(_("mensagem"), blank=True)
    source = models.CharField(_("origem"), max_length=10, choices=QuoteSource.choices, default=QuoteSource.SITE)
    status = models.CharField(
        _("status"), max_length=12, choices=QuoteStatus.choices, default=QuoteStatus.NEW, db_index=True
    )
    consent = models.BooleanField(_("consentimento"), default=False)
    consent_text = models.CharField(_("texto do consentimento"), max_length=300, blank=True)
    internal_notes = models.TextField(_("anotações internas"), blank=True)
    email_sent_at = models.DateTimeField(_("e-mails enviados em"), null=True, blank=True)
    email_error = models.TextField(_("erro de e-mail"), blank=True)

    class Meta:
        verbose_name = _("orçamento")
        verbose_name_plural = _("orçamentos")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"{self.code} — {self.name or self.get_source_display()}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.proximo_codigo()
        super().save(*args, **kwargs)

    @classmethod
    def proximo_codigo(cls) -> str:
        ano = timezone.localdate().year
        prefixo = f"ORC-{ano}-"
        with transaction.atomic():
            ultimo = (
                cls.objects.filter(code__startswith=prefixo).order_by("-code").values_list("code", flat=True).first()
            )
        numero = int(ultimo.rsplit("-", 1)[1]) + 1 if ultimo else 1
        return f"{prefixo}{numero:05d}"

    @property
    def total_items(self) -> int:
        return self.items.count()


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, verbose_name=_("orçamento"), on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalogo.Product", verbose_name=_("produto"), null=True, blank=True, on_delete=models.SET_NULL
    )
    variant = models.ForeignKey(
        "catalogo.Variant", verbose_name=_("variação"), null=True, blank=True, on_delete=models.SET_NULL
    )
    product_name = models.CharField(_("produto (cópia)"), max_length=200)
    product_sku = models.CharField(_("SKU do produto"), max_length=60)
    variant_label = models.CharField(_("variação (cópia)"), max_length=200, blank=True)
    variant_sku = models.CharField(_("SKU da variação"), max_length=60, blank=True)
    quantity = models.PositiveIntegerField(_("quantidade"))
    unit = models.CharField(_("unidade"), max_length=20)

    class Meta:
        verbose_name = _("item do orçamento")
        verbose_name_plural = _("itens do orçamento")
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} {self.unit} × {self.product_name}"

    @property
    def sku(self) -> str:
        return self.variant_sku or self.product_sku
