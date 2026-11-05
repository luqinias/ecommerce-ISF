"""Catálogo de demonstração: importa docs/exemplos/catalogo-demo.csv com imagens placeholder geradas.

Tudo é marcado `is_demo=True` e sai com `limpar_catalogo_demo`. Nenhuma foto de terceiros é usada.
"""

from __future__ import annotations

import csv
import hashlib
import tempfile
import unicodedata
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from apps.catalogo.choices import ImageKind
from apps.catalogo.models import Category, Collection, Product, ProductImage
from apps.catalogo.services.imagens import TAMANHOS, para_webp
from apps.catalogo.services.importacao import Relatorio, importar

ARQUIVO = Path(settings.BASE_DIR) / "docs" / "exemplos" / "catalogo-demo.csv"

# Metadados de apresentação das categorias e coleções de demonstração (dados, não regra).
CATEGORIAS = {
    "Gotejamento": {"icon": "droplet", "order": 1, "home": True, "cor": ("#1d6a44", "#8fdcb3"),
                    "description": "Emissores e fitas para aplicar água direto na raiz, com economia e uniformidade."},
    "Fitas gotejadoras": {"icon": "layers", "order": 1, "cor": ("#145033", "#a7d9bd"),
                          "description": "Fitas e mangueiras gotejadoras em rolo para culturas anuais e perenes."},
    "Microaspersão": {"icon": "sprout", "order": 2, "home": True, "cor": ("#1d5fa8", "#b9d3f0"),
                      "description": "Microaspersores e nebulizadores para pomares, viveiros e estufas."},
    "Aspersão": {"icon": "droplet", "order": 3, "home": True, "cor": ("#24402f", "#c7e3d2"),
                 "description": "Aspersores de impacto, setoriais e canhões para áreas abertas."},
    "Tubos e Conexões": {"icon": "layers", "order": 4, "home": True, "cor": ("#555d56", "#e6e3da"),
                         "description": "Tubos de PE e PVC, mangueiras e a linha completa de conexões."},
    "Conexões": {"icon": "wrench", "order": 1, "cor": ("#676e67", "#efede6"),
                 "description": "Conectores, luvas, registros, tês e colares para montar a rede."},
    "Filtragem": {"icon": "filter", "order": 5, "home": True, "cor": ("#9a6400", "#f6deaa"),
                  "description": "Filtros de disco, tela, areia e hidrociclones para proteger o sistema."},
    "Automação e Controladores": {"icon": "zap", "order": 6, "cor": ("#11251a", "#5bc792"),
                                  "description": "Controladores, válvulas solenoides e sensores."},
    "Bombas": {"icon": "gauge", "order": 7, "cor": ("#b42318", "#f6c9c4"),
               "description": "Bombas centrífugas e submersas para captação e pressurização."},
    "Fertirrigação": {"icon": "sprout", "order": 8, "cor": ("#1b7a45", "#cde9d8"),
                      "description": "Injetores e dosadores para aplicar nutrientes pela água."},
    "Kits": {"icon": "truck", "order": 9, "home": True, "cor": ("#f2b01e", "#11251a"),
             "description": "Conjuntos prontos para começar a irrigar sem dimensionar peça por peça."},
}  # fmt: skip


def _colecoes():
    hoje = timezone.localdate()
    return {
        "Lançamentos": {"color": "verde", "featured": True, "order": 1,
                        "description": "Produtos que acabaram de entrar no catálogo de demonstração."},
        "Preparo para a safra": {"color": "ouro", "featured": True, "is_main": True, "order": 2,
                                 "starts_on": hoje - timedelta(days=15), "ends_on": hoje + timedelta(days=120),
                                 "order_deadline": hoje + timedelta(days=45),
                                 "deadline_note": "Após a data, consultar disponibilidade",
                                 "description": "Monte o sistema antes do plantio e evite a fila da alta temporada."},
    }  # fmt: skip


def _fonte(tamanho: int):
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:  # Pillow antigo
        return ImageFont.load_default()


