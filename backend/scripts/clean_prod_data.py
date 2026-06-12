"""
Script de limpieza de datos de prueba en produccion.

Elimina en orden seguro (respetando FK) todos los registros operativos:
  Liquidaciones -> Rumas -> Analisis Lab -> Muestreos -> Lotes -> Sesiones Descarga

Conserva intactos:
  Roles, Permisos, Modulos, Operaciones, Configuraciones,
  Usuarios, Entidades/Terceros, ProveedorAcopiador, ParametrosComerciales

Tras borrar, reinicia los contadores de autoincremento para que
los IDs comiencen en 1.

Uso:
    # Simulacion (solo muestra conteos, no borra nada):
    python scripts/clean_prod_data.py --dry-run

    # Limpieza real contra BD local (PostgreSQL):
    python scripts/clean_prod_data.py

    # Limpieza real contra produccion (SQL Server / Azure):
    python scripts/clean_prod_data.py --env prod

ADVERTENCIA: Esta operacion es IRREVERSIBLE.
Hacer backup de la BD antes de ejecutar.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# -- Tablas a limpiar en orden (de hija a padre por FK) -----------------------
#    (nombre_tabla_sql, nombre_legible)
TABLAS_LIMPIAR = [
    # Nivel mas profundo primero (FK order correcto)
    ("analisis_detalle", "Analisis Detalle"),  # -> analisis_ley, analisis_recuperacion
    ("analisis_ley", "Analisis de Ley"),  # -> mapeo_cip (cip FK)
    ("analisis_recuperacion", "Analisis de Recuperacion"),  # -> mapeo_cip (cip FK)
    ("pruebas_metalurgicas", "Pruebas Metalurgicas"),  # -> mapeo_cip (cip FK) — ANTES de mapeo_cip
    ("mapeo_cip", "Mapeo CIP"),  # -> lotes
    ("liquidaciones_lotes", "Liquidacion-Lotes (relacion)"),
    ("liquidaciones", "Liquidaciones"),
    ("rumas_campanas", "Ruma-Campanas (relacion)"),
    ("rumas", "Rumas"),
    ("muestreos", "Muestreos"),
    ("pesajes", "Pesajes"),
    ("lotes_eliminados", "Lotes Eliminados"),
    ("lotes", "Lotes"),  # -> sesiones_descarga, rumas
    ("sesion_documentos", "Documentos de Sesion"),  # -> sesiones_descarga
    ("sesiones_descarga", "Sesiones de Balanza"),
    ("campanas", "Campanas"),
]


def _detect_engine() -> str:
    """Detecta si es PostgreSQL o SQL Server (mssql)."""
    engine = os.environ.get("DB_ENGINE", "postgresql").lower()
    if "mssql" in engine or "sqlserver" in engine:
        return "mssql"
    return "postgresql"


def _quote(tabla: str, engine: str) -> str:
    """Quote de tabla segun motor."""
    if engine == "mssql":
        return f"[{tabla}]"
    return f'"{tabla}"'


def contar_registros(db, tabla: str, engine: str) -> int:
    from sqlalchemy import text

    result = db.execute(text(f"SELECT COUNT(*) FROM {_quote(tabla, engine)}"))
    return result.scalar()


def limpiar_tabla(db, tabla: str, engine: str, dry_run: bool):
    from sqlalchemy import text

    n = contar_registros(db, tabla, engine)
    if dry_run:
        print(f"  [DRY-RUN] {tabla}: {n} registros -> se borrarian")
    else:
        db.execute(text(f"DELETE FROM {_quote(tabla, engine)}"))
        print(f"  [OK] {tabla}: {n} registros eliminados")
    return n


def resetear_identity(db, tabla: str, engine: str, dry_run: bool):
    from sqlalchemy import text

    if engine == "mssql":
        if dry_run:
            print(f"  [DRY-RUN] DBCC CHECKIDENT('{tabla}', RESEED, 0)")
        else:
            try:
                db.execute(text(f"DBCC CHECKIDENT ('{tabla}', RESEED, 0)"))
                print(f"  [OK] IDENTITY reiniciado: {tabla}")
            except Exception as e:
                print(f"  [!]  No se pudo reiniciar IDENTITY de {tabla}: {e}")
    else:
        # PostgreSQL: resetear secuencia
        seq_name = f"{tabla}_id_seq"
        if dry_run:
            print(f"  [DRY-RUN] ALTER SEQUENCE {seq_name} RESTART WITH 1")
        else:
            try:
                db.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
                print(f"  [OK] Secuencia reiniciada: {seq_name}")
            except Exception as e:
                print(f"  [!]  No se pudo reiniciar secuencia {seq_name}: {e}")


def borrar_todo_mssql(db, tablas: list, dry_run: bool):
    """Para SQL Server: deshabilita FKs, borra todo, rehabilita."""
    from sqlalchemy import text

    if dry_run:
        for tabla, _ in tablas:
            try:
                n = contar_registros(db, tabla, "mssql")
                print(f"  [DRY-RUN] {tabla}: {n} registros -> se borrarian")
            except Exception as e:
                print(f"  [!]  Error al contar {tabla}: {str(e)[:80]}")
                db.rollback()
        return

    print("  Deshabilitando restricciones FK...")
    db.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'"))

    total = 0
    for tabla, _ in tablas:
        try:
            n = contar_registros(db, tabla, "mssql")
            db.execute(text(f"DELETE FROM [{tabla}]"))
            print(f"  [OK] {tabla}: {n} registros eliminados")
            total += n
        except Exception as e:
            print(f"  [X] Error en {tabla}: {str(e)[:100]}")

    print("  Rehabilitando restricciones FK...")
    db.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'"))

    return total


def main():
    parser = argparse.ArgumentParser(description="Limpieza de datos de prueba.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Solo muestra conteos, no borra nada"
    )
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

    engine = _detect_engine()
    print(f"Motor detectado: {engine}\n")

    # -- Confirmacion ----------------------------------------------------------
    if not args.dry_run:
        print("=" * 65)
        print("  [!!]  ADVERTENCIA: Esta operacion es IRREVERSIBLE")
        print(f"  Entorno: {args.env.upper()} ({engine})")
        print("  Se eliminaran TODOS los registros operativos:")
        for tabla, nombre in TABLAS_LIMPIAR:
            print(f"    - {nombre} [{tabla}]")
        print()
        print("  Se conservaran: Usuarios, Terceros, Parametros, Configuraciones")
        print("=" * 65)
        respuesta = input("\nEscribe CONFIRMAR para continuar: ").strip()
        if respuesta != "CONFIRMAR":
            print("Operacion cancelada.")
            sys.exit(0)
        print()

    db = SessionLocal()
    try:
        # -- Conteo previo siempre ---------------------
        print("=== FASE 1: Conteo de registros ===")
        total = 0
        for tabla, nombre in TABLAS_LIMPIAR:
            try:
                n = contar_registros(db, tabla, engine)
                print(f"  {nombre} [{tabla}]: {n} registros")
                total += n
            except Exception as e:
                print(f"  [!]  Error al contar {tabla}: {str(e)[:80]}")
                db.rollback()
        print(f"\n  Total a eliminar: {total} registros\n")

        if args.dry_run:
            print("=== MODO DRY-RUN: sin cambios en BD ===")
            if engine == "mssql":
                borrar_todo_mssql(db, TABLAS_LIMPIAR, dry_run=True)
            else:
                for tabla, _ in TABLAS_LIMPIAR:
                    limpiar_tabla(db, tabla, engine, dry_run=True)
            print("\n=== RESET SECUENCIAS/IDENTITY (simulado) ===")
            for tabla, _ in TABLAS_LIMPIAR:
                resetear_identity(db, tabla, engine, dry_run=True)
            return

        # -- Fase 2: Borrado ---------------------------------------------------
        print("=== FASE 2: Eliminando registros ===")
        if engine == "mssql":
            borrar_todo_mssql(db, TABLAS_LIMPIAR, dry_run=False)
        else:
            for tabla, _ in TABLAS_LIMPIAR:
                try:
                    limpiar_tabla(db, tabla, engine, dry_run=False)
                except Exception as e:
                    print(f"  [X] Error en {tabla}: {e}")
                    db.rollback()
                    print("\nSe realizo rollback. No se elimino nada.")
                    raise

        db.commit()
        print("\n[OK] Commit exitoso.\n")

        # -- Fase 3: Reset IDENTITY/secuencias ---------------------------------
        print("=== FASE 3: Reiniciando contadores ===")
        for tabla, _ in TABLAS_LIMPIAR:
            resetear_identity(db, tabla, engine, dry_run=False)

        db.commit()
        print("\n[OK] Contadores reiniciados. Los nuevos registros comenzaran desde ID=1.")
        print("\n=== Limpieza completada exitosamente ===")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
