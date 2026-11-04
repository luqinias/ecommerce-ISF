from django.core.management.base import BaseCommand

from apps.catalogo.models import Product
from apps.catalogo.services.importacao import limpar_demo


class Command(BaseCommand):
    help = "Remove do catálogo apenas os registros marcados como demonstração (is_demo=True)."

    def add_arguments(self, parser):
        parser.add_argument("--sim", action="store_true", help="Confirma sem perguntar")

    def handle(self, *args, **opts):
        total = Product.objects.filter(is_demo=True).count()
        if not opts["sim"]:
            resposta = input(f"Remover {total} produto(s) de demonstração? [s/N] ")
            if resposta.strip().lower() not in {"s", "sim"}:
                self.stdout.write("Nada foi removido.")
                return
        contagem = limpar_demo()
        self.stdout.write(self.style.SUCCESS("Removidos: " + ", ".join(f"{v} {k}" for k, v in contagem.items())))
