"""Desenha as ilustrações do catálogo de demonstração no cache (settings.DEMO_MIDIA_DIR).

Roda no build da imagem Docker, para que a subida só copie arquivos. Idempotente: com o cache em dia
(mesma versão do gerador e dos dados), não desenha nada.
"""

import time

from django.core.management.base import BaseCommand

from apps.catalogo.services import demo_midia


class Command(BaseCommand):
    help = "Gera o cache de ilustrações da demonstração (produtos, cenas, hero, portfólio e coleções)."

    def add_arguments(self, parser):
        parser.add_argument("--forcar", action="store_true", help="Redesenha tudo, mesmo com o cache em dia")

    def handle(self, *args, **opts):
        inicio = time.monotonic()
        feitas = demo_midia.gerar(forcar=opts["forcar"], saida=self.stdout.write)
        total = len(demo_midia.especificacoes())
        self.stdout.write(
            self.style.SUCCESS(
                f"Cache de mídia da demonstração em {demo_midia.pasta()}: {feitas} de {total} imagens desenhadas "
                f"({time.monotonic() - inicio:.1f} s)."
            )
        )
