"""Envio de e-mail texto + HTML (inspirado no SendEmailBase do projeto interno)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def normalizar_destinatarios(destinatarios) -> list[str]:
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]
    vistos = []
    for e in destinatarios or []:
        e = (e or "").strip()
        if e and e.lower() not in {v.lower() for v in vistos}:
            vistos.append(e)
    return vistos


def enviar(template: str, assunto: str, destinatarios, contexto: dict, *, responder_para: str | None = None) -> int:
    """Renderiza `emails/<template>.txt` e `.html` e envia. Retorna o nº de mensagens enviadas."""
    para = normalizar_destinatarios(destinatarios)
    if not para:
        return 0
    texto = render_to_string(f"emails/{template}.txt", contexto)
    html = render_to_string(f"emails/{template}.html", contexto)
    msg = EmailMultiAlternatives(
        subject=assunto,
        body=texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=para,
        reply_to=[responder_para] if responder_para else None,
    )
    msg.attach_alternative(html, "text/html")
    return msg.send()
