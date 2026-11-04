"""Models base (portados do padrão interno) e configuração do site."""

import re
import uuid

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

DEFINIR = "[DEFINIR]"


class CleanSaveModel(models.Model):
    """Valida o model inteiro antes de salvar: a regra de domínio fica em `clean()`."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("atualizado em"), auto_now=True)

    class Meta:
        abstract = True


class UUIDTimeStampedModel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """Soft toggle: registros não são apagados, são desativados."""

    active = models.BooleanField(_("ativo"), default=True, db_index=True)

    class Meta:
        abstract = True


class SiteConfiguration(CleanSaveModel):
    """Registro único com dados da empresa, contatos e textos padrão.

    Campos sem valor aparecem como [DEFINIR] no site (ver docs/pendencias-empresa.md).
    """

    CACHE_KEY = "core:site-configuration"

    site_name = models.CharField(_("nome do site"), max_length=120, default="Irrigação Sem Fronteiras")
    short_name = models.CharField(_("nome curto"), max_length=40, default="ISF")
    topbar_left = models.CharField(_("faixa superior: texto à esquerda"), max_length=120, default=DEFINIR, blank=True)
    tagline = models.CharField(_("faixa superior: frase central"), max_length=160, default=DEFINIR, blank=True)
    footer_about = models.TextField(_("rodapé: texto sobre a empresa"), default=DEFINIR, blank=True)

    whatsapp_number = models.CharField(
        _("WhatsApp comercial"),
        max_length=20,
        blank=True,
        help_text=_("Só dígitos, com DDI e DDD. Ex.: 5534999999999. Vazio = botões de WhatsApp levam ao contato."),
    )
    phone_display = models.CharField(_("telefone (como exibir)"), max_length=30, default=DEFINIR, blank=True)
    contact_email = models.EmailField(_("e-mail de contato"), blank=True)
    quote_recipient_emails = models.TextField(
        _("e-mails que recebem os orçamentos"), blank=True, help_text=_("Um por linha.")
    )
    address = models.TextField(_("endereço"), default=DEFINIR, blank=True)
    cnpj = models.CharField(_("CNPJ"), max_length=20, default=DEFINIR, blank=True)
    business_hours = models.TextField(_("horário de atendimento"), default=DEFINIR, blank=True)

    instagram_url = models.URLField(_("Instagram"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    linkedin_url = models.URLField(
        _("LinkedIn"), blank=True, default="https://www.linkedin.com/company/irrigacao-sem-fronteiras/"
    )
    youtube_url = models.URLField(_("YouTube"), blank=True)

    collections_label = models.CharField(
        _("rótulo do menu de coleções"),
        max_length=40,
        default="Coleções",
        help_text=_("Equivalente a 'Datas Especiais' na referência. Ex.: Coleções, Campanhas, Safras."),
    )
    whatsapp_default_message = models.TextField(
        _("mensagem padrão do WhatsApp"),
        default="Olá! Vim pelo site da Irrigação Sem Fronteiras e gostaria de atendimento.",
    )
    quick_quote_message = models.TextField(
        _("mensagem do orçamento rápido"), default="Olá! Gostaria de solicitar um orçamento rápido."
    )
    category_help_message = models.TextField(
        _("mensagem de ajuda na categoria"),
        default="Olá! Estou vendo a categoria {categoria} no site e gostaria de ajuda para escolher.",
        help_text=_("Use {categoria} para o nome da categoria."),
    )
    product_quick_quote_message = models.TextField(
        _("mensagem de orçamento rápido do produto"),
        default="Olá! Gostaria de um orçamento de {produto} ({sku}), quantidade: {quantidade}.",
        help_text=_("Use {produto}, {sku} e {quantidade}."),
    )

    blog_enabled = models.BooleanField(
        _("blog ativo"), default=False, help_text=_("Mostra o blog no menu e no rodapé (feature opcional).")
    )

    gtm_id = models.CharField(_("Google Tag Manager ID"), max_length=30, blank=True, help_text="GTM-XXXXXXX")
    meta_pixel_id = models.CharField(_("Meta Pixel ID"), max_length=30, blank=True)

    default_meta_description = models.CharField(
        _("meta description padrão"),
        max_length=160,
        default="Catálogo de produtos de irrigação da Irrigação Sem Fronteiras. Monte sua lista e peça um orçamento.",
    )
    default_og_image = models.ImageField(_("imagem padrão para compartilhamento"), upload_to="site/", blank=True)
    updated_at = models.DateTimeField(_("atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("configuração do site")
        verbose_name_plural = _("configuração do site")

    def __str__(self):
        return str(_("Configuração do site"))

    def save(self, *args, **kwargs):
        self.pk = 1
        self._state.adding = not type(self).objects.filter(pk=1).exists()
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):  # o singleton não é apagado
        return (0, {})

    def clean(self):
        errors = {}
        if self.whatsapp_number and not re.fullmatch(r"\d{10,13}", self.whatsapp_number):
            errors["whatsapp_number"] = _("Use só dígitos, com DDI e DDD (10 a 13 dígitos).")
        if self.gtm_id and not re.fullmatch(r"GTM-[A-Z0-9]{4,12}", self.gtm_id):
            errors["gtm_id"] = _("Formato esperado: GTM-XXXXXXX.")
        if self.meta_pixel_id and not re.fullmatch(r"\d{6,20}", self.meta_pixel_id):
            errors["meta_pixel_id"] = _("Use só dígitos.")
        if errors:
            raise ValidationError(errors)

    @classmethod
    def load(cls) -> "SiteConfiguration":
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj = cls.objects.filter(pk=1).first() or cls(pk=1)
            cache.set(cls.CACHE_KEY, obj, 300)
        return obj

    @property
    def quote_recipients(self) -> list[str]:
        return [e.strip() for e in self.quote_recipient_emails.splitlines() if e.strip()]

    @property
    def social_links(self) -> list[tuple[str, str]]:
        pares = [
            ("instagram", self.instagram_url),
            ("facebook", self.facebook_url),
            ("linkedin", self.linkedin_url),
            ("youtube", self.youtube_url),
        ]
        return [(nome, url) for nome, url in pares if url]
