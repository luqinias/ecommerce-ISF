"""Limite de taxa simples com o cache do Django (decisão C11). O IP só entra, com hash, na chave do cache."""

from __future__ import annotations

import hashlib
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render


def ip_do_cliente(request) -> str:
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        encaminhado = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if encaminhado:
            return encaminhado.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def excedeu(request, escopo: str, limite: int, janela: int) -> bool:
    """Conta a requisição e diz se passou do limite na janela (segundos)."""
    ip = hashlib.sha256(f"{settings.SECRET_KEY}:{ip_do_cliente(request)}".encode()).hexdigest()[:32]
    chave = f"rl:{escopo}:{ip}"
    if cache.add(chave, 1, janela):
        return False
    try:
        total = cache.incr(chave)
    except ValueError:
        cache.set(chave, 1, janela)
        return False
    return total > limite


def limite_de_taxa(escopo: str, limite: int = 5, janela: int = 600, metodos=("POST",)):
    def decorador(view):
        @wraps(view)
        def envolvida(request, *args, **kwargs):
            if request.method in metodos and excedeu(request, escopo, limite, janela):
                return render(request, "429.html", status=429)
            return view(request, *args, **kwargs)

        return envolvida

    return decorador
