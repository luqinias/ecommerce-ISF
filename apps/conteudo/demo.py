"""Conteúdo de demonstração da home e das páginas. Genérico e marcado: nada de dado real inventado.

- Sem depoimentos (só entram com autorização do cliente: pendência P17).
- Portfólio com sistemas-tipo ilustrados, sem cliente, cidade ou número apresentado como fato (P11).
- Textos institucionais genéricos. Dados que só a empresa tem (telefone, endereço, CNPJ, horário)
  não são inventados: ficam vazios e o site oculta o campo (P3, P4, P5, P18).
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from django.db import transaction

from apps.catalogo.services import demo_dados, demo_midia
from apps.catalogo.services.demo import copiar_se_faltar
from apps.conteudo.models import (
    Banner,
    FAQItem,
    Highlight,
    HowItWorksStep,
    Page,
    PageSection,
    PortfolioItem,
    SectionText,
)
from apps.core.models import DEFINIR, SiteConfiguration

PROVAS = [
    ("users", "Atendimento técnico", "Quem atende entende de irrigação e ajuda a escolher o produto certo."),
    ("truck", "Pedido sob medida", "Quantidades, opções e entrega combinadas na proposta."),
    ("shield", "Linha completa", "Do gotejador à bomba, tudo para montar o sistema."),
]
POR_QUE = [
    (
        "users",
        "Atendimento de quem entende",
        "A conversa começa pela sua cultura e pela água disponível, não pelo produto.",
    ),
    (
        "sprout",
        "Projeto para a sua cultura",
        "A lista é conferida e ajustada para a área, o espaçamento e a pressão do sistema.",
    ),
    ("truck", "Pedido completo", "Emissores, tubos, filtros e conexões compatíveis, num único orçamento."),
    ("shield", "Suporte depois da compra", "Orientação na instalação e na manutenção para o sistema durar mais."),
]
PASSOS = [
    ("Escolha os produtos", "Navegue pelo catálogo, escolha as opções e as quantidades e monte a sua lista."),
    ("Peça o orçamento", "Envie a lista pelo site ou pelo WhatsApp. Sem preço público: a proposta é feita para você."),
    ("Ajuste técnico", "A equipe confere o dimensionamento e sugere ajustes antes de fechar."),
    ("Entrega", "Prazo e forma de entrega combinados na proposta, conforme a sua região."),
]
FAQ_HOME = [
    (
        "Existe pedido mínimo?",
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
    (
        "Vocês ajudam a dimensionar o sistema?",
        "Sim. Conte a cultura, a área, o espaçamento e a fonte de água. A equipe revisa a lista ou monta uma do zero e explica cada item.",
    ),
    (
        "Para quais regiões vocês entregam?",
        "A entrega é combinada em cada proposta, de acordo com a cidade e o volume do pedido.",
    ),
]
FAQ_CONTATO = [
    (
        "Quanto tempo leva para receber o orçamento?",
        "A equipe responde pela ordem de chegada. Listas completas, com quantidades e opções, são respondidas mais rápido.",
    ),
    ("Quais são as formas de pagamento?", "As condições de pagamento vêm detalhadas na proposta."),
    (
        "Posso enviar a lista de materiais de um projeto?",
        "Sim. Use o formulário ou o WhatsApp e envie a lista ou as fotos; a equipe monta a proposta a partir dela.",
    ),
]

PRIVACIDADE = [
    (
        "Quem cuida dos seus dados",
        "controlador",
        "A empresa responsável pelo site é a controladora dos dados. A razão social, o CNPJ e o contato do encarregado pelos dados ficam nesta seção.",
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
        "Só com fornecedores que tratam dados em nome da empresa para o site funcionar, como hospedagem e envio de e-mail. Não vendemos nem cedemos seus dados.",
    ),
    (
        "Por quanto tempo guardamos",
        "prazo",
        "Pelo tempo necessário para atender o pedido e cumprir obrigações legais. Depois disso, os dados são excluídos ou anonimizados.",
    ),
    (
        "Seus direitos",
        "direitos",
        "Você pode pedir acesso, correção, anonimização ou exclusão dos seus dados e revogar o consentimento, pelos canais da página de contato.",
    ),
]
TERMOS = [
    (
        "Quem somos",
        "quem-somos",
        "Este site é o catálogo da Irrigação Sem Fronteiras, com produtos para irrigação agrícola e de paisagismo.",
    ),
    (
        "Como o site funciona",
        "site",
        "O site é um catálogo. Ele não mostra preços e não vende online: você monta uma lista de orçamento e a equipe responde com uma proposta. O pedido só é fechado depois da proposta aceita.\n\nFotos podem ser ilustrativas e especificações podem mudar; confirme na proposta.",
    ),
    (
        "Orçamento e proposta",
        "orcamento",
        "A proposta informa preços, validade, condições comerciais e de entrega. O pedido só é fechado depois que você aceita a proposta.",
    ),
    (
        "Uso do site",
        "uso",
        "Ao usar o site, você se compromete a informar dados verdadeiros nos formulários e a não tentar prejudicar o funcionamento dele.",
    ),
    (
        "Lei aplicável",
        "foro",
        "Estes termos seguem a legislação brasileira, incluindo o Código de Defesa do Consumidor e a LGPD.",
    ),
]


HERO = {"image_main": "home/hero-1.jpg", "image_2": "home/hero-2.jpg", "image_3": "home/hero-3.jpg"}

SECOES = {
    SectionText.Key.PORTFOLIO: {
        "kicker": "Sistemas",
        "title": "Do gotejamento à casa de bombas.",
        "text": "Exemplos dos sistemas que a equipe ajuda a dimensionar, da horta familiar ao pomar comercial.",
        "cta_label": "Fale com a equipe sobre o seu projeto →",
        "cta_url": "whatsapp",
    },
    SectionText.Key.FAIXA: {
        "title": "Programe a compra antes do plantio.",
        "highlight": "Evite a alta temporada.",
        "text": "Na época de plantio, a procura por emissores, filtros e tubos aumenta. Com a lista pronta antes, a entrega acompanha o seu calendário.",
        "cta_label": "Combinar o prazo pelo WhatsApp",
        "cta_url": "whatsapp",
    },
    SectionText.Key.POR_QUE: {
        "kicker": "Por que a ISF?",
        "title": "Irrigação pensada para a sua cultura.",
        "highlight": "sua cultura",
        "text": "A Irrigação Sem Fronteiras reúne num só catálogo os produtos para irrigar do canteiro ao pomar.\n\nVocê monta a lista, e a equipe confere a compatibilidade entre emissores, tubos, filtros e bombas antes de enviar a proposta.",
        "cta_label": "Falar com a equipe no WhatsApp",
        "cta_url": "whatsapp",
    },
}

SITE = {  # textos genéricos da faixa superior e do rodapé (aplicados só se ainda estiverem em [DEFINIR])
    "topbar_left": "Catálogo técnico de irrigação",
    "tagline": "Monte a sua lista e receba a proposta pelo WhatsApp",
    "footer_about": "Produtos para irrigação por gotejamento, microaspersão e aspersão, com atendimento técnico do orçamento à instalação.",
}
OCULTAR = ("phone_display", "address", "cnpj", "business_hours")  # sem dado real: vazio = campo oculto


def _arquivo(relativo: str) -> ContentFile:
    return ContentFile(demo_midia.ler(relativo), name=PurePosixPath(relativo).name)


def _configurar_site() -> None:
    site = SiteConfiguration.objects.filter(pk=1).first() or SiteConfiguration(pk=1)
    for campo, valor in SITE.items():
        if getattr(site, campo) in ("", DEFINIR):
            setattr(site, campo, valor)
    for campo in OCULTAR:
        if getattr(site, campo) == DEFINIR:
            setattr(site, campo, "")
    site.save()


def _limpar() -> None:
    """Remove o conteúdo de demonstração (e as listas da home, que não têm marcação própria)."""
    for banner in Banner.objects.filter(is_demo=True):
        for campo in HERO:
            getattr(banner, campo).delete(save=False)  # evita nomes com sufixo na recarga
    for item in PortfolioItem.objects.filter(is_demo=True):
        item.image.delete(save=False)
    Banner.objects.filter(is_demo=True).delete()
    PortfolioItem.objects.filter(is_demo=True).delete()
    Page.objects.filter(is_demo=True).delete()
    Highlight.objects.all().delete()
    HowItWorksStep.objects.all().delete()
    FAQItem.objects.all().delete()
    SectionText.objects.filter(key__in=list(SECOES)).delete()


@transaction.atomic
def carregar(*, se_vazio: bool = False, recarregar: bool = False) -> bool:
    if recarregar:
        _limpar()
    elif se_vazio and (Banner.objects.exists() or Page.objects.exists()):
        return False
    demo_midia.gerar()
    _configurar_site()
    banner = Banner(
        badge_label="Coleções",
        title="Produtos de irrigação com orçamento rápido.",
        highlight="orçamento rápido",
        subtitle="Monte a sua lista com produtos e quantidades e receba a proposta pelo WhatsApp ou e-mail, com o dimensionamento conferido pela equipe.",
        caption_main="Gotejamento", caption_2="Filtragem", caption_3="Automação", is_demo=True,
    )  # fmt: skip
    for campo, relativo in HERO.items():
        getattr(banner, campo).save(PurePosixPath(relativo).name, _arquivo(relativo), save=False)
    banner.save()
    for i, (titulo, subtitulo, _cena) in enumerate(demo_dados.PORTFOLIO):
        item = PortfolioItem(
            title=titulo, subtitle=subtitulo, tall=i in (0, 1, 6, 7), featured=i == 0, order=i, is_demo=True
        )
        relativo = f"portfolio/portfolio-{i + 1}.jpg"
        item.image.save(PurePosixPath(relativo).name, _arquivo(relativo), save=False)
        item.save()
    for chave, valores in SECOES.items():
        SectionText.objects.update_or_create(key=chave, defaults=valores)
    for n, (icone, titulo, texto) in enumerate(PROVAS):
        Highlight.objects.create(placement=Highlight.Placement.PROOF, icon=icone, title=titulo, text=texto, order=n)
    for n, (icone, titulo, texto) in enumerate(POR_QUE):
        Highlight.objects.create(placement=Highlight.Placement.WHY, icon=icone, title=titulo, text=texto, order=n)
    for n, (titulo, texto) in enumerate(PASSOS):
        HowItWorksStep.objects.create(title=titulo, text=texto, order=n)
    for n, (pergunta, resposta) in enumerate(FAQ_HOME):
        FAQItem.objects.create(placement=FAQItem.Placement.HOME, question=pergunta, answer=resposta, order=n)
    for n, (pergunta, resposta) in enumerate(FAQ_CONTATO):
        FAQItem.objects.create(placement=FAQItem.Placement.CONTACT, question=pergunta, answer=resposta, order=n)
    sobre = Page.objects.create(slug="sobre", kind=Page.Kind.ABOUT, kicker="Sobre a ISF", title="Irrigação Sem Fronteiras", highlight="Sem Fronteiras",
                                lead="Produtos e atendimento técnico para levar água à raiz de cada planta, com economia e uniformidade.", is_demo=True)  # fmt: skip
    for n, (t, b) in enumerate(
        [
            ("O que fazemos", "Reunimos num só catálogo emissores, fitas, tubos, conexões, filtros, bombas, automação e fertirrigação, com kits prontos para quem está começando."),
            ("Como atendemos", "Você monta a lista no site e a equipe confere o dimensionamento: vazão, pressão, filtragem e compatibilidade entre as peças. A proposta chega pelo WhatsApp ou e-mail."),
            ("Para quem", "Produtores de hortaliças, frutas, café e grãos, viveiros e estufas, paisagistas e instaladores que precisam de um fornecedor técnico e direto."),
        ]
    ):  # fmt: skip
        PageSection.objects.create(page=sobre, title=t, body=b, order=n)
    for slug, titulo, destaque, kicker, lead, secoes in (
        ("politica-de-privacidade", "Como cuidamos dos seus dados", "seus dados", "Política de privacidade", "Como tratamos os dados que você informa no site.", PRIVACIDADE),
        ("termos-de-uso", "Como funciona o site", "o site", "Termos de uso", "As regras para usar o catálogo e pedir orçamento.", TERMOS),
    ):  # fmt: skip
        pagina = Page.objects.create(slug=slug, kind=Page.Kind.LEGAL, title=titulo, highlight=destaque, kicker=kicker, lead=lead,
                                     updated_label="", is_demo=True)  # fmt: skip
        for n, (t, ancora, b) in enumerate(secoes):
            PageSection.objects.create(page=pagina, title=t, anchor=ancora, body=b, order=n)
    return True


def _chave(nome: str) -> str | None:
    """Chave no cache para um arquivo do banco (pasta + nome, aceitando os .png da versão anterior)."""
    caminho = PurePosixPath(nome)
    base = re.sub(r"_[A-Za-z0-9]{7}$", "", caminho.stem)  # sufixo que o storage acrescenta em colisões
    chave = f"{caminho.parent}/{base}.jpg"
    return chave if chave in demo_midia.especificacoes() else None


def regenerar_midia() -> int:
    """Recria os arquivos ausentes do hero e do portfólio de demonstração, nos mesmos nomes do banco.

    Mesmo uso de `apps.catalogo.services.demo.regenerar_midia`: hospedagem com disco temporário.
    """
    arquivos = [getattr(b, campo) for b in Banner.objects.filter(is_demo=True) for campo in HERO]
    arquivos += [item.image for item in PortfolioItem.objects.filter(is_demo=True)]
    recriadas = 0
    for arquivo in arquivos:
        chave = _chave(arquivo.name) if arquivo.name else None
        if chave and copiar_se_faltar(arquivo.name, lambda c=chave: demo_midia.ler(c)):
            recriadas += 1
    return recriadas
