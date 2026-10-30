"""Validador compartido del contrato (módulos E9 del motor y A7 de Folio).

`validate_schema` ya funciona. `validate_draft_against_findings` es la pieza
que impide que Folio invente algo: implementarla con TDD (T-E9-01, T-E9-02).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

CONTRACT_DIR = Path(__file__).parent


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((CONTRACT_DIR / name).read_text(encoding="utf-8"))


def validate_schema(document: dict[str, Any], schema_name: str) -> list[ValidationIssue]:
    """Devuelve la lista de errores de esquema (vacía si el documento es válido)."""
    validator = Draft202012Validator(_load_schema(schema_name))
    return [
        ValidationIssue("/".join(str(p) for p in err.absolute_path) or "/", err.message)
        for err in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    ]


def validate_draft_against_findings(
    draft: dict[str, Any], findings: dict[str, Any]
) -> list[ValidationIssue]:
    """Rechaza un borrador de Folio que no esté respaldado por los hallazgos.

    Reglas (TDR, sección 4):
      1. Cada `cites` apunta a un `finding_id` que existe en `findings`.
      2. Cada número que aparece en un `text` está en los `facts` de algún hallazgo citado.
      3. Cada `norma_refs` existe en `controls.yaml` con `verificado: true`.
    """
    raise NotImplementedError("T-E9-01 / T-E9-02: implementar con TDD")
