"""
Seed de datos de DESARROLLO / PRUEBAS.

Crea entidades, relaciones proveedor-acopiador y usuarios de prueba
para poder testear todos los módulos sin insertar SQL manual.

Requiere que seed.py (datos base) ya se haya ejecutado primero.

Uso:
    python scripts/seed_dev.py           # insertar datos de prueba
    python scripts/seed_dev.py --reset   # borrar datos de prueba y reinsertar

Es idempotente sin --reset: no duplica registros existentes.

NUNCA correr en producción.
"""

import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.models import (
    Entidad,
    EntidadRol,
    ParametrosComerciales,
    ProveedorAcopiador,
    Rol,
    Usuario,
)

# =============================================================================
# DATOS DE PRUEBA
# =============================================================================

ENTIDADES_PRUEBA = [
    {
        "ruc": "20123456789",
        "razon_social": "Minera Andes Gold S.A.C.",
        "tipo": "EMPRESA",
        "referencia": "Proveedor principal - zona norte",
        "telefono": "054-123456",
        "email": "contacto@andesgold.pe",
        "activo": True,
    },
    {
        "ruc": "20987654321",
        "razon_social": "Cooperativa Minera Puno S.R.L.",
        "tipo": "EMPRESA",
        "referencia": "Proveedor secundario - zona sur",
        "telefono": "051-987654",
        "email": "coop.puno@gmail.com",
        "activo": True,
    },
    {
        "ruc": "10111222333",
        "razon_social": "Carlos Mamani Quispe",
        "tipo": "PERSONA_NATURAL",
        "referencia": "Acopiador zona norte",
        "telefono": "958123456",
        "email": "cmamani@gmail.com",
        "activo": True,
    },
    {
        "ruc": "10444555666",
        "razon_social": "Rosa Flores Condori",
        "tipo": "PERSONA_NATURAL",
        "referencia": "Acopiador zona sur",
        "telefono": "952987654",
        "email": "rfloresc@gmail.com",
        "activo": True,
    },
    {
        # Proveedor que es su propio acopiador (caso especial del sistema)
        "ruc": "20555666777",
        "razon_social": "Minera Directa E.I.R.L.",
        "tipo": "EMPRESA",
        "referencia": "Auto-acopiador",
        "telefono": "054-555666",
        "email": "minera.directa@pe.com",
        "activo": True,
    },
]

# (ruc_proveedor, ruc_acopiador)
# El último caso es auto-acopiador (misma entidad, roles distintos)
RELACIONES_PROVACOP = [
    ("20123456789", "10111222333"),  # Andes Gold → Mamani
    ("20987654321", "10444555666"),  # Coop Puno  → Flores
    ("20555666777", "20555666777"),  # Directa    → sí misma
]

# Parámetros comerciales por acopiador
# (ruc_acopiador, dict_parametros)
PARAMETROS_PRUEBA = [
    (
        "20123456789",
        "10111222333",  # Andes Gold → Mamani
        {
            "umbral_recup_bajo": 75.00,
            "umbral_recup_medio": 85.00,
            "umbral_recup_alto": 92.00,
            "lim_ley_comercial": 0.500,
            "dscto_ley_comercial": 0.010,
            "porcentaje_ley_comercial": 0.950,
            "lim_ley_inferior": 0.100,
            "lim_ley_superior": 2.000,
            "gasto_acopio": 15.00,
            "gasto_consumo": 8.00,
            "maquila": 5.00,
            "comision": 2.50,
        },
    ),
    (
        "20987654321",
        "10444555666",  # Coop Puno  → Flores
        {
            "umbral_recup_bajo": 72.00,
            "umbral_recup_medio": 83.00,
            "umbral_recup_alto": 90.00,
            "lim_ley_comercial": 0.450,
            "dscto_ley_comercial": 0.015,
            "porcentaje_ley_comercial": 0.940,
            "lim_ley_inferior": 0.100,
            "lim_ley_superior": 1.800,
            "gasto_acopio": 18.00,
            "gasto_consumo": 9.00,
            "maquila": 5.50,
            "comision": 3.00,
        },
    ),
    (
        "20555666777",
        "20555666777",  # Directa    → sí misma (auto-acopiador)
        {  # auto-acopiador
            "umbral_recup_bajo": 80.00,
            "umbral_recup_medio": 88.00,
            "umbral_recup_alto": 94.00,
            "lim_ley_comercial": 0.600,
            "dscto_ley_comercial": 0.008,
            "porcentaje_ley_comercial": 0.960,
            "lim_ley_inferior": 0.150,
            "lim_ley_superior": 2.500,
            "gasto_acopio": 12.00,
            "gasto_consumo": 7.00,
            "maquila": 4.50,
            "comision": 2.00,
        },
    ),
]

