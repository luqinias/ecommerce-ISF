from django.db import models
from django.utils.translation import gettext_lazy as _


class SaleUnit(models.TextChoices):
    PIECE = "piece", _("peça")
    METER = "meter", _("metro")
    ROLL = "roll", _("rolo")
    KIT = "kit", _("kit")
    BOX = "box", _("caixa")


# Plural e abreviação para textos como "Mínimo de 50 metros".
SALE_UNIT_PLURAL = {"piece": "peças", "meter": "metros", "roll": "rolos", "kit": "kits", "box": "caixas"}
SALE_UNIT_ABBR = {"piece": "pç", "meter": "m", "roll": "rolo", "kit": "kit", "box": "cx"}


class AttributeType(models.TextChoices):
    TEXT = "text", _("texto")
    NUMBER = "number", _("número")
    BOOLEAN = "boolean", _("sim/não")
    CHOICE = "choice", _("lista de opções")


class ImageKind(models.TextChoices):
    PRODUCT = "product", _("produto")
    ENVIRONMENT = "environment", _("aplicação em campo")


class CollectionColor(models.TextChoices):
    GREEN = "verde", _("verde")
    BLUE = "azul", _("azul")
    GOLD = "ouro", _("ouro")
    EARTH = "terra", _("terra")
    DARK = "escuro", _("escuro")


class ImportStatus(models.TextChoices):
    PENDING = "pending", _("pendente")
    DONE = "done", _("concluída")
    FAILED = "failed", _("falhou")


CATEGORY_ICONS = [
    ("droplet", _("gota")),
    ("sprout", _("broto")),
    ("gauge", _("manômetro")),
    ("filter", _("filtro")),
    ("zap", _("energia")),
    ("layers", _("camadas")),
    ("wrench", _("ferramenta")),
    ("calendar", _("calendário")),
    ("truck", _("caminhão")),
]
