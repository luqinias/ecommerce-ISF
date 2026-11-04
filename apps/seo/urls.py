from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.decorators.cache import cache_page

from apps.seo import views
from apps.seo.sitemaps import SITEMAPS

urlpatterns = [
    path("robots.txt", views.robots, name="robots"),
    path(
        "sitemap.xml", cache_page(3600)(sitemap), {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"
    ),
]
