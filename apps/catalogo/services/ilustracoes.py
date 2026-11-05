"""Ilustrações procedurais para o catálogo de demonstração (sem fotos de terceiros).

Cada produto de demonstração ganha uma "foto de estúdio" desenhada a partir de primitivas com
sombreamento cilíndrico (peças plásticas e metálicas), sombra projetada e supersampling. Há também
cenas de campo (pomar, estufa, horta, pastagem, casa de bombas) para as fotos de aplicação, o
portfólio, as coleções e o hero. Tudo é determinístico: o mesmo `desenho` gera a mesma imagem.

Uso:
    imagem = desenhar("gotejador_botao", variante=0, modo="produto")   # PIL.Image 900×900
    imagem = desenhar_cena("pomar", semente=3)
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from PIL import Image, ImageChops, ImageDraw, ImageFilter

LADO = 900
ESCALA = 2  # supersampling: desenha em 1800 px e reduz (bordas suaves)


# ---------------------------------------------------------------- cores
def rgb(hexa: str) -> tuple[int, int, int]:
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i : i + 2], 16) for i in (0, 2, 4))


def misturar(a, b, t: float):
    a, b = (rgb(a) if isinstance(a, str) else a), (rgb(b) if isinstance(b, str) else b)
    return tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))


def tom(cor, fator: float):
    cor = rgb(cor) if isinstance(cor, str) else cor
    if fator >= 1:
        return misturar(cor, (255, 255, 255), min(fator - 1, 1))
    return tuple(max(0, round(c * fator)) for c in cor)


PRETO_PE = "#2a2e2b"
GRAFITE = "#3b413d"
CINZA = "#8b928d"
BRANCO_PVC = "#eeeeea"
AZUL = "#2c69b0"
VERDE = "#1d6a44"
VERDE_CLARO = "#3f9a63"
VERMELHO = "#c33a2f"
LARANJA = "#e07a22"
LILAS = "#7b5aa6"
LATAO = "#c49a3f"
ALUMINIO = "#b9c0c4"
INOX = "#cfd5d8"
AMARELO = "#e9b324"


# ---------------------------------------------------------------- primitivas
def _perfil(n: int, luz: float = 0.32, contraste: float = 1.0) -> list[float]:
    """Multiplicadores de brilho ao longo de um cilindro (borda escura, faixa de luz em `luz`)."""
    valores = []
    for i in range(max(n, 1)):
        t = i / max(n - 1, 1)
        brilho = 0.86 + 0.34 * math.exp(-(((t - luz) / 0.16) ** 2))
        borda = 0.30 * (abs(t - 0.5) * 2) ** 2.6
        valores.append(1 + (brilho - borda - 1) * contraste)
    return valores


def _faixa(cor, n: int, luz: float, contraste: float, horizontal: bool) -> Image.Image:
    base = rgb(cor) if isinstance(cor, str) else cor
    pixels = [tom(base, f) for f in _perfil(n, luz, contraste)]
    faixa = Image.new("RGB", (n, 1) if not horizontal else (1, n))
    faixa.putdata(pixels)
    return faixa


def peca(w: float, h: float, cor, *, raio: float = 0, horizontal: bool = False, luz: float = 0.32,
         contraste: float = 1.0, forma: str = "ret", contorno: float = 0.55) -> Image.Image:  # fmt: skip
    """Peça sombreada (RGBA) em pixels de trabalho. forma: 'ret' (cantos `raio`) ou 'elipse'."""
    w, h = max(int(w), 2), max(int(h), 2)
    n = h if horizontal else w
    corpo = _faixa(cor, n, luz, contraste, horizontal).resize((w, h), Image.Resampling.BILINEAR)
    mascara = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mascara)
    if forma == "elipse":
        d.ellipse([0, 0, w - 1, h - 1], fill=255)
    else:
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(min(raio, w / 2, h / 2)), fill=255)
    camada = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    camada.paste(corpo, (0, 0), mascara)
    if contorno:
        linha = max(int(contorno * ESCALA), 1)
        borda = ImageChops.subtract(mascara, mascara.filter(ImageFilter.MinFilter(linha * 2 + 1)))
        escuro = Image.new("RGBA", (w, h), (*tom(cor, 0.55), 255))
        camada.paste(escuro, (0, 0), borda.point(lambda v: v * 0.55))
    return camada


def elipse_plana(w: float, h: float, cor, alfa: int = 255) -> Image.Image:
    w, h = max(int(w), 2), max(int(h), 2)
    camada = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(camada).ellipse([0, 0, w - 1, h - 1], fill=(*(rgb(cor) if isinstance(cor, str) else cor), alfa))
    return camada


class Objeto:
    """Camada RGBA do tamanho da tela onde as peças são montadas (coordenadas em unidades de 900)."""

    def __init__(self, lado: int = LADO, escala: int = ESCALA):
        self.e = escala
        self.lado = lado
        self.img = Image.new("RGBA", (lado * escala, lado * escala), (0, 0, 0, 0))

    def u(self, v: float) -> int:
        return round(v * self.e)

    def colar(self, camada: Image.Image, cx: float, cy: float, angulo: float = 0) -> None:
        if angulo:
            camada = camada.rotate(angulo, resample=Image.Resampling.BICUBIC, expand=True)
        x = self.u(cx) - camada.width // 2
        y = self.u(cy) - camada.height // 2
        self.img.alpha_composite(camada, (x, y)) if x >= 0 and y >= 0 else self.img.paste(camada, (x, y), camada)

    # atalhos em unidades de 900
    def cil(self, cx, cy, w, h, cor, raio=0, horizontal=False, angulo=0, **kw):
        self.colar(peca(self.u(w), self.u(h), cor, raio=self.u(raio), horizontal=horizontal, **kw), cx, cy, angulo)

    def eli(self, cx, cy, w, h, cor, angulo=0, **kw):
        self.colar(peca(self.u(w), self.u(h), cor, forma="elipse", **kw), cx, cy, angulo)

    def plana(self, cx, cy, w, h, cor, alfa=255):
        self.colar(elipse_plana(self.u(w), self.u(h), cor, alfa), cx, cy)

    def disco(self, cx, cy, w, altura, cor, angulo=0, tampa=None):
        """Cilindro curto visto de cima (3/4): lateral sombreada + tampo elíptico mais claro."""
        h_tampo = w * 0.42
        camada = Objeto(self.lado, self.e)
        camada.cil(cx, cy + altura / 2, w, altura, cor, raio=0)
        camada.eli(cx, cy + altura, w, h_tampo, cor, contraste=0.9)
        camada.eli(cx, cy, w, h_tampo, tom(tampa or cor, 1.12), luz=0.4, contraste=0.5)
        if angulo:
            caixa = camada.img.getbbox()
            if caixa:
                recorte = camada.img.crop(caixa)
                centro = ((caixa[0] + caixa[2]) / 2 / self.e, (caixa[1] + caixa[3]) / 2 / self.e)
                self.colar(recorte, *centro, angulo)
                return
        self.img.alpha_composite(camada.img)

    def tubo(self, x0, y0, x1, y1, espessura, cor, **kw):
        comprimento = math.hypot(x1 - x0, y1 - y0)
        angulo = -math.degrees(math.atan2(y1 - y0, x1 - x0))
        self.cil((x0 + x1) / 2, (y0 + y1) / 2, comprimento, espessura, cor, raio=espessura * 0.15,
                 horizontal=True, angulo=angulo, **kw)  # fmt: skip

    def espiga(self, cx, cy, comprimento, diametro, cor, angulo=0):
        """Conector de espiga (barb): anéis cônicos repetidos."""
        camada = Objeto(self.lado, self.e)
        passo = comprimento / 4
        for i in range(4):
            x = cx - comprimento / 2 + passo * (i + 0.5)
            camada.cil(x, cy, passo * 0.95, diametro * (1.0 if i % 2 == 0 else 0.82), cor, raio=diametro * 0.12,
                       horizontal=True)  # fmt: skip
        caixa = camada.img.getbbox()
        if caixa:
            recorte = camada.img.crop(caixa)
            centro = ((caixa[0] + caixa[2]) / 2 / self.e, (caixa[1] + caixa[3]) / 2 / self.e)
            self.colar(recorte, *centro, angulo)

    def rolo(self, cx, cy, diametro, largura, cor, *, furo=0.42, listras=None, pontos=None, inclinacao=0.55):
        """Bobina (fita, mangueira, tubo PE) vista em 3/4: corpo + face com espiras + furo."""
        h_face = diametro * inclinacao
        self.cil(cx, cy + largura / 2, diametro, largura, cor, raio=0, contraste=1.1)
        self.eli(cx, cy + largura, diametro, h_face, tom(cor, 0.9))
        self.eli(cx, cy, diametro, h_face, tom(cor, 1.06), luz=0.45, contraste=0.45)
        d = ImageDraw.Draw(self.img)
        espiras = 9
        for i in range(1, espiras):
            f = 1 - (1 - furo) * i / espiras
            w, h = diametro * f, h_face * f
            caixa = [self.u(cx - w / 2), self.u(cy - h / 2), self.u(cx + w / 2), self.u(cy + h / 2)]
            d.ellipse(caixa, outline=(*tom(cor, 0.72 if i % 2 else 1.22), 255), width=self.u(1.6))
        if listras:
            for k, ang in enumerate((200, 250, 300)):
                f = 0.97 - 0.05 * k
                caixa = [self.u(cx - diametro * f / 2), self.u(cy - h_face * f / 2),
                         self.u(cx + diametro * f / 2), self.u(cy + h_face * f / 2)]  # fmt: skip
                d.arc(caixa, ang, ang + 40, fill=(*rgb(listras), 255), width=self.u(3))
        w, h = diametro * furo, h_face * furo
        self.eli(cx, cy, w, h, "#d9d6cc", luz=0.7, contraste=0.6, contorno=0.8)
        self.plana(cx, cy + h * 0.12, w * 0.86, h * 0.7, "#c9c5b9")
        if pontos:  # emissores visíveis na lateral
            for i in range(7):
                x = cx - diametro * 0.42 + i * diametro * 0.14
                self.plana(x, cy + largura * 0.55 + h_face * 0.32 * math.sin(i / 7 * math.pi), 9, 6, pontos)

    def caixa(self, cx, cy, w, h, cor, raio=18, profundidade=14):
        """Caixa com tampo chanfrado (controladores, dosadores)."""
        self.cil(cx + profundidade * 0.4, cy + profundidade * 0.6, w, h, tom(cor, 0.7), raio=raio, contraste=0.3)
        self.cil(cx, cy, w, h, cor, raio=raio, luz=0.3, contraste=0.55)

    def ret(self, cx, cy, w, h, cor, raio=6, alfa=255):
        d = ImageDraw.Draw(self.img)
        caixa = [self.u(cx - w / 2), self.u(cy - h / 2), self.u(cx + w / 2), self.u(cy + h / 2)]
        d.rounded_rectangle(caixa, radius=self.u(raio), fill=(*(rgb(cor) if isinstance(cor, str) else cor), alfa))

    def arco(self, caixa, inicio, fim, cor, largura, alfa=255):
        d = ImageDraw.Draw(self.img)
        d.arc([self.u(v) for v in caixa], inicio, fim, fill=(*(rgb(cor) if isinstance(cor, str) else cor), alfa),
              width=self.u(largura))  # fmt: skip


# ---------------------------------------------------------------- fundos e composição
def _gradiente(w: int, h: int, topo, base) -> Image.Image:
    coluna = Image.new("RGB", (1, h))
    coluna.putdata([misturar(topo, base, y / max(h - 1, 1)) for y in range(h)])
    return coluna.resize((w, h), Image.Resampling.BILINEAR)


FUNDOS = {
    "produto": ("#f8f7f3", "#e9e7df"),
    "detalhe": ("#eef3ef", "#d9e4dc"),
    "categoria": ("#f4f1e8", "#e4dfd0"),
}


def _enquadrar(camada: Image.Image, ocupacao: float) -> Image.Image:
    """Centraliza o objeto e o escala para ocupar `ocupacao` do lado (peças pequenas e grandes no mesmo enquadramento)."""
    lado = camada.width
    caixa = camada.getbbox()
    if not caixa:
        return camada
    recorte = camada.crop(caixa)
    fator = ocupacao * lado / max(recorte.width, recorte.height * 1.08)
    recorte = recorte.resize(
        (max(int(recorte.width * fator), 1), max(int(recorte.height * fator), 1)), Image.Resampling.LANCZOS
    )
    nova = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    x = (lado - recorte.width) // 2
    y = int(lado * 0.47 - recorte.height / 2)
    nova.paste(recorte, (x, y), recorte)
    return nova


def _compor(objeto: Objeto, fundo: str, zoom: float = 1.0) -> Image.Image:
    lado = objeto.img.width
    camada = _enquadrar(objeto.img, 0.66 * zoom)
    topo, base = FUNDOS[fundo]
    tela = _gradiente(lado, lado, topo, base).convert("RGBA")
    # brilho suave atrás do objeto
    halo = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(halo).ellipse([lado * 0.12, lado * 0.06, lado * 0.88, lado * 0.82], fill=70)
    halo = halo.filter(ImageFilter.GaussianBlur(lado * 0.08))
    tela.paste(Image.new("RGBA", (lado, lado), (255, 255, 255, 255)), (0, 0), halo)
    alfa = camada.getchannel("A")
    caixa = alfa.getbbox()
    if caixa:
        # sombra de contato (elipse achatada na base) + sombra projetada (alfa desfocado)
        contato = Image.new("L", (lado, lado), 0)
        largura = (caixa[2] - caixa[0]) * 0.92
        cxb = (caixa[0] + caixa[2]) / 2
        ImageDraw.Draw(contato).ellipse(
            [cxb - largura / 2, caixa[3] - lado * 0.025, cxb + largura / 2, caixa[3] + lado * 0.03], fill=95
        )
        contato = contato.filter(ImageFilter.GaussianBlur(lado * 0.022))
        projetada = alfa.filter(ImageFilter.GaussianBlur(lado * 0.025)).point(lambda v: v * 0.22)
        projetada = ImageChops.offset(projetada, int(lado * 0.018), int(lado * 0.03))
        sombra = ImageChops.lighter(contato, projetada)
        tela.paste(Image.new("RGBA", (lado, lado), (*rgb("#2d342f"), 255)), (0, 0), sombra)
    tela.alpha_composite(camada)
    return tela.convert("RGB")


def _reduzir(imagem: Image.Image, lado_final: int) -> Image.Image:
    return imagem.resize((lado_final, lado_final), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------- produtos
def _gotejador_botao(o: Objeto, cor, v):
    posicoes = [(330, 470, -14), (560, 520, 18), (450, 330, 4)]
    for i, (x, y, ang) in enumerate(posicoes):
        cor_tampa = cor if i != 1 else tom(cor, 0.82)
        o.espiga(x - 6, y + 92, 70, 26, PRETO_PE, angulo=90 + ang)
        o.disco(x, y, 190, 46, PRETO_PE, tampa=cor_tampa, angulo=ang)
        o.plana(x + math.sin(math.radians(ang)) * 12, y - 2, 46, 20, tom(cor_tampa, 0.7))


def _gotejador_linha(o: Objeto, cor, v):
    for i, y in enumerate((360, 560)):
        x = 450 + (i * 2 - 1) * 40
        o.espiga(x - 205, y, 120, 34, PRETO_PE, angulo=0)
        o.espiga(x + 205, y, 120, 34, PRETO_PE, angulo=180)
        o.cil(x, y, 300, 92, cor if i == 0 else tom(cor, 0.85), raio=40, horizontal=True)
        o.cil(x, y, 70, 112, tom(cor, 0.75), raio=16, horizontal=True)
        for k in range(-3, 4):
            o.ret(x + k * 9, y, 3, 100, tom(cor, 0.6), raio=1)


def _gotejador_labirinto(o: Objeto, cor, v):
    for i, y in enumerate((380, 540)):
        x = 450 + (i * 2 - 1) * 30
        o.cil(x, y, 360, 70, cor if i == 0 else tom(cor, 0.88), raio=30, horizontal=True)
        for k in range(10):
            o.ret(x - 150 + k * 33, y + (-14 if k % 2 else 14), 26, 8, tom(cor, 0.62), raio=3)
        o.espiga(x - 225, y, 90, 30, PRETO_PE)
        o.espiga(x + 225, y, 90, 30, PRETO_PE, angulo=180)


def _gotejador_antidrenante(o: Objeto, cor, v):
    o.tubo(450, 560, 450, 760, 26, PRETO_PE)
    o.cil(450, 770, 14, 60, PRETO_PE, raio=7)
    o.disco(450, 430, 250, 60, PRETO_PE, tampa=cor)
    o.plana(450, 428, 70, 30, tom(cor, 0.68))
    o.espiga(450, 520, 80, 30, PRETO_PE, angulo=90)


def _fita(o: Objeto, cor, v):
    o.rolo(450, 380, 560, 150, cor, furo=0.38, listras=v.get("listra"), pontos=v.get("pontos"))


def _tubo_pe(o: Objeto, cor, v):
    o.rolo(450, 370, 600, 190, cor, furo=0.5, listras=v.get("listra"))
    o.tubo(700, 560, 820, 700, 46, cor)


def _tubos_pvc(o: Objeto, cor, v):
    for i in range(5):
        y = 300 + i * 70 + (i % 2) * 12
        x = 450 + (i % 2) * 30
        o.cil(x, y, 640, 64, cor, raio=8, horizontal=True, luz=0.3)
        o.eli(x - 320, y, 26, 64, tom(cor, 0.9))
        o.eli(x - 320, y, 18, 46, tom(cor, 0.6))
    o.ret(450, 650, 640, 4, tom(cor, 0.7), alfa=90)


def _mangueira_succao(o: Objeto, cor, v):
    o.rolo(450, 380, 580, 170, cor, furo=0.46, listras="#f4f4ef")
    for k in range(5):
        o.arco([450 - 290 + k * 6, 380 - 160 + k * 4, 450 + 290 - k * 6, 380 + 160 - k * 4], 15, 165, "#f4f4ef", 4, 200)


def _conector(o: Objeto, cor, v):
    tipo = v.get("tipo", "inicial")
    if tipo == "te":
        o.tubo(250, 450, 650, 450, 64, cor)
        o.tubo(450, 450, 450, 690, 64, cor)
        for x, y, ang in ((205, 450, 0), (695, 450, 180), (450, 735, 90)):
            o.espiga(x, y, 90, 52, cor, angulo=ang)
        o.cil(450, 450, 110, 110, tom(cor, 1.05), raio=30)
    elif tipo == "registro":
        o.tubo(230, 470, 670, 470, 58, cor)
        o.espiga(205, 470, 90, 50, cor)
        o.espiga(695, 470, 90, 50, cor, angulo=180)
        o.cil(450, 470, 150, 120, tom(cor, 1.04), raio=40)
        o.cil(450, 380, 52, 110, tom(cor, 0.9), raio=16)
        o.cil(450, 320, 260, 46, v.get("alavanca", AZUL), raio=23, horizontal=True)
    elif tipo == "colar":
        o.cil(450, 520, 640, 170, "#2f3431", raio=20, horizontal=True)
        o.cil(450, 470, 230, 250, cor, raio=30, contraste=0.8)
        o.cil(450, 330, 90, 120, tom(cor, 0.9), raio=18)
        for x in (370, 530):
            o.cil(x, 600, 34, 110, ALUMINIO, raio=8)
    elif tipo == "luva":
        o.cil(450, 470, 160, 78, cor, raio=20, horizontal=True)
        o.espiga(325, 470, 150, 58, cor)
        o.espiga(575, 470, 150, 58, cor, angulo=180)
    else:  # inicial com borracha
        for i, (x, y) in enumerate(((360, 430), (560, 520))):
            o.espiga(x + 120, y, 150, 50, cor, angulo=180)
            o.cil(x, y, 80, 92, cor, raio=18, horizontal=True)
            o.cil(x - 75, y, 70, 120, "#4d4f4b" if i == 0 else "#5a5c57", raio=24, horizontal=True, contraste=0.6)


def _microaspersor(o: Objeto, cor, v):
    tipo = v.get("tipo", "bailarina")
    for i, x in enumerate((330, 570)):
        topo = 300 if i == 0 else 340
        o.tubo(x, topo + 60, x, 780, 16, PRETO_PE)
        o.cil(x, 790, 8, 40, PRETO_PE, raio=4)
        o.arco([x - 120, topo + 40, x + 40, topo + 380], 180, 270, "#2f3431", 6)  # microtubo
        if tipo == "nebulizador":
            o.tubo(x - 90, topo, x + 90, topo, 26, cor)
            o.tubo(x, topo - 90, x, topo + 90, 26, cor)
            for dx, dy in ((-90, 0), (90, 0), (0, -90), (0, 90)):
                o.disco(x + dx, topo + dy, 46, 22, tom(cor, 0.8))
        else:
            o.cil(x, topo + 40, 46, 80, cor, raio=14)
            largura = 120 if tipo == "rotativo" else 92
            o.disco(x, topo - 10, largura, 30, tom(cor, 1.05), tampa=tom(cor, 1.15))
            if tipo in ("bailarina", "rotativo"):
                o.cil(x, topo - 40, 18, 40, tom(cor, 0.7), raio=6)
                o.disco(x, topo - 60, largura * 0.55, 14, tom(cor, 0.85))


def _aspersor_impacto(o: Objeto, cor, v):
    metal = v.get("metal", LATAO)
    o.cil(450, 700, 120, 120, metal, raio=12)
    o.eli(450, 640, 120, 44, tom(metal, 1.1))
    o.cil(450, 560, 90, 170, metal, raio=20)
    o.tubo(450, 520, 690, 380, 54, metal)
    o.cil(700, 375, 40, 64, tom(metal, 0.8), raio=10, angulo=30)
    o.tubo(450, 470, 300, 380, 36, metal)
    o.tubo(330, 400, 640, 300, 22, tom(metal, 0.85))  # braço
    o.cil(470, 330, 64, 30, tom(metal, 0.75), raio=8)
    o.arco([380, 380, 520, 480], 200, 340, "#9a9f9b", 6)  # mola


def _aspersor_setorial(o: Objeto, cor, v):
    o.cil(450, 690, 110, 140, PRETO_PE, raio=16)
    o.cil(450, 560, 150, 150, cor, raio=30)
    o.tubo(450, 520, 680, 420, 46, cor)
    o.cil(690, 415, 36, 56, tom(cor, 0.75), raio=10, angulo=24)
    o.disco(450, 470, 150, 30, tom(cor, 1.1))
    o.tubo(400, 470, 600, 380, 18, tom(cor, 0.7))


def _canhao(o: Objeto, cor, v):
    o.disco(450, 640, 380, 70, "#5d6560", tampa="#6d7570")
    o.cil(450, 560, 140, 150, cor, raio=20)
    o.tubo(430, 520, 760, 260, 74, cor)
    o.tubo(700, 300, 800, 220, 46, ALUMINIO)
    o.cil(450, 470, 200, 50, tom(cor, 0.8), raio=20, horizontal=True)
    o.tubo(330, 470, 250, 380, 26, tom(cor, 0.7))


def _escamoteavel(o: Objeto, cor, v):
    for x, sobe in ((340, 110), (580, 0)):
        o.cil(x, 560, 150, 330, PRETO_PE, raio=20)
        o.disco(x, 395, 150, 26, PRETO_PE, tampa="#3a3f3b")
        if sobe:
            o.cil(x, 395 - sobe / 2, 60, sobe, "#55605a", raio=12)
        o.disco(x, 395 - sobe, 110, 22, cor, tampa=tom(cor, 1.1))
        o.cil(x, 700, 70, 60, PRETO_PE, raio=10)


def _filtro(o: Objeto, cor, v):
    tipo = v.get("tipo", "disco")
    if tipo == "areia":
        for x in (330, 570):
            o.cil(x, 470, 200, 380, cor, raio=90, contraste=1.1)
            o.cil(x, 690, 18, 90, GRAFITE, raio=4)
            o.cil(x - 70, 690, 18, 90, GRAFITE, raio=4)
            o.cil(x + 70, 690, 18, 90, GRAFITE, raio=4)
            o.disco(x, 285, 90, 26, GRAFITE)
        o.tubo(210, 300, 690, 300, 46, GRAFITE)
        o.tubo(210, 610, 690, 610, 46, GRAFITE)
        return
    if tipo == "hidrociclone":
        o.cil(450, 300, 210, 160, cor, raio=50)
        triangulo = Image.new("L", (o.u(220), o.u(340)), 0)
        ImageDraw.Draw(triangulo).polygon([(0, 0), (o.u(220), 0), (o.u(130), o.u(340)), (o.u(90), o.u(340))], fill=255)
        cone = peca(o.u(220), o.u(340), cor)
        cone.putalpha(ImageChops.multiply(cone.getchannel("A"), triangulo))
        o.colar(cone, 450, 520)
        o.cil(450, 720, 60, 70, GRAFITE, raio=10)
        o.tubo(250, 300, 450, 300, 56, GRAFITE)
        o.cil(450, 200, 70, 70, GRAFITE, raio=12)
        return
    # disco ou tela: carcaça vertical com tampa colorida e entradas laterais
    tampa = v.get("tampa", VERMELHO)
    o.tubo(150, 560, 750, 560, 70, GRAFITE)
    o.espiga(130, 560, 70, 64, GRAFITE)
    o.espiga(770, 560, 70, 64, GRAFITE, angulo=180)
    o.cil(450, 560, 250, 180, "#3a3f3c", raio=30)
    o.cil(450, 400, 230, 260, tampa, raio=60, contraste=1.1)
    o.cil(450, 470, 250, 40, tom(tampa, 0.75), raio=16, horizontal=True)
    o.disco(450, 270, 120, 34, tom(tampa, 0.9))
    o.cil(450, 690, 70, 80, "#3a3f3c", raio=12)
    if tipo == "tela":
        for k in range(-3, 4):
            o.ret(450 + k * 26, 400, 6, 190, tom(tampa, 0.82), raio=3)


def _controlador(o: Objeto, cor, v):
    setores = v.get("setores", 6)
    if setores == 1:  # a bateria, junto da válvula
        o.cil(450, 540, 300, 300, cor, raio=60)
        o.ret(450, 470, 190, 110, "#20302a", raio=14)
        o.ret(450, 470, 170, 90, "#7fbf9a", raio=10, alfa=230)
        for k, x in enumerate((390, 450, 510)):
            o.disco(x, 590, 44, 12, AZUL if k == 1 else "#d9dcd8")
        return
    o.caixa(450, 450, 520, 400, cor, raio=36, profundidade=22)
    o.ret(370, 380, 260, 140, "#1c2a24", raio=14)
    o.ret(370, 380, 236, 116, "#86c9a1", raio=8, alfa=235)
    for k in range(4):
        o.ret(300 + k * 44, 372, 30, 46, "#1c2a24", raio=4, alfa=200)
    o.disco(600, 380, 130, 30, "#3a3f3c", tampa="#e9ebe7")
    for k in range(setores):
        x = 260 + (k % 6) * 72
        o.disco(x, 540, 48, 12, VERDE_CLARO if k == 0 else "#d9dcd8")
    o.ret(450, 610, 420, 8, tom(cor, 0.8), raio=4)


def _valvula(o: Objeto, cor, v):
    o.tubo(180, 560, 720, 560, 76, cor)
    o.cil(450, 560, 300, 200, cor, raio=60)
    o.disco(450, 450, 260, 40, tom(cor, 0.9))
    o.cil(450, 350, 120, 170, PRETO_PE, raio=24)
    o.disco(450, 268, 90, 20, "#3a3f3c")
    o.arco([300, 230, 470, 420], 180, 300, "#d23b2f", 6)
    o.arco([290, 250, 470, 440], 180, 300, PRETO_PE, 6)
    for x in (230, 670):
        o.cil(x, 560, 80, 120, tom(cor, 0.85), raio=20)


def _sensor_chuva(o: Objeto, cor, v):
    o.tubo(300, 650, 540, 430, 34, GRAFITE)
    o.cil(290, 660, 90, 120, GRAFITE, raio=20)
    o.cil(560, 420, 170, 150, cor, raio=40)
    o.disco(560, 335, 210, 36, tom(cor, 0.85), tampa="#dfe3df")
    o.arco([180, 600, 420, 860], 270, 360, "#2f3431", 6)


def _bomba(o: Objeto, cor, v):
    tamanho = v.get("tamanho", 1.0)
    if v.get("tipo") == "submersa":
        o.cil(450, 260, 110, 90, AZUL, raio=20)
        o.cil(450, 500, 150, 420, INOX, raio=34, contraste=1.2)
        for k in range(8):
            o.ret(450, 340 + k * 24, 150, 5, tom(INOX, 0.72), raio=2)
        o.cil(450, 735, 120, 60, tom(INOX, 0.85), raio=18)
        o.arco([450, 160, 650, 420], 270, 360, "#2f3431", 7)
        return
    s = tamanho
    o.cil(450, 690, 520 * s, 40, GRAFITE, raio=10, horizontal=True)
    o.cil(540, 520, 420 * s, 260 * s, cor, raio=60 * s, horizontal=True, contraste=1.1)
    for k in range(8):
        o.ret(560 + k * 22 * s, 520, 6, 210 * s, tom(cor, 0.72), raio=3)
    o.cil(780, 520, 60, 200 * s, tom(cor, 0.8), raio=24, horizontal=True)
    o.disco(270, 470, 300 * s, 170 * s, tom(cor, 0.92), tampa=tom(cor, 1.05), angulo=90)
    o.cil(255, 300, 110 * s, 140, tom(cor, 0.9), raio=16)
    o.disco(255, 230, 140 * s, 24, GRAFITE)
    o.cil(130, 470, 120, 100 * s, tom(cor, 0.9), raio=16, horizontal=True)


def _venturi(o: Objeto, cor, v):
    o.tubo(160, 470, 740, 470, 80, cor)
    o.cil(450, 470, 220, 120, tom(cor, 1.05), raio=40, horizontal=True)
    o.tubo(450, 470, 450, 720, 40, cor)
    o.arco([450, 640, 760, 900], 180, 270, "#9fd0b5", 14, 200)  # mangueira de sucção translúcida
    for x in (190, 710):
        o.cil(x, 470, 60, 110, tom(cor, 0.85), raio=14)


def _dosadora(o: Objeto, cor, v):
    if v.get("tipo") == "proporcional":
        o.cil(450, 520, 230, 460, "#dfe8e3", raio=60, contraste=0.6)
        o.cil(450, 520, 150, 380, "#b9d8c6", raio=40, contraste=0.5)
        o.cil(450, 270, 270, 110, cor, raio=40)
        o.tubo(230, 270, 670, 270, 56, PRETO_PE)
        o.cil(450, 760, 40, 60, PRETO_PE, raio=8)
        return
    o.caixa(450, 460, 440, 360, cor, raio=40, profundidade=20)
    o.disco(370, 420, 170, 34, "#e9ebe7", tampa="#ffffff")
    o.ret(370, 416, 8, 60, VERMELHO, raio=3)
    o.ret(570, 380, 120, 70, "#1c2a24", raio=10)
    o.ret(570, 380, 100, 52, "#86c9a1", raio=6, alfa=235)
    o.tubo(450, 640, 450, 760, 30, "#cfe5d8")
    o.tubo(600, 640, 700, 780, 30, "#cfe5d8")


def _kit(o: Objeto, cor, v):
    itens = v.get("itens", ["fita", "filtro", "conector"])
    caixa = Objeto(o.lado, o.e)
    caixa.cil(450, 640, 700, 200, "#c8a979", raio=12, contraste=0.5)
    caixa.ret(450, 545, 700, 14, "#b2925f", raio=4)
    caixa.ret(450, 640, 220, 60, "#f4efe4", raio=8, alfa=240)
    caixa.ret(420, 640, 120, 12, VERDE, raio=4)
    caixa.ret(470, 662, 160, 8, "#9a8a6a", raio=4)
    o.img.alpha_composite(caixa.img)
    posicoes = {0: (300, 400, 0.55), 1: (560, 360, 0.5), 2: (650, 520, 0.4)}
    for i, item in enumerate(itens[:3]):
        x, y, s = posicoes[i]
        sub = Objeto(o.lado, o.e)
        construtor, cor_item, var = KIT_ITENS[item]
        construtor(sub, cor_item, var)
        recorte_caixa = sub.img.getbbox()
        if not recorte_caixa:
            continue
        recorte = sub.img.crop(recorte_caixa)
        recorte = recorte.resize(
            (max(int(recorte.width * s), 2), max(int(recorte.height * s), 2)), Image.Resampling.LANCZOS
        )
        o.colar(recorte, x, y)


KIT_ITENS: dict[str, tuple[Callable, str, dict]] = {
    "fita": (_fita, PRETO_PE, {"listra": AZUL}),
    "filtro": (_filtro, "#3a3f3c", {"tipo": "disco", "tampa": VERMELHO}),
    "conector": (_conector, PRETO_PE, {"tipo": "registro"}),
    "microaspersor": (_microaspersor, AZUL, {"tipo": "bailarina"}),
    "tubo": (_tubo_pe, PRETO_PE, {}),
    "escamoteavel": (_escamoteavel, VERDE_CLARO, {}),
    "controlador": (_controlador, "#e8ebe8", {"setores": 6}),
    "nebulizador": (_microaspersor, CINZA, {"tipo": "nebulizador"}),
    "valvula": (_valvula, "#2f3431", {}),
}

DESENHOS: dict[str, Callable] = {
    "gotejador_botao": _gotejador_botao,
    "gotejador_linha": _gotejador_linha,
    "gotejador_labirinto": _gotejador_labirinto,
    "gotejador_antidrenante": _gotejador_antidrenante,
    "fita": _fita,
    "tubo_pe": _tubo_pe,
    "tubos_pvc": _tubos_pvc,
    "mangueira_succao": _mangueira_succao,
    "conector": _conector,
    "microaspersor": _microaspersor,
    "aspersor_impacto": _aspersor_impacto,
    "aspersor_setorial": _aspersor_setorial,
    "canhao": _canhao,
    "escamoteavel": _escamoteavel,
    "filtro": _filtro,
    "controlador": _controlador,
    "valvula": _valvula,
    "sensor_chuva": _sensor_chuva,
    "bomba": _bomba,
    "venturi": _venturi,
    "dosadora": _dosadora,
    "kit": _kit,
}


def desenhar(desenho: str, cor: str, opcoes: dict | None = None, *, modo: str = "produto",
             lado: int = LADO, rapido: bool = False) -> Image.Image:  # fmt: skip
    """Foto de estúdio do produto. modo: 'produto', 'detalhe' (aproximada) ou 'categoria'."""
    escala = 1 if rapido else ESCALA
    o = Objeto(LADO, escala)
    DESENHOS[desenho](o, cor, opcoes or {})
    imagem = _compor(o, "detalhe" if modo == "detalhe" else modo, zoom=1.7 if modo == "detalhe" else 1.0)
    return _reduzir(imagem, lado)


# ---------------------------------------------------------------- cenas de campo
def _ceu(lado, e, rnd: random.Random, entardecer=False):
    horizonte = int(lado * e * rnd.uniform(0.36, 0.44))
    topo, base = ("#f2c48d", "#fbe9cf") if entardecer else ("#9cc7e6", "#e6f1f6")
    ceu = _gradiente(lado * e, horizonte, topo, base)
    sol = Image.new("L", ceu.size, 0)
    sx = rnd.uniform(0.15, 0.85) * ceu.width
    ImageDraw.Draw(sol).ellipse([sx - 90 * e, horizonte * 0.25, sx + 90 * e, horizonte * 0.25 + 180 * e], fill=150)
    sol = sol.filter(ImageFilter.GaussianBlur(60 * e))
    ceu.paste((255, 250, 235), (0, 0), sol)
    return ceu, horizonte


def _morros(tela: Image.Image, horizonte: int, cor, rnd: random.Random, e: int):
    d = ImageDraw.Draw(tela)
    w = tela.width
    pontos = [(0, horizonte)]
    for i in range(9):
        pontos.append((w * i / 8, horizonte - rnd.uniform(18, 70) * e))
    pontos += [(w, horizonte), (w, horizonte + 4 * e), (0, horizonte + 4 * e)]
    d.polygon(pontos, fill=cor)


def _linhas_plantio(tela, horizonte, e, rnd, cor_solo, cor_planta, *, linhas=11, arvore=False, gotejo=True,
                    nevoa=False, jatos=False, mostrar_plantas=True):  # fmt: skip
    w, h = tela.size
    d = ImageDraw.Draw(tela, "RGBA")
    fuga = (w * rnd.uniform(0.42, 0.58), horizonte - 30 * e)
    d.rectangle([0, horizonte, w, h], fill=cor_solo)
    # faixas de entrelinha (grama) alternadas
    for i in range(-linhas, linhas + 1):
        x_base = w / 2 + i * w / linhas * 0.9
        prox = x_base + w / linhas * 0.45
        d.polygon([fuga, (x_base, h), (prox, h)], fill=(*tom(cor_solo, 1.08), 110))
    for i in range(-linhas, linhas + 1):
        x_base = w / 2 + (i + 0.5) * w / linhas * 0.9
        for k in range(26 if not arvore else 9):
            t = (k / (26 if not arvore else 9)) ** 1.6
            y = horizonte + (h - horizonte) * t
            x = fuga[0] + (x_base - fuga[0]) * t
            if not -40 * e < x < w + 40 * e:
                continue
            escala = 0.15 + t
            if arvore and t < 0.08:
                continue
            if not mostrar_plantas:
                continue
            if arvore:
                r = 70 * e * escala
                d.ellipse([x - r * 0.12, y - r * 0.3, x + r * 0.12, y + r * 0.2], fill=(*tom("#6b4a2b", 0.9), 255))
                d.ellipse(
                    [x - r, y - r * 1.9, x + r, y - r * 0.2], fill=(*tom(cor_planta, 0.85 + 0.3 * rnd.random()), 255)
                )
                d.ellipse([x - r * 0.6, y - r * 1.8, x + r * 0.3, y - r * 1.0], fill=(*tom(cor_planta, 1.25), 120))
                if nevoa:
                    d.ellipse([x - r * 1.3, y - r * 0.25, x + r * 1.3, y + r * 0.25], fill=(255, 255, 255, 70))
            else:
                r = 16 * e * escala
                d.ellipse([x - r, y - r * 1.4, x + r, y], fill=(*tom(cor_planta, 0.8 + 0.4 * rnd.random()), 255))
        if gotejo:
            x0 = fuga[0] + (x_base - fuga[0]) * 0.02
            d.line([(x0, horizonte + 2), (x_base, h)], fill=(30, 32, 30, 200), width=max(int(2.5 * e), 1))
        if jatos:
            pass
    if jatos:
        for _ in range(5):
            x = rnd.uniform(0.15, 0.85) * w
            y = rnd.uniform(horizonte + 60 * e, h - 80 * e)
            raio = (y - horizonte) * 0.9
            for k in range(6):
                d.arc([x - raio, y - raio * 0.7, x + raio, y + raio * 0.7], 200 + k * 4, 340 - k * 4,
                      fill=(255, 255, 255, 120 - k * 15), width=max(int(3 * e), 1))  # fmt: skip


def _estufa(tela, horizonte, e, rnd):
    w, h = tela.size
    d = ImageDraw.Draw(tela, "RGBA")
    d.rectangle([0, int(h * 0.12), w, h], fill=(236, 240, 236, 255))
    for i in range(7):  # bancadas em perspectiva
        y = h * 0.55 + i * h * 0.065
        d.rectangle(
            [w * 0.05 - i * 20 * e, y, w * 0.95 + i * 20 * e, y + 26 * e], fill=(*tom("#8c7b62", 0.9 + i * 0.03), 255)
        )
        for k in range(18):
            x = w * 0.06 + k * w * 0.05
            r = (10 + i * 3) * e
            d.ellipse([x - r, y - r * 1.6, x + r, y + 2], fill=(*tom(VERDE_CLARO, 0.8 + 0.4 * rnd.random()), 255))
    d.rectangle([0, 0, w, int(h * 0.12)], fill=(226, 232, 228, 255))
    for k in range(5):  # arcos e pilares da cobertura
        x = w * (k + 0.5) / 5
        d.arc([x - w * 0.1, h * 0.06, x + w * 0.1, h * 0.3], 180, 360, fill=(190, 198, 194, 255), width=int(3 * e))
        d.line([(x - w * 0.1, h * 0.18), (x - w * 0.1, h * 0.55)], fill=(190, 198, 194, 255), width=int(3 * e))
    d.rectangle([0, 0, w, h], fill=(255, 255, 255, 50))
    for _ in range(40):  # névoa dos nebulizadores
        x, y = rnd.uniform(0, w), rnd.uniform(h * 0.2, h * 0.5)
        r = rnd.uniform(40, 110) * e
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(255, 255, 255, 40))


CENAS = {
    "horta": {"solo": "#8a6a48", "planta": "#4f9a55", "linhas": 12, "gotejo": True},
    "cafe": {"solo": "#7a5a3e", "planta": "#2f6b3a", "linhas": 4, "arvore": True, "gotejo": True},
    "pomar": {"solo": "#86744f", "planta": "#3e7d3f", "linhas": 3, "arvore": True, "gotejo": False, "nevoa": True},
    "pastagem": {"solo": "#6f9a4a", "planta": "#88b65a", "linhas": 9, "gotejo": False, "jatos": True, "plantas": False},
    "graos": {"solo": "#9b8a50", "planta": "#b9a542", "linhas": 14, "gotejo": False, "jatos": True},
    "gramado": {"solo": "#5f9b4c", "planta": "#79b55d", "linhas": 8, "gotejo": False, "jatos": True, "plantas": False},
    "fruticultura": {"solo": "#8d6c4a", "planta": "#356f36", "linhas": 4, "arvore": True, "gotejo": True},
}


def desenhar_cena(cena: str, semente: int = 0, *, lado: int = LADO, rapido: bool = False,
                  produto: tuple[str, str, dict] | None = None) -> Image.Image:  # fmt: skip
    """Cena de aplicação. `cena`: chave de CENAS, 'estufa' ou 'instalacao' (casa de bombas com `produto`)."""
    e = 1 if rapido else ESCALA
    rnd = random.Random(f"{cena}-{semente}")  # noqa: S311 — variação visual determinística, sem uso de segurança
    tela = Image.new("RGB", (LADO * e, LADO * e))
    if cena == "estufa":
        _estufa(tela, 0, e, rnd)
    else:
        ceu, horizonte = _ceu(LADO, e, rnd, entardecer=rnd.random() < 0.25)
        tela.paste(ceu, (0, 0))
        _morros(tela, horizonte, tom("#6f8f73", rnd.uniform(0.9, 1.1)), rnd, e)
        if cena == "instalacao":
            d = ImageDraw.Draw(tela)
            d.rectangle([0, horizonte, tela.width, tela.height], fill=tom("#7f9a5a", 1.0))
            _linhas_plantio(tela, horizonte, e, rnd, "#8a6a48", "#4f9a55", linhas=10)
            base_y = int(tela.height * 0.62)
            d.rectangle([0, base_y, tela.width, tela.height], fill=(196, 192, 182))
            d.rectangle([0, base_y, tela.width, base_y + 10 * e], fill=(170, 166, 156))
            d.rectangle(
                [int(tela.width * 0.04), int(tela.height * 0.30), int(tela.width * 0.3), base_y], fill=(214, 206, 190)
            )
            d.polygon([(tela.width * 0.02, tela.height * 0.31), (tela.width * 0.17, tela.height * 0.22),
                       (tela.width * 0.32, tela.height * 0.31)], fill=(150, 72, 52))  # fmt: skip
            if produto:
                o = Objeto(LADO, e)
                construtor, cor, opcoes = produto
                DESENHOS[construtor](o, cor, opcoes)
                caixa = o.img.getbbox()
                if caixa:
                    recorte = o.img.crop(caixa)
                    alvo = int(tela.width * 0.46)
                    fator = alvo / max(recorte.width, recorte.height)
                    recorte = recorte.resize(
                        (int(recorte.width * fator), int(recorte.height * fator)), Image.Resampling.LANCZOS
                    )
                    x = int(tela.width * 0.62 - recorte.width / 2)
                    y = int(base_y + tela.height * 0.2 - recorte.height)
                    sombra = recorte.getchannel("A").filter(ImageFilter.GaussianBlur(14 * e)).point(lambda v: v * 0.35)
                    tela.paste((60, 60, 55), (x + 12 * e, y + 18 * e), sombra)
                    tela.paste(recorte, (x, y), recorte)
                    d.rectangle([0, int(y + recorte.height * 0.55), x + 10 * e, int(y + recorte.height * 0.55) + 26 * e],
                                fill=(52, 56, 53))  # fmt: skip
        else:
            p = CENAS[cena]
            _linhas_plantio(tela, horizonte, e, rnd, p["solo"], p["planta"], linhas=p["linhas"],
                            arvore=p.get("arvore", False), gotejo=p.get("gotejo", True),
                            nevoa=p.get("nevoa", False), jatos=p.get("jatos", False),
                            mostrar_plantas=p.get("plantas", True))  # fmt: skip
    # luz quente e vinheta suave: aspecto de foto
    vinheta = Image.new("L", tela.size, 0)
    ImageDraw.Draw(vinheta).ellipse(
        [-tela.width * 0.2, -tela.height * 0.1, tela.width * 1.2, tela.height * 1.15], fill=255
    )
    vinheta = vinheta.filter(ImageFilter.GaussianBlur(tela.width * 0.12))
    escura = Image.new("RGB", tela.size, (28, 34, 30))
    tela = Image.composite(tela, escura, vinheta.point(lambda v: 150 + v * 105 // 255))
    return _reduzir(tela, lado)
