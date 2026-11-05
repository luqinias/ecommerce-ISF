from django.core.management.base import BaseCommand

from apps.catalogo.services import demo
from apps.catalogo.services.importacao import limpar_demo


class Command(BaseCommand):
    help = "Carrega o catálogo fictício de demonstração (docs/exemplos/catalogo-demo.csv) com ilustrações próprias."

    def add_arguments(self, parser):
        parser.add_argument("--se-vazio", action="store_true", help="Só carrega se não houver nenhum produto")
        parser.add_argument(
            "--recarregar", action="store_true", help="Remove a demonstração atual (só is_demo) e carrega de novo"
        )

    def handle(self, *args, **opts):
        if opts["recarregar"]:
            contagem = limpar_demo()
            self.stdout.write("Demonstração anterior removida: " + ", ".join(f"{v} {k}" for k, v in contagem.items()))
        rel = demo.carregar(se_vazio=opts["se_vazio"] and not opts["recarregar"])
        if rel is None:
            self.stdout.write("Já existem produtos; nada foi carregado.")
            return
        for e in rel.erros:
            self.stderr.write(self.style.ERROR(f"  linha {e['linha']} [{e['sku']}] {e['mensagem']}"))
        self.stdout.write(self.style.SUCCESS(rel.resumo()))
