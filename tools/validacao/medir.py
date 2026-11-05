"""Mede estilos computados e caixas de pares de elementos (referência × ISF).

Para cada página, abre a referência e o sistema local com os mesmos viewports e registra,
por par de seletores, fonte, tamanho, peso, entrelinha, espaçamento, cor e caixa (x, y, w, h).
Gera docs/validacao/raw/medidas.json e imprime as diferenças relevantes.

Uso:
    uv run python tools/validacao/medir.py http://localhost:8000            # todas as páginas
    uv run python tools/validacao/medir.py http://localhost:8000 --so-local # reaproveita a referência já medida

Regras da seção 4.2: só páginas públicas, 1 navegação a cada 2 s, rastreadores bloqueados,
nenhum formulário submetido.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engenharia_reversa"))

from comum import BASE, USER_AGENT, aguardar
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "docs/validacao/raw/medidas.json"
VIEWPORTS = {"1440": (1440, 900), "768": (768, 1024), "390": (390, 844)}
BLOQUEAR = ("googletagmanager", "google-analytics", "facebook", "fbcdn", "doubleclick", "clarity.ms", "hotjar")

PAGINAS = {
    "home": ("/", "/"),
    "categoria": ("/categoria-produto/canetas/", "/categoria-produto/gotejamento/"),
    "produto": (
        "/produto/kit-talheres-fibra-de-bambu-personalizado/",
        "/produto/gotejador-autocompensante-de-botao/",
    ),
}

# nome: (seletor na referência, seletor no ISF)
PARES = {
    "comum": {
        "body": ("body", "body"),
        "faixa_superior": ("#cda-header-w .cda-util-row", ".faixa-superior__linha"),
        "header_linha": ("#cda-header-w .cda-main-row-inner", ".cabecalho__linha"),
        "logo": ("#cda-header-w .cda-logo img, #cda-header-w .cda-logo", ".cabecalho__linha .logo"),
        "busca": ("#cda-header-w .cda-search", ".cabecalho__linha .busca__campo"),
        "busca_input": ("#cda-header-w .cda-search input", ".cabecalho__linha .busca input"),
        "nav": ("#cda-header-w .cda-nav-d", ".navegacao"),
        "nav_linha": ("#cda-header-w .cda-nav-d .cda-container", ".navegacao__linha"),
        "nav_dd": ("#cda-header-w .cda-dd-trigger", ".dd__gatilho--escuro"),
        "nav_dd2": ("#cda-header-w .cda-dd:nth-child(2) .cda-dd-trigger", ".dd__gatilho--claro"),
        "nav_link": ("#cda-header-w .cda-nav-d .cda-container > a", ".navegacao__links a"),
        "nav_cta": ("#cda-header-w .cda-cta-gold", ".navegacao__cta"),
        "rodape_titulo": (".cda-footer .cda-tit", ".rodape__titulo"),
        "rodape_link": (".cda-footer .cda-links a", ".rodape__links a"),
        "rodape_base": (".cda-footer .cda-base .cda-wrap", ".rodape__base-linha"),
        "rodape_grade": (".cda-footer .cda-main .cda-wrap", ".rodape__grade"),
        "cookies": ("#cda-cookie", "#aviso-cookies"),
        "cookies_btn": ("#cda-cookie button", "#aviso-cookies .btn"),
    },
    "home": {
        "hero": ("#cda-hero-w .cda-hero", ".hero"),
        "hero_grade": ("#cda-hero-w .cda-hero .cda-container", ".hero__grade"),
        "hero_selo": ("#cda-hero-w .cda-badge", ".hero__selo"),
        "hero_h1": ("#cda-hero-w h1", ".hero h1"),
        "hero_h1_em": ("#cda-hero-w h1 em, #cda-hero-w h1 span", ".hero h1 em"),
        "hero_sub": ("#cda-hero-w .cda-sub", ".hero__sub"),
        "hero_btn": ("#cda-hero-w .cda-btn", ".hero__ctas .btn"),
        "hero_prova": ("#cda-hero-w .cda-proof-card", ".prova"),
        "hero_prova_b": ("#cda-hero-w .cda-proof-card b", ".prova b"),
        "hero_prova_span": ("#cda-hero-w .cda-proof-card span", ".prova span, .prova > :last-child"),
        "vitrine": ("#cda-vit-w .cda-vit", ".vitrine"),
        "kicker": ("#cda-vit-w .cda-kicker", ".kicker"),
        "h2": ("#cda-vit-w h2", "main h2"),
        "h3_vitrine": ("#cda-vit-w h3", ".vitrine__cabecalho h3"),
        "card_nome_vitrine": ("#cda-vit-w .cda-pc b", ".trilho .card-produto__nome"),
        "card_ir_vitrine": ("#cda-vit-w .cda-pc-go", ".trilho .card-produto__ir"),
        "link_seta": ("#cda-vit-w .cda-link", ".link-seta"),
        "card_colecao_h3": ("#cda-dat-w h3", ".card-colecao h3"),
        "card_colecao_p": ("#cda-dat-w .cda-body p", ".card-colecao__corpo p"),
        "tile_nome": ("#cda-cat-w .cda-tile b", ".tile__corpo b, .tile__corpo strong, .tile__corpo > :first-child"),
        "tile_qtd": ("#cda-cat-w .cda-tile small", ".tile__corpo small"),
        "passo": ("#cda-how-w .cda-step", ".passo"),
        "passo_num": ("#cda-how-w .cda-step-num", ".passo__num"),
        "passo_titulo": ("#cda-how-w .cda-step b", ".passo h3"),
        "passo_texto": ("#cda-how-w .cda-step span", ".passo p"),
        "secao_como": ("#cda-how-w .cda-how", "#como-funciona, .secao:has(.passos-home)"),
        "faixa": ("#cda-prz-w .cda-band", ".faixa"),
        "faixa_h2": ("#cda-prz-w h2", ".faixa h2"),
        "faq_secao": ("#cda-faq-w .cda-faq", ".secao:has(.faq__lista)"),
        "faq_summary": ("#cda-faq-w summary", ".faq__item summary"),
        "faq_item": ("#cda-faq-w .cda-faq-item", ".faq__item"),
    },
    "categoria": {
        "hero_lista": ("main [class*=cda-cat-hero], main [class*=hero]", ".hero-lista"),
        "h1": ("main h1", "main h1"),
        "lead": ("main h1 + p, main h1 ~ p", ".hero-lista .lead"),
        "breadcrumb": (".woocommerce-breadcrumb, nav[aria-label*=readcrumb], [class*=breadcrumb]", ".breadcrumb ol"),
        "chip": (".cda-chip", ".chip"),
        "ordenacao": ("select.orderby, select[name=orderby]", ".select-pilula"),
        "grade": ("ul.products", ".grade-produtos"),
        "card": (".cda-pc", ".card-produto"),
        "card_nome": (".cda-pc-nome", ".card-produto__nome"),
        "card_cores": (".cda-pc-cores", ".card-produto__opcoes"),
        "card_ir": (".cda-pc-go", ".card-produto__ir"),
        "paginacao": (".page-numbers:not(.current)", ".paginacao a"),
    },
    "produto": {
        "breadcrumb": (".woocommerce-breadcrumb", ".resumo .breadcrumb ol"),
        "selo": (".cda-prod-selo", ".resumo__categoria"),
        "h1": (".product_title", ".resumo__titulo"),
        "codigo": (".cda-prod-cod", ".resumo__codigo"),
        "curta": (".woocommerce-product-details__short-description", ".resumo__curta"),
        "galeria": (".woocommerce-product-gallery", ".galeria"),
        "resumo": (".summary.entry-summary", ".resumo"),
        "rotulo_var": (".variations label, .variations th", ".opcoes legend"),
        "opcao": (".cda-sw-b, .variable-item, .variations button", ".opcao span"),
        "qty": ("input.qty", ".quantidade input"),
        "botao": (".single_add_to_cart_button", ".compra__botao"),
        "relacionados_h2": (".related h2, .upsells h2, section.related h2", ".relacionados h2"),
        "card_nome": (".related .cda-pc-nome, .cda-pc-nome", ".relacionados .card-produto__nome"),
    },
}

PROPS = [
    "fontFamily",
    "fontSize",
    "fontWeight",
    "fontStyle",
    "lineHeight",
    "letterSpacing",
    "textTransform",
    "color",
    "backgroundColor",
    "padding",
    "borderRadius",
    "maxWidth",
    "gap",
    "justifyContent",
]

JS = r"""
([pares, props, lado]) => {
  const out = {};
  for (const [nome, sels] of Object.entries(pares)) {
    const sel = sels[lado];
    let el = null;
    try { el = [...document.querySelectorAll(sel)].find(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }); } catch (e) {}
    if (!el) { out[nome] = null; continue; }
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    const o = {tag: el.tagName.toLowerCase(), x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height)};
    for (const p of props) o[p] = cs[p];
    o.fontFamily = cs.fontFamily.split(',')[0].replace(/["']/g, '');
    out[nome] = o;
  }
  return out;
}
"""


def medir(page, url, pares, lado):
    page.set_viewport_size({"width": 1440, "height": 900})
    aguardar()
    page.goto(url, wait_until="networkidle", timeout=90000)
    page.wait_for_timeout(1200)
    page.evaluate("document.fonts && document.fonts.ready")
    res = {}
    for vp, (w, h) in VIEWPORTS.items():
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(600)
        res[vp] = page.evaluate(JS, [pares, PROPS, lado])
    return res


def main():
    base_local = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "http://localhost:8000"
    so_local = "--so-local" in sys.argv
    anterior = json.loads(SAIDA.read_text()) if SAIDA.exists() else {}
    dados = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for pagina, (cam_ref, cam_loc) in PAGINAS.items():
            pares = {**PARES["comum"], **PARES[pagina]}
            dados[pagina] = {}
            for lado, base, cam in ((0, BASE, cam_ref), (1, base_local, cam_loc)):
                chave = "ref" if lado == 0 else "isf"
                if lado == 0 and so_local and pagina in anterior:
                    dados[pagina]["ref"] = anterior[pagina]["ref"]
                    continue
                ctx = browser.new_context(user_agent=USER_AGENT, locale="pt-BR")
                ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in BLOQUEAR) else r.continue_())
                page = ctx.new_page()
                print(f"[{pagina}/{chave}] {base}{cam}", flush=True)
                dados[pagina][chave] = medir(page, base + cam, pares, lado)
                ctx.close()
        browser.close()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1))
    print("medidas em", SAIDA)


if __name__ == "__main__":
    main()