def gerar_placeholder(destino: Path, titulo: str, subtitulo: str, cores: tuple[str, str], ambiente: bool) -> None:
    """Imagem 900×900 com gradiente, gota estilizada, nome do produto e selo DEMO."""
    lado = 900
    escura, clara = cores
    if ambiente:
        escura, clara = "#24402f", "#cfe6d6"
    e = tuple(int(escura[i : i + 2], 16) for i in (1, 3, 5))
    c = tuple(int(clara[i : i + 2], 16) for i in (1, 3, 5))
    # gradiente vertical: 1 coluna calculada e ampliada (rápido)
    coluna = Image.new("RGB", (1, lado))
    for y in range(lado):
        t = y / lado * (0.55 if not ambiente else 0.9)
        coluna.putpixel((0, y), tuple(int(c[k] + (e[k] - c[k]) * t) for k in range(3)))
    img = coluna.resize((lado, lado))
    desenho = ImageDraw.Draw(img)
    if ambiente:  # linhas de plantio em perspectiva
        for i in range(-6, 7):
            desenho.line([(lado / 2 + i * 18, 420), (lado / 2 + i * 150, lado)], fill=(255, 255, 255), width=3)
        desenho.rectangle([0, 0, lado, 420], fill=(222, 236, 228))
    semente = int(hashlib.md5(titulo.encode(), usedforsecurity=False).hexdigest()[:6], 16)
    cx, cy, r = lado // 2, 330 + (semente % 40), 120
    desenho.ellipse([cx - r, cy - r + 60, cx + r, cy + r + 60], fill=e)
    desenho.polygon([(cx, cy - 170), (cx - r + 8, cy + 30), (cx + r - 8, cy + 30)], fill=e)
    desenho.ellipse([cx - 40, cy + 40, cx + 10, cy + 90], fill=c)
    fonte = _fonte(40)
    # a fonte embutida do Pillow não tem todos os acentos: só na imagem, texto sem acento
    titulo = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    subtitulo = unicodedata.normalize("NFKD", subtitulo).encode("ascii", "ignore").decode()
    linhas, atual = [], ""
    for palavra in titulo.split():
        if len(atual) + len(palavra) > 26:
            linhas.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    linhas.append(atual)
    y = 600
    for linha in linhas[:3]:
        w = desenho.textlength(linha, font=fonte)
        desenho.text(((lado - w) / 2, y), linha, font=fonte, fill=(17, 37, 26) if not ambiente else (255, 255, 255))
        y += 50
    desenho.rounded_rectangle([lado - 230, 30, lado - 30, 92], radius=31, fill=(17, 37, 26))
    desenho.text((lado - 202, 42), "DEMO", font=_fonte(36), fill=(242, 176, 30))
    pequena = _fonte(28)
    w = desenho.textlength(subtitulo, font=pequena)
    desenho.text(
        ((lado - w) / 2, lado - 70), subtitulo, font=pequena, fill=(85, 93, 86) if not ambiente else (255, 255, 255)
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, format="PNG")


def _gerar_imagens(pasta: Path) -> None:
    with ARQUIVO.open(encoding="utf-8") as f:
        vistos = set()
        for linha in csv.DictReader(f, delimiter=";"):
            sku = linha["sku_produto"]
            if sku in vistos:
                continue
            vistos.add(sku)
            raiz = linha["categoria"].split(">")[-1].strip()
            cores = CATEGORIAS.get(raiz, {}).get("cor", ("#1d6a44", "#e2efe7"))
            for origem in linha["imagens"].split("|"):
                ambiente = origem.startswith("ambiente:")
                caminho = origem.split(":", 1)[1] if ambiente else origem
                sub = "Aplicação em campo · imagem ilustrativa" if ambiente else "Imagem ilustrativa"
                gerar_placeholder(pasta / caminho, linha["nome"], sub, cores, ambiente)


