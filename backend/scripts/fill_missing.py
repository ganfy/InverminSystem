import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.core.database import SessionLocal
from app.models.models import SpotHistorico


def upsert_spot(db, fecha_str, au_pm, ag_noon):
    fecha = date.fromisoformat(fecha_str)
    existente = db.query(SpotHistorico).filter(SpotHistorico.fecha == fecha).first()
    if existente:
        existente.precio_au_usd = Decimal(str(round(au_pm, 2)))
        existente.precio_ag_usd = Decimal(str(round(ag_noon, 4)))
        existente.fuente = "MANUAL"
        return "ACTUALIZADO"
    else:
        registro = SpotHistorico(
            fecha=fecha,
            precio_au_usd=Decimal(str(round(au_pm, 2))),
            precio_ag_usd=Decimal(str(round(ag_noon, 4))),
            fuente="MANUAL",
        )
        db.add(registro)
        return "INSERTADO"


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dates", nargs="+", required=True)
    parser.add_argument("--au", type=float, required=True)
    parser.add_argument("--ag", type=float, required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        for d in args.dates:
            res = upsert_spot(db, d, args.au, args.ag)
            print(f"{d}: {res}")
        db.commit()
    except Exception as e:
        db.rollback()
        print("ERROR:", e)
    finally:
        db.close()


if __name__ == "__main__":
    main()
