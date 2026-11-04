import pytest
from django.template.loader import render_to_string

pytestmark = pytest.mark.django_db


def test_404_util_e_noindex(client):
    resp = client.get("/pagina-que-nao-existe/")
    html = resp.content.decode()
    assert resp.status_code == 404
    assert '<meta name="robots" content="noindex, follow">' in html
    assert "Esta página não existe." in html
    assert 'name="q"' in html
    assert 'href="/produtos/"' in html


def test_500_e_estatico_sem_banco(django_assert_num_queries):
    with django_assert_num_queries(0):
        html = render_to_string("500.html")
    assert "Algo deu errado" in html
    assert "noindex" in html
