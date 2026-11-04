# Gap analysis: referência (brindes) × ISF (irrigação)

> ✅ se aplica como está (estrutura/comportamento) · 🔁 se aplica com adaptação · ⛔ não se aplica agora (com motivo).

## 1. Páginas

| Página da referência | ISF | Motivo / adaptação |
|---|---|---|
| Home | ✅ | Todas as 9 seções, com conteúdo editável no admin |
| Catálogo geral `/categorias-de-brindes/` | 🔁 `/produtos/` | URL em pt-BR do domínio |
| Categoria / subcategoria | ✅ | Mesmo template |
| Data especial | 🔁 Coleção `/colecao/{slug}/` | Entidade própria (ver `mapeamento-dominio.md`) |
| Produto | ✅ | Variações técnicas no lugar de cor |
| Busca | 🔁 `/busca/?q=` | Ganha h1 e o layout de listagem (a referência usa o template cru do tema) |
| Novidades | ✅ | Por `new_until` |
| Sobre, Contato | ✅ | Conteúdo `[DEFINIR]` |
| Solicitar orçamento (2 páginas) | 🔁 `/orcamento/` + `/orcamento/enviado/` | Passos 1 e 2 na mesma página (menos uma navegação); passo 3 é a página de confirmação |
| Termos, Privacidade | ✅ | Texto da ISF (P5) |
| Blog e post | 🔁 feature 009 opcional | Sem comentários |
| 404 | ✅ | |
| Landings de segmento (`/agro/`, `/clinicas/`, `/empresas-rh/`) | ⛔ | São páginas de campanha com layout próprio. Para irrigação, o equivalente seria "por cultura"; fica para depois da definição comercial (P13). Coleções cobrem parte do caso |
| SEO local por cidade | ⛔ | Depende da área de atuação real (P13) |
| `/obrigado/` | 🔁 | Vira o passo 3 do orçamento |

## 2. Componentes e comportamentos

| Item | ISF | Motivo / adaptação |
|---|---|---|
| Faixa superior, header, nav sticky, dropdowns, menu mobile, rodapé | ✅ | Menus renderizados no servidor (a referência usa XHR) |
| Busca com sugestões | ✅ | HTMX |
| Mini-lista no header | ✅ | HTMX |
| Banner de cookies | ✅ | Agora controla de fato o carregamento de GTM/Pixel |
| Rolar para cima | ✅ | |
| Hero com mosaico e cards flutuantes | 🔁 | `Banner` editável; cards flutuantes apontam para coleções |
| Vitrine em trilhos por categoria | ✅ | Server-side (corrige o CLS 0,13 da referência) |
| Selo "MAIS PEDIDO" | 🔁 "Destaque" | Não há métrica de pedidos; marcação manual |
| Bolinhas de cor no card | 🔁 | Para atributo técnico, mostra "N opções" com os 2–3 primeiros valores em pílulas pequenas |
| Próximas datas + banner | 🔁 | Coleções em destaque; "data de apoio" vira coleção secundária |
| Portfólio com "Ver mais" | ✅ | Projetos e instalações |
| Tiles de categoria | ✅ | |
| Como funciona (4 passos) | ✅ | Passos editáveis |
| Faixa de prazos | 🔁 | "Janela de plantio/safra", prazos por coleção |
| Por que nós | ✅ | |
| Depoimentos | ✅ | **Oculto** sem depoimento real |
| FAQ | ✅ | |
| Chips com contagem (`?tipo=`) | ✅ | Interseção com categorias e coleções |
| Ordenação (3 opções) | ✅ | |
| Paginação 30/página | ✅ | |
| "Não encontrou?" + WhatsApp | ✅ | |
| Texto SEO da categoria | ✅ | |
| Galeria com miniaturas e tela cheia | ✅ | |
| Zoom ao passar o mouse | ⛔ | Baixo valor, custo de JS; tela cheia cobre o caso |
| Swatches de cor | 🔁 | Pílulas por atributo técnico (vazão, diâmetro…) |
| Botão bloqueado até escolher variação | ✅ | Mensagem genérica "Escolha {atributo} para continuar." |
| Quantidade mínima com stepper | ✅ | + múltiplo e unidade |
| Redirecionar para o orçamento ao adicionar | 🔁 | Fica na página com toast e contador (menos atrito para montar uma lista de vários itens) |
| Descrição expansível | ✅ | |
| Ficha técnica | ✅ | Gerada do schema |
| Avaliações de produto | ⛔ | Exigem moderação; a referência não tem nenhuma. Princípio IX |
| Relacionados | ✅ | |
| Barra fixa no mobile | ✅ | |
| Personalização com logo, envio de arte, técnicas (laser, UV…) | ⛔ | Não se aplica a irrigação. Substituído por "dimensionamento/projeto sob consulta" se a empresa quiser (P12) |
| Mapa do Google na página de contato | 🔁 | Só após consentimento, ou link "Abrir rota" |
| Formulário de contato separado | 🔁 | Reusa `Quote` com origem "contato" |
| Tags de produto | ⛔ | Sem uso funcional; busca cobre |
| Preço, carrinho com total, checkout, frete, estoque | ⛔ | Seção 1 do prompt e princípio IX |

## 3. Problemas da referência que o projeto corrige

| Problema | Correção |
|---|---|
| CLS 0,13 na home e 0,15 em novidades (vitrines por XHR) | Renderização no servidor, imagens com `width`/`height` |
| `select` sem rótulo (axe crítica) no produto | `fieldset` + `legend` + rádios |
| Contraste insuficiente em kickers e cinzas | Tokens "Campo" verificados AA |
| Dois `contentinfo`, `heading-order` no rodapé | Um `footer`; títulos do rodapé como `h2` visualmente pequenos |
| Busca sem h1 e com layout cru | Mesmo template das listagens |
| Rastreadores no HTML antes do consentimento | Injeção só após aceite |
| Fontes do Google carregadas de terceiros | Fontes locais |
| Descriptions curtas, `og:image` ausente | Metas com fallback configurável |
