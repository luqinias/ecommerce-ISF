from django.core.management.base import BaseCommand

from apps.catalogo.services import demo


class Command(BaseCommand):
    help = "Carrega o catálogo fictício de demonstração (docs/exemplos/catalogo-demo.csv) com imagens geradas."

    def add_arguments(self, parser):
        parser.add_argument("--se-vazio", action="store_true", help="Só carrega se não houver nenhum produto")

    def handle(self, *args, **opts):
        rel = demo.carregar(se_vazio=opts["se_vazio"])
        if rel is None:
            self.stdout.write("Já existem produtos; nada foi carregado.")
            return
        for e in rel.erros:
            self.stderr.write(self.style.ERROR(f"  linha {e['linha']} [{e['sku']}] {e['mensagem']}"))
        self.stdout.write(self.style.SUCCESS(rel.resumo()))
