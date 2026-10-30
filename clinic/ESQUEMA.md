# Esquema real de OpenEMR (completar el día 1)

Todo lo que el TDR dice del esquema es una hipótesis hasta confirmarlo aquí, contra la
versión instalada. Conectarse con:

```bash
docker compose --env-file .env -f clinic/docker-compose.yml exec mysql \
  mariadb -uroot -p openemr
```

Verificado el 29/10/2026 con el usuario `pulse_ro` (solo lectura) sobre la base `openemr`
recién instalada (286 tablas, solo el usuario `admin` activo).

## Versión

- [X] Versión de OpenEMR (`SELECT * FROM version;`): **8.5.0** (v_database 555)
- [X] Versión de MariaDB (`SELECT VERSION();`): **12.3.3-MariaDB-ubu2404**

## Usuarios y roles (Vigía)

- [X] Columnas útiles de `users`: `id`, `username`, `fname`, `lname`, `active` (tinyint),
  `authorized` (tinyint), `email`, `date_created`, `last_updated`. **No tiene** columna de
  último acceso. La clave (`password`) está en `users`, pero el hash vigente está en `users_secure`.
- [X] Último acceso: no está en `users`. Se calcula desde `log`: `MAX(date)` donde
  `event='login'` y `category='login'`, agrupado por `user` (el texto de `log.user` es el `username`).
- [X] Evento de inicio de sesión en `log`: `event='login'`, `category='login'`
  (`success=1` si entró). Otros eventos presentes: `http-request-*`, `other-insert`,
  `security-administration-insert/update`, `oauth2`, `uuid`.
- [X] Quién es administrador: `gacl_groups_aro_map.group_id = 11` (grupo `Administrators`,
  en `gacl_aro_groups`) unido con `gacl_aro` por `aro_id = gacl_aro.id`; **`gacl_aro.value`
  es el `username`**. Otros grupos: 12 Clinicians, 13 Physicians, 14 Front Office,
  15 Accounting, 16 Emergency Login (breakglass).
- [X] Fallos de inicio de sesión en `users_secure`: `login_fail_counter` (contador actual),
  `total_login_fail_counter` (acumulado), `last_login_fail`, `auto_block_emailed`,
  `mfa_fail_counter`, `mfa_last_fail`. Se une a `users` por `username`.

## Bitácora y configuración (Escriba)

- [X] `globals`: `enable_auditlog=1`, `audit_events_query=0`, `audit_events_patient-record=1`.
- [X] Columna `checksum` en `log`: **existe pero está vacía** (0 de 187 filas con valor).
  No se puede usar para verificar integridad de la bitácora tal como está.
- [X] `SHOW GRANTS FOR 'openemr'@'%'`: `ALL PRIVILEGES ON openemr.*`. Es decir, la cuenta de
  la aplicación **puede borrar y modificar `log`** (esto es el hallazgo F5 de fábrica).

## Documentos (Archivista)

- [X] `globals`: `drive_encryption=1`, `document_storage_method=0` (0 = archivos en disco).
- [X] Ruta de los documentos dentro del contenedor (`sites/default/documents/...`): verificar con
  `docker compose  --env-file "D:\agents\pulse-repo\pulse\.env"  -f "D:\agents\pulse-repo\pulse\clinic\docker-compose.yml"  exec openemr ls /var/www/localhost/htdocs/openemr/sites/default/documents`
- [X] Columnas útiles de `documents`: `id`, `type` (file_url/blob/web_url), `url`, `mimetype`,
  `storagemethod`, `encrypted`, `size`, `hash`, `owner`, `date`, `deleted`, `foreign_id`.

## Decisiones tomadas

| Fecha | Qué confirmamos                                                                                                  | Impacto en las herramientas                                                                           |
| ----- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 29/10 | El rol de administrador se resuelve por `gacl_groups_aro_map` + `gacl_aro.value` (= username)                 | Vigía F3 une `users` con `gacl_*` por username; no hay columna `is_admin`                      |
| 29/10 | El grupo 11 trae de fábrica `admin` y `oe-system` (usuario de sistema, inactivo)                             | F3 debe filtrar `users.active = 1` o excluir `oe-system`, o contará 1 admin de más              |
| 29/10 | `users` no guarda último acceso                                                                                | Vigía calcula la inactividad con `MAX(log.date)` de `event='login'`                              |
| 29/10 | `log.checksum` está vacío en OpenEMR 8.5.0                                                                    | Escriba no puede validar integridad por checksum; revisar si hace falta activarlo o cambiar la prueba |
| 29/10 | La cuenta `openemr` tiene `ALL PRIVILEGES`                                                                    | F5 sale de fábrica, como suponía `seed.py`                                                        |
| 29/10 | Instalación limpia: 4 usuarios (`admin` activo; `phimail-service`, `portal-user`, `oe-system` inactivos) | `seed.py` debe sumar los 42 de F1 sobre estos 4, o ajustar los conteos esperados                    |
