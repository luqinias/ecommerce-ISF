from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Irrigação Sem Fronteiras"
admin.site.site_title = "ISF · Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.seo.urls")),
    path("", include("apps.conteudo.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.catalogo.urls")),
    path("", include("apps.orcamentos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    # Instalações pequenas sem Nginx/S3 (ex.: docker compose local). Em produção, prefira Nginx ou S3.
    from django.urls import re_path
    from django.views.static import serve

    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]
