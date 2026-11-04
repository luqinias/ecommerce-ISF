"""Formulários do admin: campos de atributos técnicos gerados a partir da definição da categoria."""

from __future__ import annotations

import json

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.catalogo import schema as schema_attrs
from apps.catalogo.models import Category, Product, Variant

PREFIXO = "attr__"
CAMPOS_PRODUTO = [
    "name", "slug", "sku", "primary_category", "categories", "collections", "short_description", "description",
    "min_quantity", "quantity_step", "sale_unit", "active", "featured", "new_until", "relevance", "is_demo",
    "meta_title", "meta_description",
]  # fmt: skip


def campo_para(attr: dict, *, obrigatorio: bool) -> forms.Field:
    rotulo = attr["label"] + (f" ({attr['unit']})" if attr.get("unit") else "")
    ajuda = attr.get("help", "")
    tipo = attr["type"]
    if tipo == "number":
        return forms.FloatField(label=rotulo, required=obrigatorio, help_text=ajuda, localize=True)
    if tipo == "boolean":
        return forms.TypedChoiceField(
            label=rotulo,
            required=obrigatorio,
            help_text=ajuda,
            choices=[("", "—"), ("true", _("Sim")), ("false", _("Não"))],
            coerce=lambda v: v == "true",
            empty_value=None,
        )
    if tipo == "choice":
        opcoes = [("", "—")] + [(str(c), str(c)) for c in attr["choices"]]
        return forms.ChoiceField(label=rotulo, required=obrigatorio, help_text=ajuda, choices=opcoes)
    return forms.CharField(label=rotulo, required=obrigatorio, help_text=ajuda, max_length=200)


def valor_inicial(valor, attr: dict):
    if attr["type"] == "boolean" and valor is not None:
        return "true" if valor else "false"
    return valor


def _categoria_escolhida(form) -> Category | None:
    pk = None
    if form.is_bound:
        pk = form.data.get(form.add_prefix("primary_category"))
    pk = pk or form.initial.get("primary_category") or getattr(form.instance, "primary_category_id", None)
    if not pk:
        return None
    try:
        return Category.objects.select_related("parent").get(pk=pk)
    except (Category.DoesNotExist, ValueError):
        return None


class JSONBonito(forms.Textarea):
    """Textarea que mostra JSON indentado (mais fácil de editar o schema no admin)."""

    def format_value(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                return value
        return json.dumps(value, ensure_ascii=False, indent=2)


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            "name", "slug", "parent", "icon", "image", "order", "active", "show_on_home", "is_demo",
            "description", "seo_text", "meta_title", "meta_description", "attribute_schema",
        )  # fmt: skip
        widgets = {
            "attribute_schema": JSONBonito(attrs={"rows": 14, "class": "vLargeTextField", "spellcheck": "false"})
        }


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = CAMPOS_PRODUTO

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categoria = _categoria_escolhida(self)
        self.atributos_ficha: list[dict] = []
        if self.categoria:
            self.atributos_ficha = [a for a in self.categoria.effective_schema if not a.get("variant")]
        atuais = self.instance.attributes or {}
        for attr in self.atributos_ficha:
            nome = PREFIXO + attr["key"]
            self.fields[nome] = campo_para(attr, obrigatorio=bool(attr.get("required")))
            if attr["key"] in atuais:
                self.initial.setdefault(nome, valor_inicial(atuais[attr["key"]], attr))

    @property
    def nomes_atributos(self) -> list[str]:
        return [PREFIXO + a["key"] for a in self.atributos_ficha]

    def clean(self):
        dados = super().clean()
        atributos = {}
        for attr in self.atributos_ficha:
            valor = dados.get(PREFIXO + attr["key"])
            if valor in (None, ""):
                continue
            atributos[attr["key"]] = schema_attrs.converter_valor(valor, attr) if attr["type"] == "choice" else valor
            if isinstance(atributos[attr["key"]], float) and atributos[attr["key"]].is_integer():
                atributos[attr["key"]] = int(atributos[attr["key"]])
        self.instance.attributes = atributos
        return dados

    def _post_clean(self):
        super()._post_clean()
        # erros de `attributes` (validação do model) aparecem no topo do formulário
        if "attributes" in self._errors:
            self.add_error(None, self._errors.pop("attributes"))


def form_de_variacao(produto: Product | None) -> type[forms.ModelForm]:
    """Form da variação com um campo por atributo de variação da categoria do produto."""
    atributos = produto.variant_attributes if produto and produto.primary_category_id else []

    class VariantForm(forms.ModelForm):
        class Meta:
            model = Variant
            fields = (
                ("sku", "image", "active", "order") if atributos else ("sku", "attributes", "image", "active", "order")
            )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            atuais = self.instance.attributes or {}
            for attr in atributos:
                nome = PREFIXO + attr["key"]
                self.fields[nome] = campo_para(attr, obrigatorio=True)
                if attr["key"] in atuais:
                    self.initial.setdefault(nome, valor_inicial(atuais[attr["key"]], attr))
            if produto and "image" in self.fields:
                self.fields["image"].queryset = produto.images.all()

        def clean(self):
            dados = super().clean()
            if atributos:
                valores = {}
                for attr in atributos:
                    valor = dados.get(PREFIXO + attr["key"])
                    if valor in (None, ""):
                        continue
                    if attr["type"] == "choice":
                        valor = schema_attrs.converter_valor(valor, attr)
                    if isinstance(valor, float) and valor.is_integer():
                        valor = int(valor)
                    valores[attr["key"]] = valor
                self.instance.attributes = valores
            return dados

    return VariantForm
