"""Definição de atributos técnicos por categoria e validação com JSON Schema.

Uma categoria guarda em `attribute_schema` uma lista como:

    [{"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": true},
     {"key": "material", "label": "Material", "type": "choice", "choices": ["PE", "PVC"]}]

Nada aqui conhece atributos específicos: tudo vem desses dados.
"""

from __future__ import annotations

import re
from typing import Any

from django.core.exceptions import ValidationError
from jsonschema import Draft202012Validator

CHAVE_RE = r"^[a-z][a-z0-9_]{0,39}$"

META_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["key", "label", "type"],
        "additionalProperties": False,
        "properties": {
            "key": {"type": "string", "pattern": CHAVE_RE},
            "label": {"type": "string", "minLength": 1, "maxLength": 80},
            "type": {"enum": ["text", "number", "boolean", "choice"]},
            "unit": {"type": "string", "maxLength": 20},
            "variant": {"type": "boolean"},
            "required": {"type": "boolean"},
            "choices": {"type": "array", "items": {"type": ["string", "number"]}, "minItems": 1, "uniqueItems": True},
            "help": {"type": "string", "maxLength": 200},
        },
        "allOf": [{"if": {"properties": {"type": {"const": "choice"}}}, "then": {"required": ["choices"]}}],
    },
}

_TIPOS_JSON = {"text": "string", "number": "number", "boolean": "boolean"}


def validar_definicao(definicao: Any) -> None:
    """Valida o `attribute_schema` de uma categoria. Levanta ValidationError com mensagens em pt-BR."""
    erros = sorted(Draft202012Validator(META_SCHEMA).iter_errors(definicao), key=lambda e: list(e.path))
    if erros:
        e = erros[0]
        local = "/".join(str(p) for p in e.path) or "raiz"
        raise ValidationError(f"Definição de atributos inválida em {local}: {e.message}")
    chaves = [a["key"] for a in definicao]
    repetidas = {c for c in chaves if chaves.count(c) > 1}
    if repetidas:
        raise ValidationError(f"Chaves de atributo repetidas: {', '.join(sorted(repetidas))}")


def combinar(*definicoes: list[dict]) -> list[dict]:
    """Junta definições (pai primeiro); a mesma chave na filha substitui a do pai."""
    por_chave: dict[str, dict] = {}
    for definicao in definicoes:
        for attr in definicao or []:
            por_chave[attr["key"]] = attr
    return list(por_chave.values())


def json_schema(definicao: list[dict], *, variante: bool) -> dict:
    """Gera o JSON Schema dos atributos de produto (variante=False) ou de variação (variante=True)."""
    props, obrigatorios = {}, []
    for attr in definicao:
        if bool(attr.get("variant")) != variante:
            continue
        prop = {"enum": attr["choices"]} if attr["type"] == "choice" else {"type": _TIPOS_JSON[attr["type"]]}
        props[attr["key"]] = prop
        if variante or attr.get("required"):
            obrigatorios.append(attr["key"])
    return {"type": "object", "properties": props, "required": obrigatorios, "additionalProperties": False}


def _mensagem(erro, definicao: list[dict]) -> tuple[str, str]:
    rotulos = {a["key"]: a["label"] for a in definicao}
    if erro.validator == "required":
        chave = re.search(r"'([^']+)'", erro.message).group(1)
        return chave, f"{rotulos.get(chave, chave)}: obrigatório."
    if erro.validator == "additionalProperties":
        extras = re.findall(r"'([^']+)'", erro.message)
        return "__all__", f"Atributo não definido na categoria: {', '.join(extras)}."
    chave = str(erro.path[0]) if erro.path else "__all__"
    rotulo = rotulos.get(chave, chave)
    if erro.validator == "enum":
        return chave, f"{rotulo}: valor fora das opções ({', '.join(map(str, erro.validator_value))})."
    if erro.validator == "type":
        nomes = {"number": "um número", "string": "um texto", "boolean": "sim ou não"}
        return chave, f"{rotulo}: deve ser {nomes.get(erro.validator_value, erro.validator_value)}."
    return chave, f"{rotulo}: {erro.message}"


def validar_atributos(valores: Any, definicao: list[dict], *, variante: bool) -> None:
    """Valida um dict de atributos. ValidationError({chave: [mensagens]})."""
    if not isinstance(valores, dict):
        raise ValidationError("Os atributos devem ser um objeto chave → valor.")
    schema = json_schema(definicao, variante=variante)
    erros: dict[str, list[str]] = {}
    for erro in Draft202012Validator(schema).iter_errors(valores):
        chave, msg = _mensagem(erro, definicao)
        erros.setdefault(chave, []).append(msg)
    if erros:
        raise ValidationError(erros)


def converter_valor(bruto: Any, attr: dict) -> Any:
    """Converte um valor vindo de planilha/formulário para o tipo do atributo. Vazio → None."""
    if bruto is None or (isinstance(bruto, str) and not bruto.strip()):
        return None
    tipo = attr["type"]
    if tipo == "number" or (tipo == "choice" and all(isinstance(c, int | float) for c in attr.get("choices", []))):
        if isinstance(bruto, int | float) and not isinstance(bruto, bool):
            numero = bruto
        else:
            texto = str(bruto).strip().replace(" ", "")
            if "," in texto:
                texto = texto.replace(".", "").replace(",", ".")
            try:
                numero = float(texto)
            except ValueError:
                return str(bruto).strip()  # deixa a validação apontar o erro
        return int(numero) if float(numero).is_integer() else float(numero)
    if tipo == "boolean":
        if isinstance(bruto, bool):
            return bruto
        texto = str(bruto).strip().lower()
        if texto in {"sim", "s", "true", "1", "yes", "x"}:
            return True
        if texto in {"não", "nao", "n", "false", "0", "no"}:
            return False
        return texto
    return str(bruto).strip()


def formatar_valor(valor: Any, attr: dict) -> str:
    """Valor legível para a ficha técnica: 2,5 L/h · Sim · 16 mm."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, bool):
        texto = "Sim" if valor else "Não"
    elif isinstance(valor, float):
        texto = f"{valor:g}".replace(".", ",")
    else:
        texto = str(valor)
    unidade = attr.get("unit")
    return f"{texto} {unidade}" if unidade and not isinstance(valor, bool) else texto
