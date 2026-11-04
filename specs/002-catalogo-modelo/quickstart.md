# Quickstart: Catálogo

```bash
uv run python manage.py carregar_catalogo_demo            # ~40 produtos fictícios
uv run python manage.py importar_catalogo docs/exemplos/modelo-catalogo.xlsx --dry-run
uv run python manage.py importar_catalogo docs/exemplos/modelo-catalogo.xlsx
uv run python manage.py limpar_catalogo_demo --sim
```
Admin: Catálogo → Importações de catálogo → Adicionar (enviar planilha, marcar "simulação").
