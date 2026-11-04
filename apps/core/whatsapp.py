"""Geração de links wa.me (orçamento rápido e mensagens pré-preenchidas)."""

from urllib.parse import quote


class _Seguro(dict):
    """Mantém {chave} intacta quando o valor não foi informado."""

    def __missing__(self, chave):
        return "{" + chave + "}"


def formatar_mensagem(modelo: str, **valores) -> str:
    return modelo.format_map(_Seguro(**{k: v for k, v in valores.items() if v is not None}))


def whatsapp_link(site, mensagem: str = "", **valores) -> str:
    """Retorna https://wa.me/<número>?text=<mensagem>. Sem número configurado, cai na página de contato."""
    if not site.whatsapp_number:
        return "/contato/"
    texto = formatar_mensagem(mensagem or site.whatsapp_default_message, **valores)
    return f"https://wa.me/{site.whatsapp_number}?text={quote(texto)}"
