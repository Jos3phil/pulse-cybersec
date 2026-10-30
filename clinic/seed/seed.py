"""Siembra los escenarios de la Clínica Inti: inti_full, clean y partial.

Uso (desde la raíz del repo, con la clínica encendida):
    python clinic/seed/seed.py inti_full

Estado: F4, F6 y F7 listos. F1, F2, F3 y F10 a F12 se completan DESPUÉS de llenar
clinic/ESQUEMA.md (día 1), porque dependen de nombres de tablas y eventos que hay
que confirmar en la versión instalada.

Todos los datos son inventados. Nunca cargar datos reales de pacientes.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ["docker", "compose", "--env-file", str(ROOT / ".env"), "-f", str(ROOT / "clinic/docker-compose.yml")]
BACKUPS = ROOT / "clinic/backups"


def sql(statement: str) -> None:
    """Ejecuta SQL como root dentro del contenedor de MariaDB (solo para sembrar)."""
    root_pass = os.environ["CLINIC_DB_ROOT_PASS"]
    subprocess.run(
        [*COMPOSE, "exec", "-T", "mysql", "mariadb", "-uroot", f"-p{root_pass}", "openemr"],
        input=statement.encode(),
        check=True,
    )


def set_global(name: str, value: str) -> None:
    sql(
        "INSERT INTO globals (gl_name, gl_index, gl_value) "
        f"VALUES ('{name}', 0, '{value}') "
        f"ON DUPLICATE KEY UPDATE gl_value = '{value}';"
    )


# --- F4: no se registran las lecturas de historias -------------------------------
def seed_f4_reads_not_logged() -> None:
    set_global("enable_auditlog", "1")      # la bitácora general está encendida...
    set_global("audit_events_query", "0")   # ...pero no registra las lecturas (valor de fábrica)


def fix_f4() -> None:
    set_global("enable_auditlog", "1")
    set_global("audit_events_query", "1")


# --- F5: el usuario de la aplicación puede borrar la bitácora ---------------------
# OpenEMR crea su usuario de base de datos con todos los privilegios sobre `openemr`,
# así que F5 suele venir de fábrica. Confirmar con SHOW GRANTS en ESQUEMA.md.


# --- F6 y F7: respaldo antiguo y respaldo que no restaura --------------------------
def seed_f6_f7_backups() -> None:
    BACKUPS.mkdir(exist_ok=True)
    root_pass = os.environ["CLINIC_DB_ROOT_PASS"]
    old = BACKUPS / "openemr_2026-09-24.sql"
    broken = BACKUPS / "openemr_2026-10-27.sql"
    with old.open("wb") as fh:
        subprocess.run(
            [*COMPOSE, "exec", "-T", "mysql", "mariadb-dump", "-uroot", f"-p{root_pass}", "openemr"],
            stdout=fh, check=True,
        )
    forty_days_ago = time.time() - 40 * 86400
    os.utime(old, (forty_days_ago, forty_days_ago))          # F6: tiene 40 días
    data = old.read_bytes()
    broken.write_bytes(data[: len(data) // 3])               # F7: volcado truncado


# --- Pendientes tras inspeccionar el esquema ---------------------------------------
def seed_f1_inactive_accounts() -> None:
    """F1: 42 cuentas, 7 activas sin acceso en más de 90 días. Ver ESQUEMA.md."""
    raise NotImplementedError("Completar tras confirmar el evento de inicio de sesión en `log`")


def seed_f2_shared_account() -> None:
    """F2: cuenta 'recepcion' con rol administrador usada desde 6 equipos."""
    raise NotImplementedError("Completar tras confirmar cómo se registran IP y sesiones en `log`")


def seed_f3_too_many_admins() -> None:
    """F3: 6 administradores. Ver tablas gacl_* en ESQUEMA.md."""
    raise NotImplementedError("Completar tras confirmar cómo se asigna el grupo de administradores")


def seed_f10_to_f12_documents() -> None:
    """F10 a F12: documentos falsos sin cifrar, carpeta legible por otros, fuera del respaldo."""
    raise NotImplementedError("Completar tras confirmar la ruta de documentos y drive_encryption")


SCENARIOS = {
    "inti_full": [seed_f4_reads_not_logged, seed_f6_f7_backups,
                  seed_f1_inactive_accounts, seed_f2_shared_account,
                  seed_f3_too_many_admins, seed_f10_to_f12_documents],
    "partial": [seed_f4_reads_not_logged],
    "clean": [fix_f4],
}


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    scenario = sys.argv[1] if len(sys.argv) > 1 else "inti_full"
    for step in SCENARIOS[scenario]:
        try:
            step()
            print(f"ok    {step.__name__}")
        except NotImplementedError as exc:
            print(f"falta {step.__name__}: {exc}")


if __name__ == "__main__":
    main()