# Usuarios de prueba para cada rol
USUARIOS_PRUEBA = [
    {
        "username": "operador1",
        "password": "operador1234",
        "nombre_completo": "Pedro Condori Mamani",
        "rol_codigo": "OperadorBalanza",
        "email": "operador1@invermin.pe",
    },
    {
        "username": "muestrero1",
        "password": "muestrero1234",
        "nombre_completo": "Ana Quispe Torres",
        "rol_codigo": "TecnicoMuestreo",
        "email": "muestrero1@invermin.pe",
    },
    {
        "username": "lab1",
        "password": "lab1234",
        "nombre_completo": "Jorge Ramos Silva",
        "rol_codigo": "Laboratorista",
        "email": "lab1@invermin.pe",
    },
    {
        "username": "comercial1",
        "password": "comercial1234",
        "nombre_completo": "María Fernández Ruiz",
        "rol_codigo": "Comercial",
        "email": "comercial1@invermin.pe",
    },
    {
        "username": "gerencia1",
        "password": "gerencia1234",
        "nombre_completo": "Roberto Salas Vega",
        "rol_codigo": "Gerencia",
        "email": "gerencia1@invermin.pe",
    },
]


# =============================================================================
# HELPERS
# =============================================================================


def get_or_create_entidad(db, datos: dict) -> Entidad:
    existing = db.query(Entidad).filter_by(ruc=datos["ruc"]).first()
    if existing:
        return existing
    entidad = Entidad(**datos)
    db.add(entidad)
    db.flush()
    print(f"  ✅ Entidad: {datos['razon_social']} ({datos['ruc']})")
    return entidad


def asignar_rol_entidad(db, entidad: Entidad, rol: Rol) -> EntidadRol:
    existing = db.query(EntidadRol).filter_by(entidad_id=entidad.id, rol_id=rol.id).first()
    if existing:
        return existing
    er = EntidadRol(entidad_id=entidad.id, rol_id=rol.id, activo=True)
    db.add(er)
    db.flush()
    print(f"     → Rol {rol.codigo} asignado a {entidad.razon_social}")
    return er


def get_or_create_provacop(
    db, proveedor_er: EntidadRol, acopiador_er: EntidadRol
) -> ProveedorAcopiador:
    existing = (
        db.query(ProveedorAcopiador)
        .filter_by(
            proveedor_id=proveedor_er.entidad_id,
            acopiador_id=acopiador_er.entidad_id,
        )
        .first()
    )
    if existing:
        return existing
    pa = ProveedorAcopiador(
        proveedor_id=proveedor_er.entidad_id,
        acopiador_id=acopiador_er.entidad_id,
    )
    db.add(pa)
    db.flush()
    return pa


def get_or_create_usuario(db, datos: dict, rol: Rol) -> Usuario:
    existing = db.query(Usuario).filter_by(username=datos["username"]).first()
    if existing:
        return existing
    usuario = Usuario(
        username=datos["username"],
        password_hash=hash_password(datos["password"]),
        nombre_completo=datos["nombre_completo"],
        rol_id=rol.id,
        email=datos["email"],
        activo=True,
    )
    db.add(usuario)
    db.flush()
    print(f"  ✅ Usuario: {datos['username']} / {datos['password']} [{rol.codigo}]")
    return usuario


# =============================================================================
# RESET
# =============================================================================


def reset_dev_data(db):
    """
    Borra los datos de prueba en orden inverso a las FKs.
    Solo borra lo que creó este seed (identifica por RUCs y usernames).
    No toca roles, módulos, permisos ni el usuario admin.
    """
    print("Reseteando datos de prueba...")

    db.execute(text("TRUNCATE parametros_comerciales CASCADE"))
    db.execute(text("TRUNCATE proveedor_acopiador CASCADE"))
    db.execute(text("TRUNCATE entidades_roles CASCADE"))

    # Usuarios de prueba — solo los del seed, no admin
    usernames = [u["username"] for u in USUARIOS_PRUEBA]
    rucs = [e["ruc"] for e in ENTIDADES_PRUEBA]

    db.query(Usuario).filter(Usuario.username.in_(usernames)).delete(synchronize_session=False)
    db.query(Entidad).filter(Entidad.ruc.in_(rucs)).delete(synchronize_session=False)
    db.commit()
    print("Reset completado\n")


# =============================================================================
# SEED PRINCIPAL
# =============================================================================


