"""Lista as diferenças entre referência e ISF a partir de docs/validacao/raw/medidas.json.

Uso: uv run python tools/validacao/diferencas.py [viewport ...] [--md]
Ignora cores (a paleta é da ISF, divergência D1) e mostra só desvios relevantes:
fonte, peso, estilo, tamanho (> 0,5 px), entrelinha (> 1 px), espaçamento de letras,
caixa alta, padding, raio, alinhamento e caixa (x/w/h com tolerância de 6 %).
"""

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
dados = json.loads((RAIZ / "docs/validacao/raw/medidas.json").read_text())
args = [a for a in sys.argv[1:] if not a.startswith("--")]
vps = args or ["1440", "768", "390"]
TEXTO = ["fontFamily", "fontWeight", "fontStyle", "textTransform", "justifyContent"]
NUM = {"fontSize": 0.5, "lineHeight": 1.0, "letterSpacing": 0.3}


def px(v):
    m = re.match(r"(-?[\d.]+)px", str(v))
    return float(m.group(1)) if m else None


def diff(a, b):
    out = []
    for p in TEXTO:
        if a.get(p) != b.get(p):
            out.append(f"{p} {a.get(p)} → {b.get(p)}")
    for p, tol in NUM.items():
        x, y = px(a.get(p)), px(b.get(p))
        if x is None or y is None:
            if a.get(p) != b.get(p) and p != "lineHeight":
                out.append(f"{p} {a.get(p)} → {b.get(p)}")
        elif abs(x - y) > tol:
            out.append(f"{p} {x:g} → {y:g}")
    for p in ("padding", "borderRadius", "gap"):
        if a.get(p) != b.get(p):
            out.append(f"{p} {a.get(p)} → {b.get(p)}")
    for p in ("x", "w", "h"):
        x, y = a[p], b[p]
        if abs(x - y) > max(4, 0.06 * max(abs(x), abs(y))):
            out.append(f"{p} {x} → {y}")
    return out


total = 0
for pagina, lados in dados.items():
    for vp in vps:
        ref, isf = lados["ref"][vp], lados["isf"][vp]
        linhas = []
        for nome in ref:
            a, b = ref[nome], isf.get(nome)
            if a is None and b is None:
                continue
            if a is None or b is None:
                linhas.append(f"  {nome:20} {'(só no ISF)' if a is None else '(só na referência)'}")
                continue
            d = diff(a, b)
            if d:
                linhas.append(f"  {nome:20} " + " · ".join(d))
        total += len(linhas)
        print(f"\n## {pagina} @ {vp} ({len(linhas)} elementos com diferença)")
        print("\n".join(linhas))
print(f"\nTotal: {total}")
