"""Monta imagens lado a lado (referência | local) por tipo de página e viewport.

Saída em docs/validacao/lado-a-lado/ (fora do git: contém screenshots da referência, material de estudo).
Uso: uv run python tools/validacao/lado_a_lado.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[2]
REF = RAIZ / "docs/engenharia-reversa/screenshots"
LOC = RAIZ / "docs/validacao/screenshots"
SAIDA = RAIZ / "docs/validacao/lado-a-lado"
ALTURA_MAX = 6000


def montar(ref: Path, loc: Path, destino: Path, escala: float):
    a, b = Image.open(ref).convert("RGB"), Image.open(loc).convert("RGB")
    a = a.resize((int(a.width * escala), int(a.height * escala)))
    b = b.resize((int(b.width * escala), int(b.height * escala)))
    h = min(max(a.height, b.height), ALTURA_MAX)
    tela = Image.new("RGB", (a.width + b.width + 24, h + 40), "white")
    tela.paste(a.crop((0, 0, a.width, min(a.height, h))), (0, 40))
    tela.paste(b.crop((0, 0, b.width, min(b.height, h))), (a.width + 24, 40))
    d = ImageDraw.Draw(tela)
    d.text((8, 12), "REFERÊNCIA", fill="black")
    d.text((a.width + 32, 12), "ISF (local)", fill="black")
    destino.parent.mkdir(parents=True, exist_ok=True)
    tela.save(destino, optimize=True)


def main():
    total = 0
    for pasta in sorted(LOC.iterdir()):
        for vp, escala in (("1440", 0.4), ("768", 0.5), ("390", 0.7)):
            ref, loc = REF / pasta.name / f"{vp}.png", pasta / f"{vp}.png"
            if ref.exists() and loc.exists():
                montar(ref, loc, SAIDA / f"{pasta.name}-{vp}.png", escala)
                total += 1
    print(total, "imagens em", SAIDA)


if __name__ == "__main__":
    main()
