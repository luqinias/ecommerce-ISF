#!/bin/sh
# Aplica migrações e, se pedido, carrega o catálogo de demonstração antes de subir o servidor.
set -e

python manage.py migrate --noinput

if [ "${LOAD_DEMO_DATA:-False}" = "True" ]; then
  python manage.py carregar_catalogo_demo --se-vazio || true
  python manage.py carregar_conteudo_demo --se-vazio || true
fi

exec "$@"
