"""E2 · Seudonimizador (T-E2-01, T-E2-02).

Convierte un nombre de usuario en un seudónimo estable `u_<hex>` con HMAC-SHA256
y una sal que nunca sale de la clínica. El nombre original no debe aparecer jamás
en la salida.
"""
from __future__ import annotations


def pseudonymize(username: str, salt: str, length: int = 6) -> str:
    """Devuelve `u_` + los primeros `length` caracteres hex del HMAC-SHA256(salt, username)."""
    raise NotImplementedError("T-E2-01: implementar con TDD")
