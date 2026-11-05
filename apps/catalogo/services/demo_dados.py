"""Dados de apresentação do catálogo de demonstração: ilustração e cena de cada produto, por SKU.

São dados, não regra: o catálogo real não usa este arquivo. As descrições ficam no CSV
(`docs/exemplos/catalogo-demo.csv`), que também serve de exemplo de importação.
"""

from __future__ import annotations

from apps.catalogo.services import ilustracoes as il

# SKU → (desenho, cor, opções do desenho, cena de aplicação)
PRODUTOS: dict[str, tuple[str, str, dict, str]] = {
    "GOT-001": ("gotejador_botao", il.LILAS, {}, "fruticultura"),
    "GOT-002": ("gotejador_botao", il.VERDE_CLARO, {}, "horta"),
    "GOT-003": ("gotejador_linha", il.LARANJA, {}, "horta"),
    "GOT-004": ("gotejador_antidrenante", il.VERMELHO, {}, "estufa"),
    "GOT-005": ("gotejador_labirinto", il.AZUL, {}, "cafe"),
    "FIT-001": ("fita", il.PRETO_PE, {"listra": il.AZUL}, "horta"),
    "FIT-002": ("fita", il.PRETO_PE, {"listra": il.VERDE_CLARO}, "horta"),
    "FIT-003": ("fita", il.PRETO_PE, {"pontos": "#6b5f4a"}, "cafe"),
    "MIC-001": ("microaspersor", il.AZUL, {"tipo": "bailarina"}, "pomar"),
    "MIC-002": ("microaspersor", il.LARANJA, {"tipo": "spray"}, "pomar"),
    "MIC-003": ("microaspersor", il.CINZA, {"tipo": "nebulizador"}, "estufa"),
    "MIC-004": ("microaspersor", il.VERDE_CLARO, {"tipo": "rotativo"}, "pomar"),
    "ASP-001": ("aspersor_impacto", il.LATAO, {}, "pastagem"),
    "ASP-002": ("aspersor_setorial", il.VERDE, {}, "pastagem"),
    "ASP-003": ("canhao", "#6e7772", {}, "graos"),
    "ASP-004": ("escamoteavel", il.VERDE_CLARO, {}, "gramado"),
    "TUB-001": ("tubo_pe", il.PRETO_PE, {}, "fruticultura"),
    "TUB-002": ("tubos_pvc", il.BRANCO_PVC, {}, "instalacao"),
    "TUB-003": ("mangueira_succao", "#3f9a63", {}, "instalacao"),
    "CON-001": ("conector", il.PRETO_PE, {"tipo": "inicial"}, "horta"),
    "CON-002": ("conector", il.PRETO_PE, {"tipo": "luva"}, "horta"),
    "CON-003": ("conector", il.PRETO_PE, {"tipo": "registro", "alavanca": il.AZUL}, "horta"),
    "CON-004": ("conector", il.PRETO_PE, {"tipo": "te"}, "fruticultura"),
    "CON-005": ("conector", il.PRETO_PE, {"tipo": "colar"}, "instalacao"),
    "FIL-001": ("filtro", "#3a3f3c", {"tipo": "disco", "tampa": il.VERMELHO}, "instalacao"),
    "FIL-002": ("filtro", "#3a3f3c", {"tipo": "tela", "tampa": il.AZUL}, "instalacao"),
    "FIL-003": ("filtro", "#2f6a8f", {"tipo": "areia"}, "instalacao"),
    "FIL-004": ("filtro", il.AZUL, {"tipo": "hidrociclone"}, "instalacao"),
    "AUT-001": ("controlador", "#e8ebe8", {"setores": 6}, "gramado"),
    "AUT-002": ("controlador", "#e8ebe8", {"setores": 1}, "horta"),
    "AUT-003": ("valvula", "#2f3431", {}, "instalacao"),
    "AUT-004": ("sensor_chuva", il.CINZA, {}, "gramado"),
    "BOM-001": ("bomba", il.AZUL, {}, "instalacao"),
    "BOM-002": ("bomba", il.VERDE, {"tamanho": 1.15}, "instalacao"),
    "BOM-003": ("bomba", il.INOX, {"tipo": "submersa"}, "instalacao"),
    "FER-001": ("venturi", il.PRETO_PE, {}, "instalacao"),
    "FER-002": ("dosadora", il.AZUL, {}, "instalacao"),
    "FER-003": ("dosadora", il.AZUL, {"tipo": "proporcional"}, "estufa"),
    "KIT-001": ("kit", "", {"itens": ["fita", "filtro", "conector"]}, "horta"),
    "KIT-002": ("kit", "", {"itens": ["microaspersor", "tubo", "conector"]}, "pomar"),
    "KIT-003": ("kit", "", {"itens": ["escamoteavel", "controlador", "valvula"]}, "gramado"),
    "KIT-004": ("kit", "", {"itens": ["nebulizador", "tubo", "conector"]}, "estufa"),
}

# Produto que ilustra cada categoria (tile da home e imagem da categoria)
CATEGORIA_PRODUTO = {
    "Gotejamento": "GOT-001",
    "Fitas gotejadoras": "FIT-001",
    "Microaspersão": "MIC-001",
    "Aspersão": "ASP-001",
    "Tubos e Conexões": "TUB-001",
    "Conexões": "CON-004",
    "Filtragem": "FIL-001",
    "Automação e Controladores": "AUT-001",
    "Bombas": "BOM-001",
    "Fertirrigação": "FER-002",
    "Kits": "KIT-001",
}

# Coleção → cena
COLECAO_CENA = {"Lançamentos": ("estufa", 2), "Preparo para a safra": ("graos", 4)}

# Portfólio de demonstração: sistemas-tipo, sem cliente, cidade ou número inventado como fato
PORTFOLIO = [
    ("Café em renque com gotejamento", "Gotejamento enterrado · cafeicultura", "cafe"),
    ("Pomar de citros com microaspersão", "Microaspersão · fruticultura", "pomar"),
    ("Hortaliças com fita gotejadora", "Fita gotejadora · horticultura", "horta"),
    ("Estufa de mudas com nebulização", "Nebulização · viveiro", "estufa"),
    ("Pastagem irrigada por aspersão", "Aspersão · pecuária", "pastagem"),
    ("Casa de bombas com filtragem", "Bombeamento e filtragem", "instalacao"),
    ("Grãos com canhão aspersor", "Aspersão de grande alcance", "graos"),
    ("Jardim com aspersores escamoteáveis", "Automação · paisagismo", "gramado"),
    ("Fruticultura com gotejamento", "Gotejamento autocompensante", "fruticultura"),
    ("Fertirrigação em cultivo protegido", "Fertirrigação · estufa", "estufa"),
]
