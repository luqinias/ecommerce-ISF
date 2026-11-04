"""Importação de catálogo a partir de CSV ou XLSX (idempotente por SKU).

Formato documentado em docs/importacao-catalogo.md. Resumo:
- aba `produtos` (ou o CSV): uma linha por variação, ou por produto sem variação;
- colunas `attr:<chave> [unidade]` (ficha técnica) e `var:<chave> [unidade]` (gera variação);
- abas opcionais (XLSX) `categorias` e `atributos` para controlar árvore e definição dos atributos.

O mesmo código roda em simulação (`dry_run=True`): tudo é feito dentro de uma transação
que é desfeita no fim, então o relatório é idêntico ao da importação real.
"""

from __future__ import annotations

import csv
import io
import re
import unicodedata
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from apps.catalogo import schema as schema_attrs
from apps.catalogo.choices import ImageKind, SaleUnit
from apps.catalogo.models import Category, Collection, Product, ProductImage, Variant
from apps.catalogo.services.imagens import ImagemInvalida, obter_imagem

OBRIGATORIAS = ("sku_produto", "nome", "categoria")
SEPARADOR = "|"
UNIDADES = {
    "peca": SaleUnit.PIECE, "peça": SaleUnit.PIECE, "pç": SaleUnit.PIECE, "pc": SaleUnit.PIECE, "unidade": SaleUnit.PIECE,
    "un": SaleUnit.PIECE, "piece": SaleUnit.PIECE,
    "metro": SaleUnit.METER, "m": SaleUnit.METER, "meter": SaleUnit.METER,
    "rolo": SaleUnit.ROLL, "roll": SaleUnit.ROLL,
    "kit": SaleUnit.KIT,
    "caixa": SaleUnit.BOX, "cx": SaleUnit.BOX, "box": SaleUnit.BOX,
}  # fmt: skip
VERDADEIRO = {"sim", "s", "true", "1", "x", "yes", "verdadeiro"}
FALSO = {"não", "nao", "n", "false", "0", "no", "falso", ""}
COLUNA_ATRIBUTO = re.compile(r"^(attr|var):\s*([^\[]+?)\s*(?:\[(.+)\])?\s*$", re.IGNORECASE)


class ErroPlanilha(Exception):
    """Erro que impede a importação inteira (formato, colunas obrigatórias)."""


class ErroLinha(Exception):
    pass


@dataclass
class Relatorio:
    dry_run: bool = False
    linhas: int = 0
    criados: Counter = field(default_factory=Counter)
    atualizados: Counter = field(default_factory=Counter)
    erros: list[dict] = field(default_factory=list)
    avisos: list[dict] = field(default_factory=list)

    def erro(self, linha: int | None, sku: str, mensagem: str) -> None:
        self.erros.append({"linha": linha, "sku": sku, "mensagem": mensagem})

    def aviso(self, linha: int | None, sku: str, mensagem: str) -> None:
        self.avisos.append({"linha": linha, "sku": sku, "mensagem": mensagem})

    @property
    def ok(self) -> bool:
        return not self.erros

    def resumo(self) -> str:
        def fmt(c: Counter) -> str:
            return ", ".join(f"{v} {k}" for k, v in sorted(c.items())) or "nada"

        prefixo = "SIMULAÇÃO — " if self.dry_run else ""
        return (
            f"{prefixo}{self.linhas} linhas · criados: {fmt(self.criados)} · atualizados: {fmt(self.atualizados)} · "
            f"{len(self.erros)} erro(s) · {len(self.avisos)} aviso(s)"
        )

    def as_dict(self) -> dict:
        return {
            "dry_run": self.dry_run,
            "linhas": self.linhas,
            "criados": dict(self.criados),
            "atualizados": dict(self.atualizados),
            "erros": self.erros,
            "avisos": self.avisos,
            "resumo": self.resumo(),
        }


# ---------------------------------------------------------------- leitura


