# Importação do catálogo por planilha

O catálogo inteiro (categorias, coleções, produtos, variações, atributos técnicos e imagens) pode ser criado ou trocado por planilha **CSV** ou **XLSX**, sem mudar código. A importação é **idempotente por SKU**: rodar a mesma planilha de novo atualiza, não duplica.

- Planilha-modelo: [`exemplos/modelo-catalogo.xlsx`](exemplos/modelo-catalogo.xlsx) (abas `produtos`, `categorias`, `atributos`, `instrucoes`) e [`exemplos/modelo-catalogo.csv`](exemplos/modelo-catalogo.csv).
- Catálogo de demonstração (exemplo completo, 42 produtos): [`exemplos/catalogo-demo.csv`](exemplos/catalogo-demo.csv).
- Para regerar a planilha-modelo: `uv run python tools/gerar_modelo_planilha.py`.

## Passo a passo para trocar o catálogo de demonstração pelo real

```bash
# 1. Simular: nada é gravado, o relatório mostra o que seria feito e os erros por linha
uv run python manage.py importar_catalogo catalogo-real.xlsx --dry-run --imagens /caminho/fotos

# 2. Corrigir a planilha até não haver erros e importar de verdade
uv run python manage.py importar_catalogo catalogo-real.xlsx --imagens /caminho/fotos --relatorio relatorio.json

# 3. Remover só o que é demonstração
uv run python manage.py limpar_catalogo_demo
```

Pelo admin: **Catálogo › Importações de catálogo › Adicionar**. Envie a planilha com "simulação" marcado, leia o relatório e use a ação **"Importar de verdade"** na lista. (Pelo admin, imagens só por URL; para fotos locais use o comando com `--imagens`.)

## Aba `produtos` (ou o arquivo CSV)

**Uma linha por variação.** Produto sem variação ocupa uma linha com `sku_variacao` vazio. As linhas seguintes do mesmo produto só precisam de `sku_produto`, `sku_variacao` e das colunas `var:`; os dados do produto são lidos da **primeira** linha dele.

CSV: separador `;` (também aceita `,` ou tab), codificação UTF-8 (também aceita Windows-1252).

| Coluna | Obrigatória | Formato | Observação |
|---|---|---|---|
| `sku_produto` | ✔ | texto | Chave da idempotência. Nunca reutilize um SKU para outro produto |
| `nome` | ✔ (produto novo) | texto até 200 | |
| `categoria` | ✔ (produto novo) | `Categoria` ou `Pai > Filha` | Categoria principal: define breadcrumb, selo e **atributos técnicos**. Criada se não existir |
| `categorias_extras` | | lista com `\|` | O produto também aparece nessas listagens e nos chips |
| `colecoes` | | lista com `\|` | Criadas se não existirem |
| `slug` | | texto | Vazio = gerado do nome |
| `descricao_curta` | | até 300 caracteres | Card e topo da página do produto |
| `descricao` | | texto | Linha em branco (ou `\n\n`) separa parágrafos |
| `quantidade_minima` | | inteiro ≥ 1 | Default 1. Precisa ser múltiplo de `multiplo` |
| `multiplo` | | inteiro ≥ 1 | Ex.: 50 = vende de 50 em 50 |
| `unidade_venda` | | `peça`, `metro`, `rolo`, `kit`, `caixa` | Default peça |
| `destaque` | | sim/não | Selo "Destaque" e prioridade em vitrines |
| `novidade_ate` | | `AAAA-MM-DD` ou `DD/MM/AAAA` | Selo "Novo" e página Novidades até essa data |
| `relevancia` | | inteiro | Maior aparece primeiro em "Mais relevantes" |
| `ativo` | | sim/não | Default sim |
| `imagens` | | lista com `\|` | URL (`https://…`) ou caminho relativo à pasta `--imagens`. Prefixo `ambiente:` = foto de aplicação em campo. A primeira é a principal |
| `meta_titulo`, `meta_descricao` | | texto | SEO (opcional) |
| `sku_variacao` | quando houver variação | texto | Chave da variação |
| `imagem_variacao` | | URL ou caminho | Foto mostrada ao escolher a variação |
| `ativo_variacao`, `ordem_variacao` | | sim/não, inteiro | |
| `attr:<nome> [unidade]` | | valor | Atributo da **ficha técnica**. Ex.: `attr:Pressão máxima [bar]` |
| `var:<nome> [unidade]` | | valor | Atributo que **gera variação**. Ex.: `var:Vazão [L/h]` |

