"""Lê robots.txt e o sitemap para inventariar as páginas públicas."""

import re

from comum import BASE, get, salvar_json

status, robots = get(f"{BASE}/robots.txt")
print("robots", status)
print(robots)
sitemaps = re.findall(r"(?im)^sitemap:\s*(\S+)", robots) or [f"{BASE}/sitemap_index.xml"]
inventario = {"robots": robots, "sitemaps": {}}
for sm in sitemaps:
    st, xml = get(sm)
    filhos = re.findall(r"<loc>([^<]+)</loc>", xml)
    inventario["sitemaps"][sm] = {}
    print(sm, st, len(filhos))
    for filho in filhos:
        if filho.endswith(".xml"):
            st2, xml2 = get(filho)
            urls = re.findall(r"<loc>([^<]+)</loc>", xml2)
            inventario["sitemaps"][sm][filho] = urls
            print("  ", filho, st2, len(urls))
        else:
            inventario["sitemaps"][sm].setdefault("_urls", []).append(filho)
salvar_json("inventario.json", inventario)
