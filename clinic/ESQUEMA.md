# Esquema real de OpenEMR (completar el día 1)

Todo lo que el TDR dice del esquema es una hipótesis hasta confirmarlo aquí, contra la
versión instalada. Conectarse con:

```bash
docker compose --env-file .env -f clinic/docker-compose.yml exec mysql \
  mariadb -uroot -p openemr
```

## Versión

- [ ] Versión de OpenEMR (pantalla Acerca de, o `SELECT * FROM version;`): ______
- [ ] Versión de MariaDB (`SELECT VERSION();`): ______

## Usuarios y roles (Vigía)

- [ ] Columnas útiles de `users` (`DESCRIBE users;`): id, username, active, authorized, ...
- [ ] ¿Dónde se guarda el último acceso? (`users` no lo tiene; revisar `log` y `users_secure`)
- [ ] Nombre exacto del evento de inicio de sesión en `log`:
      `SELECT event, category, COUNT(*) FROM log GROUP BY event, category ORDER BY 3 DESC LIMIT 30;`
- [ ] Cómo se sabe quién es administrador (tablas `gacl_aro`, `gacl_groups_aro_map`, `gacl_aro_groups`)
- [ ] Columnas de fallos de inicio de sesión en `users_secure`

## Bitácora y configuración (Escriba)

- [ ] `SELECT gl_name, gl_value FROM globals WHERE gl_name IN ('enable_auditlog','audit_events_query','audit_events_patient-record');`
- [ ] ¿La tabla `log` tiene la columna `checksum` con valores?
- [ ] `SHOW GRANTS FOR 'openemr'@'%';` ¿Puede borrar en `log`?

## Documentos (Archivista)

- [ ] `SELECT gl_name, gl_value FROM globals WHERE gl_name IN ('drive_encryption','document_storage_method');`
- [ ] Ruta de los documentos dentro del contenedor (`sites/default/documents/...`)
- [ ] Columnas útiles de `documents`: id, type, url, mimetype, storagemethod, ...

## Decisiones tomadas

| Fecha | Qué confirmamos | Impacto en las herramientas |
| --- | --- | --- |
| | | |
