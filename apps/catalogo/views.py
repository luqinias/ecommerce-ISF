"""Views públicas do catálogo (implementadas na feature 003/004)."""

from django.http import Http404


def em_construcao(request, *args, **kwargs):
    raise Http404


categoria = subcategoria = colecao = produto = lista = busca = sugestoes = novidades = em_construcao
