from django.urls import path

from apps.catalogo import views

app_name = "catalogo"

urlpatterns = [
    path("produtos/", views.lista, name="lista"),
    path("produtos/page/<int:pagina>/", views.lista, name="lista_pagina"),
    path("categoria-produto/<slug:slug>/", views.categoria, name="categoria"),
    path("categoria-produto/<slug:slug>/page/<int:pagina>/", views.categoria, name="categoria_pagina"),
    path("categoria-produto/<slug:pai>/<slug:slug>/", views.subcategoria, name="subcategoria"),
    path("categoria-produto/<slug:pai>/<slug:slug>/page/<int:pagina>/", views.subcategoria, name="subcategoria_pagina"),
    path("colecao/<slug:slug>/", views.colecao, name="colecao"),
    path("colecao/<slug:slug>/page/<int:pagina>/", views.colecao, name="colecao_pagina"),
    path("produto/<slug:slug>/", views.produto, name="produto"),
    path("busca/", views.busca, name="busca"),
    path("busca/page/<int:pagina>/", views.busca, name="busca_pagina"),
    path("busca/sugestoes/", views.sugestoes, name="sugestoes"),
]
