"""Captura estrutural de páginas (referência ou sistema local).

Para cada página amostrada: 1 navegação, depois screenshots full-page em 3 viewports
(redimensionando a mesma aba), árvore de seções, headings, estilos computados,
rede XHR/fetch, SEO, axe (1440) e LCP/CLS.

Uso:
    python captura.py referencia            # amostras da referência (AMOSTRAS)
    python captura.py local http://127.0.0.1:8000   # amostras do sistema local (AMOSTRAS_LOCAL)

Regras (seção 4.2): só páginas públicas, 1 navegação a cada 2 s, scripts de rastreamento
bloqueados, nenhum formulário submetido, nenhum link wa.me/mailto seguido.
"""

import json
import sys
from pathlib import Path

from comum import BASE, RAIZ, USER_AGENT, aguardar
from playwright.sync_api import sync_playwright

BLOQUEAR = (
    "googletagmanager",
    "google-analytics",
    "facebook.net",
    "facebook.com/tr",
    "fbcdn",
    "doubleclick",
    "clarity.ms",
    "hotjar",
    "connect.facebook",
)
VIEWPORTS = {"1440": (1440, 900), "768": (768, 1024), "390": (390, 844)}

AMOSTRAS = {
    "home": ["/"],
    "catalogo": ["/categorias-de-brindes/", "/categorias-de-brindes/page/2/"],
    "categoria": ["/categoria-produto/canetas/", "/categoria-produto/mochilas/"],
    "subcategoria": [
        "/categoria-produto/cadernos/agendas/",
        "/categoria-produto/garrafas-e-squeezes/garrafas-termicas/",
    ],
    "data-especial": ["/categoria-produto/fim-de-ano-natal/", "/categoria-produto/outubro-rosa/"],
    "produto": [
        "/produto/kit-talheres-fibra-de-bambu-personalizado/",
        "/produto/kit-churrasco-premium-estojo-bambu-personalizado/",
    ],
    "busca": ["/?s=garrafa&post_type=product"],
    "novidades": ["/novidades/"],
    "sobre": ["/sobre-cia-da-arte-brindes/"],
    "blog": ["/blog/"],
    "blog-post": ["/brindes-novembro-azul/", "/tipos-de-personalizacao-de-brindes/"],
    "contato": ["/contato/"],
    "orcamento": ["/solicitar-orcamento-2/", "/finalizacao-de-orcamento/"],
    "termos": ["/termos-de-uso-e-privacidade/", "/politica-de-privacidade/"],
    "landing-segmento": ["/agro/"],
    "404": ["/pagina-inexistente-estudo-isf/"],
}

AMOSTRAS_LOCAL = {
    "home": ["/"],
    "catalogo": ["/produtos/", "/produtos/page/2/"],
    "categoria": ["/categoria-produto/gotejamento/"],
    "subcategoria": ["/categoria-produto/tubos-e-conexoes/conexoes/"],
    "data-especial": ["/colecao/lancamentos/"],
    "produto": ["/produto/gotejador-autocompensante-demo/"],
    "busca": ["/busca/?q=filtro"],
    "novidades": ["/novidades/"],
    "sobre": ["/sobre/"],
    "blog": ["/blog/"],
    "contato": ["/contato/"],
    "orcamento": ["/orcamento/"],
    "termos": ["/termos-de-uso/", "/politica-de-privacidade/"],
    "404": ["/pagina-inexistente-estudo-isf/"],
}

PERF_INIT = """
window.__lcp = 0; window.__cls = 0;
try {
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; })
    .observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
    .observe({type: 'layout-shift', buffered: true});
} catch (e) {}
"""

