from django.urls import path

from apps.orcamentos import views

app_name = "orcamentos"

urlpatterns = [
    path("orcamento/", views.lista_view, name="lista"),
    path("orcamento/adicionar/", views.adicionar, name="adicionar"),
    path("orcamento/mini/", views.mini, name="mini"),
    path("orcamento/item/<str:chave>/", views.item, name="item"),
    path("orcamento/whatsapp/", views.whatsapp, name="whatsapp"),
    path("orcamento/enviado/<uuid:pk>/", views.enviado, name="enviado"),
]
