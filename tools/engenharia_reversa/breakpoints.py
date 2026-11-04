"""Detecta breakpoints reais: redimensiona a aba de 320 a 1600 px e registra onde o layout muda.

Uso: python breakpoints.py [base_url] [caminho ...]
Assinatura por largura: colunas visíveis dos grids principais e visibilidade de header/nav/burger.
"""

import json
import sys

from comum import BASE, RAW, USER_AGENT, aguardar
from playwright.sync_api import sync_playwright

BLOQUEAR = ("googletagmanager", "google-analytics", "facebook", "fbcdn", "doubleclick", "clarity.ms", "hotjar")

ASSINATURA_JS = r"""
() => {
  const vis = e => !!e && e.getBoundingClientRect().height > 0 && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden';
  const cols = sel => { const el = document.querySelector(sel); if (!el) return null;
    const f = [...el.children].filter(c => c.getBoundingClientRect().width > 20 && c.getBoundingClientRect().height > 0); if (!f.length) return 0;
    const t = Math.round(f[0].getBoundingClientRect().top); return f.filter(c => Math.abs(Math.round(c.getBoundingClientRect().top) - t) < 4).length; };
  const sig = {};
  for (const s of window.__SELS__.grids) sig[s] = cols(s);
  for (const s of window.__SELS__.vis) sig['vis:' + s] = vis(document.querySelector(s));
  const c = document.querySelector(window.__SELS__.container);
  sig.container = c ? Math.round(c.getBoundingClientRect().width) : null;
  return sig;
}
"""

PADRAO = {
    "grids": [
        ".cda-track",
        "#cda-dat-grid",
        "#cda-port-gal",
        "#cda-cat-tiles",
        ".cda-how-steps",
        ".cda-test-grid",
        ".cda-proof",
        ".cda-media",
        "ul.products",
        ".products",
        "[class*=grid]",
        ".cda-main-row-inner",
        ".cda-wrap",
    ],
    "vis": [".cda-util", ".cda-nav-d", ".cda-burger", "#cda-search-input", ".cda-cta-gold", ".cda-media"],
    "container": ".cda-container",
}


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith("http") else BASE
    caminhos = [a for a in sys.argv[1:] if not a.startswith("http")] or [
        "/",
        "/categoria-produto/mochilas/",
        "/produto/kit-talheres-fibra-de-bambu-personalizado/",
    ]
    saida = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=USER_AGENT, viewport={"width": 1600, "height": 900})
        ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in BLOQUEAR) else r.continue_())
        page = ctx.new_page()
        for caminho in caminhos:
            aguardar()
            page.goto(base.rstrip("/") + caminho, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(3000)
            page.evaluate(f"window.__SELS__ = {json.dumps(PADRAO)}")
            anterior, mudancas = None, []
            for w in range(320, 1601, 10):
                page.set_viewport_size({"width": w, "height": 900})
                page.wait_for_timeout(60)
                sig = page.evaluate(ASSINATURA_JS)
                if anterior is not None:
                    dif = {k: [anterior[k], v] for k, v in sig.items() if anterior.get(k) != v and k != "container"}
                    if dif:
                        mudancas.append({"largura": w, "mudou": dif, "container": sig["container"]})
                anterior = sig
            saida[caminho] = mudancas
            print(caminho, [m["largura"] for m in mudancas])
        b.close()
    nome = "breakpoints_local.json" if base != BASE else "breakpoints.json"
    (RAW / nome).write_text(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