def seed_dev():
    db = SessionLocal()
    try:
        # Obtener roles del seed base (deben existir)
        rol_proveedor = db.query(Rol).filter_by(codigo="PROVEEDOR").first()
        rol_acopiador = db.query(Rol).filter_by(codigo="ACOPIADOR").first()

        if not rol_proveedor or not rol_acopiador:
            print("Roles PROVEEDOR/ACOPIADOR no encontrados.")
            print("Ejecuta primero: python scripts/seed.py")
            return

        print(" Creando entidades de prueba...")
        entidad_map = {}
        for datos in ENTIDADES_PRUEBA:
            entidad = get_or_create_entidad(db, datos)
            entidad_map[datos["ruc"]] = entidad
        db.commit()

        print("\nAsignando roles a entidades...")
        entidad_rol_map = {}  # ruc → {PROVEEDOR: er, ACOPIADOR: er}
        for datos in ENTIDADES_PRUEBA:
            ruc = datos["ruc"]
            entidad = entidad_map[ruc]
            entidad_rol_map[ruc] = {}

            # Determinar qué roles asignar según las relaciones
            es_proveedor = any(r[0] == ruc for r in RELACIONES_PROVACOP)
            es_acopiador = any(r[1] == ruc for r in RELACIONES_PROVACOP)

            if es_proveedor:
                er = asignar_rol_entidad(db, entidad, rol_proveedor)
                entidad_rol_map[ruc]["PROVEEDOR"] = er

            if es_acopiador:
                er = asignar_rol_entidad(db, entidad, rol_acopiador)
                entidad_rol_map[ruc]["ACOPIADOR"] = er

        db.commit()

        print("\nCreando relaciones proveedor-acopiador...")
        provacop_map = {}  # (ruc_prov, ruc_acop) → ProveedorAcopiador
        for ruc_prov, ruc_acop in RELACIONES_PROVACOP:
            er_prov = entidad_rol_map[ruc_prov]["PROVEEDOR"]
            er_acop = entidad_rol_map[ruc_acop]["ACOPIADOR"]
            pa = get_or_create_provacop(db, er_prov, er_acop)
            provacop_map[(ruc_prov, ruc_acop)] = pa

            prov_nombre = entidad_map[ruc_prov].razon_social
            acop_nombre = entidad_map[ruc_acop].razon_social
            sufijo = " (auto-acopiador)" if ruc_prov == ruc_acop else ""
            print(f"  ✅ {prov_nombre} → {acop_nombre}{sufijo} [ID: {pa.id}]")
        db.commit()

        print("\nCreando parámetros comerciales...")
        # for ruc_acop, params in PARAMETROS_PRUEBA:
        #     entidad = entidad_map[ruc_acop]
        #     existing = db.query(ParametrosComerciales).filter_by(acopiador_id=entidad.id).first()
        #     if not existing:
        #         pc = ParametrosComerciales(acopiador_id=entidad.id, **params)
        #         db.add(pc)
        #         print(f"Parámetros para {entidad.razon_social}")
        # db.commit()
        for ruc_prov, ruc_acop, params in PARAMETROS_PRUEBA:
            pa = provacop_map[(ruc_prov, ruc_acop)]
            existing = db.query(ParametrosComerciales).filter_by(provacop_id=pa.id).first()
            if not existing:
                pc = ParametrosComerciales(provacop_id=pa.id, **params)
                db.add(pc)

        print("\nCreando usuarios de prueba...")
        for datos in USUARIOS_PRUEBA:
            rol = db.query(Rol).filter_by(codigo=datos["rol_codigo"]).first()
            if not rol:
                print(f"Rol {datos['rol_codigo']} no encontrado, saltando")
                continue
            get_or_create_usuario(db, datos, rol)
        db.commit()

        print("\n" + "=" * 60)
        print("Seed de desarrollo completado")
        print("=" * 60)
        print("\nRESUMEN DE DATOS CREADOS:")
        print("\nRelaciones Proveedor-Acopiador disponibles:")
        for (ruc_p, ruc_a), pa in provacop_map.items():
            print(
                f"  provacop_id={pa.id}: {entidad_map[ruc_p].razon_social} → {entidad_map[ruc_a].razon_social}"
            )

        print("\nUsuarios de prueba (username / password):")
        for u in USUARIOS_PRUEBA:
            print(f"  {u['username']:15} / {u['password']:15} [{u['rol_codigo']}]")

    except Exception as e:
        db.rollback()
        print(f"\nError en seed_dev: {e}")
        raise
    finally:
        db.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    if "--reset" in sys.argv:
        db = SessionLocal()
        try:
            reset_dev_data(db)
        finally:
            db.close()

    seed_dev()
