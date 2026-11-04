"""Gera docs/exemplos/modelo-catalogo.xlsx e .csv (planilha-modelo da importação).

Uso: uv run python tools/gerar_modelo_planilha.py
"""

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "exemplos"

PRODUTOS = [
    ["sku_produto", "nome", "categoria", "categorias_extras", "colecoes", "descricao_curta", "descricao",
     "quantidade_minima", "multiplo", "unidade_venda", "destaque", "novidade_ate", "relevancia", "imagens",
     "sku_variacao", "imagem_variacao", "attr:Material", "attr:Autocompensante", "attr:Pressão máxima [bar]",
     "var:Vazão [L/h]"],
    ["EX-GOT-01", "Gotejador autocompensante (exemplo)", "Gotejamento", "", "Lançamentos",
     "Texto curto que aparece no card e abaixo do nome.", "Parágrafo 1.\\n\\nParágrafo 2.",
     100, 100, "peça", "sim", "2027-06-30", 90,
     "https://exemplo.com/fotos/gotejador.jpg|ambiente:https://exemplo.com/fotos/gotejador-campo.jpg",
     "EX-GOT-01-2", "", "PE", "sim", 3.5, 2],
    ["EX-GOT-01", "", "", "", "", "", "", "", "", "", "", "", "", "", "EX-GOT-01-4",
     "https://exemplo.com/fotos/gotejador-4lh.jpg", "", "", "", 4],
    ["EX-KIT-01", "Kit horta (exemplo, sem variação)", "Kits", "Gotejamento", "", "Kit pronto.", "",
     1, 1, "kit", "não", "", 50, "kit-horta.jpg", "", "", "", "", "", ""],
]  # fmt: skip

CATEGORIAS = [
    ["categoria", "pai", "descricao", "texto_seo", "ordem", "icone", "home", "ativo"],
    ["Gotejamento", "", "Emissores e fitas para aplicar água na raiz.", "Texto longo para o fim da listagem.", 1, "droplet", "sim", "sim"],
    ["Fitas gotejadoras", "Gotejamento", "Fitas em rolo.", "", 1, "layers", "não", "sim"],
    ["Kits", "", "Conjuntos prontos.", "", 9, "truck", "sim", "sim"],
]  # fmt: skip

ATRIBUTOS = [
    ["categoria", "chave", "rotulo", "tipo", "unidade", "gera_variacao", "obrigatorio", "opcoes", "ajuda"],
    ["Gotejamento", "material", "Material", "opções", "", "não", "não", "PE|PP", ""],
    ["Gotejamento", "autocompensante", "Autocompensante", "sim/não", "", "não", "não", "", ""],
    ["Gotejamento", "pressao_maxima", "Pressão máxima", "número", "bar", "não", "sim", "", "Pressão de trabalho"],
    ["Gotejamento", "vazao", "Vazão", "número", "L/h", "sim", "", "", ""],
]  # fmt: skip

INSTRUCOES = [
    ["Importação do catálogo — instruções"],
    ["Documentação completa: docs/importacao-catalogo.md"],
    ["1. Uma linha por variação. Produto sem variação = uma linha, com sku_variacao vazio."],
    ["2. Linhas extras do mesmo produto só precisam de sku_produto, sku_variacao e as colunas var:."],
    ["3. Obrigatórias: sku_produto, nome e categoria (use 'Pai > Filha' para subcategoria)."],
    ["4. Listas (categorias_extras, colecoes, imagens) usam | como separador."],
    ["5. attr:<nome> [unidade] = ficha técnica; var:<nome> [unidade] = gera variação."],
    ["6. Abas 'categorias' e 'atributos' são opcionais: sem elas, categorias e atributos são criados automaticamente."],
    ["7. Rode primeiro em simulação: python manage.py importar_catalogo arquivo.xlsx --dry-run"],
]


def _aba(livro, titulo, linhas):
    aba = livro.create_sheet(titulo)
    for linha in linhas:
        aba.append(linha)
    for celula in aba[1]:
        celula.font = Font(bold=True, color="FFFFFF")
        celula.fill = PatternFill("solid", fgColor="1D6A44")
        celula.alignment = Alignment(vertical="center")
    for i, _ in enumerate(linhas[0], start=1):
        aba.column_dimensions[get_column_letter(i)].width = 22
    aba.freeze_panes = "A2"
    return aba


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    livro = Workbook()
    livro.remove(livro.active)
    _aba(livro, "produtos", PRODUTOS)
    _aba(livro, "categorias", CATEGORIAS)
    _aba(livro, "atributos", ATRIBUTOS)
    instr = livro.create_sheet("instrucoes")
    for linha in INSTRUCOES:
        instr.append(linha)
    instr["A1"].font = Font(bold=True, size=14)
    instr.column_dimensions["A"].width = 110
    livro.save(SAIDA / "modelo-catalogo.xlsx")
    with (SAIDA / "modelo-catalogo.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter=";").writerows(PRODUTOS)
    print("gerado em", SAIDA)


if __name__ == "__main__":
    main()
