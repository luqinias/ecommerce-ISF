"""Conteúdo de demonstração da home e das páginas. Genérico e marcado: nada de dado real inventado.

- Sem depoimentos (só entram com autorização do cliente: pendência P17).
- Portfólio com placeholders "Projeto de exemplo" (P11).
- Textos que dependem da empresa ficam como [DEFINIR] (P3, P5, P18).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from django.core.files import File
from django.db import transaction

from apps.catalogo.services.demo import gerar_placeholder
from apps.conteudo.models import Banner, FAQItem, Highlight, HowItWorksStep, Page, PageSection, PortfolioItem

PROVAS = [
    ("users", "Atendimento técnico", "[DEFINIR] Quem atende e como ajuda a dimensionar o sistema."),
    ("truck", "Entrega", "[DEFINIR] Regiões e prazos de entrega."),
    ("shield", "Produtos de qualidade", "[DEFINIR] Marcas e garantias trabalhadas."),
]
POR_QUE = [
    ("users", "Atendimento de quem entende", "[DEFINIR] Diferencial de atendimento."),
    ("sprout", "Projeto para a sua cultura", "[DEFINIR] Como a equipe dimensiona o sistema."),
    ("truck", "Entrega no campo", "[DEFINIR] Logística e prazos."),
    ("shield", "Suporte depois da compra", "[DEFINIR] Pós-venda e assistência."),
]
PASSOS = [
    ("Escolha os produtos", "Navegue pelo catálogo, escolha as opções e as quantidades e monte a sua lista."),
    ("Peça o orçamento", "Envie a lista pelo site ou pelo WhatsApp. Sem preço público: a proposta é feita para você."),
    ("Ajuste técnico", "A equipe confere o dimensionamento e sugere ajustes antes de fechar."),
    ("Entrega", "[DEFINIR] Como e em quanto tempo o pedido chega."),
]
FAQ_HOME = [
    (
        "Qual é a quantidade mínima de compra?",
        "Cada produto mostra na página a quantidade mínima e o múltiplo de venda (por exemplo, rolos ou caixas). Você ajusta as quantidades na lista antes de enviar.",
    ),
    (
        "Por que o site não mostra preços?",
        "Os valores dependem da quantidade, do projeto e da região de entrega. Por isso você monta a lista e recebe uma proposta personalizada.",
    ),
    (
        "Como faço para pedir um orçamento?",
        "Adicione os produtos à lista de orçamento, revise as quantidades e envie seus dados. Você recebe a confirmação por e-mail e pode continuar a conversa pelo WhatsApp.",
    ),
    ("Vocês ajudam a dimensionar o sistema?", "[DEFINIR] Como funciona o apoio técnico para projetos."),
    ("Para quais regiões vocês entregam?", "[DEFINIR] Área de atendimento e prazos."),
]
FAQ_CONTATO = [
    ("Quanto tempo leva para receber o orçamento?", "[DEFINIR] Prazo de resposta da equipe."),
    ("Quais são as formas de pagamento?", "[DEFINIR] Formas de pagamento aceitas."),
    (
        "Posso enviar a lista de materiais de um projeto?",
        "Sim. Use o formulário ou o WhatsApp e envie a lista ou as fotos; a equipe monta a proposta a partir dela.",
    ),
]

PRIVACIDADE = [
    (
        "Quem cuida dos seus dados",
        "controlador",
        "[DEFINIR] Razão social, CNPJ e contato do responsável pelos dados (encarregado).",
    ),
    (
        "Quais dados coletamos",
        "dados",
        "Quando você pede um orçamento ou manda uma mensagem, coletamos os dados que você informa:\n- nome, empresa ou propriedade;\n- e-mail e telefone/WhatsApp;\n- cidade e UF;\n- a mensagem e os produtos da lista.\n\nNão pedimos documentos, dados de pagamento nem dados sensíveis.",
    ),
    (
        "Para que usamos",
        "finalidades",
        "Usamos esses dados só para responder ao seu pedido de orçamento ou mensagem e para conversar com você sobre ele. A base legal é o seu consentimento, registrado no envio do formulário, e a execução de procedimentos preliminares a um contrato a seu pedido.",
    ),
    (
        "Cookies",
        "cookies",
        'O site usa cookies necessários para funcionar: sessão (guarda a sua lista de orçamento), proteção contra fraude em formulários (CSRF) e o registro da sua escolha sobre cookies.\n\nCookies de medição e de anúncios (Google Tag Manager e Meta Pixel, quando configurados) só são carregados se você clicar em "Aceitar todos". Você pode mudar a escolha a qualquer momento em "Preferências de cookies", no rodapé.',
    ),
    (
        "Com quem compartilhamos",
        "compartilhamento",
        "[DEFINIR] Fornecedores que tratam dados em nome da empresa (por exemplo, hospedagem e envio de e-mail).",
    ),
    ("Por quanto tempo guardamos", "prazo", "[DEFINIR] Prazo de guarda dos pedidos de orçamento."),
    (
        "Seus direitos",
        "direitos",
        "Você pode pedir acesso, correção, anonimização ou exclusão dos seus dados e revogar o consentimento, pelos canais da página de contato.",
    ),
]
TERMOS = [
    ("Quem somos", "quem-somos", "[DEFINIR] Identificação da empresa."),
    (
        "Como o site funciona",
        "site",
        "O site é um catálogo. Ele não mostra preços e não vende online: você monta uma lista de orçamento e a equipe responde com uma proposta. O pedido só é fechado depois da proposta aceita.\n\nFotos podem ser ilustrativas e especificações podem mudar; confirme na proposta.",
    ),
    ("Orçamento e proposta", "orcamento", "[DEFINIR] Validade da proposta, condições comerciais e de entrega."),
    (
        "Uso do site",
        "uso",
        "Ao usar o site, você se compromete a informar dados verdadeiros nos formulários e a não tentar prejudicar o funcionamento dele.",
    ),
    ("Lei aplicável e foro", "foro", "[DEFINIR] Foro e legislação aplicável."),
]


def _imagem(pasta: Path, nome: str, titulo: str, cores=("#1d6a44", "#e2efe7"), ambiente=True) -> File:
    caminho = pasta / nome
    gerar_placeholder(caminho, titulo, "Imagem ilustrativa", cores, ambiente)
    return File(caminho.open("rb"), name=nome)


@transaction.atomic
def carregar(*, se_vazio: bool = False) -> bool:
    if se_vazio and (Banner.objects.exists() or Page.objects.exists()):
        return False
    with tempfile.TemporaryDirectory(prefix="isf-conteudo-") as tmp:
        pasta = Path(tmp)
        banner = Banner(
            badge_label="Coleções",
            title="Produtos de irrigação com orçamento rápido.",
            highlight="orçamento rápido",
            subtitle="Monte a sua lista com produtos e quantidades e receba a proposta pelo WhatsApp ou e-mail. [DEFINIR] proposta de valor da Irrigação Sem Fronteiras.",
            caption_main="Gotejamento", caption_2="Filtragem", caption_3="Automação", is_demo=True,
        )  # fmt: skip
        banner.image_main.save("hero-1.png", _imagem(pasta, "hero-1.png", "Gotejamento"), save=False)
        banner.image_2.save(
            "hero-2.png", _imagem(pasta, "hero-2.png", "Filtragem", ("#9a6400", "#f6deaa"), False), save=False
        )
        banner.image_3.save(
            "hero-3.png", _imagem(pasta, "hero-3.png", "Automacao", ("#1d5fa8", "#b9d3f0"), False), save=False
        )
        banner.save()
        for i in range(10):
            item = PortfolioItem(
                title=f"Projeto de exemplo {i + 1}",
                subtitle="[DEFINIR] cultura · cidade/UF",
                tall=i in (0, 1, 6, 7),
                featured=i == 0,
                order=i,
                is_demo=True,
            )
            item.image.save(
                f"portfolio-{i + 1}.png",
                _imagem(pasta, f"portfolio-{i + 1}.png", f"Projeto de exemplo {i + 1}"),
                save=False,
            )
            item.save()
    for n, (icone, titulo, texto) in enumerate(PROVAS):
        Highlight.objects.create(placement=Highlight.Placement.PROOF, icon=icone, title=titulo, text=texto, order=n)
    for n, (icone, titulo, texto) in enumerate(POR_QUE):
        Highlight.objects.create(placement=Highlight.Placement.WHY, icon=icone, title=titulo, text=texto, order=n)
    for n, (titulo, texto) in enumerate(PASSOS):
        HowItWorksStep.objects.create(title=titulo, text=texto, order=n)
    for n, (p, r) in enumerate(FAQ_HOME):
        FAQItem.objects.create(placement=FAQItem.Placement.HOME, question=p, answer=r, order=n)
    for n, (p, r) in enumerate(FAQ_CONTATO):
        FAQItem.objects.create(placement=FAQItem.Placement.CONTACT, question=p, answer=r, order=n)
    sobre = Page.objects.create(slug="sobre", kind=Page.Kind.ABOUT, kicker="Sobre a ISF", title="Irrigação Sem Fronteiras", highlight="Sem Fronteiras",
                                lead="[DEFINIR] Apresentação da empresa: história, missão e área de atuação.", is_demo=True)  # fmt: skip
    for n, (t, b) in enumerate(
        [
            ("Nossa história", "[DEFINIR] História da empresa."),
            ("O que fazemos", "[DEFINIR] Linhas de produto e serviços."),
            ("Onde atendemos", "[DEFINIR] Regiões e culturas atendidas."),
        ]
    ):
        PageSection.objects.create(page=sobre, title=t, body=b, order=n)
    for slug, titulo, destaque, kicker, lead, secoes in (
        ("politica-de-privacidade", "Seus dados, com cuidado e só para o necessário", "só para o necessário", "Política de privacidade", "Como tratamos os dados que você informa no site.", PRIVACIDADE),
        ("termos-de-uso", "Como funciona o site", "o site", "Termos de uso", "As regras para usar o catálogo e pedir orçamento.", TERMOS),
    ):  # fmt: skip
        pagina = Page.objects.create(slug=slug, kind=Page.Kind.LEGAL, title=titulo, highlight=destaque, kicker=kicker, lead=lead,
                                     updated_label="[DEFINIR] data de atualização", is_demo=True)  # fmt: skip
        for n, (t, ancora, b) in enumerate(secoes):
            PageSection.objects.create(page=pagina, title=t, anchor=ancora, body=b, order=n)
    return True