Regras das colunas de atributo:

- A chave do atributo vem do nome sem acento, em minúsculas e com `_` (ex.: `Pressão máxima` → `pressao_maxima`).
- Se a categoria ainda não define o atributo, ele é **adicionado à definição da categoria** com o tipo deduzido dos valores (número, sim/não ou texto) e a unidade entre colchetes. O relatório avisa.
- Se a categoria já define o atributo, o valor é **validado** (tipo, lista de opções, obrigatoriedade). Valor inválido = erro naquela linha; o produto inteiro não é importado e as demais linhas seguem.
- Números aceitam vírgula decimal (`2,5`). Sim/não aceita `sim`, `não`, `s`, `n`, `x`, `1`, `0`.
- Célula vazia numa coluna `attr:` **remove** o valor do produto. Coluna ausente não mexe no que já existe.

## Aba `categorias` (opcional, só XLSX)

| Coluna | Formato |
|---|---|
| `categoria` | nome |
| `pai` | nome da categoria raiz (vazio = raiz) |
| `descricao`, `texto_seo` | texto |
| `ordem` | inteiro |
| `icone` | `droplet`, `sprout`, `gauge`, `filter`, `zap`, `layers`, `wrench`, `calendar`, `truck` |
| `home` | sim/não (vitrine na home) |
| `ativo` | sim/não |

## Aba `atributos` (opcional, só XLSX)

Define atributos com controle total (tipo, opções, obrigatório), antes de ler os produtos.

| Coluna | Formato |
|---|---|
| `categoria` | nome (ou `Pai > Filha`) |
| `chave` | sem espaços (ex.: `vazao`) |
| `rotulo` | nome exibido (ex.: `Vazão`) |
| `tipo` | `texto`, `número`, `sim/não`, `opções` |
| `unidade` | ex.: `L/h`, `mm`, `bar` |
| `gera_variacao` | sim/não |
| `obrigatorio` | sim/não |
| `opcoes` | lista com `\|` (para `opções`) |
| `ajuda` | texto curto mostrado no admin |

Subcategorias **herdam** os atributos da categoria pai.

## Relatório

```
SIMULAÇÃO — 85 linhas · criados: 11 categorias, 2 coleções, 84 imagens, 42 produtos, 81 variações · atualizados: 0 produtos · 0 erro(s) · 40 aviso(s)
  linha 7 [GOT-009] Vazão: deve ser um número.
  aviso linha 12 [FIL-002] não foi possível baixar https://…: HTTP Error 404
```

- **Erro**: a linha (e o produto dela) não foi importada. Corrija e rode de novo.
- **Aviso**: a importação seguiu (categoria criada, atributo adicionado, imagem não encontrada…).
- `--relatorio arquivo.json` salva tudo em JSON.

## Opções do comando

| Opção | Efeito |
|---|---|
| `--dry-run` | Simula: executa tudo e desfaz no fim (relatório idêntico ao real). Imagens não são baixadas |
| `--imagens DIR` | Pasta base dos caminhos relativos de imagem (caminhos fora dela são recusados) |
| `--sem-imagens` | Ignora a coluna `imagens` |
| `--demo` | Marca o que for importado como demonstração (`is_demo`) |
| `--relatorio ARQ` | Salva o relatório em JSON |

## Demonstração

- `python manage.py carregar_catalogo_demo [--se-vazio]` importa `docs/exemplos/catalogo-demo.csv` com imagens placeholder geradas na hora (nenhuma foto de terceiros) e marca tudo como demonstração.
- `python manage.py limpar_catalogo_demo [--sim]` remove apenas produtos, categorias e coleções de demonstração. Categoria ou coleção de demonstração que já tenha produto real é mantida (e deixa de ser demonstração).
