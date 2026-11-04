import pytest
from django.core.exceptions import ValidationError

from apps.catalogo import schema
from tests.factories import SCHEMA_GOTEJO


def test_definicao_valida_passa():
    schema.validar_definicao(SCHEMA_GOTEJO)


@pytest.mark.parametrize(
    "definicao",
    [
        [{"key": "Vazão", "label": "x", "type": "number"}],  # chave com acento/maiúscula
        [{"key": "a", "label": "x", "type": "cor"}],  # tipo desconhecido
        [{"key": "a", "label": "x", "type": "choice"}],  # choice sem opções
        [{"key": "a", "label": "x", "type": "text"}, {"key": "a", "label": "y", "type": "text"}],  # repetida
        {"key": "a"},  # não é lista
    ],
)
def test_definicao_invalida(definicao):
    with pytest.raises(ValidationError):
        schema.validar_definicao(definicao)


def test_combinar_filha_sobrescreve_pai():
    pai = [{"key": "material", "label": "Material", "type": "text"}]
    filha = [
        {"key": "material", "label": "Material da fita", "type": "text"},
        {"key": "x", "label": "X", "type": "text"},
    ]
    combinado = schema.combinar(pai, filha)
    assert [a["label"] for a in combinado] == ["Material da fita", "X"]


def test_valida_atributos_de_produto():
    schema.validar_atributos({"material": "PE", "pressao_max": 2.5}, SCHEMA_GOTEJO, variante=False)
    with pytest.raises(ValidationError) as erro:
        schema.validar_atributos(
            {"material": "PVC", "pressao_max": "alta", "cor": "azul"}, SCHEMA_GOTEJO, variante=False
        )
    msgs = erro.value.message_dict
    assert "material" in msgs and "pressao_max" in msgs and "__all__" in msgs


def test_obrigatorio_de_produto():
    with pytest.raises(ValidationError) as erro:
        schema.validar_atributos({}, SCHEMA_GOTEJO, variante=False)
    assert "pressao_max" in erro.value.message_dict


def test_variacao_exige_todos_os_atributos_de_variacao():
    schema.validar_atributos({"vazao": 2}, SCHEMA_GOTEJO, variante=True)
    with pytest.raises(ValidationError):
        schema.validar_atributos({}, SCHEMA_GOTEJO, variante=True)
    with pytest.raises(ValidationError):
        schema.validar_atributos({"vazao": 2, "material": "PE"}, SCHEMA_GOTEJO, variante=True)


@pytest.mark.parametrize(
    ("bruto", "tipo", "esperado"),
    [("2,5", "number", 2.5), ("1.000,5", "number", 1000.5), ("4", "number", 4), ("sim", "boolean", True),
     ("Não", "boolean", False), ("  PE ", "text", "PE"), ("", "text", None)],
)  # fmt: skip
def test_converter_valor(bruto, tipo, esperado):
    assert schema.converter_valor(bruto, {"type": tipo}) == esperado


def test_formatar_valor():
    assert schema.formatar_valor(2.5, {"unit": "L/h"}) == "2,5 L/h"
    assert schema.formatar_valor(True, {"unit": "x"}) == "Sim"
    assert schema.formatar_valor(16, {}) == "16"
