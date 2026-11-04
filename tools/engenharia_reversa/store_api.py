"""Consulta a Store API pública do WooCommerce (poucas páginas, 1 req/2 s)."""

import json

from comum import BASE, get, salvar_json

st, cats = get(f"{BASE}/wp-json/wc/store/v1/products/categories?per_page=100")
print("categorias", st)
cats = json.loads(cats)
salvar_json("api_categorias.json", cats)
produtos = []
for pagina in (1, 2):
    st, body = get(f"{BASE}/wp-json/wc/store/v1/products?per_page=30&page={pagina}")
    print("produtos pag", pagina, st)
    produtos += json.loads(body)
salvar_json("api_produtos.json", produtos)
variavel = next((p for p in produtos if p.get("type") == "variable"), None)
if variavel:
    st, body = get(f"{BASE}/wp-json/wc/store/v1/products/{variavel['id']}")
    salvar_json("api_produto_variavel.json", json.loads(body))
    if variavel.get("variations"):
        vid = variavel["variations"][0]["id"]
        st, body = get(f"{BASE}/wp-json/wc/store/v1/products/{vid}")
        salvar_json("api_variacao.json", json.loads(body))
