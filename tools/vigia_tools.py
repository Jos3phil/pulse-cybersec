"""E3 · Herramientas de Vigía (usuarios). Solo lectura. Ver TDR, sección 6."""
from __future__ import annotations

from datetime import date

from tools.privacy_filter import Code, Pseudonym, ToolOutput


class UserRow(ToolOutput):
    subject: Pseudonym
    active: bool
    is_admin: bool
    days_since_last_login: int | None


class ListUsersOutput(ToolOutput):
    total_accounts: int
    inactive_accounts: int
    threshold_days: int
    users: list[UserRow]


class AdminCountOutput(ToolOutput):
    admin_accounts: int


class AccessBySubjectOutput(ToolOutput):
    subject: Pseudonym
    distinct_devices_30d: int
    max_concurrent_sessions: int
    last_login: date | None


class PasswordPolicyOutput(ToolOutput):
    secure_password: bool
    password_expiration_days: int
    policy_code: Code


def listar_usuarios(threshold_days: int = 90) -> ListUsersOutput:
    """F1. Inactiva = activa y sin acceso en MÁS de `threshold_days` días (T-E3-01, T-E3-02)."""
    raise NotImplementedError("T-E3-01: implementar tras llenar clinic/ESQUEMA.md")


def contar_admins() -> AdminCountOutput:
    """F3. Número de cuentas activas en el grupo de administradores."""
    raise NotImplementedError


def accesos_por_usuario(subject: str) -> AccessBySubjectOutput:
    """F2. Equipos distintos y sesiones simultáneas de un seudónimo (T-E3-03)."""
    raise NotImplementedError


def politica_claves() -> PasswordPolicyOutput:
    """Ajustes globales de contraseñas."""
    raise NotImplementedError
