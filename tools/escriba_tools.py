"""E4 · Herramientas de Escriba (base de datos, bitácora y respaldos). Solo lectura."""
from __future__ import annotations

from datetime import date

from tools.privacy_filter import Code, ToolOutput


class AuditConfigOutput(ToolOutput):
    audit_enabled: bool
    read_events_logged: bool


class DbGrantsOutput(ToolOutput):
    app_user_can_delete_log: bool
    app_user_can_truncate_log: bool


class LogStatsOutput(ToolOutput):
    hours: int
    events_total: int
    events_patient_record: int
    events_select: int
    has_checksums: bool


class BackupRow(ToolOutput):
    backup_id: Code
    taken_on: date
    age_days: int
    size_bytes: int


class BackupListOutput(ToolOutput):
    backups: list[BackupRow]


class RestoreTestOutput(ToolOutput):
    backup_id: Code
    restore_ok: bool
    seconds: float
    tables_matching_manifest: int
    error: Code | None


def config_auditoria() -> AuditConfigOutput:
    """F4 (T-E4-01)."""
    raise NotImplementedError


def permisos_bd() -> DbGrantsOutput:
    """F5 (T-E4-02)."""
    raise NotImplementedError


def estadisticas_bitacora(hours: int = 24) -> LogStatsOutput:
    raise NotImplementedError


def listar_respaldos() -> BackupListOutput:
    """F6 (T-E4-03)."""
    raise NotImplementedError


def probar_restauracion(backup_id: str) -> RestoreTestOutput:
    """F7 (T-E4-04). Restaura en un contenedor descartable y lo destruye siempre."""
    raise NotImplementedError
