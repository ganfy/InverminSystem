"""
seed_spot_manual.py - Inserta datos LBMA del ultimo mes directamente.
Datos provistos manualmente (Gold AM, Gold PM, Silver Noon).
Formato: DD Mon YYYY | Au AM | Au PM | Ag Noon
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.models import SpotHistorico

# Datos LBMA proporcionados: (fecha_str, au_am, au_pm, ag_noon)
# Columnas: Date | Gold AM | Gold PM | Silver (Noon)
DATOS = [
    ("21 Aug 2026", 4581.95, 4582.10, 69.51),
    ("20 Aug 2026", 4487.60, 4482.95, 66.745),
    ("19 Aug 2026", 4355.75, 4460.70, 63.355),
    ("18 Aug 2026", 4388.75, 4403.50, 65.095),
    ("17 Aug 2026", 4393.60, 4405.80, 65.61),
    ("14 Aug 2026", 4349.90, 4390.70, 64.605),
    ("13 Aug 2026", 4380.45, 4373.00, 64.955),
    ("12 Aug 2026", 4413.20, 4426.65, 66.25),
    ("11 Aug 2026", 4372.20, 4383.35, 65.185),
    ("10 Aug 2026", 4340.50, 4324.45, 63.935),
    ("07 Aug 2026", 4301.85, 4335.55, 64.32),
    ("06 Aug 2026", 4281.10, 4267.85, 61.735),
    ("05 Aug 2026", 4156.45, 4206.60, 61.265),
    ("04 Aug 2026", 4049.20, 4084.20, 58.785),
    ("03 Aug 2026", 4045.65, 4028.15, 57.965),
]

DIAS = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]


def guardar_dia(db, fecha, au_pm, ag_noon) -> str:
    existente = db.query(SpotHistorico).filter(SpotHistorico.fecha == fecha).first()
    if existente:
        existente.precio_au_usd = Decimal(str(round(au_pm, 2)))
        existente.precio_ag_usd = Decimal(str(round(ag_noon, 4)))
        existente.fuente = "SCRAPING"
        return "ACTUALIZAR"
    else:
        registro = SpotHistorico(
            fecha=fecha,
            precio_au_usd=Decimal(str(round(au_pm, 2))),
            precio_ag_usd=Decimal(str(round(ag_noon, 4))),
            fuente="SCRAPING",
        )
        db.add(registro)
        return "INSERTAR"


def main():
    db = SessionLocal()
    insertar = actualizar = 0

    print(f"\nInsertando {len(DATOS)} registros LBMA...\n")
    print(f"{'FECHA':<14} {'DIA':<4} {'Au PM':>10} {'Ag Noon':>10}  ACCION")
    print("-" * 55)

    try:
        for fecha_str, _au_am, au_pm, ag_noon in DATOS:
            fecha = datetime.strptime(fecha_str, "%d %b %Y").date()
            dia = DIAS[fecha.weekday()]

            # Guardar el dia actual
            accion = guardar_dia(db, fecha, au_pm, ag_noon)
            if accion == "ACTUALIZAR":
                actualizar += 1
            else:
                insertar += 1
            print(f"{str(fecha):<14} {dia:<4} ${au_pm:>9.2f} ${ag_noon:>9.4f}  [{accion}]")

            # Completar fines de semana
            if fecha.weekday() == 4:  # Viernes -> copiar a Sábado
                sabado = fecha + timedelta(days=1)
                accion_sab = guardar_dia(db, sabado, au_pm, ag_noon)
                if accion_sab == "ACTUALIZAR":
                    actualizar += 1
                else:
                    insertar += 1
                print(
                    f"{str(sabado):<14} {'Sab':<4} ${au_pm:>9.2f} ${ag_noon:>9.4f}  [{accion_sab}] (copia de Viernes)"
                )

            if fecha.weekday() == 0:  # Lunes -> copiar a Domingo
                domingo = fecha - timedelta(days=1)
                accion_dom = guardar_dia(db, domingo, au_pm, ag_noon)
                if accion_dom == "ACTUALIZAR":
                    actualizar += 1
                else:
                    insertar += 1
                print(
                    f"{str(domingo):<14} {'Dom':<4} ${au_pm:>9.2f} ${ag_noon:>9.4f}  [{accion_dom}] (copia de Lunes)"
                )

        db.commit()
        print(f"\nOK: {insertar} nuevos, {actualizar} actualizados.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
