import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.database import SessionLocal
from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    Lote,
    Muestreo,
    Pesaje,
    ProveedorAcopiador,
    SesionDescarga,
)


def seed_liquidables():
    db = SessionLocal()
    try:
        provacop = db.query(ProveedorAcopiador).first()
        if not provacop:
            print("Error: No hay provacop disponible.")
            return

        sesion = SesionDescarga(provacop_id=provacop.id, placa="TEST-123", estado="COMPLETO")
        db.add(sesion)
        db.flush()

        # Get max IP to avoid constraint issues
        last_lote = db.query(Lote).order_by(Lote.id.desc()).first()
        ip_start = int(last_lote.ip.split("-")[1]) if last_lote and "-" in last_lote.ip else 1000

        for i in range(1, 4):
            ip_num = ip_start + i
            lote = Lote(
                sesion_id=sesion.id,
                ip=f"IP-{ip_num:04d}",
                numero_lote=i,
                tipo_material="Mineral",
                estado="RECEPCIONADO",
            )
            db.add(lote)
            db.flush()

            # Pesaje
            pesaje = Pesaje(lote_id=lote.id, peso_inicial=30.0, peso_final=10.0, es_manual=False)
            db.add(pesaje)

            # Muestreo
            muestreo = Muestreo(lote_id=lote.id, intento=1, peso_humedo=10.0, peso_seco=9.5)
            db.add(muestreo)

            # Analisis Ley
            ley_planta = AnalisisLey(
                lote_id=lote.id,
                laboratorio="Laboratorio Interno",
                tipo_analisis="PLANTA",
                material="Au",
                ley_fino=random.uniform(0.5, 1.5),
                ley_grueso=0.0,
                ley_final=random.uniform(0.5, 1.5),
                vigente=True,
            )
            db.add(ley_planta)

            ley_minero = AnalisisLey(
                lote_id=lote.id,
                laboratorio="Laboratorio Minero",
                tipo_analisis="MINERO",
                material="Au",
                ley_fino=random.uniform(0.4, 1.6),
                ley_grueso=0.0,
                ley_final=random.uniform(0.4, 1.6),
                vigente=True,
            )
            db.add(ley_minero)

            rec = AnalisisRecuperacion(
                lote_id=lote.id,
                laboratorio="Laboratorio Interno",
                ley_cabeza=random.uniform(0.5, 1.5),
                ley_cola=random.uniform(0.05, 0.15),
                ley_liquido=random.uniform(0.1, 0.3),
                vigente=True,
            )
            db.add(rec)

        db.commit()
        print("Lotes liquidables creados exitosamente.")

    except Exception as e:
        db.rollback()
        print(f"Error al crear lotes: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_liquidables()
