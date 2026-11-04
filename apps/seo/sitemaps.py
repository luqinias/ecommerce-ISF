from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.catalogo.models import Category, Collection, Product
from apps.conteudo.models import Page, Post
from apps.core.models import SiteConfiguration


class BaseSitemap(Sitemap):
    def get_urls(self, page=1, site=None, protocol=None):
        from django.conf import settings

        dominio = settings.BASE_URL.split("://", 1)[-1]
        protocolo = settings.BASE_URL.split("://", 1)[0]

        class _Site:
            domain = dominio

        return super().get_urls(page=page, site=_Site(), protocol=protocolo)


class EstaticasSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["conteudo:home", "catalogo:lista", "conteudo:novidades", "conteudo:contato"]

    def location(self, item):
        return reverse(item)


class CategoriasSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return (
            Category.objects.active().select_related("parent").filter(parent__active=True)
            | Category.objects.active().roots()
        )

    def lastmod(self, obj):
        return obj.updated_at


class ColecoesSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Collection.objects.visible()

    def lastmod(self, obj):
        return obj.updated_at


class ProdutosSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.9
    limit = 5000

    def items(self):
        return Product.objects.active().order_by("pk")

    def lastmod(self, obj):
        return obj.updated_at


class PaginasSitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.4

    def items(self):
        return Page.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.updated_at


class PostsSitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        if not SiteConfiguration.load().blog_enabled:
            return Post.objects.none()
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "estaticas": EstaticasSitemap,
    "categorias": CategoriasSitemap,
    "colecoes": ColecoesSitemap,
    "produtos": ProdutosSitemap,
    "paginas": PaginasSitemap,
    "blog": PostsSitemap,
}