ESTRUTURA_JS = r"""
() => {
  const box = el => { const r = el.getBoundingClientRect(); return {x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height)}; };
  const cls = el => (typeof el.className === 'string' ? el.className : '').split(/\s+/).filter(x => x && !/^(elementor|e-con|e-flex|e-parent|e-child)/.test(x)).slice(0, 4).join('.');
  const landmarks = [...document.querySelectorAll('header, nav, main, footer, aside, [role=banner], [role=navigation], [role=main], [role=contentinfo]')]
    .map(el => ({tag: el.tagName.toLowerCase(), role: el.getAttribute('role'), cls: cls(el), label: el.getAttribute('aria-label'), ...box(el)}));
  const headings = [...document.querySelectorAll('h1,h2,h3,h4')].filter(h => h.offsetParent !== null)
    .map(h => ({tag: h.tagName.toLowerCase(), text: h.innerText.trim().replace(/\s+/g, ' ').slice(0, 90)}));
  // seções: blocos de primeiro nível dentro de main (ou body), com altura relevante
  const main = document.querySelector('main') || document.body;
  const secoes = [];
  const visitar = (el, prof) => {
    for (const c of el.children) {
      if (['SCRIPT','STYLE','NOSCRIPT','LINK'].includes(c.tagName)) continue;
      const b = box(c);
      if (b.h < 30) continue;
      const ehSecao = c.tagName === 'SECTION' || /(^|\s)cda-[a-z]+(\s|$)/.test(c.className) && b.w > 900 && prof > 0;
      if (c.tagName === 'SECTION' || (ehSecao && !secoes.length)) {
        const h = c.querySelector('h1,h2,h3');
        secoes.push({tag: c.tagName.toLowerCase(), id: c.id, cls: cls(c), titulo: h ? h.innerText.trim().replace(/\s+/g,' ').slice(0, 80) : '', ...b});
      } else if (prof < 12) visitar(c, prof + 1);
    }
  };
  visitar(main, 0);
  // containers: maiores larguras máximas
  const containers = {};
  for (const el of document.querySelectorAll('[class*=container], [class*=wrap], .ast-container, main > *')) {
    const cs = getComputedStyle(el);
    if (cs.maxWidth !== 'none') containers[cls(el) || el.tagName] = {maxWidth: cs.maxWidth, padding: cs.paddingLeft + ' ' + cs.paddingRight, w: Math.round(el.getBoundingClientRect().width)};
  }
  // grids: elementos com display grid/flex-wrap e >= 3 filhos visíveis
  const grids = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    const filhos = [...el.children].filter(c => c.offsetParent !== null && c.getBoundingClientRect().width > 40);
    if (filhos.length < 3) continue;
    if (cs.display.includes('grid') || (cs.display.includes('flex') && cs.flexWrap === 'wrap') || cs.overflowX === 'auto' || cs.overflowX === 'scroll') {
      const top0 = Math.round(filhos[0].getBoundingClientRect().top);
      const colunas = filhos.filter(c => Math.abs(Math.round(c.getBoundingClientRect().top) - top0) < 4).length;
      grids.push({sel: el.id ? '#' + el.id : cls(el) || el.tagName.toLowerCase(), display: cs.display, template: cs.gridTemplateColumns, gap: cs.gap, colunas, itens: filhos.length, overflowX: cs.overflowX, w: Math.round(el.getBoundingClientRect().width)});
    }
  }
  const scrollW = document.documentElement.scrollWidth;
  return {landmarks, headings, secoes, containers, grids: grids.slice(0, 40), scrollW, altura: document.documentElement.scrollHeight};
}
"""

PROPS = [
    "color",
    "backgroundColor",
    "backgroundImage",
    "fontFamily",
    "fontSize",
    "fontWeight",
    "lineHeight",
    "letterSpacing",
    "textTransform",
    "padding",
    "margin",
    "border",
    "borderRadius",
    "boxShadow",
    "transition",
    "width",
    "height",
    "display",
    "gap",
    "gridTemplateColumns",
    "maxWidth",
]

