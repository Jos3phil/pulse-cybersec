"""Conexión de solo lectura a la base de la clínica (usuario pulse_ro)."""
from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor


@contextmanager
def readonly_connection() -> Iterator[pymysql.connections.Connection]:
    conn = pymysql.connect(
        host=os.environ.get("PULSE_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("PULSE_DB_PORT", "3307")),
        user=os.environ["PULSE_DB_USER"],
        password=os.environ["PULSE_DB_PASS"],
        database=os.environ.get("PULSE_DB_NAME", "openemr"),
        cursorclass=DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SET SESSION TRANSACTION READ ONLY")
        yield conn
    finally:
        conn.close()
