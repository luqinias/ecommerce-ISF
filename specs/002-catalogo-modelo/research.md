# Research: Modelo do catálogo

| # | Decisão | Alternativas | Motivo |
|---|---|---|---|
| R1 | `attribute_schema` = lista de `{key, label, type, unit, variant, required, choices}`; meta-schema validado com jsonschema | EAV com tabelas de atributo | JSON é mais simples, versionável e importável; jsonschema já é do padrão interno |
| R2 | Schema efetivo do produto = atributos da categoria pai + da categoria principal (filha sobrescreve chave igual) | só a categoria principal | Subcategoria herda o que é comum (ex.: material) |
| R3 | Atributos de produto validados com `additionalProperties: false` sobre as chaves **não-variação**; variações validadas sobre as chaves **de variação** | aceitar chaves livres | Evita lixo e erro de digitação; a importação estende o schema quando a coluna é nova |
| R4 | Categoria principal obrigatória (`primary_category`) + M2M `categories` (inclui a principal) | só M2M | Breadcrumb, selo e schema precisam de uma categoria determinística |
| R5 | Planilha: 1 linha por variação (ou por produto sem variação); colunas `attr:<chave> [unidade]` e `var:<chave> [unidade]`; XLSX aceita abas opcionais `categorias` e `atributos` | uma aba por entidade | Equipe comercial edita uma única tabela; abas extras dão controle fino |
| R6 | Idempotência: produto por `sku`, variação por `sku`, imagem por `source` (URL/caminho de origem) | hash do arquivo | Evita baixar e duplicar imagens a cada reimportação |
| R7 | Dry-run = mesma execução dentro de `transaction.atomic()` com `set_rollback(True)`; download de imagens pulado em dry-run | parser separado | Um só caminho de código → relatório idêntico |
| R8 | Miniaturas WebP 400 px (card) e 900 px (página) em campos próprios, geradas no `save()` quando a imagem muda | sorl/easy-thumbnails | Sem dependência; tamanhos fixos conhecidos |
| R9 | Demonstração: `docs/exemplos/catalogo-demo.csv` importado pelo mesmo serviço com `is_demo=True`; imagens placeholder geradas por Pillow (gradiente + ícone + rótulo "DEMO") | fixture JSON | Prova o fluxo de substituição por planilha e não usa fotos de terceiros |
| R10 | Remoção: `limpar_catalogo_demo` apaga `Product`/`Category`/`Collection` com `is_demo=True` (categorias só se vazias de produtos reais) | soft delete | Requisito explícito do prompt |