def _normalizar_cabecalho(nome: Any) -> str:
    texto = str(nome or "").strip()
    if COLUNA_ATRIBUTO.match(texto):
        return texto
    texto = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto).strip("_")


def _linhas(cabecalho: list, registros, inicio: int = 2) -> list[dict]:
    chaves = [_normalizar_cabecalho(c) for c in cabecalho]
    saida = []
    for n, valores in enumerate(registros, start=inicio):
        valores = list(valores) + [None] * (len(chaves) - len(valores))
        linha = {k: v for k, v in zip(chaves, valores, strict=False) if k}
        if any(v not in (None, "") for v in linha.values()):
            linha["_linha"] = n
            saida.append(linha)
    return saida


def ler_planilha(arquivo, nome: str | None = None) -> dict[str, list[dict]]:
    """Lê CSV ou XLSX (caminho, bytes ou arquivo aberto). Retorna {aba: [linhas]}."""
    if isinstance(arquivo, str | Path):
        nome = nome or str(arquivo)
        dados = Path(arquivo).read_bytes()
    elif isinstance(arquivo, bytes):
        dados = arquivo
    else:
        nome = nome or getattr(arquivo, "name", "")
        arquivo.seek(0)
        dados = arquivo.read()
    extensao = Path(nome or "").suffix.lower()
    if extensao in (".xlsx", ".xlsm"):
        return _ler_xlsx(dados)
    if extensao in (".csv", ".txt", ""):
        return {"produtos": _ler_csv(dados)}
    raise ErroPlanilha(f"Formato não suportado: {extensao}. Use .csv ou .xlsx.")


def _ler_csv(dados: bytes) -> list[dict]:
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            texto = dados.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ErroPlanilha("Não foi possível ler o CSV (codificação desconhecida).")
    # O delimitador é o mais frequente no cabeçalho (o Sniffer erra com descrições cheias de vírgulas).
    cabecalho_bruto = texto.split("\n", 1)[0]
    delimitador = max((";", ",", "\t"), key=cabecalho_bruto.count)
    leitor = csv.reader(io.StringIO(texto), delimiter=delimitador)
    try:
        cabecalho = next(leitor)
    except StopIteration as erro:
        raise ErroPlanilha("Planilha vazia.") from erro
    return _linhas(cabecalho, leitor)


def _ler_xlsx(dados: bytes) -> dict[str, list[dict]]:
    from openpyxl import load_workbook

    try:
        livro = load_workbook(io.BytesIO(dados), read_only=True, data_only=True)
    except Exception as erro:
        raise ErroPlanilha(f"Não foi possível abrir o XLSX: {erro}") from erro
    abas = {_normalizar_cabecalho(n): livro[n] for n in livro.sheetnames}
    saida = {}
    for chave, aba in abas.items():
        linhas = aba.iter_rows(values_only=True)
        try:
            cabecalho = next(linhas)
        except StopIteration:
            continue
        saida[chave] = _linhas(list(cabecalho), linhas)
    if "produtos" not in saida:
        primeira = _normalizar_cabecalho(livro.sheetnames[0])
        saida["produtos"] = saida.get(primeira, [])
    livro.close()
    return saida


# ---------------------------------------------------------------- conversões


