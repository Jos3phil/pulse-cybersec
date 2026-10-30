"""E5 · Herramientas de Archivista (documentos de historias). Solo lectura.

Abrir un archivo para leer sus primeros bytes ocurre en la clínica y solo produce
un conteo. Ninguna salida contiene nombres de archivo, rutas ni contenido.
"""
from __future__ import annotations

from tools.privacy_filter import ToolOutput


class DocumentInventoryOutput(ToolOutput):
    documents_total: int
    documents_pdf: int
    documents_image: int
    documents_other: int
    orphan_files: int


class DocumentEncryptionOutput(ToolOutput):
    drive_encryption_enabled: bool
    documents_total: int
    documents_unencrypted: int


class FolderPermissionsOutput(ToolOutput):
    readable_by_others: bool
    writable_by_others: bool


class BackupCoverageOutput(ToolOutput):
    documents_total: int
    documents_missing_in_backup: int


def inventario_documentos() -> DocumentInventoryOutput:
    raise NotImplementedError


def cifrado_documentos() -> DocumentEncryptionOutput:
    """F10 (T-E5-01): un archivo que empieza con %PDF o con cabecera de imagen está sin cifrar."""
    raise NotImplementedError


def permisos_carpeta() -> FolderPermissionsOutput:
    """F11 (T-E5-02)."""
    raise NotImplementedError


def respaldo_incluye_documentos() -> BackupCoverageOutput:
    """F12."""
    raise NotImplementedError
