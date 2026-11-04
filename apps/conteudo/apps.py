from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConteudoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.conteudo"
    verbose_name = _("Conteúdo")