def _texto(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def _booleano(valor: Any, padrao: bool) -> bool:
    if valor is None:
        return padrao
    if isinstance(valor, bool):
        return valor
    texto = _texto(valor).lower()
    if texto in VERDADEIRO:
        return True
    if texto in FALSO:
        return False
    raise ErroLinha(f"valor sim/não inválido: {valor!r}")


def _inteiro(valor: Any, campo: str) -> int | None:
    if valor in (None, ""):
        return None
    try:
        numero = float(str(valor).replace(",", "."))
    except ValueError as erro:
        raise ErroLinha(f"{campo}: número inválido ({valor!r})") from erro
    if not numero.is_integer() or numero < 0:
        raise ErroLinha(f"{campo}: use um número inteiro positivo ({valor!r})")
    return int(numero)


def _data(valor: Any, campo: str) -> date | None:
    if valor in (None, ""):
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = _texto(valor)
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ErroLinha(f"{campo}: data inválida ({valor!r}); use AAAA-MM-DD ou DD/MM/AAAA")


def _unidade(valor: Any) -> str | None:
    texto = _texto(valor).lower()
    if not texto:
        return None
    if texto not in UNIDADES:
        opcoes = ", ".join(sorted({str(u.label) for u in SaleUnit}))
        raise ErroLinha(f"unidade_venda desconhecida: {valor!r} (use: {opcoes})")
    return UNIDADES[texto]


def _lista(valor: Any) -> list[str]:
    return [p.strip() for p in _texto(valor).split(SEPARADOR) if p.strip()]


def _chave(texto: str) -> str:
    chave = slugify(texto).replace("-", "_")
    if not chave or not chave[0].isalpha():
        chave = f"a_{chave}"
    return chave[:40]


def _humanizar(chave: str) -> str:
    return chave.replace("_", " ").strip().capitalize()


# ---------------------------------------------------------------- importador


class Importador:
    def __init__(self, relatorio: Relatorio, *, pasta_imagens: Path | None, demo: bool, baixar_imagens: bool):
        self.r = relatorio
        self.pasta = pasta_imagens
        self.demo = demo
        self.baixar = baixar_imagens and not relatorio.dry_run
        self.cache_categorias: dict[str, Category] = {}
        self.cache_colecoes: dict[str, Collection] = {}
        self.colunas_attr: dict[str, dict] = {}

    # ----- categorias e coleções
    def categoria(self, caminho: str, linha: int | None = None) -> Category:
        caminho = " > ".join(p.strip() for p in caminho.split(">") if p.strip())
        if not caminho:
            raise ErroLinha("categoria vazia")
        if caminho in self.cache_categorias:
            return self.cache_categorias[caminho]
        partes = caminho.split(" > ")
        if len(partes) > 2:
            raise ErroLinha(f"categoria com mais de 2 níveis: {caminho}")
        pai = None
        for parte in partes:
            qs = Category.objects.filter(parent=pai)
            atual = qs.filter(name__iexact=parte).first() or qs.filter(slug=slugify(parte)).first()
            if atual is None:
                if pai is None and Category.objects.filter(slug=slugify(parte)).exists():
                    atual = Category.objects.get(slug=slugify(parte))
                else:
                    atual = Category(name=parte, parent=pai, is_demo=self.demo)
                    atual.save()
                    self.r.criados["categorias"] += 1
                    self.r.aviso(linha, "", f"categoria criada: {atual}")
            pai = atual
        self.cache_categorias[caminho] = pai
        return pai

    def colecao(self, nome: str) -> Collection:
        if nome in self.cache_colecoes:
            return self.cache_colecoes[nome]
        col = (
            Collection.objects.filter(name__iexact=nome).first()
            or Collection.objects.filter(slug=slugify(nome)).first()
        )
        if col is None:
            col = Collection(name=nome, is_demo=self.demo)
            col.save()
            self.r.criados["coleções"] += 1
        self.cache_colecoes[nome] = col
        return col

    def processar_aba_categorias(self, linhas: list[dict]) -> None:
        for linha in linhas:
            n = linha["_linha"]
            nome = _texto(linha.get("categoria") or linha.get("nome"))
            pai = _texto(linha.get("pai"))
            try:
                with transaction.atomic():
                    cat = self.categoria(f"{pai} > {nome}" if pai else nome, n)
                    for campo, coluna in (("description", "descricao"), ("seo_text", "texto_seo"), ("icon", "icone"),
                                          ("meta_title", "meta_titulo"), ("meta_description", "meta_descricao")):  # fmt: skip
                        if coluna in linha:
                            setattr(cat, campo, _texto(linha[coluna]))
                    if "ordem" in linha:
                        cat.order = _inteiro(linha["ordem"], "ordem") or 0
                    if "home" in linha:
                        cat.show_on_home = _booleano(linha["home"], False)
                    if "ativo" in linha:
                        cat.active = _booleano(linha["ativo"], True)
                    cat.save()
                    self.r.atualizados["categorias"] += 1
            except (ErroLinha, ValidationError) as erro:
                self.r.erro(n, nome, f"[categorias] {_mensagem(erro)}")

    def processar_aba_atributos(self, linhas: list[dict]) -> None:
        por_categoria: dict[int, list[dict]] = OrderedDict()
        objetos: dict[int, Category] = {}
        for linha in linhas:
            n = linha["_linha"]
            try:
                cat = self.categoria(_texto(linha.get("categoria")), n)
                chave = _chave(_texto(linha.get("chave")) or _texto(linha.get("rotulo")))
                tipo = _texto(linha.get("tipo")).lower() or "text"
                tipos = {"texto": "text", "numero": "number", "número": "number", "sim/nao": "boolean",
                         "sim/não": "boolean", "opcoes": "choice", "opções": "choice", "lista": "choice"}  # fmt: skip
                tipo = tipos.get(tipo, tipo)
                attr = {"key": chave, "label": _texto(linha.get("rotulo")) or _humanizar(chave), "type": tipo}
                if _texto(linha.get("unidade")):
                    attr["unit"] = _texto(linha.get("unidade"))
                if _booleano(linha.get("gera_variacao"), False):
                    attr["variant"] = True
                if _booleano(linha.get("obrigatorio"), False):
                    attr["required"] = True
                if _texto(linha.get("ajuda")):
                    attr["help"] = _texto(linha.get("ajuda"))
                if tipo == "choice":
                    opcoes = _lista(linha.get("opcoes"))
                    attr["choices"] = [schema_attrs.converter_valor(o, {"type": "number"}) if _numerico(o) else o
                                       for o in opcoes]  # fmt: skip
                por_categoria.setdefault(cat.pk, []).append(attr)
                objetos[cat.pk] = cat
            except ErroLinha as erro:
                self.r.erro(n, "", f"[atributos] {erro}")
        for pk, atributos in por_categoria.items():
            cat = objetos[pk]
            cat.attribute_schema = schema_attrs.combinar(cat.attribute_schema, atributos)
            try:
                cat.save()
                self.r.atualizados["definições de atributos"] += 1
            except ValidationError as erro:
                self.r.erro(None, cat.name, f"[atributos] {_mensagem(erro)}")

    # ----- produtos
    def mapear_colunas(self, linhas: list[dict]) -> None:
        colunas = list(OrderedDict.fromkeys(k for linha in linhas for k in linha if not k.startswith("_")))
        for coluna in colunas:
            m = COLUNA_ATRIBUTO.match(coluna)
            if not m:
                continue
            prefixo, nome, unidade = m.group(1).lower(), m.group(2).strip(), (m.group(3) or "").strip()
            valores = [linha.get(coluna) for linha in linhas if linha.get(coluna) not in (None, "")]
            tipo = "text"
            if valores and all(isinstance(v, bool) or _texto(v).lower() in VERDADEIRO | FALSO - {""} for v in valores):
                tipo = "boolean"
            elif valores and sum(_numerico(v) for v in valores) / len(valores) > 0.5:
                # maioria numérica: é número; os valores fora do padrão viram erro na linha
                tipo = "number"
            self.colunas_attr[coluna] = {
                "key": _chave(nome),
                "label": nome if nome != _chave(nome) else _humanizar(nome),
                "unit": unidade,
                "variant": prefixo == "var",
                "type": tipo,
            }

    def garantir_atributo(self, categoria: Category, info: dict, linha: int) -> dict:
        """Devolve a definição do atributo; se a categoria não o conhece, estende a definição dela."""
        for attr in categoria.effective_schema:
            if attr["key"] == info["key"]:
                if bool(attr.get("variant")) != info["variant"]:
                    tipo = "de variação (var:)" if attr.get("variant") else "de ficha (attr:)"
                    raise ErroLinha(f"o atributo '{info['key']}' é {tipo} na categoria {categoria}")
                return attr
        novo = {"key": info["key"], "label": info["label"], "type": info["type"]}
        if info["unit"]:
            novo["unit"] = info["unit"]
        if info["variant"]:
            novo["variant"] = True
        categoria.attribute_schema = [*categoria.attribute_schema, novo]
        categoria.save()
        self.r.aviso(linha, "", f"atributo '{novo['key']}' adicionado à categoria {categoria}")
        return novo

    def importar_produto(self, sku: str, linhas: list[dict]) -> None:
        primeira = linhas[0]
        n = primeira["_linha"]
        produto = Product.objects.filter(sku=sku).first()
        novo = produto is None
        if novo:
            produto = Product(sku=sku, is_demo=self.demo)
        nome = _texto(primeira.get("nome"))
        if not nome and novo:
            raise ErroLinha("nome é obrigatório")
        if nome:
            produto.name = nome
        categoria = self.categoria(_texto(primeira.get("categoria")), n) if _texto(primeira.get("categoria")) else None
        if categoria is None and novo:
            raise ErroLinha("categoria é obrigatória")
        if categoria:
            produto.primary_category = categoria
        textos = (("slug", "slug"), ("short_description", "descricao_curta"), ("description", "descricao"),
                  ("meta_title", "meta_titulo"), ("meta_description", "meta_descricao"))  # fmt: skip
        for campo, coluna in textos:
            if coluna in primeira and (_texto(primeira[coluna]) or campo != "slug"):
                setattr(produto, campo, _texto(primeira[coluna]).replace("\\n", "\n"))
        if "quantidade_minima" in primeira:
            produto.min_quantity = _inteiro(primeira["quantidade_minima"], "quantidade_minima") or 1
        if "multiplo" in primeira:
            produto.quantity_step = _inteiro(primeira["multiplo"], "multiplo") or 1
        if "unidade_venda" in primeira and _unidade(primeira["unidade_venda"]):
            produto.sale_unit = _unidade(primeira["unidade_venda"])
        if "destaque" in primeira:
            produto.featured = _booleano(primeira["destaque"], False)
        if "ativo" in primeira:
            produto.active = _booleano(primeira["ativo"], True)
        if "novidade_ate" in primeira:
            produto.new_until = _data(primeira["novidade_ate"], "novidade_ate")
        if "relevancia" in primeira:
            produto.relevance = _inteiro(primeira["relevancia"], "relevancia") or 0
        if self.demo:
            produto.is_demo = True

        # atributos de ficha (attr:) — da primeira linha do produto
        atributos = dict(produto.attributes or {})
        for coluna, info in self.colunas_attr.items():
            if info["variant"] or coluna not in primeira:
                continue
            valor = primeira.get(coluna)
            if valor in (None, ""):
                atributos.pop(info["key"], None)
                continue
            attr = self.garantir_atributo(produto.primary_category, info, n)
            atributos[info["key"]] = schema_attrs.converter_valor(valor, attr)
        produto.attributes = atributos
        produto.save()
        self.r.criados["produtos"] += novo
        self.r.atualizados["produtos"] += not novo

        # categorias extras e coleções
        if "categorias_extras" in primeira:
            extras = [self.categoria(c, n) for c in _lista(primeira["categorias_extras"])]
            produto.categories.set([produto.primary_category, *extras])
        else:
            produto.ensure_primary_in_categories()
        if "colecoes" in primeira:
            produto.collections.set([self.colecao(c) for c in _lista(primeira["colecoes"])])

        if "imagens" in primeira:
            self.importar_imagens(produto, _lista(primeira["imagens"]), n)

        for linha in linhas:
            if _texto(linha.get("sku_variacao")):
                self.importar_variacao(produto, linha)
            elif linha is not primeira and any(
                self.colunas_attr[c]["variant"] for c in linha if c in self.colunas_attr
            ):
                raise ErroLinha(f"linha {linha['_linha']}: atributos de variação sem sku_variacao")
        if produto.variant_attributes and not produto.variants.exists():
            self.r.aviso(n, sku, "categoria tem atributos de variação, mas o produto não tem variações")

    def importar_variacao(self, produto: Product, linha: dict) -> None:
        n = linha["_linha"]
        sku = _texto(linha["sku_variacao"])
        variacao = Variant.objects.filter(sku=sku).select_related("product").first()
        if variacao and variacao.product_id != produto.pk:
            raise ErroLinha(f"linha {n}: sku_variacao {sku} já pertence ao produto {variacao.product.sku}")
        novo = variacao is None
        variacao = variacao or Variant(product=produto, sku=sku)
        atributos = {}
        for coluna, info in self.colunas_attr.items():
            if not info["variant"]:
                continue
            valor = linha.get(coluna)
            if valor in (None, ""):
                continue
            attr = self.garantir_atributo(produto.primary_category, info, n)
            atributos[info["key"]] = schema_attrs.converter_valor(valor, attr)
        variacao.attributes = atributos
        if "ativo_variacao" in linha:
            variacao.active = _booleano(linha["ativo_variacao"], True)
        if "ordem_variacao" in linha:
            variacao.order = _inteiro(linha["ordem_variacao"], "ordem_variacao") or 0
        if _texto(linha.get("imagem_variacao")):
            imagens = self.importar_imagens(produto, [_texto(linha["imagem_variacao"])], n, anexar=True)
            variacao.image = imagens[0] if imagens else None
        produto.__dict__.pop("schema", None)  # a definição pode ter sido estendida
        try:
            variacao.save()
        except ValidationError as erro:
            raise ErroLinha(f"linha {n} (variação {sku}): {_mensagem(erro)}") from erro
        self.r.criados["variações"] += novo
        self.r.atualizados["variações"] += not novo

    def importar_imagens(self, produto: Product, origens: list[str], linha: int, anexar: bool = False) -> list:
        resultado = []
        existentes = {img.source: img for img in produto.images.all()}
        proxima_ordem = max([img.order for img in existentes.values()], default=-1) + 1
        for posicao, origem in enumerate(origens):
            tipo = ImageKind.PRODUCT
            if origem.lower().startswith(("ambiente:", "campo:")):
                tipo = ImageKind.ENVIRONMENT
                origem = origem.split(":", 1)[1].strip()
            if origem in existentes:
                img = existentes[origem]
                if not anexar and (img.order != posicao or img.kind != tipo):
                    img.order, img.kind = posicao, tipo
                    img.save(update_fields=["order", "kind"])
                resultado.append(img)
                continue
            if not self.baixar:
                if not origem.lower().startswith("http") and self.pasta and not (self.pasta / origem).is_file():
                    self.r.aviso(linha, produto.sku, f"imagem não encontrada: {origem}")
                else:
                    self.r.criados["imagens"] += 1
                continue
            try:
                nome, conteudo = obter_imagem(origem, self.pasta)
            except ImagemInvalida as erro:
                self.r.aviso(linha, produto.sku, str(erro))
                continue
            img = ProductImage(product=produto, kind=tipo, order=proxima_ordem if anexar else posicao, source=origem)
            img.image.save(nome, conteudo, save=False)
            img.save()
            existentes[origem] = img
            proxima_ordem += 1
            self.r.criados["imagens"] += 1
            resultado.append(img)
        return resultado


def _numerico(valor: Any) -> bool:
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int | float):
        return True
    texto = _texto(valor).replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        float(texto)
    except ValueError:
        return False
    return True


