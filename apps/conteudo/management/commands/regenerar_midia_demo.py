"""Recria os arquivos de imagem ausentes do catálogo e do conteúdo de demonstração.

Para hospedagens com disco temporário (ex.: Render gratuito), em que o banco persiste e a pasta de mídia
é apagada a cada deploy ou reinício. Usa os mesmos nomes gravados no banco e não altera registros.
Idempotente: o que já existe é mantido. Roda no entrypoint do Docker quando LOAD_DEMO_DATA=True.
"""

from django.core.management.base import BaseCommand

from apps.catalogo.services import demo as demo_catalogo
from apps.conteudo import demo as demo_conteudo


class Command(BaseCommand):
    help = "Recria as imagens de demonstração que faltam no storage de mídia (sem alterar o banco)."

    def handle(self, *args, **opts):
        catalogo = demo_catalogo.regenerar_midia()
        conteudo = demo_conteudo.regenerar_midia()
        self.stdout.write(
            self.style.SUCCESS(
                f"Mídia de demonstração: {catalogo['recriadas']} imagens de produto e "
                f"{catalogo['miniaturas']} miniaturas recriadas; {catalogo['colecoes']} imagens de coleções; "
                f"{conteudo} imagens da home e do portfólio."
            )
        )
        if catalogo["reais_ausentes"]:
            self.stderr.write(
                self.style.WARNING(
                    f"{catalogo['reais_ausentes']} imagens de produtos reais estão sem arquivo e não podem ser "
                    "recriadas. Use armazenamento persistente para mídia (disco ou S3; ver docs/deploy.md)."
                )
            )
