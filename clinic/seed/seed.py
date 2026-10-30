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


# --- Usuarios sembrados (F1, F2, F3) -----------------------------------------------
# Cada paso marca sus filas con users.info = 'pulse-seed:<paso>' y log.log_from =
# 'pulse-seed', así se puede repetir sin duplicar y sin tocar lo que crea OpenEMR.
# Según clinic/ESQUEMA.md: el rol de administrador es gacl_groups_aro_map (grupo 11)
# unido con gacl_aro.value = username; el último acceso sale de log (event='login'),
# y la IP va en log.comments codificada en base64 ("success: <ip>").
GROUP_ADMIN, GROUP_CLINICIAN = 11, 12
FAKE_HASH = "$2y$10$invalidinvalidinvalidinvalidFAKEFAKEFAKEFAKEFAKEFAKEFAKEFA"


def _clean(tag: str) -> str:
    return f"""
DELETE gm FROM gacl_groups_aro_map gm JOIN gacl_aro a ON a.id = gm.aro_id
  JOIN users u ON u.username = a.value WHERE u.info = '{tag}';
DELETE a FROM gacl_aro a JOIN users u ON u.username = a.value WHERE u.info = '{tag}';
DELETE s FROM users_secure s JOIN users u ON u.id = s.id WHERE u.info = '{tag}';
DELETE l FROM log l JOIN users u ON u.username = l.user
  WHERE u.info = '{tag}' AND l.log_from = 'pulse-seed';
DELETE FROM users WHERE info = '{tag}';
"""


def _seed_users(tag: str, group: int, users: list[dict]) -> None:
    """users: [{username, fname, lname, active, logins: [(dias_atras, ip), ...]}]"""
    rows = ",".join(
        f"(UNHEX(REPLACE(UUID(),'-','')),'{u['username']}','{FAKE_HASH}',1,'{u['fname']}',"
        f"'{u['lname']}',{int(u['active'])},'{u['username']}@clinica-inti.example','{tag}',NOW())"
        for u in users
    )
    logins = ",".join(
        f"(TIMESTAMP(CURDATE() - INTERVAL {days} DAY, '{8 + i % 9:02d}:{(i * 7) % 60:02d}:00'),"
        f"'login','login','{u['username']}','Default',TO_BASE64('success: {ip}'),1,'pulse-seed')"
        for u in users
        for i, (days, ip) in enumerate(u["logins"])
    )
    names = ",".join(f"'{u['username']}'" for u in users)
    sql(
        "SET autocommit = 0;\n"
        + _clean(tag)
        + f"""
INSERT INTO users (uuid, username, password, authorized, fname, lname, active, email, info, date_created)
  VALUES {rows};
INSERT INTO users_secure (id, username, password, last_update_password)
  SELECT id, username, '{FAKE_HASH}', NOW() FROM users WHERE info = '{tag}';
SET @n = (SELECT COALESCE(MAX(id), 0) FROM gacl_aro);
INSERT INTO gacl_aro (id, section_value, value, order_value, name, hidden)
  SELECT (@n := @n + 1), 'users', username, 10, CONCAT(fname, ' ', lname), 0
  FROM users WHERE info = '{tag}';
UPDATE gacl_aro_seq SET id = (SELECT MAX(id) FROM gacl_aro);
INSERT INTO gacl_groups_aro_map (group_id, aro_id)
  SELECT {group}, id FROM gacl_aro WHERE value IN ({names});
INSERT INTO log (date, event, category, user, groupname, comments, success, log_from)
  VALUES {logins};
COMMIT;
"""
    )


def seed_f1_inactive_accounts() -> None:
    """F1: 42 cuentas en total, 7 activas sin acceso en MÁS de 90 días.

    Las 4 de fábrica (admin y 3 de sistema) + recepcion + 4 administradores (F2 y F3) +
    33 de aquí = 42. Aquí: 7 inactivas, 1 en el límite exacto (90 días, no cuenta),
    5 desactivadas con acceso viejo (tampoco cuentan) y 20 con acceso reciente.
    """
    stale = [("rquispe", 120), ("mhuaman", 145), ("lcastro", 180), ("jtorres", 210),
             ("vpaucar", 260), ("cflores", 330), ("dmendoza", 400)]
    users = [dict(username=n, fname=n[0].upper(), lname=n[1:].capitalize(), active=True,
                  logins=[(d, "192.168.1.30")]) for n, d in stale]
    users.append(dict(username="abenites", fname="A", lname="Benites", active=True,
                      logins=[(90, "192.168.1.31")]))        # T-E3-02: exactamente 90 días
    for i in range(1, 6):
        users.append(dict(username=f"exp{i:02d}", fname="Ex", lname=f"Personal{i}", active=False,
                          logins=[(200 + 15 * i, "192.168.1.32")]))
    for i in range(1, 21):
        users.append(dict(username=f"clin{i:02d}", fname="Clin", lname=f"Usuario{i}", active=True,
                          logins=[(i % 28 + 1, f"192.168.1.{40 + i}")]))
    assert len(users) == 33
    _seed_users("pulse-seed:f1", GROUP_CLINICIAN, users)


def seed_f2_shared_account() -> None:
    """F2: cuenta 'recepcion' con rol administrador usada desde 6 equipos (últimos 30 días)."""
    ips = [f"192.168.1.{10 + i}" for i in range(6)]
    logins = [(1 + (i * 3) % 28, ips[i % 6]) for i in range(18)]   # 3 accesos por equipo
    _seed_users("pulse-seed:f2", GROUP_ADMIN, [
        dict(username="recepcion", fname="Recepcion", lname="Compartida", active=True, logins=logins)])


def seed_f3_too_many_admins() -> None:
    """F3: 6 administradores activos = admin + recepcion (F2) + estos 4. oe-system está inactivo."""
    names = ["dir.medico", "ti.soporte", "jefe.admision", "contabilidad"]
    _seed_users("pulse-seed:f3", GROUP_ADMIN, [
        dict(username=n, fname=n.split(".")[0].capitalize(), lname="Admin", active=True,
             logins=[(2 + i, f"192.168.1.{20 + i}")]) for i, n in enumerate(names)])


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
