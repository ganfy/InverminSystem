"""
fix_rbac_permisos.py — Sincroniza la tabla permisos con lo que el código aplica HOY.

Contexto:
    El seed.py original tenía permisos que en algunos casos difieren de los
    sets hardcodeados en los routers (la autorización real en uso).
    Este script hace que la BD refleje el comportamiento actual del código,
    como paso previo a reemplazar esos hardcodes por check_permiso().

Cambios que aplica:
    1. Agrega el rol JefeComercial (faltaba en el seed original).
    2. Agrega operaciones especiales: VIEW_CONFIDENTIAL, EDIT_PARAMS.
    3. Inserta permisos de JefeComercial en todos los módulos donde hoy
       los routers lo incluyen.
    4. Agrega BALANZA/EDIT_PARAMS → solo Admin puede editar lotes.
    5. Agrega LIQUIDACIONES/EDIT_PARAMS → Admin, Gerencia, JefeComercial.
    6. Agrega LABORATORIO/VIEW_CONFIDENTIAL → Admin, Gerencia, Comercial, JefeComercial.
    7. Agrega MUESTREO/UPDATE para JefeComercial (asignar laboratorio a CIP).

Es idempotente: no duplica registros existentes. Seguro de correr en producción.

Uso:
    python scripts/fix_rbac_permisos.py
    python scripts/fix_rbac_permisos.py --env prod
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def run(db):
    from app.models.models import Modulo, Operacion, Permiso, Rol

    print("\n=== Sincronizando permisos BD con comportamiento real del código ===\n")

    # ── 1. Rol JefeComercial ──────────────────────────────────────────────────
    jefe = db.query(Rol).filter_by(codigo="JefeComercial").first()
    if not jefe:
        jefe = Rol(codigo="JefeComercial", nombre="Jefe Comercial")
        db.add(jefe)
        db.flush()
        print("  [+] Rol creado: JefeComercial")
    else:
        print("  [ok] Rol JefeComercial ya existe")

    # ── 2. Operaciones especiales ─────────────────────────────────────────────
    ops_nuevas = [
        ("VIEW_CONFIDENTIAL", "Ver datos confidenciales (IP de lote)"),
        ("EDIT_PARAMS", "Editar parámetros sensibles"),
    ]
    op_map = {}
    for codigo, nombre in ops_nuevas:
        op = db.query(Operacion).filter_by(codigo=codigo).first()
        if not op:
            op = Operacion(codigo=codigo, nombre=nombre)
            db.add(op)
            db.flush()
            print(f"  [+] Operación creada: {codigo}")
        else:
            print(f"  [ok] Operación {codigo} ya existe")
        op_map[codigo] = op

    # Cargar también las operaciones CRUD existentes en el mapa
    for codigo in ("VIEW", "CREATE", "UPDATE", "DELETE"):
        op = db.query(Operacion).filter_by(codigo=codigo).first()
        if op:
            op_map[codigo] = op

    db.commit()

    # ── 3. Helper para insertar/actualizar permiso idempotente ────────────────
    creados = 0
    actualizados = 0

    def upsert_permiso(rol_codigo, modulo_codigo, operacion_codigo, permitido):
        nonlocal creados, actualizados
        rol = db.query(Rol).filter_by(codigo=rol_codigo).first()
        mod = db.query(Modulo).filter_by(codigo=modulo_codigo).first()
        op = (
            op_map.get(operacion_codigo)
            or db.query(Operacion).filter_by(codigo=operacion_codigo).first()
        )

        if not rol:
            print(f"  [!] Rol no encontrado: {rol_codigo}")
            return
        if not mod:
            print(f"  [!] Módulo no encontrado: {modulo_codigo}")
            return
        if not op:
            print(f"  [!] Operación no encontrada: {operacion_codigo}")
            return

        existing = (
            db.query(Permiso).filter_by(rol_id=rol.id, modulo_id=mod.id, operacion_id=op.id).first()
        )
        if not existing:
            db.add(
                Permiso(
                    rol_id=rol.id,
                    modulo_id=mod.id,
                    operacion_id=op.id,
                    permitido=permitido,
                )
            )
            creados += 1
        elif existing.permitido != permitido:
            existing.permitido = permitido
            actualizados += 1
            print(
                f"  [~] Actualizado: {rol_codigo}/{modulo_codigo}/{operacion_codigo} → {permitido}"
            )

    # ── 4. Permisos de JefeComercial ──────────────────────────────────────────
    # Derivado de los sets hardcodeados en los routers actuales:
    #   _ROLES_COMERCIAL = {Admin, Gerencia, Comercial, JefeComercial}
    #   Módulos afectados: RUMAS, CAMPANAS, MUESTREO, LABORATORIO, DASHBOARD,
    #                      LIQUIDACIONES, TERCEROS, PRUEBAS_MET
    print("\n  Insertando permisos de JefeComercial...")
    jefe_permisos = [
        # RUMAS — _ROLES_COMERCIAL en todos los endpoints
        ("JefeComercial", "RUMAS", "VIEW", True),
        ("JefeComercial", "RUMAS", "CREATE", True),
        ("JefeComercial", "RUMAS", "UPDATE", True),
        # CAMPANAS — _ROLES_COMERCIAL para GET; _ROLES_GERENCIA para POST/PATCH
        ("JefeComercial", "CAMPANAS", "VIEW", True),
        # MUESTREO — _ROLES_COMERCIAL en PATCH /cips/{id}/laboratorio
        ("JefeComercial", "MUESTREO", "VIEW", True),
        ("JefeComercial", "MUESTREO", "UPDATE", True),
        # LABORATORIO — check_permiso + _puede_ver_ip
        ("JefeComercial", "LABORATORIO", "VIEW", True),
        ("JefeComercial", "LABORATORIO", "CREATE", True),
        ("JefeComercial", "LABORATORIO", "UPDATE", True),
        ("JefeComercial", "LABORATORIO", "DELETE", True),
        # DASHBOARD — require_roles en trazabilidad lote
        ("JefeComercial", "DASHBOARD", "VIEW", True),
        ("JefeComercial", "DASHBOARD", "UPDATE", True),
        # LIQUIDACIONES — frontend meta.roles lo incluye; consistente con sistema
        ("JefeComercial", "LIQUIDACIONES", "VIEW", True),
        ("JefeComercial", "LIQUIDACIONES", "CREATE", True),
        ("JefeComercial", "LIQUIDACIONES", "UPDATE", True),
        # TERCEROS — frontend meta.roles y TercerosView.vue lo incluyen
        ("JefeComercial", "TERCEROS", "VIEW", True),
        ("JefeComercial", "TERCEROS", "CREATE", True),
        ("JefeComercial", "TERCEROS", "UPDATE", True),
        # PRUEBAS_MET — frontend meta.roles lo incluye en /pruebas
        ("JefeComercial", "PRUEBAS_MET", "VIEW", True),
    ]
    for args in jefe_permisos:
        upsert_permiso(*args)

    # ── 5. VIEW_CONFIDENTIAL — quién puede ver el IP del lote en laboratorio ──
    # Actualmente: _puede_ver_ip() → {Admin, Gerencia, Comercial, JefeComercial}
    # Laboratorista NO puede ver IP (muestreo ciego, confidencialidad RF-LAB-001)
    print("\n  Insertando permisos VIEW_CONFIDENTIAL (ver IP en Laboratorio)...")
    for rol_codigo in ("Admin", "Gerencia", "Comercial", "JefeComercial"):
        upsert_permiso(rol_codigo, "LABORATORIO", "VIEW_CONFIDENTIAL", True)
    for rol_codigo in ("Laboratorista", "TecnicoMuestreo", "OperadorBalanza", "Metalurgista"):
        upsert_permiso(rol_codigo, "LABORATORIO", "VIEW_CONFIDENTIAL", False)

    # ── 6. EDIT_PARAMS en BALANZA — solo Admin puede editar lotes ─────────────
    # Actualmente: balanza.py service L534: if rol != ADMIN → 403
    # OperadorBalanza tiene UPDATE=True para crear pesajes, pero no para editar lote.
    print("\n  Insertando permisos EDIT_PARAMS en BALANZA (editar lote completo)...")
    upsert_permiso("Admin", "BALANZA", "EDIT_PARAMS", True)
    upsert_permiso("Comercial", "BALANZA", "EDIT_PARAMS", True)
    upsert_permiso("Comercial", "BALANZA", "UPDATE", True)
    upsert_permiso("Comercial", "MUESTREO", "UPDATE", True)
    for rol_codigo in (
        "Gerencia",
        "JefeComercial",
        "OperadorBalanza",
        "TecnicoMuestreo",
        "Laboratorista",
        "Metalurgista",
    ):
        upsert_permiso(rol_codigo, "BALANZA", "EDIT_PARAMS", False)

    # ── 7. EDIT_PARAMS en LIQUIDACIONES — Admin, Gerencia, JefeComercial ──────
    # Actualmente: liquidaciones.py L262-271:
    #   rol in {Admin.value, Gerencia.value, JefeComercial.value}
    # Comercial tiene LIQUIDACIONES/UPDATE=True (puede emitir/cambiar estado)
    # pero NO puede editar parámetros de lote en una liquidación.
    print("\n  Insertando permisos EDIT_PARAMS en LIQUIDACIONES (editar params de lote)...")
    for rol_codigo in ("Admin", "Gerencia", "JefeComercial"):
        upsert_permiso(rol_codigo, "LIQUIDACIONES", "EDIT_PARAMS", True)
    for rol_codigo in (
        "Comercial",
        "TecnicoMuestreo",
        "Laboratorista",
        "Metalurgista",
        "OperadorBalanza",
    ):
        upsert_permiso(rol_codigo, "LIQUIDACIONES", "EDIT_PARAMS", False)

    # ── 8. TERCEROS para Comercial — puede ver y registrar, pero NO editar parámetros ──
    # Comercial puede: ver la lista, registrar proveedores (hasta sección Acopiador)
    # Comercial NO puede: editar parámetros comerciales (UPDATE queda bloqueado)
    print("\n  Insertando permisos TERCEROS para Comercial (VIEW + CREATE, sin UPDATE)...")
    upsert_permiso("Comercial", "TERCEROS", "VIEW", True)
    upsert_permiso("Comercial", "TERCEROS", "CREATE", True)
    upsert_permiso("Comercial", "TERCEROS", "UPDATE", False)  # Bloquea editar parámetros
    upsert_permiso("Comercial", "TERCEROS", "DELETE", False)

    print(
        "\n  Insertando permiso PRUEBAS_MET/UPDATE para Metalurgista (necesario para etiquetar y adiciones)..."
    )
    upsert_permiso("Metalurgista", "PRUEBAS_MET", "UPDATE", True)

    db.commit()
    print(f"\n  {creados} permisos nuevos insertados, {actualizados} actualizados.")

    print("\n=== Sincronización completada ===\n")


def main():
    parser = argparse.ArgumentParser(
        description="Sincroniza permisos BD con comportamiento real del código."
    )
    parser.add_argument("--env", choices=["local", "prod"], default="local")
    args = parser.parse_args()

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

    db = SessionLocal()
    try:
        run(db)
    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
