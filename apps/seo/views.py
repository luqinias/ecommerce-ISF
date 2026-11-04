from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


@require_GET
@cache_control(max_age=3600)
def robots(request):
    linhas = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /orcamento/",
        "Disallow: /busca/",
        "",
        f"Sitemap: {settings.BASE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(linhas) + "\n", content_type="text/plain; charset=utf-8")
