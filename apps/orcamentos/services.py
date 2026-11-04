"""Escrita: criação do pedido, mensagem do WhatsApp e e-mails (enviados após o commit)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.core import email
from apps.core.models import SiteConfiguration
from apps.core.whatsapp import whatsapp_link
from apps.orcamentos.choices import QuoteSource
from apps.orcamentos.lista import Item
from apps.orcamentos.models import Quote, QuoteItem

logger = logging.getLogger(__name__)

TEXTO_CONSENTIMENTO = (
    "Concordo com o uso dos meus dados para receber este orçamento e ser contatado sobre ele, "
    "conforme a Política de Privacidade."
)


@transaction.atomic
def criar_orcamento(dados: dict, itens: list[Item], *, origem: str = QuoteSource.SITE) -> Quote:
    if not itens and origem != QuoteSource.CONTACT:
        raise ValueError("Orçamento sem itens.")
    quote = Quote.objects.create(
        name=dados.get("name", ""),
        company=dados.get("company", ""),
        email=dados.get("email", ""),
        phone=dados.get("phone", ""),
        city=dados.get("city", ""),
        state=dados.get("state", ""),
        message=dados.get("message", ""),
        source=origem,
        consent=bool(dados.get("consent")),
        consent_text=TEXTO_CONSENTIMENTO if dados.get("consent") else "",
    )
    QuoteItem.objects.bulk_create(
        QuoteItem(
            quote=quote,
            product=i.produto,
            variant=i.variacao,
            product_name=i.produto.name,
            product_sku=i.produto.sku,
            variant_label=i.rotulo_variacao,
            variant_sku=i.variacao.sku if i.variacao else "",
            quantity=i.quantidade,
            unit=i.unidade,
        )
        for i in itens
    )
    if origem != QuoteSource.WHATSAPP:
        transaction.on_commit(lambda: enviar_emails(quote.pk))
    return quote


def mensagem_whatsapp(quote: Quote) -> str:
    linhas = [f"Olá! Acabei de pedir um orçamento pelo site ({quote.code})."]
    if quote.name:
        linhas.append(f"Nome: {quote.name}" + (f" — {quote.company}" if quote.company else ""))
    if quote.city:
        linhas.append(f"Cidade: {quote.city}" + (f"/{quote.state}" if quote.state else ""))
    linhas.append("")
    linhas.append("Itens:")
    for item in quote.items.all():
        detalhe = f" ({item.variant_label})" if item.variant_label else ""
        linhas.append(f"• {item.quantity} {item.unit} — {item.product_name}{detalhe} [{item.sku}]")
    if quote.message:
        linhas += ["", f"Observações: {quote.message}"]
    return "\n".join(linhas)


def link_whatsapp(quote: Quote) -> str:
    site = SiteConfiguration.load()
    return whatsapp_link(site, mensagem_whatsapp(quote)) if site.whatsapp_number else ""


def enviar_emails(quote_id) -> None:
    """Envia o e-mail da equipe e a confirmação do cliente. Falha não perde o pedido: fica registrada."""
    quote = Quote.objects.prefetch_related("items").get(pk=quote_id)
    site = SiteConfiguration.load()
    contexto = {
        "quote": quote,
        "itens": list(quote.items.all()),
        "site": site,
        "url_admin": settings.BASE_URL + reverse("admin:orcamentos_quote_change", args=[quote.pk]),
        "link_whatsapp": link_whatsapp(quote),
    }
    erros = []
    equipe = site.quote_recipients or ([site.contact_email] if site.contact_email else [])
    if not equipe:
        erros.append("Nenhum destinatário configurado (Configuração do site › e-mails que recebem os orçamentos).")
    try:
        email.enviar(
            "orcamento_equipe",
            f"[{site.short_name}] Novo orçamento {quote.code} — {quote.name or quote.get_source_display()}",
            equipe,
            contexto,
            responder_para=quote.email or None,
        )
    except Exception as erro:
        logger.exception("Falha ao enviar e-mail da equipe do orçamento %s", quote.code)
        erros.append(f"Equipe: {erro}")
    if quote.email:
        try:
            email.enviar(
                "orcamento_cliente",
                f"Recebemos o seu pedido de orçamento {quote.code}",
                [quote.email],
                contexto,
                responder_para=site.contact_email or None,
            )
        except Exception as erro:
            logger.exception("Falha ao enviar confirmação do orçamento %s", quote.code)
            erros.append(f"Cliente: {erro}")
    Quote.objects.filter(pk=quote.pk).update(
        email_sent_at=None if erros else timezone.now(),
        email_error="\n".join(erros),
    )
