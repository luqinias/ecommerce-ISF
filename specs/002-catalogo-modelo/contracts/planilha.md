# Contrato: planilha de importação

Ver `docs/importacao-catalogo.md` (fonte única). Resumo:

- Aba `produtos` (ou o CSV): 1 linha por variação. Obrigatórias: `sku_produto`, `nome`, `categoria`.
- Atributos: `attr:<chave> [unidade]` (ficha) e `var:<chave> [unidade]` (variação, com `sku_variacao`).
- Abas opcionais no XLSX: `categorias` (categoria, pai, descricao, ordem, icone, home) e `atributos` (categoria, chave, rotulo, tipo, unidade, gera_variacao, obrigatorio, opcoes).
- Saída: relatório `{criados, atualizados, ignorados, erros: [{linha, sku, mensagem}], avisos: [...]}`.

Commands: `importar_catalogo <arquivo> [--dry-run] [--imagens DIR] [--demo]` · `limpar_catalogo_demo [--sim]` · `carregar_catalogo_demo [--se-vazio]`.
