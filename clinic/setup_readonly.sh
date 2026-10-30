#!/usr/bin/env bash
# Crea el usuario de solo lectura que usan las herramientas de Pulse.
# Uso (desde la raíz del repo, con la clínica encendida):  bash clinic/setup_readonly.sh
set -euo pipefail
set -a; source .env; set +a
docker compose --env-file .env -f clinic/docker-compose.yml exec -T mysql \
  mariadb -uroot -p"$CLINIC_DB_ROOT_PASS" <<SQL
CREATE USER IF NOT EXISTS '${PULSE_DB_USER}'@'%' IDENTIFIED BY '${PULSE_DB_PASS}';
-- Lectura de las tablas de OpenEMR (usuarios, ACL, log, globals, documents).
GRANT SELECT ON ${PULSE_DB_NAME}.* TO '${PULSE_DB_USER}'@'%';
-- Lectura de las tablas de privilegios, para que permisos_bd pueda ver los GRANTS
-- del usuario de la aplicación (F5). Sigue siendo solo lectura.
GRANT SELECT ON mysql.* TO '${PULSE_DB_USER}'@'%';
FLUSH PRIVILEGES;
SHOW GRANTS FOR '${PULSE_DB_USER}'@'%';
SQL
echo "Usuario ${PULSE_DB_USER} listo (solo SELECT)."
