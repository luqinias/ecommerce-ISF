"""Catálogo de demonstração: importa docs/exemplos/catalogo-demo.csv com ilustrações próprias.

Tudo é marcado `is_demo=True` e sai com `limpar_catalogo_demo`. Nenhuma foto de terceiros é usada:
as imagens vêm de `ilustracoes.py`, desenhadas uma vez no cache de `demo_midia.py`.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.catalogo.models import Category, Collection, Product, ProductImage
from apps.catalogo.services import demo_midia
from apps.catalogo.services.imagens import TAMANHOS
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
                        "description": "Produtos que acabaram de chegar ao catálogo."},
        "Preparo para a safra": {"color": "ouro", "featured": True, "is_main": True, "order": 2,
                                 "starts_on": hoje - timedelta(days=15), "ends_on": hoje + timedelta(days=120),
                                 "order_deadline": hoje + timedelta(days=45),
                                 "deadline_note": "Após a data, consultar disponibilidade",
                                 "description": "Monte o sistema antes do plantio e evite a fila da alta temporada."},
    }  # fmt: skip


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
            f"{cat.name}: {meta['description'][0].lower()}{meta['description'][1:]} Escolha as opções, informe as "
            "quantidades e receba a proposta pelo WhatsApp ou e-mail."
        )
        cat.save()
    for nome, meta in _colecoes().items():
        col = Collection.objects.filter(name=nome, is_demo=True).first()
        if col:
            for campo, valor in meta.items():
                setattr(col, campo, valor)
            relativo = f"colecoes/{slugify(nome)}.jpg"
            if not col.image:
                col.image.save(PurePosixPath(relativo).name, ContentFile(demo_midia.ler(relativo)), save=False)
            col.save()


def carregar(*, se_vazio: bool = False) -> Relatorio | None:
    """Importa o catálogo de demonstração. Com `se_vazio`, não faz nada se já houver produtos."""
    if se_vazio and Product.objects.exists():
        return None
    demo_midia.gerar()
    relatorio = importar(ARQUIVO, pasta_imagens=demo_midia.pasta(), demo=True)
    _aplicar_metadados()
    return relatorio


def _no_cache(relativo: str) -> str | None:
    """Chave do cache para um `source` do banco (aceita os nomes .png da versão anterior da demo)."""
    especs = demo_midia.especificacoes()
    if relativo in especs:
        return relativo
    alternativo = str(PurePosixPath(relativo).with_suffix(".jpg"))
    return alternativo if alternativo in especs else None


def copiar_se_faltar(nome: str, conteudo) -> bool:
    """Grava `conteudo()` em `nome` no storage padrão, se o arquivo não existir. Retorna se gravou."""
    if not nome or default_storage.exists(nome):
        return False
    salvo = default_storage.save(nome, ContentFile(conteudo()))
    if salvo != nome:  # não deve acontecer (o arquivo não existia); evita apontar para o nome errado
        default_storage.delete(salvo)
        raise RuntimeError(f"o storage gravou {salvo} em vez de {nome}")
    return True


def regenerar_midia() -> dict[str, int]:
    """Recria os arquivos ausentes das imagens de produtos e coleções de demonstração, nos mesmos nomes do banco.

    Serve a hospedagens com disco temporário (ex.: Render gratuito): o banco persiste, os arquivos não.
    Copia do cache de ilustrações (rápido) e não altera registros. Imagens de produtos reais ausentes só
    são contadas: não há como recriá-las.
    """
    contagem = {"recriadas": 0, "miniaturas": 0, "colecoes": 0, "reais_ausentes": 0}
    for img in ProductImage.objects.select_related("product").order_by("pk"):
        if not img.image.name:
            continue
        chave = _no_cache(img.source) if img.product.is_demo else None
        if chave is None:
            if not default_storage.exists(img.image.name):
                contagem["reais_ausentes"] += 1
            continue
        if copiar_se_faltar(img.image.name, lambda c=chave: demo_midia.ler(c)):
            contagem["recriadas"] += 1
        for campo, lado in TAMANHOS.items():
            nome = getattr(img, campo).name
            if copiar_se_faltar(nome, lambda c=chave, ld=lado: demo_midia.ler_miniatura(c, ld)):
                contagem["miniaturas"] += 1
    for col in Collection.objects.filter(is_demo=True).exclude(image=""):
        relativo = f"colecoes/{slugify(col.name)}.jpg"
        if relativo in demo_midia.especificacoes() and copiar_se_faltar(
            col.image.name, lambda r=relativo: demo_midia.ler(r)
        ):
            contagem["colecoes"] += 1
    return contagem
