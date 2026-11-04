from django.db import models
from django.utils.translation import gettext_lazy as _


class QuoteStatus(models.TextChoices):
    NEW = "new", _("Novo")
    IN_PROGRESS = "in_progress", _("Em atendimento")
    ANSWERED = "answered", _("Respondido")
    CLOSED = "closed", _("Fechado (ganho)")
    LOST = "lost", _("Perdido")


class QuoteSource(models.TextChoices):
    SITE = "site", _("Site (formulário)")
    WHATSAPP = "whatsapp", _("WhatsApp")
    CONTACT = "contato", _("Página de contato")


UFS = [(uf, uf) for uf in (
    ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
)]  # fmt: skip
