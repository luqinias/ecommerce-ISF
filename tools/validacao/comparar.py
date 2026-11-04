"""Gera tabelas do comparativo estrutural referência × sistema local (Fase 4).

Lê docs/engenharia-reversa/raw/{captura,breakpoints}.json e docs/validacao/raw/{captura,breakpoints_local}.json
e imprime Markdown com: ordem de seções, grids por viewport, tokens de componentes, desempenho e acessibilidade.
Uso: uv run python tools/validacao/comparar.py > /tmp/tabelas.md
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REF = json.loads((RAIZ / "docs/engenharia-reversa/raw/captura.json").read_text())
LOC = json.loads((RAIZ / "docs/validacao/raw/captura.json").read_text())

# grids equivalentes (seletor da referência → seletor local)
GRIDS = {
    "home": [("cda-track", "trilho", "Trilho da vitrine"), ("#cda-dat-grid", "colecoes__grade", "Cards de coleção/data"),
             ("#cda-port-gal", "portfolio__grade", "Portfólio"), ("#cda-cat-tiles", "tiles", "Tiles de categoria"),
             ("cda-how-steps", "passos-home", "Como funciona"), ("cda-proof", "hero__provas", "Cards de prova (hero)")],
    "categoria": [("products.columns-5", "grade-produtos", "Grade de produtos")],
    "catalogo": [("products.columns-5", "grade-produtos", "Grade de produtos")],
    "produto": [("products.columns-5", "grade-produtos", "Relacionados")],
}  # fmt: skip

TOKENS = ["body", "h1", "h2", "util_bar", "header_main", "header_nav", "dd_trigger", "dd_panel", "cta_gold", "btn_primario",
          "btn_ghost", "kicker", "card_produto", "tile_categoria", "passo", "faq_item", "chip", "paginacao_atual",
          "breadcrumb", "cookie_banner"]  # fmt: skip
PROPS = ["fontSize", "fontWeight", "borderRadius", "padding", "height"]


def grid(reg, vp, nome):
    for g in reg["viewports"][vp]["estrutura"]["grids"]:
        if g["sel"].startswith(nome) or g["sel"] == nome:
            return g["colunas"]
    return "—"


def px(v):
    return v.replace("px", "") if isinstance(v, str) else v


def main():
    print("## Grids (colunas visíveis na 1ª linha)\n")
    print("| Página | Componente | Ref 390 | Local 390 | Ref 768 | Local 768 | Ref 1440 | Local 1440 |")
    print("|---|---|---|---|---|---|---|---|")
    for tipo, pares in GRIDS.items():
        r, loc = REF[tipo][0], LOC[tipo][0]
        for ref_sel, loc_sel, rotulo in pares:
            cel = []
            for vp in ("390", "768", "1440"):
                cel += [str(grid(r, vp, ref_sel)), str(grid(loc, vp, loc_sel))]
            print(f"| {tipo} | {rotulo} | " + " | ".join(cel) + " |")

    print("\n## Métricas de componentes (1440 px)\n")
    print("| Componente | Propriedade | Referência | Local |")
    print("|---|---|---|---|")
    for tipo in ("home", "categoria", "produto"):
        er, el = REF[tipo][0]["viewports"]["1440"]["estilos"], LOC[tipo][0]["viewports"]["1440"]["estilos"]
        for chave in TOKENS:
            if chave in er and chave in el and not chave.startswith("_"):
                for p in PROPS:
                    a, b = px(er[chave].get(p)), px(el[chave].get(p))
                    if a not in (None, "", "auto", "normal") or b not in (None, "", "auto", "normal"):
                        print(f"| {chave} ({tipo}) | {p} | {a} | {b} |")
                TOKENS.remove(chave)

    print("\n## Desempenho e acessibilidade (1440 px, rastreadores bloqueados na referência)\n")
    print(
        "| Tipo | LCP ref (ms) | LCP local (ms) | CLS ref | CLS local | axe crít./sérias ref | axe crít./sérias local | rolagem horizontal 390 (local) |"
    )
    print("|---|---|---|---|---|---|---|---|")
    for tipo in LOC:
        if tipo not in REF:
            continue
        r, loc = REF[tipo][0], LOC[tipo][0]

        def graves(reg):
            ax = reg.get("axe")
            if not isinstance(ax, list):
                return "—"
            return str(sum(1 for v in ax if v["impacto"] in ("critical", "serious")))

        sw = loc["viewports"]["390"]["estrutura"]["scrollW"]
        print(
            f"| {tipo} | {r['perf']['lcp']} | {loc['perf']['lcp']} | {r['perf']['cls']} | {loc['perf']['cls']} | {graves(r)} | {graves(loc)} | {'não' if sw <= 390 else f'sim ({sw}px)'} |"
        )

    print("\n## Ordem das seções (1440 px)\n")
    for tipo in ("home", "produto", "categoria", "contato", "termos"):
        if tipo in LOC:
            r = [s["titulo"][:40] or s["cls"][:30] for s in REF[tipo][0]["viewports"]["1440"]["estrutura"]["secoes"]]
            loc = [s["titulo"][:40] or s["cls"][:30] for s in LOC[tipo][0]["viewports"]["1440"]["estrutura"]["secoes"]]
            print(f"**{tipo}** — referência ({len(r)}): {' → '.join(r)}\n\nlocal ({len(loc)}): {' → '.join(loc)}\n")


if __name__ == "__main__":
    main()
