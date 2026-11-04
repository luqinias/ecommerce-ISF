"""Lista de orçamento guardada na sessão (sem login). Os dados do produto são sempre lidos do banco."""

from __future__ import annotations

from dataclasses import dataclass

from apps.catalogo.models import Product, Variant

CHAVE_SESSAO = "lista_orcamento"


def normalizar_quantidade(produto: Product, quantidade) -> int:
    """Aplica o mínimo e arredonda para o múltiplo de venda a partir do mínimo."""
    try:
        q = int(quantidade)
    except (TypeError, ValueError):
        q = produto.min_quantity
    minimo, passo = produto.min_quantity, max(produto.quantity_step, 1)
    if q < minimo:
        return minimo
    return minimo + round((q - minimo) / passo) * passo


@dataclass
class Item:
    chave: str
    produto: Product
    variacao: Variant | None
    quantidade: int

    @property
    def sku(self) -> str:
        return self.variacao.sku if self.variacao else self.produto.sku

    @property
    def unidade(self) -> str:
        return self.produto.unit_label if self.quantidade == 1 else self.produto.unit_plural

    @property
    def rotulo_variacao(self) -> str:
        return self.variacao.label if self.variacao else ""


class ErroLista(Exception):
    pass


class ListaOrcamento:
    def __init__(self, request):
        self.session = request.session
        self.dados: dict[str, int] = dict(self.session.get(CHAVE_SESSAO, {}))
        self._itens: list[Item] | None = None
        self.removidos: list[str] = []

    @staticmethod
    def chave(produto_id: int, variacao_id: int | None) -> str:
        return f"{produto_id}:{variacao_id or 0}"

    def _salvar(self) -> None:
        self.session[CHAVE_SESSAO] = self.dados
        self.session.modified = True
        self._itens = None

    def __len__(self) -> int:
        return len(self.dados)

    def __bool__(self) -> bool:
        return bool(self.dados)

    def adicionar(self, produto: Product, variacao: Variant | None, quantidade) -> Item:
        tem_variacoes = produto.variants.filter(active=True).exists()
        if tem_variacoes and variacao is None:
            raise ErroLista("Escolha uma opção do produto antes de adicionar.")
        if variacao is not None and (variacao.product_id != produto.pk or not variacao.active):
            raise ErroLista("Opção inválida para este produto.")
        chave = self.chave(produto.pk, variacao.pk if variacao else None)
        atual = self.dados.get(chave, 0)
        q = normalizar_quantidade(produto, quantidade)
        self.dados[chave] = normalizar_quantidade(produto, atual + q) if atual else q
        self._salvar()
        return Item(chave, produto, variacao, self.dados[chave])

    def atualizar(self, chave: str, quantidade) -> None:
        if chave not in self.dados:
            return
        item = next((i for i in self.itens() if i.chave == chave), None)
        if item:
            self.dados[chave] = normalizar_quantidade(item.produto, quantidade)
            self._salvar()

    def remover(self, chave: str) -> None:
        if self.dados.pop(chave, None) is not None:
            self._salvar()

    def limpar(self) -> None:
        self.dados = {}
        self._salvar()

    def itens(self) -> list[Item]:
        """Itens válidos, na ordem de inclusão. Produtos inativos saem da lista."""
        if self._itens is not None:
            return self._itens
        ids_p, ids_v = set(), set()
        for chave in self.dados:
            p, v = chave.split(":")
            ids_p.add(int(p))
            if int(v):
                ids_v.add(int(v))
        produtos = {
            p.pk: p
            for p in Product.objects.active()
            .filter(pk__in=ids_p)
            .select_related("primary_category", "primary_category__parent")
            .prefetch_related("images")
        }
        variacoes = {v.pk: v for v in Variant.objects.filter(pk__in=ids_v, active=True).select_related("product")}
        itens, invalidas = [], []
        for chave, quantidade in self.dados.items():
            p, v = (int(x) for x in chave.split(":"))
            produto = produtos.get(p)
            variacao = variacoes.get(v) if v else None
            if produto is None or (v and variacao is None):
                invalidas.append(chave)
                continue
            if variacao is not None:
                variacao.product = produto
            itens.append(Item(chave, produto, variacao, quantidade))
        if invalidas:
            self.removidos = invalidas
            for chave in invalidas:
                self.dados.pop(chave, None)
            self.session[CHAVE_SESSAO] = self.dados
            self.session.modified = True
        self._itens = itens
        return itens
