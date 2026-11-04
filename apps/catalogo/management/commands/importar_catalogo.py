import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.catalogo.services.importacao import ErroPlanilha, importar


class Command(BaseCommand):
    help = "Importa/atualiza o catálogo a partir de uma planilha CSV ou XLSX (idempotente por SKU)."

    def add_arguments(self, parser):
        parser.add_argument("arquivo", help="Caminho do .csv ou .xlsx")
        parser.add_argument("--dry-run", action="store_true", help="Simula: valida e gera o relatório sem gravar")
        parser.add_argument("--imagens", help="Pasta base para imagens com caminho relativo na planilha")
        parser.add_argument("--demo", action="store_true", help="Marca o que for importado como demonstração")
        parser.add_argument("--sem-imagens", action="store_true", help="Não baixa/associa imagens")
        parser.add_argument("--relatorio", help="Salva o relatório completo em JSON neste caminho")

    def handle(self, *args, **opts):
        arquivo = Path(opts["arquivo"])
        if not arquivo.is_file():
            raise CommandError(f"Arquivo não encontrado: {arquivo}")
        try:
            rel = importar(
                arquivo,
                dry_run=opts["dry_run"],
                pasta_imagens=opts["imagens"],
                demo=opts["demo"],
                baixar_imagens=not opts["sem_imagens"],
            )
        except ErroPlanilha as erro:
            raise CommandError(str(erro)) from erro
        for e in rel.erros:
            self.stderr.write(self.style.ERROR(f"  linha {e['linha'] or '-'} [{e['sku']}] {e['mensagem']}"))
        for a in rel.avisos:
            self.stdout.write(self.style.WARNING(f"  aviso linha {a['linha'] or '-'} [{a['sku']}] {a['mensagem']}"))
        estilo = self.style.SUCCESS if rel.ok else self.style.WARNING
        self.stdout.write(estilo(rel.resumo()))
        if opts["relatorio"]:
            Path(opts["relatorio"]).write_text(json.dumps(rel.as_dict(), ensure_ascii=False, indent=2))
