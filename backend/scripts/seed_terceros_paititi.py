"""
Carga de proveedores desde la hoja RUC del Excel "PL paititi (1).xlsx".

Mapeo de columnas Excel -> campos del sistema:
  B  → razon_social (NOMBRE)
  C  → referencia (REFERENCIA / PROCEDENCIA)
  D  → ruc
  E  → maquila (antes lim_ley_superior)
  F  → riesgo_comercial   (RIESGO COMERCIAL en USD/TM)
  G  → gasto_acopio       (GASTO ACOPIO en USD/TM)
  H  → gasto_consumo      (GASTO CONSUMO en USD/TM)
  I  -> porcentaje_ley_comercial  (% LEY -- porcentaje de recuperación comercial)
  J  → dscto_ley_comercial (antes lim_ley_inferior)
  K  → lim_ley_comercial  (LEY MINIMA — ley comercial mínima / ley volado)
  L  -> comision           (COMISION en USD/TM -- si existe)
  M  -> acopiador (nombre -- se busca como entidad; si no existe, se crea como nuevo)
  S  -> notas de recuperacion diferenciada por rango de ley, se parsean los umbrales de recup bajo y medio

Uso:
    # Simulación (no escribe en BD):
    python scripts/seed_terceros_paititi.py --dry-run

    # Carga real contra BD local (.env):
    python scripts/seed_terceros_paititi.py

    # Carga real contra producción (Azure):
    python scripts/seed_terceros_paititi.py --env prod

IMPORTANTE:
    - La carga es idempotente por RUC: si ya existe una entidad con ese RUC,
      actualiza sus parámetros sin duplicar.
    - Los RUC con asterisco (*) o valores no numéricos se marcan como pendientes.
    - Los acopiadores se crean como entidades si no existen.
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET  # noqa: N817
import zipfile
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

EXCEL_PATH = Path(__file__).parent.parent.parent / "PL paititi (6).xlsx"


# ── Lector de Excel sin dependencias externas ─────────────────────────────────


def _leer_shared_strings(z):
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        tree = ET.parse(z.open("xl/sharedStrings.xml"))
        root = tree.getroot()
        ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        for si in root.findall("ns:si", ns):
            texts = [t.text or "" for t in si.findall(".//ns:t", ns)]
            shared.append("".join(texts))
    return shared


def _get_cell_val(c, shared, ns):
    t = c.get("t", "")
    v_el = c.find("ns:v", ns)
    if v_el is None:
        return None
    v = v_el.text
    if t == "s":
        return shared[int(v)]
    return v


def leer_hoja_ruc(excel_path: Path) -> list[dict]:
    """Lee la hoja RUC del Excel y devuelve lista de dicts por proveedor."""
    with zipfile.ZipFile(excel_path) as z:
        shared = _leer_shared_strings(z)

        rels = ET.parse(z.open("xl/_rels/workbook.xml.rels"))
        rel_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
        rel_map = {
            r.get("Id"): r.get("Target") for r in rels.getroot().findall("r:Relationship", rel_ns)
        }

        wb_tree = ET.parse(z.open("xl/workbook.xml"))
        wb_root = wb_tree.getroot()
        ns2 = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        sph = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

        for sheet in wb_root.findall(".//ns:sheet", ns2):
            if sheet.get("name") != "RUC":
                continue

            rid = sheet.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
            target = rel_map.get(rid)
            sheet_tree = ET.parse(z.open(f"xl/{target}"))
            sheet_root = sheet_tree.getroot()

            proveedores = []
            for row in sheet_root.findall(".//ns:row", sph):
                row_num = int(row.get("r", 0))
                if row_num <= 2:  # Filas de encabezado
                    continue

                raw = {}
                for cell in row.findall("ns:c", sph):
                    ref = cell.get("r", "")
                    col = "".join(filter(str.isalpha, ref))
                    val = _get_cell_val(cell, shared, sph)
                    if val is not None:
                        raw[col] = val

                if not raw.get("B"):  # Sin nombre = fila vacía
                    continue

                # Limpiar RUC (quitar asteriscos, espacios, notación científica)
                ruc_raw = str(raw.get("D", "")).strip().replace("*", "")
                ruc_limpio = None
                ruc_valido = False

                if ruc_raw:
                    # Convertir notacion cientifica y extraer digitos
                    try:
                        if "E" in ruc_raw.upper():
                            ruc_limpio = str(int(float(ruc_raw)))
                        else:
                            # Quitar cualquier caracter que no sea digito
                            ruc_limpio = re.sub(r"[^\d]", "", ruc_raw)
                        ruc_valido = bool(ruc_limpio)
                    except ValueError:
                        ruc_limpio = ruc_raw  # Mantener como string si falla

                def to_float(val):
                    try:
                        return float(val) if val is not None else None
                    except (ValueError, TypeError):
                        return None

                notas_s = str(raw.get("S", "")).strip() or None
                umbral_recup_bajo = None
                umbral_recup_medio = None
                if notas_s:
                    matches = re.findall(r"<\s*(\d+\.\d+)", notas_s)
                    if len(matches) >= 1:
                        umbral_recup_bajo = float(matches[0])
                    if len(matches) >= 2:
                        umbral_recup_medio = float(matches[1])

                proveedores.append(
                    {
                        "razon_social": str(raw.get("B", "")).strip(),
                        "referencia": str(raw.get("C", "")).strip() or None,
                        "ruc": ruc_limpio,
                        "ruc_valido": ruc_valido,
                        # Parámetros comerciales
                        "maquila": to_float(raw.get("E")),  # MAQUILA
                        "riesgo_comercial": to_float(raw.get("F")),  # RIESGO COMERCIAL
                        "gasto_acopio": to_float(raw.get("G")),  # GASTO ACOPIO
                        "gasto_consumo": to_float(raw.get("H")),  # GASTO CONSUMO
                        "porcentaje_ley_comercial": to_float(raw.get("I")),  # % LEY
                        "dscto_ley_comercial": to_float(raw.get("J")),  # DSCTO LEY COMERCIAL
                        "lim_ley_comercial": to_float(raw.get("K")),  # LEY MINIMA
                        "comision": to_float(raw.get("L")),  # COMISION
                        "acopiador_nombre": str(raw.get("M", "")).strip() or None,
                        "notas_recuperacion": notas_s,
                        "umbral_recup_bajo": umbral_recup_bajo,
                        "umbral_recup_medio": umbral_recup_medio,
                        "notas_plata": str(raw.get("T", "")).strip() or None,
                        "row_num": row_num,
                    }
                )

            return proveedores
    return []


# ── Lógica de carga en BD ─────────────────────────────────────────────────────


def cargar_terceros(dry_run: bool = False):
    # Importar aquí para respetar el entorno seleccionado
    from app.core.database import SessionLocal
    from app.models.enums import RolEntidad, TipoEntidad
    from app.models.models import (
        Entidad,
        EntidadRol,
        ParametrosComerciales,
        ProveedorAcopiador,
        Rol,
    )

    prefix = "[DRY-RUN] " if dry_run else ""
    sql_statements = []

    proveedores = leer_hoja_ruc(EXCEL_PATH)
    print(f"Leídos {len(proveedores)} proveedores desde el Excel.\n")

    db = SessionLocal()
    try:
        rol_proveedor = db.query(Rol).filter_by(codigo=RolEntidad.PROVEEDOR).first()
        rol_acopiador = db.query(Rol).filter_by(codigo=RolEntidad.ACOPIADOR).first()
        if not rol_proveedor or not rol_acopiador:
            print("ERROR: Roles PROVEEDOR/ACOPIADOR no encontrados. Ejecuta seed.py primero.")
            return

        # Cache de acopiadores ya creados en esta sesion (nombre -> Entidad)
        acopiador_cache: dict[str, "Entidad"] = {}

        stats = {"creados": 0, "actualizados": 0, "omitidos": 0, "advertencias": []}

        for p in proveedores:
            nombre = p["razon_social"]

            # ── Validar RUC ───────────────────────────────────────────────────
            if not p["ruc_valido"]:
                msg = f"Fila {p['row_num']}: '{nombre}' - RUC invalido '{p['ruc']}' -> omitido"
                print(f"  [!]  {msg}")
                stats["advertencias"].append(msg)
                stats["omitidos"] += 1
                continue

            # ── Obtener o crear acopiador ─────────────────────────────────────
            acopiador_nombre = p["acopiador_nombre"]
            acopiador = None

            if acopiador_nombre and acopiador_nombre.upper() not in (
                "SIN ACOPIO",
                "XXXXXX",
                "VALORIZACION",
                "",
            ):
                # Buscar en cache primero
                acopiador = acopiador_cache.get(acopiador_nombre)

                if not acopiador and not dry_run:
                    # Buscar en BD por razon_social aproximada
                    acopiador = (
                        db.query(Entidad)
                        .filter(Entidad.razon_social.ilike(f"%{acopiador_nombre.split()[0]}%"))
                        .join(EntidadRol, EntidadRol.entidad_id == Entidad.id)
                        .join(Rol, Rol.id == EntidadRol.rol_id)
                        .filter(Rol.codigo == RolEntidad.ACOPIADOR)
                        .first()
                    )

                if not acopiador and not dry_run:
                    # Crear acopiador nuevo
                    ruc_acop = f"A{uuid4().hex[:10].upper()}"
                    acopiador = Entidad(
                        ruc=ruc_acop,
                        razon_social=acopiador_nombre,
                        tipo=TipoEntidad.PERSONA_NATURAL,
                        activo=True,
                    )
                    db.add(acopiador)
                    db.flush()
                    # Asignar rol acopiador
                    ent_rol = EntidadRol(
                        entidad_id=acopiador.id, rol_id=rol_acopiador.id, activo=True
                    )
                    db.add(ent_rol)
                    db.flush()

                    sql_statements.append(f"-- Acopiador nuevo: {acopiador_nombre}")
                    sql_statements.append(
                        f"INSERT INTO entidades (ruc, razon_social, tipo, activo) VALUES ('{ruc_acop}', '{acopiador_nombre}', '{TipoEntidad.PERSONA_NATURAL.value}', true);"
                    )
                    sql_statements.append(
                        f"INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '{ruc_acop}'), {rol_acopiador.id}, true);"
                    )

                    print(f"  + Acopiador creado: '{acopiador_nombre}'")

                if acopiador:
                    acopiador_cache[acopiador_nombre] = acopiador

            # ── Obtener o crear proveedor ─────────────────────────────────────
            proveedor = db.query(Entidad).filter_by(ruc=p["ruc"]).first()

            if proveedor:
                accion = "actualizar"
            else:
                accion = "crear"
                proveedor = None

            if accion == "crear":
                print(
                    f"{prefix}[CREAR]  '{nombre}' (RUC: {p['ruc']}) - acopiador: {acopiador_nombre or 'propio'}"
                )
                tipo_entidad = (
                    TipoEntidad.EMPRESA
                    if p["ruc"] and len(p["ruc"]) == 11
                    else TipoEntidad.PERSONA_NATURAL
                )
                if not dry_run:
                    proveedor = Entidad(
                        ruc=p["ruc"],
                        razon_social=nombre,
                        referencia=p["referencia"],
                        tipo=tipo_entidad,
                        activo=True,
                    )
                    db.add(proveedor)
                    db.flush()
                    db.add(
                        EntidadRol(entidad_id=proveedor.id, rol_id=rol_proveedor.id, activo=True)
                    )
                    db.flush()

                sql_statements.append(f"-- Proveedor nuevo: {nombre}")
                sql_statements.append(
                    f"INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('{p['ruc']}', '{nombre}', '{p['referencia'] or ''}', '{tipo_entidad.value}', true);"
                )
                sql_statements.append(
                    f"INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '{p['ruc']}'), {rol_proveedor.id}, true);"
                )

                stats["creados"] += 1
            else:
                print(
                    f"{prefix}[UPDATE] '{nombre}' (RUC: {p['ruc']}) - ya existe, actualizando parametros"
                )
                if not dry_run:
                    proveedor.razon_social = nombre
                    if p["referencia"]:
                        proveedor.referencia = p["referencia"]
                stats["actualizados"] += 1

            if dry_run:
                continue

            # ── Crear/obtener relación provacop ───────────────────────────────
            acopiador_final = (
                acopiador if acopiador else proveedor
            )  # Si no tiene, es su propio acopiador
            if not acopiador:
                # Asignar también rol acopiador al propio proveedor
                existing_acop_rol = (
                    db.query(EntidadRol)
                    .filter_by(entidad_id=proveedor.id, rol_id=rol_acopiador.id)
                    .first()
                )
                if not existing_acop_rol:
                    db.add(
                        EntidadRol(entidad_id=proveedor.id, rol_id=rol_acopiador.id, activo=True)
                    )
                    db.flush()

            provacop = (
                db.query(ProveedorAcopiador)
                .filter_by(proveedor_id=proveedor.id, acopiador_id=acopiador_final.id)
                .first()
            )
            if not provacop:
                provacop = ProveedorAcopiador(
                    proveedor_id=proveedor.id,
                    acopiador_id=acopiador_final.id,
                )
                db.add(provacop)
                db.flush()

            # ── Crear/actualizar parámetros comerciales ───────────────────────
            pc = db.query(ParametrosComerciales).filter_by(provacop_id=provacop.id).first()
            if not pc:
                pc = ParametrosComerciales(provacop_id=provacop.id)
                db.add(pc)

            # Mapeo directo de campos
            campo_map = {
                "maquila": p["maquila"],
                "riesgo_comercial": p["riesgo_comercial"],
                "gasto_acopio": p["gasto_acopio"],
                "gasto_consumo": p["gasto_consumo"],
                "porcentaje_ley_comercial": p["porcentaje_ley_comercial"],
                "dscto_ley_comercial": p["dscto_ley_comercial"],
                "lim_ley_comercial": p["lim_ley_comercial"],
                "comision": p["comision"],
                "umbral_recup_bajo": p["umbral_recup_bajo"],
                "umbral_recup_medio": p["umbral_recup_medio"],
            }
            for campo, valor in campo_map.items():
                if valor is not None:
                    setattr(pc, campo, valor)

            # ── Parámetros de Plata (Ag) ───────────────────────────────────────
            # Valores por defecto: 3.5 oz/tc y 30% de recuperación
            umbral_ag = 3.5
            recup_ag = 30.0

            # El bloque coloreado (filas 109 a 114) tiene 4 oz
            if p.get("row_num") and 109 <= p["row_num"] <= 114:
                umbral_ag = 4.0
                recup_ag = 30.0

            # Si hubiera una nota explícita distinta en la columna T, la priorizamos
            if p.get("notas_plata") and "PLATA" in p["notas_plata"].upper():
                import re

                match = re.search(
                    r"(\d+(?:\.\d+)?)\s*OZ.*?(\d+(?:\.\d+)?)%", p["notas_plata"].upper()
                )
                if match:
                    umbral_ag = float(match.group(1))
                    recup_ag = float(match.group(2))

            pc.umbral_ag_oz_tc = umbral_ag
            pc.rec_ag_pct = recup_ag

            # ── Lógica de Llampo ───────────────────────────────────────────────
            # Standard rule: +40 for consumption and +10 for acopio
            # Exception rule: 'Ronald Miranda' -> 40 for consumption, 50 for acopio
            is_ronald = (
                acopiador_final and "RONALD MIRANDA" in (acopiador_final.razon_social or "").upper()
            )

            if is_ronald:
                pc.gasto_consumo_llampo = 40
                pc.gasto_acopio_llampo = 50
            else:
                if pc.gasto_consumo is not None:
                    pc.gasto_consumo_llampo = pc.gasto_consumo + 40
                if pc.gasto_acopio is not None:
                    pc.gasto_acopio_llampo = pc.gasto_acopio + 10

            db.flush()

        if not dry_run:
            db.commit()

        # ── Resumen ───────────────────────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"{prefix}RESUMEN:")
        print(f"  Creados:     {stats['creados']}")
        print(f"  Actualizados: {stats['actualizados']}")
        print(f"  Omitidos:    {stats['omitidos']} (RUC inválido)")
        if stats["advertencias"]:
            print(f"\n  Advertencias ({len(stats['advertencias'])}):")
            for w in stats["advertencias"]:
                print(f"    - {w}")
        print("=" * 60)

        if not dry_run:
            db.commit()

        return sql_statements, stats

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Carga proveedores de PL Paititi Excel -> BD.")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin hacer cambios en la BD")
    parser.add_argument("--env", choices=["local", "prod"], default="local", help="Entorno de BD")
    parser.add_argument(
        "--sql-out",
        type=str,
        help="Ruta de archivo para guardar las sentencias SQL de inserción generadas (solo PostgreSQL)",
    )
    args = parser.parse_args()

    if args.env == "prod":
        import os

        env_file = Path(__file__).parent.parent / ".env.prod"
        print(f"Usando .env.prod: {env_file}")
        # Cargar variables del .env.prod antes de importar la app
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"'))

    if args.dry_run:
        print("=== MODO DRY-RUN: sin cambios en BD ===\n")

    sql_stmts, stats = cargar_terceros(dry_run=args.dry_run)

    if args.sql_out and sql_stmts:
        out_path = Path(args.sql_out)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("-- SQL INSERTS PARA NUEVOS TERCEROS\n")
            f.write("BEGIN;\n\n")
            for stmt in sql_stmts:
                f.write(stmt + "\n")
            f.write("\nCOMMIT;\n")
        print(f"\n[OK] Archivo SQL generado en: {out_path.resolve()}")


if __name__ == "__main__":
    main()
