"""Exploração inicial do DOM: imprime o esqueleto de seções de uma página.

Uso: python explorar.py <url> [arquivo_saida]
Somente leitura; 1 navegação por execução; bloqueia scripts de rastreamento.
"""

import json
import sys

from comum import RAW, USER_AGENT, aguardar
from playwright.sync_api import sync_playwright

BLOQUEAR = ("googletagmanager", "google-analytics", "facebook", "fbcdn", "doubleclick", "clarity", "hotjar")

ESQUELETO_JS = r"""
() => {
  const out = [];
  const walk = (el, depth) => {
    if (depth > 18) return;
    for (const c of el.children) {
      const tag = c.tagName.toLowerCase();
      if (['script','style','noscript','svg','path','link','meta'].includes(tag)) continue;
      const r = c.getBoundingClientRect();
      if (r.height < 4 && !['header','nav','main','footer'].includes(tag)) continue;
      const cls = (c.className && c.className.baseVal === undefined ? c.className : '').toString().split(/\s+/).filter(x => !/^elementor/.test(x) && !/^e-/.test(x)).slice(0,5).join('.');
      const txt = (c.innerText || '').trim().replace(/\s+/g,' ').slice(0, 70);
      const isHead = /^h[1-4]$/.test(tag);
      const id = c.id ? '#' + c.id : '';
      const data = c.dataset && c.dataset.widget_type ? ' [' + c.dataset.widget_type + ']' : '';
      const cdaCls = /(^|\s)(cda|cia|ca)-/.test(c.className && c.className.baseVal === undefined ? c.className : '');
      if (isHead || cdaCls || ['header','nav','main','footer','section','form','button','a','ul','input','select','details','dialog','aside'].includes(tag) || data) {
        out.push('  '.repeat(depth) + tag + id + (cls ? '.' + cls : '') + data + ` ${Math.round(r.width)}x${Math.round(r.height)}` + (isHead || tag==='a' || tag==='button' ? ' «' + txt.slice(0,50) + '»' : ''));
      }
      if (!['a','button'].includes(tag) && !isHead) walk(c, depth + 1);
    }
  };
  walk(document.body, 0);
  return out;
}
"""


def main():
    url = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else None
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=USER_AGENT, viewport={"width": 1440, "height": 900}, locale="pt-BR")
        ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in BLOQUEAR) else r.continue_())
        page = ctx.new_page()
        aguardar()
        page.goto(url, wait_until="networkidle", timeout=90000)
        linhas = page.evaluate(ESQUELETO_JS)
        texto = "\n".join(linhas)
        if saida:
            (RAW / saida).write_text(texto)
            (RAW / (saida + ".html")).write_text(page.content())
        print(texto[:20000])
        b.close()


if __name__ == "__main__":
    print(json.dumps(sys.argv[1:]))
    main()