def _mensagem(erro: Exception) -> str:
    if isinstance(erro, ValidationError):
        if hasattr(erro, "message_dict"):
            partes = []
            for campo, msgs in erro.message_dict.items():
                rotulo = "" if campo == "__all__" else f"{campo}: "
                partes.extend(f"{rotulo}{m}" for m in msgs)
            return "; ".join(partes)
        return "; ".join(erro.messages)
    return str(erro)


def importar(
    arquivo,
    *,
    nome: str | None = None,
    dry_run: bool = False,
    pasta_imagens: Path | str | None = None,
    demo: bool = False,
    baixar_imagens: bool = True,
) -> Relatorio:
    """Importa a planilha. Nunca levanta erro de linha: tudo vai para o relatório.

    Levanta ErroPlanilha quando o arquivo inteiro é inválido (formato ou colunas obrigatórias).
    """
    relatorio = Relatorio(dry_run=dry_run)
    abas = ler_planilha(arquivo, nome)
    produtos = abas.get("produtos", [])
    if not produtos:
        raise ErroPlanilha("A aba/arquivo de produtos está vazia.")
    faltando = [c for c in OBRIGATORIAS if not any(c in linha for linha in produtos)]
    if faltando:
        raise ErroPlanilha(f"Colunas obrigatórias ausentes: {', '.join(faltando)}")
    relatorio.linhas = len(produtos)
    pasta = Path(pasta_imagens) if pasta_imagens else None
    imp = Importador(relatorio, pasta_imagens=pasta, demo=demo, baixar_imagens=baixar_imagens)

    with transaction.atomic():
        if abas.get("categorias"):
            imp.processar_aba_categorias(abas["categorias"])
        if abas.get("atributos"):
            imp.processar_aba_atributos(abas["atributos"])
        imp.mapear_colunas(produtos)
        grupos: OrderedDict[str, list[dict]] = OrderedDict()
        for linha in produtos:
            sku = _texto(linha.get("sku_produto"))
            if not sku:
                relatorio.erro(linha["_linha"], "", "sku_produto é obrigatório")
                continue
            grupos.setdefault(sku, []).append(linha)
        for sku, linhas in grupos.items():
            try:
                with transaction.atomic():
                    imp.importar_produto(sku, linhas)
            except (ErroLinha, ValidationError) as erro:
                relatorio.erro(linhas[0]["_linha"], sku, _mensagem(erro))
        if dry_run:
            transaction.set_rollback(True)
    return relatorio


@transaction.atomic
def limpar_demo() -> dict[str, int]:
    """Remove só o que é demonstração. Categorias/coleções de demo com produtos reais ficam (e viram reais)."""
    produtos = Product.objects.filter(is_demo=True)
    imagens = [img for p in produtos.prefetch_related("images") for img in p.images.all()]
    contagem = {"produtos": produtos.count()}
    for img in imagens:
        for campo in (img.image, img.card, img.large):
            if campo:
                campo.delete(save=False)
    produtos.delete()
    filhas = Category.objects.filter(is_demo=True, parent__isnull=False)
    raizes = Category.objects.filter(is_demo=True, parent__isnull=True)
    contagem["categorias"] = 0
    for grupo in (filhas, raizes):
        for cat in grupo:
            if cat.primary_products.exists() or cat.children.exists():
                Category.objects.filter(pk=cat.pk).update(is_demo=False)
            else:
                cat.delete()
                contagem["categorias"] += 1
    colecoes = Collection.objects.filter(is_demo=True)
    contagem["coleções"] = 0
    for col in colecoes:
        if col.products.exists():
            Collection.objects.filter(pk=col.pk).update(is_demo=False)
        else:
            col.delete()
            contagem["coleções"] += 1
    return contagem
