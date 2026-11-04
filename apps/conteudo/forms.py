from django import forms

from apps.orcamentos.forms import QuoteForm


class ContatoForm(QuoteForm):
    """Mesmo formulário do orçamento, com mensagem obrigatória e cidade/UF opcionais."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = True
        self.fields["message"].label = "Mensagem"
        self.fields["message"].widget = forms.Textarea(
            attrs={"rows": 5, "placeholder": "Conte o que você precisa: cultura, área, prazo, dúvidas…"}
        )
        self.fields["city"].required = False
        self.fields["state"].required = False
