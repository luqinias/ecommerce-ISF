import re

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.orcamentos.choices import UFS
from apps.orcamentos.services import TEXTO_CONSENTIMENTO


class QuoteForm(forms.Form):
    name = forms.CharField(label=_("Nome"), max_length=120)
    company = forms.CharField(label=_("Empresa ou propriedade"), max_length=120, required=False)
    email = forms.EmailField(label=_("E-mail"))
    phone = forms.CharField(label=_("Telefone / WhatsApp"), max_length=20, help_text=_("Com DDD."))
    city = forms.CharField(label=_("Cidade"), max_length=80)
    state = forms.ChoiceField(label=_("UF"), choices=[("", "—"), *UFS])
    message = forms.CharField(
        label=_("Mensagem (opcional)"),
        required=False,
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Cultura, área, prazo, dúvidas técnicas…"}),
    )
    consent = forms.BooleanField(label=TEXTO_CONSENTIMENTO)
    # honeypot: invisível para pessoas; robôs costumam preencher
    website = forms.CharField(required=False, label="Não preencha este campo")

    autocomplete = {
        "name": "name",
        "company": "organization",
        "email": "email",
        "phone": "tel",
        "city": "address-level2",
        "state": "address-level1",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome, valor in self.autocomplete.items():
            self.fields[nome].widget.attrs["autocomplete"] = valor
        self.fields["phone"].widget.attrs.update({"inputmode": "tel", "type": "tel"})
        self.fields["website"].widget.attrs.update({"tabindex": "-1", "autocomplete": "off"})

    def clean_phone(self):
        digitos = re.sub(r"\D", "", self.cleaned_data["phone"])
        if digitos.startswith("55") and len(digitos) > 11:
            digitos = digitos[2:]
        if len(digitos) not in (10, 11):
            raise forms.ValidationError(_("Informe o telefone com DDD (10 ou 11 dígitos)."))
        return f"({digitos[:2]}) {digitos[2:-4]}-{digitos[-4:]}"

    @property
    def e_robo(self) -> bool:
        return bool(self.data.get("website"))
