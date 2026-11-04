"""Utilidades compartilhadas da engenharia reversa (somente páginas públicas).

Regras: no máximo 1 requisição a cada 2 s, User-Agent identificável e genérico,
sem submeter formulários e sem seguir links wa.me/mailto.
"""

import json
import time
import urllib.request
from pathlib import Path

BASE = "https://ciadaartebrindes.com.br"
USER_AGENT = "ISF-EstudoDeLayout/1.0 (+estudo interno de estrutura; 1 req/2s)"
INTERVALO = 2.0
RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "docs" / "engenharia-reversa"
RAW = SAIDA / "raw"

_ultima = 0.0


def aguardar():
    global _ultima
    espera = INTERVALO - (time.monotonic() - _ultima)
    if espera > 0:
        time.sleep(espera)
    _ultima = time.monotonic()


def get(url: str) -> tuple[int, str]:
    aguardar()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def salvar_json(nome: str, dados) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    p = RAW / nome
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2))
    return p
