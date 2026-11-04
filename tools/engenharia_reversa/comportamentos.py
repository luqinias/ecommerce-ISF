"""Observa comportamentos interativos da referência (sem submeter formulários).

Gera docs/engenharia-reversa/raw/comportamentos.json e screenshots/comportamentos/*.png.
Regras: 1 navegação a cada 2 s, nenhum formulário submetido, links wa.me/mailto apenas
registrados. Adicionar ao orçamento é observado (o item fica só na sessão anônima da
referência; nenhum contato é gerado, porque o envio do orçamento não é feito).
"""

import json
import sys

from comum import BASE, RAW, SAIDA, USER_AGENT, aguardar
from playwright.sync_api import sync_playwright

BLOQUEAR = ("googletagmanager", "google-analytics", "facebook.net", "facebook.com/tr", "fbcdn",
            "doubleclick", "clarity.ms", "hotjar", "connect.facebook")
SHOTS = SAIDA / "screenshots" / "comportamentos"
PRODUTO = "/produto/kit-talheres-fibra-de-bambu-personalizado/"
LISTA = "/categoria-produto/mochilas/"
R = {}


def passo(nome):
    """Executa o passo imediatamente e guarda o resultado (ou o erro) em R[nome]."""
    def deco(fn):
        try:
            R[nome] = fn()
        except Exception as e:  # noqa: BLE001
            R[nome] = {"erro": str(e)[:400]}
        print(nome, json.dumps(R[nome], ensure_ascii=False)[:300], flush=True)
        return fn
    return deco


def shot(page, nome, full=False):
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOTS / f"{nome}.png"), full_page=full)