@transaction.atomic
def _aplicar_metadados() -> None:
    for cat in Category.objects.filter(is_demo=True):
        meta = CATEGORIAS.get(cat.name)
        if not meta:
            continue
        cat.icon = meta["icon"]
        cat.order = meta["order"]
        cat.show_on_home = meta.get("home", False)
        cat.description = meta["description"]
        cat.seo_text = (
            f"{cat.name}: categoria do catálogo de demonstração. Os produtos, textos e especificações são "
            "fictícios e serão trocados pelo catálogo real da Irrigação Sem Fronteiras."
        )
        cat.save()
    for nome, meta in _colecoes().items():
        col = Collection.objects.filter(name=nome, is_demo=True).first()
        if col:
            for campo, valor in meta.items():
                setattr(col, campo, valor)
            col.save()


def _cores_do_produto(produto: Product) -> tuple[str, str]:
    categoria = produto.primary_category
    return CATEGORIAS.get(categoria.name if categoria else "", {}).get("cor", ("#1d6a44", "#e2efe7"))


def recriar_arquivo(nome: str, titulo: str, subtitulo: str, cores: tuple[str, str], ambiente: bool) -> bool:
    """Gera o placeholder e grava em `nome` no storage padrão, se o arquivo não existir. Retorna se gravou."""
    if default_storage.exists(nome):
        return False
    with tempfile.TemporaryDirectory(prefix="isf-midia-") as tmp:
        caminho = Path(tmp) / "placeholder.png"
        gerar_placeholder(caminho, titulo, subtitulo, cores, ambiente)
        with caminho.open("rb") as arquivo:
            salvo = default_storage.save(nome, File(arquivo))
    if salvo != nome:  # não deve acontecer (o arquivo não existia); evita apontar para o nome errado
        default_storage.delete(salvo)
        raise RuntimeError(f"o storage gravou {salvo} em vez de {nome}")
    return True


def _recriar_miniaturas(img: ProductImage) -> int:
    """Grava `card` e `large` ausentes nos nomes já registrados no banco, a partir de `image`."""
    faltando = {
        campo: getattr(img, campo).name
        for campo in TAMANHOS
        if getattr(img, campo).name and not default_storage.exists(getattr(img, campo).name)
    }
    if not faltando:
        return 0
    with default_storage.open(img.image.name, "rb") as arquivo, Image.open(arquivo) as original:
        imagem = original.convert("RGB")
        for campo, nome in faltando.items():
            default_storage.save(nome, para_webp(imagem, TAMANHOS[campo]))
    return len(faltando)


def regenerar_midia() -> dict[str, int]:
    """Recria os arquivos ausentes das imagens de produtos de demonstração, nos mesmos nomes do banco.

    Serve a hospedagens com disco temporário (ex.: Render gratuito): o banco persiste, os arquivos não.
    Não altera registros. Imagens de produtos reais ausentes só são contadas (não há como recriá-las).
    """
    contagem = {"recriadas": 0, "miniaturas": 0, "reais_ausentes": 0}
    imagens = ProductImage.objects.select_related("product__primary_category").order_by("pk")
    for img in imagens:
        if not img.image.name:
            continue
        if not img.product.is_demo:
            if not default_storage.exists(img.image.name):
                contagem["reais_ausentes"] += 1
            continue
        ambiente = img.kind == ImageKind.ENVIRONMENT
        sub = "Aplicação em campo · imagem ilustrativa" if ambiente else "Imagem ilustrativa"
        if recriar_arquivo(img.image.name, img.product.name, sub, _cores_do_produto(img.product), ambiente):
            contagem["recriadas"] += 1
        contagem["miniaturas"] += _recriar_miniaturas(img)
    return contagem


def carregar(*, se_vazio: bool = False) -> Relatorio | None:
    """Importa o catálogo de demonstração. Com `se_vazio`, não faz nada se já houver produtos."""
    if se_vazio and Product.objects.exists():
        return None
    with tempfile.TemporaryDirectory(prefix="isf-demo-") as tmp:
        pasta = Path(tmp)
        _gerar_imagens(pasta)
        relatorio = importar(ARQUIVO, pasta_imagens=pasta, demo=True)
    _aplicar_metadados()
    return relatorio