ESTILOS_JS = r"""
(props) => {
  const alvos = {
    body: 'body', h1: 'h1', h2: 'main h2, h2', h3: 'main h3, h3', h4: 'h4', p: 'main p', link: 'main a:not([class])',
    util_bar: '.cda-util', header_main: '.cda-main-row', header_nav: '.cda-nav-d', logo: '.cda-logo',
    busca_input: '#cda-search-input, input[type=search]', nav_link: '.cda-nav-d a:not([class])',
    dd_trigger: '.cda-dd-trigger', dd_panel: '.cda-dd-panel', cta_gold: '.cda-cta-gold',
    btn_primario: '.cda-btn-primary, .cda-btn.primary, .single_add_to_cart_button', btn_ghost: '.cda-btn-ghost',
    btn: '.cda-btn', kicker: '.cda-kicker', link_seta: '.cda-link', badge: '.cda-badge, .cda-pc-badge',
    card_produto: '.cda-pc, li.product, .product-card, [class*=prod-card]', card_produto_img: '.cda-pc-img, li.product img',
    card_data: '.cda-card', tile_categoria: '.cda-tile', passo: '.cda-step', depoimento: '.cda-test-card',
    faq_item: '.cda-faq-item', faq_summary: '.cda-faq-item summary', footer: '.cda-footer, footer',
    hero: '.cda-hero', banner: '.cda-banner', band: '.cda-band',
    chip: '[class*=chip]', chip_ativo: '[class*=chip].active, [class*=chip][class*=active], [class*=chip][aria-current]',
    ordenacao: 'select.orderby, select[name=orderby], [class*=sort] select, [class*=order] select',
    paginacao: '.page-numbers:not(.current), [class*=pag] a', paginacao_atual: '.page-numbers.current, [class*=pag] [aria-current]',
    breadcrumb: '.woocommerce-breadcrumb, .rank-math-breadcrumb, nav[aria-label*=readcrumb], [class*=breadcrumb]',
    input: 'main input[type=text], main input[type=email], main input:not([type])', textarea: 'main textarea',
    select: 'main select', variacao_swatch: '[class*=swatch], .variable-item, [class*=color] button, [class*=cor] button',
    qty: 'input.qty, [class*=qty] input', qty_btn: '[class*=qty] button, .plus, .minus',
    cookie_banner: '[class*=cookie], #ck-banner, .ck-banner, [id*=ck-]', cookie_ok: '.ck-ok', cookie_min: '.ck-min',
    scroll_top: '[class*=top][class*=btn], #cda-totop, [class*=scroll-top], [class*=back-to-top], [class*=totop]',
    wpp_float: '[class*=wpp-float], [class*=whats][class*=float], a[href*="wa.me"][class*=float]',
  };
  const out = {};
  for (const [nome, sel] of Object.entries(alvos)) {
    let el = null;
    try { el = [...document.querySelectorAll(sel)].find(e => e.getBoundingClientRect().width > 0) || document.querySelector(sel); } catch (e) {}
    if (!el) continue;
    const cs = getComputedStyle(el);
    const o = {_sel: sel, _tag: el.tagName.toLowerCase(), _cls: (typeof el.className === 'string' ? el.className : '').slice(0, 80)};
    for (const p of props) o[p] = cs[p];
    out[nome] = o;
  }
  // classes recorrentes por padrão de nome (descoberta)
  const cont = {};
  for (const el of document.querySelectorAll('[class]')) {
    for (const c of (typeof el.className === 'string' ? el.className : '').split(/\s+/))
      if (/chip|card|btn|badge|pag|tag|pill|swatch|qty|crumb|sort|order|filter|cat/i.test(c) && !/^elementor|^e-/.test(c)) cont[c] = (cont[c] || 0) + 1;
  }
  out._classes_recorrentes = Object.entries(cont).sort((a, b) => b[1] - a[1]).slice(0, 60);
  return out;
}
"""

SEO_JS = r"""
() => {
  const m = n => { const e = document.querySelector(`meta[name="${n}"], meta[property="${n}"]`); return e ? e.content : null; };
  const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { return JSON.parse(s.textContent); } catch (e) { return 'invalido'; } });
  const tipos = [];
  const coletar = o => { if (!o || typeof o !== 'object') return; if (Array.isArray(o)) return o.forEach(coletar); if (o['@type']) tipos.push(o['@type']); if (o['@graph']) coletar(o['@graph']); };
  ld.forEach(coletar);
  const canon = document.querySelector('link[rel=canonical]');
  const bc = document.querySelector('.rank-math-breadcrumb, .woocommerce-breadcrumb, nav[aria-label*=readcrumb], [class*=breadcrumb]');
  const wa = [...document.querySelectorAll('a[href*="wa.me"], a[href*="api.whatsapp"], a[href^="mailto:"], a[href^="tel:"]')].map(a => ({texto: a.innerText.trim().slice(0, 60), href: a.href.slice(0, 400)}));
  return {
    title: document.title, description: m('description'), robots: m('robots'), canonical: canon ? canon.href : null,
    og: {title: m('og:title'), description: m('og:description'), type: m('og:type'), image: m('og:image'), url: m('og:url'), locale: m('og:locale'), site_name: m('og:site_name')},
    twitter: {card: m('twitter:card')}, lang: document.documentElement.lang,
    jsonld_tipos: tipos, jsonld: ld, breadcrumb: bc ? bc.innerText.trim().replace(/\s+/g, ' ') : null,
    links_contato: wa.slice(0, 15), h1_count: document.querySelectorAll('h1').length,
  };
}
"""