def nav(page, caminho):
    aguardar()
    page.goto(BASE + caminho, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(3500)


ESTADO_JS = """(sel) => { const e = document.querySelector(sel); if (!e) return null; const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
 return {visivel: cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity > 0 && r.height > 0, display: cs.display, opacity: cs.opacity, transform: cs.transform,
 boxShadow: cs.boxShadow, bg: cs.backgroundColor, color: cs.color, outline: cs.outline, borderColor: cs.borderColor, transition: cs.transition, w: Math.round(r.width), h: Math.round(r.height), aria: e.getAttribute('aria-expanded'), cls: e.className.toString().slice(0,120)}; }"""


def estado(page, sel):
    return page.evaluate(ESTADO_JS, sel)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=USER_AGENT, viewport={"width": 1440, "height": 900}, locale="pt-BR")
        ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in BLOQUEAR) else r.continue_())
        page = ctx.new_page()
        rede = []
        page.on("request", lambda q: rede.append({"m": q.method, "u": q.url[:250], "t": q.resource_type, "post": (q.post_data or "")[:400]})
                if q.resource_type in ("xhr", "fetch") else None)
        nav(page, "/")
        (RAW / "home.html").write_text(page.content())

        @passo("cookies_banner")
        def _():
            info = page.evaluate("""() => { const el = [...document.querySelectorAll('[class*=ck-], [id*=ck-], [class*=cookie], [id*=cookie]')].filter(e => e.getBoundingClientRect().height > 30 && getComputedStyle(e).position === 'fixed')[0];
              if (!el) return null; const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
              return {sel: el.id ? '#' + el.id : el.className.toString(), texto: el.innerText.trim().slice(0, 400), x: r.x, y: r.y, w: r.width, h: r.height, bottom: cs.bottom, bg: cs.backgroundColor, radius: cs.borderRadius, shadow: cs.boxShadow, zIndex: cs.zIndex,
              botoes: [...el.querySelectorAll('button, a')].map(x => ({texto: x.innerText.trim(), cls: x.className.toString(), href: x.getAttribute('href')}))}; }""")
            shot(page, "cookies-banner")
            return info

        @passo("dropdown_categorias")
        def _():
            antes = estado(page, "#cda-dd-cats .cda-dd-panel")
            page.hover("#cda-dd-cats .cda-dd-trigger")
            page.wait_for_timeout(600)
            hover = estado(page, "#cda-dd-cats .cda-dd-panel")
            if not (hover or {}).get("visivel"):
                page.click("#cda-dd-cats .cda-dd-trigger")
                page.wait_for_timeout(800)
            depois = estado(page, "#cda-dd-cats .cda-dd-panel")
            shot(page, "dropdown-categorias")
            itens = page.evaluate("() => [...document.querySelectorAll('#cda-dd-cats .cda-dd-link')].map(a => ({t: a.innerText.trim().replace(/\\s+/g,' '), href: a.getAttribute('href')}))")
            painel = page.evaluate("() => { const p = document.querySelector('#cda-dd-cats .cda-dd-panel'); if(!p) return null; const cs = getComputedStyle(p); const r = p.getBoundingClientRect(); return {w: r.width, h: r.height, x: r.x, y: r.y, grid: cs.gridTemplateColumns, display: cs.display, radius: cs.borderRadius, shadow: cs.boxShadow, padding: cs.padding, viewall: [...p.querySelectorAll('.cda-dd-viewall')].map(a => a.innerText.trim())}; }")
            page.mouse.move(700, 600)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            fechado = estado(page, "#cda-dd-cats .cda-dd-panel")
            return {"antes": antes, "apos_hover": hover, "aberto": depois, "apos_esc_e_sair": fechado, "itens": itens[:60], "n_itens": len(itens), "painel": painel}

        @passo("dropdown_datas")
        def _():
            page.hover("#cda-dd-dates .cda-dd-trigger")
            page.wait_for_timeout(600)
            st = estado(page, "#cda-dd-dates .cda-dd-panel")
            if not (st or {}).get("visivel"):
                page.click("#cda-dd-dates .cda-dd-trigger")
                page.wait_for_timeout(800)
            shot(page, "dropdown-datas")
            itens = page.evaluate("() => [...document.querySelectorAll('#cda-dd-dates .cda-dd-panel a')].map(a => ({t: a.innerText.trim().replace(/\\s+/g,' '), href: a.getAttribute('href')}))")
            page.mouse.move(700, 600)
            page.wait_for_timeout(400)
            return {"apos_hover": st, "itens": itens}

        @passo("busca_header")
        def _():
            page.fill("#cda-search-input", "garr")
            page.wait_for_timeout(2500)
            sug = page.evaluate("() => { const s = [...document.querySelectorAll('[class*=search] [class*=result], [class*=sugg], [class*=autocomplete], [class*=search-res]')].filter(e => e.getBoundingClientRect().height > 10); return s.map(e => ({cls: e.className.toString(), txt: e.innerText.slice(0,200)})); }")
            form = page.evaluate("() => { const f = document.querySelector('#cda-search-form'); return {action: f.getAttribute('action'), method: f.method, campos: [...f.elements].map(e => [e.name, e.type, e.value])}; }")
            shot(page, "busca-digitando")
            page.fill("#cda-search-input", "")
            return {"sugestoes": sug, "form": form}

        @passo("hover_card_produto")
        def _():
            page.locator(".cda-pc").first.scroll_into_view_if_needed()
            antes = estado(page, ".cda-pc")
            page.hover(".cda-pc >> nth=0")
            page.wait_for_timeout(500)
            depois = estado(page, ".cda-pc")
            img = estado(page, ".cda-pc-img img, .cda-pc-img")
            card = page.evaluate("() => { const c = document.querySelector('.cda-pc'); return {html: c.outerHTML.slice(0, 1500)}; }")
            shot(page, "hover-card")
            return {"antes": antes, "hover": depois, "img": img, "card": card}

        @passo("carrossel_vitrine")
        def _():
            return page.evaluate("() => { const t = document.querySelector('.cda-track'); const cs = getComputedStyle(t); return {overflowX: cs.overflowX, snap: cs.scrollSnapType, scrollW: t.scrollWidth, clientW: t.clientWidth, gap: cs.gap, display: cs.display, setas: [...t.parentElement.querySelectorAll('button')].map(b => b.getAttribute('aria-label') || b.innerText)}; }")

        @passo("portfolio_ver_mais")
        def _():
            botoes = page.evaluate("() => [...document.querySelectorAll('#cda-feito-aqui button, #cda-feito-aqui a')].map(b => ({t: b.innerText.trim(), href: b.getAttribute('href'), tag: b.tagName}))")
            n = page.evaluate("() => [...document.querySelectorAll('#cda-port-gal .cda-g')].filter(e => e.offsetParent !== null).length")
            out = {"botoes": botoes, "itens_visiveis": n}
            alvo = page.locator("#cda-feito-aqui button:has-text('Ver mais'), #cda-feito-aqui button:has-text('mais')")
            if alvo.count():
                alvo.first.click()
                page.wait_for_timeout(800)
                out["itens_apos_ver_mais"] = page.evaluate("() => [...document.querySelectorAll('#cda-port-gal .cda-g')].filter(e => e.offsetParent !== null).length")
            # clique em item da galeria (lightbox?)
            page.locator("#cda-port-gal .cda-g").first.click()
            page.wait_for_timeout(800)
            out["lightbox"] = page.evaluate("() => { const d = [...document.querySelectorAll('dialog[open], [class*=lightbox], [class*=modal]')].filter(e => e.getBoundingClientRect().height > 100); return d.map(e => e.className.toString()); }")
            page.keyboard.press("Escape")
            return out

        @passo("faq_acordeao")
        def _():
            page.locator(".cda-faq-item").first.scroll_into_view_if_needed()
            inicial = page.evaluate("() => [...document.querySelectorAll('.cda-faq-item')].map(d => d.open)")
            page.locator(".cda-faq-item summary").nth(1).click()
            page.wait_for_timeout(600)
            apos = page.evaluate("() => [...document.querySelectorAll('.cda-faq-item')].map(d => d.open)")
            icone = estado(page, ".cda-faq-item[open] .cda-faq-icon")
            shot(page, "faq-aberto")
            perguntas = page.evaluate("() => [...document.querySelectorAll('.cda-faq-item summary')].map(s => s.innerText.trim())")
            return {"inicial": inicial, "apos_clicar_2": apos, "exclusivo": sum(apos) == 1, "icone_aberto": icone, "n": len(perguntas)}

        @passo("rolar_para_cima")
        def _():
            page.evaluate("scrollTo(0, 3000)")
            page.wait_for_timeout(900)
            fixos = page.evaluate("""() => [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); return cs.position === 'fixed' && e.getBoundingClientRect().height > 20 && cs.display !== 'none' && +cs.opacity > 0; })
              .map(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return {tag: e.tagName, id: e.id, cls: e.className.toString().slice(0, 80), aria: e.getAttribute('aria-label'), href: e.getAttribute('href'), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), bg: cs.backgroundColor, radius: cs.borderRadius}; })""")
            sticky = page.evaluate("() => { const s = document.querySelector('.cda-sticky-wrap'); const cs = getComputedStyle(s); return {position: cs.position, top: cs.top, y: s.getBoundingClientRect().y, shadow: cs.boxShadow, cls: s.className}; }")
            shot(page, "rolado")
            topo = [f for f in fixos if "top" in (f["cls"] + f["id"] + str(f["aria"])).lower()]
            if topo:
                sel = "#" + topo[0]["id"] if topo[0]["id"] else "." + topo[0]["cls"].split()[0]
                page.click(sel)
                page.wait_for_timeout(1200)
            return {"fixos_apos_rolar": fixos, "header_sticky": sticky, "scrollY_apos_clicar_topo": page.evaluate("scrollY")}

        @passo("foco_teclado")
        def _():
            page.evaluate("scrollTo(0,0)")
            page.locator("body").click(position={"x": 5, "y": 300})
            focos = []
            for _ in range(6):
                page.keyboard.press("Tab")
                focos.append(page.evaluate("() => { const e = document.activeElement; const cs = getComputedStyle(e); return {tag: e.tagName, txt: (e.innerText || e.value || '').trim().slice(0, 40), cls: e.className.toString().slice(0, 50), outline: cs.outline, outlineOffset: cs.outlineOffset, boxShadow: cs.boxShadow}; }"))
            shot(page, "foco")
            return focos

        @passo("carrinho_vazio")
        def _():
            page.evaluate("scrollTo(0,0)")
            page.click("#cda-cart-btn")
            page.wait_for_timeout(900)
            st = page.evaluate("() => { const p = document.querySelector('.cda-cart-panel'); if(!p) return null; const r = p.getBoundingClientRect(); const cs = getComputedStyle(p); return {txt: p.innerText.slice(0, 400), x: r.x, y: r.y, w: r.width, h: r.height, display: cs.display, position: cs.position, shadow: cs.boxShadow, radius: cs.borderRadius}; }")
            shot(page, "carrinho-vazio")
            page.keyboard.press("Escape")
            page.mouse.click(700, 700)
            return st

        @passo("links_contato_home")
        def _():
            return page.evaluate("() => [...new Set([...document.querySelectorAll('a[href*=\"wa.me\"], a[href*=\"whatsapp\"], a[href^=\"mailto:\"], a[href^=\"tel:\"]')].map(a => a.innerText.trim().slice(0,50) + ' -> ' + decodeURIComponent(a.href).slice(0, 300)))]")

        R["rede_home"] = list(rede)
        rede.clear()

        # ---------- listagem ----------
        nav(page, LISTA)
        (RAW / "listagem.html").write_text(page.content())

        @passo("listagem_controles")
        def _():
            return page.evaluate("""() => {
              const vis = e => e.getBoundingClientRect().height > 0;
              const chips = [...document.querySelectorAll('a, button')].filter(a => vis(a) && /\\(?\\d+\\)?$/.test(a.innerText.trim()) && a.closest('main') && a.innerText.length < 50).slice(0, 50)
                .map(a => ({t: a.innerText.trim().replace(/\\s+/g, ' '), href: a.getAttribute('href'), cls: a.className.toString().slice(0, 80), atual: a.getAttribute('aria-current')}));
              const selects = [...document.querySelectorAll('main select')].map(s => ({name: s.name, cls: s.className.toString(), opcoes: [...s.options].map(o => [o.value, o.text]), form: s.form ? s.form.getAttribute('action') : null}));
              const sortBtns = [...document.querySelectorAll('[class*=sort] a, [class*=sort] button, [class*=order] a, [class*=order] button')].filter(vis).map(a => ({t: a.innerText.trim(), href: a.getAttribute('href'), cls: a.className.toString()}));
              const pag = [...document.querySelectorAll('.page-numbers, [class*=pagin] a, [class*=pagin] span')].filter(vis).map(a => ({t: a.innerText.trim(), href: a.getAttribute('href'), cls: a.className.toString()}));
              const cards = document.querySelectorAll('li.product, .cda-pc, [class*=prod-card], [class*=product-card]');
              const c0 = cards[0];
              const res = [...document.querySelectorAll('.woocommerce-result-count, [class*=result-count], [class*=count]')].filter(vis).map(e => e.innerText.trim()).slice(0, 5);
              const h1 = document.querySelector('h1');
              return {h1: h1 && h1.innerText, chips, selects, sortBtns, pag, n_cards: cards.length, card_html: c0 ? c0.outerHTML.slice(0, 2500) : null, contadores: res};
            }""")

        @passo("listagem_ordenacao")
        def _():
            antes = page.url
            sel = page.locator("main select").first
            if sel.count():
                opcoes = sel.evaluate("s => [...s.options].map(o => o.value)")
                aguardar()
                sel.select_option(opcoes[-1])
                page.wait_for_timeout(4000)
                return {"antes": antes, "depois": page.url, "opcao": opcoes[-1], "xhr": [r for r in rede if r["t"] in ("xhr", "fetch")][-5:]}
            btn = page.locator("[class*=sort] button, [class*=order] button, [class*=sort] a").first
            if btn.count():
                btn.click()
                page.wait_for_timeout(1000)
                shot(page, "ordenacao-aberta")
                return {"tipo": "botao", "menu": page.evaluate("() => [...document.querySelectorAll('[class*=sort] li, [class*=sort] a, [class*=sort] button')].map(e => e.innerText.trim()).filter(Boolean)")}
            return None

        shot(page, "listagem-desktop")
        R["rede_listagem"] = list(rede)
        rede.clear()

        # ---------- produto ----------
        nav(page, PRODUTO)
        (RAW / "produto.html").write_text(page.content())

        @passo("produto_controles")
        def _():
            return page.evaluate("""() => {
              const vis = e => e.getBoundingClientRect().height > 0;
              const f = document.querySelector('form.cart, form.variations_form, main form');
              const controles = [...document.querySelectorAll('main button, main input, main select, main [role=radio], main [class*=swatch] *')].filter(vis).slice(0, 60)
                .map(e => ({tag: e.tagName, type: e.type, name: e.name, cls: e.className.toString().slice(0, 80), txt: (e.innerText || e.value || '').trim().slice(0, 60), disabled: e.disabled, aria: e.getAttribute('aria-label'), min: e.min, step: e.step, value: e.value}));
              const especs = [...document.querySelectorAll('main table tr, main dl > *, main [class*=spec] li, main [class*=attr] li, main [class*=ficha] li')].filter(vis).map(e => e.innerText.trim().replace(/\\s+/g, ' ')).slice(0, 30);
              const galeria = [...document.querySelectorAll('main [class*=gallery] img, main [class*=galeria] img, main [class*=thumb] img')].filter(vis).map(i => ({src: i.currentSrc.slice(-80), w: i.width, h: i.height, alt: i.alt}));
              const textos = [...document.querySelectorAll('main *')].filter(e => vis(e) && e.children.length === 0 && /m[ií]nim|escolha|cor|quant|c[oó]digo|sku|dimens|material|peso|capacidade/i.test(e.innerText)).map(e => e.innerText.trim().slice(0, 120)).slice(0, 40);
              const links = [...document.querySelectorAll('main a')].filter(vis).map(a => ({t: a.innerText.trim().slice(0, 60), href: (a.getAttribute('href') || '').slice(0, 300)})).filter(a => a.t).slice(0, 60);
              const bc = document.querySelector('[class*=breadcrumb]');
              return {form: f ? {action: f.getAttribute('action'), cls: f.className.toString(), dataVar: (f.dataset.product_variations || '').slice(0, 1500)} : null, controles, especs, galeria, textos, links, breadcrumb: bc && bc.innerText,
                      headings: [...document.querySelectorAll('main h1, main h2, main h3')].map(h => h.tagName + ': ' + h.innerText.trim().slice(0, 80))};
            }""")

        shot(page, "produto-inicial", full=True)

        @passo("produto_variacao")
        def _():
            out = {}
            btn = page.locator("main button:has-text('orçamento'), .single_add_to_cart_button").first
            out["botao_antes"] = btn.evaluate("b => ({txt: b.innerText.trim(), disabled: b.disabled, cls: b.className.toString(), aria: b.getAttribute('aria-disabled'), cursor: getComputedStyle(b).cursor, opacity: getComputedStyle(b).opacity, bg: getComputedStyle(b).backgroundColor})")
            btn.click(force=True)
            page.wait_for_timeout(800)
            out["msg_apos_click_sem_cor"] = page.evaluate("() => [...document.querySelectorAll('main *')].filter(e => e.children.length === 0 && e.getBoundingClientRect().height > 0 && /escolha|selecione/i.test(e.innerText)).map(e => e.innerText.trim().slice(0,100))")
            select = page.locator("main select").first
            swatch = page.locator("main [class*=swatch] button, main [class*=swatch] li, main .variable-item, main [class*=cor] button, main [data-value]").first
            if swatch.count():
                out["metodo"] = "swatch"
                swatch.click()
            elif select.count():
                out["metodo"] = "select"
                vals = select.evaluate("s => [...s.options].map(o => o.value).filter(Boolean)")
                select.select_option(vals[0])
            page.wait_for_timeout(1200)
            out["botao_depois"] = btn.evaluate("b => ({txt: b.innerText.trim(), disabled: b.disabled, cls: b.className.toString(), cursor: getComputedStyle(b).cursor, opacity: getComputedStyle(b).opacity, bg: getComputedStyle(b).backgroundColor})")
            out["imagem_trocou"] = page.evaluate("() => (document.querySelector('main [class*=gallery] img, main img') || {}).currentSrc")
            shot(page, "produto-cor-escolhida")
            return out

        @passo("produto_quantidade")
        def _():
            q = page.locator("main input[type=number], main input.qty").first
            out = {"inicial": q.evaluate("i => ({value: i.value, min: i.min, max: i.max, step: i.step, name: i.name})")}
            mais = page.locator("main button:has-text('+'), main .plus, main [class*=plus], main [aria-label*=umentar]").first
            if mais.count():
                mais.click()
                page.wait_for_timeout(400)
                out["apos_mais"] = q.input_value()
            menos = page.locator("main button:has-text('−'), main button:has-text('-'), main .minus, main [class*=minus], main [aria-label*=iminuir]").first
            if menos.count():
                for _ in range(3):
                    menos.click()
                page.wait_for_timeout(400)
                out["apos_3_menos"] = q.input_value()
            q.fill("1")
            q.blur()
            page.wait_for_timeout(600)
            out["apos_digitar_1"] = q.input_value()
            out["validacao"] = q.evaluate("i => i.validationMessage")
            out["msgs"] = page.evaluate("() => [...document.querySelectorAll('main *')].filter(e => e.children.length === 0 && e.getBoundingClientRect().height > 0 && /m[ií]nim/i.test(e.innerText)).map(e => e.innerText.trim().slice(0,120))")
            shot(page, "produto-quantidade")
            return out

        @passo("produto_descricao_expansivel")
        def _():
            b = page.locator("main :text-matches('Ler descri|Ver descri|Leia mais|completa', 'i')").first
            if not b.count():
                return None
            antes = page.evaluate("() => { const d = document.querySelector('[class*=desc]'); return d ? {h: d.getBoundingClientRect().height, cls: d.className.toString()} : null; }")
            tag = b.evaluate("e => ({tag: e.tagName, href: e.getAttribute('href'), txt: e.innerText})")
            b.click()
            page.wait_for_timeout(1200)
            depois = page.evaluate("() => { const d = document.querySelector('[class*=desc]'); return d ? {h: d.getBoundingClientRect().height} : null; }")
            return {"gatilho": tag, "antes": antes, "depois": depois, "scrollY": page.evaluate("scrollY")}

        @passo("produto_galeria")
        def _():
            page.evaluate("scrollTo(0,0)")
            thumbs = page.locator("main [class*=thumb] img, main .flex-control-thumbs img, main [class*=gallery] button")
            out = {"n_thumbs": thumbs.count()}
            principal = "main [class*=gallery] img, main [class*=main-img] img, main img"
            out["antes"] = page.evaluate(f"() => document.querySelector('{principal}').currentSrc")
            if thumbs.count() > 1:
                thumbs.nth(1).click()
                page.wait_for_timeout(900)
                out["depois"] = page.evaluate(f"() => document.querySelector('{principal}').currentSrc")
            shot(page, "produto-galeria")
            return out

        @passo("produto_adicionar_orcamento")
        def _():
            rede.clear()
            q = page.locator("main input[type=number], main input.qty").first
            minimo = q.evaluate("i => i.min || i.value")
            q.fill(str(minimo or 1))
            contador_antes = page.evaluate("() => (document.querySelector('#cda-cart-btn') || {}).innerText")
            btn = page.locator("main button:has-text('orçamento'), .single_add_to_cart_button").first
            btn.click()
            page.wait_for_timeout(5000)
            contador = page.evaluate("() => (document.querySelector('#cda-cart-btn') || {}).innerText")
            feedback = page.evaluate("() => [...document.querySelectorAll('.woocommerce-message, [class*=toast], [class*=notice], [class*=added], .cda-cart-panel')].filter(e => e.getBoundingClientRect().height > 0).map(e => ({cls: e.className.toString().slice(0, 80), txt: e.innerText.trim().slice(0, 300)}))")
            shot(page, "produto-adicionado")
            return {"contador_antes": contador_antes, "contador_depois": contador, "url": page.url, "feedback": feedback, "rede": list(rede)}

        @passo("carrinho_com_item")
        def _():
            page.evaluate("scrollTo(0,0)")
            page.click("#cda-cart-btn")
            page.wait_for_timeout(1000)
            shot(page, "carrinho-com-item")
            return page.evaluate("() => { const p = document.querySelector('.cda-cart-panel'); return p ? {txt: p.innerText.slice(0, 600), links: [...p.querySelectorAll('a,button')].map(a => [a.innerText.trim(), a.getAttribute('href')])} : null; }")

        R["rede_produto"] = list(rede)
        rede.clear()

        # ---------- página de orçamento (sem enviar) ----------
        for caminho in ("/finalizacao-de-orcamento/", "/solicitar-orcamento-2/"):
            nav(page, caminho)
            nome = caminho.strip("/")
            (RAW / f"{nome}.html").write_text(page.content())

            @passo(f"orcamento_{nome}")
            def _():
                shot(page, f"orcamento-{nome}", full=True)
                return page.evaluate("""() => ({
                  forms: [...document.querySelectorAll('form')].filter(f => f.getBoundingClientRect().height > 0).map(f => ({action: f.getAttribute('action'), method: f.method, cls: f.className.toString().slice(0, 80),
                    campos: [...f.elements].filter(e => e.type !== 'hidden' || /hp|honey|nonce/i.test(e.name)).map(e => {
                      const lbl = e.id && document.querySelector(`label[for="${e.id}"]`);
                      return {tag: e.tagName, type: e.type, name: e.name, required: e.required, placeholder: e.placeholder, label: lbl ? lbl.innerText.trim() : null, visivel: e.getBoundingClientRect().height > 0};
                    })})),
                  itens: [...document.querySelectorAll('[class*=item], tr')].filter(e => e.getBoundingClientRect().height > 0).map(e => e.innerText.trim().replace(/\\s+/g, ' ').slice(0, 160)).slice(0, 15),
                  links: [...document.querySelectorAll('main a')].filter(a => /wa\\.me|whats|mailto/.test(a.href)).map(a => a.innerText.trim() + ' -> ' + decodeURIComponent(a.href).slice(0, 500)),
                  headings: [...document.querySelectorAll('main h1, main h2, main h3')].map(h => h.tagName + ': ' + h.innerText.trim().slice(0, 80)),
                })""")

        ctx.close()

        # ---------- mobile ----------
        ctx = b.new_context(user_agent=USER_AGENT, viewport={"width": 390, "height": 844}, locale="pt-BR", is_mobile=True, has_touch=True)
        ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in BLOQUEAR) else r.continue_())
        page = ctx.new_page()
        nav(page, "/")

        @passo("mobile_header")
        def _():
            shot(page, "mobile-header")
            return page.evaluate("""() => { const vis = e => e && e.getBoundingClientRect().height > 0 && getComputedStyle(e).display !== 'none';
              return {burger: vis(document.querySelector('.cda-burger')), nav_desktop: vis(document.querySelector('.cda-nav-d')), busca: vis(document.querySelector('#cda-search-input')),
                      util: vis(document.querySelector('.cda-util')), header_h: document.querySelector('header').getBoundingClientRect().height}; }""")

        @passo("mobile_menu")
        def _():
            page.click(".cda-burger")
            page.wait_for_timeout(900)
            shot(page, "mobile-menu")
            info = page.evaluate("""() => { const p = document.querySelector('.cda-mobile-panel'); if (!p) return null; const r = p.getBoundingClientRect(); const cs = getComputedStyle(p);
              return {x: r.x, w: r.width, h: r.height, transform: cs.transform, transition: cs.transition, overlay: getComputedStyle(document.querySelector('.cda-mobile-overlay')).backgroundColor,
                      secoes: [...p.querySelectorAll('.cda-mobile-section')].map(s => s.innerText.trim().split('\\n').slice(0, 8)), cta: [...p.querySelectorAll('.cda-mobile-cta')].map(a => a.innerText.trim()),
                      bodyOverflow: getComputedStyle(document.body).overflow}; }""")
            page.click(".cda-mobile-close")
            page.wait_for_timeout(600)
            info["fechado_x"] = page.evaluate("() => document.querySelector('.cda-mobile-panel').getBoundingClientRect().x")
            return info

        ctx.close()
        b.close()
    (RAW / "comportamentos.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
    sys.exit(0)
