from django.urls import path

from apps.conteudo import views

app_name = "conteudo"

urlpatterns = [
    path("", views.home, name="home"),
    path("sobre/", views.sobre, name="sobre"),
    path("contato/", views.contato, name="contato"),
    path("novidades/", views.novidades, name="novidades"),
    path("novidades/page/<int:pagina>/", views.novidades, name="novidades_pagina"),
    path("termos-de-uso/", views.termos, name="termos"),
    path("politica-de-privacidade/", views.privacidade, name="privacidade"),
    path("pagina/<slug:slug>/", views.pagina, name="pagina"),
    path("blog/", views.blog, name="blog"),
    path("blog/page/<int:pagina>/", views.blog, name="blog_pagina"),
    path("blog/categoria/<slug:slug>/", views.blog_categoria, name="blog_categoria"),
    path("blog/categoria/<slug:slug>/page/<int:pagina>/", views.blog_categoria, name="blog_categoria_pagina"),
    path("blog/<slug:slug>/", views.post, name="post"),
]