def caminho_seguro(url_path: str) -> str:
    s = url_path.strip("/").replace("/", "__").replace("?", "_").replace("=", "-").replace("&", "_")
    return s or "home"


def capturar(base: str, amostras: dict, destino: Path, com_axe: bool = True):
    destino.mkdir(parents=True, exist_ok=True)
    shots = destino / "screenshots"
    resultados = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tipo, caminhos in amostras.items():
            for i, caminho in enumerate(caminhos):
                ctx = browser.new_context(
                    user_agent=USER_AGENT, viewport={"width": 1440, "height": 900}, locale="pt-BR"
                )
                ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in BLOQUEAR) else r.continue_())
                ctx.add_init_script(PERF_INIT)
                page = ctx.new_page()
                rede = []

                def on_req(req, rede=rede):
                    if req.resource_type in ("xhr", "fetch"):
                        rede.append(
                            {
                                "metodo": req.method,
                                "url": req.url[:300],
                                "tipo": req.resource_type,
                                "post": (req.post_data or "")[:300],
                            }
                        )

                page.on("request", on_req)
                url = base.rstrip("/") + caminho
                print(f"[{tipo}] {url}", flush=True)
                aguardar()
                try:
                    resp = page.goto(url, wait_until="networkidle", timeout=90000)
                    status = resp.status if resp else None
                except Exception as e:
                    print("  erro", e)
                    ctx.close()
                    continue
                page.wait_for_timeout(1500)
                # rola até o fim para disparar lazy-load, volta ao topo
                page.evaluate(
                    "async () => { for (let y = 0; y < document.body.scrollHeight; y += 700) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); }"
                )
                page.wait_for_timeout(800)
                perf = page.evaluate(
                    "() => ({lcp: Math.round(window.__lcp), cls: +window.__cls.toFixed(4), dcl: Math.round(performance.getEntriesByType('navigation')[0]?.domContentLoadedEventEnd || 0)})"
                )
                reg = {"url": url, "status": status, "perf": perf, "rede": rede, "viewports": {}}
                reg["seo"] = page.evaluate(SEO_JS)
                if com_axe and i == 0:
                    try:
                        from axe_playwright_python.sync_playwright import Axe

                        r = Axe().run(page)
                        viol = r.response.get("violations", [])
                        reg["axe"] = [
                            {"id": v["id"], "impacto": v["impact"], "nos": len(v["nodes"]), "descricao": v["help"]}
                            for v in viol
                        ]
                    except Exception as e:
                        reg["axe"] = f"erro: {e}"
                for vp, (w, h) in VIEWPORTS.items():
                    page.set_viewport_size({"width": w, "height": h})
                    page.wait_for_timeout(700)
                    pasta = shots / tipo
                    pasta.mkdir(parents=True, exist_ok=True)
                    sufixo = "" if i == 0 else f"-{i + 1}"
                    page.screenshot(path=str(pasta / f"{vp}{sufixo}.png"), full_page=True)
                    reg["viewports"][vp] = {
                        "estrutura": page.evaluate(ESTRUTURA_JS),
                        "estilos": page.evaluate(ESTILOS_JS, PROPS),
                    }
                resultados.setdefault(tipo, []).append(reg)
                ctx.close()
        browser.close()
    (destino / "raw").mkdir(parents=True, exist_ok=True)
    (destino / "raw" / "captura.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
    return resultados


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "referencia"
    if modo == "local":
        base = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"
        capturar(base, AMOSTRAS_LOCAL, RAIZ / "docs" / "validacao")
    else:
        filtro = sys.argv[2:] or None
        amostras = {k: v for k, v in AMOSTRAS.items() if not filtro or k in filtro}
        capturar(BASE, amostras, RAIZ / "docs" / "engenharia-reversa")
