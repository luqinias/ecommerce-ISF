import json
import re
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.conteudo.models import Post, PostCategory

pytestmark = pytest.mark.django_db


@pytest.fixture
def blog(site_config):
    site_config.blog_enabled = True
    site_config.save()
    cat = PostCategory.objects.create(name="Guias", slug="guias")
    agora = timezone.now()
    for i in range(15):
        Post.objects.create(title=f"Post {i}", slug=f"post-{i}", category=cat, excerpt="Resumo", body="## Seção\n\nTexto.\n- item",
                            published=True, published_at=agora - timedelta(days=i))  # fmt: skip
    Post.objects.create(
        title="Rascunho", slug="rascunho", category=cat, excerpt="x", body="x", published=False, published_at=agora
    )
    Post.objects.create(
        title="Futuro",
        slug="futuro",
        category=cat,
        excerpt="x",
        body="x",
        published=True,
        published_at=agora + timedelta(days=3),
    )
    return cat


def test_blog_desativado_e_404_e_sem_link(client):
    assert client.get("/blog/").status_code == 404
    assert 'href="/blog/"' not in client.get("/").content.decode()


def test_lista_destaque_e_paginacao(client, blog):
    html = client.get("/blog/").content.decode()
    assert 'href="/blog/"' in client.get("/").content.decode()
    assert "post-destaque" in html and "Post 0" in html
    assert html.count('class="card-post"') == 12 and 'href="/blog/page/2/"' in html
    p2 = client.get("/blog/page/2/").content.decode()
    assert p2.count('class="card-post"') == 2


def test_rascunho_e_futuro_ficam_ocultos(client, blog):
    assert client.get("/blog/rascunho/").status_code == 404
    assert client.get("/blog/futuro/").status_code == 404


def test_post_com_jsonld_e_texto_rico(client, blog):
    html = client.get("/blog/post-1/").content.decode()
    assert "<h2>Seção</h2>" in html and "<ul><li>item</li></ul>" in html
    tipos = [
        n["@type"]
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        for n in json.loads(b)["@graph"]
    ]
    assert "BlogPosting" in tipos and "BreadcrumbList" in tipos
    assert "Continue lendo" in html


def test_categoria_e_sitemap(client, blog):
    assert client.get("/blog/categoria/guias/").status_code == 200
    assert "/blog/post-3/" in client.get("/sitemap.xml").content.decode()
