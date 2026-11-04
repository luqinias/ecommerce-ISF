import io

import pytest
from openpyxl import Workbook

from apps.catalogo.models import Category, Collection, Product, ProductImage, Variant
from apps.catalogo.services.importacao import ErroPlanilha, importar, limpar_demo
from tests.factories import ProductFactory, png

pytestmark = pytest.mark.django_db

CSV = """sku_produto;nome;categoria;colecoes;quantidade_minima;multiplo;unidade_venda;destaque;sku_variacao;attr:Material;attr:Autocompensante;var:Vazão [L/h]
GOT-1;Gotejador A;Gotejamento;Lançamentos;100;100;peça;sim;GOT-1-2;PE;sim;2
GOT-1;Gotejador A;Gotejamento;Lançamentos;100;100;peça;sim;GOT-1-4;PE;sim;4
FIT-1;Fita 16 mm;Gotejamento > Fitas;;1;1;rolo;não;FIT-1-16;PE;não;1,6
"""


def arquivo(texto: str, nome="cat.csv"):
    f = io.BytesIO(texto.encode("utf-8"))
    f.name = nome
    return f


def test_importa_csv_cria_tudo():
    rel = importar(arquivo(CSV))
    assert rel.ok, rel.erros
    assert Product.objects.count() == 2 and Variant.objects.count() == 3
    fitas = Category.objects.get(name="Fitas")
    assert fitas.parent.name == "Gotejamento"
    got = Category.objects.get(name="Gotejamento")
    vazao = next(a for a in got.attribute_schema if a["key"] == "vazao")
    assert vazao == {"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True}
    p = Product.objects.get(sku="GOT-1")
    assert p.attributes == {"material": "PE", "autocompensante": True}
    assert p.min_quantity == 100 and p.sale_unit == "piece" and p.featured
    assert list(p.collections.values_list("name", flat=True)) == ["Lançamentos"]
    assert Variant.objects.get(sku="FIT-1-16").attributes == {"vazao": 1.6}
    assert Product.objects.get(sku="FIT-1").sale_unit == "roll"


def test_dry_run_nao_grava_e_relata_igual():
    simulado = importar(arquivo(CSV), dry_run=True)
    assert Product.objects.count() == 0 and Category.objects.count() == 0 and Collection.objects.count() == 0
    real = importar(arquivo(CSV))
    assert simulado.criados == real.criados


def test_reimportar_e_idempotente():
    importar(arquivo(CSV))
    rel = importar(arquivo(CSV.replace("Gotejador A", "Gotejador A2")))
    assert rel.criados.get("produtos", 0) == 0 and rel.criados.get("variações", 0) == 0
    assert rel.atualizados["produtos"] == 2
    assert Product.objects.get(sku="GOT-1").name == "Gotejador A2"
    assert Product.objects.count() == 2 and Variant.objects.count() == 3


def test_erros_por_linha_nao_impedem_as_validas():
    ruim = CSV + "X-1;;Gotejamento;;;;;;;;;\nX-2;Ruim;Gotejamento;;;;caixote;;;;;\n;Sem sku;Gotejamento;;;;;;;;;\n"
    rel = importar(arquivo(ruim))
    linhas = {e["linha"]: e["mensagem"] for e in rel.erros}
    assert "nome é obrigatório" in linhas[5]
    assert "unidade_venda" in linhas[6]
    assert "sku_produto" in linhas[7]
    assert Product.objects.count() == 2


def test_variacao_com_valor_invalido_derruba_so_o_produto():
    texto = CSV + "Z-1;Zé;Gotejamento;;1;1;peça;;Z-1-A;PE;sim;muito\n"
    rel = importar(arquivo(texto))
    assert any(e["sku"] == "Z-1" for e in rel.erros)
    assert not Product.objects.filter(sku="Z-1").exists()
    assert Product.objects.count() == 2


def test_sku_de_variacao_de_outro_produto():
    importar(arquivo(CSV))
    texto = "sku_produto;nome;categoria;sku_variacao;var:Vazão [L/h]\nNOVO;Novo;Gotejamento;GOT-1-2;2\n"
    rel = importar(arquivo(texto))
    assert "já pertence" in rel.erros[0]["mensagem"]


def test_colunas_obrigatorias():
    with pytest.raises(ErroPlanilha):
        importar(arquivo("sku_produto;nome\nA;B\n"))
    with pytest.raises(ErroPlanilha):
        importar(arquivo("a,b", nome="x.pdf"))


def test_xlsx_com_abas_de_categorias_e_atributos():
    wb = Workbook()
    ws = wb.active
    ws.title = "produtos"
    ws.append(["sku_produto", "nome", "categoria", "attr:material", "sku_variacao", "var:diametro"])
    ws.append(["TUB-1", "Tubo PE", "Tubos", "PEBD", "TUB-1-16", 16])
    ws.append(["TUB-1", "Tubo PE", "Tubos", "PEBD", "TUB-1-20", 20])
    cats = wb.create_sheet("categorias")
    cats.append(["categoria", "pai", "descricao", "ordem", "icone", "home"])
    cats.append(["Tubos", "", "Tubos e mangueiras", 3, "layers", "sim"])
    attrs = wb.create_sheet("atributos")
    attrs.append(["categoria", "chave", "rotulo", "tipo", "unidade", "gera_variacao", "obrigatorio", "opcoes"])
    attrs.append(["Tubos", "material", "Material", "opções", "", "não", "sim", "PEBD|PEAD"])
    attrs.append(["Tubos", "diametro", "Diâmetro", "opções", "mm", "sim", "", "16|20|25"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.name = "cat.xlsx"
    rel = importar(buf)
    assert rel.ok, rel.erros
    tubos = Category.objects.get(name="Tubos")
    assert tubos.show_on_home and tubos.order == 3 and tubos.icon == "layers"
    diam = next(a for a in tubos.attribute_schema if a["key"] == "diametro")
    assert diam["choices"] == [16, 20, 25] and diam["variant"]
    assert sorted(Variant.objects.values_list("attributes__diametro", flat=True)) == [16, 20]


def test_imagens_locais_e_idempotentes(tmp_path):
    (tmp_path / "a.png").write_bytes(png().read())
    (tmp_path / "b.png").write_bytes(png((200, 10, 10)).read())
    texto = "sku_produto;nome;categoria;imagens\nK-1;Kit;Kits;a.png|ambiente:b.png|nao-existe.png\n"
    rel = importar(arquivo(texto), pasta_imagens=tmp_path)
    assert ProductImage.objects.count() == 2
    assert ProductImage.objects.get(source="b.png").kind == "environment"
    assert any("não encontrado" in a["mensagem"] for a in rel.avisos)
    importar(arquivo(texto), pasta_imagens=tmp_path)
    assert ProductImage.objects.count() == 2


def test_caminho_de_imagem_fora_da_pasta(tmp_path):
    texto = "sku_produto;nome;categoria;imagens\nK-1;Kit;Kits;../../etc/passwd\n"
    rel = importar(arquivo(texto), pasta_imagens=tmp_path)
    assert any("fora da pasta" in a["mensagem"] for a in rel.avisos)


def test_atributo_de_ficha_vs_variacao_conflitante():
    importar(arquivo(CSV))
    texto = "sku_produto;nome;categoria;attr:Vazão\nP-9;P;Gotejamento;2\n"
    rel = importar(arquivo(texto))
    assert "de variação" in rel.erros[0]["mensagem"]


def test_limpar_demo_remove_so_demonstracao():
    importar(arquivo(CSV), demo=True)
    real = ProductFactory(name="Real", primary_category=Category.objects.get(name="Fitas"))
    contagem = limpar_demo()
    assert list(Product.objects.all()) == [real]
    assert contagem["produtos"] == 2
    assert Category.objects.filter(name="Fitas").exists()  # tem produto real: fica
    assert not Collection.objects.exists()
