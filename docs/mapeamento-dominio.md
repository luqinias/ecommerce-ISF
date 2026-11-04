# Mapeamento de domínio: brindes → irrigação (Fase 2)

> Traduz os conceitos do sistema de referência (catálogo de brindes) para o catálogo da Irrigação Sem Fronteiras (ISF).
> Tudo o que é **provisório** está marcado. Dados reais da empresa (CNPJ, endereço, telefone, preços, especificações técnicas) **não foram inventados**: aparecem como `[DEFINIR]` e estão em [`pendencias-empresa.md`](pendencias-empresa.md).
> Insumos: [`engenharia-reversa/modelo-dados-referencia.md`](engenharia-reversa/modelo-dados-referencia.md), [`engenharia-reversa/gap-analysis.md`](engenharia-reversa/gap-analysis.md) e [`contexto-empresa.md`](contexto-empresa.md).

## 1. Tabela de tradução

| Referência (brindes) | ISF (proposta provisória) | Model | Observações |
|---|---|---|---|
| Categoria de brinde (≈36, hierarquia rasa, ex.: Agendas dentro de Cadernos) | **Categoria de produto**, árvore de no máximo 2 níveis. Sugestões **provisórias**: Gotejamento, Microaspersão, Aspersão, Tubos e Conexões, Filtragem, Automação e Controladores, Bombas, Fertirrigação, Kits | `Category` (`parent`, `attribute_schema`) | Nomes finais: pendência P9. Subcategorias de demonstração: "Conexões" (em Tubos e Conexões) e "Fitas gotejadoras" (em Gotejamento) |
| "Datas Especiais" (Natal, Outubro Rosa…), que na referência **são categorias comuns** | **Coleção / campanha** configurável (ex.: "Lançamentos", "Safra de verão", "Por cultura: café"). Entidade separada, com período opcional e destaque na home | `Collection` (`starts_on`, `ends_on`, `featured`) | Na referência as datas especiais são `product_cat` misturadas às categorias. Separamos em entidade própria para o menu "Datas Especiais" e para o bloco "próximas datas". O rótulo do menu ("Coleções", "Campanhas", "Safras"…) é configurável em `SiteConfiguration.collections_label` (pendência P10) |
| Variação por **Cor** (atributo único `Cores`, 1 a 5 termos) | **Variações por atributos técnicos** (vazão, diâmetro, pressão, voltagem, comprimento…), definidos **por categoria** no admin | `Category.attribute_schema` (lista de `{key, label, type, unit, variant, choices}`) + `Variant.attributes` | Um produto pode variar em mais de um atributo (ex.: diâmetro × pressão). O seletor bloqueia o botão até todos os atributos de variação estarem escolhidos |
| Campos fixos do produto: código/SKU, dimensões, material, capacidade, peso | **Ficha técnica** gerada a partir de `Product.attributes` validado contra o schema da categoria | `Product.attributes` (JSON) + `sku` | Nenhum atributo técnico é hard-coded. Valores de demonstração são fictícios e marcados `is_demo` |
| Quantidade mínima (ex.: "mín. 50 un.") | **Quantidade mínima + unidade de venda** (peça, metro, rolo, kit, caixa) e múltiplo opcional | `Product.min_quantity`, `sale_unit`, `quantity_step` | Ex.: fita gotejadora vendida em rolo; tubo em metro com múltiplo de 50 m |
| Produto "variável" com galeria (produto + ambiente) | Igual: imagens do tipo **produto** e **aplicação em campo** | `ProductImage.kind` (`product` / `environment`) | Miniaturas WebP geradas no upload |
| Tags de produto (`brinde barato`, `brinde ecológico`) | **Não adotado agora** | — | Na referência servem só para SEO. Busca e coleções cobrem o uso. Registrado no gap analysis |
| Selos "NOVO" / "MAIS PEDIDO" no card | "Novidade" (por `new_until`) e "Destaque" (`featured`) | `Product.new_until`, `featured` | "Mais pedido" exigiria métrica real de pedidos; usamos destaque manual |
| Carrinho WooCommerce usado como lista de orçamento | **Lista de orçamento na sessão** (sem preço) | sessão + `Quote`/`QuoteItem` no envio | Sem checkout, sem preço, sem estoque |
| Página "Finalização de orçamento" + formulário | Página `/orcamento/` com revisão dos itens e formulário (nome, empresa, e-mail, telefone/WhatsApp, cidade/UF, mensagem) | `Quote` (`status`, `source`) | Grava o lead, envia e-mail para a equipe e confirmação para o cliente, depois abre o `wa.me` com a mensagem gerada |
| "Solicitar orçamento rápido" (WhatsApp direto, mensagem fixa) | Igual, com mensagem configurável em `SiteConfiguration` | `SiteConfiguration.whatsapp_number`, `quick_quote_message` | Número real: pendência P4 |
| Portfólio "trabalhos que saíram da nossa produção" | **Projetos e instalações realizadas** (cultura, área, cidade/UF, sistema) | `PortfolioItem` | Sem fotos reais até a empresa enviar (P11). Placeholders gerados |
| Personalização com logo, "arquivo de logo", "tipos de personalização" | **Não se aplica.** Substituído por "Dimensionamento e projeto sob consulta" no "Como funciona" e no FAQ, se a empresa quiser | `HowItWorksStep`, `FAQItem` (conteúdo) | Decisão de oferta: pendência P12 |
| Prazos sazonais ("Fim de ano tem fila") | **Janela de plantio / safra** ("Garanta o sistema antes do plantio") | `Collection` com período + bloco "band" editável | Textos finais: P3 |
| Landings de segmento (Clínicas, Empresas/RH, **Agro**) e por cidade (Uberaba, Uberlândia…) | **Fora do escopo agora.** Podem virar coleções por cultura ou páginas institucionais editáveis | — | SEO local depende da área de atuação (P13) |
| Depoimentos com estrelas | Depoimentos editáveis, **sem conteúdo inventado**: a seção só aparece quando houver depoimento cadastrado | `Testimonial` | Regra do `PRODUCT.md` interno: não inventar depoimentos |
| Avaliações de produto (WooCommerce reviews) | **Não adotado agora** | — | Exige moderação e contas; não há base real |
| Blog (posts + 4 categorias) | Feature 009 **opcional** | `Post`, `PostCategory` | Confirmar com a empresa (P14) |

