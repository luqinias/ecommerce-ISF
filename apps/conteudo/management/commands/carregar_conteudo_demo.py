from django.core.management.base import BaseCommand

from apps.conteudo import demo


class Command(BaseCommand):
    help = "Cria o conteúdo de demonstração da home e das páginas institucionais (sem depoimentos inventados)."

    def add_arguments(self, parser):
        parser.add_argument("--se-vazio", action="store_true", help="Só cria se ainda não houver conteúdo")
        parser.add_argument(
            "--recarregar",
            action="store_true",
            help="Apaga o conteúdo de demonstração (e as listas da home: provas, passos, diferenciais, FAQ) e cria de novo",
        )

    def handle(self, *args, **opts):
        if demo.carregar(se_vazio=opts["se_vazio"], recarregar=opts["recarregar"]):
            self.stdout.write(self.style.SUCCESS("Conteúdo de demonstração criado."))
        else:
            self.stdout.write("Já existe conteúdo; nada foi criado.")
