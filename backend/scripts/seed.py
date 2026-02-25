"""
Seed de datos base del sistema.

Crea los registros mínimos necesarios para que el sistema funcione:
- Roles del sistema
- Módulos
- Operaciones (CRUD)
- Matriz de permisos RBAC (según requerimiento RF-SYS-001)
- Usuario Admin inicial

Correr UNA sola vez después de la primera migración:
    python scripts/seed.py

Es idempotente: usa INSERT OR SKIP para no duplicar registros.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import app.core.security
from app.core.database import SessionLocal
from app.models.models import Modulo, Operacion, Permiso, Rol, Usuario

# ── Datos ─────────────────────────────────────────────────────────────────────

ROLES = [
    # Roles de sistema
    {"codigo": "Admin", "nombre": "Administrador"},
    {"codigo": "Gerencia", "nombre": "Gerencia General"},
    {"codigo": "Comercial", "nombre": "Área Comercial"},
    {"codigo": "Laboratorista", "nombre": "Técnico Analista"},
    {"codigo": "OperadorBalanza", "nombre": "Operador de Balanza"},
    {"codigo": "TecnicoMuestreo", "nombre": "Técnico de Muestreo"},
    # Roles comerciales de entidades
    {"codigo": "PROVEEDOR", "nombre": "Proveedor"},
    {"codigo": "ACOPIADOR", "nombre": "Acopiador"},
]

MODULOS = [
    {"codigo": "BALANZA", "nombre": "Módulo de Balanza"},
    {"codigo": "MUESTREO", "nombre": "Módulo de Muestreo"},
    {"codigo": "LABORATORIO", "nombre": "Módulo de Laboratorio"},
    {"codigo": "PRUEBAS_MET", "nombre": "Módulo de Pruebas Metalúrgicas"},
    {"codigo": "RUMAS", "nombre": "Módulo de Rumas"},
    {"codigo": "LIQUIDACIONES", "nombre": "Módulo de Liquidaciones"},
    {"codigo": "CAMPANAS", "nombre": "Módulo de Campañas"},
    {"codigo": "TERCEROS", "nombre": "Módulo de Terceros"},
    {"codigo": "DASHBOARD", "nombre": "Dashboard Principal"},
    {"codigo": "ADMINISTRACION", "nombre": "Módulo de Administración"},
]

OPERACIONES = [
    {"codigo": "CREATE", "nombre": "Crear"},
    {"codigo": "UPDATE", "nombre": "Editar"},
    {"codigo": "DELETE", "nombre": "Eliminar"},
    {"codigo": "VIEW", "nombre": "Ver"},
]

# Matriz de permisos: (rol, modulo, operacion) → permitido
# Basado en RF-SYS-001 — Matriz de Permisos por Módulo
# True = permitido, False = denegado
# (VIEW también incluye solo-lectura)
PERMISOS = [
    # ── BALANZA ──────────────────────────────────────────────────────────────
    ("Admin", "BALANZA", "CREATE", True),
    ("Admin", "BALANZA", "UPDATE", True),
    ("Admin", "BALANZA", "DELETE", True),
    ("Admin", "BALANZA", "VIEW", True),
    ("Gerencia", "BALANZA", "CREATE", False),
    ("Gerencia", "BALANZA", "UPDATE", False),
    ("Gerencia", "BALANZA", "DELETE", True),
    ("Gerencia", "BALANZA", "VIEW", True),
    ("Comercial", "BALANZA", "CREATE", False),
    ("Comercial", "BALANZA", "UPDATE", False),
    ("Comercial", "BALANZA", "DELETE", True),
    ("Comercial", "BALANZA", "VIEW", True),
    ("Laboratorista", "BALANZA", "CREATE", False),
    ("Laboratorista", "BALANZA", "UPDATE", False),
    ("Laboratorista", "BALANZA", "DELETE", False),
    ("Laboratorista", "BALANZA", "VIEW", False),
    ("OperadorBalanza", "BALANZA", "CREATE", True),
    ("OperadorBalanza", "BALANZA", "UPDATE", True),
    ("OperadorBalanza", "BALANZA", "DELETE", False),
    ("OperadorBalanza", "BALANZA", "VIEW", True),
    ("TecnicoMuestreo", "BALANZA", "CREATE", False),
    ("TecnicoMuestreo", "BALANZA", "UPDATE", False),
    ("TecnicoMuestreo", "BALANZA", "DELETE", False),
    ("TecnicoMuestreo", "BALANZA", "VIEW", False),
    # ── MUESTREO ─────────────────────────────────────────────────────────────
    ("Admin", "MUESTREO", "CREATE", True),
    ("Admin", "MUESTREO", "UPDATE", True),
    ("Admin", "MUESTREO", "VIEW", True),
    ("Gerencia", "MUESTREO", "VIEW", True),
    ("Comercial", "MUESTREO", "VIEW", True),
    ("OperadorBalanza", "MUESTREO", "VIEW", True),
    ("TecnicoMuestreo", "MUESTREO", "CREATE", True),
    ("TecnicoMuestreo", "MUESTREO", "UPDATE", True),
    ("TecnicoMuestreo", "MUESTREO", "VIEW", True),
    # ── LABORATORIO ───────────────────────────────────────────────────────────
    ("Admin", "LABORATORIO", "CREATE", True),
    ("Admin", "LABORATORIO", "UPDATE", True),
    ("Admin", "LABORATORIO", "DELETE", True),
    ("Admin", "LABORATORIO", "VIEW", True),
    ("Gerencia", "LABORATORIO", "DELETE", True),
    ("Gerencia", "LABORATORIO", "VIEW", True),
    ("Comercial", "LABORATORIO", "CREATE", True),
    ("Comercial", "LABORATORIO", "UPDATE", True),
    ("Comercial", "LABORATORIO", "DELETE", True),
    ("Comercial", "LABORATORIO", "VIEW", True),
    ("Laboratorista", "LABORATORIO", "CREATE", True),
    ("Laboratorista", "LABORATORIO", "VIEW", True),
    # ── PRUEBAS METALÚRGICAS ──────────────────────────────────────────────────
    ("Admin", "PRUEBAS_MET", "CREATE", True),
    ("Admin", "PRUEBAS_MET", "VIEW", True),
    ("Gerencia", "PRUEBAS_MET", "VIEW", True),
    ("Comercial", "PRUEBAS_MET", "VIEW", True),
    ("TecnicoMuestreo", "PRUEBAS_MET", "CREATE", True),
    ("TecnicoMuestreo", "PRUEBAS_MET", "VIEW", True),
    # ── RUMAS ─────────────────────────────────────────────────────────────────
    ("Admin", "RUMAS", "CREATE", True),
    ("Admin", "RUMAS", "UPDATE", True),
    ("Admin", "RUMAS", "DELETE", True),
    ("Admin", "RUMAS", "VIEW", True),
    ("Gerencia", "RUMAS", "CREATE", True),
    ("Gerencia", "RUMAS", "UPDATE", True),
    ("Gerencia", "RUMAS", "VIEW", True),
    ("Comercial", "RUMAS", "CREATE", True),
    ("Comercial", "RUMAS", "UPDATE", True),
    ("Comercial", "RUMAS", "VIEW", True),
    # ── LIQUIDACIONES ─────────────────────────────────────────────────────────
    ("Admin", "LIQUIDACIONES", "CREATE", True),
    ("Admin", "LIQUIDACIONES", "UPDATE", True),
    ("Admin", "LIQUIDACIONES", "VIEW", True),
    ("Gerencia", "LIQUIDACIONES", "CREATE", True),
    ("Gerencia", "LIQUIDACIONES", "UPDATE", True),
    ("Gerencia", "LIQUIDACIONES", "VIEW", True),
    ("Comercial", "LIQUIDACIONES", "CREATE", True),
    ("Comercial", "LIQUIDACIONES", "UPDATE", True),
    ("Comercial", "LIQUIDACIONES", "VIEW", True),
    # ── CAMPAÑAS ──────────────────────────────────────────────────────────────
    ("Admin", "CAMPANAS", "CREATE", True),
    ("Admin", "CAMPANAS", "UPDATE", True),
    ("Admin", "CAMPANAS", "DELETE", True),
    ("Admin", "CAMPANAS", "VIEW", True),
    ("Gerencia", "CAMPANAS", "CREATE", True),
    ("Gerencia", "CAMPANAS", "UPDATE", True),
    ("Gerencia", "CAMPANAS", "VIEW", True),
    ("Comercial", "CAMPANAS", "VIEW", True),
    ("OperadorBalanza", "CAMPANAS", "VIEW", True),
    ("TecnicoMuestreo", "CAMPANAS", "VIEW", True),
    # ── TERCEROS (Proveedores/Acopiadores) ────────────────────────────────────
    ("Admin", "TERCEROS", "CREATE", True),
    ("Admin", "TERCEROS", "UPDATE", True),
    ("Admin", "TERCEROS", "VIEW", True),
    ("Gerencia", "TERCEROS", "CREATE", True),
    ("Gerencia", "TERCEROS", "UPDATE", True),
    ("Gerencia", "TERCEROS", "VIEW", True),
    ("Comercial", "TERCEROS", "CREATE", True),
    ("Comercial", "TERCEROS", "UPDATE", True),
    ("Comercial", "TERCEROS", "VIEW", True),
    # ── DASHBOARD ─────────────────────────────────────────────────────────────
    ("Admin", "DASHBOARD", "VIEW", True),
    ("Admin", "DASHBOARD", "UPDATE", True),
    ("Gerencia", "DASHBOARD", "VIEW", True),
    ("Gerencia", "DASHBOARD", "UPDATE", True),
    ("Comercial", "DASHBOARD", "VIEW", True),
    ("Comercial", "DASHBOARD", "UPDATE", True),
    # ── ADMINISTRACIÓN ────────────────────────────────────────────────────────
    ("Admin", "ADMINISTRACION", "CREATE", True),
    ("Admin", "ADMINISTRACION", "UPDATE", True),
    ("Admin", "ADMINISTRACION", "DELETE", True),
    ("Admin", "ADMINISTRACION", "VIEW", True),
    ("Gerencia", "ADMINISTRACION", "VIEW", True),
]


# ── Runner ────────────────────────────────────────────────────────────────────


def seed():
    db = SessionLocal()
    try:
        print("Iniciando seed de datos base...")

        # Roles
        rol_map = {}
        for r in ROLES:
            existing = db.query(Rol).filter_by(codigo=r["codigo"]).first()
            if not existing:
                obj = Rol(**r)
                db.add(obj)
                db.flush()
                rol_map[r["codigo"]] = obj
                print(f"Rol: {r['codigo']}")
            else:
                rol_map[r["codigo"]] = existing
        db.commit()

        # Módulos
        mod_map = {}
        for m in MODULOS:
            existing = db.query(Modulo).filter_by(codigo=m["codigo"]).first()
            if not existing:
                obj = Modulo(**m)
                db.add(obj)
                db.flush()
                mod_map[m["codigo"]] = obj
                print(f"Módulo: {m['codigo']}")
            else:
                mod_map[m["codigo"]] = existing
        db.commit()

        # Operaciones
        op_map = {}
        for o in OPERACIONES:
            existing = db.query(Operacion).filter_by(codigo=o["codigo"]).first()
            if not existing:
                obj = Operacion(**o)
                db.add(obj)
                db.flush()
                op_map[o["codigo"]] = obj
                print(f"Operación: {o['codigo']}")
            else:
                op_map[o["codigo"]] = existing
        db.commit()

        # Permisos
        permisos_creados = 0
        for rol_cod, mod_cod, op_cod, permitido in PERMISOS:
            rol = rol_map.get(rol_cod)
            mod = mod_map.get(mod_cod)
            op = op_map.get(op_cod)
            if not (rol and mod and op):
                continue
            existing = (
                db.query(Permiso)
                .filter_by(rol_id=rol.id, modulo_id=mod.id, operacion_id=op.id)
                .first()
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
                permisos_creados += 1
        db.commit()
        print(f"{permisos_creados} permisos creados")

        # Usuario Admin inicial
        admin_rol = rol_map.get("Admin")
        if admin_rol:
            existing = db.query(Usuario).filter_by(username="admin").first()
            if not existing:
                admin = Usuario(
                    username="admin",
                    password_hash=app.core.security.hash_password("admin1234"),
                    nombre_completo="Administrador del Sistema",
                    rol_id=admin_rol.id,
                    email="admin@invermin.pe",
                    activo=True,
                )
                db.add(admin)
                db.commit()
                print("Usuario admin creado (password: admin1234)")
                print(" CAMBIAR PASSWORD EN PRODUCCIÓN")
            else:
                print("usuario admin ya existe")

        print("\nSeed completado exitosamente")

    except Exception as e:
        db.rollback()
        print(f"\nError en seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