## 2. Atributos técnicos de demonstração (por categoria)

Todos **fictícios**, para exercitar o schema. A empresa substitui pelos atributos reais via admin ou planilha (P15).

| Categoria (provisória) | Atributos de ficha (`variant: false`) | Atributos que geram variação (`variant: true`) |
|---|---|---|
| Gotejamento | material, espaçamento entre emissores (cm), autocompensante (sim/não) | vazão (L/h), diâmetro (mm) |
| Microaspersão | alcance (m), bocal | vazão (L/h) |
| Aspersão | alcance (m), material, rosca | bocal (mm), pressão (bar) |
| Tubos e Conexões | material, norma | diâmetro (mm), pressão nominal (PN) |
| Filtragem | tipo de elemento, mesh | diâmetro (pol), vazão máx. (m³/h) |
| Automação e Controladores | nº de setores, alimentação, conectividade | voltagem (V) |
| Bombas | potência (cv), altura manométrica (mca), fases | voltagem (V) |
| Fertirrigação | tipo de injeção, material | vazão (L/h) |
| Kits | área atendida (m²), itens inclusos | — |

Tipos suportados no schema: `text`, `number`, `boolean`, `choice` (com `choices`). Unidade opcional (`unit`).

## 3. Unidades de venda

`piece` (peça), `meter` (metro), `roll` (rolo), `kit` (kit), `box` (caixa). Rótulo, plural e abreviação vêm de `TextChoices` em pt-BR. A empresa pode precisar de outras (P16).

## 4. Status e origem do orçamento

| Status | Rótulo |
|---|---|
| `new` | Novo |
| `in_progress` | Em atendimento |
| `answered` | Respondido |
| `closed` | Fechado (ganho) |
| `lost` | Perdido |

Origem: `site` (formulário) ou `whatsapp` (orçamento rápido, registrado quando o visitante usa o botão a partir da lista).

## 5. Rotas (padrão de URL preservado da referência quando faz sentido)

| Referência | ISF |
|---|---|
| `/` | `/` |
| `/categorias-de-brindes/` e `/categorias-de-brindes/page/{n}/` | `/produtos/` e `/produtos/page/{n}/` |
| `/categoria-produto/{slug}/` | `/categoria-produto/{slug}/` |
| `/categoria-produto/{pai}/{filho}/` | `/categoria-produto/{pai}/{filho}/` |
| (datas especiais como categoria) | `/colecao/{slug}/` |
| `/produto/{slug}/` | `/produto/{slug}/` |
| `/?s=termo&post_type=product` | `/busca/?q=termo` |
| `/novidades/` | `/novidades/` |
| `/sobre-cia-da-arte-brindes/` | `/sobre/` |
| `/contato/` | `/contato/` |
| `/finalizacao-de-orcamento/` e `/solicitar-orcamento-2/` | `/orcamento/` (revisão + formulário) e `/orcamento/enviado/` |
| `/termos-de-uso-e-privacidade/`, `/politica-de-privacidade/` | `/termos-de-uso/`, `/politica-de-privacidade/` |
| `/blog/`, `/{post}/`, `/category/{slug}/` | `/blog/`, `/blog/{slug}/`, `/blog/categoria/{slug}/` (feature 009) |
| `/sitemap_index.xml` | `/sitemap.xml` |
