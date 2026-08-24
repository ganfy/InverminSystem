import argparse
import os
import sys

# Add the backend directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    MapeoCIP,
    PruebaMetalurgica,
)


def rename_cip(old_cip: str, new_cip: str):
    db = SessionLocal()
    try:
        print(f"Buscando CIP origen: {old_cip}")
        old_mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == old_cip).first()

        if not old_mapeo:
            print(f"Error: El CIP {old_cip} no existe en la base de datos.")
            return

        # Check if new already exists
        new_mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == new_cip).first()
        if new_mapeo:
            print(f"Error: El CIP {new_cip} ya existe en la base de datos. No se puede renombrar.")
            return

        print(f"Creando nuevo registro MapeoCIP para {new_cip}")
        # Create a new MapeoCIP with the new code
        new_mapeo = MapeoCIP(
            lote_id=old_mapeo.lote_id,
            ruma_id=old_mapeo.ruma_id,
            codigo_cip=new_cip,
            laboratorio=old_mapeo.laboratorio,
            fecha_envio=old_mapeo.fecha_envio,
            tipo_muestra=old_mapeo.tipo_muestra,
        )
        db.add(new_mapeo)
        db.commit()  # Commit so it can be referenced

        print("Actualizando referencias en AnalisisLey...")
        analisis_leyes = db.query(AnalisisLey).filter(AnalisisLey.cip == old_cip).all()
        for a in analisis_leyes:
            a.cip = new_cip

        print("Actualizando referencias en AnalisisRecuperacion...")
        recuperaciones = (
            db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.cip == old_cip).all()
        )
        for r in recuperaciones:
            r.cip = new_cip

        print("Actualizando referencias en PruebaMetalurgica...")
        pruebas = db.query(PruebaMetalurgica).filter(PruebaMetalurgica.cip == old_cip).all()
        for p in pruebas:
            p.cip = new_cip

        # Verify LotePruebaMetalurgica if it references cip (it shouldn't, only PruebaMetalurgica does)

        # Save updates to references
        db.commit()

        print(f"Eliminando el antiguo registro MapeoCIP: {old_cip}")
        # Now it is safe to delete the old MapeoCIP
        db.delete(old_mapeo)
        db.commit()

        print("¡Renombrado de CIP completado con éxito!")

    except Exception as e:
        db.rollback()
        print(f"Ocurrió un error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Renombra un código CIP y actualiza todas sus referencias."
    )
    parser.add_argument("old_cip", help="El código CIP actual (ej. CIP-12345-REE4)")
    parser.add_argument("new_cip", help="El nuevo código CIP (ej. CIP-12345-REE1)")

    args = parser.parse_args()
    rename_cip(args.old_cip, args.new_cip)
