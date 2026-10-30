"""E6 · Filtro de privacidad (T-E6-01).

Cada herramienta declara su salida con un modelo pydantic. El filtro deja pasar
solo campos declarados de tipo número, booleano, fecha, código o seudónimo, y
descarta cualquier otro campo (registrando una alerta). Es lo único que se
interpone entre la base de la clínica y Gemini: no es un modelo de IA.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, StringConstraints

Pseudonym = Annotated[str, StringConstraints(pattern=r"^u_[0-9a-f]{6,16}$")]
Code = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9_]{1,40}$")]

SAFE_SCALARS = (bool, int, float, date, datetime)
PSEUDONYM_RE = re.compile(r"^u_[0-9a-f]{6,16}$")
CODE_RE = re.compile(r"^[A-Z0-9_]{1,40}$")


class ToolOutput(BaseModel):
    """Base de toda salida de herramienta: prohíbe campos no declarados."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class FilterResult(BaseModel):
    data: dict[str, Any]
    dropped_fields: list[str]


def filter_tool_output(raw: dict[str, Any], schema: type[ToolOutput]) -> FilterResult:
    """Devuelve solo los campos seguros de `raw` según `schema`.

    - Un campo que no está en `schema` se descarta y se lista en `dropped_fields`.
    - Un valor de texto que no es seudónimo ni código se descarta aunque esté declarado.
    - Listas: se filtran elemento por elemento con las mismas reglas.
    """
    raise NotImplementedError("T-E6-01: implementar con TDD")
