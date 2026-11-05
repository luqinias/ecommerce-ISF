"""Mídia da demonstração: gera as ilustrações uma vez numa pasta de cache e as copia para o storage.

Desenhar ~140 imagens com supersampling leva cerca de um minuto, caro demais para cada subida de uma
hospedagem com disco temporário e pouca CPU (Render gratuito). Por isso:
- `gerar()` desenha tudo em `settings.DEMO_MIDIA_DIR` (no Docker, durante o build da imagem), com as
  miniaturas WebP já prontas, e grava um selo de versão. Se o selo bate, não refaz nada.
- O carregamento e `regenerar_midia_demo` só copiam arquivos do cache para o storage.
Com `settings.DEMO_MIDIA_RAPIDA` (testes), as imagens saem pequenas e sem supersampling.
"""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Callable
from pathlib import Path

from django.conf import settings
from PIL import Image

from apps.catalogo.services import demo_dados, ilustracoes
from apps.catalogo.services.imagens import TAMANHOS, para_webp

SELO = ".versao.json"


def pasta() -> Path:
    return Path(settings.DEMO_MIDIA_DIR)


def _rapido() -> bool:
    return bool(getattr(settings, "DEMO_MIDIA_RAPIDA", False))


def _lado() -> int:
    return 240 if _rapido() else ilustracoes.LADO


def especificacoes() -> dict[str, Callable[[], Image.Image]]:
    """Caminho relativo no cache → função que desenha a imagem."""
    rapido, lado = _rapido(), _lado()
    specs: dict[str, Callable[[], Image.Image]] = {}
    for sku, (desenho, cor, opcoes, cena) in demo_dados.PRODUTOS.items():
        semente = int(hashlib.md5(sku.encode(), usedforsecurity=False).hexdigest()[:4], 16)
        specs[f"demo/{sku}.jpg"] = lambda d=desenho, c=cor, o=opcoes: ilustracoes.desenhar(
            d, c, o, lado=lado, rapido=rapido
        )
        specs[f"demo/{sku}-detalhe.jpg"] = lambda d=desenho, c=cor, o=opcoes: ilustracoes.desenhar(
            d, c, o, modo="detalhe", lado=lado, rapido=rapido
        )
        produto = (desenho, cor, opcoes) if cena == "instalacao" else None
        specs[f"demo/{sku}-campo.jpg"] = lambda c=cena, s=semente, p=produto: ilustracoes.desenhar_cena(
            c, s, lado=lado, rapido=rapido, produto=p
        )
    for nome, (cena, semente) in demo_dados.COLECAO_CENA.items():
        specs[f"colecoes/{_slug(nome)}.jpg"] = lambda c=cena, s=semente: ilustracoes.desenhar_cena(
            c, s, lado=lado, rapido=rapido
        )
    hero = demo_dados.PRODUTOS
    specs["home/hero-1.jpg"] = lambda: ilustracoes.desenhar_cena("fruticultura", 7, lado=lado, rapido=rapido)
    specs["home/hero-2.jpg"] = lambda: ilustracoes.desenhar(*hero["FIL-001"][:3], lado=lado, rapido=rapido)
    specs["home/hero-3.jpg"] = lambda: ilustracoes.desenhar(*hero["AUT-001"][:3], lado=lado, rapido=rapido)
    for i, (_titulo, _sub, cena) in enumerate(demo_dados.PORTFOLIO):
        produto = hero["FIL-001"][:3] if cena == "instalacao" else None
        specs[f"portfolio/portfolio-{i + 1}.jpg"] = lambda c=cena, s=i, p=produto: ilustracoes.desenhar_cena(
            c, s + 11, lado=lado, rapido=rapido, produto=p
        )
    return specs


def _slug(texto: str) -> str:
    from django.utils.text import slugify

    return slugify(texto)


def _versao() -> str:
    """Muda quando o gerador, os dados ou o modo mudam (invalida o cache)."""
    h = hashlib.sha256()
    for modulo in (ilustracoes, demo_dados):
        h.update(Path(modulo.__file__).read_bytes())
    h.update(f"rapido={_rapido()}".encode())
    return h.hexdigest()[:16]


def miniatura(relativo: str, lado: int) -> Path:
    caminho = Path(relativo)
    return pasta() / "miniaturas" / caminho.parent / f"{caminho.stem}-{lado}.webp"


def gerar(*, forcar: bool = False, saida=None) -> int:
    """Desenha no cache o que falta (ou tudo, se a versão mudou). Retorna quantas imagens desenhou."""
    raiz = pasta()
    selo = raiz / SELO
    versao = _versao()
    specs = especificacoes()
    atual = not forcar and selo.exists() and json.loads(selo.read_text()).get("versao") == versao
    feitas = 0
    for relativo, desenhar in specs.items():
        destino = raiz / relativo
        if atual and destino.exists() and all(miniatura(relativo, lado).exists() for lado in TAMANHOS.values()):
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagem = desenhar().convert("RGB")
        imagem.save(destino, format="JPEG", quality=88, optimize=True, progressive=True)
        for lado in TAMANHOS.values():
            arquivo = miniatura(relativo, lado)
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_bytes(para_webp(imagem, lado).read())
        feitas += 1
        if saida and feitas % 20 == 0:
            saida(f"  {feitas} imagens…")
    if feitas or not atual:  # só escreve quando algo mudou (no Docker o cache é somente leitura)
        raiz.mkdir(parents=True, exist_ok=True)
        selo.write_text(json.dumps({"versao": versao, "total": len(specs)}))
    return feitas


def ler(relativo: str) -> bytes:
    """Bytes de uma imagem do cache (gera o cache se preciso)."""
    caminho = pasta() / relativo
    if not caminho.exists():
        gerar()
    return caminho.read_bytes()


def ler_miniatura(relativo: str, lado: int) -> bytes:
    caminho = miniatura(relativo, lado)
    if not caminho.exists():
        gerar()
    if caminho.exists():
        return caminho.read_bytes()
    with Image.open(io.BytesIO(ler(relativo))) as imagem:  # imagem fora das especificações
        return para_webp(imagem.convert("RGB"), lado).read()
