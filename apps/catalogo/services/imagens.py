"""Imagens de produto: miniaturas WebP e obtenção de arquivos (URL ou pasta local) na importação."""

from __future__ import annotations

import contextlib
import io
import logging
import urllib.request
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)

TAMANHOS = {"card": 400, "large": 900}
LIMITE_BYTES = 10 * 1024 * 1024
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class ImagemInvalida(Exception):
    pass


def _webp(imagem: Image.Image, lado: int) -> ContentFile:
    copia = imagem.copy()
    copia.thumbnail((lado, lado), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    copia.save(buffer, format="WEBP", quality=82, method=4)
    return ContentFile(buffer.getvalue())


def gerar_miniaturas(produto_imagem) -> None:
    """Gera `card` (400 px) e `large` (900 px) em WebP a partir de `image`. Não salva o model."""
    if not produto_imagem.image:
        return
    try:
        produto_imagem.image.open("rb")
        produto_imagem.image.seek(0)
        with Image.open(produto_imagem.image) as original:
            imagem = ImageOps.exif_transpose(original)
            imagem = imagem.convert("RGBA" if imagem.mode in ("RGBA", "LA", "P") else "RGB")
            nome = Path(produto_imagem.image.name).stem
            for campo, lado in TAMANHOS.items():
                getattr(produto_imagem, campo).save(f"{nome}-{lado}.webp", _webp(imagem, lado), save=False)
    except (UnidentifiedImageError, OSError) as erro:
        logger.warning("Não foi possível gerar miniaturas de %s: %s", produto_imagem.image.name, erro)
    finally:
        with contextlib.suppress(ValueError, OSError):
            produto_imagem.image.seek(0)


def _validar(conteudo: bytes, origem: str) -> None:
    if len(conteudo) > LIMITE_BYTES:
        raise ImagemInvalida(f"imagem maior que 10 MB: {origem}")
    try:
        with Image.open(io.BytesIO(conteudo)) as img:
            img.verify()
    except (UnidentifiedImageError, OSError) as erro:
        raise ImagemInvalida(f"arquivo não é uma imagem válida: {origem}") from erro


def obter_imagem(origem: str, pasta_base: Path | None = None) -> tuple[str, ContentFile]:
    """Baixa (http/https) ou lê de `pasta_base` a imagem indicada na planilha. Retorna (nome, conteúdo)."""
    origem = origem.strip()
    if origem.lower().startswith(("http://", "https://")):
        req = urllib.request.Request(origem, headers={"User-Agent": "ISF-Catalogo/1.0 (importacao)"})  # noqa: S310
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 — esquema validado acima
                conteudo = resp.read(LIMITE_BYTES + 1)
        except OSError as erro:
            raise ImagemInvalida(f"não foi possível baixar {origem}: {erro}") from erro
        nome = Path(origem.split("?")[0]).name or "imagem.jpg"
    else:
        if pasta_base is None:
            raise ImagemInvalida(f"caminho local sem --imagens: {origem}")
        base = pasta_base.resolve()
        caminho = (base / origem).resolve()
        if base not in caminho.parents:
            raise ImagemInvalida(f"caminho fora da pasta de imagens: {origem}")
        if not caminho.is_file():
            raise ImagemInvalida(f"arquivo não encontrado: {origem}")
        conteudo = caminho.read_bytes()
        nome = caminho.name
    if Path(nome).suffix.lower() not in EXTENSOES:
        nome = f"{Path(nome).stem or 'imagem'}.jpg"
    _validar(conteudo, origem)
    return nome, ContentFile(conteudo)
