"""
Seed de usuarios genéricos para producción — Marcha Blanca.

Crea usuarios vinculados a estaciones de trabajo (no a personas) y
desactiva todos los usuarios de desarrollo/prueba preexistentes.

Usuarios creados:
  balanza1/2/3       → OperadorBalanza   (3 PC de balanza)
  laboratorio        → Laboratorista
  muestreo           → TecnicoMuestreo
  comercial1/2/3     → Comercial         (3 usuarios comerciales)
  gerencia_gral      → Gerencia          (Gerente General)
  gerencia_comercial → Gerencia          (Gerente Comercial)
  admin              → Admin             (se mantiene / actualiza)

Uso:
    python scripts/seed_usuarios_prod.py [--env prod]

Es idempotente: se puede correr múltiples veces sin duplicar.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# -- Definicion de usuarios genericos -----------------------------------------

USUARIOS_PROD = [
    # Balanza
    {
        "username": "balanza1",
        "nombre_completo": "PC Balanza 1",
        "rol": "OperadorBalanza",
        "email": "balanza1@invermin.pe",
        "password": "Balanza1#2026",
    },
    {
        "username": "balanza2",
        "nombre_completo": "PC Balanza 2",
        "rol": "OperadorBalanza",
        "email": "balanza2@invermin.pe",
        "password": "Balanza2#2026",
    },
    {
        "username": "balanza3",
        "nombre_completo": "PC Balanza 3",
        "rol": "OperadorBalanza",
        "email": "balanza3@invermin.pe",
        "password": "Balanza3#2026",
    },
    # Laboratorio
    {
        "username": "laboratorio",
        "nombre_completo": "PC Laboratorio",
        "rol": "Laboratorista",
        "email": "laboratorio@invermin.pe",
        "password": "Laboratorio#2026",
    },
    # Muestreo
    {
        "username": "muestreo",
        "nombre_completo": "PC Muestreo",
        "rol": "TecnicoMuestreo",
        "email": "muestreo@invermin.pe",
        "password": "Muestreo#2026",
    },
    # Comercial (3 usuarios)
    {
        "username": "comercial1",
        "nombre_completo": "Comercial Paititi 1",
        "rol": "Comercial",
        "email": "comercial1@invermin.pe",
        "password": "Comercial1#2026",
    },
    {
        "username": "comercial2",
        "nombre_completo": "Comercial Paititi 2",
        "rol": "Comercial",
        "email": "comercial2@invermin.pe",
        "password": "Comercial2#2026",
    },
    {
        "username": "comercial3",
        "nombre_completo": "Comercial Paititi 3",
        "rol": "Comercial",
        "email": "comercial3@invermin.pe",
        "password": "Comercial3#2026",
    },
    # Gerencia
    {
        "username": "gerencia_gral",
        "nombre_completo": "Gerente General",
        "rol": "Gerencia",
        "email": "gerencia.gral@invermin.pe",
        "password": "GerenciaGral#2026",
    },
    {
        "username": "gerencia_comercial",
        "nombre_completo": "Gerente Comercial",
        "rol": "Gerencia",
        "email": "gerencia.comercial@invermin.pe",
        "password": "GerenciaComercial#2026",
    },
    # Admin
    {
        "username": "admin",
        "nombre_completo": "Administrador del Sistema",
        "rol": "Admin",
        "email": "admin@invermin.pe",
        "password": "Admin#Paititi2026",
    },
]

# Usernames que NO se deben desactivar (son los genericos de prod)
USERNAMES_PROD = {u["username"] for u in USUARIOS_PROD}


def seed_usuarios(db, dry_run: bool = False):
    import app.core.security as security
    from app.models.models import Rol, Usuario

    prefix = "[DRY-RUN] " if dry_run else ""

    # -- 1. Desactivar todos los usuarios de prueba ----------------------------
    usuarios_actuales = db.query(Usuario).all()
    desactivados = 0
    for u in usuarios_actuales:
        if u.username not in USERNAMES_PROD:
            if u.activo:
                print(
                    f"{prefix}Desactivando usuario de prueba: '{u.username}' ({u.nombre_completo})"
                )
                if not dry_run:
                    u.activo = False
                desactivados += 1
    if not dry_run:
        db.flush()
    print(f"{prefix}>> {desactivados} usuarios de prueba desactivados.\n")

    # -- 2. Crear / actualizar usuarios genericos de produccion ----------------
    creados = 0
    actualizados = 0

    for datos in USUARIOS_PROD:
        rol = db.query(Rol).filter_by(codigo=datos["rol"]).first()
        if not rol:
            print(f"  [!]  Rol '{datos['rol']}' no encontrado. Ejecuta seed.py primero.")
            continue

        existing = db.query(Usuario).filter_by(username=datos["username"]).first()

        if existing:
            # Actualizar: reactivar si estaba inactivo y refrescar nombre/rol/email
            changed = False
            if not existing.activo:
                existing.activo = True
                changed = True
            if existing.nombre_completo != datos["nombre_completo"]:
                existing.nombre_completo = datos["nombre_completo"]
                changed = True
            if existing.rol_id != rol.id:
                existing.rol_id = rol.id
                changed = True
            if existing.email != datos["email"]:
                existing.email = datos["email"]
                changed = True
            # NOTA: no sobreescribimos password si ya existe para no pisar cambios manuales
            if changed:
                print(f"{prefix}Actualizando: '{datos['username']}' [{datos['rol']}]")
                actualizados += 1
            else:
                print(f"  OK (sin cambios): '{datos['username']}' [{datos['rol']}]")
        else:
            print(
                f"{prefix}Creando: '{datos['username']}' [{datos['rol']}] - password: {datos['password']}"
            )
            if not dry_run:
                nuevo = Usuario(
                    username=datos["username"],
                    nombre_completo=datos["nombre_completo"],
                    rol_id=rol.id,
                    email=datos["email"],
                    password_hash=security.hash_password(datos["password"]),
                    activo=True,
                )
                db.add(nuevo)
            creados += 1

    if not dry_run:
        db.commit()

    print(f"\n{prefix}Resumen:")
    print(f"  Creados:     {creados}")
    print(f"  Actualizados: {actualizados}")
    print(f"  Desactivados: {desactivados}")

    if creados > 0:
        print(
            "\n[!]  IMPORTANTE: Guarda las passwords en un lugar seguro y cambialas despues del primer login."
        )


def main():
    parser = argparse.ArgumentParser(description="Seed de usuarios genericos para produccion.")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin hacer cambios en la BD")
    parser.add_argument("--env", choices=["local", "prod"], default="local", help="Entorno de BD")
    args = parser.parse_args()

    # -- Cargar variables de entorno si es prod --------------------------------
    if args.env == "prod":
        env_file = Path(__file__).parent.parent / ".env.prod"
        print(f"Usando .env.prod: {env_file}\n")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ[k.strip()] = v.strip().strip('"')

    from app.core.database import SessionLocal

    if args.dry_run:
        print("=== MODO DRY-RUN: sin cambios en BD ===\n")

    db = SessionLocal()
    try:
        seed_usuarios(db, dry_run=args.dry_run)
    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
