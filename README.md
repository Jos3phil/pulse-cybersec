# Baryonem Pulse

Diagnóstico de evidencia de protección de datos para clínicas privadas. Tres agentes verificadores
(Vigía, Escriba y Archivista) leen una clínica en solo lectura y un redactor (Folio) escribe el informe.

> **Regla de oro:** el agente decide qué mirar, las herramientas deciden qué es verdad
> y al modelo solo le llegan números. Ningún dato de pacientes sale de la clínica.

Especificación completa: TDR v2 (documento del equipo).

## Estructura

| Carpeta | Responsable | Contenido |
| --- | --- | --- |
| `contract/` | Ambos | Esquemas JSON, catálogo de controles y validador compartido |
| `clinic/` | Timothy | La Clínica Inti: OpenEMR oficial en Docker y scripts de siembra |
| `tools/` | Timothy | Herramientas de solo lectura de los 3 agentes y filtro de privacidad |
| `engine/` | Timothy | Puntaje, ensamblado, firma y PDF |
| `agents/` | Compañero | Ciclo con Gemini, modo guion, instrucciones de los agentes y Folio |
| `console/` | Por asignar | Pantallas FastAPI + HTMX |
| `infra/` | Timothy | Google Cloud (desde el día 5) |
| `tests/` | Ambos | Unitarias, contrato e integración |

## Empezar (día 1)

```bash
# 1. Entorno de Python
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Pruebas que no necesitan la clínica
pytest -m "not integration"

# 3. Levantar la Clínica Inti (tarda 5 a 10 minutos la primera vez)
cp .env.example .env          # y cambia todas las claves
docker compose --env-file .env -f clinic/docker-compose.yml up -d
# OpenEMR: https://localhost:8443  (usuario admin, clave CLINIC_OE_ADMIN_PASS)

# 4. Crear el usuario de solo lectura de Pulse e inspeccionar el esquema
bash clinic/setup_readonly.sh
#    luego completar clinic/ESQUEMA.md y sembrar:
python clinic/seed/seed.py inti_full

# 5. Pruebas de integración (necesitan la clínica encendida)
pytest -m integration
```

## Cómo trabajamos (TDD)

1. Se escribe la prueba del TDR (por ejemplo `T-E2-01`) y se ve fallar.
2. Se escribe el código mínimo para pasarla.
3. Se refactoriza con las pruebas en verde y se hace commit.

- `main` está protegida: solo se mezcla por pull request con CI en verde y revisión del otro integrante.
- Un cambio en `contract/` se hace en pareja y sube `schema_version`.
- El CI arranca **en rojo a propósito**: las pruebas de `tools/` esperan su implementación.

## Estado de las pruebas iniciales

| Prueba | Estado inicial | Qué hace pasar |
| --- | --- | --- |
| `tests/test_contract.py` | Verde | Los ejemplos válidos e inválidos del contrato |
| `tests/test_pseudonymizer.py` (T-E2-01/02) | Rojo | `tools/pseudonymizer.py` |
| `tests/test_privacy_filter.py` (T-E6-01) | Rojo | `tools/privacy_filter.py` |
| `tests/test_validator.py` (T-E9-01/02) | Rojo | `contract/validator.py` |
| `tests/test_vigia_tools.py` (T-E3-01/02) | Integración | `tools/vigia_tools.py` + clínica sembrada |
