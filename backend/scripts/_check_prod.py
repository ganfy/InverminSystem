"""Quick check of production DB status."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

env_file = Path(__file__).parent.parent / ".env.prod"
with open(env_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip().strip('"')

from app.core.database import SessionLocal  # noqa: E402
from sqlalchemy import text  # noqa: E402

db = SessionLocal()
try:
    tables = [
        ("roles", "Roles"),
        ("usuarios", "Usuarios"),
        ("entidades", "Entidades"),
        ("sesiones_descarga", "Sesiones descarga"),
        ("lotes", "Lotes"),
        ("muestreos", "Muestreos"),
        ("analisis_ley", "Analisis ley"),
        ("analisis_recuperacion", "Analisis recuperacion"),
        ("liquidaciones", "Liquidaciones"),
        ("rumas", "Rumas"),
        ("campanas", "Campanas"),
    ]
    print("=== Estado BD Produccion (Azure) ===\n")
    for tabla, nombre in tables:
        try:
            r = db.execute(text(f"SELECT COUNT(*) FROM [{tabla}]"))
            print(f"  {nombre} [{tabla}]: {r.scalar()}")
        except Exception as e:
            print(f"  {nombre} [{tabla}]: ERROR - {str(e)[:60]}")
            db.rollback()

    # List current users
    print("\n=== Usuarios actuales ===")
    rows = db.execute(
        text(
            "SELECT u.username, u.nombre_completo, r.codigo, u.activo "
            "FROM [usuarios] u LEFT JOIN [roles] r ON u.rol_id = r.id "
            "ORDER BY u.id"
        )
    )
    for row in rows:
        status = "ACTIVO" if row[3] else "INACTIVO"
        print(f"  {row[0]:20s} | {row[1]:30s} | {row[2]:20s} | {status}")

finally:
    db.close()
